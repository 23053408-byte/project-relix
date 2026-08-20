# Research Tasks & Workflow Execution Log

> **Project:** LLM-Opt (Relational LLM Query Optimization)  
> **Based on Paper:** Shu Liu et al., *Optimizing LLM Queries in Relational Data Analytics Workloads*, MLSys 2025.

---

## Tasks Status

- [x] **Task A: Paper Extraction** — Extracted problem statement, objectives, PHC, OPHR, GGR, metrics, and limitations into `docs/paper_notes.md`.
- [x] **Task B: Algorithm Mapping** — Mapped paper concepts to prototype components in `docs/algorithm_mapping.md`.
- [x] **Task C: Dataset Analysis** — Implemented automated profiler in `src/profiler.py` and exported `experiments/results/dataset_profile.json`.
- [x] **Task D: Baseline Analysis** — Implemented baseline evaluator in `src/baseline.py`.
- [x] **Task E: Optimizer Analysis** — Implemented OPHR (`src/ophr.py`) and GGR-Inspired (`src/ggr.py`).
- [x] **Task F: Correctness Analysis** — Built semantic validator in `src/semantic_validator.py` and exported `experiments/results/correctness_report.json`.
- [x] **Task G: Comparative Analysis** — Calculated Speedup, Cost Reduction %, and Cache Reuse Improvement in `src/benchmark.py`.
- [x] **Task H: Scaling Analysis** — Benchmark suite runs across 100, 1,000, and 10,000 rows.
- [x] **Task I: Repetition Sensitivity** — Analyzed performance impact across low, medium, and high value repetition datasets.
- [x] **Task J: Research Conclusion** — Compiled empirical findings into `docs/experimental_summary.md`.
