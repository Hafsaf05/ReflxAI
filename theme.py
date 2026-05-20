import streamlit as st
import os

def inject_css():
    """Reads style.css and injects it into the Streamlit app."""
    css_path = os.path.join(os.path.dirname(__file__), "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    else:
        # Fallback if not found
        st.warning("style.css not found in path.")

def render_header():
    """Renders a clean, technical VSCode/Cursor style header."""
    header_html = """
    <div style="display: flex; align-items: center; justify-content: space-between; padding-bottom: 0.75rem; margin-bottom: 1.5rem; border-bottom: 1px solid rgba(0,0,0,0.1);">
        <div style="display: flex; align-items: center; gap: 0.6rem;">
            <span style="font-family: 'Geist Mono', monospace; font-size: 1.4rem; color: #8B5CF6; font-weight: 800; animation: bounce-pulse 2s infinite;">⟁</span>
            <span style="font-family: 'Outfit', sans-serif; font-size: 1.1rem; font-weight: 800; letter-spacing: 0.05em; color: #0F172A;">REFLX.AI</span>
            <span style="font-family: 'Geist Mono', monospace; font-size: 0.7rem; background-color: rgba(255,255,255,0.7); border: 1px solid rgba(0,0,0,0.05); padding: 0.2rem 0.5rem; border-radius: 8px; color: #64748B; font-weight: 600;">v0.2-alpha</span>
        </div>
        <div style="display: flex; align-items: center; gap: 0.4rem;">
            <span style="width: 6px; height: 6px; border-radius: 50%; background-color: #10B981; display: inline-block;"></span>
            <span style="font-family: 'Geist Mono', monospace; font-size: 0.7rem; color: #8E8E9F;">SYSTEM: ONLINE</span>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

def render_timeline(stages_state):
    """
    Renders the custom live execution status timeline.
    
    stages_state: dict of {
        'memory': {'status': 'pending/running/success/failed', 'detail': 'description...'},
        ...
    }
    """
    stages_info = [
        ("memory", "Memory Recall"),
        ("generator", "Code Synthesis"),
        ("sandbox", "Sandbox Execution"),
        ("critique", "Critique & Analysis"),
        ("optimizer", "Optimization Phase"),
        ("benchmark", "Differential Profiling"),
        ("evaluator", "Champion Selection")
    ]
    
    steps_html = ""
    for key, name in stages_info:
        state = stages_state.get(key, {"status": "pending", "detail": "Waiting in queue..."})
        status = state.get("status", "pending")
        detail = state.get("detail", "")
        
        detail_class = "running" if status == "running" else "normal"
        name_class = "running" if status == "running" else "normal"
        
        steps_html += f"""
        <div class="timeline-step">
            <div class="step-dot {status}"></div>
            <div class="step-name {name_class}">{name}</div>
            <div class="step-details {detail_class}">{detail}</div>
        </div>
        """
        
    timeline_html = f"""
    <div class="timeline-container">
        <div class="timeline-title">Agent Execution Pipeline</div>
        <div class="timeline-steps">
            {steps_html}
        </div>
    </div>
    """
    st.markdown(timeline_html, unsafe_allow_html=True)

def render_metrics(winner, base_time, opt_time, peak_memory=None):
    """
    Renders custom metrics.
    
    winner: 'Optimized Version' or 'Original Version' or similar
    base_time: float or None
    opt_time: float or None
    peak_memory: int or None
    """
    # Format winner
    winner_display = "Optimized" if "opt" in winner.lower() else "Base V1"
    
    # Format times
    base_time_str = f"{base_time:.6f}s" if (isinstance(base_time, (int, float)) and base_time > 0) else "N/A"
    opt_time_str = f"{opt_time:.6f}s" if (isinstance(opt_time, (int, float)) and opt_time > 0) else "N/A"
    
    # Calculate speedup
    delta_html = ""
    if isinstance(base_time, (int, float)) and isinstance(opt_time, (int, float)) and base_time > 0 and opt_time > 0:
        if opt_time < base_time:
            speedup = base_time / opt_time
            pct = ((base_time - opt_time) / base_time) * 100
            delta_html = f'<div class="metric-delta positive">▲ {speedup:.1f}x speedup ({pct:.1f}% faster)</div>'
        elif opt_time > base_time:
            slowdown = opt_time / base_time
            pct = ((opt_time - base_time) / base_time) * 100
            delta_html = f'<div class="metric-delta negative">▼ {slowdown:.1f}x slower ({pct:.1f}% slower)</div>'
        else:
            delta_html = '<div class="metric-delta neutral">■ Identical runtime</div>'
    else:
        delta_html = '<div class="metric-delta neutral">No delta computed</div>'

    # Memory
    if peak_memory is not None and isinstance(peak_memory, (int, float)):
        # Convert bytes to KB or MB
        if peak_memory < 1024:
            mem_str = f"{peak_memory} B"
        elif peak_memory < 1024 * 1024:
            mem_str = f"{peak_memory / 1024:.1f} KB"
        else:
            mem_str = f"{peak_memory / (1024 * 1024):.1f} MB"
    else:
        mem_str = "N/A"

    metrics_html = f"""
    <div class="metric-container">
        <div class="metric-card">
            <div class="metric-label">Pipeline Winner</div>
            <div class="metric-value" style="color: #A78BFA;">{winner_display}</div>
            <div class="metric-delta neutral">Selected champion</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Base V1 Runtime</div>
            <div class="metric-value">{base_time_str}</div>
            <div class="metric-delta neutral">Unoptimized base</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Optimized Runtime</div>
            <div class="metric-value">{opt_time_str}</div>
            {delta_html}
        </div>
        <div class="metric-card">
            <div class="metric-label">Peak Memory</div>
            <div class="metric-value">{mem_str}</div>
            <div class="metric-delta neutral">Max trace usage</div>
        </div>
    </div>
    """
    st.markdown(metrics_html, unsafe_allow_html=True)
