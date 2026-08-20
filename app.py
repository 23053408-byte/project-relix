import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.profiler import profile_dataset
from src.baseline import evaluate_baseline
from src.ophr import optimize_ophr_exact
from src.ggr import optimize_ggr_inspired
from src.semantic_validator import validate_semantic_correctness
from src.benchmark import run_benchmark_suite, generate_synthetic_dataset

# Page configuration
st.set_page_config(
    page_title="LLM-Opt | Relational LLM Query Optimizer",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ LLM-Opt: Relational LLM Query Optimization")
st.caption("Based on Shu Liu et al., *Optimizing LLM Queries in Relational Data Analytics Workloads*, MLSys 2025.")

# Sidebar navigation & options
st.sidebar.header("⚙️ Settings & Dataset")

data_source = st.sidebar.radio(
    "Data Source",
    ["Upload CSV", "Use Default Sample Data", "Generate Synthetic Scale Data"]
)

uploaded_df = None
if data_source == "Upload CSV":
    uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=["csv"])
    if uploaded_file is not None:
        uploaded_df = pd.read_csv(uploaded_file)
elif data_source == "Use Default Sample Data":
    sample_path = "data/sample_reviews.csv"
    if os.path.exists(sample_path):
        uploaded_df = pd.read_csv(sample_path)
    else:
        uploaded_df = generate_synthetic_dataset(50)
else:
    synth_size = st.sidebar.slider("Synthetic Dataset Size (Rows)", 20, 2000, 200, step=20)
    uploaded_df = generate_synthetic_dataset(synth_size)

if uploaded_df is None or uploaded_df.empty:
    st.info("👈 Please select or upload a dataset using the sidebar.")
    st.stop()

# Workload selector
st.sidebar.subheader("🎯 LLM Workload Task")
workload_task = st.sidebar.selectbox(
    "Select Task Workload",
    ["sentiment", "entity_extraction", "attribute_extraction"],
    format_func=lambda x: x.replace("_", " ").title()
)

# Tabs navigation
tab_dataset, tab_optimize, tab_benchmark, tab_about = st.tabs([
    "📊 Dataset Profile", "⚡ Optimization & Comparison", "📈 Scaling Benchmark", "📖 About & Paper Notes"
])

# -------------------------------------------------------------------
# TAB 1: DATASET PROFILE
# -------------------------------------------------------------------
with tab_dataset:
    st.subheader("Dataset Preview & Profiling")
    
    col_preview1, col_preview2 = st.columns([2, 1])
    with col_preview1:
        st.write("##### Raw Data Table Preview")
        st.dataframe(uploaded_df.head(10), use_container_width=True)
    
    profile = profile_dataset(uploaded_df)
    with col_preview2:
        st.write("##### Summary Statistics")
        st.metric("Total Rows", profile["rows"])
        st.metric("Total Columns", profile["columns"])
        st.metric("Duplicate Rows", profile["duplicate_rows"])

    st.markdown("---")
    col_prof1, col_prof2 = st.columns(2)
    with col_prof1:
        st.write("##### Column Unique Values & Cardinality Ratio")
        card_df = pd.DataFrame({
            "Column": list(profile["unique_counts"].keys()),
            "Unique Count": list(profile["unique_counts"].values()),
            "Cardinality Ratio": list(profile["cardinality_ratio"].values()),
        })
        st.dataframe(card_df, use_container_width=True)

    with col_prof2:
        st.write("##### Candidate Functional Dependencies & Repetition")
        if profile["candidate_dependencies"]:
            st.success("Detected Candidate Functional Dependencies:")
            for fd in profile["candidate_dependencies"]:
                st.write(f"- `{fd}`")
        else:
            st.info("No strict candidate functional dependencies detected.")

        st.write("##### Columns with High Value Repetition:")
        if profile["repeated_value_columns"]:
            st.write(", ".join([f"`{c}`" for c in profile["repeated_value_columns"]]))
        else:
            st.write("None")

# -------------------------------------------------------------------
# TAB 2: OPTIMIZATION & COMPARISON
# -------------------------------------------------------------------
with tab_optimize:
    st.subheader("Interactive Query Optimization Comparison")

    run_opt = st.button("🚀 Run Baseline vs GGR-Inspired Optimization", type="primary")

    if run_opt or "opt_results" in st.session_state:
        if run_opt:
            with st.spinner("Computing optimization & prefix metrics..."):
                baseline_res = evaluate_baseline(uploaded_df, task_type=workload_task)
                ggr_res = optimize_ggr_inspired(uploaded_df, task_type=workload_task)
                
                # Check small data for OPHR
                ophr_res = None
                if len(uploaded_df) <= 7 and len(uploaded_df.columns) <= 4:
                    ophr_res = optimize_ophr_exact(uploaded_df, candidate_fields=list(uploaded_df.columns), task_type=workload_task)

                opt_df = uploaded_df.loc[ggr_res["row_order"]]
                correctness = validate_semantic_correctness(
                    uploaded_df, opt_df, baseline_res["prompts"], ggr_res["prompts"]
                )

                st.session_state["opt_results"] = {
                    "baseline": baseline_res,
                    "ggr": ggr_res,
                    "ophr": ophr_res,
                    "correctness": correctness
                }

        results = st.session_state["opt_results"]
        b_m = results["baseline"]["metrics"]
        g_m = results["ggr"]["metrics"]

        # Metric Cards
        st.markdown("### 📊 Metrics Summary")
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        
        speedup = round(b_m["estimated_latency_sec"] / max(g_m["estimated_latency_sec"], 1e-6), 2)
        cost_red = round(((b_m["total_cost_usd"] - g_m["total_cost_usd"]) / max(b_m["total_cost_usd"], 1e-6)) * 100, 1)

        m1.metric("Prefix Hits", g_m["prefix_hit_count"], delta=f"{g_m['prefix_hit_count'] - b_m['prefix_hit_count']}")
        m2.metric("Reuse Ratio", f"{g_m['cache_reuse_ratio']*100:.1f}%", delta=f"{(g_m['cache_reuse_ratio'] - b_m['cache_reuse_ratio'])*100:.1f}%")
        m3.metric("Reused Tokens", g_m["reused_prefix_tokens"], delta=f"{g_m['reused_prefix_tokens'] - b_m['reused_prefix_tokens']}")
        m4.metric("Est. Latency", f"{g_m['estimated_latency_sec']:.2f}s", delta=f"{g_m['estimated_latency_sec'] - b_m['estimated_latency_sec']:.2f}s", delta_color="inverse")
        m5.metric("Est. Cost", f"${g_m['total_cost_usd']:.4f}", delta=f"-{cost_red}%", delta_color="inverse")
        m6.metric("Speedup Factor", f"{speedup}×", delta="Over Baseline")

        # Correctness Alert
        cor = results["correctness"]
        if cor["status"] == "PASSED":
            st.success("✅ **Semantic Correctness Preserved**: 100% row integrity, cell value immutability, and prompt task identity verified.")
        else:
            st.error("⚠️ Semantic correctness check failed!")

        st.markdown("---")

        # Interactive Charts (6 Required Charts)
        st.markdown("### 📈 Visual Evaluation & Charts")

        methods = ["Baseline", "GGR-Inspired"]
        if results["ophr"] is not None:
            methods.append("OPHR (Exact)")

        chart_data = {
            "Method": ["Baseline", "GGR-Inspired"],
            "Prefix Hits": [b_m["prefix_hit_count"], g_m["prefix_hit_count"]],
            "Reuse Ratio (%)": [b_m["cache_reuse_ratio"] * 100, g_m["cache_reuse_ratio"] * 100],
            "Estimated Latency (s)": [b_m["estimated_latency_sec"], g_m["estimated_latency_sec"]],
            "Estimated Cost ($)": [b_m["total_cost_usd"], g_m["total_cost_usd"]],
            "Speedup": [1.0, speedup],
        }
        df_chart = pd.DataFrame(chart_data)

        c1, c2, c3 = st.columns(3)
        with c1:
            fig1 = px.bar(df_chart, x="Method", y="Prefix Hits", color="Method", title="1. Prefix Hit Count")
            st.plotly_chart(fig1, use_container_width=True)
        with c2:
            fig2 = px.bar(df_chart, x="Method", y="Reuse Ratio (%)", color="Method", title="2. Cache Reuse Ratio (%)")
            st.plotly_chart(fig2, use_container_width=True)
        with c3:
            fig3 = px.bar(df_chart, x="Method", y="Estimated Latency (s)", color="Method", title="3. Estimated Latency (sec)")
            st.plotly_chart(fig3, use_container_width=True)

        c4, c5 = st.columns(2)
        with c4:
            fig4 = px.bar(df_chart, x="Method", y="Estimated Cost ($)", color="Method", title="4. Estimated Cost ($ USD)")
            st.plotly_chart(fig4, use_container_width=True)
        with c5:
            fig5 = px.bar(df_chart, x="Method", y="Speedup", color="Method", title="5. Speedup vs Baseline")
            st.plotly_chart(fig5, use_container_width=True)

        # Field & Prompt comparison
        st.markdown("### 📝 Field & Prompt Order Comparison")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.write("**Baseline Field Order:**", ", ".join(results["baseline"]["field_order"]))
            st.text_area("Baseline Prompt Sample", results["baseline"]["prompts"][0], height=180)
        with col_p2:
            st.write("**GGR-Inspired Field Order:**", ", ".join(results["ggr"]["field_order"]))
            st.text_area("GGR-Inspired Prompt Sample", results["ggr"]["prompts"][0], height=180)

# -------------------------------------------------------------------
# TAB 3: SCALING BENCHMARK
# -------------------------------------------------------------------
with tab_benchmark:
    st.subheader("Multi-Scale Benchmark Execution (100, 1,000, 10,000 Rows)")
    
    if st.button("▶️ Run Automated Benchmark Suite", type="primary"):
        with st.spinner("Executing benchmark across dataset scale sizes..."):
            run_benchmark_suite()
            st.success("Benchmark completed! Results updated.")

    res_csv_path = "experiments/results/results.csv"
    if os.path.exists(res_csv_path):
        df_bench = pd.read_csv(res_csv_path)
        st.write("##### Benchmark Results Table")
        st.dataframe(df_bench, use_container_width=True)

        st.write("##### 6. Scaling with Number of Rows")
        fig_scale = px.line(
            df_bench,
            x="Rows",
            y="Estimated Latency (s)",
            color="Method",
            line_dash="Query",
            markers=True,
            title="Estimated Latency Scaling Across Dataset Rows"
        )
        st.plotly_chart(fig_scale, use_container_width=True)
    else:
        st.info("Run the automated benchmark suite to generate scaling charts.")

# -------------------------------------------------------------------
# TAB 4: ABOUT & PAPER NOTES
# -------------------------------------------------------------------
with tab_about:
    st.subheader("Methodological Foundation & MLSys 2025 Paper Reference")
    st.markdown("""
    **Primary Paper Reference:**
    - Shu Liu et al., *Optimizing LLM Queries in Relational Data Analytics Workloads*, Proceedings of Machine Learning and Systems (MLSys 2025).
    - [Paper PDF Link](https://proceedings.mlsys.org/paper_files/paper/2025/file/b5dc49f44db2fadc5c4d717c57f4a424-Paper-Conference.pdf)

    ### Honest Disclosure & Implementation Mapping
    | Paper Concept | Prototype Implementation | Label |
    | :--- | :--- | :--- |
    | Baseline | `src/baseline.py` | Baseline |
    | OPHR | `src/ophr.py` | Exact Small-Data Oracle |
    | GGR Algorithm | `src/ggr.py` | Inspired Implementation |
    | Prefix Hit Count (PHC) | `src/prefix_metrics.py` | Token LCP Implementation |
    | KV Cache Measurement | `src/prefix_metrics.py` | Whitespace Tokenization Proxy |
    | Latency & Cost | `src/cost_model.py` | Throughput Simulation Model |
    """)
