# LLM-Opt — Rapid Full-Stack Project Blueprint

> **Deadline mode:** This blueprint is optimized for a build window of only a couple of hours.
>
> **Primary paper:** Shu Liu et al., *Optimizing LLM Queries in Relational Data Analytics Workloads*, MLSys 2025.
>
> **Goal:** Build a working, research-grounded prototype—not an unfinished production system.

---

## 1. Project Title

**LLM-Opt: Cost- and Latency-Aware Optimization of LLM Queries over Relational Data**

### One-line problem statement

Large-scale LLM analytics over relational data can be expensive and slow because many generated requests contain repeated prefixes. LLM-Opt reorders rows and fields to increase shared-prefix reuse, reducing estimated/actual inference work while preserving the analytical task.

### Real-world problem

A company may want an LLM to classify, extract, summarize, or analyze thousands/millions of database records. Sending each request independently causes repeated processing of common prompt/context tokens.

```text
Relational data
      ↓
Generate many LLM requests
      ↓
Repeated prefixes
      ↓
Repeated prefill computation
      ↓
High latency + high cost
```

LLM-Opt:

```text
Relational data
      ↓
Profile repetition/dependencies
      ↓
Reorder rows + fields
      ↓
Create longer shared prefixes
      ↓
Increase KV-cache reuse
      ↓
Lower latency / cost
```

---

# 2. PRIMARY PAPER REFERENCES

Use these as the methodological foundation:

1. Liu, S. et al. (2025). *Optimizing LLM Queries in Relational Data Analytics Workloads*. Proceedings of Machine Learning and Systems (MLSys 2025).
   - https://proceedings.mlsys.org/paper_files/paper/2025/file/b5dc49f44db2fadc5c4d717c57f4a424-Paper-Conference.pdf

2. MLSys paper page:
   - https://proceedings.mlsys.org/paper_files/paper/2025/hash/b5dc49f44db2fadc5c4d717c57f4a424-Abstract-Conference.html

3. OpenReview:
   - https://openreview.net/forum?id=R7bK9yycHp

4. Papers With Code:
   - https://paperswithcode.com/paper/optimizing-llm-queries-in-relational

### Paper concepts to implement/reference

- Row and field reordering for shared-prefix reuse.
- Prefix Hit Count (PHC).
- OPHR — Optimal Prefix Hit Recursion.
- GGR — Greedy Group Recursion.
- Functional dependencies and table statistics.
- Apache Spark + vLLM architecture from the paper.
- Batch LLM analytics workloads.

The paper evaluates 16 LLM queries across 7 real-world datasets and reports 1.5–3.4× end-to-end speedups and up to 32% cost reduction in its evaluated setup. **Do not claim those numbers for this project unless experiments actually produce them.**

---

# 3. TWO-HOUR BUILD PRIORITY

## Mandatory MVP

- [ ] CSV dataset loading
- [ ] Dataset profiling
- [ ] Prompt generation
- [ ] Baseline ordering
- [ ] Prefix-hit calculation
- [ ] Small-data exact/brute-force OPHR validator
- [ ] GGR-inspired greedy optimizer
- [ ] Semantic-equivalence validation
- [ ] Cost model
- [ ] Latency simulation
- [ ] Benchmark runner
- [ ] Results CSV/JSON
- [ ] Streamlit dashboard
- [ ] Required charts
- [ ] README
- [ ] Tests

## Optional only after MVP

- [ ] Real vLLM
- [ ] Apache Spark
- [ ] Llama 3 8B local inference
- [ ] GPU measurements
- [ ] Real API billing
- [ ] CAR correlation-aware extension
- [ ] Docker
- [ ] PostgreSQL
- [ ] MLflow

**Do not let optional work block the MVP.**

---

# 4. IMPORTANT: ANALYSIS/RESEARCH WORK MUST ALSO BE EXECUTABLE BY THE IDE

Because the project must be built quickly, the IDE agent must not treat analysis as something to be done manually later.

Create a `research_tasks.md` file and execute these tasks automatically where possible.

## Analysis Task A — Paper extraction

Read the primary paper and extract into `docs/paper_notes.md`:

- problem definition
- assumptions
- objective function
- PHC definition
- OPHR procedure
- GGR procedure
- complexity discussion
- datasets
- workloads
- model/backend
- metrics
- reported results
- limitations

Do not invent missing details.

## Analysis Task B — Algorithm mapping

Create `docs/algorithm_mapping.md` with:

| Paper concept | Project implementation | Exact / simplified / extension |
|---|---|---|
| Baseline | Original row/field order | baseline |
| OPHR | Small-data exact search | simplified validation |
| GGR | Greedy grouping/reordering | inspired implementation |
| PHC | Prefix metric | implementation |
| KV reuse | Prefix reuse proxy | simulation unless vLLM is active |
| CAR | Correlation-aware ordering | original extension, optional |

## Analysis Task C — Dataset analysis

For every loaded dataset calculate:

- rows
- columns
- data types
- missing values
- duplicate rows
- unique counts
- cardinality ratios
- repeated-value frequency
- candidate functional dependencies
- candidate high-prefix columns

Save to `experiments/results/dataset_profile.json`.

## Analysis Task D — Baseline analysis

Run the original ordering and record:

- number of prompts
- estimated token count
- total reused prefix tokens
- PHC
- cache-reuse ratio
- estimated latency
- estimated cost

## Analysis Task E — Optimizer analysis

Run OPHR on tiny datasets and GGR-Inspired on all feasible datasets.

Record the same metrics.

## Analysis Task F — Correctness analysis

Verify:

1. Every input row appears exactly once after optimization.
2. No cell values change.
3. The task template is unchanged.
4. Deterministic labels remain identical.
5. Extraction outputs remain equivalent after normalization.

Save to `experiments/results/correctness_report.json`.

## Analysis Task G — Comparative analysis

Automatically calculate:

```text
speedup = baseline_latency / optimized_latency

cost_reduction_percent =
    (baseline_cost - optimized_cost) / baseline_cost * 100

cache_reuse_improvement =
    optimized_reuse_ratio - baseline_reuse_ratio
```

## Analysis Task H — Scaling analysis

Run at:

- 100 rows
- 1,000 rows
- 10,000 rows

If hardware/time allows:

- 50,000 rows
- 100,000 rows

## Analysis Task I — Repetition sensitivity

Generate or test:

- low repetition
- medium repetition
- high repetition

Determine whether optimization benefit increases with repeated/shared values.

## Analysis Task J — Research conclusion

Automatically generate a short `docs/experimental_summary.md` containing only actual measured results.

Never fabricate results.

---

# 5. RAPID ARCHITECTURE

```text
                    ┌────────────────────┐
                    │      Dataset       │
                    │ CSV / Parquet      │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │  Dataset Profiler  │
                    └─────────┬──────────┘
                              │
             ┌────────────────┴────────────────┐
             │                                 │
             ▼                                 ▼
    ┌─────────────────┐               ┌─────────────────┐
    │    BASELINE     │               │    OPTIMIZER    │
    │ original order  │               │ OPHR / GGR      │
    └────────┬────────┘               └────────┬────────┘
             │                                 │
             └────────────────┬────────────────┘
                              ▼
                    ┌────────────────────┐
                    │ Prompt Generator   │
                    └─────────┬──────────┘
                              ▼
                    ┌────────────────────┐
                    │ Prefix Analyzer    │
                    │ PHC / reuse ratio  │
                    └─────────┬──────────┘
                              ▼
                    ┌────────────────────┐
                    │ Benchmark Engine   │
                    └─────────┬──────────┘
                              ▼
                    ┌────────────────────┐
                    │ Streamlit Dashboard│
                    └────────────────────┘
```

---

# 6. RAPID TECHNOLOGY STACK

Use:

- Python 3.11+
- Pandas
- NumPy
- FastAPI only if an API is actually needed
- Streamlit
- Plotly
- Pydantic
- pytest

Optional later:

- Apache Spark
- vLLM
- Llama 3 8B
- Docker
- PostgreSQL
- MLflow

**Do not build React during the first two hours.** Streamlit is sufficient for the demonstration.

---

# 7. REPOSITORY STRUCTURE

```text
llm-opt/
├── README.md
├── requirements.txt
├── .gitignore
├── app.py
├── research_tasks.md
│
├── src/
│   ├── profiler.py
│   ├── prompt_generator.py
│   ├── prefix_metrics.py
│   ├── baseline.py
│   ├── ophr.py
│   ├── ggr.py
│   ├── semantic_validator.py
│   ├── cost_model.py
│   └── benchmark.py
│
├── data/
│   └── sample_reviews.csv
│
├── experiments/
│   └── results/
│
├── tests/
│   ├── test_prefix.py
│   ├── test_optimizer.py
│   ├── test_profiler.py
│   └── test_semantics.py
│
└── docs/
    ├── paper_notes.md
    ├── algorithm_mapping.md
    ├── architecture.md
    ├── methodology.md
    └── experimental_summary.md
```

---

# 8. DATASET

For the fast demonstration use a review dataset with repeated values.

Required fields:

```text
review_id
product_id
category
brand
rating
review_text
```

Example:

```csv
review_id,product_id,category,brand,rating,review_text
1,P100,Phone,Apple,5,"Excellent battery life"
2,P101,Phone,Apple,4,"Good camera"
3,P102,Phone,Samsung,5,"Excellent display"
4,P103,Laptop,Apple,5,"Very fast"
5,P104,Phone,Apple,3,"Battery is average"
```

The project must also accept arbitrary CSV files.

---

# 9. DATASET PROFILER

Implement:

```python
profile_dataset(df)
```

Return:

```json
{
  "rows": 1000,
  "columns": 6,
  "column_types": {},
  "unique_counts": {},
  "cardinality_ratio": {},
  "missing_values": {},
  "duplicate_rows": 0,
  "repeated_value_columns": [],
  "candidate_dependencies": []
}
```

For candidate functional dependencies, use a practical heuristic. Example:

```text
product_id → brand
```

if each product ID maps consistently to one brand.

Label these as **candidate** dependencies, not formally proven dependencies, unless a formal test is implemented.

---

# 10. PROMPT GENERATOR

Use deterministic prompts.

Example:

```text
You are a sentiment classifier.

Product: P100
Category: Phone
Brand: Apple
Rating: 5
Review: Excellent battery life

Classify the review as positive, neutral, or negative.
```

Field order must be configurable because field ordering is part of the optimization experiment.

The semantic task itself must remain unchanged.

---

# 11. BASELINE

Baseline means:

```text
Original row order
+
Fixed field order
```

Measure:

- prompt count
- input token estimate
- output token estimate
- prefix hit count
- reused tokens
- reuse ratio
- estimated latency
- estimated cost

---

# 12. PREFIX METRICS

Implement:

```python
longest_common_prefix(tokens_a, tokens_b)
prefix_hit_count(requests)
total_reused_prefix_tokens(requests)
cache_reuse_ratio(requests)
average_prefix_length(requests)
```

If a real tokenizer is unavailable, use a deterministic whitespace-token approximation.

Label it explicitly:

> **Token approximation / cache-reuse proxy**

Do not claim it is an actual vLLM KV-cache measurement.

---

# 13. OPHR

Implement exact search only for tiny datasets.

For example:

```text
n <= 7 rows
m <= 4 fields
```

Generate candidate permutations and select the ordering maximizing the prefix-sharing objective.

Use this as the correctness oracle.

Never run brute-force OPHR on large datasets.

The paper's search space grows as:

```text
n! × (m!)^n
```

so scalability is intentionally demonstrated as a limitation of exact optimization.

---

# 14. GGR-INSPIRED

Implement a practical greedy optimizer inspired by the paper's GGR methodology.

Use:

- value frequency
- cardinality
- candidate functional dependencies
- grouping
- expected prefix gain

Suggested process:

1. Identify high-frequency values.
2. Identify columns with useful repeated values.
3. Identify candidate dependencies.
4. Group rows by high-sharing fields.
5. Sort groups by estimated prefix benefit.
6. Order fields using repetition/dependency scores.
7. Generate optimized prompts.
8. Measure PHC and reuse ratio.

Call it **GGR-Inspired**, not an exact reproduction.

---

# 15. OPTIONAL CAR EXTENSION

Only implement after MVP completion.

Name:

**CAR — Correlation-Aware Reordering**

Possible score:

```text
field_score =
    α × repetition_score
    + β × dependency_score
    + γ × prefix_gain
```

Use correlation/dependency information to choose field ordering.

This is an **original project extension**, not a method from the primary paper.

If time is insufficient, omit it.

---

# 16. COST MODEL

Implement configurable pricing:

```text
input_cost =
    input_tokens / 1,000,000 × input_price_per_million

output_cost =
    output_tokens / 1,000,000 × output_price_per_million

total_cost = input_cost + output_cost
```

Support cached/uncached input tokens where applicable.

Do not hard-code current provider prices into research conclusions.

For local inference, use:

- GPU time
- token throughput
- total tokens

if those are actually measured.

---

# 17. LATENCY MODEL

If no real LLM server is available, use a documented simulation:

```text
latency =
    fixed_overhead
    + uncached_tokens / prefill_throughput
    + output_tokens / decode_throughput
```

All parameters must be configurable.

Charts must say:

> **Estimated / simulated latency**

unless actual inference is used.

---

# 18. SEMANTIC CORRECTNESS

Mandatory checks:

1. Same number of rows.
2. Same row values.
3. Same task prompt.
4. Only ordering/formatting changes.
5. Deterministic outputs remain identical.
6. Extraction outputs match after normalization.

Create:

```text
experiments/results/correctness_report.json
```

---

# 19. BENCHMARK

Run at minimum:

```text
100 rows
1,000 rows
10,000 rows
```

If time allows:

```text
50,000 rows
100,000 rows
```

Workloads:

1. Sentiment classification.
2. Entity extraction.
3. Attribute extraction.

Methods:

- Baseline
- OPHR on tiny data only
- GGR-Inspired
- CAR if implemented

---

# 20. REQUIRED RESULT TABLE

Generate:

| Method | Rows | Query | Prefix Hits | Reused Tokens | Total Tokens | Estimated Latency | Estimated Cost | Speedup |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| Baseline | | | | | | | | 1.00× |
| OPHR | | | | | | | | |
| GGR-Inspired | | | | | | | | |
| CAR | | | | | | | | |

Remove CAR if it is not implemented.

---

# 21. REQUIRED CHARTS

Create with Plotly:

1. Prefix Hit Count by method.
2. Cache Reuse Ratio by method.
3. Estimated Latency by method.
4. Estimated Cost by method.
5. Speedup vs baseline.
6. Scaling with number of rows.

Do not invent values.

---

# 22. STREAMLIT DASHBOARD

Sections:

## Dataset

- Upload CSV.
- Preview.
- Show profile.

## Query

- Select workload.
- Show generated prompt.

## Optimization

Show:

```text
Baseline
OPHR
GGR-Inspired
CAR (optional)
```

## Metrics

Show:

- Prefix Hit Count
- Reuse Ratio
- Reused Tokens
- Estimated Latency
- Estimated Cost
- Speedup

## Charts

Show the six required charts.

Keep UI simple. Do not spend time on visual polish.

---

# 23. TESTS

Write tests for:

- longest common prefix
- prefix hit count
- profiler
- OPHR correctness
- optimizer permutation validity
- no duplicate/missing rows
- semantic preservation
- cost calculation
- benchmark output

Run:

```bash
pytest -q
```

Fix failures before declaring the project complete.

---

# 24. FAST EXECUTION PLAN

## 0–15 minutes

Create:

- repository
- dependencies
- folders
- sample dataset
- research_tasks.md

## 15–40 minutes

Implement:

- profiler
- prompt generator
- prefix metrics
- baseline

## 40–70 minutes

Implement:

- OPHR
- GGR-Inspired
- semantic validation

## 70–95 minutes

Implement:

- benchmark
- cost model
- latency model
- result export

## 95–120 minutes

Implement:

- Streamlit dashboard
- charts
- README
- tests
- actual benchmark run

## After 120 minutes

Only if everything works:

- CAR
- vLLM
- Spark
- Docker

---

# 25. DO NOT BUILD FIRST

Do not start with:

- authentication
- accounts
- React frontend
- microservices
- Kubernetes
- cloud deployment
- complex RAG
- 70B model
- distributed Spark cluster
- real-time monitoring
- advanced prompt engineering

A working measured optimizer is the priority.

---

# 26. REQUIRED ANALYSIS OUTPUTS

The IDE must produce these files automatically:

```text
docs/paper_notes.md
docs/algorithm_mapping.md
docs/experimental_summary.md
experiments/results/dataset_profile.json
experiments/results/results.csv
experiments/results/results.json
experiments/results/correctness_report.json
```

### `paper_notes.md`

Record only facts verified from the primary paper.

### `algorithm_mapping.md`

Clearly distinguish exact concepts, simplified implementations, and original extensions.

### `experimental_summary.md`

Use only actual measurements from the current run.

---

# 27. MASTER IDE PROMPT

Paste this into Cursor/Windsurf/Claude Code/etc.:

```text
You are a senior Python engineer, data-systems researcher, ML engineer, and research-project mentor.

Build a working rapid prototype called:

LLM-Opt — Cost- and Latency-Aware Optimization of LLM Queries over Relational Data

PRIMARY PAPER:
Shu Liu et al., "Optimizing LLM Queries in Relational Data Analytics Workloads", MLSys 2025.

Primary reference:
https://proceedings.mlsys.org/paper_files/paper/2025/file/b5dc49f44db2fadc5c4d717c57f4a424-Paper-Conference.pdf

Papers With Code:
https://paperswithcode.com/paper/optimizing-llm-queries-in-relational

TIME CONSTRAINT:
I have only a couple of hours. Build the smallest complete, working research prototype first.

Do not build unnecessary production infrastructure.
Do not require a GPU for the MVP.
Do not require vLLM for the MVP.
Do not require Spark for the MVP.
Do not fabricate experimental results.
Do not claim simulated cache reuse is actual KV-cache measurement.
Do not claim the simplified GGR implementation is an exact reproduction.
Do not claim the paper's reported speedups are our results.

FIRST, create and execute a research-analysis workflow.

==================================================
RESEARCH ANALYSIS WORKFLOW
==================================================

Create research_tasks.md and execute the following tasks.

TASK A — PAPER EXTRACTION
Read the primary paper and extract into docs/paper_notes.md:
- problem definition
- assumptions
- PHC objective
- OPHR
- GGR
- complexity
- functional dependencies
- datasets
- workloads
- models/backend
- metrics
- reported results
- limitations

Never invent missing details.

TASK B — ALGORITHM MAPPING
Create docs/algorithm_mapping.md with:
- paper concept
- project implementation
- exact/simplified/extension label

TASK C — DATASET ANALYSIS
For every dataset calculate:
- rows
- columns
- dtypes
- missing values
- duplicates
- unique counts
- cardinality ratio
- repeated values
- candidate functional dependencies

Save experiments/results/dataset_profile.json.

TASK D — BASELINE ANALYSIS
Calculate:
- prompt count
- token estimate
- PHC
- reused prefix tokens
- reuse ratio
- estimated latency
- estimated cost

TASK E — OPTIMIZER ANALYSIS
Run OPHR on tiny datasets and GGR-Inspired on feasible datasets.
Record identical metrics.

TASK F — CORRECTNESS ANALYSIS
Verify:
1. Every row appears exactly once.
2. No cell values change.
3. Task semantics remain unchanged.
4. Deterministic outputs remain equivalent.

Save experiments/results/correctness_report.json.

TASK G — COMPARATIVE ANALYSIS
Calculate:
- speedup = baseline_latency / optimized_latency
- cost reduction percentage
- cache reuse improvement

TASK H — SCALING ANALYSIS
Run 100, 1000, and 10000 rows.
Use larger sizes only if time permits.

TASK I — REPETITION ANALYSIS
Test low, medium, and high repetition.

TASK J — RESEARCH SUMMARY
Create docs/experimental_summary.md containing only actual results.

==================================================
IMPLEMENTATION
==================================================

Create:

src/profiler.py
src/prompt_generator.py
src/prefix_metrics.py
src/baseline.py
src/ophr.py
src/ggr.py
src/semantic_validator.py
src/cost_model.py
src/benchmark.py
app.py

Create tests and sample data.

DATASET:
Create a review dataset with repeated product_id, category, and brand values and varied ratings/review text. Also support arbitrary CSV upload.

PROMPT:
Use a deterministic sentiment/classification prompt with configurable field order.

BASELINE:
Original row order + fixed field order.

PREFIX METRICS:
Implement longest_common_prefix, prefix_hit_count, reused tokens, reuse ratio, average prefix length.
If no real tokenizer is available, use deterministic whitespace tokenization and clearly label it a proxy.

OPHR:
Implement exact/brute-force search only for tiny datasets. Use it as a correctness oracle. Never run it on large datasets.

GGR-INSPIRED:
Implement a practical greedy optimizer inspired by the paper using repetition, cardinality, candidate functional dependencies, grouping, and prefix gain. Clearly label it GGR-Inspired.

OPTIONAL CAR:
Only after all mandatory features work. CAR is an original extension, not part of the paper.

COST:
Make token pricing configurable.

LATENCY:
If real inference is unavailable, simulate latency using configurable fixed overhead, prefill throughput, and decode throughput. Label it simulated/estimated.

SEMANTICS:
Verify optimization changes ordering only and does not alter values or task semantics.

BENCHMARK:
Run Baseline, OPHR on tiny data, and GGR-Inspired on 100/1000/10000 rows. Include sentiment, entity extraction, and attribute extraction workloads.

OUTPUT:
experiments/results/results.csv
experiments/results/results.json

DASHBOARD:
Use Streamlit. Include CSV upload, dataset profile, workload selection, benchmark execution, metrics, and Plotly charts.

CHARTS:
- prefix hits
- reuse ratio
- estimated latency
- estimated cost
- speedup
- scaling

TESTS:
Run pytest -q and fix all failures.

README:
Explain:
- problem
- paper
- methodology
- architecture
- exact vs simplified implementation
- experiments
- limitations
- future work
- how to run

IMPORTANT:
Do not stop after creating files. Actually execute the application/tests/benchmark and fix errors.
Do not fabricate results.
At the end, print:
1. files created
2. tests passed/failed
3. benchmark results
4. how to launch the dashboard
5. limitations
6. optional next steps
```

---

# 28. FINAL DEMONSTRATION

The demo should follow this sequence:

```text
Upload dataset
      ↓
Dataset profile
      ↓
Select workload
      ↓
Generate baseline prompts
      ↓
Calculate prefix reuse
      ↓
Run GGR-Inspired optimizer
      ↓
Calculate optimized prefix reuse
      ↓
Compare latency/cost proxy
      ↓
Verify semantic equivalence
      ↓
Show charts
```

Example result format:

```text
                     BASELINE       GGR
Prefix Hits             X             Y
Reuse Ratio             X%            Y%
Input Tokens            X             Y
Estimated Latency       X             Y
Estimated Cost          X             Y
Speedup                 1.00×         Z×
```

Use only actual values produced by the benchmark.

---

# 29. RESEARCH QUESTIONS

Use these in the report:

### RQ1
How much can relational-data reordering reduce LLM analytics latency?

### RQ2
How does increased shared-prefix length affect estimated KV-cache reuse?

### RQ3
How does a greedy strategy compare with exact ordering on small datasets?

### RQ4
How does optimization effectiveness change with dataset size and repetition?

### RQ5
Can optimized ordering preserve analytical semantics?

### RQ6 — optional
Can correlation/dependency-aware ordering improve upon the simplified greedy strategy?

---

# 30. PAPER VS PROJECT: HONEST CLAIMS

Use this distinction throughout the documentation.

| Item | Status |
|---|---|
| Relational LLM query optimization | Based on paper |
| Row/field reordering | Based on paper |
| PHC/prefix reuse concept | Based on paper |
| OPHR | Implemented as small-data exact validator |
| GGR | Simplified/inspired implementation |
| Spark | Optional future integration |
| vLLM | Optional future integration |
| Real KV-cache metrics | Only if vLLM is actually measured |
| CAR | Original optional extension |
| Dashboard | Project implementation |
| Benchmark | Project-specific reduced benchmark |

Never present the reduced benchmark as a full reproduction of the paper.

---

# 31. RESEARCH PAPER STRUCTURE

If turning this into a paper/report:

## Abstract
Problem → approach → experiments → measured result.

## 1. Introduction
LLM analytics, cost/latency, KV reuse, relational ordering.

## 2. Related Work
LLM inference, KV caching, relational optimization, RAG, vLLM.

## 3. Background
Prefill, KV cache, shared prefixes, relational data, dependencies.

## 4. Methodology
Baseline, OPHR, GGR-Inspired, optional CAR.

## 5. System Architecture
Profiler, prompt generator, optimizer, prefix analyzer, benchmark, dashboard.

## 6. Experimental Setup
Datasets, workloads, hardware, token model, metrics.

## 7. Results
Prefix reuse, latency, cost, scalability, correctness.

## 8. Discussion
Where optimization helps, overhead, limitations.

## 9. Conclusion
Main findings and future work.

---

# 32. LIMITATIONS TO DISCLOSE

The rapid version may:

- use a token approximation;
- simulate cache reuse;
- simulate latency;
- use smaller datasets;
- use fewer workloads;
- simplify GGR;
- run OPHR only on small datasets;
- omit Spark/vLLM.

These are acceptable if explicitly disclosed.

---

# 33. FUTURE WORK

1. Real vLLM integration.
2. Real KV-cache measurements.
3. Apache Spark integration.
4. Full paper benchmark reproduction.
5. Larger Llama models.
6. Real provider prefix-cache pricing.
7. Formal functional-dependency detection.
8. CAR extension.
9. Adaptive optimizer selection.
10. Distributed benchmarking.
11. GPU utilization/energy measurements.
12. MLflow experiment tracking.

---

# 34. DEFINITION OF DONE

The rapid prototype is complete when:

- [ ] `streamlit run app.py` works.
- [ ] CSV loads.
- [ ] Dataset profile works.
- [ ] Prompts are generated.
- [ ] Baseline metrics work.
- [ ] OPHR works on tiny data.
- [ ] GGR-Inspired works on larger data.
- [ ] Semantic validation works.
- [ ] Benchmark runs.
- [ ] Results are saved.
- [ ] Charts display.
- [ ] README explains the methodology.
- [ ] Analysis outputs exist.
- [ ] Tests pass.
- [ ] No fabricated results are present.

---

# 35. FINAL PROJECT STATEMENT

> **LLM-Opt is a data-systems research prototype that optimizes batch LLM analytics over relational data by reordering rows and fields to increase shared prompt-prefix reuse. Inspired by OPHR and GGR from Liu et al., the system profiles relational data, constructs LLM requests, compares baseline and optimized orderings, estimates cache reuse and inference cost, and validates semantic equivalence.**

---

# 36. MOST IMPORTANT DEADLINE RULE

**Build the research loop first:**

```text
Paper
  ↓
Core concept
  ↓
Working optimizer
  ↓
Prefix metric
  ↓
Baseline comparison
  ↓
Actual benchmark
  ↓
Charts
  ↓
Research explanation
```

A smaller working experiment with honest measurements is much stronger than an unfinished Spark + vLLM + React system.
