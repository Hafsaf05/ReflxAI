
import streamlit as st

from generator import generate_code, fix_code
from sandbox import run_code

from critique import critique_code, optimize_code

from benchmark import benchmark_code

from evaluator import choose_best_version

from memory import (
    retrieve_memory,
    store_memory
)


# PAGE CONFIG
st.set_page_config(
    page_title="ReflexionAI",
    page_icon="🤖",
    layout="wide"
)


# HEADER
st.title("🤖 ReflexionAI")
st.caption(
    "Autonomous AI Software Engineering System"
)


# SIDEBAR
with st.sidebar:

    st.header("⚡ System Status")

    st.success("Generator Agent")
    st.success("Sandbox Executor")
    st.success("Critique Agent")
    st.success("Optimizer Agent")
    st.success("Vector Memory")

    st.divider()

    st.header("📊 Features")

    st.write("✅ Code Generation")
    st.write("✅ Autonomous Execution")
    st.write("✅ Self Debugging")
    st.write("✅ Memory Retrieval")
    st.write("✅ Optimization")
    st.write("✅ Benchmarking")


# TASK INPUT
st.subheader("💻 Enter Coding Task")

example_tasks = [
    "Write Python code for bubble sort",
    "Write inefficient Fibonacci code",
    "Write Python code for binary search",
    "Write Python code to detect duplicates in a list",
    "Write Python code for quick sort"
]

selected_example = st.selectbox(
    "Choose Example Task",
    ["Custom"] + example_tasks
)

if selected_example == "Custom":

    task = st.text_area(
        "Task",
        height=150,
        placeholder="Describe the coding task here..."
    )

else:

    task = selected_example

    st.text_area(
        "Selected Task",
        value=task,
        height=120,
        disabled=True
    )


# RUN BUTTON
run = st.button(
    "🚀 Run ReflexionAI",
    use_container_width=True
)


if run and task:

    with st.spinner("Agents are thinking..."):

        # MEMORY RETRIEVAL
        memories = retrieve_memory(task)

        # GENERATE CODE
        code = generate_code(
            task,
            memories
        )

        # EXECUTE CODE
        result = run_code(code)

        # CRITIQUE
        critique = critique_code(code)

        # OPTIMIZE
        optimized_code = optimize_code(
            code,
            critique
        )

        # BENCHMARKS
        original_benchmark = benchmark_code(code)

        optimized_benchmark = benchmark_code(
            optimized_code
        )

        # BEST VERSION
        decision = choose_best_version(
            code,
            original_benchmark,
            optimized_code,
            optimized_benchmark
        )


    # SUCCESS HEADER
    st.success("Agent Pipeline Completed")


    # METRICS
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Best Version",
            decision["winner"]
        )

    with col2:
        st.metric(
            "Original Runtime",
            f"{original_benchmark['runtime']:.6f}s"
        )

    with col3:
        st.metric(
            "Optimized Runtime",
            f"{optimized_benchmark['runtime']:.6f}s"
        )


    # AGENT TRACE
    st.subheader("🧠 Agent Trace")

    trace_cols = st.columns(5)

    trace_steps = [
        "Memory",
        "Generator",
        "Sandbox",
        "Critique",
        "Optimizer"
    ]

    for col, step in zip(trace_cols, trace_steps):
        col.success(step)


    # TABS
    tabs = st.tabs([
        "⚙️ Generated Code",
        "🚀 Optimized Code",
        "📊 Benchmarks",
        "🧠 Memory",
        "🔍 Critique",
        "▶️ Output"
    ])


    # GENERATED CODE TAB
    with tabs[0]:

        st.code(
            code,
            language="python"
        )


    # OPTIMIZED CODE TAB
    with tabs[1]:

        st.code(
            optimized_code,
            language="python"
        )


    # BENCHMARK TAB
    with tabs[2]:

        b1, b2 = st.columns(2)

        with b1:
            st.subheader("Original")
            st.json(original_benchmark)

        with b2:
            st.subheader("Optimized")
            st.json(optimized_benchmark)


    # MEMORY TAB
    with tabs[3]:

        st.write(memories)


    # CRITIQUE TAB
    with tabs[4]:

        st.write(critique)


    # OUTPUT TAB
    with tabs[5]:

        st.subheader("Execution Output")

        st.text(result["stdout"])

        if result["stderr"]:

            st.error(result["stderr"])

            store_memory(
                task,
                result["stderr"]
            )

            st.subheader("🛠️ Fixed Code")

            fixed_code = fix_code(
                code,
                result["stderr"]
            )

            st.code(
                fixed_code,
                language="python"
            )

else:

    st.info("Enter a coding task and run the agent.")
