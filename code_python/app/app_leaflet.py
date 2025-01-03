import dash
import dash_leaflet as dl
from dash import html, Output, Input

app = dash.Dash(__name__)

app.layout = html.Div([
    dl.Map(
        center=[39.5, -117],
        zoom=6,
        style={'width': '50vw', 'height': '60vh'},
        children=[dl.TileLayer()],
        id="map"
    ),
    html.Div(id="click-debug", style={"marginTop": "20px"})
])

@app.callback(
    Output("click-debug", "children"),
    Input("map", "click_lat_lng")
)
def debug_user_click(click_lat_lng):
    print("Callback triggered with:", click_lat_lng)  # <--- added
    if click_lat_lng is None:
        return "Click the map to see lat/lon"
    lat, lon = click_lat_lng
    return f"You clicked: lat={click_lat_lng}"

if __name__ == "__main__":
    app.run_server(debug=True)
