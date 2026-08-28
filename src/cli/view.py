"""Schema-agnostic Streamlit viewer for workflow YAML reports."""

from __future__ import annotations

import argparse
import datetime as dt
import subprocess
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import streamlit as st
import yaml

MAX_RENDER_DEPTH = 32
HIDDEN_REPORT_FIELDS = frozenset({"request", "started_at", "input_file"})


def parse_report_yaml(text: str) -> Any:
    """Parse a YAML report without imposing a workflow-specific schema."""
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML report: {exc}") from exc


def load_report(report_path: Path) -> Any:
    return parse_report_yaml(report_path.read_text(encoding="utf-8"))


def _is_sequence(value: Any) -> bool:
    return isinstance(value, (list, tuple, set, frozenset))


def _sequence_items(value: Any) -> list[Any]:
    if isinstance(value, (set, frozenset)):
        return sorted(value, key=repr)
    return list(value)


def _node_summary(value: Any) -> str:
    if isinstance(value, Mapping):
        count = len(value)
        return f"{count} field" if count == 1 else f"{count} fields"
    if _is_sequence(value):
        count = len(value)
        return f"{count} item" if count == 1 else f"{count} items"
    return type(value).__name__


def _display_label(value: Any) -> str:
    label = " ".join(str(value).split()) or "(empty key)"
    if len(label) > 100:
        return f"{label[:97]}..."
    return label


def _render_scalar(value: Any, *, label: str | None, ui: Any) -> None:
    block = ui.container(border=True)
    if label is not None:
        block.caption(label)

    if value is None:
        block.caption("null")
    elif isinstance(value, bool):
        block.write("true" if value else "false")
    elif isinstance(value, str):
        if "\n" in value or len(value) > 120:
            block.markdown(value)
        else:
            block.write(value)
    elif isinstance(value, bytes):
        block.code(value.hex(), language="text")
    elif isinstance(value, (dt.date, dt.datetime, dt.time)):
        block.write(value.isoformat())
    else:
        block.write(value)


def render_yaml_value(
    value: Any,
    *,
    ui: Any = st,
    depth: int = 0,
    _active_ids: set[int] | None = None,
) -> None:
    """Recursively render arbitrary safe-loaded YAML values with Streamlit."""
    if depth > MAX_RENDER_DEPTH:
        ui.warning(f"Maximum render depth ({MAX_RENDER_DEPTH}) reached.")
        return

    is_mapping = isinstance(value, Mapping)
    is_sequence = _is_sequence(value)
    if not is_mapping and not is_sequence:
        _render_scalar(value, label=None, ui=ui)
        return

    active_ids = _active_ids if _active_ids is not None else set()
    object_id = id(value)
    if object_id in active_ids:
        ui.warning("Recursive YAML reference omitted.")
        return
    active_ids.add(object_id)

    try:
        if is_mapping:
            if not value:
                ui.caption("Empty mapping")
                return
            for key, child in value.items():
                label = _display_label(key)
                if isinstance(child, Mapping) or _is_sequence(child):
                    section = ui.expander(
                        f"{label} · {_node_summary(child)}",
                        expanded=True,
                    )
                    render_yaml_value(
                        child,
                        ui=section,
                        depth=depth + 1,
                        _active_ids=active_ids,
                    )
                else:
                    _render_scalar(child, label=label, ui=ui)
            return

        items = _sequence_items(value)
        if not items:
            ui.caption("Empty sequence")
            return
        for index, child in enumerate(items, start=1):
            label = f"Item {index}"
            if isinstance(child, Mapping) or _is_sequence(child):
                section = ui.expander(
                    f"{label} · {_node_summary(child)}",
                    expanded=True,
                )
                render_yaml_value(
                    child,
                    ui=section,
                    depth=depth + 1,
                    _active_ids=active_ids,
                )
            else:
                _render_scalar(child, label=label, ui=ui)
    finally:
        active_ids.remove(object_id)


def _raw_yaml(value: Any) -> str:
    return yaml.safe_dump(value, allow_unicode=True, sort_keys=False)


def _load_uploaded_report(uploaded_file: Any) -> Any:
    try:
        text = uploaded_file.getvalue().decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("The uploaded report must be UTF-8 text.") from exc
    return parse_report_yaml(text)


def _visible_report_metadata(report: Any) -> Any:
    """Hide runner bookkeeping while preserving unknown report metadata."""
    if not isinstance(report, Mapping):
        return report
    return {
        key: value
        for key, value in report.items()
        if key != "results" and key not in HIDDEN_REPORT_FIELDS
    }


def _profile_results(report: Any) -> list[Mapping[Any, Any]] | None:
    """Recognize the generic batch envelope without inspecting workflow output."""
    if not isinstance(report, Mapping) or "results" not in report:
        return None
    raw_results = report["results"]
    if not _is_sequence(raw_results):
        return None
    results = _sequence_items(raw_results)
    if not all(isinstance(item, Mapping) and "profile" in item for item in results):
        return None
    return results


def _profile_label(result: Mapping[Any, Any], index: int) -> str:
    profile = result.get("profile")
    if isinstance(profile, Mapping):
        name = profile.get("name")
        if name is not None and str(name).strip():
            return str(name).strip()
    return f"Profile {index + 1}"


def _profile_payload(result: Mapping[Any, Any]) -> Any:
    """Return only the selected workflow output, never the input lá số."""
    if "output" in result:
        return result["output"]
    if "error" in result:
        return {"error": result["error"]}
    return {key: value for key, value in result.items() if key != "profile"}


def streamlit_main(argv: Sequence[str] | None = None) -> None:
    """Render either the CLI-provided report or an uploaded YAML report."""
    forwarded_args = list(sys.argv[1:] if argv is None else argv)
    st.set_page_config(
        page_title="TuviLM report viewer",
        page_icon="📄",
        layout="wide",
    )
    st.title("Workflow report viewer")
    st.caption(
        "Schema-independent YAML rendering. New workflow output shapes require "
        "no UI changes."
    )

    if len(forwarded_args) > 1:
        st.error("Expected at most one report path after Streamlit's `--` separator.")
        return

    initial_path = Path(forwarded_args[0]) if forwarded_args else None
    st.sidebar.header("Report source")
    uploaded_file = st.sidebar.file_uploader(
        "Upload YAML",
        type=("yaml", "yml"),
        help="An uploaded file overrides the report path passed on the command line.",
    )

    try:
        if uploaded_file is not None:
            report = _load_uploaded_report(uploaded_file)
            source_name = uploaded_file.name
            source_detail = "Uploaded file"
        elif initial_path is not None:
            report = load_report(initial_path)
            source_name = initial_path.name
            source_detail = str(initial_path.resolve())
        else:
            st.info("Upload a YAML report in the sidebar to begin.")
            return
    except (OSError, ValueError) as exc:
        st.error(str(exc))
        return

    st.sidebar.caption(source_detail)
    st.subheader(source_name)

    profile_results = _profile_results(report)
    if profile_results is None:
        visible_report = _visible_report_metadata(report)
        render_yaml_value(visible_report)
        raw_value = visible_report
    elif not profile_results:
        st.info("This report does not contain any profile results yet.")
        raw_value = {}
    else:
        st.sidebar.header("Profile")
        selected_index = st.sidebar.selectbox(
            "Choose a profile",
            options=range(len(profile_results)),
            format_func=lambda index: _profile_label(profile_results[index], index),
        )
        selected_result = profile_results[selected_index]
        selected_label = _profile_label(selected_result, selected_index)
        selected_payload = _profile_payload(selected_result)

        metadata = _visible_report_metadata(report)
        if metadata:
            with st.expander("Report details"):
                render_yaml_value(metadata)

        st.subheader(selected_label)
        render_yaml_value(selected_payload)
        raw_value = selected_payload

    with st.expander("Raw YAML for current view"):
        st.code(_raw_yaml(raw_value), language="yaml")


def build_streamlit_command(
    report_path: Path | None,
    *,
    port: int | None = None,
    address: str | None = None,
    headless: bool = False,
    executable: str | None = None,
) -> list[str]:
    """Build the subprocess command used by the report-view CLI."""
    command = [
        executable or sys.executable,
        "-m",
        "streamlit",
        "run",
    ]
    if port is not None:
        command.extend(("--server.port", str(port)))
    if address is not None:
        command.extend(("--server.address", address))
    if headless:
        command.extend(("--server.headless", "true"))
    command.append(str(Path(__file__).resolve()))
    if report_path is not None:
        command.extend(("--", str(report_path.resolve())))
    return command


def build_cli_parser(*, prog: str | None = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=prog,
        description="Open a workflow YAML report in the dynamic Streamlit viewer.",
    )
    parser.add_argument(
        "report",
        type=Path,
        nargs="?",
        help="Report YAML path. Omit it to select a file in the browser.",
    )
    parser.add_argument("--port", type=int, help="Streamlit server port.")
    parser.add_argument("--address", help="Streamlit server address.")
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run Streamlit without opening a browser.",
    )
    return parser


def cli_main(
    argv: Sequence[str] | None = None,
    *,
    prog: str | None = None,
) -> int:
    parser = build_cli_parser(prog=prog)
    args = parser.parse_args(argv)
    if args.report is not None and not args.report.is_file():
        parser.error(f"report file does not exist: {args.report}")
    if args.port is not None and not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")

    command = build_streamlit_command(
        args.report,
        port=args.port,
        address=args.address,
        headless=args.headless,
    )
    try:
        return subprocess.call(command)
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    streamlit_main()
