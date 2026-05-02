# Tu Vi Agent Evals

This folder contains the Pydantic Evals setup for the Tu Vi agent in
`src/agent/main.py`.

Each eval case gives the agent:

- a `TuviTime`, used to build the `TinhBan`/la so before the agent runs
- a natural-language `query`

The task returns an `AgentResult` with:

- `output`: the model answer
- `tools_used`: tool names extracted from Pydantic AI messages
- `usage`: token/model usage when available
- `messages`: JSON-safe Pydantic AI run messages

## Run Evals

Install dependencies first:

```bash
poetry install
```

Run the default dataset:

```bash
poetry run python -m src.evals.cli run
```

The default dataset path is:

```text
src/evals/data.yaml
```

Run a custom dataset:

```bash
poetry run python -m src.evals.cli run --data path/to/data.yaml
```

Run one or more named cases:

```bash
poetry run python -m src.evals.cli run --case menh_overview
poetry run python -m src.evals.cli run --case menh_overview --case quan_loc_career
```

Use a different model:

```bash
poetry run python -m src.evals.cli run --model openai:gpt-4.1-mini
```

Save the report to JSON:

```bash
poetry run python -m src.evals.cli run -o reports/tuvi-eval.json
```

Useful options:

```bash
poetry run python -m src.evals.cli run --include-output
poetry run python -m src.evals.cli run --hide-reasons
poetry run python -m src.evals.cli run --max-concurrency 2
poetry run python -m src.evals.cli run --repeat 3
```

## Render A Saved Report

Render a report saved with `run -o`:

```bash
poetry run python -m src.evals.cli render reports/tuvi-eval.json
```

Hide inputs or assertion reasons:

```bash
poetry run python -m src.evals.cli render reports/tuvi-eval.json --no-include-input
poetry run python -m src.evals.cli render reports/tuvi-eval.json --hide-reasons
```

Show model outputs:

```bash
poetry run python -m src.evals.cli render reports/tuvi-eval.json --include-output
```

## Dataset Format

A dataset is a YAML file with a top-level `name` and a `cases` list.

```yaml
name: tuvi_agent_eval
cases:
  - name: menh_overview
    inputs:
      tuvi_time:
        hour: Tý
        date: 10
        month: 3
        thien_can: Giấp
        dia_chi: Tý
        gender: M
      query: Luận giải ngắn gọn cung Mệnh, tập trung vào chính tinh và điểm cần thận trọng.
    expected_output:
      min_output_chars: 120
      required_substrings:
        - Mệnh
      forbidden_substrings:
        - tôi không có dữ liệu
      required_tools:
        - get_cung_analyze_skill
        - get_cung_by_role
    metadata:
      topic: cung_menh
```

## Case Fields

`name`

Unique case name. Use this with `--case`.

`inputs.tuvi_time`

The lunar Tu Vi birth time used by `Builder().build(...)`.

Required fields:

- `hour`: one of `Tý`, `Sửu`, `Dần`, `Mão`, `Thìn`, `Tị`, `Ngọ`, `Mùi`, `Thân`, `Dậu`, `Tuất`, `Hợi`
- `date`: lunar day as an integer
- `month`: lunar month as an integer
- `thien_can`: one of `Giấp`, `Ất`, `Bính`, `Đinh`, `Mậu`, `Kỷ`, `Canh`, `Tân`, `Nhâm`, `Quý`
- `dia_chi`: one of `Tý`, `Sửu`, `Dần`, `Mão`, `Thìn`, `Tị`, `Ngọ`, `Mùi`, `Thân`, `Dậu`, `Tuất`, `Hợi`
- `gender`: `M` or `F`

`inputs.query`

The user question sent to the Tu Vi agent after the chart is built.

`expected_output`

Optional deterministic checks:

- `min_output_chars`: minimum answer length, default `80`
- `required_substrings`: strings that must appear in the answer
- `forbidden_substrings`: strings that must not appear in the answer
- `required_tools`: Pydantic AI tool names that must be used

`metadata`

Optional free-form metadata for grouping and later analysis.

## Evaluator Output

The CLI prints each assertion by name, for example:

```text
structured_result: ✔
non_empty_output: ✔
contains:Mệnh: ✔
used_tool:get_cung_by_role: ✗
```

If a check fails, the reason line explains what was missing. For example,
tool checks print the captured tool list.

## Files

- `cli.py`: `cyclopts` CLI with `run` and `render`
- `dataset.py`: YAML loader that builds a Pydantic Evals `Dataset`
- `tasks.py`: builds the chart and runs the Tu Vi agent
- `evaluators.py`: deterministic assertion checks
- `schema.py`: typed inputs, expected output, and structured agent result
