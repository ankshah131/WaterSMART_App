definitions_text = """\

DEFINITIONS

Groundwater Boundaries:
Nevada has 256 hydrographic areas that are defined by the State Engineer’s Office for administering groundwater. These were developed in the 1960s and are the basis for water planning, management and administration of water in Nevada. 
[Source for definition: Nevada Division of Water Planning, 1999; Source of data layer:
https://data-ndwr.hub.arcgis.com/datasets/NDWR::basins-state-engineer-admin-boundaries/about

Soil Texture:
Soil texture refers to the proportion of sand, silt and clay particles in the soil. This can influence the ease of working with the soil, the amount of water and air the soil holds, and the rate at which water enters and moves through the soil.
[Source for definition: Food and Agriculture Organization, 2006; Source of data layer: Walkinshaw et all (2020)]

Average annual precipitation (1991-2020) (P):
The average precipitation for the area in question is calculated by summing the observed annual precipitation over 1991-2020 and dividing by the number of years for which there were observations. 
[Source of data: Abatzoglou (2013)]

Average annual potential evapotranspiration (1991-2020) (PET)
Potential evapotranspiration gives an indication of how “thirsty” the atmosphere is. Here, it is represented as the American Society of Civil Engineers’ Grass Reference Evapotranspiration (ETref), calculated using the Penman-Monteith method. 
ETref is the amount of water that would evaporate or be transpired from a well-watered grass surface. [Source of data: Abatzoglou (2013)]

Average annual potential water deficit (1991-2020) (PWD)
The potential water deficit (PWD) represents the difference between annual precipitation (supply) and annual potential evapotranspiration (demand). Negative values indicate that there is more demand for water from the atmosphere than is available from precipitation.  PWD is calculated by subtracting potential evapotranspiration from precipitation for a given area.
The average annual PWD is calculated by summing observations of annual PWD over 1991-2020 and dividing by the number of years for which there were observations.

Soil texture
The soil texture from Walkinshaw et al. (2020) is the default choice for the area in question. Select another soil texture to see how it could affect results. Soils with different amounts of sand, silt, and clay have differing abilities to retain water, some drain away instantly, and some also hold onto It more tightly when dry, like a clay, which can limit plant access to that water

Rooting Depth:
Groundwater-dependent vegetation can access groundwater through their roots, but rooting depths vary. Meadow and rangeland grasses often have roots within 2 m of the ground surface, whereas some phreatophytic shrubs and trees can have roots as deep as 6 m or more (The Nature Conservancy 2021). 
Choose from 0.5 m for herbaceous meadow root depths, 2 m for grass root depth, and 3.6 m for phreatophyte shrubland root depths.

Leaf Area Index (LAI)
Leaf area index (LAI) represents the amount of leaf area in an ecosystem and is related to the amount of photosynthesis, evapotranspiration and productivity of an area of interest. 
\LAI is the one-sided green leaf area per unit of ground surface area, and its value can be an indication of the health of an ecosystem (Fang et al. 2019). 
We have assumed a typical target LAI for a phreatophytic shrubland in Nevada to be 1, whereas a meadow in Nevada would have a typical target LAI of 2, as shown in examples below (LAI data source: https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD15A3H)


ET from Groundwater (ETgw):
The groundwater component of evapotranspiration is the portion of total evapotranspiration that is extracted directly from groundwater. 
The remainder of transpiration comes from the vadose zone. If the water table were deeper, the groundwater component might be reduced. 
The groundwater component is a good indicator of how much groundwater is used by GDEs when calculating the water budget of a groundwater system.

Groundwater Subsidy:
Groundwater subsidy is the additional water available for root water uptake resulting from shallow water table conditions. It is a hypothetical quantity that cannot be measured in the field but is a good indicator of how much GDEs in water-limited environments might benefit from shallow groundwater conditions that reduces the water stress experienced by vegetation.
DISCLAIMERS:
This modeling tool does not replace field surveys. Non-regulatory. Not legally binding.
Project: Reclamation Applied Science R19AP00278
Overview: Nevada TNC
https://www.groundwaterresourcehub.org

REFERENCES:

Abatzoglou, J.T. (2013). Development of gridded surface meteorological data.
https://onlinelibrary.wiley.com/doi/10.1002/joc.3413/full

Fang, H., Baret, F., et al. (2019). Global Leaf Area Index (LAI) overview.
https://doi.org/10.1029/2018RG000608

FAO (2006). Soil Texture Guide.
https://www.fao.org/fishery/static/FAO_Training/General/x6706e/x6706e06.htm

Nevada Division of Water Planning (1999). Nevada State Water Plan.
https://water.nv.gov/library/water-planning-reports

The Nature Conservancy (2021). Plant Rooting Depth Database.
https://www.groundwaterresourcehub.org/where-we-work/california/plant-rooting-depth-database/

Walkinshaw et al. (2020). California Soil Resource Lab.
https://casoilresource.lawr.ucdavis.edu/soil-properties/
"""
