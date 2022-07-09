# Load packages
source("../dependencies.R")

# load color palette
colors <- brewer.pal(4, "Set1")

# plot different beta distributions as example
betaDistributions<-ggplot()+
  stat_function(fun=dbeta,
                args = list(shape1=1, shape2=1),
                aes(color="uniform"),
  )+
  stat_function(fun=dbeta,
                args = list(shape1=9, shape2=9),
                aes(color="normal"),
  )+
  stat_function(fun=dbeta,
                args = list(shape1=1, shape2=5),
                aes(color="power"),
  )+
  stat_function(fun=dbeta,
                args = list(shape1=2, shape2=6),
                aes(color="left"),
  )+
  scale_color_manual(
    breaks = c("uniform", "normal", "power", "left"),
    values = colors,
    labels = c(
      expression(paste(alpha,"=1, ",beta,"=1")),
      expression(paste(alpha,"=9, ",beta,"=9")),
      expression(paste(alpha,"=1, ",beta,"=5")),
      expression(paste(alpha,"=2, ",beta,"=6"))
    )
  )+
  scale_x_continuous(expand = c(0,0))+
  scale_y_continuous(expand = c(0,0))+
  theme_minimal()+
  labs(
    x="s",
    y=bquote(f[S](s))
  )+
  theme(
    panel.grid.minor = element_blank(),
    panel.grid.major.x  = element_blank(),
    panel.grid.major.y = element_blank(),
    plot.title = element_text(hjust = 0.5),
    axis.title.x = element_text(family = "CM", size=20, margin=margin(10,0,0,0)),
    axis.title.y = element_text(family = "CM", size=20, margin=margin(0,10,0,0)),
    legend.title = element_blank(),
    legend.position = c(0.94, 0.88),
    legend.text = element_text(family="CM", size=20),
    axis.line = element_line(color="darkgrey"),
    axis.ticks = element_line(color="darkgrey"),
    axis.text.x = element_text(family = "CM", size=16),
    axis.text.y = element_text(family = "CM", size=16)
  )

betaDistributions
ggsave(betaDistributions, file = "betaDistributions.png", height=4, width=8, bg='white')

# Load data
winShares<-read_csv("Win Shares NL 2021-22.csv")

# Load color palettes
Set3<-brewer.pal(name="Set3", n=12)

# import font
font_add(family="CM",
         regular='../fonts/cmunrm.ttf')
showtext_auto()

# prepare data
winShareFinal<-winShares%>%
  filter(GP >= 10)%>%
  rename(winShares = `WS per game`)
  
# create plot to illustrate skill distribution
skillDistribution<-ggplot(winShareFinal, aes(x=winShares))+
  geom_density(fill='darkgrey')+
  theme_minimal()+
  labs(
    x="Win shares per game",
    y="Density"
  )+
  theme(
    panel.grid.minor = element_blank(),
    panel.grid.major.x  = element_blank(),
    panel.grid.major.y = element_blank(),
    plot.title = element_text(hjust = 0.5),
    axis.title.x = element_text(family = "CM", size=20, margin=margin(10,0,0,0)),
    axis.title.y = element_text(family = "CM", size=20, margin=margin(0,10,0,0)),
    legend.title = element_blank(),
    legend.text = element_text(family="CM", size=20),
    axis.line = element_line(color="darkgrey"),
    axis.ticks = element_line(color="darkgrey"),
    axis.text.x = element_text(family = "CM", size=16),
    axis.text.y = element_text(family = "CM", size=16)
    
  )
skillDistribution
ggsave(skillDistribution, file = "skillDistribution.png", height=4, width=8, bg='white')

# win share as vector
winShareVector<-winShareFinal$winShares

# min-max normalization function
norm_minmax <- function(x){
  (x- min(x)) /(max(x)-min(x))
}

# normalize win shares to a range between 0 and 1
normalizedWinShares<-norm_minmax(winShareVector)

# estimate alpha and beta with maximum likelihood
mleResults <- ebeta(normalizedWinShares, method = "mle")

# extract parameters
alphaValue <- mleResults$parameters[1]
betaValue <- mleResults$parameters[2]

# list with parameters
parameters <- list(shape1=alphaValue, shape2=betaValue)

# string expression for plot legend 
legendString <- bquote("Fitted Distribution, "~alpha==.(round(alphaValue,2))~","~beta==.(round(betaValue,2)))

# plot data distribution against fitted distribution
fittedSkillDistribution<-ggplot()+
  geom_density(aes(x=normalizedWinShares, fill="blue"), alpha=0.5)+
  stat_function(fun=dbeta,
                args = parameters,
                geom = "area",
                aes(fill="red"),
                alpha=0.5
                )+
  stat_function(fun=dbeta,
                args = parameters
                )+
  scale_fill_manual(
    values = c("red", "blue"),
    labels = c("Observed Distribution", legendString)
  )+
  theme_minimal()+
  labs(
    x="Normalized win shares per game",
    y="Density"
  )+
  theme(
    panel.grid.minor = element_blank(),
    panel.grid.major.x  = element_blank(),
    panel.grid.major.y = element_blank(),
    plot.title = element_text(hjust = 0.5),
    axis.title.x = element_text(family = "CM", size=20, margin=margin(10,0,0,0)),
    axis.title.y = element_text(family = "CM", size=20, margin=margin(0,10,0,0)),
    legend.title = element_blank(),
    legend.position = c(0.84, 0.93),
    legend.text = element_text(family="CM", size=20),
    axis.line = element_line(color="darkgrey"),
    axis.ticks = element_line(color="darkgrey"),
    axis.text.x = element_text(family = "CM", size=16),
    axis.text.y = element_text(family = "CM", size=16)
  )
fittedSkillDistribution
ggsave(fittedSkillDistribution, file = "fittedSkillDistribution.png", height=4, width=8, bg='white')
  


