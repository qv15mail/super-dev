# Pipeline Observability + Rehearsal Design

## Context

The project already had end-to-end generation, red-team, quality gate, and delivery packaging. The main gaps were:

1. low runtime visibility for each pipeline stage
2. no standardized launch rehearsal outputs
3. requirement intelligence lacked persistent, traceable cache outputs

## Decisions

### 1. Pipeline telemetry as first-class artifact

Added a dedicated telemetry model (`PipelineTelemetryReport`) that records:

- stage id + title
- success/failure status
- stage duration
- stage-level details
- total duration + overall success rate

Outputs are written to:

- `output/<project>-pipeline-metrics.json`
- `output/<project>-pipeline-metrics.md`

This is integrated directly in CLI pipeline execution path so stage metrics are available for both success and failure exits.

### 2. Rehearsal docs generated from deploy command

Added `LaunchRehearsalGenerator` and a new CLI option:

- `super-dev deploy --rehearsal`

It generates:

- launch rehearsal plan
- rollback playbook
- smoke checklist

These artifacts provide an operational release rehearsal baseline before production rollout.

### 3. Knowledge bundle persistence and citation trace

`KnowledgeAugmenter` now enriches output with:

- `generated_at`
- `citations.local`
- `citations.web`

And supports bundle persistence:

- `output/knowledge-cache/<project>-knowledge-bundle.json`

This provides requirement augmentation traceability and repeatability.

### 4. Quality gate extension

Code quality checks now include:

- pipeline observability artifact validation
- launch rehearsal artifact validation

This makes observability and release rehearsal part of quality governance.

## Tradeoffs

- Chose file-based metrics for simplicity and portability over introducing a DB.
- Rehearsal is template/checklist driven first; no active probe execution yet.
- Telemetry currently measures local stage runtime; no distributed trace correlation yet.

## Follow-ups

1. Add trend analysis across multiple pipeline runs.
2. Add cost telemetry (token estimate / LLM call budget).
3. Add automated launch rehearsal execution mode (not only docs).
