import streamlit as st

def load_css():
    """Inject custom CSS directly."""
    st.markdown("""
    <style>
    :root {
        --primary-color: #2c3e50;
        --secondary-color: #18bc9c;
        --accent-color: #1f8a70;
        --text-color: #2c3e50;
        --background-color: #ecf0f1;
        --muted-text: #7f8c8d;
        --border-color: #bdc3c7;
        --light-bg: #f5f7fa;
        --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    }

    * {
        font-family: var(--font-family);
        box-sizing: border-box;
        transition: all 0.3s ease;
    }

    body {
        color: var(--text-color);
        background-color: var(--background-color);
        line-height: 1.6;
        margin: 0;
        padding: 0;
    }

    a {
        color: var(--secondary-color);
        text-decoration: none;
        position: relative;
    }

    a::after {
        content: "";
        position: absolute;
        left: 0;
        bottom: -2px;
        width: 0;
        height: 2px;
        background-color: var(--secondary-color);
        transition: width 0.3s ease;
    }

    a:hover::after {
        width: 100%;
    }

    a:hover {
        color: var(--accent-color);
    }

    .main-title {
        color: var(--primary-color);
        font-weight: 700;
        font-size: 2.2rem;
        margin: 1rem 0 0.5rem;
        text-align: center;
        letter-spacing: -0.5px;
    }

    .subtitle {
        color: var(--text-color);
        font-weight: 500;
        font-size: 1.5rem;
        margin-bottom: 2rem;
        text-align: center;
        letter-spacing: -0.3px;
    }

    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 1rem;
    }

    .logo-container img {
        max-height: 60px;
        width: auto;
        margin: 0 10px;
    }

    .definition-header {
        color: var(--primary-color);
        font-weight: 600;
        font-size: 1.35rem;
        margin: 2.5rem 0 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--border-color);
        scroll-margin-top: 80px;
    }

    .definition-content {
        margin-bottom: 1.5rem;
        line-height: 1.6;
        font-size: 0.9rem;
        color: var(--text-color);
    }

    .quick-links {
        background-color: var(--light-bg);
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        line-height: 1.8;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }

    .quick-links a {
        color: var(--secondary-color);
        margin-right: 8px;
        font-size: 0.9rem;
        font-weight: 500;
    }

    .image-container {
        display: flex;
        justify-content: center;
        margin: 1.5rem 0;
    }

    img {
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        max-width: 100%;
        height: auto;
    }

    .small-image {
        max-width: 100px;
    }

    .medium-image {
        max-width: 200px;
    }

    .large-image {
        max-width: 200px;
    }

    .image-caption {
        text-align: center;
        font-style: italic;
        color: var(--muted-text);
        margin-top: 0.5rem;
        font-size: 0.85rem;
    }

    .disclaimer-content, .references-content {
        background-color: var(--background-color);
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid var(--primary-color);
        margin-bottom: 2rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
    }

    .disclaimer-content p, .references-content p {
        margin-bottom: 1rem;
        line-height: 1.6;
        font-size: 0.85rem;
    }

    .references-content a {
        color: var(--secondary-color);
        word-break: break-word;
    }

    .footer {
        text-align: center;
        color: var(--muted-text);
        font-size: 0.85rem;
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid var(--border-color);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        font-size: 16px;
        color: var(--primary-color);
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background-color: rgba(44, 63, 80, 0.1);
        border-radius: 5px 5px 0 0;
    }

    .definition-card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid var(--border-color);
    }

    @media (max-width: 768px) {
        .main-title { font-size: 1.8rem; }
        .subtitle { font-size: 1.3rem; }
        .definition-header { font-size: 1.2rem; }
        .small-image, .medium-image, .large-image { max-width: 100%; }
    }
    </style>
    """, unsafe_allow_html=True)
    

def render_definition_section(title, content, image=None, image_caption=None, image_size="medium", section_id=None):
    """
    Render a definition section with optional image, placing the image to the right of the content.
    
    Args:
        title (str): Section title
        content (str): HTML content for the section
        image (str): Path to image file (optional)
        image_caption (str): Caption for the image (optional)
        image_size (str): Size of image ("small", "medium", or "large", default is "medium")
        section_id (str): HTML id for the section to create anchor links
    """
    # Add an anchor for this section
    if section_id:
        st.markdown(f"<div id='{section_id}'></div>", unsafe_allow_html=True)
    
    # Render title with styling
    st.markdown(f"<h3 class='definition-header'>{title}</h3>", unsafe_allow_html=True)

    if image:
        col1, col2 = st.columns([3, 1]) 

        with col1:
            st.markdown(f"<div class='definition-card'> <div class='disclaimer-content'> <div class='definition-content'>{content}</div></div></div>", unsafe_allow_html=True)

        with col2:
            st.image(image)
            if image_caption:
                st.markdown(f"<p class='image-caption'>{image_caption}</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='definition-card'> <div class='disclaimer-content'> <div class='definition-content'>{content}</div></div></div>", unsafe_allow_html=True)
    
    # Add some spacing between sections
    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)


def render_definitions():
    """
    Render all definition topics on a single page with anchor links navigation.
    """
    # Load CSS
    load_css()
    
    # Introduction section
    st.markdown("<h2>Definitions</h2>", unsafe_allow_html=True)
    st.markdown("""
        <div class="intro-section">
            <p>This page provides definitions and explanations for key terms used in groundwater management and hydrology.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Define all topics including disclaimers and references
    topics = [
        {"id": "groundwater-boundaries", "title": "Groundwater Boundaries"},
        {"id": "soil-texture", "title": "Soil Texture"},
        {"id": "precipitation", "title": "Precipitation"},
        {"id": "evapotranspiration", "title": "Evapotranspiration"},
        {"id": "water-deficit", "title": "Water Deficit"},
        #{"id": "soil-texture-selection", "title": "Soil Texture (Selection)"},
        {"id": "rooting-depth", "title": "Rooting Depth"},
        {"id": "leaf-area-index", "title": "Leaf Area Index"},
        {"id": "actual-et", "title": "Average Actual Evapotranspiration"},
        {"id": "etgw", "title": "Groundwater Component of ET (ETgw)"},
        {"id": "groundwater-subsidy", "title": "Groundwater Subsidy"},
        {"id": "disclaimers", "title": "Disclaimers"},
        {"id": "references", "title": "References"}
    ]
    
    # Create a table of contents with anchor links
    st.markdown("<h3>Jump to Section:</h3>", unsafe_allow_html=True)
    
    # Use columns to create a multi-column layout for the table of contents
    col1, col2, col3 = st.columns(3)
    
    # Calculate the number of items per column for even distribution
    items_per_column = len(topics) // 3
    remainder = len(topics) % 3
    
    # First column of links
    with col1:
        end_idx = items_per_column + (1 if remainder > 0 else 0)
        for topic in topics[:end_idx]:
            st.markdown(f"<a href='#{topic['id']}' target='_self'>{topic['title']}</a>", unsafe_allow_html=True)
    
    # Second column of links
    with col2:
        start_idx = end_idx
        end_idx = start_idx + items_per_column + (1 if remainder > 1 else 0)
        for topic in topics[start_idx:end_idx]:
            st.markdown(f"<a href='#{topic['id']}' target='_self'>{topic['title']}</a>", unsafe_allow_html=True)
    
    # Third column of links
    with col3:
        for topic in topics[end_idx:]:
            st.markdown(f"<a href='#{topic['id']}' target='_self'>{topic['title']}</a>", unsafe_allow_html=True)
    
    # Add separator after table of contents
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Add JavaScript to handle anchor links scrolling correctly in Streamlit
    st.markdown("""
    <script>
    // Function to scroll to the element with the given ID
    function scrollToElement(id) {
        const element = document.getElementById(id);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth' });
        }
    }
    
    // Check for hash in URL and scroll to that element when page loads
    window.addEventListener('load', function() {
        if (window.location.hash) {
            const id = window.location.hash.substring(1);
            setTimeout(function() {
                scrollToElement(id);
            }, 500); // Short delay to ensure Streamlit content is loaded
        }
    });
    </script>
    """, unsafe_allow_html=True)
    
    # Administrative groundwater boundaries
    render_definition_section(
        "Administrative Groundwater Boundaries",
        """Nevada has 256 hydrographic areas that are defined by the State Engineer’s Office for administering groundwater. 
        These were developed in the 1960s and are the basis for water planning, management and administration of water in Nevada.  
        <span class="source-text">[Source: Nevada Division of Water Planning, 1999; Data: <a href="https://data-ndwr.hub.arcgis.com/datasets/NDWR::basins-state-engineer-admin-boundaries/about" target="_blank">
        Nevada Division of Water Resources</a>]</span>""",
        section_id="groundwater-boundaries"
    )
    
    # Soil texture
    render_definition_section(
        "Soil Texture",
        """Soil texture refers to the proportion of sand, silt, and clay particles in the soil.  
        This can influence the ease of working with the soil, the amount of water and air the soil holds, and the rate at which water enters and moves through the soil. 
        <span class="source-text">[Source for definition: Food and Agriculture Organization, 2006; Source of data layer: Walkinshaw et all (2020)]</span>
        Select soil textures to explore how different proportions of sand, silt, and clay influence the soil's ability to retain water. For example, clay can hold water more tightly, limiting plant access when dry.""",
        "https://raw.githubusercontent.com/ankshah131/WaterSMART_App/46955734559a0046773e492b70d013737377c1ec/streamlit_app/app_def/assets/images/soil_texture.png", 
        "Soil Texture Example",
        image_size="medium",
        section_id="soil-texture"
    )
    
    # Precipitation
    render_definition_section(
        "Average Annual Precipitation (1991-2020)",
        """The average precipitation for the area in question is calculated by summing the observed annual precipitation 
        over 1991-2020 and dividing by the number of years for which there were observations.
        <span class="source-text">[Source: Abatzoglou, 2013]</span>""",
        section_id="precipitation"
    )
    
    # Evapotranspiration
    render_definition_section(
        "Average Annual Potential Evapotranspiration (1991-2020)",
        """Potential evapotranspiration gives an indication of how “thirsty” the atmosphere is.
        Here, it is represented as the American Society of Civil Engineers’ Grass Reference Evapotranspiration (ETref), calculated using the Penman-Monteith method.
        ETref is the amount of water that would evaporate or be transpired from a well-watered grass surface.""",
        "https://raw.githubusercontent.com/ankshah131/WaterSMART_App/2a98d82114927e7ebd5facfbf7b0351a88d6ae64/streamlit_app/app_def/assets/images/et_ref.png",
        "ETref Example",
        image_size="small",
        section_id="evapotranspiration"
    )
    
    # Water deficit
    render_definition_section(
        "Average Annual Potential Water Deficit (1991-2020)",
        """The potential water deficit (PWD) represents the difference between annual precipitation (supply) and annual potential evapotranspiration (demand).
       Negative values indicate that there is more demand for water from the atmosphere than is available from precipitation. 
       PWD is calculated by subtracting potential evapotranspiration from precipitation for a given area.
       The average annual PWD is calculated by summing observations of annual PWD over 1991-2020 and dividing by the number of years for which there were observations.""",
        section_id="water-deficit"
    )
    
    # # Soil texture selection
    # render_definition_section(
    #     "Soil Texture Selection",
    #     """Select soil textures to explore how different proportions of sand, silt, and clay influence the soil's ability to retain water. 
    #     For example, clay can hold water more tightly, limiting plant access when dry.""",
    #     "https://raw.githubusercontent.com/ankshah131/WaterSMART_App/46955734559a0046773e492b70d013737377c1ec/streamlit_app/app_def/assets/images/soil_texture.png",
    #     "Soil Texture Example",
    #     image_size="small",
    #     section_id="soil-texture-selection"
    # )
    
    # Rooting depth
    render_definition_section(
        "Rooting Depth",
        """Groundwater-dependent vegetation can access groundwater through their roots, but rooting depths vary. 
        Meadow and rangeland grasses often have roots within 2 m of the ground surface, whereas some phreatophytic shrubs and trees can have roots as deep as 6 m or more (The Nature Conservancy 2021).
        can reach depths of 6m or more. Choose from 0.5 m for herbaceous meadow root depths, 2 m for grass root depth, and 3.6 m for phreatophyte shrubland root depths.""",
        section_id="rooting-depth"
    )
    
    # Leaf area index
    render_definition_section(
        "Leaf Area Index (LAI)",
        """Leaf area index (LAI) represents the amount of leaf area in an ecosystem and is related to the amount of photosynthesis, evapotranspiration and productivity of an area of interest.
        LAI is the one-sided green leaf area per unit of ground surface area, and its value can be an indication of the health of an ecosystem (Fang et al. 2019).
        We have assumed a typical target LAI for a phreatophytic shrubland in Nevada to be 1, whereas a meadow in Nevada would have a typical target LAI of 2, as shown in examples below. 
        <span class="source-text">[LAI Data Source: <a href="https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD15A3H" target="_blank">MODIS</a>]</span>""",
        "https://raw.githubusercontent.com/ankshah131/WaterSMART_App/2a98d82114927e7ebd5facfbf7b0351a88d6ae64/streamlit_app/app_def/assets/images/lai_examples1.png",
        "LAI Examples",
        image_size="medium",
        section_id="leaf-area-index"
    )

    # Actual evapotranspiration
    render_definition_section(
        "Average Actual Evapotranspiration (1991-2020)",
        """Actual evapotranspiration (Actual ET)) is the actual amount of water that is evapotranspired and is limited by the amount of available water. 
        It is always less than or equal to Potential ET.""",
        section_id="actual-et"
    )
    
    
    # Groundwater component of evapotranspiration
    render_definition_section(
        "Groundwater Component of Evapotranspiration (ETgw)",
        """The groundwater component of evapotranspiration is the portion of total evapotranspiration that is extracted from groundwater (i.e., the saturated zone). 
        The remainder of transpiration comes from the vadose (i.e., the unsaturated) zone. If the water table were deeper, the groundwater component might be reduced. 
        The groundwater component is a good indicator of how much groundwater is used by GDEs when calculating the water budget of a groundwater system.""",
        "https://raw.githubusercontent.com/ankshah131/WaterSMART_App/dda06340a021b043ac3c74e4b1dace9b375f01e0/streamlit_app/app_def/assets/images/groundwater_et.png",
        "(Modified from Lowry and Loheide, 2010)",
        image_size="small",
        section_id="etgw"
    )
    
    # Groundwater subsidy
    render_definition_section(
        "Groundwater Subsidy",
        """Groundwater subsidy is the additional water available in the vadose (i.e., unsaturated) zone for root water uptake resulting from shallow water table conditions.
        It is a hypothetical quantity that cannot be measured in the field but is a good indicator of how much GDEs in water-limited 
        environments might benefit from shallow groundwater conditions that reduces the water stress experienced by vegetation.""",
        "https://raw.githubusercontent.com/ankshah131/WaterSMART_App/2a98d82114927e7ebd5facfbf7b0351a88d6ae64/streamlit_app/app_def/assets/images/groundwater_subsidy.png",
        "(Modified from Lowry and Loheide, 2010)",
        image_size="small",
        section_id="groundwater-subsidy"
    )
    
    # Disclaimers section
    st.markdown(
        """
        <div id="disclaimers"></div>
        <div class="definition-card">
            <h3 class='definition-header'>Disclaimers</h3>
            <div class="disclaimer-content">
                <p>This map tool presents results of modeling for Reclamation Applied Science project R19AP00278 Quantifying Environmental Water Requirements for Groundwater Dependent Ecosystems for Resilient Water Management. See <a href="https://www.conservationgateway.org/ConservationByGeography/NorthAmerica/UnitedStates/nevada/water/Pages/Quantifying-water-requirements-for-GDEs.aspx" target="_blank">this link</a> to find out more about the project. The paper describing the methods for the modeling is still in preparation but an overview is available on the Nevada TNC website. This dataset does not prove or make any claim about the nature and/or extent of groundwater levels or groundwater-dependent ecosystems (GDEs) for any mapped location. The dataset is non-regulatory and no information presented here is intended to imply whether a project can or should be approved or denied, and the data are not legally binding in any way. This tool does not replace the need for field surveys or agency consultation to determine water level status, presence of GDEs, or impacts of groundwater use or climate. This tool does not contain bias in favor or against any one form of conservation or land use development. This tool does not preempt the authority of local land use agencies. Features mapped here are not intended for legal uses and no warranty, expressed or implied, is made by The Nature Conservancy or data contributors as to the accuracy of the data. The Nature Conservancy shall not be held liable for improper or incorrect use of the data described and/or contained herein. Any sale, distribution, loan, or offering for use of these data, in whole or in part, is prohibited. The use of these data to produce other products and services with the intent to use or sell for a profit is prohibited. All parties receiving these data must be informed of these restrictions. This is an aggregate dataset with multiple data contributors.</p>
            </div>
        </div>
        <div style='margin-bottom: 30px;'></div>
        """,
        unsafe_allow_html=True
    )
    
    # References section
    st.markdown(
        """
        <div id="references"></div>
        <div class="definition-card">
            <h3 class='definition-header'>References</h3>
            <div class="references-content">
                <p>Abatzoglou JT. 2013. Development of gridded surface meteorological data for ecological applications and modelling. Int. J. Climatol. 33: 121--131. Available at <a href="http://onlinelibrary.wiley.com/doi/10.1002/joc.3413/full" target="_blank">http://onlinelibrary.wiley.com/doi/10.1002/joc.3413/full</a></p>
                <p>Fang, H., Baret, F., Plummer, S., & Schaepman-Strub, G. (2019). An overview of global leaf area index (LAI): Methods, products, validation, and applications. <em>Reviews of Geophysics</em>. 57, 739--799. <a href="https://doi.org/10.1029/2018RG000608" target="_blank">https://doi.org/10.1029/2018RG000608</a></p>
                <p>Food and Agriculture Organization. 2006. Soil Texture. <a href="https://www.fao.org/fishery/static/FAO_Training/FAO_Training/General/x6706e/x6706e06.htm" target="_blank">https://www.fao.org/fishery/static/FAO_Training/FAO_Training/General/x6706e/x6706e06.htm</a></p>
                <p>Lowry, C. S., and S. P. Loheide II (2010), Groundwater-dependent vegetation: Quantifying the groundwater subsidy, Water Resour. Res., 46, W06202, doi:10.1029/2009WR008874</a></p>
                <p>Nevada Division of Water Planning. 1999. Nevada State Water Plan. Carson City: Department of Conservation and Natural Resources, Nevada Division of Water Planning. Available at <a href="https://water.nv.gov/library/water-planning-reports" target="_blank">https://water.nv.gov/library/water-planning-reports</a>.</p>
                <p>The Nature Conservancy. 2021. Plant Rooting Depth Database. Available at <a href="https://www.groundwaterresourcehub.org/where-we-work/california/plant-rooting-depth-database/" target="_blank">https://www.groundwaterresourcehub.org/where-we-work/california/plant-rooting-depth-database/</a>.</p>
                <p>Walkinshaw M, O'Geen AT, Beaudette DE. 2020. Soil Properties. California Soil Resource Lab. Available at <a href="https://casoilresource.lawr.ucdavis.edu/soil-properties/" target="_blank">https://casoilresource.lawr.ucdavis.edu/soil-properties/</a></p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
