# Prompt Uplifting: Neuro Patient Tracker

This document details the prompt engineering improvements applied to all 7 agent system prompts and 4 orchestrator task prompts in the Neuro Patient Tracker multi-agent system.

## Summary of Changes

| Technique | Before | After | Impact |
|-----------|--------|-------|--------|
| Chain-of-Thought (CoT) | Not used | All 7 agents have step-by-step reasoning processes | More systematic, reproducible clinical reasoning |
| Few-Shot Examples | Not used | All 7 agents include complete input/output examples | Consistent output format and quality |
| Structured Output | Informal | All agents have defined response templates | Parseable, predictable outputs |
| Self-Review / Self-Critique | Not used | All agents have verification checklists | Reduced hallucination and missed items |
| Confidence Calibration | Mentioned only in Prognosis | All clinical agents must state confidence levels | Transparent uncertainty communication |
| Reference Tables | Scattered knowledge | QA Validator and Neurologist have explicit lookup tables | More accurate validation |
| Behavioral Guardrails | Basic disclaimers | Explicit "Critical Rules" sections with specific prohibitions | Stronger safety boundaries |
| Role Depth | Generic role descriptions | Detailed expertise with years of experience | Better role adherence |
| Orchestrator Prompts | Generic task descriptions | Structured instructions with agent sequencing and output format references | Better multi-agent coordination |

## Techniques Applied Per Agent

### 1. Neurologist Agent

**Chain-of-Thought (5-Step Clinical Reasoning Process):**
1. Identify Key Findings - extract significant data points
2. Pattern Recognition - match against neurological syndromes
3. Red Flag Check - explicit urgent finding screening
4. Differential Considerations - primary + 2-3 alternatives
5. Assessment & Recommendations - evidence-based with rationale

**Few-Shot Example:** Complete Parkinson's case assessment demonstrating all 5 steps, structured output format, and confidence scoring.

**Structured Output:** `CLINICAL ASSESSMENT` template with: Key Findings, Clinical Impression, Differential Considerations, Red Flags, Recommended Workup, Clinical Recommendations, Confidence Level.

**Self-Review Checklist:** 6-point verification covering reasoning completeness, red flags, differentials, confidence, evidence basis, and data gaps.

**Reference Tables:** Assessment score interpretation ranges (MMSE, MoCA, Motor Function, EDSS, UPDRS).

---

### 2. Clinical Architect Agent

**Chain-of-Thought (4-Step Data Review Process):**
1. Completeness Check - verify required clinical fields
2. HIPAA Compliance Audit - 18 identifiers, minimum necessary, encryption
3. Clinical Accuracy - score ranges, data types
4. Standards Alignment - ICD-10, LOINC, FHIR

**Few-Shot Example:** Review of a flawed data model showing incorrect MMSE range, missing fields, and HIPAA gaps.

**Structured Output:** `DATA ARCHITECTURE REVIEW` template with: Completeness, HIPAA Compliance, Clinical Accuracy, Standards Alignment, Recommendations, Risk Assessment.

**Self-Review Checklist:** 5-point verification covering HIPAA identifiers, score ranges, condition-specific fields, prioritization, and risk level.

---

### 3. Prognosis Analyst Agent

**Chain-of-Thought (5-Step Analytical Process + Self-Critique):**
1. Data Inventory - list all data points with dates, identify gaps
2. Trend Calculation - rate of change against condition benchmarks
3. Risk Factor Assessment - active risk factors and poor prognostic indicators
4. Trajectory Projection - 3-month and 6-month predictions
5. Self-Critique - evaluate data sufficiency, confounders, extrapolation limits

**Condition-Specific Benchmarks:** Published progression rates for Alzheimer's (MMSE decline), Parkinson's (UPDRS), MS (EDSS), Epilepsy, Migraine, and Stroke recovery.

**Few-Shot Example:** Complete Alzheimer's case with 5 MMSE data points over 24 months, showing benchmark comparison, trajectory projection, and nuanced confidence scoring.

**Structured Output:** `PROGNOSIS ANALYSIS` template with: Data Summary, Trend Analysis, Risk Factors, Trajectory Projection, Key Concerns, Protective Factors, Recommendations, Confidence score (0.0-1.0).

---

### 4. Treatment Advisor Agent

**Chain-of-Thought (5-Step Clinical Decision Process):**
1. Current Regimen Review - doses, durations, therapeutic levels
2. Response Assessment - baseline vs current with classification (Excellent/Good/Partial/Poor/Worsening)
3. Drug Interaction & Safety Screen - interactions, contraindications, overuse
4. Treatment Recommendation - exact medication, dose, frequency, titration, rationale
5. Alternatives & Contingency - Plan B, non-pharmacological, escalation criteria

**Comprehensive Treatment Knowledge Base:** Specific medications, doses, and clinical guidelines for Epilepsy, Parkinson's, Migraine, Alzheimer's, and MS.

**Few-Shot Example:** Complete epilepsy treatment recommendation showing dose optimization before adding second agent, with specific titration schedule and monitoring plan.

**Structured Output:** `TREATMENT RECOMMENDATION` template with: Current Regimen Review, Treatment Response, Drug Interaction Check, Recommendation (with exact doses), Alternative Plan, Non-Pharmacological, Escalation Criteria, Safety Notes.

---

### 5. QA Validator Agent

**Chain-of-Thought (6-Step Validation Process):**
1. Data Completeness - required fields check
2. Range Validation - against reference tables
3. Clinical Logic Check - severity-score alignment, appropriate medications
4. Temporal Consistency - date ordering, plausible timelines
5. Anomaly Detection - sudden changes, contradictions, duplicates
6. Cross-Field Validation - systolic > diastolic, date logic

**Reference Tables:** Complete score ranges for 8 assessments, vital sign plausible ranges, score change thresholds (flags if exceeded between visits).

**Few-Shot Example:** Validation of a record with MMSE=35 (out of range), Donepezil 50mg (overdose), and implausible score improvement, showing CRITICAL/HIGH/MEDIUM severity classification.

**Structured Output:** `VALIDATION REPORT` template with: Overall Status, Checks Performed, Issues Found (with severity counts), numbered issues with recommendations, Data Quality Score (0-100%), Patient Safety Impact.

---

### 6. Report Generator Agent

**Chain-of-Thought (5-Step Report Generation Process):**
1. Gather Inputs - collect findings from all agents
2. Structure Selection - choose appropriate report template
3. Synthesize Findings - integrate multi-agent input into cohesive narrative (not just list)
4. Highlight Critical Items - urgent findings at top, key metric changes, action items
5. Quality Review - PHI check, valid ranges cited, actionable recommendations

**Few-Shot Example:** Complete prognosis report for a Parkinson's patient synthesizing input from all 5 other agents, with executive summary, urgent findings section, assessment data with benchmarks, and specific follow-up plan.

**Structured Output:** Comprehensive report template with: Executive Summary, Urgent Findings, Clinical Overview, Assessment Data, Trend Analysis, Treatment Status, Recommendations, Follow-Up Plan, Validation Status.

**Writing Guidelines:** Specific rules against vague language ("consider monitoring" -> specify what, how often, why).

---

### 7. Backend Developer Agent

**Chain-of-Thought (5-Step Development Process):**
1. Requirements Analysis - data models, validation rules, HIPAA, performance
2. Data Model Design - audit fields, indexes, soft-delete
3. Implementation - async/await, repository pattern, DI, type hints
4. Error Handling - custom exceptions, global handlers, correlation IDs
5. Security Review - SQL injection, PHI logging, input validation, CORS

**Few-Shot Example:** Complete FastAPI endpoint for patient creation with validation, duplicate check, audit logging, and proper error handling.

**Structured Output:** API design standards table, response patterns, endpoint inventory.

**Security Rules:** Explicit prohibitions against SQL injection, PHI plaintext logging, stack trace exposure, and hard deletes.

---

## Orchestrator Task Prompts

### Before
```
Perform a comprehensive prognosis analysis for this patient:
...
Each specialist should contribute:
1. Neurologist: Review case
2. Prognosis Analyst: Analyze trends
...
Collaborate to provide a comprehensive assessment.
```

### After
```
## Multi-Agent Prognosis Analysis Request
...
### Instructions for Each Specialist
1. **Neurologist** (FIRST): Perform your 5-step clinical reasoning process...
   Use your CLINICAL ASSESSMENT format.
2. **Prognosis Analyst** (SECOND): Using the Neurologist's findings...
   Use your PROGNOSIS ANALYSIS format with confidence score.
3. **Treatment Advisor** (THIRD): Follow your clinical decision process...
   Use your TREATMENT RECOMMENDATION format.
4. **QA Validator** (FOURTH): Use your VALIDATION REPORT format...
5. **Report Generator** (FIFTH): Synthesize ALL findings...

### Collaboration Rules
- Build on previous agents' findings
- If you disagree, state your reasoning
- Flag data gaps
- Say TERMINATE when complete
```

**Key improvements:**
- Explicit agent ordering with numbered sequence
- References to each agent's specific response format
- Collaboration rules (build on, don't repeat)
- Explicit TERMINATE instruction for clean conversation ending
- Markdown formatting for better LLM parsing

---

## Prompt Engineering Principles Applied

### 1. Chain-of-Thought (CoT)
Every agent has a numbered step-by-step reasoning process they must follow. This forces systematic analysis rather than jumping to conclusions, which is critical in clinical settings.

### 2. Few-Shot Learning
Each agent includes a complete input -> output example demonstrating the expected format, level of detail, and reasoning quality. This anchors the LLM's output.

### 3. Structured Output Formatting
Every agent has a named template (e.g., `CLINICAL ASSESSMENT`, `PROGNOSIS ANALYSIS`) with explicit fields. This makes outputs consistent and parseable.

### 4. Self-Critique / Self-Review
Agents have verification checklists to run before submitting responses. The Prognosis Analyst has an explicit "Self-Critique" step to check for extrapolation beyond data.

### 5. Confidence Calibration
All clinical agents must state confidence levels (High/Moderate/Low or 0.0-1.0) with justification. This prevents overconfident assertions from limited data.

### 6. Reference Grounding
Agents include reference tables (score ranges, benchmarks, dosage ranges) directly in their prompts so the LLM has ground truth to validate against rather than relying on training data alone.

### 7. Behavioral Guardrails
Each agent has a "Critical Rules" section with explicit prohibitions and safety boundaries, reducing the risk of harmful outputs.

### 8. Role Depth
Instead of "You are a neurologist", agents are given specific expertise depth ("20+ years", "senior specialist") and concrete knowledge domains, improving role adherence.

### 9. Multi-Agent Coordination
Orchestrator prompts explicitly sequence agents, reference their output formats, and establish collaboration rules to prevent redundant analysis.

---

## Metrics for Evaluation

To assess the impact of prompt uplifting, compare before/after on:

| Metric | How to Measure |
|--------|---------------|
| Output consistency | Do repeated runs produce same structure? |
| Clinical accuracy | Are score ranges and dosages correct? |
| Reasoning depth | Does the agent show its reasoning steps? |
| Confidence calibration | Are confidence levels appropriate for data quality? |
| Safety coverage | Are red flags and contraindications caught? |
| Agent coordination | Do later agents build on earlier findings? |
| Actionability | Are recommendations specific enough to act on? |
