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
  geom_area(color="black")+
  theme_minimal()+
  scale_fill_manual(values=colors)+
  scale_y_continuous(labels = scales::percent, expand = c(0,0), breaks = seq(0,1,1))+
  scale_x_discrete(expand = c(0,0))+
  labs(
    x="Season",
    y="Share of game attendance"
  )+
  theme(
    panel.grid.minor = element_blank(),
    panel.grid.major.x  = element_blank(),
    panel.grid.major.y = element_blank(),
    panel.border = element_blank(),
    plot.title = element_text(hjust = 0.5),
    axis.title.x = element_text(family = "CM", size=20, margin=margin(10,0,0,0)),
    axis.title.y = element_text(family = "CM", size=20, margin=margin(0,10,0,0)),
    legend.title = element_blank(),
    legend.text = element_text(family="CM", size=20),
    axis.line = element_line(color="darkgrey"),
    axis.ticks = element_line(color="darkgrey"),
    axis.text.x = element_text(family = "CM", size=16, margin = margin(10,0,0,0)),
    axis.text.y = element_text(family = "CM", size=16, margin = margin(0,10,0,0))
  )
attDev
ggsave(attDev, file = "attendanceDevelopment.png", height=4, width=8, bg="white")
