# load dependencies
source("../dependencies.R")

# load color palette
colors <- brewer.pal(7, "Set1")[c(1:5,7)]

# import font
font_add(family="CM",
         regular='../fonts/cmunrm.ttf')
showtext_auto()

# font sizes
titleSize <- 80
textSize <- 75

# load simulation results
sim1Wages <- read_csv("../../../simulation/results/playerResults_imports=4_cap=False_seasons=10_simNumb=1000.csv")
sim1League <- read_csv("../../../simulation/results/teamResults_imports=4_cap=False_seasons=10_simNumb=1000.csv")
sim2Wages <- read_csv("../../../simulation/results/playerResults_imports=4_cap=True_seasons=10_simNumb=1000.csv")
sim2League <- read_csv("../../../simulation/results/teamResults_imports=4_cap=True_seasons=10_simNumb=1000.csv")
sim3Wages <- read_csv("../../../simulation/results/playerResults_imports=6_cap=False_seasons=10_simNumb=1000.csv")
sim3League <- read_csv("../../../simulation/results/teamResults_imports=6_cap=False_seasons=10_simNumb=1000.csv")
sim4Wages <- read_csv("../../../simulation/results/playerResults_imports=6_cap=True_seasons=10_simNumb=1000.csv")
sim4League <- read_csv("../../../simulation/results/teamResults_imports=6_cap=True_seasons=10_simNumb=1000.csv")
sim5Wages <- read_csv("../../../simulation/results/playerResults_imports=10_cap=False_seasons=10_simNumb=1000.csv")
sim5League <- read_csv("../../../simulation/results/teamResults_imports=10_cap=False_seasons=10_simNumb=1000.csv")
sim6Wages <- read_csv("../../../simulation/results/playerResults_imports=10_cap=True_seasons=10_simNumb=1000.csv")
sim6League <- read_csv("../../../simulation/results/teamResults_imports=10_cap=True_seasons=10_simNumb=1000.csv")


# competitive balance ####

# cbr ####
# prepare data
simLeagueCombined<-bind_rows(  # combine all simulation data 
  sim1League%>%mutate(simulationSetting=1)%>%select(simulationSetting,validSimulation,simulation,season,validSeason,team,wins,games),
  sim2League%>%mutate(simulationSetting=2)%>%select(simulationSetting,validSimulation,simulation,season,validSeason,team,wins,games),
  sim3League%>%mutate(simulationSetting=3)%>%select(simulationSetting,validSimulation,simulation,season,validSeason,team,wins,games),
  sim4League%>%mutate(simulationSetting=4)%>%select(simulationSetting,validSimulation,simulation,season,validSeason,team,wins,games),
  sim5League%>%mutate(simulationSetting=5)%>%select(simulationSetting,validSimulation,simulation,season,validSeason,team,wins,games),
  sim6League%>%mutate(simulationSetting=6)%>%select(simulationSetting,validSimulation,simulation,season,validSeason,team,wins,games),
)%>%
  mutate(winningPercentage=wins/games)%>%  # calculate winning percentages per simulation, simulation iteration, season and team
  filter(validSeason==TRUE)%>%  # filter out observations from invalid seasons where teams went bankrupt at the begining and season couldnt be simulated 
  
  # within team variation 
  arrange(simulationSetting, simulation, team)%>%
  group_by(simulationSetting, simulation, team)%>%  # group by simulation, simulation iteration and team
  mutate(withinTeamVariation = sqrt(sum((winningPercentage - mean(winningPercentage))^2)/n()))%>%  # calculate standard deviation of a team's winning percentages over all seasons
  group_by(simulationSetting, simulation)%>%
  mutate(averageWithinTeamVariation = mean(unique(withinTeamVariation)))%>%  # calculate average within-team variation over all teams
  
  # within team variation 
  arrange(simulationSetting, simulation, season)%>%
  group_by(simulationSetting, simulation, season)%>%  # group by simulation, simulation iteration and season
  mutate(withinSeasonVariation = sqrt(sum((winningPercentage - 0.5)^2)/n()))%>%  # calculate standard deviation of team winning percentages per season
  group_by(simulationSetting, simulation)%>%
  mutate(averageWithinSeasonVariation = mean(unique(withinSeasonVariation)))%>%  # calculate average within-team season over seasons
  
  # CBR
  arrange(simulationSetting, simulation)%>%
  group_by(simulationSetting, simulation, season)%>%  # group by simulation and simulation iteration
  mutate(CBR = unique(averageWithinTeamVariation)/unique(averageWithinSeasonVariation))%>%  # calculate standard deviation of team winning percentages per season
  ungroup()%>%
  
  # final preparations
  filter(!(CBR == 0 & season == 1))%>%  # remove simulation iterations where only one season was observed because of bankrupcty in second season and thus within-team variation equals 0
  mutate(simulationSetting = as.factor(paste0("Simulation ", simulationSetting)))%>%  #  simulation setting as factor
  distinct(simulationSetting, simulation, CBR)%>%
  select(simulationSetting, CBR)%>%
  rename(Simulation = simulationSetting)

# plot data
cbrDistribution <- ggplot(simLeagueCombined, aes(x=CBR, y=Simulation, color=Simulation))+
  geom_boxplot()+
  scale_y_discrete(
    limits = c("Simulation 6", "Simulation 5", "Simulation 4", "Simulation 3", "Simulation 2", "Simulation 1")
  )+
  scale_x_continuous(
    breaks = seq(0, 1, 0.1)
  )+
  scale_color_manual(
    values = colors
  )+
  theme_minimal()+
  labs(
    x="CBR"
  )+
  theme(
    panel.grid.minor = element_blank(),
    panel.grid.major.x  = element_blank(),
    panel.grid.major.y = element_blank(),
    plot.title = element_text(hjust = 0.5),
    axis.title.x = element_text(family = "CM", size=titleSize, margin=margin(7,0,0,0)),
    axis.title.y = element_blank(),
    legend.position = "none",
    axis.line = element_line(color="darkgrey"),
    axis.ticks = element_line(color="darkgrey"),
    axis.text.x = element_text(family = "CM", size=textSize),
    axis.text.y = element_text(family = "CM", size=textSize),
    plot.margin = margin(t=10, r=10, b=5, l=5, unit = "pt")
  )+
  guides(color = guide_legend(byrow = TRUE))

cbrDistribution
ggsave(cbrDistribution, file = "cbrDistribution.png", height=3, width=6, bg='white', dpi=700)

# one way anova for competitive balance
resultsANOVA <- aov(CBR ~ Simulation, data = simLeagueCombined)

# save summary results of anova
tableANOVA <- summary(resultsANOVA)

# create latex code of result summary
xtable(tableANOVA)  

# Tukey multipair-comparison
resultsTukey<-TukeyHSD(resultsANOVA)

# create latex code of tukey summary
xtable(tidy(resultsTukey), digits = 3)





# unique champions ####
# prepare data
simLeagueCombined<-bind_rows(  # combine all simulation data 
  sim1League%>%mutate(simulationSetting=1)%>%select(simulationSetting,validSimulation,simulation,season,validSeason,team,champion),
  sim2League%>%mutate(simulationSetting=2)%>%select(simulationSetting,validSimulation,simulation,season,validSeason,team,champion),
  sim3League%>%mutate(simulationSetting=3)%>%select(simulationSetting,validSimulation,simulation,season,validSeason,team,champion),
  sim4League%>%mutate(simulationSetting=4)%>%select(simulationSetting,validSimulation,simulation,season,validSeason,team,champion),
  sim5League%>%mutate(simulationSetting=5)%>%select(simulationSetting,validSimulation,simulation,season,validSeason,team,champion),
  sim6League%>%mutate(simulationSetting=6)%>%select(simulationSetting,validSimulation,simulation,season,validSeason,team,champion),
)%>%
  filter(validSimulation==TRUE)%>%  # filter out observations from invalid simulations where teams went bankrupt to guarantee comparability 
  
  # unique champions 
  filter(champion==1)%>%  # only keep the champion of each season
  select(simulationSetting, simulation, team)%>%  
  distinct()%>%  # obtain all unique champions per simulation setting
  group_by(simulationSetting, simulation)%>%
  mutate(uniqueChampions = n())%>%
  ungroup()%>%
  select(simulationSetting, simulation, uniqueChampions)%>%
  distinct()%>%  # obtain the number of unique champions per simulation and simulation iteration
  
  # final preparations
  mutate(simulationSetting = as.factor(paste0("Simulation ", simulationSetting)))%>%  #  simulation setting as factor
  mutate(uniqueChampions = as.factor(uniqueChampions))%>%  # simulation 
  select(simulationSetting, uniqueChampions)%>%
  rename(Simulation = simulationSetting)

# plot data
uniqueChampionsPlot <- ggplot(simLeagueCombined, aes(x=uniqueChampions, fill=Simulation))+
  geom_bar()+
  facet_wrap(~Simulation)+
  scale_fill_manual(
    values = colors
  )+
  theme_minimal()+
  labs(
    x="Number of unique champions",
    y="Count"
  )+
  theme(
    panel.grid.minor = element_blank(),
    panel.grid.major.x  = element_blank(),
    panel.grid.major.y = element_blank(),
    plot.title = element_text(hjust = 0.5),
    strip.text = element_text(family = "CM", size=titleSize, margin=margin(10,0,0,0), vjust=4),
    panel.spacing = unit(1, "lines"),
    axis.title.x = element_text(family = "CM", size=titleSize, margin=margin(7,0,0,0)),
    axis.title.y = element_blank(),
    legend.position = "none",
    axis.line = element_line(color="darkgrey"),
    axis.ticks = element_line(color="darkgrey"),
    axis.text.x = element_text(family = "CM", size=textSize),
    axis.text.y = element_text(family = "CM", size=textSize),
    plot.margin = margin(t=10, r=10, b=5, l=5, unit = "pt")
  )+
  guides(color = guide_legend(byrow = TRUE))

uniqueChampionsPlot
ggsave(uniqueChampionsPlot, file = "uniqueChampionsPlot.png", height=3, width=6, bg='white', dpi=700)

# ordinal logit model
ordinalLogit <- polr(uniqueChampions ~ Simulation, data=simLeagueCombined)

# calculate confidence interval
ci <- confint(ordinalLogit)

# calculate odds ratios and add calculated confidence intervals
OR<-exp(cbind(coef(ordinalLogit),ci))

# print latex table
xtable(OR)


# financial health ####

# bankrupcty ####

# prepare data
simLeagueCombined<-bind_rows(  # combine all simulation data 
  sim1League%>%mutate(simulationSetting=1)%>%select(simulationSetting,simulation,validSimulation),
  sim2League%>%mutate(simulationSetting=2)%>%select(simulationSetting,simulation,validSimulation),
  sim3League%>%mutate(simulationSetting=3)%>%select(simulationSetting,simulation,validSimulation),
  sim4League%>%mutate(simulationSetting=4)%>%select(simulationSetting,simulation,validSimulation),
  sim5League%>%mutate(simulationSetting=5)%>%select(simulationSetting,simulation,validSimulation),
  sim6League%>%mutate(simulationSetting=6)%>%select(simulationSetting,simulation,validSimulation),
)%>%
  distinct()%>% # determine the validity of each simulation iteration
  mutate(Bankruptcy = ifelse(validSimulation, 0, 1))%>%  # create binary variable for bankruptcy
  mutate(simulationSetting = as.factor(paste0("Simulation ", simulationSetting)))%>%  #  simulation setting as factor
  select(simulationSetting, Bankruptcy)%>%
  rename(Simulation = simulationSetting)
  
  

# plot data
bankruptcyRates<-simLeagueCombined%>%
  group_by(Simulation)%>%
  summarise(
    `Bankruptcy Rate`=sum(Bankruptcy/n())
  )


bankruptcyRatesPlot <- ggplot(bankruptcyRates, aes(x=Simulation, y=`Bankruptcy Rate`, fill=Simulation))+
  geom_col()+
  scale_y_continuous(
    expand = c(0,0)
  )+
  scale_fill_manual(
    values = colors
  )+
  theme_minimal()+
  theme(
    panel.grid.minor = element_blank(),
    panel.grid.major.x  = element_blank(),
    panel.grid.major.y = element_blank(),
    plot.title = element_text(hjust = 0.5),
    axis.title.x = element_blank(),
    axis.title.y = element_text(family = "CM", size=titleSize, margin=margin(0,7,0,0)),
    legend.position = "none",
    axis.line = element_line(color="darkgrey"),
    axis.ticks = element_line(color="darkgrey"),
    axis.text.x = element_text(family = "CM", size=textSize-10),
    axis.text.y = element_text(family = "CM", size=textSize),
    plot.margin = margin(t=10, r=10, b=5, l=5, unit = "pt")
  )+
  guides(color = guide_legend(byrow = TRUE))

bankruptcyRatesPlot
ggsave(bankruptcyRatesPlot, file = "bankruptcyRatesPlot.png", height=3, width=6, bg='white', dpi=700)

# estimate logit model
logMod<-glm(Bankruptcy~Simulation, data = simLeagueCombined, family = "binomial")

# save summary results
logModelSummary <- summary(margins(logMod))

# create latex code of result summary
xtable(logModelSummary)  




# asgr ####

# prepare data
simWagesCombined<-bind_rows(  # combine all simulation data 
  sim1Wages%>%mutate(simulationSetting=1)%>%rename(medianSalary = `50%`)%>%select(simulationSetting,validSimulation,simulation,season,validSeason,medianSalary),
  sim2Wages%>%mutate(simulationSetting=2)%>%rename(medianSalary = `50%`)%>%select(simulationSetting,validSimulation,simulation,season,validSeason,medianSalary),
  sim3Wages%>%mutate(simulationSetting=3)%>%rename(medianSalary = `50%`)%>%select(simulationSetting,validSimulation,simulation,season,validSeason,medianSalary),
  sim4Wages%>%mutate(simulationSetting=4)%>%rename(medianSalary = `50%`)%>%select(simulationSetting,validSimulation,simulation,season,validSeason,medianSalary),
  sim5Wages%>%mutate(simulationSetting=5)%>%rename(medianSalary = `50%`)%>%select(simulationSetting,validSimulation,simulation,season,validSeason,medianSalary),
  sim6Wages%>%mutate(simulationSetting=6)%>%rename(medianSalary = `50%`)%>%select(simulationSetting,validSimulation,simulation,season,validSeason,medianSalary),
)%>%
  
  # filtering
  filter(validSeason==TRUE)%>%  # filter out observations from invalid seasons where teams went bankrupt at the begining and season couldnt be simulated 
  group_by(simulationSetting, simulation)%>%
  mutate(totalSeasons = n())%>%  # Calculate the total number of valid seasons simulated per simulation iteration
  filter(totalSeasons>=3)%>%  # the minimal number of seasons to being able to calculate a ASGR is 3:  the growth rate for first season is always zero and it makes no sense to take a median of one single value (growth rate in season two)
  
  # calculate asgr
  mutate(seasonalGrowth = (medianSalary/lag(medianSalary))-1)%>%  # calculate relative salary growth compared to previous season
  filter(!is.na(seasonalGrowth))%>%  # remove all first seasons as there exists no growth for theses seasons
  mutate(ASGR = mean(seasonalGrowth))%>%
  ungroup()%>%
  
  # final preparations
  distinct(simulationSetting, simulation, ASGR)%>%
  mutate(simulationSetting = as.factor(paste0("Simulation ", simulationSetting)))%>%  #  simulation setting as factor
  select(simulationSetting, ASGR)%>%
  rename(Simulation=simulationSetting)
 

# plot data
asgrDistribution <- ggplot(simWagesCombined, aes(x=ASGR, y=Simulation, color=Simulation))+
  geom_boxplot()+
  scale_y_discrete(
    limits = c("Simulation 6", "Simulation 5", "Simulation 4", "Simulation 3", "Simulation 2", "Simulation 1")
  )+
  scale_color_manual(
    values = colors
  )+
  scale_x_continuous(
    breaks = seq(-1, 1, 0.1),
    limits = c(-0.03, 0.6)
  )+
  theme_minimal()+
  labs(
    x="ASGR"
  )+
  theme(
    panel.grid.minor = element_blank(),
    panel.grid.major.x  = element_blank(),
    panel.grid.major.y = element_blank(),
    plot.title = element_text(hjust = 0.5),
    axis.title.x = element_text(family = "CM", size=titleSize, margin=margin(7,0,0,0)),
    axis.title.y = element_blank(),
    legend.position = "none",
    axis.line = element_line(color="darkgrey"),
    axis.ticks = element_line(color="darkgrey"),
    axis.text.x = element_text(family = "CM", size=textSize),
    axis.text.y = element_text(family = "CM", size=textSize),
    plot.margin = margin(t=10, r=10, b=5, l=5, unit = "pt")
  )+
  guides(color = guide_legend(byrow = TRUE))

asgrDistribution
ggsave(asgrDistribution, file = "asgrDistribution.png", height=3, width=6, bg='white', dpi=700)

# one way anova for salary distribution
resultsANOVA <- aov(ASGR ~ Simulation, data = simWagesCombined)

# save summary results of anova
tableANOVA <- summary(resultsANOVA)

# create latex code of result summary
xtable(tableANOVA)  

# Tukey multipair-comparison
resultsTukey<-TukeyHSD(resultsANOVA)

# create latex code of tukey summary
xtable(tidy(resultsTukey), digits = 3)




