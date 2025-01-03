
library(dplyr)
library(lubridate)
library(tidyr)
library(ggplot2)
library(stringr)

####climate time series from 10 locations, mixed effects regression predictors, coefficients, and outputs 
dfsum<-read.csv("Desktop/Christine_DataVis/MixedEffectsModel_filtered_results_102924_clean.csv")

##filter for pulling climate timeseries from a location
climsites<-unique(dfsum$loc)[c(1,2,4,9)]

##water table depths
wtds<-unique(dfsum$wtd)

##soil types
soiltypes<-unique(dfsum$soiltype)

##root depths
rtds<-unique(dfsum$rootdepth)

s=1
r=1
d=1
cs<-climsites[s]
st<-soiltypes[r]
rd<-rtds[d]

if(rd==0.5){laithresh<-1.5}
if(rd==2){laithresh<-2}
if(rd==3.6){laithresh<-1}
    
############# plot lai
lai<- dfsum %>% 
  filter(loc==cs, rootdepth==rd, soiltype ==st)
laisum<-lai %>% 
  group_by(wtd2) %>% 
  filter(LAIcalc>=laithresh) %>% 
  summarise(noverthresh = n()) 
lai2<-left_join(lai, laisum)
lai2$noverthresh<-ifelse(is.na(lai2$noverthresh),0,lai2$noverthresh)
lai2$percoverthresh<-round(lai2$noverthresh/21,2)*100

p_lai1 <- ggplot(data=lai2)+
  geom_line(aes(wy,LAIcalc, linetype=wtd2))+
  geom_point(aes(wy,LAIcalc, color=wb*100))+
  geom_hline(aes(yintercept=laithresh), alpha=0.5)+
  geom_text(aes(y=laithresh+.1, x=2007), label=paste0("Example Management Target, LAI=",laithresh))+
  theme_bw()+
  scale_color_distiller(palette="YlGnBu", direction=1)+
  ggtitle(paste0("Location: ", cs, ", Root Depth: ", rd, "m, Soil Type: ", st))+
  labs(x="Water Year", y="Annual Maximum Leaf Area Index (LAI)", color="Annual Potential\nWater Deficit (mm)", linetype="Water Table Depth")

ggsave(paste0("Desktop/Christine_DataVis/",cs,st,rd,"rootdepth_timeseries_LAI.png"),p_lai1, bg="white", height=4, width=6, units="in", device="png")
 
p_lai2 <- ggplot(data=lai2)+
  geom_boxplot(aes(wtd,LAIcalc))+
  geom_point(aes(wtd,LAIcalc, color=wb*100))+
  geom_hline(aes(yintercept=laithresh), alpha=0.5)+
  geom_text(aes(y=laithresh, x=wtd, label=percoverthresh), vjust="bottom")+
  geom_text(aes(y=laithresh, x=2), label=paste0("% Years over Management Target, LAI=",laithresh), vjust="top")+
  theme_bw()+
  scale_color_distiller(palette="YlGnBu", direction=1)+
  ggtitle(paste0("Location: ", cs, ", Root Depth: ", rd, "m, Soil Type: ", st))+
  labs(x="Water Table Depth", y="Annual Maximum Leaf Area Index (LAI)", color="Annual Potential\nWater Deficit (mm)")

ggsave(paste0("Desktop/Christine_DataVis/",cs,st,rd,"rootdepth_boxplot_LAI.png"),p_lai2, bg="white", height=4, width=6, units="in", device="png")
  
################ plot aet
aet<-dfsum %>% filter(loc==cs, rootdepth==rd, soiltype ==st)
aetsum<-aet %>% group_by(wtd2) %>% summarise(min=min(aetcalc, na.rm=TRUE), max=max(aetcalc, na.rm=TRUE)) 
aet2<-left_join(aet, aetsum)
aet2$min<-round(aet2$min,0)
aet2$max<-round(aet2$max,0)
aet2$rangelab<-paste0(aet2$min,"-", aet2$max)
charttop<-aet2$max
  
p_aet1 <- ggplot(aet2)+
  geom_line(aes(wy,aetcalc, linetype=wtd2))+
  geom_point(aes(wy,aetcalc, color=wb*100))+
  theme_bw()+
  scale_color_distiller(palette="YlGnBu", direction=1)+
  ggtitle(paste0("Location: ", cs, ", Root Depth: ", rd, "m, Soil Type: ", st))+
  labs(x="Water Year", y="Annual Actual Evapotranspiration-Total (mm)", color="Annual Potential\nWater Deficit (mm)", linetype="Water Table Depth")
  
ggsave(paste0("Desktop/Christine_DataVis/",cs,st,rd,"rootdepth_timeseries_totalET.png"),p_aet1, bg="white", height=4, width=6, units="in", device="png")
  
p_aet2 <- ggplot(data=aet2)+
  geom_boxplot(aes(wtd,aetcalc))+
  geom_point(aes(wtd,aetcalc, color=wb*100))+
  geom_text(aes(wtd,charttop,label=rangelab), vjust="bottom")+
  theme_bw()+
  scale_color_distiller(palette="YlGnBu", direction=1)+
  ggtitle(paste0("Location: ", cs, ", Root Depth: ", rd, "m, Soil Type: ", st))+
  labs(x="Water Table Depth", y="Annual Actual Evapotranspiration- Total (mm)", color="Annual Potential\nWater Deficit (mm)")

ggsave(paste0("Desktop/Christine_DataVis/",cs,st,rd,"rootdepth_boxplot_totalET.png"),p_aet2, bg="white", height=4, width=6, units="in", device="png")
  
  
################ plot gwsubs
gwsubs<-dfsum %>% 
  filter(loc==cs, rootdepth==rd, soiltype ==st,wtd2!="Free Drain")

gwsubssum<-gwsubs %>% 
  group_by(wtd2) %>% 
  summarise(min=min(gwsubscalc, na.rm=TRUE), max=max(gwsubscalc, na.rm=TRUE), minperc=min(gwsubscalc/aetcalc, na.rm=TRUE), maxperc=max(gwsubscalc/aetcalc, na.rm=TRUE)) 
  
gwsubs2<-left_join(gwsubs, gwsubssum)
gwsubs2$min<-round(gwsubs2$min,0)
gwsubs2$max<-round(gwsubs2$max,0)
gwsubs2$rangelab<-paste0(gwsubs2$min,"-", gwsubs2$max)
charttop<-gwsubs2$max
  
gwsubs2$minperc<-round(gwsubs2$minperc*100,0)
gwsubs2$maxperc<-round(gwsubs2$maxperc*100,0)
gwsubs2$rangelabperc<-paste0(gwsubs2$minperc,"-",gwsubs2$maxperc,"% of Actual ET")
  
p_gwsubs1 <- ggplot(data=gwsubs2)+
  geom_line(aes(wy,gwsubscalc, linetype=wtd2))+
  geom_point(aes(wy,gwsubscalc, color=wb*100))+
  theme_bw()+
  scale_color_distiller(palette="YlGnBu", direction=1)+
  ggtitle(paste0("Location: ", cs, ", Root Depth: ", rd, "m, Soil Type: ", st))+
  labs(x="Water Year", y="Annual Groundwater Subsidy (mm)", color="Annual Potential\nWater Deficit (mm)", linetype="Water Table Depth")
  
ggsave(paste0("Desktop/Christine_DataVis/",cs,st,rd,"rootdepth_timeseries_GWsubsET.png"),p_gwsubs1, bg="white", height=4, width=6, units="in", device="png")

p_gwsubs2 <- ggplot(data=gwsubs2)+
  geom_boxplot(aes(wtd,gwsubscalc))+
  geom_point(aes(wtd,gwsubscalc, color=wb*100))+
  geom_text(aes(wtd,charttop,label=rangelabperc), vjust="bottom")+
  theme_bw()+
  scale_color_distiller(palette="YlGnBu", direction=1)+
  ggtitle(paste0("Location: ", cs, ", Root Depth: ", rd, "m, Soil Type: ", st))+
  labs(x="Water Table Depth", y="Annual Groundwater Subsidy (mm)", color="Annual Potential\nWater Deficit (mm)")
  
ggsave(paste0("Desktop/Christine_DataVis/",cs,st,rd,"rootdepth_boxplot_GWsubsET.png"),p_gwsubs2, bg="white", height=4, width=6, units="in", device="png")
 
  