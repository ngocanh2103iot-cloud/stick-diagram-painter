import streamlit as st

# Page config
st.set_page_config(
    page_title="Stick Diagram Painter",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS (Combined from app.py and Home.py)
st.markdown("""
<style>
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: white;
    }
    .sidebar-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: white;
        text-align: center;
        padding: 1rem 0;
    }
    
    /* Main Content Styling */
    .main-title {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: left; /* Align left */
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.3rem;
        text-align: left; /* Align left */
        color: #333; /* Darker color for white background */
        margin-bottom: 2rem;
    }
    .theory-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: #333; /* Ensure text is visible */
    }
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        color: #333;
    }
    .vlsi-colors {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        margin: 1rem 0;
    }
    .color-box {
        padding: 1rem 2rem;
        border-radius: 8px;
        font-weight: bold;
        text-align: center;
        flex: 1;
        min-width: 120px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Content
with st.sidebar:
    st.markdown("<h2 class='sidebar-title'>Stick Diagram Painter</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Navigation")
    st.markdown("Use the pages above to navigate")
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    **Version:** 1.0.0  
    **Author:** VLSI CAD Team  
    **Purpose:** Educational Tool for Physical Design
    """)
    st.markdown("---")
    st.markdown("#### Quick Tips")
    st.markdown("💡 Start with simple gates like NAND")
    st.markdown("💡 Check the theory on the homepage")
    st.markdown("💡 Use the quick examples dropdown")

# Main Content (From Home.py)

# Header with logo (Logo Left, Title Right)
col1, col2 = st.columns([1, 4]) # Adjust ratio for logo vs title

with col1:
    try:
        st.image("C:/Users/justi/.gemini/antigravity/brain/84c85642-6ae9-48cb-bdfd-a357ef2b26ea/stick_diagram_logo_1765273112986.png", use_container_width=True)
    except:
        pass

with col2:
    st.markdown("<h1 class='main-title'>Stick Diagram Painter</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Physical Design Automation Tool</p>", unsafe_allow_html=True)

st.markdown("---")

# Introduction
st.markdown("""
### 🎯 What is this tool?

The **Stick Diagram Painter** is an educational tool that bridges the gap between **Boolean Logic** and **Physical VLSI Layout**. 
It automatically generates optimized stick diagrams from CMOS logic equations using graph theory and Euler path algorithms.
""")

# Theory Section
# Theory Section
st.markdown("""
<div class='theory-card'>
<h2>📚 Theoretical Foundation</h2>
<h3>Why Euler Paths Matter in VLSI Design</h3>
<p>In CMOS circuit design, every logic gate consists of two complementary networks:</p>
<ul>
<li><strong>Pull-Down Network (PDN)</strong>: NMOS transistors that connect output to GND when the gate is ON</li>
<li><strong>Pull-Up Network (PUN)</strong>: PMOS transistors that connect output to VCC when the gate is OFF</li>
</ul>

<h4>The Layout Challenge</h4>
<p>To create a <strong>compact, efficient layout</strong>, the order of inputs (polysilicon gates) must be <strong>identical</strong> in both PDN and PUN. 
This allows for:</p>
<ol>
<li>✅ <strong>Continuous diffusion strips</strong> (no breaks)</li>
<li>✅ <strong>Minimal area</strong> (fewer contacts and routing)</li>
<li>✅ <strong>Higher performance</strong> (lower parasitic capacitance)</li>
</ol>

<h4>The Graph Theory Solution</h4>
<p>We model PDN and PUN as graphs where:</p>
<ul>
<li><strong>Nodes</strong> = Source/drain terminals</li>
<li><strong>Edges</strong> = Transistors (labeled with input variables)</li>
</ul>
<p>An <strong>Euler Path</strong> is a path that visits every edge exactly once. Finding a <strong>common Euler path</strong> for both graphs 
gives us the optimal input ordering!</p>
</div>
""", unsafe_allow_html=True)

# VLSI Color Legend
st.markdown("## 🎨 Standard VLSI Stick Diagram Colors")
st.markdown("""
<div class='vlsi-colors'>
    <div class='color-box' style='background-color: #ff6b6b; color: white;'>🟥 Polysilicon (Gates)</div>
    <div class='color-box' style='background-color: #51cf66; color: white;'>🟩 N-Diffusion (NMOS)</div>
    <div class='color-box' style='background-color: #ff922b; color: white;'>🟧 P-Diffusion (PMOS)</div>
    <div class='color-box' style='background-color: #4dabf7; color: white;'>🟦 Metal-1 (Routing)</div>
</div>
""", unsafe_allow_html=True)

# Features
st.markdown("## ⚡ Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class='feature-card'>
    <h4>🧮 Logic Parser</h4>
    Parses boolean equations and constructs PDN/PUN graphs automatically.
    Supports AND (&), OR (|), NOT (~), and parentheses.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='feature-card'>
    <h4>🎨 Visual Renderer</h4>
    Generates industry-standard stick diagrams with proper color coding
    and automatic VCC/GND/Output routing.
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='feature-card'>
    <h4>🔍 Euler Path Finder</h4>
    Implements graph algorithms to find optimal transistor ordering,
    ensuring continuous diffusion strips.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='feature-card'>
    <h4>📊 Schematic View</h4>
    Visualizes the transistor-level network topology for both
    Pull-Up and Pull-Down networks.
    </div>
    """, unsafe_allow_html=True)

# Call to Action
st.markdown("---")
st.markdown("### 🚀 Ready to Start?")
st.markdown("Navigate to **Layout Generator** in the sidebar to create your first stick diagram!")

# Examples
with st.expander("📖 Example Equations to Try"):
    st.code("""
# Basic Gates
Y = ~(A & B)           # NAND
Y = ~(A | B)           # NOR
Y = ~A                 # Inverter

# Complex Gates
Y = ~(A & (B | C))     # AND-OR-Invert (AOI21)
Y = ~((A & B) | C)     # AOI22
Y = ~((A | B) & (C | D))  # Complex gate
    """)

# Initialize session state
if 'generated' not in st.session_state:
    st.session_state['generated'] = False
