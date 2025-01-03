
library(dplyr)
library(lubridate)
library(tidyr)
library(data.table)
library(ggplot2)
library(ggpubr)
library(stringr)
library(RcppRoll)
library(ggpubr)
library(ggpmisc)
library(ggfortify)
library(khroma)


dfclimate<-read.csv('../data/ClimateTimeseries.csv')
dfclimate$wb<-(dfclimate$Precip-dfclimate$PotET)/100
dfclimate$wb2<-dfclimate$wb*dfclimate$wb
dfclimate$wb3<-dfclimate$wb*dfclimate$wb*dfclimate$wb

dfcoeffs<-read.csv('../data/MixedEffectsModelCoefficients102924_LAI_AET_AETG_GWsubs.csv')
dfcoeffs$WTD<-as.numeric(dfcoeffs$WTD)
dfcoeffs$wtd2<-ifelse(dfcoeffs$WTD==12, "Free Drain", paste0(dfcoeffs$WTD," m"))


##filter for pulling climate timeseries from a location
climsites<-unique(dfclimate$loc)[c(1,2,4,9)]

##water table depths
wtds<-unique(dfcoeffs$wtd2)

##soil types
soiltypes<-unique(dfcoeffs$soiltype)

##root depths
rtds<-unique(dfcoeffs$rootdepth)


s=1
r=1
d=1
# for(s in 1: length(climsites)){
  cs<-climsites[s]
  # for(r in 1:length(soiltypes)){
    st<-soiltypes[r]
    # for(d in 1: length(rtds)){
      rd<-rtds[d]
      if(rd==0.5){laithresh<-1.5}
      if(rd==2){laithresh<-2}
      if(rd==3.6){laithresh<-1}
      
    df<-dfclimate %>% filter(loc==cs)
    coeffs<-dfcoeffs %>% filter(soiltype==st, rootdepth==rd)
    df2<-rbind(df,df,df,df)
    df2$WTD<-rep(c(1,3,6,12), each=nrow(df))
    dfsum<-left_join(df2, coeffs)
    
    dfsum$LAIcalc<-dfsum$LAIIntercept+dfsum$wb*dfsum$LAIwbx+dfsum$wb2*dfsum$LAIwb2x+dfsum$wb3*dfsum$LAIwb3x
    dfsum$aetcalc<-dfsum$aetIntercept+dfsum$wb*dfsum$aetwbx+dfsum$wb2*dfsum$aetwb2x+dfsum$wb3*dfsum$aetwb3x
    dfsum$aetgwcalc<-dfsum$aetgwIntercept+dfsum$wb*dfsum$aetgwwbx+dfsum$wb2*dfsum$aetgwwb2x+dfsum$wb3*dfsum$aetgwwb3x
    dfsum$gwsubscalc<-dfsum$gwsubsIntercept+dfsum$wb*dfsum$gwsubswbx+dfsum$wb2*dfsum$gwsubswb2x+dfsum$wb3*dfsum$gwsubswb3x
    
    
    #############plot lai
    lai<-dfsum %>% filter(loc==cs, rootdepth==rd, soiltype ==st)
    laisum<-lai %>% group_by(wtd2) %>% filter(LAIcalc>=laithresh) %>% summarise(noverthresh = n()) 
    lai2<-left_join(lai, laisum)
    lai2$noverthresh<-ifelse(is.na(lai2$noverthresh),0,lai2$noverthresh)
    lai2$percoverthresh<-round(lai2$noverthresh/21,2)*100
    
    # p<-
      ggplot(data=lai2)+
      geom_line(aes(wy,LAIcalc, linetype=wtd2))+
      geom_point(aes(wy,LAIcalc, color=wb*100))+
      geom_hline(aes(yintercept=laithresh), alpha=0.5)+
      geom_text(aes(y=laithresh+.1, x=2007), label=paste0("Example Management Target, LAI=",laithresh))+
      theme_bw()+
      scale_color_distiller(palette="YlGnBu", direction=1)+
      ggtitle(paste0("Location: ", cs, ", Root Depth: ", rd, "m, Soil Type: ", st))+
      labs(x="Water Year", y="Annual Maximum Leaf Area Index (LAI)", color="Annual Potential\nWater Deficit (mm)", linetype="Water Table Depth")
    # ggsave(paste0("C:\\Users\\albano\\OneDrive - Desert Research Institute\\ComsolModels\\RWUModels\\modelcomparisonplots\\AppExamples\\",cs,st,rd,"rootdepth_timeseries_LAI.png"),p, bg="white", height=4, width=6, units="in", device="png")
    
    # p<-
      ggplot(data=lai2)+
      geom_boxplot(aes(wtd2,LAIcalc))+
      geom_point(aes(wtd2,LAIcalc, color=wb*100))+
      geom_hline(aes(yintercept=laithresh), alpha=0.5)+
      geom_text(aes(y=laithresh, x=wtd2, label=percoverthresh), vjust="bottom")+
      geom_text(aes(y=laithresh, x=2), label=paste0("% Years over Management Target, LAI=",laithresh), vjust="top")+
      theme_bw()+
      scale_color_distiller(palette="YlGnBu", direction=1)+
      ggtitle(paste0("Location: ", cs, ", Root Depth: ", rd, "m, Soil Type: ", st))+
      labs(x="Water Table Depth", y="Annual Maximum Leaf Area Index (LAI)", color="Annual Potential\nWater Deficit (mm)")
    # ggsave(paste0("C:\\Users\\albano\\OneDrive - Desert Research Institute\\ComsolModels\\RWUModels\\modelcomparisonplots\\AppExamples\\",cs,st,rd,"rootdepth_boxplot_LAI.png"),p, bg="white", height=4, width=6, units="in", device="png")
    
    ################aet
    aet<-dfsum %>% filter(loc==cs, rootdepth==rd, soiltype ==st)
    aetsum<-aet %>% group_by(wtd2) %>% summarise(min=min(aetcalc, na.rm=TRUE), max=max(aetcalc, na.rm=TRUE)) 
    aet2<-left_join(aet, aetsum)
    aet2$min<-round(aet2$min,0)
    aet2$max<-round(aet2$max,0)
    aet2$rangelab<-paste0(aet2$min,"-", aet2$max)
    charttop<-aet2$max
    
    # p<-
      ggplot(aet2)+
      geom_line(aes(wy,aetcalc, linetype=wtd2))+
      geom_point(aes(wy,aetcalc, color=wb*100))+
      theme_bw()+
      scale_color_distiller(palette="YlGnBu", direction=1)+
      ggtitle(paste0("Location: ", cs, ", Root Depth: ", rd, "m, Soil Type: ", st))+
      labs(x="Water Year", y="Annual Actual Evapotranspiration-Total (mm)", color="Annual Potential\nWater Deficit (mm)", linetype="Water Table Depth")
    # ggsave(paste0("C:\\Users\\albano\\OneDrive - Desert Research Institute\\ComsolModels\\RWUModels\\modelcomparisonplots\\AppExamples\\",cs,st,rd,"rootdepth_timeseries_totalET.png"),p, bg="white", height=4, width=6, units="in", device="png")
    
    # p<-
      ggplot(data=aet2)+
      geom_boxplot(aes(wtd2,aetcalc))+
      geom_point(aes(wtd2,aetcalc, color=wb*100))+
      geom_text(aes(wtd2,charttop,label=rangelab), vjust="bottom")+
      theme_bw()+
      scale_color_distiller(palette="YlGnBu", direction=1)+
      ggtitle(paste0("Location: ", cs, ", Root Depth: ", rd, "m, Soil Type: ", st))+
      labs(x="Water Table Depth", y="Annual Actual Evapotranspiration- Total (mm)", color="Annual Potential\nWater Deficit (mm)")
    # ggsave(paste0("C:\\Users\\albano\\OneDrive - Desert Research Institute\\ComsolModels\\RWUModels\\modelcomparisonplots\\AppExamples\\",cs,st,rd,"rootdepth_boxplot_totalET.png"),p, bg="white", height=4, width=6, units="in", device="png")
    
    
    ################gwsubs
    gwsubs<-dfsum %>% filter(loc==cs, rootdepth==rd, soiltype ==st,wtd2!="Free Drain")
    gwsubssum<-gwsubs %>% group_by(wtd2) %>% summarise(min=min(gwsubscalc, na.rm=TRUE), max=max(gwsubscalc, na.rm=TRUE),
                                                       minperc=min(gwsubscalc/aetcalc, na.rm=TRUE), maxperc=max(gwsubscalc/aetcalc, na.rm=TRUE)) 
    gwsubs2<-left_join(gwsubs, gwsubssum)
    gwsubs2$min<-round(gwsubs2$min,0)
    gwsubs2$max<-round(gwsubs2$max,0)
    gwsubs2$rangelab<-paste0(gwsubs2$min,"-", gwsubs2$max)
    charttop<-gwsubs2$max
    
    gwsubs2$minperc<-round(gwsubs2$minperc*100,0)
    gwsubs2$maxperc<-round(gwsubs2$maxperc*100,0)
    gwsubs2$rangelabperc<-paste0(gwsubs2$minperc,"-",gwsubs2$maxperc,"% of Actual ET")
    
    # p<-
      ggplot(data=gwsubs2)+
      geom_line(aes(wy,gwsubscalc, linetype=wtd2))+
      geom_point(aes(wy,gwsubscalc, color=wb*100))+
      theme_bw()+
      scale_color_distiller(palette="YlGnBu", direction=1)+
      ggtitle(paste0("Location: ", cs, ", Root Depth: ", rd, "m, Soil Type: ", st))+
      labs(x="Water Year", y="Annual Groundwater Subsidy (mm)", color="Annual Potential\nWater Deficit (mm)", linetype="Water Table Depth")
    # ggsave(paste0("C:\\Users\\albano\\OneDrive - Desert Research Institute\\ComsolModels\\RWUModels\\modelcomparisonplots\\AppExamples\\",cs,st,rd,"rootdepth_timeseries_GWsubsET.png"),p, bg="white", height=4, width=6, units="in", device="png")
    
    # p<-
      ggplot(data=gwsubs2)+
      geom_boxplot(aes(wtd2,gwsubscalc))+
      geom_point(aes(wtd2,gwsubscalc, color=wb*100))+
      geom_text(aes(wtd2,charttop,label=rangelabperc), vjust="bottom")+
      theme_bw()+
      scale_color_distiller(palette="YlGnBu", direction=1)+
      ggtitle(paste0("Location: ", cs, ", Root Depth: ", rd, "m, Soil Type: ", st))+
      labs(x="Water Table Depth", y="Annual Groundwater Subsidy (mm)", color="Annual Potential\nWater Deficit (mm)")
    # ggsave(paste0("C:\\Users\\albano\\OneDrive - Desert Research Institute\\ComsolModels\\RWUModels\\modelcomparisonplots\\AppExamples\\",cs,st,rd,"rootdepth_boxplot_GWsubsET.png"),p, bg="white", height=4, width=6, units="in", device="png")
    
    # }}}
  
 
 