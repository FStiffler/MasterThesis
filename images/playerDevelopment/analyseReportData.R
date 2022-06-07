# Load packages
library(tidyverse)
library(RColorBrewer)

# Load data
reportData<-read.csv("IIHFSurveysCombined.csv")

# Load color palettes
Set3<-brewer.pal(name="Set3", n=12)

# Swiss Player Development
swissDev<-reportData%>%
  select(Year:Female)%>%
  filter(Country=="Switzerland")%>%
  pivot_longer(cols = Registered:Female, values_to = "Count", names_to = "Category")%>%
  ggplot(aes(Year, Count, color=Category))+
  geom_line(size=1)+
  geom_point(size=2)+
  geom_text(aes(label=Count), vjust=-1.2, show.legend =F, size=3)+
  theme_minimal()+
  scale_color_manual(values=c("black",Set3[4],Set3[5],Set3[6]),
                     labels=c("Registered (total)", "U20", "Senior", "Female"),
                     limits=c("Registered","U20","Senior","Female"))+
  scale_x_continuous(breaks = c(min(reportData$Year):max(reportData$Year)))+
  scale_y_continuous(breaks = seq(0,35000,5000), expand = c(0, 0), limits = c(0,max(reportData$Registered[reportData$Country=="Switzerland"])+2000))+
  theme(
    panel.grid.minor = element_blank(),
    panel.grid.major.x  = element_blank(),
    panel.grid.major.y = element_blank(),
    plot.title = element_text(hjust = 0.5),
    axis.title.x = element_blank(),
    axis.title.y = element_blank(),
    legend.title = element_blank(),
    axis.line = element_line(color="darkgrey"),
    axis.ticks = element_line(color="darkgrey"),
    
  )
swissDev
ggsave(swissDev, file = "playerDevelopmentAbsolut.png", height=4, width=8)

# Swiss Player Development Relative (Male)
swissDevRel<-reportData%>%
  select(Year:U20)%>%
  mutate(registeredMale=Senior+U20)%>%
  filter(Country=="Switzerland")%>%
  mutate(yearlyGrowth=(registeredMale-lag(registeredMale))/lag(registeredMale))%>%
  filter(!is.na(yearlyGrowth))%>%
  mutate(vjustPos=ifelse(yearlyGrowth<0, 1.25, -0.5))%>%
  ggplot(aes(as.factor(Year), yearlyGrowth, fill=yearlyGrowth))+
  geom_bar(stat="identity")+
  geom_text(
    aes(
      label=paste0(100*round(yearlyGrowth,3),"%"),
      vjust=vjustPos), size=3)+
  scale_y_continuous(labels = scales::percent,
                       limits = c(-0.15, 0.2),
                     breaks=0)+
  scale_fill_distiller(palette = "RdYlGn", direction = 1, labels=scales::percent)+
  theme_minimal()+
  theme(
    panel.grid.minor = element_blank(),
    panel.grid.major.x  = element_blank(),
    panel.grid.major.y = element_line(linetype = 2, color="grey"),
    plot.title = element_text(hjust = 0.5),
    axis.title.x = element_blank(),
    axis.text.y = element_blank(),
    axis.title.y = element_blank(),
    axis.line.x = element_blank(),
    axis.line.y = element_blank(),
    legend.title = element_blank(),
    axis.ticks.x = element_line(),
  )
swissDevRel
ggsave(swissDevRel, file = "playerDevelopmentRelative.png", height=4, width=8)

# Average growth rate
round(100*mean(swissDevRel$data$yearlyGrowth), 1)

