import streamlit as st

from generator import generate_code, fix_code
from sandbox import run_code
from critique import critique_code, optimize_code
from benchmark import benchmark_code
from evaluator import choose_best_version
from memory import retrieve_memory, store_memory

from theme import inject_css, render_header, render_timeline, render_metrics

# 1. PAGE CONFIG
st.set_page_config(
    page_title="REFLX.AI Engine",
    page_icon="⟁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. INJECT CSS
inject_css()

# 3. HEADER
render_header()

# 4. SIDEBAR CONFIG
with st.sidebar:
    st.markdown("### Config Panel")
    
    model_name = st.selectbox(
        "Agent Model",
        options=["llama-3.3-70b-versatile", "mixtral-8x7b-32768"],
        index=0,
        help="Model used for code synthesis and critique."
    )
    
    temp_val = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.1,
        help="Higher values increase randomness, lower values are more deterministic."
    )
    
    mem_k = st.slider(
        "Memory Recall Depth (k)",
        min_value=1,
        max_value=5,
        value=2,
        help="Number of historical failure contexts to retrieve."
    )
    
    timeout_val = st.slider(
        "Sandbox Timeout (s)",
        min_value=1,
        max_value=10,
        value=5,
        help="Maximum time allowed for code execution in the sandbox."
    )
    
    st.markdown("<br><hr style='border-color: #1E1E24;'><br>", unsafe_allow_html=True)
    st.markdown("### Vector Store")
    st.code("Collection: failure_memory\nBackend: ChromaDB", language="text")

# 5. DEFINE REQUEST / TEMPLATES
if "task_input_area" not in st.session_state:
    st.session_state.task_input_area = ""

st.markdown("### Define Request")

# Text Area for instructions
task = st.text_area(
    "Instructions",
    label_visibility="collapsed",
    height=120,
    key="task_input_area",
    placeholder="E.g., Write a highly optimized Python function for bubble sort..."
)

# Quick templates rendered as compact buttons/chips below textarea
example_tasks = [
    "Write Python code for bubble sort",
    "Write inefficient Fibonacci code",
    "Write Python code for binary search",
    "Write Python code to detect duplicates in a list",
    "Write Python code for quick sort"
]

st.markdown("<div style='font-size: 0.75rem; color: #8E8E9F; margin-top: 0.5rem;'>Templates:</div>", unsafe_allow_html=True)
cols = st.columns(len(example_tasks))
for idx, example in enumerate(example_tasks):
    with cols[idx]:
        chip_label = example.replace("Write Python code for ", "").replace("Write ", "").capitalize()
        # Small buttons styled like chips
        if st.button(chip_label, key=f"chip_{idx}"):
            st.session_state.task_input_area = example
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# 6. RUN BUTTON
st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
run = st.button("Initialize Pipeline  →", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# 7. PIPELINE EXECUTION
if run and task:
    st.markdown("### Pipeline Execution Monitor")
    
    # Initialize timeline stages state
    stages = {
        "memory": {"status": "pending", "detail": "Waiting for memory query..."},
        "generator": {"status": "pending", "detail": "Waiting for synthesis..."},
        "sandbox": {"status": "pending", "detail": "Waiting for execution..."},
        "critique": {"status": "pending", "detail": "Waiting for review..."},
        "optimizer": {"status": "pending", "detail": "Waiting for optimizations..."},
        "benchmark": {"status": "pending", "detail": "Waiting for profiling..."},
        "evaluator": {"status": "pending", "detail": "Waiting for champion selection..."}
    }
    
    # Empty container for the live status timeline
    timeline_placeholder = st.empty()
    
    # Initial render
    with timeline_placeholder:
        render_timeline(stages)
        
    # Helper to update active stage and render
    def update_stage(key, status, detail):
        stages[key] = {"status": status, "detail": detail}
        with timeline_placeholder:
            render_timeline(stages)

    # --- Step 1: Memory Retrieve ---
    update_stage("memory", "running", "Querying ChromaDB failure logs...")
    try:
        memories = retrieve_memory(task, k=mem_k)
        num_mem = len(memories[0]) if (memories and len(memories) > 0) else 0
        update_stage("memory", "success", f"Retrieved {num_mem} relevant memory contexts")
    except Exception as e:
        update_stage("memory", "failed", f"Recall failed: {str(e)}")
        memories = None

    # --- Step 2: Generator Agent ---
    update_stage("generator", "running", f"Synthesizing candidate code via {model_name}...")
    try:
        code = generate_code(task, memories, model=model_name, temperature=temp_val)
        update_stage("generator", "success", "Candidate code (V1) synthesized")
    except Exception as e:
        update_stage("generator", "failed", f"Generation failed: {str(e)}")
        code = ""

    # --- Step 3: Sandbox Executor ---
    if code:
        update_stage("sandbox", "running", f"Running inside Python subprocess (timeout={timeout_val}s)...")
        try:
            result = run_code(code, timeout=timeout_val)
            if result["stderr"]:
                update_stage("sandbox", "failed", "Runtime error detected in sandbox")
            else:
                update_stage("sandbox", "success", "Code executed successfully in sandbox")
        except Exception as e:
            update_stage("sandbox", "failed", f"Sandbox crash: {str(e)}")
            result = {"stdout": "", "stderr": str(e)}
    else:
        update_stage("sandbox", "failed", "No candidate code to execute")
        result = {"stdout": "", "stderr": "No code generated"}

    # --- Step 4: Critique Agent ---
    if code:
        update_stage("critique", "running", "Evaluating implementation heuristics...")
        try:
            critique = critique_code(code, model=model_name, temperature=temp_val)
            update_stage("critique", "success", "Code critique completed")
        except Exception as e:
            update_stage("critique", "failed", f"Critique failed: {str(e)}")
            critique = "Critique unavailable."
    else:
        update_stage("critique", "failed", "No code to critique")
        critique = ""

    # --- Step 5: Optimizer Module ---
    if code and critique:
        update_stage("optimizer", "running", "Synthesizing optimized implementation...")
        try:
            optimized_code = optimize_code(code, critique, model=model_name, temperature=temp_val)
            update_stage("optimizer", "success", "Optimized code synthesized")
        except Exception as e:
            update_stage("optimizer", "failed", f"Optimization failed: {str(e)}")
            optimized_code = code
    else:
        update_stage("optimizer", "failed", "Missing V1 code or critique")
        optimized_code = code

    # --- Step 6: Differential Benchmarker ---
    if code and optimized_code:
        update_stage("benchmark", "running", "Measuring runtime & memory profiles...")
        try:
            original_benchmark = benchmark_code(code)
            optimized_benchmark = benchmark_code(optimized_code)
            update_stage("benchmark", "success", "Microbenchmarking complete")
        except Exception as e:
            update_stage("benchmark", "failed", f"Profiling failed: {str(e)}")
            original_benchmark = {"success": False, "error": str(e)}
            optimized_benchmark = {"success": False, "error": str(e)}
    else:
        update_stage("benchmark", "failed", "Missing candidate codes to benchmark")
        original_benchmark = {"success": False}
        optimized_benchmark = {"success": False}

    # --- Step 7: Evaluator ---
    update_stage("evaluator", "running", "Determining champion implementation...")
    try:
        decision = choose_best_version(code, original_benchmark, optimized_code, optimized_benchmark)
        winner_lbl = "Optimized" if decision["winner"] == "optimized" else "Base V1"
        update_stage("evaluator", "success", f"Selected {winner_lbl} as final output")
    except Exception as e:
        update_stage("evaluator", "failed", f"Evaluation failed: {str(e)}")
        decision = {"winner": "original", "code": code}

    st.markdown("<br>### Champion Compilation", unsafe_allow_html=True)
    
    # 8. PREMIUM METRICS
    base_time = original_benchmark.get("runtime") if original_benchmark.get("success") else None
    opt_time = optimized_benchmark.get("runtime") if optimized_benchmark.get("success") else None
    peak_mem = optimized_benchmark.get("memory") if optimized_benchmark.get("success") else None
    
    render_metrics(decision["winner"], base_time, opt_time, peak_mem)
    
    # 9. RESULTS TABS (VSCODE-STYLE OVERRIDES APPLIED)
    t1, t2, t3, t4 = st.tabs(["💻 Editor Source", "📋 Sandbox Output", "⚖️ Profiler Details", "🧠 Meta Context"])
    
    with t1:
        st.markdown("**Selected Champion Source Code:**")
        champion_src = optimized_code if decision["winner"] == "optimized" else code
        st.code(champion_src, language="python")
        
        if decision["winner"] == "optimized":
            with st.expander("View Original V1 Source"):
                st.code(code, language="python")
        
    with t2:
        # Standard stdout log
        stdout_content = result.get("stdout", "").strip()
        stdout_html = f"""
        <div class="terminal-container">
            <div class="terminal-header">
                <span>stdout - sandbox_session</span>
                <span>Python 3.10</span>
            </div>
            <div class="terminal-body">{stdout_content if stdout_content else 'No output written to stdout.'}</div>
        </div>
        """
        st.markdown(stdout_html, unsafe_allow_html=True)
        
        # Standard stderr log (if crash)
        if result.get("stderr"):
            stderr_content = result.get("stderr", "").strip()
            stderr_html = f"""
            <div class="terminal-container">
                <div class="terminal-header">
                    <span style="color: #F87171;">stderr - Exception Stacktrace</span>
                    <span style="color: #F87171;">error</span>
                </div>
                <div class="terminal-body error">{stderr_content}</div>
            </div>
            """
            st.markdown(stderr_html, unsafe_allow_html=True)
            
            # Store in failure database
            store_memory(task, result["stderr"])
            
            # Self-healing attempt
            with st.expander("Self-Healing Patch (Autonomous Recovery)"):
                st.markdown("Sandbox threw exceptions. Generator created this recovery patch:")
                fixed_code = fix_code(code, result["stderr"], model=model_name, temperature=temp_val)
                st.code(fixed_code, language="python")
                
    with t3:
        colA, colB = st.columns(2)
        with colA:
            st.markdown("**Base V1 Profiler JSON**")
            st.json(original_benchmark)
        with colB:
            st.markdown("**Optimized Profiler JSON**")
            st.json(optimized_benchmark)
            
    with t4:
        st.markdown("**Retrieval-Augmented Memories:**")
        if memories:
            st.write(memories)
        else:
            st.info("No relevant historical memories retrieved.")
            
        st.markdown("**Critique & Self-Reflection Report:**")
        st.info(critique)

elif run and not task:
    st.error("Operation Aborted: Please explicitly define a request before initializing the pipeline.")
