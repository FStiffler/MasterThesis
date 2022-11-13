# Load packages
source("../dependencies.R")

# Load data
reportData<-read.csv("IIHFSurveysCombined.csv")

# Load color palettes
Set3<-brewer.pal(name="Set3", n=12)

# import font
font_add(family="CM",
         regular='../fonts/cmunrm.ttf')
showtext_auto()

# font sizes
titleSize <- 70
textSize <- 65

# Swiss Player Development
swissDev<-reportData%>%
  select(Year:Female)%>%
  filter(Country=="Switzerland")%>%
  pivot_longer(cols = Registered:Female, values_to = "Count", names_to = "Category")%>%
  ggplot(aes(Year, Count, color=Category))+
  geom_line(size=0.5)+
  geom_point(size=1)+
  geom_text(aes(label=Count), vjust=-1.2, show.legend =F, size=(textSize-10)/.pt, family="CM")+
  theme_minimal()+
  scale_color_manual(values=c("black",Set3[4],Set3[5],Set3[6]),
                     labels=c("Registered (total)", "U20 (male)", "Adult (male)", "Female"),
                     limits=c("Registered","U20","Senior","Female"))+
  scale_x_continuous(breaks = c(min(reportData$Year):max(reportData$Year)),
                     limits = c(2011,2021))+
  scale_y_continuous(breaks = seq(0,35000,5000),
                     expand = c(0, 0),
                     limits = c(0,35000)
                     )+
  labs(
    x="Year",
    y="Number of players"
  )+
  theme(
    panel.grid.minor = element_blank(),
    panel.grid.major.x  = element_blank(),
    panel.grid.major.y = element_blank(),
    plot.title = element_text(hjust = 0.5),
    axis.title.x = element_text(family = "CM", size=titleSize, margin=margin(7,0,0,0)),
    axis.title.y = element_text(family = "CM", size=titleSize, margin=margin(0,7,0,0)),
    legend.title = element_blank(),
    legend.text = element_text(family="CM", size=textSize),
    axis.line = element_line(color="darkgrey"),
    axis.ticks = element_line(color="darkgrey"),
    axis.text.x = element_text(family = "CM", size=textSize),
    axis.text.y = element_text(family = "CM", size=textSize),
    plot.margin = margin(t=10, r=0, b=5, l=5, unit = "pt")
    
  )
swissDev
ggsave(swissDev, file = "playerDevelopmentAbsolut.png", height=3, width=6, bg='white', dpi=700)

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
      vjust=vjustPos), size=textSize/.pt, family="CM")+
  scale_y_continuous(labels = scales::percent,
                       limits = c(-0.15, 0.2),
                     breaks=0)+
  scale_fill_distiller(palette = "RdYlGn", direction = 1, labels=scales::percent)+
  labs(
    x="Year",
    y="Relative growth of player base"
  )+
  theme_minimal()+
  theme(
    panel.grid.minor = element_blank(),
    panel.grid.major.x  = element_blank(),
    panel.grid.major.y = element_line(linetype = 2, color="darkgrey"),
    plot.title = element_text(hjust = 0.5),
    legend.text = element_text(family="CM", size=textSize),
    axis.title.x = element_text(family = "CM", size=titleSize, margin=margin(7,0,0,0)),
    axis.title.y = element_text(family = "CM", size=titleSize, margin=margin(0,7,0,0)),
    axis.line = element_blank(),
    axis.ticks = element_line(color="darkgrey"),
    axis.text.x = element_text(family = "CM", size=textSize),
    axis.text.y = element_blank(),
    legend.title = element_blank(),
    plot.margin = margin(t=10, r=0, b=5, l=5, unit = "pt")
  )
swissDevRel
ggsave(swissDevRel, file = "playerDevelopmentRelative.png", height=3, width=6, bg='white', dpi=700)

# Average growth rate
round(100*mean(swissDevRel$data$yearlyGrowth), 1)

