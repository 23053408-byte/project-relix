# Architecture & Dataflow Specification

## 1. System Architecture

```text
┌──────────────────────────────────────────────────────────┐
│                   Input Relational Data                   │
│                     (CSV / DataFrame)                    │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│                   Dataset Profiler                       │
│        (Cardinality, FDs, Repetition Frequencies)        │
└────────────────────────────┬─────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
┌──────────────────────────┐   ┌──────────────────────────┐
│     Baseline Engine      │   │    GGR-Inspired Optimizer│
│ (Original Row & Field)   │   │  (Reordered Rows & Fields│
└─────────────┬────────────┘   └────────────┬─────────────┘
              │                             │
              └──────────────┬──────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│                    Prompt Generator                      │
│             (Deterministic Template Builder)             │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│                    Prefix Analyzer                       │
│        (LCP, PHC, Reused Tokens, Cache Reuse %)          │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│                  Cost & Latency Model                    │
│      (Prefill/Decode Throughput & API Pricing Model)     │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│                 Streamlit Dashboard & UI                 │
│              (Interactive Plotly Charts)                 │
└──────────────────────────────────────────────────────────┘
```

## 2. Core Component Interactions

1. **Dataset Profiler (`src/profiler.py`)**: Computes summary statistics, identifies repeated value columns, and extracts candidate functional dependencies (e.g., `product_id -> brand`).
2. **Optimizer (`src/ggr.py` / `src/ophr.py`)**: Prioritizes low-cardinality determinant columns at the top of prompt field lists and groups identical attribute values adjacently.
3. **Prompt Generator (`src/prompt_generator.py`)**: Constructs standardized prompt strings formatted with the optimized field order.
4. **Prefix Analyzer (`src/prefix_metrics.py`)**: Calculates consecutive longest common prefixes (LCP), total reused tokens, and cache reuse ratio.
5. **Cost & Latency Simulator (`src/cost_model.py`)**: Applies token pricing discounts to cached tokens and estimates prefill/decode throughput speedup.
6. **Dashboard (`app.py`)**: Renders interactive controls, data tables, and metrics.
