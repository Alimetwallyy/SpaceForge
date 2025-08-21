import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder

# Page Configuration
st.set_page_config(page_title="Space Forge", layout="wide")
st.title("🚀 Space Forge: FC Layout Configurator")

# Initialize Session State for our layout data
if 'df_layout' not in st.session_state:
    # Create a simple 10x10 grid to represent an FC floor plan
    # Each cell will have a 'type' (Empty, Rack, Aisle, Wall)
    data = [['Empty' for _ in range(10)] for _ in range(10)]
    st.session_state.df_layout = pd.DataFrame(data)

# Function to handle cell edits from AgGrid
def update_cell(change):
    row, col, new_value = change['row'], change['col'], change['new']
    st.session_state.df_layout.iat[row, col] = new_value

# Create the main interface
tab1, tab2 = st.tabs(["📊 Grid Editor", "🎨 Visual Viewer"])

with tab1:
    st.header("Edit FC Layout Grid")
    st.caption("Click on a cell to edit its type. This represents your AutoCAD logic layer.")

    # Configure AgGrid for editing
    gb = GridOptionsBuilder.from_dataframe(st.session_state.df_layout)
    gb.configure_default_column(editable=True, resizable=True)
    gb.configure_grid_options(onCellValueChanged=update_cell)
    grid_options = gb.build()

    # Display the editable grid
    grid_response = AgGrid(
        st.session_state.df_layout,
        gridOptions=grid_options,
        height=400,
        theme='streamlit',
        fit_columns=True,
        allow_unsafe_jupyter_html=True,
        key='grid_editor'
    )
    # Update session state if any changes were made
    st.session_state.df_layout = grid_response['data']

with tab2:
    st.header("Visual Layout Viewer")
    st.caption("This is a heatmap visualization of your grid. This will evolve into a true CAD view.")

    # Create a numerical representation for the heatmap
    type_mapping = {'Empty': 0, 'Rack': 1, 'Aisle': 2, 'Wall': 3}
    df_numeric = st.session_state.df_layout.replace(type_mapping)

    # Create an interactive heatmap with Plotly
    fig = px.imshow(
        df_numeric,
        labels=dict(x="Column", y="Row", color="Zone Type"),
        color_continuous_scale='Viridis',
        aspect='auto'
    )
    fig.update_xaxes(side="top")
    st.plotly_chart(fig, use_container_width=True)

# Sidebar for utilities
with st.sidebar:
    st.header("Controls")
    if st.button("Reset Grid to Empty"):
        st.session_state.df_layout = pd.DataFrame([['Empty' for _ in range(10)] for _ in range(10)])
        st.rerun()

    st.download_button(
        label="Download Layout (CSV)",
        data=st.session_state.df_layout.to_csv(index=False).encode('utf-8'),
        file_name='fc_layout.csv',
        mime='text/csv',
    )

    uploaded_file = st.file_uploader("Upload a Layout CSV", type=['csv'])
    if uploaded_file is not None:
        try:
            st.session_state.df_layout = pd.read_csv(uploaded_file)
            st.rerun()
        except Exception as e:
            st.error(f"Error uploading file: {e}")
