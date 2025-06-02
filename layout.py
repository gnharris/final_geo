# layout.py
from dash import html, dcc
import dash_bootstrap_components as dbc

def create_layout():
    return html.Div([
        html.H1("Farm GeoJSON Dashboard", style={
            "textAlign": "center",
            "marginTop": "20px",
            "marginBottom": "10px",
            "color": "#2c3e50"
        }),

        html.Div([
            dcc.Upload(
                id="upload-geojson",
                children=html.Div(["\ud83d\udcc1 Click or drag to upload a GeoJSON file"]),
                multiple=False,
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "2px",
                    "borderStyle": "dashed",
                    "borderRadius": "10px",
                    "textAlign": "center",
                    "margin": "auto",
                    "color": "#3498db",
                    "fontWeight": "bold",
                    "cursor": "pointer"
                }
            )
        ], style={"width": "60%", "margin": "auto", "marginBottom": "20px"}),

        dcc.Tabs(id="tabs", value="table", children=[
            dcc.Tab(label="\ud83d\udccb Table View", value="table", style={"padding": "10px"}),
            dcc.Tab(label="\ud83d\uddd8\ufe0f Map View", value="map", style={"padding": "10px"}),
        ], style={"margin": "auto", "width": "80%"}),

        html.Div(id="tab-content-container", style={"padding": "20px"}),

        dcc.Store(id="stored-gdf")
    ], style={"fontFamily": "Arial, sans-serif", "maxWidth": "1200px", "margin": "auto"})
