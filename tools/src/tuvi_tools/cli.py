"""`tuvi`: run the TuviLM stack and checks from the repo root.

    uv run tuvi setup     install deps and create local env files
    uv run tuvi up        MongoDB (Docker) + API on :8000 + web on :3000
    uv run tuvi down      stop MongoDB (data is kept)
    uv run tuvi check     Python tests + web typecheck, lint and tests
    uv run tuvi editor    Streamlit cách cục rule editor
    uv run tuvi viewer    Streamlit chart viewer
"""

from __future__ import annotations

import argparse
import os
import secrets
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

MONGO_PORT = 27017
API_PORT = 8000
WEB_PORT = 3000

_COLORS = {"db": "35", "api": "36", "web": "33", "tuvi": "32"}


# ----------------------------------------------------------------------------- output


def _use_color() -> bool:
    return sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def _prefix(name: str) -> str:
    label = f"{name:>4} │"
    return f"\033[{_COLORS.get(name, '0')}m{label}\033[0m" if _use_color() else label


def say(message: str) -> None:
    print(f"{_prefix('tuvi')} {message}", flush=True)


def fail(message: str) -> int:
    say(f"error: {message}")
    return 1


# ----------------------------------------------------------------------------- paths and env


def repo_root() -> Path:
    """The workspace root: the nearest parent with apps/web and pyproject.toml."""
    for start in (Path.cwd(), Path(__file__).resolve()):
        for path in (start, *start.parents):
            if (path / "pyproject.toml").is_file() and (path / "apps" / "web").is_dir():
                return path
    raise SystemExit("tuvi: run this inside the TuviLM repository")


def read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip().strip("'\"")
    return values


def child_env(root: Path) -> dict[str, str]:
    """The shell env plus the repo .env, so keys like OPENROUTER_API_KEY reach the agent.

    Values already in the shell win over the file.
    """
    env = dict(os.environ)
    for key, value in read_env_file(root / ".env").items():
        env.setdefault(key, value)
    return env


def port_open(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.3)
        return sock.connect_ex((host, port)) == 0


def wait_for_port(port: int, timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if port_open(port):
            return True
        time.sleep(0.5)
    return False


def require(tool: str, hint: str) -> bool:
    if shutil.which(tool) is None:
        say(f"'{tool}' is not on PATH. {hint}")
        return False
    return True


# ----------------------------------------------------------------------------- processes


@dataclass
class Service:
    name: str
    command: list[str]
    cwd: Path
    env: dict[str, str]
    process: subprocess.Popen[str] | None = field(default=None, repr=False)

    def start(self) -> None:
        self.process = subprocess.Popen(
            self.command,
            cwd=self.cwd,
            env=self.env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            # Own process group, so stopping also stops reloaders and child workers.
            start_new_session=True,
        )
        threading.Thread(target=self._pipe_output, daemon=True).start()

    def _pipe_output(self) -> None:
        assert self.process is not None and self.process.stdout is not None
        for line in self.process.stdout:
            print(f"{_prefix(self.name)} {line.rstrip()}", flush=True)

    def stop(self) -> None:
        if self.process is None or self.process.poll() is not None:
            return
        try:
            os.killpg(self.process.pid, signal.SIGTERM)
            self.process.wait(timeout=10)
        except ProcessLookupError:
            pass
        except subprocess.TimeoutExpired:
            os.killpg(self.process.pid, signal.SIGKILL)


def _interrupt(signum: int, frame: object) -> None:
    raise KeyboardInterrupt


def run_services(services: list[Service]) -> int:
    """Run until Ctrl+C, SIGTERM or one service exits; then stop the others.

    Services run in their own process groups, so they do not get the terminal's
    signals: this function must stop them on every way out.
    """
    signal.signal(signal.SIGTERM, _interrupt)
    signal.signal(signal.SIGHUP, _interrupt)
    for service in services:
        say(f"starting {service.name}: {' '.join(service.command)}")
        service.start()
    exit_code = 0
    try:
        while True:
            for service in services:
                assert service.process is not None
                code = service.process.poll()
                if code is not None:
                    say(f"{service.name} exited with code {code}; stopping the rest")
                    exit_code = code or 1
                    raise KeyboardInterrupt
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        say("stopping…")
        for service in reversed(services):
            service.stop()
    return exit_code


def run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> int:
    say(f"$ {' '.join(command)}" + (f"   (in {cwd.name}/)" if cwd != repo_root() else ""))
    return subprocess.call(command, cwd=cwd, env=env)


# ----------------------------------------------------------------------------- commands


def cmd_setup(_: argparse.Namespace) -> int:
    root = repo_root()
    ok = require("pnpm", "Install it with `corepack enable` or https://pnpm.io/installation.")
    ok &= require("docker", "Install Docker to run MongoDB, or run your own on port 27017.")
    if not ok:
        return 1

    if run(["uv", "sync"], cwd=root) != 0:
        return fail("uv sync failed")
    if run(["pnpm", "install"], cwd=root / "apps" / "web") != 0:
        return fail("pnpm install failed")

    env_file = root / ".env"
    if not env_file.exists():
        text = (root / ".env.example").read_text()
        text = text.replace(
            "# AUTH__SECRET_KEY=", f"AUTH__SECRET_KEY={secrets.token_urlsafe(32)}"
        )
        env_file.write_text(text)
        say("created .env from .env.example (add OPENROUTER_API_KEY for the chat)")
    web_env = root / "apps" / "web" / ".env.local"
    if not web_env.exists():
        shutil.copyfile(root / "apps" / "web" / ".env.example", web_env)
        say("created apps/web/.env.local")

    say("done. Next: uv run tuvi up")
    return 0


def cmd_up(args: argparse.Namespace) -> int:
    root = repo_root()
    env = child_env(root)

    if not args.no_db:
        if port_open(MONGO_PORT):
            say(f"MongoDB already answers on :{MONGO_PORT}; using it")
        else:
            if not require("docker", "Or start MongoDB yourself and pass --no-db."):
                return 1
            if run(["docker", "compose", "up", "-d", "mongodb"], cwd=root) != 0:
                return fail("could not start MongoDB with docker compose")
            if not wait_for_port(MONGO_PORT, timeout=60):
                return fail(f"MongoDB did not open port {MONGO_PORT} within 60 s")
            say(f"MongoDB is up on :{MONGO_PORT} (stop it with: uv run tuvi down)")

    if "OPENROUTER_API_KEY" not in env:
        say("note: OPENROUTER_API_KEY is not set; charts work, the AI chat will fail")

    services: list[Service] = []
    if not args.web_only:
        if port_open(API_PORT):
            return fail(f"port {API_PORT} is busy; stop the other API first")
        services.append(
            Service(
                "api",
                [
                    sys.executable, "-m", "uvicorn", "tuvi_api.main:app",
                    "--reload", "--reload-dir", "apps/api/src", "--reload-dir", "packages",
                    "--host", args.host, "--port", str(API_PORT),
                ],
                cwd=root,
                env=env,
            )
        )
    if not args.api_only:
        if not require("pnpm", "Run `uv run tuvi setup` first."):
            return 1
        if not (root / "apps" / "web" / "node_modules").is_dir():
            return fail("web deps are missing; run `uv run tuvi setup` first")
        if port_open(WEB_PORT):
            return fail(f"port {WEB_PORT} is busy; stop the other web server first")
        web_env = dict(env)
        web_env.setdefault("API_ORIGIN", f"http://127.0.0.1:{API_PORT}")
        services.append(
            Service(
                "web",
                ["pnpm", "dev", "--hostname", args.host, "--port", str(WEB_PORT)],
                cwd=root / "apps" / "web",
                env=web_env,
            )
        )

    if not services:
        return fail("nothing to run")
    if not args.api_only:
        say(f"open http://localhost:{WEB_PORT}  (API docs: http://localhost:{API_PORT}/docs)")
    return run_services(services)


def cmd_down(_: argparse.Namespace) -> int:
    root = repo_root()
    if not require("docker", ""):
        return 1
    return run(["docker", "compose", "down"], cwd=root)


def cmd_check(args: argparse.Namespace) -> int:
    root = repo_root()
    web = root / "apps" / "web"
    # Node 25+ ships a global localStorage that shadows jsdom's in Vitest.
    web_env = dict(os.environ)
    web_env["NODE_OPTIONS"] = f"{web_env.get('NODE_OPTIONS', '')} --no-experimental-webstorage".strip()

    steps: list[tuple[str, list[str], Path, dict[str, str] | None]] = []
    if not args.web_only:
        steps.append(("python tests", ["uv", "run", "pytest", "-q"], root, None))
    if not args.python_only:
        steps += [
            ("web typecheck", ["pnpm", "typecheck"], web, None),
            ("web lint", ["pnpm", "lint"], web, None),
            ("web tests", ["pnpm", "test"], web, web_env),
        ]

    failed = [name for name, command, cwd, env in steps if run(command, cwd=cwd, env=env) != 0]
    if failed:
        return fail("failed: " + ", ".join(failed))
    say("all checks passed")
    return 0


def _streamlit(script: str) -> int:
    root = repo_root()
    return run(
        [sys.executable, "-m", "streamlit", "run", str(root / script)],
        cwd=root,
        env=child_env(root),
    )


def cmd_editor(_: argparse.Namespace) -> int:
    return _streamlit("tools/src/tuvi_tools/cach_cuc/cach_cuc_editor.py")


def cmd_viewer(_: argparse.Namespace) -> int:
    return _streamlit("tools/src/tuvi_tools/chart_viewer.py")


# ----------------------------------------------------------------------------- entry point


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tuvi",
        description="Run the TuviLM stack and checks.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("setup", help="install deps and create local env files").set_defaults(
        func=cmd_setup
    )

    up = commands.add_parser("up", help="start MongoDB, the API and the web app")
    up.add_argument("--no-db", action="store_true", help="do not start MongoDB with Docker")
    only = up.add_mutually_exclusive_group()
    only.add_argument("--api-only", action="store_true", help="start only the API")
    only.add_argument("--web-only", action="store_true", help="start only the web app")
    up.add_argument(
        "--host",
        default="127.0.0.1",
        help="bind address; use 0.0.0.0 to open the app from a phone on the LAN",
    )
    up.set_defaults(func=cmd_up)

    commands.add_parser("down", help="stop MongoDB (data is kept)").set_defaults(func=cmd_down)

    check = commands.add_parser("check", help="run tests, typecheck and lint")
    side = check.add_mutually_exclusive_group()
    side.add_argument("--python-only", action="store_true")
    side.add_argument("--web-only", action="store_true")
    check.set_defaults(func=cmd_check)

    commands.add_parser("editor", help="Streamlit cách cục rule editor").set_defaults(
        func=cmd_editor
    )
    commands.add_parser("viewer", help="Streamlit chart viewer").set_defaults(func=cmd_viewer)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
