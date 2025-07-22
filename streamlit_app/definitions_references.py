definitions_text = """\

<b>DEFINITIONS</b><br/><br/>

<b>Groundwater Boundaries:</b><br/>
Nevada has 256 hydrographic areas that are defined by the State Engineer’s Office for administering groundwater. These were developed in the 1960s and are the basis for water planning, management and administration of water in Nevada. 
[Source for definition: Nevada Division of Water Planning, 1999; Source of data layer: <a href="https://data-ndwr.hub.arcgis.com/datasets/NDWR::basins-state-engineer-admin-boundaries/about/" color="blue">https://data-ndwr.hub.arcgis.com/datasets/NDWR::basins-state-engineer-admin-boundaries/about/</a>]<br/><br/>

<b>Soil Texture:</b><br/>
Soil texture refers to the proportion of sand, silt and clay particles in the soil. This can influence the ease of working with the soil, the amount of water and air the soil holds, and the rate at which water enters and moves through the soil.
[Source for definition: Food and Agriculture Organization, 2006; Source of data layer: Walkinshaw et all (2020)]<br/><br/>

<b>Average annual precipitation (1991-2020) (P):</b><br/>
The average precipitation for the area in question is calculated by summing the observed annual precipitation over 1991-2020 and dividing by the number of years for which there were observations. 
[Source of data: Abatzoglou (2013)]<br/><br/>

<b>Average annual potential evapotranspiration (1991-2020) (PET):</b><br/>
Potential evapotranspiration gives an indication of how “thirsty” the atmosphere is. Here, it is represented as the American Society of Civil Engineers’ Grass Reference Evapotranspiration (ETref), calculated using the Penman-Monteith method. ETref is the amount of water that would evaporate or be transpired from a well-watered grass surface. 
[Source of data: Abatzoglou (2013)]<br/><br/>

<b>Average annual potential water deficit (1991-2020) (PWD):</b><br/>
The potential water deficit (PWD) represents the difference between annual precipitation (supply) and annual potential evapotranspiration (demand). Negative values indicate that there is more demand for water from the atmosphere than is available from precipitation.  PWD is calculated by subtracting potential evapotranspiration from precipitation for a given area. The average annual PWD is calculated by summing observations of annual PWD over 1991-2020 and dividing by the number of years for which there were observations.<br/><br/>

<b>Rooting Depth:</b><br/>
Groundwater-dependent vegetation can access groundwater through their roots, but rooting depths vary. Meadow and rangeland grasses often have roots within 2 m of the ground surface, whereas some phreatophytic shrubs and trees can have roots as deep as 6 m or more (The Nature Conservancy 2021). Choose from 0.5 m for herbaceous meadow root depths, 2 m for grass root depth, and 3.6 m for phreatophyte shrubland root depths.<br/><br/>

<b>Leaf Area Index (LAI):</b><br/>
Leaf area index (LAI) represents the amount of leaf area in an ecosystem and is related to the amount of photosynthesis, evapotranspiration and productivity of an area of interest. LAI is the one-sided green leaf area per unit of ground surface area, and its value can be an indication of the health of an ecosystem (Fang et al. 2019).

We have assumed a typical target LAI for a phreatophytic shrubland in Nevada to be 1, whereas a meadow in Nevada would have a typical target LAI of 2, as shown in examples below (LAI data source: <a href="https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD15A3H/" color="blue">https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD15A3H/</a>)<br/><br/>

<b>Average Actual Evapotranspiration (1991-2020):</b><br/>
Actual evapotranspiration (Actual ET)) is the actual amount of water that is evapotranspired and is limited by the amount of available water. It is always less than or equal to Potential ET.<br/><br/>

<b>Groundwater Component of Evapotranspiration (ETgw):</b><br/>
The groundwater component of evapotranspiration is the portion of total evapotranspiration that is extracted from groundwater (i.e., the saturated zone). The remainder of transpiration comes from the vadose (i.e., the unsaturated) zone. If the water table were deeper, the groundwater component might be reduced. The groundwater component is a good indicator of how much groundwater is used by GDEs when calculating the water budget of a groundwater system.<br/><br/>

<b>Groundwater Subsidy:</b><br/>
Groundwater subsidy is the additional water available in the vadose (i.e., unsaturated) zone for root water uptake resulting from shallow water table conditions. It is a hypothetical quantity that cannot be measured in the field but is a good indicator of how much GDEs in water-limited environments might benefit from shallow groundwater conditions that reduces the water stress experienced by vegetation.<br/><br/><br/><br/>


<b>DISCLAIMERS:</b><br/><br/>

This map tool presents results of modeling for Reclamation Applied Science project R19AP00278 
<i>Quantifying Environmental Water Requirements for Groundwater Dependent Ecosystems for Resilient Water Management</i>. 
See <a href="https://www.conservationgateway.org/ConservationByGeography/NorthAmerica/UnitedStates/nevada/water/Pages/Quantifying-water-requirements-for-GDEs.aspx" color="blue">this link</a> to find out more about the project. 
The paper describing the methods for the modeling is still in preparation, but an overview is available on the 
<a href="https://www.conservationgateway.org/ConservationByGeography/NorthAmerica/UnitedStates/nevada/water/Documents/ModelingUpdate_Watersmart_Workshop3_forpdf.pdf" color="blue">Nevada TNC website (here)</a>.<br/><br/>

This dataset does not prove or make any claim about the nature and/or extent of groundwater levels or groundwater-dependent ecosystems (GDEs) for any mapped location. 
The dataset is non-regulatory and no information presented here is intended to imply whether a project can or should be approved or denied, and the data are not legally binding in any way. 
This tool does not replace the need for field surveys or agency consultation to determine water level status, presence of GDEs, or impacts of groundwater use or climate.<br/><br/>

This tool does not contain bias in favor or against any one form of conservation or land use development. 
This tool does not preempt the authority of local land use agencies.<br/><br/>

Features mapped here are not intended for legal uses and no warranty, expressed or implied, is made by The Nature Conservancy or data contributors as to the accuracy of the data. 
The Nature Conservancy shall not be held liable for improper or incorrect use of the data described and/or contained herein.<br/><br/>

Any sale, distribution, loan, or offering for use of these data, in whole or in part, is prohibited. 
The use of these data to produce other products and services with the intent to use or sell for a profit is prohibited. 
All parties receiving these data must be informed of these restrictions. 
This is an aggregate dataset with multiple data contributors.<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>


<b>REFERENCES:</b><br/><br/><br/>

Abatzoglou JT. 2013. Development of gridded surface meteorological data for ecological applications and modelling. Int. J. Climatol. 33: 121–131. 
Available at <a href="http://onlinelibrary.wiley.com/doi/10.1002/joc.3413/full" color="blue">http://onlinelibrary.wiley.com/doi/10.1002/joc.3413/full</a><br/><br/>

Fang, H., Baret, F., Plummer, S., & Schaepman-Strub, G. (2019). An overview of global leaf area index (LAI): Methods, products, validation, and applications. Reviews of Geophysics, 57, 739–799. 
Available at <a href="https://doi.org/10.1029/2018RG000608" color="blue">https://doi.org/10.1029/2018RG000608</a><br/><br/>

Food and Agriculture Organization. 2006. Soil Texture. 
Available at <a href="https://www.fao.org/fishery/static/FAO_Training/FAO_Training/General/x6706e/x6706e06.htm" color="blue">https://www.fao.org/fishery/static/FAO_Training/FAO_Training/General/x6706e/x6706e06.htm</a><br/><br/>

Lowry, C. S., and S. P. Loheide II (2010), Groundwater-dependent vegetation: Quantifying the groundwater subsidy, Water Resour. Res., 46, W06202. <a href="https://doi.org/10.1029/2009WR008874" color="blue">https://doi.org/10.1029/2009WR008874</a><br/><br/>

Nevada Division of Water Planning. 1999. Nevada State Water Plan. Carson City: Department of Conservation and Natural Resources, Nevada Division of Water Planning. 
Available at <a href="https://water.nv.gov/library/water-planning-reports" color="blue">https://water.nv.gov/library/water-planning-reports</a><br/><br/>

The Nature Conservancy. 2021. Plant Rooting Depth Database. 
Available at <a href="https://www.groundwaterresourcehub.org/where-we-work/california/plant-rooting-depth-database/" color="blue">https://www.groundwaterresourcehub.org/where-we-work/california/plant-rooting-depth-database/</a><br/><br/>

Walkinshaw M, O’Geen AT, Beaudette DE. 2020. Soil Properties. California Soil Resource Lab. 
Available at <a href="https://casoilresource.lawr.ucdavis.edu/soil-properties/" color="blue">https://casoilresource.lawr.ucdavis.edu/soil-properties/</a>
"""
