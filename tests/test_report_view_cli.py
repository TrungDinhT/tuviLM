from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

import pytest
from streamlit.testing.v1 import AppTest

from src.cli.view import (
    build_streamlit_command,
    parse_report_yaml,
    render_yaml_value,
)


class RecordingUI:
    def __init__(self, events: list[tuple[str, Any]] | None = None):
        self.events = events if events is not None else []

    def container(self, **kwargs: Any) -> RecordingUI:
        self.events.append(("container", kwargs))
        return RecordingUI(self.events)

    def expander(self, label: str, **kwargs: Any) -> RecordingUI:
        self.events.append(("expander", (label, kwargs)))
        return RecordingUI(self.events)

    def caption(self, value: Any) -> None:
        self.events.append(("caption", value))

    def markdown(self, value: Any) -> None:
        self.events.append(("markdown", value))

    def write(self, value: Any) -> None:
        self.events.append(("write", value))

    def code(self, value: Any, **kwargs: Any) -> None:
        self.events.append(("code", (value, kwargs)))

    def warning(self, value: Any) -> None:
        self.events.append(("warning", value))


def _run_report_app(report_path: str) -> None:
    from src.cli.view import streamlit_main

    streamlit_main((report_path,))


def test_parse_report_yaml_keeps_an_unknown_nested_output_shape():
    report = parse_report_yaml(
        """
future_workflow_output:
  phases:
    - name: synthesis
      metrics:
        confidence: 0.82
        active: true
        note: null
  narrative: |
    ## Dynamic section
    Arbitrary Markdown remains intact.
""".strip()
    )

    assert report["future_workflow_output"]["phases"][0]["metrics"] == {
        "confidence": 0.82,
        "active": True,
        "note": None,
    }
    assert report["future_workflow_output"]["narrative"].startswith(
        "## Dynamic section"
    )


def test_dynamic_renderer_visits_arbitrary_mappings_sequences_and_scalars():
    report = {
        "new_output": {
            "sections": [
                {
                    "title": "Overview",
                    "body": "## Heading\nNarrative",
                    "score": 4.5,
                    "published": True,
                    "reviewed_at": dt.date(2026, 8, 26),
                }
            ]
        }
    }
    ui = RecordingUI()

    render_yaml_value(report, ui=ui)

    rendered = repr(ui.events)
    assert "new_output" in rendered
    assert "sections" in rendered
    assert "title" in rendered
    assert "## Heading\\nNarrative" in rendered
    assert "score" in rendered
    assert "published" in rendered
    assert "2026-08-26" in rendered


def test_parse_report_yaml_rejects_invalid_yaml():
    with pytest.raises(ValueError, match="Invalid YAML report"):
        parse_report_yaml("output: [unterminated")


def test_streamlit_command_forwards_server_options_and_report_path(
    tmp_path: Path,
):
    report_path = tmp_path / "report.yaml"

    command = build_streamlit_command(
        report_path,
        port=8765,
        address="127.0.0.1",
        headless=True,
        executable="python-test",
    )

    assert command[:4] == [
        "python-test",
        "-m",
        "streamlit",
        "run",
    ]
    assert command[4:] == [
        "--server.port",
        "8765",
        "--server.address",
        "127.0.0.1",
        "--server.headless",
        "true",
        str(Path("src/cli/view.py").resolve()),
        "--",
        str(report_path.resolve()),
    ]


def test_streamlit_app_renders_report_passed_on_the_command_line(tmp_path: Path):
    report_path = tmp_path / "future-report.yaml"
    report_path.write_text(
        """
brand_new_shape:
  entries:
    - heading: First result
      narrative: |
        ## Future narrative
        Rendered without a workflow-specific component.
""".strip(),
        encoding="utf-8",
    )
    app = AppTest.from_function(
        _run_report_app,
        default_timeout=5,
        args=(str(report_path),),
    )

    app.run()

    assert not app.exception
    assert app.title[0].value == "Workflow report viewer"
    assert any("Future narrative" in element.value for element in app.markdown)


def test_streamlit_app_selects_and_renders_one_profile_at_a_time(tmp_path: Path):
    report_path = tmp_path / "batch-report.yaml"
    report_path.write_text(
        """
workflow: future_workflow
request: hidden request
started_at: 2026-08-26T08:00:00+02:00
input_file: profiles.yaml
results:
  - profile:
      name: Khanh
      birth_time: 8
    output:
      narrative: Khanh output only
      dynamic_section:
        score: 8
  - profile:
      name: Dung
      birth_time: 14
    output:
      narrative: Dung output only
      another_future_shape:
        tags: [careful, focused]
""".strip(),
        encoding="utf-8",
    )
    app = AppTest.from_function(
        _run_report_app,
        default_timeout=5,
        args=(str(report_path),),
    )

    app.run()

    assert not app.exception
    assert len(app.selectbox) == 1
    assert app.selectbox[0].value == 0
    rendered = repr(
        [element.value for element in (*app.markdown, *app.caption, *app.code)]
    )
    assert "Khanh output only" in rendered
    assert "Dung output only" not in rendered
    assert "birth_time" not in rendered
    assert "hidden request" not in rendered
    assert "profiles.yaml" not in rendered

    app.selectbox[0].select(1).run()

    assert not app.exception
    rendered = repr(
        [element.value for element in (*app.markdown, *app.caption, *app.code)]
    )
    assert "Dung output only" in rendered
    assert "Khanh output only" not in rendered
    assert "another_future_shape" in rendered
