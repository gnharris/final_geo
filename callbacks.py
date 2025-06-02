# callbacks.py
import io
import json
import geopandas as gpd
import pandas as pd
import base64
from dash import Input, Output, State, html, dcc, dash_table
import plotly.express as px

def register_callbacks(app):

    @app.callback(
        Output("stored-gdf", "data"),
        Input("upload-geojson", "contents"),
        State("upload-geojson", "filename")
    )
    def handle_upload(contents, filename):
        if contents is None:
            return None
        content_type, content_string = contents.split(',')
        decoded = io.BytesIO(base64.b64decode(content_string))
        gdf = gpd.read_file(decoded)

        gdf["__id__"] = gdf.index.astype(str)
        gdf["is_valid"] = gdf["geometry"].is_valid

        # Detect duplicates robustly using equality
        duplicate_flags = [False] * len(gdf)
        for i, geom_i in enumerate(gdf.geometry):
            for j in range(i + 1, len(gdf)):
                if geom_i.equals(gdf.geometry.iloc[j]):
                    duplicate_flags[j] = True
        gdf["is_duplicate"] = duplicate_flags

        return gdf.to_json()

    @app.callback(
        Output("tab-content-container", "children"),
        Input("tabs", "value"),
        Input("stored-gdf", "data")
    )
    def render_tabs(active_tab, geojson_data):
        if geojson_data is None:
            return html.Div("Please upload a GeoJSON file.")

        gdf = gpd.read_file(io.StringIO(geojson_data))
        gdf["__id__"] = gdf.index.astype(str)

        table = dash_table.DataTable(
            id="geojson-table",
            columns=[{"name": col, "id": col} for col in gdf.columns if col != "geometry"],
            data=gdf.drop(columns="geometry").to_dict("records"),
            page_size=10,
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left"},
        )

        dropdown = dcc.Dropdown(
            id="feature-dropdown",
            options=[{"label": f"Feature {i}", "value": str(i)} for i in gdf.index],
            placeholder="Select feature to highlight",
        )

        map_fig = build_map_figure(None, geojson_data)

        map_layout = html.Div([
            html.P("Select feature to highlight:"),
            dropdown,
            dcc.Graph(id="map-view", figure=map_fig)
        ])

        return html.Div([
            html.Div(table, style={"display": "block" if active_tab == "table" else "none"}),
            html.Div(map_layout, style={"display": "block" if active_tab == "map" else "none"})
        ])

    @app.callback(
        Output("map-view", "figure"),
        Input("feature-dropdown", "value"),
        State("stored-gdf", "data")
    )
    def update_map(selected_id, geojson_data):
        return build_map_figure(selected_id, geojson_data)


def build_map_figure(selected_id, geojson_data):
    gdf = gpd.read_file(io.StringIO(geojson_data))
    gdf["__id__"] = gdf.index.astype(str)

    center = {
        "lat": gdf.geometry.centroid.y.mean(),
        "lon": gdf.geometry.centroid.x.mean()
    }

    fig = px.choropleth_mapbox(
        gdf,
        geojson=json.loads(gdf.to_json()),
        locations="__id__",
        color=gdf["is_duplicate"].astype(str),
        mapbox_style="open-street-map",
        center=center,
        zoom=10,
        opacity=0.4
    )

    if selected_id:
        sel_geom = gdf.loc[int(selected_id), "geometry"]
        sel_gdf = gpd.GeoDataFrame(geometry=[sel_geom], crs=gdf.crs)
        sel_geojson = json.loads(sel_gdf.to_json())

        fig.add_trace({
            "type": "scattermapbox",
            "lat": [sel_geom.centroid.y],
            "lon": [sel_geom.centroid.x],
            "mode": "markers",
            "marker": {"size": 1, "color": "red"},
            "hoverinfo": "none",
        })

        fig.update_layout(
            mapbox=dict(
                center={"lat": sel_geom.centroid.y, "lon": sel_geom.centroid.x},
                zoom=16,
                layers=[{
                    "source": sel_geojson,
                    "type": "line",
                    "color": "red",
                    "line": {"width": 3}
                }]
            )
        )

    return fig
