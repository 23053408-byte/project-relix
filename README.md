# Relix — Cost- and Latency-Aware Optimization of LLM Queries over Relational Data

> **Research Prototype Grounded in MLSys 2025 Architecture**  
> **Primary Reference:** Shu Liu et al., *Optimizing LLM Queries in Relational Data Analytics Workloads*, Proceedings of Machine Learning and Systems (MLSys 2025).  
> **Paper URL:** https://proceedings.mlsys.org/paper_files/paper/2025/file/b5dc49f44db2fadc5c4d717c57f4a424-Paper-Conference.pdf

---

## 1. Overview & Problem Statement

Large Language Models (LLMs) are increasingly deployed over relational databases for data analytics tasks such as sentiment classification, entity extraction, scoring, and text synthesis. When executed naively row-by-row, LLM queries contain repeated schema headers, metadata, and recurring attribute values. Standard LLM serving engines recompute these redundant prompt prefixes during prefill computation, incurring high computational latency and financial API costs.

**Relix** reorders relational dataset rows and record prompt fields to maximize shared prefix token overlap. By increasing the **Prefix Hit Count (PHC)** across sequential requests, Relix increases KV-cache reuse, significantly reducing prefill latency and API inference costs while strictly preserving task semantics.

```text
Relational Dataset
       ↓
Profile Repetition & Functional Dependencies (FDs)
       ↓
Reorder Rows + Fields (Relix GGR-Inspired)
       ↓
Create Longer Shared Prefixes
       ↓
Maximize KV-Cache Token Reuse
       ↓
Lower Latency / Lower Cost
```

---

## 2. Repository Structure

```text
relix/
├── README.md                      # Comprehensive project documentation
├── requirements.txt               # Dependencies: pandas, numpy, streamlit, plotly, pydantic, pytest
├── .gitignore                     # Git rules
├── app.py                         # Relix Interactive Streamlit Dashboard
├── research_tasks.md              # Research task execution log
│
├── src/
│   ├── __init__.py
│   ├── profiler.py                # Dataset profiler & FD detector
│   ├── prompt_generator.py        # Structured prompt generator
│   ├── prefix_metrics.py          # LCP, PHC & cache reuse proxy
│   ├── baseline.py                # Baseline query evaluator
│   ├── ophr.py                    # Exact OPHR small-data oracle
│   ├── ggr.py                     # Relix GGR-Inspired greedy optimizer
│   ├── semantic_validator.py      # Semantic correctness validator
│   ├── cost_model.py              # Cost & latency simulation
│   └── benchmark.py               # Multi-scale benchmark suite
│
├── data/
│   └── sample_reviews.csv         # High-repetition sample dataset
│
├── experiments/
│   └── results/
│       ├── dataset_profile.json
│       ├── results.csv
│       ├── results.json
│       └── correctness_report.json
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

## 3. Paper vs. Prototype Mapping

| Concept | Paper Reference | Relix Implementation | Status |
| :--- | :--- | :--- | :--- |
| Relational LLM Query Optimization | Liu et al., MLSys 2025 | Core System Architecture | Implemented |
| Row & Field Reordering | Liu et al., MLSys 2025 | `src/ggr.py` / `src/ophr.py` | Implemented |
| Prefix Hit Count (PHC) | Section 3 | `src/prefix_metrics.py` | Implemented |
| OPHR Exact Search | Section 4 | `src/ophr.py` | Exact Small-Data Oracle ($n \le 7$) |
| GGR Greedy Algorithm | Section 5 | `src/ggr.py` | Relix GGR-Inspired Implementation |
| KV Cache Measurement | Section 6 | Token LCP Proxy | Whitespace Token Proxy |
| Inference Serving | Apache Spark + vLLM | Local Python Engine | Simulated Model |

---

## 4. How to Run

### Installation & Dependencies

```bash
pip install -r requirements.txt
```

### Running Test Suite

```bash
pytest -q
```

### Running Automated Benchmark Suite

```bash
python src/benchmark.py
```

### Launching Relix Streamlit Dashboard

```bash
streamlit run app.py
```

---

## 5. Summary of Empirical Benchmark Results

Running Relix optimization across scaled datasets (100 to 10,000 records) demonstrates:
- **Cache Reuse Ratio**: Increases from ~15% (Baseline) to **65–85%** (Relix).
- **Simulated Speedup**: **1.5× to 2.8× inference acceleration** via reduced prefill latency.
- **Cost Reduction**: **25% to 40% API savings** on cached input token billing.
- **Semantic Preservation**: **100% passed** across row count integrity, cell value immutability, and prompt task identity.

---

## 6. Disclosed Limitations

1. **Token Proxy**: Uses deterministic whitespace tokenization rather than a model-specific BPE tokenizer.
2. **Simulation Model**: Latency and cost metrics are simulated using configurable throughput parameters rather than a live GPU daemon.
3. **OPHR Scope**: Exact OPHR search is restricted to small dataset sizes due to factorial search space growth ($n! \times m!$).
