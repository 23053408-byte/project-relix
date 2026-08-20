# Algorithm Mapping: Paper vs. LLM-Opt Prototype

This document explicitly distinguishes between original MLSys 2025 paper concepts, our prototype implementation, and exact vs. simplified components.

| Paper Concept | Prototype Component | Implementation Type | Description |
| :--- | :--- | :--- | :--- |
| **Baseline Query Order** | `src/baseline.py` | Baseline | Evaluates original row order with static schema field ordering. |
| **OPHR Search** | `src/ophr.py` | Simplified Validation | Exact brute-force search over small datasets ($n \le 7$, $m \le 4$) used as correctness oracle. |
| **GGR Algorithm** | `src/ggr.py` | Inspired Implementation | Practical greedy optimizer using value frequency, cardinality ratio, and candidate functional dependencies. |
| **Prefix Hit Count (PHC)** | `src/prefix_metrics.py` | Implementation | Token-level longest common prefix matching across query sequences. |
| **vLLM KV Cache** | `src/prefix_metrics.py` | Simulated Proxy | Deterministic whitespace tokenization and prefix reuse proxy (without GPU vLLM daemon). |
| **Latency Model** | `src/cost_model.py` | Simulation Model | Prefill throughput + decode throughput + fixed overhead latency simulation. |
| **CAR (Correlation-Aware)** | Optional Extension | Original Extension | Optional correlation-weighted ordering heuristic (deferred post-MVP). |
