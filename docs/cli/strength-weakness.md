# Strength and weakness CLI

Run commands from the repository root after `uv sync`. Set the API key required
by your selected Pydantic AI provider (for example, `OPENAI_API_KEY` when using
`--model openai:gpt-5.4-mini`).

Create `profiles.yaml` with a list of solar birth dates and integer hours:

```yaml
- name: Example
  birth_date: 1990-05-15
  birth_time: 10
  gender: male
```

```sh
uv run python -m src.cli.main run --list-workflows
uv run python -m src.cli.main run profiles.yaml \
  --workflow strength_weakness \
  --model openai:gpt-5.4-mini \
  --book-root data/tuvitanbien_chunking_compact/part_2 \
  --output report.yaml
uv run python -m src.cli.main view report.yaml
```

The book directory must contain the locally provisioned Tân Biên Markdown
sections; the book corpus is not checked into Git. `--book-root` can point to
another copy of that corpus. `TUVILM_WORKFLOW_MODEL` sets the default model.

The runner checkpoints each profile to YAML, continues after individual
failures, and exits with code 1 if any profile failed. The report includes each
profile's structured result or error and a completion summary. The `view`
command starts a Streamlit report viewer; use `--headless` on a remote machine.

The available workflows are `strength_weakness` and `personality`. Select either
with `--workflow`, or omit it to choose interactively. Further workflows can be
registered through `WorkflowDefinition`.
