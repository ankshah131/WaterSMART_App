import streamlit as st
import ee
import folium
import matplotlib.pyplot as plt
import pandas as pd
import base64
import io
from matplotlib.backends.backend_pdf import PdfPages

from plotnine import *
import matplotlib.pyplot as plt
from streamlit_folium import st_folium
from google.oauth2 import service_account
from ee import oauth
from io import BytesIO
from io import StringIO
from PIL import Image

# Earth Engine Setup
def get_auth():
    service_account_keys = st.secrets["GEE_CREDS"]['settings']
    credentials = service_account.Credentials.from_service_account_info(
        service_account_keys,
        scopes=oauth.SCOPES
    )
    ee.Initialize(credentials)
    success = 'Successfully synced to GEE!'
    return success


get_auth()

# Set up Streamlit layout
st.set_page_config(page_title="Nevada GDE Water Needs Explorer", layout="wide")
st.title("Welcome to the Nevada GDE Water Needs Explorer")

# App description
st.write("""
Groundwater-dependent ecosystems (GDEs) in Nevada play a critical role in sustaining biodiversity and supporting ecological balance.
These systems rely on stable water levels, making them particularly vulnerable to changes in groundwater availability caused by climate variability and human activities.

This tool allows users to explore the water needs of GDEs in Nevada, assess soil types, and understand the relationship between water availability, rooting depths, and evapotranspiration.
Select your area of interest on the map to gain insights and make data-informed decisions to support the sustainable management of these vital ecosystems.

Use the control panel on the left to get started to select your area of interest and to pull climate and soils data for this location. Once you have selected your location, click “Get Data”.
""")

st.sidebar.header("Control Panel")
st.sidebar.write("Select your area of interest by clicking on the map below:")

# Initialize a Folium map with a proper basemap
default_coords = [39.5, -117]
coords_ee = ee.Geometry.Point(default_coords)
# folium_map = folium.Map(location=default_coords, zoom_start=7, tiles="cartodbpositron")

# # Add a marker to the map
# folium.Marker(location=default_coords, popup="Default Location").add_to(folium_map)

# Embed the map in the sidebar
with st.sidebar:
    st.write("### Interactive Map")
    map_data = st_folium(folium_map, width=300, height=500)

# Check for selected coordinates from the map
if map_data is not None and "last_clicked" in map_data and map_data["last_clicked"] is not None:
    lat, lon = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]
    coords_ee = ee.Geometry.Point([lon, lat])
    st.sidebar.write(f"**Selected Coordinates:** ({lat:.4f}, {lon:.4f})")
else:
    st.sidebar.warning("No point selected on the map yet.")


# Add a "Get Data" button
get_data_btn = st.sidebar.button("Get Data!")

# Add an image to the main panel
# image_path = "/content/nature_conservancy_logo.jpeg"  # Replace with the path to your image file
# st.image(image_path)


# Execute upon clicking "Get Data"
if get_data_btn is not None: #and coords_ee is not None:
    st.empty()

    # Soil type determination
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

    # Extract soil texture for the point
    soil_point = soil.reduceRegion(reducer=ee.Reducer.mean(), geometry=coords_ee, scale=30).get('texture')
    soil_string = soil_lu_dict.get(ee.Number(soil_point).format('%.0f')).getInfo()

    # Water balance calculation
    year_start = 1991
    year_end = 2021
    year_list = ee.List.sequence(year_start, year_end)

    gm = ee.ImageCollection('IDAHO_EPSCOR/GRIDMET').select(['pr', 'eto'])

    def calculate_wy_stats(year):
        date_start = ee.Date.fromYMD(ee.Number(year).subtract(1), 10, 1)
        date_end = ee.Date.fromYMD(ee.Number(year), 10, 1)
        return ee.Image(gm.filterDate(date_start, date_end).sum()).set({
            'system:time_start': date_start.millis(),
            'year': ee.Number(year),
            'system:index': ee.Number(year).format('%.0f')
        })

    gm_wy = ee.ImageCollection(year_list.map(calculate_wy_stats))

    def calculate_wb(image):
        image_ws = image.select('pr').subtract(image.select('eto')).rename('wb')
        image_ws = image_ws.divide(100)
        return image.addBands(image_ws)

    gm_wy = ee.ImageCollection(gm_wy).map(calculate_wb).toBands()
    gm_point = gm_wy.reduceRegion(reducer=ee.Reducer.mean(), geometry=coords_ee, scale=4000).getInfo()

    # Rooting depth and soil type controls
    # Define allowed values
    allowed_values = [0.5, 2, 3.6]

    # Use select_slider instead of slider to restrict to specific values
    rooting_depth = st.select_slider("Select rooting depth (m):", options=allowed_values, value=0.5)

    st.write(f"Selected Rooting Depth: {rooting_depth} m")

    soil_type = st.selectbox(
        "Select soil type:",
        ["loamysand", "sandyloam", "loam", "siltloam", "silt",
        "sandyclayloam", "clayloam", "siltyclayloam", "sandyclay", "siltyclay", "clay"],
        index=2
    )

    # Mock defined variable to override EE operations
    #gm_point = {'1991_eto': 1258.8973198533058, '1991_pr': 277.44268065690994, '1991_wb': -9.814546391963958, '1992_eto': 1339.4788173437119, '1992_pr': 198.2026747763157, '1992_wb': -11.412761425673962, '1993_eto': 1234.113734871149, '1993_pr': 263.7720437049866, '1993_wb': -9.703416911661625, '1994_eto': 1334.7636932730675, '1994_pr': 213.75563368201256, '1994_wb': -11.210080595910549, '1995_eto': 1166.2698855996132, '1995_pr': 438.0278924703598, '1995_wb': -7.282419931292534, '1996_eto': 1320.879874765873, '1996_pr': 281.16770535707474, '1996_wb': -10.397121694087982, '1997_eto': 1268.3588969111443, '1997_pr': 293.90991020202637, '1997_wb': -9.744489867091179, '1998_eto': 1143.232638180256, '1998_pr': 495.573089748621, '1998_wb': -6.476595484316349, '1999_eto': 1247.8120474815369, '1999_pr': 240.79711747169495, '1999_wb': -10.07014930009842, '2000_eto': 1358.9225591123104, '2000_pr': 234.0520594716072, '2000_wb': -11.248704996407032, '2001_eto': 1343.3759242892265, '2001_pr': 176.1760538816452, '2001_wb': -11.671998704075813, '2002_eto': 1372.3919923007488, '2002_pr': 214.4552606344223, '2002_wb': -11.579367316663266, '2003_eto': 1335.3546098470688, '2003_pr': 254.82380563020706, '2003_wb': -10.805308042168617, '2004_eto': 1366.8700581490993, '2004_pr': 218.14580446481705, '2004_wb': -11.487242536842823, '2005_eto': 1268.5541378259659, '2005_pr': 342.68022459745407, '2005_wb': -9.258739132285118, '2006_eto': 1332.9253282546997, '2006_pr': 336.42576122283936, '2006_wb': -9.964995670318604, '2007_eto': 1381.5141016244888, '2007_pr': 166.56535190343857, '2007_wb': -12.149487497210503, '2008_eto': 1353.2850314378738, '2008_pr': 227.98866021633148, '2008_wb': -11.252963712215424, '2009_eto': 1288.4222103059292, '2009_pr': 292.0265671312809, '2009_wb': -9.963956431746483, '2010_eto': 1257.4372656345367, '2010_pr': 201.6916048824787, '2010_wb': -10.55745660752058, '2011_eto': 1182.088837146759, '2011_pr': 316.8663139939308, '2011_wb': -8.652225231528282, '2012_eto': 1362.4130966365337, '2012_pr': 128.76578524708748, '2012_wb': -12.336473113894463, '2013_eto': 1354.059213846922, '2013_pr': 174.25016695261002, '2013_wb': -11.79809046894312, '2014_eto': 1339.7214939594269, '2014_pr': 222.30873107910156, '2014_wb': -11.174127628803253, '2015_eto': 1329.980028450489, '2015_pr': 254.69928726553917, '2015_wb': -10.7528074118495, '2016_eto': 1332.7939132601023, '2016_pr': 254.1333208680153, '2016_wb': -10.78660592392087, '2017_eto': 1256.099998190999, '2017_pr': 352.6000027656555, '2017_wb': -9.034999954253434, '2018_eto': 1343.899999588728, '2018_pr': 217.80000007152557, '2018_wb': -11.260999995172023, '2019_eto': 1220.5999988168478, '2019_pr': 375.0000013113022, '2019_wb': -8.455999975055455, '2020_eto': 1367.500000834465, '2020_pr': 155.99999940395355, '2020_wb': -12.115000014305116, '2021_eto': 1377.2000001370907, '2021_pr': 163.29999896883965, '2021_wb': -12.13900001168251, '2022_eto': 1293.899999603629, '2022_pr': 193.7999995648861, '2022_wb': -11.00100000038743, '2023_eto': 1219.5999989509583, '2023_pr': 355.3999990224838, '2023_wb': -8.641999999284744}

    # Parse the dictionary into a DataFrame
    parsed_data = []
    for key, value in gm_point.items():
        year, suffix = key.split('_')
        parsed_data.append({'wy': int(year), suffix: value})

    # Combine the parsed data into a DataFrame
    dfee = pd.DataFrame(parsed_data)
    dfee = dfee.groupby('wy').first().reset_index()

    # Calculate annual water balance variables
    dfee['wb2'] = dfee['wb'] ** 2  # Square of 'wb'
    dfee['wb3'] = dfee['wb'] ** 3  # Cube of 'wb'

    # Rename dfee as dfclimate
    dfclimate = dfee

    # Load the dataset
    #dfcoeffs = pd.read_csv('/content/MixedEffectsModelCoefficients102924_LAI_AET_AETG_GWsubs.csv')
    dfcoeffs = pd.read_csv('https://raw.githubusercontent.com/ankshah131/WaterSMART_App/main/streamlit_app/MixedEffectsModelCoefficients102924_LAI_AET_AETG_GWsubs.csv')
    dfcoeffs['wtd2'] = dfcoeffs['WTD'].apply(lambda x: "Free Drain" if x == 12 else f"{x} m")
    # print(dfcoeffs)

    # Define rooting depth and soil type
    # These are user inputs
    # TODO: There will be visuals and descriptions to help the user select rooting depth and soil type
    rd = rooting_depth #0.5 # rooting_depth
    soilt = str(soil_type)#'clayloam' # soil_type

    # Filter the coefficients for the soil type and rooting depth
    # CHANGE these based on rooting depth and soil type
    dfcoeffs = dfcoeffs[dfcoeffs['rootdepth'] == rd]
    dfcoeffs = dfcoeffs[dfcoeffs['soiltype'] == soilt]#'clayloam']

    # Add WTD column to dfclimate
    wtd_values = [1, 3, 6, 12]
    dfclimate = pd.concat([dfclimate.assign(WTD=wtd) for wtd in wtd_values], ignore_index=True)

    # Left join dfclimate and dfcoeffs
    dfsum = pd.merge(dfclimate, dfcoeffs, left_on='WTD', right_on='WTD', how='left')

    # Calculate LAI, AET, AETgw, and GWsubs
    # TODO: Have some descriptions and visuals of LAI
    # TODO: Have explanation of groundwater subsidy with images
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
    # remove remnant error in GW ET calcs
    dfsum["aetgwcalc"]=dfsum["aetgwcalc"].apply(lambda x: 0 if x <1 else x)

    # # Display results
    # st.markdown("### We’ve got your data, here is a summary:")
    # st.markdown(f"""
    # **Location:** ({lat:.4f}, {lon:.4f})
    # **Soil type:** {soil_string}
    # **Climate Data (Sample):** {gm_point}
    # """)

    # Set threshold based on root depth
    laithresh = 1.5 if rd == 0.5 else (2 if rd == 2 else 1 if rd == 3.6 else None)

    # Group by wtd2 and count rows where LAIcalc >= laithresh
    filtered_lai = dfsum[dfsum["LAIcalc"] >= laithresh]
    laisum = (
        filtered_lai
        .groupby("wtd2")
        .size()  # counts the number of rows per group
        .reset_index(name="noverthresh")
    )

    # Left-join lai with laisum
    lai2 = pd.merge(dfsum, laisum, on="wtd2", how="left")

    # Replace NaN values in 'noverthresh' with 0
    lai2["noverthresh"] = lai2["noverthresh"].fillna(0)

    # Calculate the percentage (percoverthresh) and round
    lai2["percoverthresh"] = round(lai2["noverthresh"] / 21, 2) * 100

    # Plot LAI time series
    p_lai1 = (
        ggplot(lai2) +
        geom_line(aes('wy', 'LAIcalc', linetype='wtd2')) +
        geom_point(aes('wy', 'LAIcalc', color='wb * 100')) +
        geom_hline(yintercept=laithresh, alpha=0.5) +
        geom_text(aes(x=2007, y=laithresh + 0.1), label=f"Example Management Target, LAI={laithresh}") +
        theme_bw() +
        scale_color_distiller(palette="YlGnBu", direction=1) +
        #ggtitle(f"Root Depth: {rd}m, Soil Type: {st}") +
        labs(x="Water Year", y="Annual Maximum Leaf Area Index (LAI)", color="Annual Potential\nWater Deficit (mm)", linetype="Water Table Depth")
    )
    # p_lai1.save(f"../outputs/python/{st}_{rd}_rootdepth_timeseries_LAI.png", height=4, width=6, units="in", dpi=300)

    # Plot LAI boxplot
    p_lai2 = (
        ggplot(lai2) +
        geom_boxplot(aes('wtd2', 'LAIcalc')) +
        geom_point(aes('wtd2', 'LAIcalc', color='wb * 100')) +
        geom_hline(yintercept=laithresh, alpha=0.5) +
        geom_text(aes(x='wtd2', y=laithresh, label='percoverthresh'), va="bottom") +
        geom_text(aes(y=laithresh, x=0), label=f"% Years over Management Target, LAI={laithresh}", va="top", ha="left")+
        theme_bw() +
        scale_color_distiller(palette="YlGnBu", direction=1) +
      #  ggtitle(f"Root Depth: {rd}m, Soil Type: {st}") +
        labs(x="Water Table Depth", y="Annual Maximum Leaf Area Index (LAI)", color="Annual Potential\nWater Deficit (mm)")
    )

    # Group by wtd2 and calculate min, max of aetcalc
    aetsum = (
        dfsum.groupby("wtd2")
        .agg(min=("aetcalc", "min"), max=("aetcalc", "max"))
        .reset_index()
    )

    # Left-join aet with aetsum
    aet2 = pd.merge(dfsum, aetsum, on="wtd2", how="left")

    # Round min and max to 0 digits
    aet2["min"] = aet2["min"].astype(int)
    aet2["max"] = aet2["max"].astype(int)

    # Create a rangelab column (e.g., "10-25")
    aet2["rangelab"] = aet2["min"].astype(str) + "-" + aet2["max"].astype(str)

    # charttop corresponds to the 'max' column in the DataFrame
    charttop = aet2["max"]

    # Plot AET time series
    p_aet1 = (
        ggplot(aet2) +
        geom_line(aes('wy', 'aetcalc', linetype='wtd2')) +
        geom_point(aes('wy', 'aetcalc', color='wb * 100')) +
        theme_bw() +
        scale_color_distiller(palette="YlGnBu", direction=1) +
      # ggtitle(f"Root Depth: {rd}m, Soil Type: {st}") +
        labs(x="Water Year", y="Annual Actual Evapotranspiration-Total (mm)", color="Annual Potential\nWater Deficit (mm)", linetype="Water Table Depth")
    )
    # p_aet1.save(f"../outputs/python/{st}_{rd}_rootdepth_timeseries_totalET.png", height=4, width=6, units="in", dpi=300)

    # Plot AET boxplot
    p_aet2 = (
        ggplot(aet2) +
        geom_boxplot(aes('wtd2', 'aetcalc')) +
        geom_point(aes('wtd2', 'aetcalc', color='wb * 100')) +
        geom_text(aes(x='wtd2', y='max', label='rangelab'), va="bottom") +
        theme_bw() +
        scale_color_distiller(palette="YlGnBu", direction=1) +
      # ggtitle(f"Root Depth: {rd}m, Soil Type: {st}") +
        labs(x="Water Table Depth", y="Annual Actual Evapotranspiration-Total (mm)",  color="Annual Potential\nWater Deficit (mm)")
    )
    # p_aet2.save(f"../outputs/python/{st}_{rd}_rootdepth_boxplot_totalET.png", height=4, width=6, units="in", dpi=300)


    # Filter the DataFrame
    gwsubs = dfsum[
        (dfsum["wtd2"] != "Free Drain")
    ]

    # Create 'ratio' column for gwsubscalc/aetcalc
    gwsubs = gwsubs.assign(ratio = gwsubs["gwsubscalc"] / gwsubs["aetcalc"])

    # Group by wtd2 and compute min, max, minperc, maxperc
    gwsubssum = (
        gwsubs.groupby("wtd2")
        .agg(
            min=("gwsubscalc", "min"),
            max=("gwsubscalc", "max"),
            minperc=("ratio", "min"),   # min of (gwsubscalc / aetcalc)
            maxperc=("ratio", "max"),   # max of (gwsubscalc / aetcalc)
        )
        .reset_index()
    )

    # Left-join the summarized data back to the filtered data
    gwsubs2 = pd.merge(gwsubs, gwsubssum, on="wtd2", how="left")

    # Round min and max to 0 decimals
    gwsubs2["min"] = gwsubs2["min"].astype(int)
    gwsubs2["max"] = gwsubs2["max"].astype(int)

    # Create a range label (e.g., "10-25")
    gwsubs2["rangelab"] = gwsubs2["min"].astype(str) + "-" + gwsubs2["max"].astype(str)

    # Define charttop as the 'max' column
    charttop = gwsubs2["max"]

    # Multiply minperc, maxperc by 100 and round
    gwsubs2["minperc"] = (gwsubs2["minperc"] * 100).astype(int)
    gwsubs2["maxperc"] = (gwsubs2["maxperc"] * 100).astype(int)

    # Create a percentage range label (e.g., "10-30% of Actual ET")
    gwsubs2["rangelabperc"] = (
        gwsubs2["minperc"].astype(str)
        + "-"
        + gwsubs2["maxperc"].astype(str)
        + "% of Actual ET"
    )

    # Plot GWsubs time series
    p_gwsubs1 = (
        ggplot(gwsubs2) +
        geom_line(aes('wy', 'gwsubscalc', linetype='wtd2')) +
        geom_point(aes('wy', 'gwsubscalc', color='wb * 100')) +
        theme_bw() +
        scale_color_distiller(palette="YlGnBu", direction=1) +
        #ggtitle(f"Root Depth: {rd}m, Soil Type: {st}") +
        labs(x="Water Year", y="Annual Groundwater Subsidy (mm)", color="Annual Potential\nWater Deficit (mm)", linetype="Water Table Depth")
    )
    # p_gwsubs1.save(f"../outputs/python/{st}_{rd}_rootdepth_timeseries_GWsubsET.png", height=4, width=6, units="in", dpi=300)

    # Plot GWsubs boxplot
    p_gwsubs2 = (
        ggplot(gwsubs2) +
        geom_boxplot(aes('wtd2', 'gwsubscalc')) +
        geom_point(aes('wtd2', 'gwsubscalc', color='wb * 100')) +
        geom_text(aes(x='wtd2', y='max', label='rangelabperc'), va="bottom") +
        theme_bw() +
        scale_color_distiller(palette="YlGnBu", direction=1) +
      # ggtitle(f"Root Depth: {rd}m, Soil Type: {st}") +
        labs(x="Water Table Depth", y="Annual Groundwater Subsidy (mm)",  color="Annual Potential\nWater Deficit (mm)")
    )

    # Create 'ratio' column for gwetcalc/aetcalc
    dfsum = dfsum.assign(ratio = dfsum["aetgwcalc"] / dfsum["aetcalc"])

    # Group by wtd2 and compute min, max, minperc, maxperc
    aetgwsum = (
        dfsum.groupby("wtd2")
        .agg(
            min=("aetgwcalc", "min"),
            max=("aetgwcalc", "max"),
            minperc=("ratio", "min"),   # min of (aetgwcalccalc / aetcalc)
            maxperc=("ratio", "max")   # max of (aetgwcalccalc / aetcalc)
        )
        .reset_index()
    )


    # Left-join aetaetgw with aetgwsum
    aetgw2 = pd.merge(dfsum, aetgwsum, on="wtd2", how="left")

    # Round min and max to 0 decimals
    aetgw2["min"] = aetgw2["min"].astype(int)
    aetgw2["max"] = aetgw2["max"].astype(int)

    # Create a range label (e.g., "10-25")
    aetgw2["rangelab"] = aetgw2["min"].astype(str) + "-" + aetgw2["max"].astype(str)

    # Define charttop as the 'max' column
    charttop = aetgw2["max"]

    # Multiply minperc, maxperc by 100 and round
    aetgw2["minperc"] = (aetgw2["minperc"] * 100).astype(int)
    aetgw2["maxperc"] = (aetgw2["maxperc"] * 100).astype(int)

    # Create a percentage range label (e.g., "10-30% of Actual ET")
    aetgw2["rangelabperc"] = (
        aetgw2["minperc"].astype(str)
        + "-"
        + aetgw2["maxperc"].astype(str)
        + "%\nof Actual ET"
    )

    # Plot AETAETGW time series
    p_aetgw1 = (
        ggplot(aetgw2) +
        geom_line(aes('wy', 'aetgwcalc', linetype='wtd2')) +
        geom_point(aes('wy', 'aetgwcalc', color='wb * 100')) +
        theme_bw() +
        scale_color_distiller(palette="YlGnBu", direction=1) +
      #  ggtitle(f"Root Depth: {rd}m, Soil Type: {st}") +
        labs(x="Water Year", y="Annual Actual Evapotranspiration-Groundwater (mm)", color="Annual Potential\nWater Deficit (mm)", linetype="Water Table Depth")
    )
    #p_aetgw1.save(f"../outputs/python/{st}_{rd}_rootdepth_timeseries_GWET.png", height=4, width=6, units="in", dpi=300)

    # Plot AETAETGW boxplot
    p_aetgw2 = (
        ggplot(aetgw2) +
        geom_boxplot(aes('wtd2', 'aetgwcalc')) +
        geom_point(aes('wtd2', 'aetgwcalc', color='wb * 100')) +
        geom_text(aes(x='wtd2', y='max', label='rangelabperc')) +

        theme_bw() +
        scale_color_distiller(palette="YlGnBu", direction=1) +
        #ggtitle(f"Root Depth: {rd}m, Soil Type: {st}") +
        labs(x="Water Table Depth", y="Annual Actual Evapotranspiration-Groundwater (mm)",  color="Annual Potential\nWater Deficit (mm)")
    )

    # Convert `p_lai1` and `p_lai2` to images
    def plot_to_image(plot):
        buf = BytesIO()
        plot.save(buf, format="png", height=4, width=6, units="in", dpi=300)
        buf.seek(0)
        return Image.open(buf)

    img_p_lai1 = plot_to_image(p_lai1)
    img_p_lai2 = plot_to_image(p_lai2)

    # Display the plots side by side on the main panel
    st.markdown("### Leaf Area Index (LAI) Analysis")

    # Create two columns
    col1, col2 = st.columns(2)

    # Render and display the first plot in the first column
    with col1:
        st.markdown("#### Annual Maximum Leaf Area Index (LAI)")
        st.pyplot(ggplot.draw(p_lai1))

    # Render and display the second plot in the second column
    with col2:
        st.markdown("#### Boxplot of Leaf Area Index (LAI)")
        st.pyplot(ggplot.draw(p_lai2))

    # Second row: Display AET plots
    st.markdown("### Actual Evapotranspiration (AET) Analysis")
    col3, col4 = st.columns(2)

    # Render and display the third plot in the first column of the second row
    with col3:
        st.markdown("#### Annual Actual Evapotranspiration-Total (AET)")
        st.pyplot(ggplot.draw(p_aet1))

    # Render and display the fourth plot in the second column of the second row
    with col4:
        st.markdown("#### Boxplot of Annual Actual Evapotranspiration-Total (AET)")
        st.pyplot(ggplot.draw(p_aet2))

    # Third row: Display Groundwater Subsidy (GWsubs) Analysis plots
    st.markdown("### Groundwater Subsidy (GWsubs) Analysis")
    col5, col6 = st.columns(2)

    # Render and display the third set of plots
    with col5:
        st.markdown("#### Groundwater Subsidy Time Series)")
        st.pyplot(ggplot.draw(p_gwsubs1))

    with col6:
        st.markdown("#### Boxplot of Annual Groundwater Subsidy")
        st.pyplot(ggplot.draw(p_gwsubs2))


    # Fourth row: Display Groundwater Subsidy (GWsubs) Analysis plots
    st.markdown("### Groundwater Subsidy (GWsubs) Analysis")
    col7, col8 = st.columns(2)

    # Render and display the fourth set of plots
    with col7:
        st.markdown("#### Annual Actual Evapotranspiration-Groundwater (mm)")
        st.pyplot(ggplot.draw(p_aetgw1))

    with col8:
        st.markdown("#### Boxplot of Annual Actual Evapotranspiration-Groundwater (mm)")
        st.pyplot(ggplot.draw(p_aetgw2))

    # # Function to save plots to PDF
    # def save_plots_to_pdf():
    #     pdf_buffer = io.BytesIO()

    #     with PdfPages(pdf_buffer) as pdf:
    #         # List of ggplots to save
    #         plots = [p_lai1, p_lai2, p_aet1, p_aet2, p_gwsubs1, p_gwsubs2, p_aetgw1, p_aetgw2]
    #         titles = [
    #             "Annual Maximum Leaf Area Index (LAI)",
    #             "Boxplot of Leaf Area Index (LAI)",
    #             "Annual Actual Evapotranspiration-Total (AET)",
    #             "Boxplot of Annual Actual Evapotranspiration-Total (AET)",
    #             "Groundwater Subsidy Time Series",
    #             "Boxplot of Annual Groundwater Subsidy",
    #             "Annual Actual Evapotranspiration-Groundwater (mm)",
    #             "Boxplot of Annual Actual Evapotranspiration-Groundwater (mm)"
    #         ]

    #         for plot, title in zip(plots, titles):
    #             fig = plot.draw()  # Correctly draw ggplot as a figure
    #             fig.set_size_inches(6, 4)  # Adjust figure size
    #             fig.suptitle(title)  # Add title
    #             pdf.savefig(fig, bbox_inches='tight')  # Save to PDF
    #             plt.close(fig)  # Close figure to free memory

    #     pdf_buffer.seek(0)
    #     return pdf_buffer

    # # Button to generate and download PDF
    # pdf_buffer = save_plots_to_pdf()
    # st.download_button(
    #     label="Download Report as PDF",
    #     data=pdf_buffer,
    #     file_name="LAI_AET_Report.pdf",
    #     mime="application/pdf"
    # )

# Function to save plots to PDF with proper title spacing
def save_plots_to_pdf():
    pdf_buffer = io.BytesIO()

    with PdfPages(pdf_buffer) as pdf:
        # List of ggplots to save
        plots = [p_lai1, p_lai2, p_aet1, p_aet2, p_gwsubs1, p_gwsubs2, p_aetgw1, p_aetgw2]
        titles = [
            "Annual Maximum Leaf Area Index (LAI)",
            "Boxplot of Leaf Area Index (LAI)",
            "Annual Actual Evapotranspiration-Total (AET)",
            "Boxplot of Annual Actual Evapotranspiration-Total (AET)",
            "Groundwater Subsidy Time Series",
            "Boxplot of Annual Groundwater Subsidy",
            "Annual Actual Evapotranspiration-Groundwater (mm)",
            "Boxplot of Annual Actual Evapotranspiration-Groundwater (mm)"
        ]

        for plot, title in zip(plots, titles):
            fig = plot.draw()  # Correctly draw ggplot as a figure
            fig.set_size_inches(6, 4)  # Adjust figure size
            
            # Add title with adjusted spacing
            fig.suptitle(title, y=1.05, fontsize=12)  # Move title higher
            plt.subplots_adjust(top=0.85)  # Adjust top spacing to prevent overlap
            
            pdf.savefig(fig, bbox_inches='tight')  # Save to PDF
            plt.close(fig)  # Close figure to free memory

    pdf_buffer.seek(0)
    return pdf_buffer

# Button to generate and download PDF
pdf_buffer = save_plots_to_pdf()
st.download_button(
    label="Download Report as PDF",
    data=pdf_buffer,
    file_name="LAI_AET_Report.pdf",
    mime="application/pdf"
)

else:
    if map_data is None:
        st.sidebar.warning("Please select a point on the map before clicking 'Get Data'.")
