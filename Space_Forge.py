import streamlit as st
from streamlit_drawable_canvas import st_canvas
import pandas as pd
import json

# Page Configuration
st.set_page_config(page_title="Space Forge: Professional CAD", layout="wide")
st.title("🛠️ Space Forge: Professional CAD Tool")

# Initialize session state
if 'canvas_tool' not in st.session_state:
    st.session_state.canvas_tool = "line"
if 'stroke_width' not in st.session_state:
    st.session_state.stroke_width = 2
if 'stroke_color' not in st.session_state:
    st.session_state.stroke_color = "#000000"
if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#FFFFFF"
if 'canvas_size' not in st.session_state:
    st.session_state.canvas_size = 1000
if 'canvas_scale' not in st.session_state:
    st.session_state.canvas_scale = 1.0
if 'drawing_objects' not in st.session_state:
    st.session_state.drawing_objects = []
if 'canvas_key' not in st.session_state:
    st.session_state.canvas_key = 0

# Tool definitions
tools = {
    "select": "Select and transform objects",
    "line": "Draw a line between two points",
    "circle": "Draw a circle (center point + radius)",
    "rect": "Draw a rectangle",
    "triangle": "Draw a triangle",
    "freedraw": "Free drawing tool"
}

# Sidebar - Tools and Properties
with st.sidebar:
    st.header("🛠️ CAD Tools")
    
    # Tool selection
    st.session_state.canvas_tool = st.selectbox(
        "Drawing Tool:",
        options=list(tools.keys()),
        format_func=lambda x: f"{x.capitalize()} - {tools[x]}"
    )
    
    # Properties
    st.header("Properties")
    st.session_state.stroke_width = st.slider("Line Width:", 1, 10, 2)
    st.session_state.stroke_color = st.color_picker("Line Color:", "#000000")
    st.session_state.bg_color = st.color_picker("Background Color:", "#FFFFFF")
    
    # Canvas settings
    st.header("Canvas Settings")
    st.session_state.canvas_size = st.number_input("Canvas Size (pixels):", 500, 2000, 1000)
    st.session_state.canvas_scale = st.slider("Zoom Level:", 0.5, 2.0, 1.0, 0.1)
    
    # Actions
    st.header("Actions")
    if st.button("🔄 Clear Canvas", use_container_width=True):
        st.session_state.drawing_objects = []
        st.session_state.canvas_key += 1
        st.rerun()
    
    if st.button("💾 Save Project", use_container_width=True):
        if st.session_state.drawing_objects:
            st.download_button(
                label="Download Drawing Data",
                data=json.dumps(st.session_state.drawing_objects),
                file_name="project.json",
                mime="application/json",
                use_container_width=True
            )

# Main content area
col1, col2 = st.columns([3, 1])

with col1:
    st.header("🎨 Drawing Canvas")
    
    # Display grid and measurements if enabled
    if st.checkbox("Show Grid", True):
        st.caption(f"Canvas Size: {st.session_state.canvas_size}px × {st.session_state.canvas_size}px | Scale: {st.session_state.canvas_scale}")
    
    # Create the canvas
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=st.session_state.stroke_width,
        stroke_color=st.session_state.stroke_color,
        background_color=st.session_state.bg_color,
        background_image=None,
        update_streamlit=True,
        height=st.session_state.canvas_size,
        width=st.session_state.canvas_size,
        drawing_mode=st.session_state.canvas_tool,
        initial_drawing=st.session_state.drawing_objects,
        key=f"canvas_{st.session_state.canvas_key}",
    )
    
    # Update drawing objects if canvas has changed
    if canvas_result.json_data is not None:
        st.session_state.drawing_objects = canvas_result.json_data.get("objects", [])

with col2:
    st.header("📋 Object Properties")
    
    if st.session_state.drawing_objects:
        st.write(f"Objects on canvas: {len(st.session_state.drawing_objects)}")
        
        # Display properties of selected object
        if canvas_result.selected_object is not None:
            st.subheader("Selected Object")
            st.json(canvas_result.selected_object)
    else:
        st.info("No objects on canvas. Start drawing using the tools in the sidebar.")
    
    st.header("📐 Measurements")
    if st.session_state.drawing_objects:
        # Calculate approximate total line length
        total_length = 0
        for obj in st.session_state.drawing_objects:
            if obj.get("type") == "line":
                x1, y1 = obj.get("x1", 0), obj.get("y1", 0)
                x2, y2 = obj.get("x2", 0), obj.get("y2", 0)
                length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
                total_length += length
        
        st.metric("Total Line Length", f"{total_length:.2f} pixels")
    else:
        st.write("No measurements available")

# Instructions section
with st.expander("📖 How to Use This CAD Tool"):
    st.markdown("""
    **Professional CAD Tool Instructions:**
    
    1. **Select a Tool** from the sidebar
        - **Line**: Click and drag to create straight lines
        - **Circle**: Click for center, drag to set radius
        - **Rect**: Click and drag to create rectangles
        - **Triangle**: Coming soon (use line tool for now)
        - **Select**: Click on objects to select and transform them
    
    2. **Adjust Properties**:
        - Set line width and color before drawing
        - Customize canvas background color
        - Adjust canvas size and zoom level
    
    3. **Precision Drawing**:
        - Use the grid for accurate measurements
        - Select objects to view and edit their properties
        - Export your project when finished
    """)

# Footer
st.divider()
st.caption("Space Forge CAD Tool v1.0 • Designed for Amazon FC Space Management")
