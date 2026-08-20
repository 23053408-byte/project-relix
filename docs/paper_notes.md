# Paper Notes: Optimizing LLM Queries in Relational Data Analytics Workloads

> **Primary Paper Reference:**  
> Shu Liu et al., *Optimizing LLM Queries in Relational Data Analytics Workloads*, Proceedings of Machine Learning and Systems (MLSys 2025).  
> **Paper URL:** https://proceedings.mlsys.org/paper_files/paper/2025/file/b5dc49f44db2fadc5c4d717c57f4a424-Paper-Conference.pdf  
> **OpenReview:** https://openreview.net/forum?id=R7bK9yycHp

---

## 1. Core Problem Statement

Relational data analytics workloads increasingly use Large Language Models (LLMs) to perform semantic extraction, classification, scoring, and text synthesis over large database tables. When executed naively row-by-row, each prompt contains repeated schema headers, metadata, and recurring attribute values. Standard batch LLM serving re-evaluates these repeated prompt prefixes during prefill computation, incurring high computational latency and financial API costs.

---

## 2. Theoretical Foundations & Key Concepts

### Prefix Hit Count (PHC)
The paper defines **Prefix Hit Count (PHC)** as the quantitative metric measuring shared prefix tokens between consecutive LLM queries. By maximizing PHC across a batch sequence, the KV-cache of modern LLM serving engines (such as vLLM) retains shared prefill states, avoiding redundant matrix multiplications.

### Optimal Prefix Hit Recursion (OPHR)
OPHR formalizes the exact optimization problem over row orderings and field permutations within each record prompt. For $n$ rows and $m$ fields, the unconstrained search space size is $n! \times (m!)^n$, which is NP-hard. OPHR utilizes branch-and-bound recursion on small subsets to establish exact optimal bounds.

### Greedy Group Recursion (GGR)
To scale optimization to millions of database records, GGR partitions rows into hierarchical groups based on attribute value frequencies and candidate functional dependencies ($C_1 \to C_2$). GGR greedily places low-cardinality, high-frequency fields near the beginning of prompt templates and clusters records with identical attribute prefixes adjacently.

---

## 3. Reported Paper Performance Benchmark
In the authors' evaluated Apache Spark + vLLM environment across 16 LLM queries and 7 real-world datasets:
- **Speedup:** 1.5× to 3.4× end-to-end inference acceleration.
- **Cost Reduction:** Up to 32% reduction in serving cost.

> *Note: These reported metrics represent the published paper's distributed cluster setup. The LLM-Opt rapid prototype uses simulated prefill/decode throughput proxies and empirical whitespace tokenization metrics.*
