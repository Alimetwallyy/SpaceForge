import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Space Forge: CAD", layout="wide")
st.title("🛠️ Space Forge: CAD Canvas")

# Initialize all session state variables
if 'shapes' not in st.session_state:
    st.session_state.shapes = []  # Stores all drawn shapes as plotly shapes
if 'current_shape' not in st.session_state:
    st.session_state.current_shape = 'circle'  # Default shape
if 'current_color' not in st.session_state:
    st.session_state.current_color = 'Blue'  # Default color
if 'canvas_size' not in st.session_state:
    st.session_state.canvas_size = 1000  # Default canvas size (1000x1000 meters)
if 'bg_color' not in st.session_state:
    st.session_state.bg_color = 'White'  # Default background

# Function to add a new shape to the canvas
def add_shape_to_canvas(click_data):
    if click_data is None:
        return
        
    # Get the x and y coordinates of the click
    x = click_data['points'][0]['x']
    y = click_data['points'][0]['y']
    
    # Define properties for the new shape based on user selection
    new_shape = {
        'type': st.session_state.current_shape,
        'color': st.session_state.current_color,
        'x': x,
        'y': y,
        'size': 50  # Default size for shapes
    }
    # Add the new shape to the list
    st.session_state.shapes.append(new_shape)

# Function to clear all shapes
def clear_canvas():
    st.session_state.shapes = []

# Create the main interface
col1, col2 = st.columns([1, 3])

with col1:
    st.header("Controls")
    
    # Canvas Settings
    st.subheader("Canvas Settings")
    st.session_state.canvas_size = st.number_input("Canvas Size (meters)", min_value=100, value=1000, step=100)
    st.session_state.bg_color = st.selectbox("Background Color", ("White", "Black"))
    
    # Drawing Tools
    st.subheader("Drawing Tools")
    st.session_state.current_shape = st.selectbox("Select Shape", ("circle", "rect", "triangle-up", "diamond", "pentagon", "hexagon"))
    st.session_state.current_color = st.selectbox("Select Color", ("Red", "Blue", "Green", "Yellow", "Black", "White", "Orange", "Purple"))
    
    # Add a button to clear the canvas
    if st.button("Clear Canvas", type="primary"):
        clear_canvas()
        st.rerun()

    st.info("Click on the canvas to place the selected shape.")

with col2:
    st.header("Design Canvas")
    
    # Create the base figure (the empty canvas)
    fig = go.Figure()
    
    # Set up the canvas layout based on user settings
    axis_config = dict(
        showgrid=True,
        gridcolor="lightgray",
        zeroline=False,
        range=[0, st.session_state.canvas_size]  # Dynamic axis range
    )
    
    fig.update_layout(
        width=700,
        height=700,
        xaxis=axis_config,
        yaxis=axis_config,
        plot_bgcolor=st.session_state.bg_color.lower(),  # Set background color
        paper_bgcolor='#0E1117',  # Matches Streamlit dark sidebar
        title=f"Space Canvas ({st.session_state.canvas_size}m x {st.session_state.canvas_size}m)"
    )
    
    # Plot all existing shapes from session state
    for shape in st.session_state.shapes:
        fig.add_trace(go.Scatter(
            x=[shape['x']],
            y=[shape['y']],
            mode='markers',
            marker=dict(
                symbol=shape['type'],
                size=shape['size'],
                color=shape['color']
            ),
            name=f"{shape['type']}-{shape['color']}"
        ))
    
    # Make the figure interactive and handle clicks
    click_data = st.plotly_chart(
        fig,
        use_container_width=True,
        key="main_canvas",
        on_select="rerun"  # This captures the click event
    )
    
    # If the user clicked on the canvas, add a new shape
    if click_data.selection:
        add_shape_to_canvas(click_data.selection)
        st.rerun()  # Rerun to redraw the canvas with the new shape

# Display current drawing info in the sidebar
with st.sidebar:
    st.header("Current Drawing")
    st.write(f"Shapes on canvas: **{len(st.session_state.shapes)}**")
    if st.session_state.shapes:
        st.download_button(
            label="Export Drawing Data (CSV)",
            data=pd.DataFrame(st.session_state.shapes).to_csv(index=False).encode('utf-8'),
            file_name='fc_layout_drawing.csv',
            mime='text/csv',
        )
