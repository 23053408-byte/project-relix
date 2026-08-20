# Methodology & Algorithmic Details

## 1. Problem Formulation

Given a relational dataset $D$ with $n$ records and schema fields $F = \{f_1, f_2, \dots, f_m\}$, an LLM query task $T$ transforms each record $r_i \in D$ into a text prompt $P(r_i, \pi_f)$ where $\pi_f$ is a field ordering permutation.

The objective is to find a record row sequence $\pi_r$ and a field order permutation $\pi_f$ that maximizes the **Total Prefix Hit Count (PHC)**:

$$\max_{\pi_r, \pi_f} \sum_{i=2}^{n} | \text{LCP}(P(r_{\pi_r(i-1)}, \pi_f), P(r_{\pi_r(i)}, \pi_f)) |$$

subject to semantic preservation constraint:
$$\text{Output}(P(r_i, \pi_f)) \equiv \text{Output}(P(r_i, \text{default}))$$

---

## 2. GGR-Inspired Heuristic Strategy

1. **Field Prioritization**:
   - Compute cardinality ratio $CR(f) = \frac{|\text{unique}(f)|}{n}$.
   - Rank fields in ascending order of $CR(f)$. Low-cardinality metadata fields (e.g. `category`, `brand`) are placed before high-cardinality text fields (`review_text`).
   - If candidate functional dependency $C_1 \to C_2$ exists, place determinant $C_1$ immediately before dependent $C_2$.

2. **Row Clustering**:
   - Sort database rows lexicographically by the top prioritized fields $\pi_f[1 \dots k]$.
   - This groups records sharing identical prefix attribute values into contiguous blocks.

3. **Prefix Evaluation**:
   - Compute $LCP$ over sequential prompts.
   - Evaluate cache reuse ratio and pass output to cost/latency simulation.
