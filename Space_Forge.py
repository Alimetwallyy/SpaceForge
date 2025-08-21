import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Space Forge: Professional CAD", layout="wide")
st.title("🛠️ Space Forge: Professional CAD Tool")

# Initialize session state
if 'drawing_mode' not in st.session_state:
    st.session_state.drawing_mode = "select"
if 'shapes' not in st.session_state:
    st.session_state.shapes = []
if 'temp_points' not in st.session_state:
    st.session_state.temp_points = []
if 'canvas_size' not in st.session_state:
    st.session_state.canvas_size = 1000
if 'grid_size' not in st.session_state:
    st.session_state.grid_size = 50
if 'stroke_color' not in st.session_state:
    st.session_state.stroke_color = "#000000"
if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#FFFFFF"

# Tool definitions
tools = {
    "select": "Select objects",
    "line": "Draw a line between two points",
    "rectangle": "Draw a rectangle",
    "circle": "Draw a circle",
    "triangle": "Draw a triangle"
}

# Sidebar - Tools and Properties
with st.sidebar:
    st.header("🛠️ CAD Tools")
    
    # Tool selection
    st.session_state.drawing_mode = st.selectbox(
        "Drawing Tool:",
        options=list(tools.keys()),
        format_func=lambda x: f"{x.capitalize()} - {tools[x]}"
    )
    
    # Properties
    st.header("Properties")
    st.session_state.stroke_color = st.color_picker("Line Color:", "#000000")
    st.session_state.bg_color = st.color_picker("Background Color:", "#FFFFFF")
    
    # Canvas settings
    st.header("Canvas Settings")
    st.session_state.canvas_size = st.number_input("Canvas Size (units):", 500, 2000, 1000)
    st.session_state.grid_size = st.slider("Grid Size:", 10, 100, 50)
    
    # Actions
    st.header("Actions")
    if st.button("🔄 Clear Canvas", use_container_width=True):
        st.session_state.shapes = []
        st.session_state.temp_points = []
        st.rerun()
    
    if st.button("📐 Toggle Grid", use_container_width=True):
        st.session_state.show_grid = not st.session_state.get('show_grid', True)
        st.rerun()

# Create the main canvas
col1, col2 = st.columns([3, 1])

with col1:
    st.header("🎨 Drawing Canvas")
    
    # Create a clickable grid using Plotly
    fig = go.Figure()
    
    # Add grid if enabled
    if st.session_state.get('show_grid', True):
        grid_lines = []
        for i in range(0, st.session_state.canvas_size + 1, st.session_state.grid_size):
            grid_lines.append(
                dict(type="line", x0=i, y0=0, x1=i, y1=st.session_state.canvas_size, 
                     line=dict(color="lightgray", width=1))
            )
            grid_lines.append(
                dict(type="line", x0=0, y0=i, x1=st.session_state.canvas_size, y1=i, 
                     line=dict(color="lightgray", width=1))
            )
        fig.update_layout(shapes=grid_lines)
    
    # Add existing shapes to the plot
    for shape in st.session_state.shapes:
        if shape['type'] == 'line':
            fig.add_trace(go.Scatter(
                x=[shape['x1'], shape['x2']], y=[shape['y1'], shape['y2']],
                mode='lines', line=dict(color=shape['color'], width=2)
            ))
        elif shape['type'] == 'rectangle':
            x0, y0, x1, y1 = shape['x1'], shape['y1'], shape['x2'], shape['y2']
            fig.add_trace(go.Scatter(
                x=[x0, x1, x1, x0, x0], y=[y0, y0, y1, y1, y0],
                mode='lines', fill="none", line=dict(color=shape['color'], width=2)
            ))
    
    # Configure the layout
    fig.update_layout(
        width=700,
        height=700,
        xaxis=dict(range=[0, st.session_state.canvas_size], showgrid=False, zeroline=False),
        yaxis=dict(range=[0, st.session_state.canvas_size], showgrid=False, zeroline=False),
        plot_bgcolor=st.session_state.bg_color,
        dragmode="drawline" if st.session_state.drawing_mode != "select" else "select",
        title="Click to place points. Select tool to manipulate objects."
    )
    
    # Display the plot
    st.plotly_chart(fig, use_container_width=True)
    
    # Coordinate input for precision drawing
    st.subheader("📏 Precision Drawing")
    col_x, col_y = st.columns(2)
    with col_x:
        x_coord = st.number_input("X Coordinate:", 0, st.session_state.canvas_size, 0)
    with col_y:
        y_coord = st.number_input("Y Coordinate:", 0, st.session_state.canvas_size, 0)
    
    if st.button("Add Point at Coordinates"):
        st.session_state.temp_points.append((x_coord, y_coord))
        st.success(f"Point added at ({x_coord}, {y_coord})")
        
        # If we have enough points for the current tool, create the shape
        if st.session_state.drawing_mode == "line" and len(st.session_state.temp_points) >= 2:
            x1, y1 = st.session_state.temp_points[-2]
            x2, y2 = st.session_state.temp_points[-1]
            st.session_state.shapes.append({
                'type': 'line', 'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
                'color': st.session_state.stroke_color
            })
            st.session_state.temp_points = []
            st.rerun()
        
        elif st.session_state.drawing_mode == "rectangle" and len(st.session_state.temp_points) >= 2:
            x1, y1 = st.session_state.temp_points[-2]
            x2, y2 = st.session_state.temp_points[-1]
            st.session_state.shapes.append({
                'type': 'rectangle', 'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
                'color': st.session_state.stroke_color
            })
            st.session_state.temp_points = []
            st.rerun()

with col2:
    st.header("📋 Object Manager")
    
    if st.session_state.shapes:
        st.write(f"Objects on canvas: {len(st.session_state.shapes)}")
        
        for i, shape in enumerate(st.session_state.shapes):
            with st.expander(f"Object {i+1} - {shape['type']}"):
                st.write(f"Type: {shape['type']}")
                if shape['type'] == 'line':
                    st.write(f"From: ({shape['x1']}, {shape['y1']})")
                    st.write(f"To: ({shape['x2']}, {shape['y2']})")
                elif shape['type'] == 'rectangle':
                    st.write(f"Corner 1: ({shape['x1']}, {shape['y1']})")
                    st.write(f"Corner 2: ({shape['x2']}, {shape['y2']})")
                
                if st.button(f"Delete Object {i+1}", key=f"del_{i}"):
                    st.session_state.shapes.pop(i)
                    st.rerun()
    else:
        st.info("No objects on canvas. Use the tools to create shapes.")
    
    st.header("📐 Measurements")
    if st.session_state.shapes:
        total_length = 0
        for shape in st.session_state.shapes:
            if shape['type'] == 'line':
                dx = shape['x2'] - shape['x1']
                dy = shape['y2'] - shape['y1']
                total_length += (dx**2 + dy**2)**0.5
        
        st.metric("Total Line Length", f"{total_length:.2f} units")
    else:
        st.write("No measurements available")

# Instructions
with st.expander("📖 How to Use This CAD Tool"):
    st.markdown("""
    **Professional CAD Tool Instructions:**
    
    1. **Select a Tool** from the sidebar
    2. **Enter precise coordinates** in the precision drawing section
    3. **Click 'Add Point at Coordinates'** to place points
    4. **For lines and rectangles**, add two points to create the shape
    5. **View and manage objects** in the Object Manager panel
    6. **Use the grid** for visual reference (toggle in sidebar)
    
    **Tools Available:**
    - **Line**: Create straight lines between two points
    - **Rectangle**: Create rectangles from two opposite corners
    - **Select**: View and delete existing objects
    """)

# Footer
st.divider()
st.caption("Space Forge CAD Tool v2.0 • Precision Engineering for Amazon FC Space Management")
