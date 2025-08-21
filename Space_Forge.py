import streamlit as st
from streamlit_drawable_canvas import st_canvas

# Page Configuration
st.set_page_config(page_title="Space Forge: CAD", layout="wide")
st.title("🛠️ Space Forge: CAD Canvas")

# Initialize session state for canvas reset
if 'canvas_key' not in st.session_state:
    st.session_state.canvas_key = 0

# Initialize drawing settings
drawing_mode = st.sidebar.selectbox(
    "Drawing tool:",
    ("freedraw", "line", "rect", "circle", "transform")
)

stroke_width = st.sidebar.slider("Stroke width: ", 1, 25, 3)
stroke_color = st.sidebar.color_picker("Stroke color: ")
bg_color = st.sidebar.color_picker("Background color: ", "#eee")

# Canvas size settings
canvas_size = st.sidebar.number_input("Canvas Size (px):", min_value=400, value=800, step=100)

# Main canvas
st.header("Draw on the Canvas Below")
st.markdown("""
- **Choose tools and colors from the sidebar**
- **Click and drag to draw** 
- **Select 'transform' to move objects**
""")

canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    background_image=None,
    update_streamlit=True,
    height=canvas_size,
    width=canvas_size,
    drawing_mode=drawing_mode,
    point_display_radius=0,
    key=f"canvas_{st.session_state.canvas_key}",
)

# Controls
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Clear Canvas"):
        st.session_state.canvas_key += 1
        st.rerun()

with col2:
    if st.button("💾 Save Drawing"):
        if canvas_result.image_data is not None:
            st.success("Drawing saved to session state")
            st.session_state.last_drawing = canvas_result.image_data
        else:
            st.warning("Nothing to save")

with col3:
    if st.button("📤 Export JSON"):
        if canvas_result.json_data is not None:
            st.download_button(
                label="Download Drawing Data",
                data=str(canvas_result.json_data),
                file_name="drawing_data.json",
                mime="application/json"
            )
