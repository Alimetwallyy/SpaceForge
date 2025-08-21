import streamlit as st
from streamlit_drawable_canvas import st_canvas
import json
import os
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import shapely.geometry as sg
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as rl_canvas
import io
from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# DB Setup (local)
DATABASE_URL = "postgresql://postgres:yoursecurepass@localhost:5432/spaceforge"  # Update as needed
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Layout(Base):
    __tablename__ = "layouts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    data = Column(JSON)

Base.metadata.create_all(bind=engine)

def get_db():
    return SessionLocal()

# AI Optimization Logic
def optimize_layout(canvas_data):
    objects = canvas_data.get('objects', [])
    points = np.array([[obj['left'], obj['top']] for obj in objects if obj['type'] == 'rect'])
    if len(points) < 2:
        return "Not enough elements to optimize."
    
    kmeans = KMeans(n_clusters=min(2, len(points)))
    kmeans.fit(points)
    centers = kmeans.cluster_centers_
    
    suggestions = []
    total_area = canvas_data['width'] * canvas_data['height']
    used_area = sum(obj['width'] * obj['height'] for obj in objects if obj['type'] == 'rect')
    utilization = (used_area / total_area) * 100 if total_area > 0 else 0
    
    for i, obj in enumerate(objects):
        if obj['type'] == 'rect':
            rect = sg.box(obj['left'], obj['top'], obj['left'] + obj['width'], obj['top'] + obj['height'])
            if rect.area > 1000:  # Example threshold
                suggestions.append(f"Reduce size of rack {i} for better utilization.")
    
    suggestions.append(f"Current utilization: {utilization:.2f}%. Suggest clustering around {centers}.")
    return suggestions

# Export Utils
def generate_pdf(canvas_data):
    buffer = io.BytesIO()
    c = rl_canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, f"Layout: {st.session_state.get('layout_name', 'Untitled')}")
    for obj in canvas_data.get('objects', []):
        if obj['type'] == 'rect':
            c.rect(obj['left'], obj['top'], obj['width'], obj['height'])
    c.save()
    buffer.seek(0)
    return buffer.read()

def save_file_locally(content, filename):
    os.makedirs("storage", exist_ok=True)
    file_path = os.path.join("storage", filename)
    with open(file_path, "wb") as f:
        f.write(content)
    return file_path

# Streamlit App
st.title("SpaceForge: Custom FC Layout Tool")

# Sidebar for Controls
with st.sidebar:
    st.header("Controls")
    layout_name = st.text_input("Layout Name", "MyFC")
    bg_color = st.color_picker("Canvas Background", "#eee")
    stroke_width = st.slider("Stroke Width", 1, 50, 10)
    stroke_color = st.color_picker("Stroke Color", "#000")
    drawing_mode = st.selectbox("Drawing Mode", ["freedraw", "line", "rect", "circle", "transform"])

# Main Canvas
st.subheader("Draw Your FC Layout (e.g., Racks as Rects)")
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",  # Semi-transparent fill
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=600,
    width=800,
    drawing_mode=drawing_mode,
    key="canvas",
)

if canvas_result.json_data is not None:
    st.session_state['canvas_data'] = canvas_result.json_data
    st.session_state['layout_name'] = layout_name

    # Save to DB
    if st.button("Save Layout"):
        db = get_db()
        db_layout = Layout(name=layout_name, data=canvas_result.json_data)
        db.add(db_layout)
        db.commit()
        db.refresh(db_layout)
        st.success(f"Saved as ID: {db_layout.id}")
        db.close()

    # Optimize
    if st.button("Optimize & Suggest"):
        suggestions = optimize_layout(canvas_result.json_data)
        st.write("AI Suggestions:")
        for sug in suggestions:
            st.write(f"- {sug}")

    # Exports
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Export PDF"):
            pdf_bytes = generate_pdf(canvas_result.json_data)
            file_path = save_file_locally(pdf_bytes, "layout.pdf")
            st.success(f"PDF saved at: {file_path}")
            st.download_button("Download PDF", pdf_bytes, "layout.pdf")
    with col2:
        if st.button("Export JSON"):
            json_data = json.dumps(canvas_result.json_data, indent=4).encode()
            file_path = save_file_locally(json_data, "layout.json")
            st.success(f"JSON saved at: {file_path}")
            st.download_button("Download JSON", json_data, "layout.json")

# Load Existing Layout (Example)
layout_id = st.number_input("Load Layout ID", min_value=1)
if st.button("Load"):
    db = get_db()
    layout = db.query(Layout).filter(Layout.id == layout_id).first()
    if layout:
        st.session_state['canvas_data'] = layout.data  # Note: Reload canvas manually or refresh page
        st.success(f"Loaded {layout.name}. Refresh canvas to see changes.")
    else:
        st.error("Not found.")
    db.close()

# BI Dashboard Example
st.subheader("Quick Metrics")
if 'canvas_data' in st.session_state:
    df = pd.DataFrame(st.session_state['canvas_data']['objects'])
    st.dataframe(df)  # Show object data
    st.bar_chart(df['type'].value_counts() if 'type' in df else None)  # Example chart
