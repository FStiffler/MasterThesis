# Load packages
source("../dependencies.R")

# Load data
attendance<-read_csv("averageAttendanceHistory.csv")

# Load color palettes
colors<-wes_palette("Darjeeling1", 14, type = "continuous")

# import font
font_add(family="CM",
         regular='../fonts/cmunrm.ttf')
showtext_auto()

# font sizes
titleSize <- 50
textSize <- 45

# National League Attendance Development
attDev<-attendance%>%
  select(-contains("po"), -contains("gr"), -rsMedian)%>%
  pivot_longer(cols = contains("rs"), values_to = 'attendanceAverage', names_to = 'season', names_prefix = 'rs')%>%
  filter(!is.na(attendanceAverage))%>%
  group_by(season)%>%
  mutate(share=attendanceAverage/sum(attendanceAverage, na.rm = T))%>%
  ungroup()%>%
  mutate(season = as.factor(season), team=as.factor(team))%>%
  ggplot(aes(x=season, y=share, group=team, fill=team))+
  geom_area(color="black", size=0.3)+
  theme_minimal()+
  scale_fill_manual(values=colors)+
  scale_y_continuous(labels = scales::percent, expand = c(0,0), breaks = seq(0,1,1))+
  scale_x_discrete(expand = c(0,0))+
  labs(
    x="Season",
    y="Share of average league game attendance"
  )+
  theme(
    panel.grid.minor = element_blank(),
    panel.grid.major.x  = element_blank(),
    panel.grid.major.y = element_blank(),
    panel.border = element_rect(color="darkgrey", fill = NA, size=1),
    plot.title = element_text(hjust = 0.5),
    axis.title.x = element_text(family = "CM", size=titleSize, margin=margin(7,0,0,0)),
    axis.title.y = element_text(family = "CM", size=titleSize, margin=margin(0,7,0,0)),
    legend.title = element_blank(),
    legend.key.size = unit(10, "pt"),
    legend.key.width = unit(10, "pt"),
    legend.spacing.y = unit(2, "pt"),
    legend.text = element_text(family="CM", size=textSize),
    axis.line = element_blank(),
    axis.ticks = element_line(color="darkgrey"),
    axis.text.x = element_text(family = "CM", size=textSize, margin = margin(7,0,0,0)),
    axis.text.y = element_text(family = "CM", size=textSize, margin = margin(0,7,0,0)),
    plot.margin = margin(t=10, r=0, b=5, l=5, unit = "pt")
  )+
  guides(fill = guide_legend(byrow = TRUE))
attDev
ggsave(attDev, file = "attendanceDevelopment.png", height=3, width=6, bg="white", dpi=700)

