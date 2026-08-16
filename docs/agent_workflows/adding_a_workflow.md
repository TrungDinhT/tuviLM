# Adding an agent workflow

This document defines the repository standard for adding a specialized workflow
under `src/agent/workflow/`. The personality workflow is the reference example.

## What a workflow owns

A workflow owns four things:

1. One or more named input contracts.
2. One composite tool for each input contract.
3. Agent reasoning instructions and output instructions.
4. A runner and, when the main agent must delegate to it, one composite workflow
   tool.

A workflow does not own deployment configuration such as model credentials,
book directories, database URLs, or mounted assets. Those belong in application
settings and dependencies. A workflow may document that it requires a resource,
but it must not hardcode the resource location.

## Reference layout

```text
src/agent/workflow/<workflow_name>/
|-- __init__.py
|-- agent.py
|-- input/
|   |-- __init__.py
|   `-- <input_name>.py
`-- output/
    |-- __init__.py
    `-- <output_instruction_name>.py
```

Use valid Python module names. A stable registry key may start with a number,
but a file name must use words, for example `seven_foundation_questions.py`
with registry key `7_foundation_questions`.

Shared definitions live in `src/agent/workflow/contracts.py`:

- `WorkflowInputDefinition` binds an input model to its builder tool,
  instructions, and supporting tools.
- `WorkflowOutputInstruction` binds response instructions to the agent's
  enforced output type.

## Input contracts

An input contract is a Pydantic model containing the evidence that a workflow
actually consumes. It is a projection, not necessarily a copy of every shared
tool payload.

Shared tools may return more information than one workflow needs. Input models
should therefore allow or ignore extra fields deliberately. Declared fields
remain the contract: they must have types, required/optional status, and stable
meaning. Do not add a field merely because the source tool currently returns it.

Every registered input contract must have exactly one composite builder tool:

```python
class CareerEvidence(BaseModel):
    model_config = ConfigDict(extra="ignore")

    foundation: FoundationEvidence
    career_palace: CareerPalaceEvidence


def get_career_evidence(
    ctx: RunContext[TuviAgentDeps],
) -> CareerEvidence:
    la_so = ctx.deps.require_la_so()
    return CareerEvidence(
        foundation=FoundationEvidence.model_validate(
            build_laso_foundation_payload(la_so)
        ),
        career_palace=build_career_palace_evidence(la_so),
    )
```

Lower-level builder functions may be shared internally. The composite tool is
the only public path that promises to build the complete input contract. Do not
also collect and serialize the same input in the workflow runner.

Register the contract and its tool together:

```python
WorkflowInputDefinition(
    name="default",
    model=CareerEvidence,
    tool=get_career_evidence,
    instructions=(CAREER_REASONING_INSTRUCTION,),
    supporting_tools=(get_laso_foundation, get_cung_by_role),
)
```

The model type documents and tests the tool result. The agent instruction must
tell the sub-agent to call the composite input tool before reasoning.

## Tool placement and sharing

A tool may be exposed to:

- The main agent only, when it supports broad routing or general questions.
- A workflow sub-agent only, when it is implementation detail of that workflow.
- Both, when both agents have a legitimate independent use for it.

Do not infer placement from the module where the tool is implemented. Decide it
from agent responsibilities. In particular, the main agent should normally see
one composite workflow tool, while the sub-agent sees the input builder and any
supporting tools it needs.

Register supporting tools on the input definition instead of hardcoding them in
the generic agent assembly. This keeps each input source responsible for the
tools and instructions needed to interpret its own contract.

## Instructions and research prompts

Keep three instruction layers separate:

1. Workflow base instructions: safety and behavior common to every input/output
   combination.
2. Input instructions: how to reason over one input contract.
3. Output instructions: how to organize and express the result.

Prompt research often needs inactive variants. It is acceptable to keep an
unused prompt fragment when it is clearly marked, for example:

```python
OPTIONAL_HIDE_TECHNICAL_EVIDENCE_INSTRUCTION = """..."""
```

Optional or experimental fragments must not be silently included. Their module
should state whether they are active, and an experiment must compose them
explicitly. Tests should assert both the default composition and the experiment
composition being evaluated. Remove abandoned variants after the research
decision is made.

## Output instruction and output type

Do not call a prompt an output schema. Use `WorkflowOutputInstruction`:

```python
WorkflowOutputInstruction(
    name="summary",
    instruction=SUMMARY_OUTPUT_INSTRUCTION,
    output_type=str,
)
```

The instruction is always text given to the model. The output type is a separate
contract and may be:

- `str` for natural-language output.
- A Pydantic model for structured output.

When using a structured output type, the runner and its caller must preserve
that structure or render it explicitly. Do not type the runner as `str` and then
silently stringify a structured result.

## Configuration lifecycle

Select the input and output instruction when building the sub-agent. Treat that
selection as immutable for the agent's lifetime. Do not override the input in
the runner, because the agent instructions and tool set were composed for the
build-time input.

Resource locations are a separate concern:

- Define them in application settings.
- Pass resolved resources or paths through dependencies.
- Validate required resources at application startup when practical.
- Keep unit tests independent of machine-specific paths.

## Runner and conversation history

The runner invokes the already configured sub-agent. The sub-agent calls its
input builder tool; the runner must not build the same evidence again.

```python
result = await workflow_agent.run(
    request,
    deps=deps,
    usage=usage,
    message_history=message_history,
)
return result.output
```

Nested workflows must receive confirmed conversation history. Otherwise a
follow-up such as "expand the third point" loses the response it refers to.
For API chat, construct model history once, store it on the request-scoped
dependencies, pass it to the main agent, and pass the same history to any nested
workflow.

Do not copy the current in-progress tool-call messages from `RunContext`; pass
the clean user/assistant history prepared by the application boundary.

## Integration checklist

When adding a workflow:

1. Create its input model and composite builder tool.
2. Create its input and output-instruction registry entries.
3. Build the sub-agent from one immutable configuration.
4. Add a dependency field and `require_<workflow>_agent` method when the main
   agent delegates to it.
5. Construct the sub-agent in application startup using application settings.
6. Add one composite workflow tool to the main agent.
7. Add a routing instruction telling the main agent when to use that tool and
   how to handle its result.
8. Export only the workflow's supported public API.
9. Pass request-scoped chart data, resources, usage, and conversation history.

## Required tests

At minimum, test:

- The composite input tool returns the declared Pydantic model.
- Required fields, optional fields, and intentional extra-field behavior.
- Each input definition has exactly one builder tool.
- Registry defaults and unknown-name failures.
- Default prompt composition and any active research variant.
- Output instruction selection and output type.
- The runner forwards request, dependencies, usage, and conversation history.
- The main agent exposes the composite workflow tool.
- The sub-agent exposes its input builder and declared supporting tools.
- API request-scoped dependencies preserve the same clean message history passed
  to the main agent.

Prefer public library APIs in tests. If a dependency exposes no public way to
inspect registered tools, isolate the compatibility assertion so a library
upgrade has one obvious repair point.
