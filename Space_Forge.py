import streamlit as st
from streamlit_drawable_canvas import st_canvas
import pandas as pd
from PIL import Image

# Page Configuration
st.set_page_config(page_title="Space Forge: CAD", layout="wide")
st.title("🛠️ Space Forge: CAD Canvas")

# Initialize session state
if 'canvas_size' not in st.session_state:
    st.session_state.canvas_size = 1000
if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#FFFFFF"
if 'drawing_mode' not in st.session_state:
    st.session_state.drawing_mode = "freedraw"
if 'stroke_color' not in st.session_state:
    st.session_state.stroke_color = "#000000"
if 'stroke_width' not in st.session_state:
    st.session_state.stroke_width = 3

# Main interface
col1, col2 = st.columns([1, 3])

with col1:
    st.header("🛠️ Tools")
    
    # Canvas Settings
    st.subheader("Canvas Settings")
    st.session_state.canvas_size = st.number_input("Canvas Size (px)", min_value=500, value=1000, step=100)
    st.session_state.bg_color = st.color_picker("Background Color", "#FFFFFF")
    
    # Drawing Tools
    st.subheader("Drawing Tools")
    st.session_state.drawing_mode = st.selectbox(
        "Tool:",
        ("freedraw", "line", "rect", "circle", "transform")
    )
    st.session_state.stroke_color = st.color_picker("Stroke Color:", "#000000")
    st.session_state.stroke_width = st.slider("Stroke Width:", 1, 10, 3)
    
    if st.button("🗑️ Clear Canvas", type="primary"):
        st.session_state.canvas_key += 1
        st.rerun()

with col2:
    st.header("🎨 Canvas")
    
    # Create a canvas component
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
        stroke_width=st.session_state.stroke_width,
        stroke_color=st.session_state.stroke_color,
        background_color=st.session_state.bg_color,
        background_image=None,
        update_streamlit=True,
        height=st.session_state.canvas_size,
        width=st.session_state.canvas_size,
        drawing_mode=st.session_state.drawing_mode,
        point_display_radius=0,
        key="main_canvas",
    )

    # Do something interesting with the canvas data
    if canvas_result.json_data is not None:
        objects = pd.json_normalize(canvas_result.json_data["objects"])
        if not objects.empty:
            st.write(f"Objects on canvas: {len(objects)}")
            st.dataframe(objects)

# Sidebar for info
with st.sidebar:
    st.header("ℹ️ Info")
    st.markdown("""
    **How to use:**
    1. Select a tool (draw, rectangle, circle, etc.)
    2. Choose a color and stroke width.
    3. **Click and drag** on the canvas to draw.
    4. Use the 'transform' tool to select and move objects.
    """)
