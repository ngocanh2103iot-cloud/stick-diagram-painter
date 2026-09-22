import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import sys
sys.path.append('c:/Users/justi/.gemini/antigravity/scratch/Cmos_designer')
from logic_parser import LogicParser
from stick_renderer import StickRenderer

st.set_page_config(page_title="Layout Generator", page_icon="⚡", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 1.1rem;
        padding: 0.5rem 2rem;
        border-radius: 10px;
        border: none;
        font-weight: bold;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    .success-box {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .info-box {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ Layout Generator")
st.markdown("Generate optimal CMOS stick diagrams from boolean equations")

# Input Section
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Logic Input")
    
    # Quick examples
    example = st.selectbox(
        "Quick Examples",
        ["Custom", "NAND", "NOR", "Inverter", "AOI21", "AOI22"],
        index=0
    )
    
    if example == "NAND":
        default_eq = "Y = ~(A & B)"
    elif example == "NOR":
        default_eq = "Y = ~(A | B)"
    elif example == "Inverter":
        default_eq = "Y = ~A"
    elif example == "AOI21":
        default_eq = "Y = ~(A & (B | C))"
    elif example == "AOI22":
        default_eq = "Y = ~((A & B) | (C & D))"
    else:
        default_eq = "Y = ~(A & (B | C))"
    
    equation = st.text_input("Boolean Equation", value=default_eq, key="equation_input")
    
    st.markdown("**Supported Operators:**")
    st.markdown("- `&` : AND")
    st.markdown("- `|` : OR")
    st.markdown("- `~` : NOT")
    st.markdown("- `( )` : Grouping")
    
    generate_btn = st.button("🚀 Generate Layout", use_container_width=True)
    
    if generate_btn:
        try:
            parser = LogicParser()
            pdn, pun = parser.parse_equation(equation)
            
            st.markdown("<div class='success-box'>✅ Equation Parsed Successfully!</div>", unsafe_allow_html=True)
            
            # Find Euler Path
            euler_path = parser.find_euler_path()
            
            if euler_path:
                st.markdown(f"<div class='info-box'>🎯 <b>Optimal Poly Ordering:</b> {' → '.join(euler_path)}</div>", unsafe_allow_html=True)
                st.success("Single continuous diffusion strip is possible! ✨")
            else:
                st.warning("⚠️ No perfect Euler Path found. Layout may require breaks.")
                euler_path = sorted(list(parser.inputs))
            
            # Store results in session state
            st.session_state['euler_path'] = euler_path
            st.session_state['pdn'] = pdn
            st.session_state['pun'] = pun
            st.session_state['generated'] = True
            st.session_state['inputs'] = list(parser.inputs)
            
        except Exception as e:
            st.error(f"❌ Error parsing equation: {e}")
            st.session_state['generated'] = False

with col2:
    st.subheader("Stick Diagram Layout")
    if st.session_state.get('generated'):
        renderer = StickRenderer()
        fig = renderer.draw_layout(
            st.session_state['euler_path'], 
            st.session_state['pdn'], 
            st.session_state['pun']
        )
        st.pyplot(fig)
        
        # Legend
        st.markdown("""
        **Legend:**
        - 🟥 **Red**: Polysilicon (Gates / Inputs)
        - 🟩 **Green**: N-Diffusion (NMOS Active Area)
        - 🟧 **Orange**: P-Diffusion (PMOS Active Area)
        - 🟦 **Blue**: Metal 1 (VCC, GND, Output)
        - ⬛ **Black X**: Contacts (Vias)
        """)
    else:
        st.info("👈 Enter an equation and click 'Generate Layout' to see the result.")

# Show schematic if generated
if st.session_state.get('generated'):
    st.markdown("---")
    st.subheader("📊 Transistor-Level Schematic")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Pull-Down Network (NMOS)**")
        fig_pdn, ax_pdn = plt.subplots(figsize=(5, 4))
        pos = nx.spring_layout(st.session_state['pdn'], seed=42)
        nx.draw(st.session_state['pdn'], pos, ax=ax_pdn, with_labels=True, 
                node_color='lightgreen', node_size=800, edge_color='black', 
                font_size=10, font_weight='bold')
        edge_labels = nx.get_edge_attributes(st.session_state['pdn'], 'label')
        nx.draw_networkx_edge_labels(st.session_state['pdn'], pos, edge_labels=edge_labels, ax=ax_pdn)
        ax_pdn.set_title("PDN: Series for AND, Parallel for OR")
        st.pyplot(fig_pdn)
    
    with col2:
        st.markdown("**Pull-Up Network (PMOS)**")
        fig_pun, ax_pun = plt.subplots(figsize=(5, 4))
        pos = nx.spring_layout(st.session_state['pun'], seed=42)
        nx.draw(st.session_state['pun'], pos, ax=ax_pun, with_labels=True, 
                node_color='orange', node_size=800, edge_color='black', 
                font_size=10, font_weight='bold')
        edge_labels = nx.get_edge_attributes(st.session_state['pun'], 'label')
        nx.draw_networkx_edge_labels(st.session_state['pun'], pos, edge_labels=edge_labels, ax=ax_pun)
        ax_pun.set_title("PUN: Parallel for AND, Series for OR")
        st.pyplot(fig_pun)
    
    # Analysis
    st.markdown("### 📈 Analysis")
    num_inputs = len(st.session_state['inputs'])
    st.metric("Number of Inputs", num_inputs)
    st.markdown(f"**Input Variables:** {', '.join(sorted(st.session_state['inputs']))}")
