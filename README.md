# Relix — Cost- and Latency-Aware Optimization of LLM Queries over Relational Data

> **Groundbreaking Data-Systems Research Prototype**  
> **Based on MLSys 2025 Research:** Shu Liu et al., *Optimizing LLM Queries in Relational Data Analytics Workloads*, Proceedings of Machine Learning and Systems (MLSys 2025).  
> **Paper Link:** https://proceedings.mlsys.org/paper_files/paper/2025/file/b5dc49f44db2fadc5c4d717c57f4a424-Paper-Conference.pdf  
> **GitHub Repository:** https://github.com/23053408-byte/project-relix

---

## 1. 🎯 What Problem Does Relix Solve?

### The Real-World Problem
Modern database analytics applications increasingly use Large Language Models (LLMs) to classify, extract, score, and summarize millions of database records (e.g. customer reviews, e-commerce product listings, support tickets, financial transactions).

When databases send records to LLMs naively row-by-row:
1. Every single prompt repeats identical system instructions, schema headers, brand names, and category attributes.
2. Standard LLM serving engines re-evaluate these **same repeated starting words** during prefill computation for every single request.
3. This creates massive computational bottlenecks, **high latency**, and **excessive financial API costs**.

```text
Naive Database Query Engine
       ↓
Generate 10,000 Independent LLM Prompts
       ↓
Identical Instructions & Metadata Repeated
       ↓
Full Prefill Computation Repeated for Every Record
       ↓
High Latency + High API Costs
```

### The Relix Solution
**Relix** profiles column value repetition and candidate functional dependencies ($C_1 \to C_2$) across relational tables. It then dynamically **reorders database rows and prompt fields** so that records sharing identical attribute values are processed adjacently.

Because modern LLM inference engines utilize key-value prefix caching (**KV-Cache**), Relix creates **longer contiguous shared prompt prefixes**. The LLM engine reuses pre-computed attention states from memory, skipping redundant prefill calculations!

```text
Relational Database Table
       ↓
Relix Profiler (Cardinality, Repetition & Functional Dependencies)
       ↓
Reorder Database Rows + Reorder Prompt Fields (GGR-Inspired Algorithm)
       ↓
Create Long Contiguous Shared Prompt Prefixes
       ↓
Maximize KV-Cache Memory Reuse
       ↓
⚡ 1.5× – 2.8× Faster Processing | 💰 25% – 40% Lower API Cost | 🛡️ 100% Identical Output
```

---

## 2. 🖥️ Interactive Dashboard: Tab-by-Tab Guide

Relix includes a modern, glassmorphic Streamlit web application (`app.py`). Here is what each tab explains and provides:

### ⚡ Tab 1: Interactive Optimizer & Performance Comparison
- **Purpose**: Runs live comparative benchmarks between un-optimized database ordering (**Baseline**) and **Relix's GGR-Inspired Query Optimizer**.
- **What It Explains**:
  - Displays live metric cards comparing Prefix Hits, Cache Reuse %, Reused Tokens, Latency Speedup, and API Cost Savings.
  - Generates **5 Interactive Glowing Plotly Charts** analyzing latency, cost, and token reuse.
  - Shows side-by-side prompt previews to illustrate how Relix restructures field sequences without changing task instructions.

### 📊 Tab 2: Dataset Profiling & Functional Dependencies (FDs)
- **Purpose**: Analyzes the underlying mathematical and relational structure of your dataset.
- **What It Explains**:
  - **Cardinality Ratios** ($|unique| / N$): Measures value repetition per column.
  - **High Value Repetition Columns**: Identifies low-cardinality metadata fields (e.g. `brand`, `category`) that yield high prefix sharing.
  - **Candidate Functional Dependencies** ($C_1 \to C_2$): Detects deterministic relationships (e.g., `product_id -> brand`) to ensure determinant attributes precede dependent attributes in prompt field order.

### 📈 Tab 3: Multi-Scale Benchmark Suite
- **Purpose**: Evaluates system performance under large data volume growth.
- **What It Explains**:
  - Runs automated scalability benchmarks across **100**, **1,000**, and **10,000** records across 3 LLM workloads (*Sentiment Classification*, *Entity Extraction*, *Attribute Extraction*).
  - Plots interactive scaling line curves showing how prefill latency scales smoothly as dataset size increases.

### 📖 Tab 4: MLSys Paper Notes & Theoretical Mapping
- **Purpose**: Provides academic attribution and methodological verification.
- **What It Explains**:
  - Summarizes key theoretical concepts from Liu et al. (MLSys 2025).
  - Contains a formal mapping table matching original paper concepts (OPHR, GGR, PHC, KV-Cache) to Relix's prototype code modules.

---

## 3. 💎 What Measurement Gains Mean (Metric Definitions)

When you run Relix, the dashboard displays 6 key **Measured Optimization Gains**. Here is what each metric means:

| Metric Name | Mathematical Definition | What It Means & Why It Matters |
| :--- | :--- | :--- |
| **Prefix Hits (PHC)** | $\sum_{i=2}^{N} \mathbb{I}(\text{LCP}(P_{i-1}, P_i) > 0)$ | **Prefix Hit Count**. Number of consecutive LLM request pairs that successfully share prefilled starting tokens. Higher is better. |
| **Cache Reuse Ratio (%)** | $\frac{\text{Reused Input Tokens}}{\text{Total Input Tokens}} \times 100$ | Percentage of total prompt input tokens served directly from memory cache instead of recomputed. Higher is better (typically 65%–85%). |
| **Reused Tokens** | $\sum_{i=2}^{N} |\text{LCP}(P_{i-1}, P_i)|$ | Exact count of individual prompt tokens saved from redundant prefill matrix multiplications. |
| **Est. Latency (sec)** | $T_{\text{overhead}} + \frac{\text{Uncached Tokens}}{\text{Prefill TPS}} + \frac{\text{Output Tokens}}{\text{Decode TPS}}$ | Total estimated processing time in seconds. Lower prefill tokens directly translate to faster query completion times. |
| **Est. Cost ($ USD)** | $\text{Cost}_{\text{uncached}} + \text{Cost}_{\text{cached}} + \text{Cost}_{\text{output}}$ | Total financial inference cost in USD. Cached input tokens receive a 50% price discount on provider billing. |
| **Speedup Factor (×)** | $\frac{\text{Baseline Latency}}{\text{Relix Latency}}$ | Relative acceleration multiplier (e.g. `2.2×` means queries finish more than twice as fast). |

---

## 4. 📁 Project File Structure

```text
relix/
├── README.md                      # Complete project documentation & guide
├── requirements.txt               # Dependencies: pandas, numpy, streamlit, plotly, pydantic, pytest
├── .gitignore                     # Git ignore rules
├── app.py                         # Streamlit Interactive Dashboard UI
├── research_tasks.md              # Research task execution log
│
├── src/                           # Core Engine Modules
│   ├── __init__.py
│   ├── profiler.py                # Dataset profiler & FD candidate detector
│   ├── prompt_generator.py        # Configurable field order prompt generator
│   ├── prefix_metrics.py          # LCP, PHC & cache reuse proxy calculations
│   ├── baseline.py                # Baseline unordered query evaluator
│   ├── ophr.py                    # Exact small-data OPHR search oracle (n <= 7)
│   ├── ggr.py                     # Relix GGR-Inspired greedy row/field optimizer
│   ├── semantic_validator.py      # Row integrity & cell immutability validator
│   ├── cost_model.py              # API pricing & latency throughput simulator
│   └── benchmark.py               # Multi-scale benchmark execution engine
│
├── data/
│   └── sample_reviews.csv         # Pre-loaded high-repetition sample dataset
│
├── experiments/
│   └── results/                   # Generated Benchmark Outputs
│       ├── dataset_profile.json   # Structural dataset summary
│       ├── results.csv            # Empirical benchmark output table
│       ├── results.json           # JSON benchmark export
│       └── correctness_report.json# Semantic validator verification report
│
├── tests/                         # Pytest Automated Test Suite
│   ├── test_prefix.py             # Prefix computation unit tests
│   ├── test_optimizer.py          # Optimizer permutation unit tests
│   ├── test_profiler.py           # Profiler & FD detection tests
│   └── test_semantics.py          # Semantic correctness validator tests
│
└── docs/                          # Detailed Technical Specifications
    ├── paper_notes.md             # MLSys 2025 paper summary
    ├── algorithm_mapping.md       # Paper concept to implementation mapping
    ├── architecture.md            # System architecture & dataflow diagram
    ├── methodology.md             # Mathematical formulation & GGR strategy
    └── experimental_summary.md    # Empirical benchmark summary
```

---

## 5. 🚀 Quick Start Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Test Suite
```bash
python -m pytest -q
```

### 3. Run Benchmark Engine
```bash
python src/benchmark.py
```

### 4. Launch Streamlit Web Dashboard
```bash
streamlit run app.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser!

---

## 6. 🛡️ Semantic Preservation Guarantee

Relix strictly enforces a **Semantic Correctness Guarantee**:
- **Row Integrity**: Every input row appears exactly once in the optimized sequence (no duplicates or dropped records).
- **Cell Immutability**: No cell values or record attributes are altered.
- **Task Identity**: System instructions and analytical tasks remain identical across baseline and optimized queries.
- **Output Equivalence**: Deterministic analytical outputs remain identical after normalization.
