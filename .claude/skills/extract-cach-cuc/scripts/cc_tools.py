#!/usr/bin/env python3
"""cc_tools — deterministic helpers for the extract-cach-cuc skill.

Subcommands:
  vocab                       Dump canonical ids (stars, roles, chi, can, brightness, scopes, groups).
  validate <file...>          Pydantic-validate file(s); report duplicate ids + unknown star ids.
  dedup    <file...>          Detect records with semantically identical conditions (across the union).
  check    <tmp> <reviewed>   Preflight gate: validate both, id clashes, cross-file condition collisions.
  append   <tmp> <reviewed>   Append tmp records into reviewed (textual, format-preserving) iff check passes.

Exit code is non-zero when a problem is found, so the skill can gate on it.
Run from anywhere; the repo root is auto-detected.
"""
from __future__ import annotations

import argparse
import enum
import json
import os
import sys
from collections import Counter, defaultdict
from typing import Any, get_args


def find_repo_root(start: str) -> str:
    p = os.path.abspath(start)
    while p != os.path.dirname(p):
        if os.path.isdir(os.path.join(p, "support_tool")) and os.path.isdir(os.path.join(p, "src")):
            return p
        p = os.path.dirname(p)
    raise SystemExit("cc_tools: could not locate repo root (no support_tool/ + src/ ancestor)")


ROOT = find_repo_root(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
DATA_DIR = os.path.join(ROOT, "src", "refactored", "components", "data")

import yaml  # noqa: E402  (after sys.path setup)
from support_tool.cach_cuc.condition_models import CachCucData  # noqa: E402
from support_tool.cach_cuc import condition_models as cm  # noqa: E402


# ----------------------------------------------------------------------------- helpers
def _load_yaml(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _members(t: Any) -> list[str]:
    """Enum members or Literal args -> list of string values."""
    if isinstance(t, type) and issubclass(t, enum.Enum):
        return [str(e.value) for e in t]
    args = get_args(t)
    if args:
        return [str(a) for a in args]
    return []


def _read_json(name: str) -> list[dict]:
    with open(os.path.join(DATA_DIR, name), encoding="utf-8") as fh:
        return json.load(fh)


def canon(x: Any) -> Any:
    """Order-insensitive canonical form: sort dict keys AND list members by their JSON repr.

    Lists in the condition model (stars / chi / brightness / can / all|any children) carry no
    semantic order, so sorting members makes [a,b] and [b,a] compare equal.
    """
    if isinstance(x, dict):
        return {k: canon(x[k]) for k in sorted(x)}
    if isinstance(x, list):
        items = [canon(i) for i in x]
        return sorted(items, key=lambda v: json.dumps(v, ensure_ascii=False, sort_keys=True))
    return x


def cond_key(record: dict) -> str:
    return json.dumps(canon(record.get("conditions")), ensure_ascii=False, sort_keys=True)


def _records(path: str) -> list[dict]:
    return _load_yaml(path).get("cach_cuc", []) or []


# star ids may appear as free strings in conditions; pydantic does not enum-check them.
_STAR_REF_LIST_KEYS = ("stars",)  # leaves carrying a list of star ids
_STAR_REF_SCALAR_KEYS = ("star",)  # leaves carrying a single star id (only_chinh_tinh)


def _valid_star_ids() -> set[str]:
    stars = _read_json("sao.json") + _read_json("tuhoa.json")
    ids = {s["id"] for s in stars}
    ids |= {"tuan", "triet"}  # special stars, same as vocab
    return ids


def _walk_conditions(cond: Any):
    """Yield every leaf-condition dict in a conditions tree (descend all/any/not)."""
    if not isinstance(cond, dict):
        return
    for combinator in ("all", "any"):
        if combinator in cond:
            for child in cond[combinator] or []:
                yield from _walk_conditions(child)
            return
    if "not" in cond:
        yield from _walk_conditions(cond["not"])
        return
    yield cond


def _star_refs(cond: Any) -> list[str]:
    refs: list[str] = []
    for leaf in _walk_conditions(cond):
        for key in _STAR_REF_LIST_KEYS:
            val = leaf.get(key)
            if isinstance(val, list):
                refs += [s for s in val if isinstance(s, str)]
        for key in _STAR_REF_SCALAR_KEYS:
            val = leaf.get(key)
            if isinstance(val, str):
                refs.append(val)
    return refs


def _unknown_star_ids(data: dict, valid: set[str]) -> dict[str, list[str]]:
    """Map record id (or 'groups:<name>') -> sorted unknown star ids referenced."""
    bad: dict[str, list[str]] = {}
    for rec in data.get("cach_cuc", []) or []:
        unknown = sorted({s for s in _star_refs(rec.get("conditions")) if s not in valid})
        if unknown:
            bad[rec.get("id", "?")] = unknown
    for name, grp in (data.get("groups", {}) or {}).items():
        stars = (grp or {}).get("stars", []) if isinstance(grp, dict) else []
        unknown = sorted({s for s in stars if isinstance(s, str) and s not in valid})
        if unknown:
            bad[f"groups:{name}"] = unknown
    return bad


# ----------------------------------------------------------------------------- commands
def cmd_vocab(_args) -> int:
    stars = _read_json("sao.json") + _read_json("tuhoa.json")
    roles = _read_json("cung_role.json")
    out = {
        "stars": {s["id"]: s.get("name", "") for s in stars},
        "roles": {r["id"]: r.get("name", "") for r in roles},
        "special_stars": {"tuan": "Tuần", "triet": "Triệt"},
        "chi": _members(cm.DiaChi),
        "can": _members(cm.ThienCan),
        "brightness": _members(cm.Brightness),
        "scopes": _members(cm.Scope),
        "group_names": _members(cm.GroupName),
        "modes": _members(cm.Mode),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=False))
    return 0


def _validate_file(path: str) -> tuple[bool, list[str]]:
    msgs: list[str] = []
    data = _load_yaml(path)
    try:
        m = CachCucData.model_validate(data)
    except Exception as exc:  # pydantic ValidationError or yaml issue
        return False, [f"{path}: INVALID\n{exc}"]
    ids = [c.id for c in m.cach_cuc]
    dups = {k: v for k, v in Counter(ids).items() if v > 1}
    bad_stars = _unknown_star_ids(data, _valid_star_ids())
    ok = not dups and not bad_stars
    msgs.append(
        f"{path}: OK {len(ids)} records"
        + ("" if not dups else f"  | DUPLICATE ids: {dups}")
        + ("" if not bad_stars else f"  | UNKNOWN star ids: {bad_stars}")
    )
    return ok, msgs


def cmd_validate(args) -> int:
    ok_all = True
    for p in args.files:
        ok, msgs = _validate_file(p)
        ok_all &= ok
        print("\n".join(msgs))
    return 0 if ok_all else 1


def _collisions(records_by_src: list[tuple[str, dict]]) -> list[list[tuple[str, str, str]]]:
    groups: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for src, rec in records_by_src:
        groups[cond_key(rec)].append((src, rec.get("id", "?"), rec.get("meaning", "")))
    return [v for v in groups.values() if len(v) > 1]


def cmd_dedup(args) -> int:
    pairs: list[tuple[str, dict]] = []
    for p in args.files:
        for rec in _records(p):
            pairs.append((os.path.basename(p), rec))
    coll = _collisions(pairs)
    if not coll:
        print("no condition collisions across:", ", ".join(args.files))
        return 0
    print(f"{len(coll)} collision group(s) — identical conditions:")
    for grp in coll:
        for src, rid, mean in grp:
            print(f"  [{src}] {rid}  ::  {mean}")
        print()
    return 1


def cmd_check(args) -> int:
    tmp, reviewed = args.tmp, args.reviewed
    problems = 0

    for p in (reviewed, tmp):
        ok, msgs = _validate_file(p)
        print("\n".join(msgs))
        if not ok:
            problems += 1

    tmp_ids = [c.get("id") for c in _records(tmp)]
    rev_ids = {c.get("id") for c in _records(reviewed)}
    clash = sorted({i for i in tmp_ids if i in rev_ids})
    if clash:
        problems += 1
        print(f"ID CLASH (tmp vs reviewed): {clash}")
    else:
        print("id clash: none")

    pairs = [("reviewed", r) for r in _records(reviewed)] + [("tmp", r) for r in _records(tmp)]
    coll = _collisions(pairs)
    if coll:
        problems += 1
        print(f"CONDITION COLLISIONS: {len(coll)} group(s) — merge before append:")
        for grp in coll:
            for src, rid, mean in grp:
                print(f"  [{src}] {rid}  ::  {mean}")
            print()
    else:
        print("condition collisions: none")

    print("CHECK:", "PASS" if problems == 0 else f"FAIL ({problems} issue group(s))")
    return 0 if problems == 0 else 1


def cmd_append(args) -> int:
    tmp, reviewed = args.tmp, args.reviewed
    if cmd_check(args) != 0:
        print("append aborted: check failed.")
        return 1

    with open(tmp, encoding="utf-8") as fh:
        lines = fh.readlines()
    # drop everything up to and including the top-level `cach_cuc:` header line
    start = None
    for i, ln in enumerate(lines):
        if ln.rstrip("\n").strip() == "cach_cuc:":
            start = i + 1
            break
    if start is None:
        print(f"append aborted: no top-level 'cach_cuc:' header found in {tmp}")
        return 1
    body = "".join(lines[start:]).strip("\n")
    if not body.strip():
        print("append aborted: tmp has no records under cach_cuc:.")
        return 1

    with open(reviewed, encoding="utf-8") as fh:
        cur = fh.read()
    if not cur.endswith("\n"):
        cur += "\n"
    with open(reviewed, "w", encoding="utf-8") as fh:
        fh.write(cur + body + "\n")

    print(f"appended tmp records into {reviewed}. re-checking merged file...")
    ok, msgs = _validate_file(reviewed)
    print("\n".join(msgs))
    pairs = [("reviewed", r) for r in _records(reviewed)]
    coll = _collisions(pairs)
    if coll:
        print(f"WARNING: merged file has {len(coll)} condition collision group(s).")
        ok = False
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(prog="cc_tools", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("vocab", help="dump canonical ids").set_defaults(fn=cmd_vocab)

    p = sub.add_parser("validate", help="pydantic-validate file(s); report dup ids + unknown star ids")
    p.add_argument("files", nargs="+")
    p.set_defaults(fn=cmd_validate)

    p = sub.add_parser("dedup", help="detect identical-condition collisions across files")
    p.add_argument("files", nargs="+")
    p.set_defaults(fn=cmd_dedup)

    p = sub.add_parser("check", help="preflight gate: validate + id clash + collisions")
    p.add_argument("tmp")
    p.add_argument("reviewed")
    p.set_defaults(fn=cmd_check)

    p = sub.add_parser("append", help="append tmp into reviewed iff check passes")
    p.add_argument("tmp")
    p.add_argument("reviewed")
    p.set_defaults(fn=cmd_append)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
