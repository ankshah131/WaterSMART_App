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

from app_def.components.header import render_header
from app_def.components.footer import render_footer
from app_def.content.definitions import render_definitions

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

# Add Earth Engine layer support to folium
def add_ee_layer(self, ee_image_object, vis_params, name):
    map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
    folium.raster_layers.TileLayer(
        tiles=map_id_dict['tile_fetcher'].url_format,
        attr='Google Earth Engine',
        name=name,
        overlay=True,
        control=True
    ).add_to(self)

# Patch the folium.Map class
folium.Map.add_ee_layer = add_ee_layer

# Set up Streamlit layout
st.set_page_config(page_title="Nevada GDE Water Needs Explorer", layout="wide")

# Get current query params
query_params = st.query_params

# Get the tab name from URL or default to "GDE Explorer"
default_tab = query_params.get("tab", "GDE Explorer")

# Create tabs
#tab1, tab2 = st.tabs(["GDE Explorer", "Definitions"])

tab_labels = ["GDE Explorer", "Definitions"]

# Reorder tabs so the selected one appears first
if default_tab == "Definitions":
    tab_labels = ["Definitions", "GDE Explorer"]
else:
    tab_labels = ["GDE Explorer", "Definitions"]

# Create Streamlit tabs
tabs = st.tabs(tab_labels)

# Get references
tab_map = dict(zip(tab_labels, tabs))

with tab_map["GDE Explorer"]:
    if default_tab == "GDE Explorer":
        st.session_state.get_data_clicked = False

        # Set up Streamlit layout
        st.title("Welcome to the Nevada GDE Water Needs Explorer")

        # App description
        st.write("""
        Groundwater-dependent ecosystems (GDEs) in Nevada play a critical role in sustaining biodiversity and supporting ecological balance.
        These systems rely on stable water levels, making them particularly vulnerable to changes in groundwater availability caused by climate variability and human activities.
        
        This tool allows users to explore the water needs of GDEs in Nevada and how this varies among soil textures, climate, rooting depth, and groundwater depth based on estimates from model output. 
        
        Use the control panel on the left to get started to select your area of interest and to pull climate and soils data for this location. Once you have selected your location, click “Get Data.”
        
        *NOTE: This tool provides estimates of how a GDE would respond IF it existed at the selected location with the chosen characteristics. 
        However, GDEs do not occur at many locations in Nevada and it is your responsibility to understand your results relate to a hypothetical system at the location you specify. 
        Estimates of GDE water needs are based on what water a hypothetical GDE might use under the climate conditions associated with the location on a map and the soil, vegetation, and groundwater depth characteristics you define.  
        The soil hydraulic properties, vegetation characteristics and health and groundwater conditions in an actual GDE might differ and could therefore cause actual water use to be substantially different. 
        Furthermore, the model developed here is a simplification of our current understanding of ecosystem processes and may not accurately quantify water use in all cases.*
        """)

        # Initialize a Folium map with a proper basemap
        default_coords = [39.5, -117]
        coords_ee = ee.Geometry.Point(default_coords)

        # Initialize session state
        if "selected_coords" not in st.session_state:
            st.session_state.selected_coords = default_coords

        # Create Folium map
        folium_map = folium.Map(location=st.session_state.selected_coords, zoom_start=7, tiles="OpenStreetMap")

        # Add initial marker
        marker = folium.Marker(location=st.session_state.selected_coords, popup="Selected Location", icon=folium.Icon(color="red"))
        marker.add_to(folium_map)

        # # Embed the map in the sidebar
        # with st.sidebar:
        #     st.header("Control Panel")
        #     st.write("Select your area of interest by clicking on the map below:")
        #     st.write("### Interactive Map")
        #     map_data = st_folium(folium_map, width=300, height=500)


        # Define layer options
        layer_options = {
            "Administrative groundwater boundaries": None,
            "Soil texture": None,
            "Average precipitation": None,
            "Average potential evapotranspiration": None,
            "Average potential water deficit": None
        }


        # Define information for each layer
        # Change links accordingly
        layer_links = {
            "Administrative groundwater boundaries": "groundwater-boundaries",
            "Soil texture": "soil-texture",
            "Average precipitation": "precipitation",
            "Average potential evapotranspiration": "evapotranspiration",
            "Average potential water deficit": "water-deficit"
        }

        layer_assets = {
            "Average potential evapotranspiration": "projects/nps-waterforecosystems/assets/WaterSMART_App/GRIDMET_Mean_ETo_1991_2020",
            "Average precipitation": "projects/nps-waterforecosystems/assets/WaterSMART_App/GRIDMET_Mean_Precip_1991_2020",
            "Average potential water deficit": "projects/nps-waterforecosystems/assets/WaterSMART_App/GRIDMET_Water_Deficit_1991_2020",
            "Soil Texture": "projects/sat-io/open-datasets/CSRL_soil_properties/physical/soil_texture_profile/texture_2550",
        }

        layer_vis_params = {
            "Soil texture": {
                'min': 1,
                'max': 12,
                'palette': ['blue', 'green', 'yellow', 'orange', 'red']
            },
            "Average precipitation": {
                'min': 0,
                'max': 2500,
                'palette': ['ffffff', 'blue']
            },
            "Average potential evapotranspiration": {
                'min': 0,
                'max': 2000,
                'palette': ['ffffff', 'orange']
            },
            "Average potential water deficit": {
                'min': -1000,
                'max': 1000,
                'palette': ['blue', 'white', 'red']
            }
        }

        selected_layers = {key: False for key in layer_options.keys()}

        # Embed the map in the sidebar
        with st.sidebar:
            st.header("Control Panel")
            st.write("Select your area of interest by clicking on the map below:")
            st.write("### Interactive Map")
            map_data = st_folium(folium_map, width=300, height=500)
        
            # display ee layers
            for label, is_checked in selected_layers.items():
                if is_checked and label in layer_assets:
                    asset_id = layer_assets[label]
                    vis_params = layer_vis_params.get(label, {})
                    ee_image = ee.Image(asset_id)
                    folium_map.add_ee_layer(ee_image, vis_params, label)
            
            # Add layer toggle control
            folium.LayerControl().add_to(folium_map)
            
            # Check for selected coordinates from the map
            if map_data is not None and "last_clicked" in map_data and map_data["last_clicked"] is not None:
                lat, lon = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]
                coords_ee = ee.Geometry.Point([lon, lat])
                st.sidebar.write(f"**Selected Coordinates:** ({lat:.4f}, {lon:.4f})")
            else:
                st.sidebar.warning("No point selected on the map yet.")


        # Add a "Get Data" button with session state tracking
        if "get_data_clicked" not in st.session_state:
            st.session_state.get_data_clicked = False  # Ensure default state is False

        if st.sidebar.button("Get Data!"):
            st.session_state.get_data_clicked = True  # Update state when button is clicked


         # Add checkboxes for each layer with info buttons
        st.sidebar.write("### Visualization Layers:")
        #selected_layers = {}  # Store checkbox states
        #selected_layers = {key: False for key in layer_options.keys()}
        
        for label, key in layer_options.items():
            cols = st.sidebar.columns([0.8, 0.2])  # 80% checkbox, 20% info button
            
            # Checkbox for layer selection
            with cols[0]:
                selected_layers[label] = st.checkbox(label, value=False)
        
            # Small info button with unique key based on label
            with cols[1]:
                if st.button("ℹ️", key=f"info_{label.replace(' ', '_')}"):
                    anchor = layer_links.get(label)
                    if anchor:
                        # Redirect to Definitions tab with jump target
                        st.query_params.tab = "Definitions"
                        st.query_params.jump_to = anchor
                        st.rerun()
            
        # Ensure the code only runs if the button was clicked
        if st.session_state.get_data_clicked and coords_ee is not None:
        #if get_data_btn is not None and coords_ee is not None:
            st.empty()

            try:
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
        
                # Display summary box before root depth selector
                st.markdown(
                    f"""
                    <div style="
                        background-color: #c6e2a9;
                        padding: 10px;
                        border-radius: 5px;
                        border: 1px solid #666;
                        font-family: Arial, sans-serif;">
                        <b>We've got your data, here is a summary:</b><br>
                        <b>Location:</b> {lat:.2f} N, {lon:.2f} W &nbsp;&nbsp;
                        <b>Soil type:</b> {soil_string}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
                # Water balance calculation
                year_start = 1991
                year_end = 2020
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
                    #image_ws = image_ws.divide(100)
                    return image.addBands(image_ws)
            
                gm_wy = ee.ImageCollection(gm_wy).map(calculate_wb).toBands()
                
                gm_point = gm_wy.reduceRegion(reducer=ee.Reducer.mean(), geometry=coords_ee, scale=4000).getInfo()
            
                # Rooting depth and soil type controls
                # Define allowed values
                allowed_values = [0.5, 2, 3.6]
            
                # Custom CSS for hoverable tooltips
                st.markdown("""
                    <style>
                    .info-icon {
                        display: inline-block;
                        font-size: 18px;
                        margin-left: 8px;
                        cursor: pointer;
                        color: #4F8BF9;
                    }
                    .tooltip {
                        position: relative;
                        display: inline-block;
                    }
                    .tooltip .tooltiptext {
                        visibility: hidden;
                        width: 300px;
                        background-color: #555;
                        color: #fff;
                        text-align: left;
                        border-radius: 5px;
                        padding: 8px;
                        position: absolute;
                        z-index: 1;
                        bottom: 125%; /* Position above the icon */
                        left: 50%;
                        transform: translateX(-50%);
                        opacity: 0;
                        transition: opacity 0.3s;
                    }
                    .tooltip:hover .tooltiptext {
                        visibility: visible;
                        opacity: 1;
                    }
                    </style>
                """, unsafe_allow_html=True)
                
                # Rooting Depth Section with Inline Info Button
                col1, col2 = st.columns([0.012, 0.1])  # Adjust column widths to keep icon close
                with col1:
                    st.subheader("Rooting Depth")
                with col2:
                    st.markdown("""
                        <div class="tooltip">
                            <span class="info-icon">ℹ️</span>
                            <span class="tooltiptext">
                                Groundwater-dependent vegetation can access groundwater through their roots, but rooting depths vary. 
                                Meadow and rangeland grasses often have roots within 2m of the ground surface, whereas some phreatophytic shrubs and trees 
                                can have roots as deep as 6m or more (The Nature Conservancy 2021).
                                Choose from 0.5m for herbaceous meadow root depths, 2m for grass root depth, and 3.6m for phreatophyte shrubland root depths.
                            </span>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Rooting Depth Slider
                rooting_depth = st.select_slider("Select rooting depth (m):", options=allowed_values, value=2)
                st.write(f"Selected Rooting Depth: {rooting_depth} m")
                
                # Soil Type Section with Inline Info Button
                col3, col4 = st.columns([0.012, 0.1])
                with col3:
                    st.subheader("Soil Type")
                with col4:
                    st.markdown("""
                        <div class="tooltip">
                            <span class="info-icon">ℹ️</span>
                            <span class="tooltiptext">
                                The soil texture from Walkinshaw et al. (2020) is the default choice for the area in question.
                                Soils with different amounts of sand, silt, and clay have differing abilities to retain water.
                                Some drain away instantly, and some also hold onto it more tightly when dry, like a clay, which can limit plant access to that water.
                            </span>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Soil Type Dropdown
                # soil_type = st.selectbox(
                #     "Select soil type:",
                #     ["loamysand", "sandyloam", "loam", "siltloam", "silt",
                #      "sandyclayloam", "clayloam", "siltyclayloam", "sandyclay", "siltyclay", "clay"],
                #     index=2
                # )

                soil_options = ["loamysand", "sandyloam", "loam", "siltloam", "silt",
                "sandyclayloam", "clayloam", "siltyclayloam", "sandyclay", "siltyclay", "clay"]

                # Ensure the soil_string is valid
                default_index = soil_options.index(soil_string) if soil_string in soil_options else 0
                
                soil_type = st.selectbox(
                    "Select soil type:",
                    soil_options,
                    index=default_index
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
                # dfee['wb2'] = dfee['wb'] ** 2  # Square of 'wb'
                # dfee['wb3'] = dfee['wb'] ** 3  # Cube of 'wb'
                
                # Calculate annual water balance variables
                dfee['eto2'] = dfee['eto'] /10  # divide ‘eto’ by 10
                dfee['pr2'] = dfee['pr'] ** 2  # Square of 'pr'
                dfee['pet2'] = dfee['eto2'] ** 2  # Square of ‘eto’/10'
            
                # Rename dfee as dfclimate
                dfclimate = dfee
            
                # Load the dataset
                #dfcoeffs = pd.read_csv('/content/MixedEffectsModelCoefficients102924_LAI_AET_AETG_GWsubs.csv')
                dfcoeffs = pd.read_csv('https://raw.githubusercontent.com/ankshah131/WaterSMART_App/main/streamlit_app/MixedEffectsModelCoefficients102924_ppetquad.csv')
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
                # dfsum['LAIcalc'] = (
                #     dfsum['LAIIntercept'] +
                #     dfsum['wb'] * dfsum['LAIwbx'] +
                #     dfsum['wb2'] * dfsum['LAIwb2x'] +
                #     dfsum['wb3'] * dfsum['LAIwb3x']
                # )
                # dfsum['aetcalc'] = (
                #     dfsum['aetIntercept'] +
                #     dfsum['wb'] * dfsum['aetwbx'] +
                #     dfsum['wb2'] * dfsum['aetwb2x'] +
                #     dfsum['wb3'] * dfsum['aetwb3x']
                # )
                # dfsum['aetgwcalc'] = (
                #     dfsum['aetgwIntercept'] +
                #     dfsum['wb'] * dfsum['aetgwwbx'] +
                #     dfsum['wb2'] * dfsum['aetgwwb2x'] +
                #     dfsum['wb3'] * dfsum['aetgwwb3x']
                # )
                # dfsum['gwsubscalc'] = (
                #     dfsum['gwsubsIntercept'] +
                #     dfsum['wb'] * dfsum['gwsubswbx'] +
                #     dfsum['wb2'] * dfsum['gwsubswb2x'] +
                #     dfsum['wb3'] * dfsum['gwsubswb3x']
                # )
                # # remove remnant error in GW ET calcs
                # dfsum["aetgwcalc"]=dfsum["aetgwcalc"].apply(lambda x: 0 if x <1 else x)
            
                dfsum['LAIcalc'] = (
                    dfsum['LAIIntercept'] +
                    dfsum['pr'] * dfsum['LAIPx'] +
                    dfsum['eto2'] * dfsum['LAIPETx'] +
                    dfsum['pr2'] * dfsum['LAIP2x']+
                    dfsum['pet2'] * dfsum['LAIPET2x']
                    )
                dfsum['aetcalc'] = (
                    dfsum['aetIntercept'] +
                    dfsum['pr'] * dfsum['aetPx'] +
                    dfsum['eto2'] * dfsum['aetPETx'] +
                    dfsum['pr2'] * dfsum['aetP2x'] +
                    dfsum['pet2'] * dfsum['aetPET2x']
                )
                dfsum['aetgwcalc'] = (
                    dfsum['aetgwIntercept'] +
                    dfsum['pr'] * dfsum['aetgwPx'] +
                    dfsum['eto2'] * dfsum['aetgwPETx'] +
                    dfsum['pr2'] * dfsum['aetgwP2x'] +
                    dfsum['pet2'] * dfsum['aetgwPET2x']
                )
                dfsum['gwsubscalc'] = (
                    dfsum['gwsubsIntercept'] +
                    dfsum['pr'] * dfsum['gwsubsPx'] +
                    dfsum['eto2'] * dfsum['gwsubsPETx'] +
                    dfsum['pr2'] * dfsum['gwsubsP2x'] +
                    dfsum['pet2'] * dfsum['gwsubsPET2x']
                )
                # remove remnant error in GW ET calcs
                dfsum["aetgwcalc"]=dfsum["aetgwcalc"].apply(lambda x: 0 if x <1 else x)
                dfsum["LAIcalc"]=dfsum["LAIcalc"].apply(lambda x: 0 if x <1 else x)
                dfsum["aetcalc"]=dfsum["aetcalc"].apply(lambda x: 0 if x <1 else x)
                dfsum["gwsubscalc"]=dfsum["gwsubscalc"].apply(lambda x: 0 if x <1 else x)
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
                
                #identify min and max lai values
                minlai = lai2["LAIcalc"].min()
                maxlai = lai2["LAIcalc"].max()
                maxlai1 = maxlai*1.1
                
                # Replace NaN values in 'noverthresh' with 0
                lai2["noverthresh"] = lai2["noverthresh"].fillna(0)
                
                # Calculate the percentage (percoverthresh) and round
                lai2["percoverthresh"] = round(lai2["noverthresh"] / 30, 2) * 100
            
                # Group by wtd2 and calculate min, max of pwd
                pwdsum = dfsum[
                    (dfsum["wtd2"] == "Free Drain")
                ]
                #identify min and max lai values
                mineto = pwdsum["eto"].min()*-1.2
                maxp = pwdsum["pr"].max()*1.1
                maxpwd = pwdsum["wb"].max()*0.9
            
                p_pwd1 = (
                 ggplot(data=pwdsum)+
                      geom_bar(aes('wy','pr'), fill="Blue", stat="identity", alpha=0.5)+
                      geom_bar(aes('wy','eto*-1'), fill="Brown", stat="identity", alpha=0.5)+
                      geom_line(aes('wy','wb'), color="white")+
                      geom_point(aes('wy','wb', color='wb'))+
                      theme_bw()+
                      geom_text(aes(1990, mineto),label="Potential ET", color="Brown", ha="left", va="top")+
                      geom_text(aes(1990, maxp),label="Precipitation",color="Blue", ha="left")+
                      scale_color_distiller(palette="YlGnBu", direction=1)+
                      ggtitle("Annual Precipitation, Potential ET, and Potential Water Deficit")+
                      labs(x="Water Year", y="Annual Water Balance (mm)", color="Potential\nWater\nDeficit (mm)")
                )
            
                # Plot LAI time series
                p_lai1 = (
                    ggplot(lai2) +
                    geom_line(aes('wy', 'LAIcalc', linetype='wtd2')) +
                    geom_point(aes('wy', 'LAIcalc', color='wb')) +
                    geom_hline(yintercept=laithresh, alpha=0.5) +
                   # geom_text(aes(x=2007, y=laithresh + 0.1), label=f"Example Management Target, LAI={laithresh}") +
                    theme_bw() +
                    scale_color_distiller(palette="YlGnBu", direction=1) +
                    ggtitle("Timeseries of Annual Maximum\nLeaf Area Index (LAI)")+
                    labs(x="Water Year", y="Annual Maximum Leaf Area Index (LAI)", color="Annual\nPotential\nWater\nDeficit (mm)", linetype="Water Table\nDepth",
                         subtitle=f"Ex. Management Target, LAI={laithresh}")
                )
                # p_lai1.save(f"../outputs/python/{st}_{rd}_rootdepth_timeseries_LAI.png", height=4, width=6, units="in", dpi=300)
            
                # Plot LAI boxplot
                p_lai2 = (
                    ggplot(lai2) +
                    geom_boxplot(aes('wtd2', 'LAIcalc')) +
                    geom_point(aes('wtd2', 'LAIcalc', color='wb')) +
                    geom_hline(yintercept=laithresh, alpha=0.5) +
                   #geom_text(aes(x='wtd2', y=laithresh, label='percoverthresh'), va="bottom") +
                   #geom_text(aes(y=laithresh, x=0), label=f"% Years over Management Target, LAI={laithresh}", va="top", ha="left")+
                    annotate('text', y = maxlai1, x=lai2["wtd2"], label = lai2["percoverthresh"]) +
                    coord_cartesian(ylim = [minlai, maxlai1], expand = True) +
                    theme_bw() +
                    scale_color_distiller(palette="YlGnBu", direction=1) +
                    ggtitle(f"% Years over\nManagement Target, LAI={laithresh}")+
                    theme(legend_position="none")+
                  #  ggtitle(f"Root Depth: {rd}m, Soil Type: {st}") +
                    labs(x="Water Table Depth", y="Annual Maximum Leaf Area Index (LAI)", subtitle="")
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
                
                #identify min and max aet values
                minaet = aet2["aetcalc"].min()
                maxaet = aet2["aetcalc"].max()
                maxaet1 = maxaet*1.1
            
                p_aet1 = (
                    ggplot(aet2) +
                    geom_line(aes('wy', 'aetcalc', linetype='wtd2')) +
                    geom_point(aes('wy', 'aetcalc', color='wb')) +
                    theme_bw() +
                    scale_color_distiller(palette="YlGnBu", direction=1) +
                    ggtitle("Timeseries of Annual Actual\nEvapotranspiration (mm)") +
                    labs(x="Water Year", y="Annual Actual Evapotranspiration (mm)", color="Annual\nPotential\nWater\nDeficit (mm)", linetype="Water Table\nDepth")
                )
                # p_aet1.save(f"../outputs/python/{st}_{rd}_rootdepth_timeseries_totalET.png", height=4, width=6, units="in", dpi=300)
            
                # Plot AET boxplot
                p_aet2 = (
                    ggplot(aet2) +
                    geom_boxplot(aes('wtd2', 'aetcalc')) +
                    geom_point(aes('wtd2', 'aetcalc', color='wb')) +
                   # geom_text(aes(x='wtd2', y='max', label='rangelab'), va="bottom") +
                    #annotate('text', y = maxaet1, x=aet2["wtd2"], label = aet2["rangelab"]) +
                    #coord_cartesian(ylim = [minaet, maxaet1], expand = True) +
                    annotate('text', y = maxaet1, x=aet2["wtd2"], label = aet2["rangelab"]) +
                    coord_cartesian(ylim = [minaet, maxaet1], expand = True) +
                    theme_bw() +
                    scale_color_distiller(palette="YlGnBu", direction=1) +
                    ggtitle("Range of Annual\nActual ET (mm)") +
                    theme(legend_position="none")+
                    labs(x="Water Table Depth", y="Annual Actual Evapotranspiration (mm)",  color="Annual\nPotential\nWater\nDeficit (mm)", subtitle="")
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
                    + "%"
                )
                
                #identify min and max gwsubs values
                mingwsubs = gwsubs2["gwsubscalc"].min()
                maxgwsubs = gwsubs2["gwsubscalc"].max()
                maxgwsubs1 = maxgwsubs*1.1
            
                # Plot GWsubs time series
                p_gwsubs1 = (
                    ggplot(gwsubs2) +
                    geom_line(aes('wy', 'gwsubscalc', linetype='wtd2')) +
                    geom_point(aes('wy', 'gwsubscalc', color='wb')) +
                    theme_bw() +
                    scale_color_distiller(palette="YlGnBu", direction=1) +
                    ggtitle("Timeseries of Annual Groundwater\nSubsidy (% of Actual ET)") +
                    labs(x="Water Year", y="Annual Groundwater Subsidy (mm)", color="Annual\nPotential\nWater\nDeficit (mm)", linetype="Water Table\nDepth")
                )
                # p_gwsubs1.save(f"../outputs/python/{st}_{rd}_rootdepth_timeseries_GWsubsET.png", height=4, width=4, units="in", dpi=300)
                
                # Plot GWsubs boxplot
                p_gwsubs2 = (
                    ggplot(gwsubs2) +
                    geom_boxplot(aes('wtd2', 'gwsubscalc')) +
                    geom_point(aes('wtd2', 'gwsubscalc', color='wb')) +
                   # geom_text(aes(x='wtd2', y='max', label='rangelabperc'), va="bottom") +
                    annotate('text', y = maxgwsubs1, x=gwsubs2["wtd2"], label = gwsubs2["rangelabperc"]) +
                    coord_cartesian(ylim = [mingwsubs, maxgwsubs1], expand = True) +
                    theme_bw() +
                    scale_color_distiller(palette="YlGnBu", direction=1) +
                    ggtitle("Range of Annual Groundwater\nSubsidy (% of Actual ET)") +
                    theme(legend_position="none")+
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
                    + "%"
                )
                
                #identify min and max aetgwc values
                minaetgw = aetgw2["aetgwcalc"].min()
                maxaetgw = aetgw2["aetgwcalc"].max()
                maxaetgw1 = maxaetgw*1.1
            
                # Plot AETAETGW time series
                p_aetgw1 = (
                    ggplot(aetgw2) +
                    geom_line(aes('wy', 'aetgwcalc', linetype='wtd2')) +
                    geom_point(aes('wy', 'aetgwcalc', color='wb')) +
                    theme_bw() +
                    scale_color_distiller(palette="YlGnBu", direction=1) +
                    ggtitle("Timeseries of Annual Groundwater ET\n(% of Actual ET)") +
                    labs(x="Water Year", y="Annual Actual Evapotranspiration-Groundwater (mm)", color="Annual\nPotential\nWater\nDeficit (mm)", linetype="Water Table\nDepth")
                )
                #p_aetgw1.save(f"../outputs/python/{st}_{rd}_rootdepth_timeseries_GWET.png", height=4, width=4, units="in", dpi=300)
                
                # Plot AETAETGW boxplot
                p_aetgw2 = (
                    ggplot(aetgw2) +
                    geom_boxplot(aes('wtd2', 'aetgwcalc')) +
                    geom_point(aes('wtd2', 'aetgwcalc', color='wb')) +
                    #geom_text(aes(x='wtd2', y='max', label='rangelabperc')) +
                    annotate('text', y = maxaetgw1, x=aetgw2["wtd2"], label = aetgw2["rangelabperc"]) +
                    coord_cartesian(ylim = [minaetgw, maxaetgw1], expand = True) +
                    theme_bw() +
                    scale_color_distiller(palette="YlGnBu", direction=1) +
                    ggtitle("Range of Annual Groundwater\nET (% of Actual ET)") +
                    theme(legend_position="none")+
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
            
                st.markdown("### Cumulative Plot")
                st.pyplot(ggplot.draw(p_pwd1))
            
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
                    st.markdown("#### Groundwater Subsidy Time Series")
                    st.pyplot(ggplot.draw(p_gwsubs1))
            
                with col6:
                    st.markdown("#### Boxplot of Annual Groundwater Subsidy")
                    st.pyplot(ggplot.draw(p_gwsubs2))
            
            
                # Fourth row: Display Groundwater Subsidy (GWsubs) Analysis plots
                st.markdown("### Groundwater Evapotranspiration (AETgw) Analysis")
                col7, col8 = st.columns(2)
            
                # Render and display the fourth set of plots
                with col7:
                    st.markdown("#### Annual Actual Evapotranspiration-Groundwater (mm)")
                    st.pyplot(ggplot.draw(p_aetgw1))
            
                with col8:
                    st.markdown("#### Boxplot of Annual Actual Evapotranspiration-Groundwater (mm)")
                    st.pyplot(ggplot.draw(p_aetgw2))
    
                
                # def save_plots_to_pdf():
                #     pdf_buffer = io.BytesIO()
                
                #     with PdfPages(pdf_buffer) as pdf:
                #         # Pair the plots and their titles
                #         paired_plots = [
                #             (p_lai1, "Annual Maximum Leaf Area Index (LAI)", p_lai2, "Boxplot of Leaf Area Index (LAI)"),
                #             (p_aet1, "Annual Actual Evapotranspiration-Total (AET)", p_aet2, "Boxplot of Annual AET-Total"),
                #             (p_gwsubs1, "Groundwater Subsidy Time Series", p_gwsubs2, "Boxplot of Groundwater Subsidy"),
                #             (p_aetgw1, "Annual AET-Groundwater", p_aetgw2, "Boxplot of AET-Groundwater")
                #         ]
                
                #         for plot1, title1, plot2, title2 in paired_plots:
                #             # Draw individual ggplot figures
                #             fig1 = plot1.draw()
                #             fig2 = plot2.draw()
                
                #             fig1.set_size_inches(6, 4)
                #             fig2.set_size_inches(6, 4)
                
                #             # Render both into images
                #             buf1 = BytesIO()
                #             buf2 = BytesIO()
                #             fig1.savefig(buf1, format='png', dpi=300, bbox_inches='tight')
                #             fig2.savefig(buf2, format='png', dpi=300, bbox_inches='tight')
                #             plt.close(fig1)
                #             plt.close(fig2)
                
                #             buf1.seek(0)
                #             buf2.seek(0)
                
                #             img1 = Image.open(buf1)
                #             img2 = Image.open(buf2)
                
                #             # Match heights
                #             h = max(img1.height, img2.height)
                #             img1 = img1.resize((int(img1.width * h / img1.height), h))
                #             img2 = img2.resize((int(img2.width * h / img2.height), h))
                
                #             # Combine side by side
                #             combined = Image.new("RGB", (img1.width + img2.width, h), (255, 255, 255))
                #             combined.paste(img1, (0, 0))
                #             combined.paste(img2, (img1.width, 0))
                
                #             # Insert combined image into a matplotlib figure
                #             fig, ax = plt.subplots(figsize=(12, h / 100))  # height in inches
                #             ax.axis('off')
                #             ax.imshow(combined)
                
                #             pdf.savefig(fig, bbox_inches='tight')
                #             plt.close(fig)
                
                #     pdf_buffer.seek(0)
                #     return pdf_buffer
    
                def save_plots_to_pdf(lat=lat, lon=-lon, soil_string=soilt):
                    pdf_buffer = io.BytesIO()
                
                    with PdfPages(pdf_buffer) as pdf:
                        from PIL import ImageDraw, ImageFont
                
                        ### -------- PAGE 1: INFO BOX + CUMULATIVE PLOT -------- ###
                        fig_pwd1 = p_pwd1.draw()
                        fig_pwd1.set_size_inches(10, 5)
                
                        # Save cumulative plot to buffer
                        buf_pwd1 = BytesIO()
                        fig_pwd1.savefig(buf_pwd1, format='png', dpi=300, bbox_inches='tight')
                        plt.close(fig_pwd1)
                        buf_pwd1.seek(0)
                
                        img_pwd1 = Image.open(buf_pwd1)
                
                        # Generate info box banner
                        info_text = f"We've got your data, here is a summary:\nLocation: {lat:.2f} N, {lon:.2f} W    Soil type: {soil_string}"
                        font_size = 20
                        try:
                            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
                        except:
                            font = ImageFont.load_default()
                
                        padding = 20
                        info_img = Image.new("RGB", (img_pwd1.width, 80), "#c6e2a9")
                        draw = ImageDraw.Draw(info_img)
                        draw.text((padding, 10), info_text, font=font, fill="black")
                
                        # Combine vertically: info banner + plot
                        combined_top = Image.new("RGB", (img_pwd1.width, info_img.height + img_pwd1.height), (255, 255, 255))
                        combined_top.paste(info_img, (0, 0))
                        combined_top.paste(img_pwd1, (0, info_img.height))
                
                        # Save page to PDF
                        fig, ax = plt.subplots(figsize=(12, combined_top.height / 100))
                        ax.axis('off')
                        ax.imshow(combined_top)
                        pdf.savefig(fig, bbox_inches='tight')
                        plt.close(fig)
                
                        ### -------- PAGES 2+: SIDE-BY-SIDE PLOT PAIRS -------- ###
                        paired_plots = [
                            (p_lai1, "Annual Maximum Leaf Area Index (LAI)", p_lai2, "Boxplot of Leaf Area Index (LAI)"),
                            (p_aet1, "Annual Actual Evapotranspiration-Total (AET)", p_aet2, "Boxplot of Annual AET-Total"),
                            (p_gwsubs1, "Groundwater Subsidy Time Series", p_gwsubs2, "Boxplot of Groundwater Subsidy"),
                            (p_aetgw1, "Annual AET-Groundwater", p_aetgw2, "Boxplot of AET-Groundwater")
                        ]
                
                        for plot1, title1, plot2, title2 in paired_plots:
                            fig1 = plot1.draw()
                            fig2 = plot2.draw()
                
                            fig1.set_size_inches(6, 4)
                            fig2.set_size_inches(6, 4)
                
                            buf1 = BytesIO()
                            buf2 = BytesIO()
                            fig1.savefig(buf1, format='png', dpi=300, bbox_inches='tight')
                            fig2.savefig(buf2, format='png', dpi=300, bbox_inches='tight')
                            plt.close(fig1)
                            plt.close(fig2)
                
                            buf1.seek(0)
                            buf2.seek(0)
                            img1 = Image.open(buf1)
                            img2 = Image.open(buf2)
                
                            h = max(img1.height, img2.height)
                            img1 = img1.resize((int(img1.width * h / img1.height), h))
                            img2 = img2.resize((int(img2.width * h / img2.height), h))
                
                            combined = Image.new("RGB", (img1.width + img2.width, h), (255, 255, 255))
                            combined.paste(img1, (0, 0))
                            combined.paste(img2, (img1.width, 0))
                
                            fig, ax = plt.subplots(figsize=(12, h / 100))
                            ax.axis('off')
                            ax.imshow(combined)
                            pdf.savefig(fig, bbox_inches='tight')
                            plt.close(fig)
                
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
            
            except Exception as e:
                st.warning("Choose a location on the map.")
                st.error(str(e))  # Optional: for debugging
            
        else:
            if map_data is None:
                st.sidebar.warning("Please select a point on the map before clicking 'Get Data'.")
                    

            


# with tab_map["Definitions"]:
#     if default_tab == "Definitions":
#          # Render header with logos
#         render_header()
        
#         # Main title and subtitle
#         st.markdown("<h1 class='main-title'>Definitions</h1>", unsafe_allow_html=True)

#         render_definitions()

#         jump_to = st.query_params.get("jump_to")
#         if jump_to:
#             st.markdown(f"""
#                 <script>
#                     // Delay scroll to anchor after full render
#                     window.addEventListener("load", function() {{
#                         setTimeout(function() {{
#                             var el = document.getElementById("{jump_to}");
#                             if (el) {{
#                                 el.scrollIntoView({{ behavior: "smooth", block: "start" }});
#                                 // Optional: clean up the hash from the URL
#                                 history.replaceState(null, "", window.location.pathname + window.location.search);
#                             }}
#                         }}, 500);
#                     }});
#                 </script>
#             """, unsafe_allow_html=True)
        
#         # Close container
#         st.markdown('</div>', unsafe_allow_html=True)
        
#         # Render footer
#         render_footer()

with tab_map["Definitions"]:
    if default_tab == "Definitions":
        jump_to = st.query_params.get("jump_to")

        # Optional: Go back button at top
        if st.button("⬅️ Back to GDE Explorer"):
            st.query_params.tab = "GDE Explorer"
            st.query_params.jump_to = None
            st.rerun()

        render_header()
        st.markdown("<h1 class='main-title'>Definitions</h1>", unsafe_allow_html=True)

        render_definitions()

        if not jump_to:
            # Fallback: try to grab from the URL hash if not passed as query param
            st.markdown("""
                <script>
                    const hash = window.location.hash;
                    if (hash && hash.length > 1) {
                        const anchorId = hash.substring(1);
                        const interval = setInterval(function() {
                            const el = document.getElementById(anchorId);
                            if (el) {
                                el.scrollIntoView({ behavior: "smooth", block: "start" });
                                clearInterval(interval);
                                // Optionally remove hash from URL
                                history.replaceState(null, "", window.location.pathname + window.location.search);
                            }
                        }, 100);
                    }
                </script>
            """, unsafe_allow_html=True)
        else:
            # Jump using query param method (from info button)
            st.markdown(f"""
                <script>
                    const anchorId = "{jump_to}";
                    const interval = setInterval(function() {{
                        const el = document.getElementById(anchorId);
                        if (el) {{
                            el.scrollIntoView({{ behavior: "smooth", block: "start" }});
                            clearInterval(interval);
                            history.replaceState(null, "", window.location.pathname + window.location.search);
                        }}
                    }}, 100);
                </script>
            """, unsafe_allow_html=True)


        st.markdown('</div>', unsafe_allow_html=True)
        render_footer()

