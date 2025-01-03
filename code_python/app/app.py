import os
import dash
import dash_leaflet as dl
from dash import dcc, html, Input, Output, State, callback_context
import plotnine as p9
import pandas as pd
import base64
import ee
import datetime

####################
# 1) INITIAL SETUP
####################
ee.Initialize(project="dri-apps")

# We'll store user-clicked coords in a Dash "Store" (JSON),
# so we can reference them in callbacks.
# The local folder for saving plots (and then reading them back).
OUTPUT_DIR = "../outputs/python/"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

####################
# 2) BUILD DASH APP
####################
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H2("Dash + dash_leaflet + Earth Engine + plotnine"),

    # A) A dash_leaflet map for user clicks
    dl.Map(
        center=[39.5, -117],
        zoom=6,
        style={'width': '50vw', 'height': '60vh'},
        children=[
            dl.TileLayer(),
        ],
        id="map",
    ),

    # A hidden dcc.Store to remember the last clicked lat-lon
    dcc.Store(id="store_latlon", data=None),

    html.Br(),

    # B) UI for selecting rooting depth
    html.Label("Select Rooting Depth (m)"),
    dcc.Dropdown(
        id="dropdown_rd",
        options=[
            {"label": "0.5 m", "value": 0.5},
            {"label": "2.0 m", "value": 2.0},
            {"label": "3.6 m", "value": 3.6},
        ],
        value=0.5,  # default
        clearable=False,
        style={"width": "200px"}
    ),

    html.Br(),

    # C) Text input for soil override
    html.Label("Override Soil Type (optional)"),
    dcc.Input(
        id="input_soil_override",
        type="text",
        placeholder="e.g., 'clay', 'loamysand'...",
        style={"width": "200px"}
    ),

    html.Br(), html.Br(),

    # D) Button to trigger data fetch & plot generation
    html.Button("Compute & Generate Plots", id="btn_compute"),

    html.Br(), html.Br(),

    # E) Output images for each plot. We'll show them as <img> tags.
    #    We'll produce 6 figures total:
    #    1) LAI timeseries, 2) LAI boxplot
    #    3) AET timeseries, 4) AET boxplot
    #    5) GWSubs timeseries, 6) GWSubs boxplot
    html.Div([
        html.H4("LAI Timeseries"),
        html.Img(id="plot_lai1"),
        html.Br(),
        html.H4("LAI Boxplot"),
        html.Img(id="plot_lai2"),

        html.Br(),
        html.H4("AET Timeseries"),
        html.Img(id="plot_aet1"),
        html.Br(),
        html.H4("AET Boxplot"),
        html.Img(id="plot_aet2"),

        html.Br(),
        html.H4("Groundwater Subsidy Timeseries"),
        html.Img(id="plot_gwsubs1"),
        html.Br(),
        html.H4("Groundwater Subsidy Boxplot"),
        html.Img(id="plot_gwsubs2"),
    ])
])

##############################
# 3) DASH CALLBACKS & LOGIC
##############################

# A) Capture user clicks on the dash_leaflet map
@app.callback(
    Output("store_latlon", "data"),
    [Input("map", "click_lat_lng")],
    prevent_initial_call=True
)
def capture_map_click(click_lat_lng):
    """Stores the [lat, lng] in dcc.Store."""
    if click_lat_lng is None:
        return None
    # click_lat_lng is [lat, lng]
    print(f"User clicked at: {click_lat_lng}")
    return {"lat": click_lat_lng[0], "lon": click_lat_lng[1]}


# B) Main compute callback
@app.callback(
    [
        Output("plot_lai1", "src"),
        Output("plot_lai2", "src"),
        Output("plot_aet1", "src"),
        Output("plot_aet2", "src"),
        Output("plot_gwsubs1", "src"),
        Output("plot_gwsubs2", "src"),
    ],
    [
        Input("btn_compute", "n_clicks"),
    ],
    [
        State("store_latlon", "data"),
        State("dropdown_rd", "value"),
        State("input_soil_override", "value"),
    ],
    prevent_initial_call=True
)
def run_ee_and_generate_plots(n_clicks, store_latlon, rd_val, soil_override):
    """
    When user clicks "Compute & Generate Plots", read lat/lon from store,
    read rd_val, soil_override, then run Earth Engine, build data frames,
    create plotnine figures, and save them to disk. 
    Return base64-embedded <img> content for each figure.
    """
    if (not store_latlon) or (store_latlon["lat"] is None):
        # No map click yet
        return [None]*6

    lat = store_latlon["lat"]
    lon = store_latlon["lon"]

    ############################
    # 1) EARTH ENGINE LOOKUPS
    ############################
    coords_ee = ee.Geometry.Point([lon, lat])

    # Soil image
    soil = ee.Image('projects/sat-io/open-datasets/CSRL_soil_properties/physical/soil_texture_profile/texture_2550').rename('texture')
    soil_lu_dict = ee.Dictionary({
        "1": "sand",
        "2": "loamysand",
        "3": "sandyloam",
        "4": "loam",
        "5": "siltloam",
        "6": "silt",
        "7": "sandyclayloam",
        "8": "clayloam",
        "9": "siltyclayloam",
        "10": "sandyclay",
        "11": "siltyclay",
        "12": "clay"
    })

    soil_point = soil.reduceRegion(
        reducer=ee.Reducer.mean(), 
        geometry=coords_ee, 
        scale=30
    ).get('texture')

    if soil_point is not None:
        numeric_soil_val = ee.Number(soil_point).format('%.0f').getInfo()
        auto_soil_string = soil_lu_dict.get(numeric_soil_val).getInfo()
    else:
        auto_soil_string = "loam"  # fallback if no data

    # If user typed a soil override, use it
    if soil_override and soil_override.strip():
        st = soil_override.strip()
    else:
        st = auto_soil_string

    # Water years
    year_start = 1991
    year_end = 2023
    year_list = ee.List.sequence(year_start, year_end)

    gm = ee.ImageCollection('IDAHO_EPSCOR/GRIDMET').select(['pr', 'eto'])

    def calculate_wy_stats(year):
        date_start = ee.Date.fromYMD(ee.Number(year).subtract(1), 10, 1)
        date_end = ee.Date.fromYMD(ee.Number(year), 10, 1)  # exclusive
        return (gm.filterDate(date_start, date_end).sum()
                .set({
                    'system:time_start': date_start.millis(),
                    'year': ee.Number(year),
                    'system:index': ee.Number(year).format('%.0f')
                }))

    gm_wy = ee.ImageCollection(year_list.map(calculate_wy_stats))

    def calculate_wb(image):
        image_ws = image.select('pr').subtract(image.select('eto')).rename('wb')
        image_ws = image_ws.divide(100)
        return image.addBands(image_ws)

    gm_wy = gm_wy.map(calculate_wb).toBands()

    gm_point = gm_wy.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=coords_ee,
        scale=4000
    ).getInfo()

    if not gm_point:
        # If no climate data is returned, bail
        return [None]*6

    parsed_data = []
    for key, value in gm_point.items():
        year, suffix = key.split('_')
        parsed_data.append({'wy': int(year), suffix: value})

    dfee = pd.DataFrame(parsed_data)
    dfee = dfee.groupby('wy').first().reset_index()

    dfee['wb2'] = dfee['wb']**2
    dfee['wb3'] = dfee['wb']**3
    dfclimate = dfee.copy()

    ########################################
    # 2) MERGE WITH MODEL COEFFICIENTS
    ########################################
    dfcoeffs = pd.read_csv('../data/MixedEffectsModelCoefficients102924_LAI_AET_AETG_GWsubs.csv')
    dfcoeffs['wtd2'] = dfcoeffs['WTD'].apply(lambda x: "Free Drain" if x == 12 else f"{x} m")

    # Filter by rd_val & soil type
    dfcoeffs = dfcoeffs[dfcoeffs['rootdepth'] == rd_val]
    dfcoeffs = dfcoeffs[dfcoeffs['soiltype'] == st]

    # Expand dfclimate with WTD [1,3,6,12]
    wtd_values = [1, 3, 6, 12]
    dfclimate = pd.concat(
        [dfclimate.assign(WTD=w) for w in wtd_values],
        ignore_index=True
    )

    dfsum = pd.merge(dfclimate, dfcoeffs, on='WTD', how='left')

    # Compute LAI, AET, etc.
    dfsum['LAIcalc'] = (
        dfsum['LAIIntercept'] +
        dfsum['wb'] * dfsum['LAIwbx'] +
        dfsum['wb2'] * dfsum['LAIwb2x'] +
        dfsum['wb3'] * dfsum['LAIwb3x']
    )
    dfsum['aetcalc'] = (
        dfsum['aetIntercept'] +
        dfsum['wb'] * dfsum['aetwbx'] +
        dfsum['wb2'] * dfsum['aetwb2x'] +
        dfsum['wb3'] * dfsum['aetwb3x']
    )
    dfsum['aetgwcalc'] = (
        dfsum['aetgwIntercept'] +
        dfsum['wb'] * dfsum['aetgwwbx'] +
        dfsum['wb2'] * dfsum['aetgwwb2x'] +
        dfsum['wb3'] * dfsum['aetgwwb3x']
    )
    dfsum['gwsubscalc'] = (
        dfsum['gwsubsIntercept'] +
        dfsum['wb'] * dfsum['gwsubswbx'] +
        dfsum['wb2'] * dfsum['gwsubswb2x'] +
        dfsum['wb3'] * dfsum['gwsubswb3x']
    )

    # LAI threshold logic
    if rd_val == 0.5:
        laithresh = 1.5
    elif rd_val == 2:
        laithresh = 2
    elif rd_val == 3.6:
        laithresh = 1
    else:
        laithresh = 1.5

    # Summaries for LAI
    # We'll build "lai2" after counting rows >= laithresh
    filtered_lai = dfsum[dfsum["LAIcalc"] >= laithresh]
    laisum = (filtered_lai.groupby(dfsum["WTD"]).size()
              .reset_index(name="noverthresh"))
    laisum["wtd2"] = laisum["WTD"].apply(lambda x: "Free Drain" if x == 12 else f"{x} m")
    dfsum["wtd2"] = dfsum["WTD"].apply(lambda x: "Free Drain" if x == 12 else f"{x} m")
    lai2 = pd.merge(dfsum, laisum, on="WTD", how="left")
    lai2["noverthresh"] = lai2["noverthresh"].fillna(0)
    total_years = len(dfsum["wy"].unique())
    lai2["percoverthresh"] = (lai2["noverthresh"] / total_years * 100).round(1)

    # Build Figures
    # We'll save them to OUTPUT_DIR as PNG, then base64-encode them for display in the app.

    fig_paths = {
        "p_lai1": os.path.join(OUTPUT_DIR, f"{st}_{rd_val}_rootdepth_timeseries_LAI.png"),
        "p_lai2": os.path.join(OUTPUT_DIR, f"{st}_{rd_val}_rootdepth_boxplot_LAI.png"),
        "p_aet1": os.path.join(OUTPUT_DIR, f"{st}_{rd_val}_rootdepth_timeseries_totalET.png"),
        "p_aet2": os.path.join(OUTPUT_DIR, f"{st}_{rd_val}_rootdepth_boxplot_totalET.png"),
        "p_gwsubs1": os.path.join(OUTPUT_DIR, f"{st}_{rd_val}_rootdepth_timeseries_GWsubsET.png"),
        "p_gwsubs2": os.path.join(OUTPUT_DIR, f"{st}_{rd_val}_rootdepth_boxplot_GWsubsET.png"),
    }

    # --- LAI timeseries
    p_lai1 = (
        p9.ggplot(lai2)
        + p9.geom_line(p9.aes('wy', 'LAIcalc', linetype='wtd2'))
        + p9.geom_point(p9.aes('wy', 'LAIcalc', color='wb * 100'))
        + p9.geom_hline(yintercept=laithresh, alpha=0.5)
        + p9.theme_bw()
        + p9.scale_color_distiller(palette="YlGnBu", direction=1)
        + p9.ggtitle(f"LAI Time Series\nRoot Depth: {rd_val}m, Soil Type: {st}")
        + p9.labs(
            x="Water Year",
            y="Annual Max LAI",
            color="Deficit (mm)",
            linetype="Water Table Depth"
        )
    )
    p_lai1.save(fig_paths["p_lai1"], height=4, width=6, dpi=300)

    # --- LAI boxplot
    p_lai2 = (
        p9.ggplot(lai2)
        + p9.geom_boxplot(p9.aes('wtd2', 'LAIcalc'))
        + p9.geom_point(p9.aes('wtd2', 'LAIcalc', color='wb * 100'))
        + p9.geom_hline(yintercept=laithresh, alpha=0.5)
        + p9.theme_bw()
        + p9.scale_color_distiller(palette="YlGnBu", direction=1)
        + p9.ggtitle(f"LAI Boxplot\nRoot Depth: {rd_val}m, Soil Type: {st}")
        + p9.labs(
            x="Water Table Depth",
            y="Annual Max LAI",
            color="Deficit (mm)"
        )
    )
    p_lai2.save(fig_paths["p_lai2"], height=4, width=6, dpi=300)

    # --- AET timeseries
    aetsum = (dfsum.groupby("wtd2")
              .agg(min=("aetcalc", "min"), max=("aetcalc", "max"))
              .reset_index())
    aet2 = pd.merge(dfsum, aetsum, on="wtd2", how="left")
    aet2["min"] = aet2["min"].round(0)
    aet2["max"] = aet2["max"].round(0)

    p_aet1 = (
        p9.ggplot(aet2)
        + p9.geom_line(p9.aes('wy', 'aetcalc', linetype='wtd2'))
        + p9.geom_point(p9.aes('wy', 'aetcalc', color='wb * 100'))
        + p9.theme_bw()
        + p9.scale_color_distiller(palette="YlGnBu", direction=1)
        + p9.ggtitle(f"AET Time Series\nRoot Depth: {rd_val}m, Soil Type: {st}")
        + p9.labs(
            x="Water Year",
            y="Annual AET (mm)",
            color="Deficit (mm)",
            linetype="Water Table Depth"
        )
    )
    p_aet1.save(fig_paths["p_aet1"], height=4, width=6, dpi=300)

    # --- AET boxplot
    p_aet2 = (
        p9.ggplot(aet2)
        + p9.geom_boxplot(p9.aes('wtd2', 'aetcalc'))
        + p9.geom_point(p9.aes('wtd2', 'aetcalc', color='wb * 100'))
        + p9.theme_bw()
        + p9.scale_color_distiller(palette="YlGnBu", direction=1)
        + p9.ggtitle(f"AET Boxplot\nRoot Depth: {rd_val}m, Soil Type: {st}")
        + p9.labs(
            x="Water Table Depth",
            y="Annual AET (mm)",
            color="Deficit (mm)"
        )
    )
    p_aet2.save(fig_paths["p_aet2"], height=4, width=6, dpi=300)

    # --- GWSubs timeseries
    gwsubs = dfsum[dfsum["wtd2"] != "Free Drain"].copy()
    gwsubs["ratio"] = gwsubs["gwsubscalc"] / gwsubs["aetcalc"]
    gwsubssum = (
        gwsubs.groupby("wtd2")
        .agg(
            min=("gwsubscalc", "min"),
            max=("gwsubscalc", "max"),
            minperc=("ratio", "min"),
            maxperc=("ratio", "max"),
        )
        .reset_index()
    )
    gwsubs2 = pd.merge(gwsubs, gwsubssum, on="wtd2", how="left")
    gwsubs2["min"] = gwsubs2["min"].round(0)
    gwsubs2["max"] = gwsubs2["max"].round(0)

    p_gwsubs1 = (
        p9.ggplot(gwsubs2)
        + p9.geom_line(p9.aes('wy', 'gwsubscalc', linetype='wtd2'))
        + p9.geom_point(p9.aes('wy', 'gwsubscalc', color='gwsubscalc'))
        + p9.theme_bw()
        + p9.scale_color_distiller(palette="YlGnBu", direction=1)
        + p9.ggtitle(f"GW Subsidy Time Series\nRoot Depth: {rd_val}m, Soil Type: {st}")
        + p9.labs(
            x="Water Year",
            y="GW Subsidy (mm)",
            color="GW Subsidy (mm)",
            linetype="Water Table Depth"
        )
    )
    p_gwsubs1.save(fig_paths["p_gwsubs1"], height=4, width=6, dpi=300)

    # --- GWSubs boxplot
    p_gwsubs2 = (
        p9.ggplot(gwsubs2)
        + p9.geom_boxplot(p9.aes('wtd2', 'gwsubscalc'))
        + p9.geom_point(p9.aes('wtd2', 'gwsubscalc', color='gwsubscalc'))
        + p9.theme_bw()
        + p9.scale_color_distiller(palette="YlGnBu", direction=1)
        + p9.ggtitle(f"GW Subsidy Boxplot\nRoot Depth: {rd_val}m, Soil Type: {st}")
        + p9.labs(
            x="Water Table Depth",
            y="GW Subsidy (mm)",
            color="GW Subsidy (mm)",
        )
    )
    p_gwsubs2.save(fig_paths["p_gwsubs2"], height=4, width=6, dpi=300)

    # Convert each plot to base64 string
    def fig_to_base64(path):
        if not os.path.exists(path):
            return None
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/png;base64,{b64}"

    return [
        fig_to_base64(fig_paths["p_lai1"]),
        fig_to_base64(fig_paths["p_lai2"]),
        fig_to_base64(fig_paths["p_aet1"]),
        fig_to_base64(fig_paths["p_aet2"]),
        fig_to_base64(fig_paths["p_gwsubs1"]),
        fig_to_base64(fig_paths["p_gwsubs2"]),
    ]


##############################
# 4) RUN THE APP
##############################
if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
