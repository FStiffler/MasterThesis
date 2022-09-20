# Load packages
source("../dependencies.R")

# load color palette
colors <- brewer.pal(4, "Set1")

# create supply effect function
supplyFunction <- function(k, kmin, lambda, gamma){
  
  solution <- lambda/(k+gamma)
  solution[k<kmin]<-NA
  solution
   
}

# parameters
xmax= 7500
kmin = 300
k0=350
lambda = 500
gamma = 0

# import font
font_add(family="CM",
         regular='../fonts/cmunrm.ttf')
showtext_auto()

# font sizes
titleSize <- 80
textSize <- 75

# function to find parameters lambda and gamma based on solution to equation system:
#   lambda/(k0+gamma)=1
#   lambda/(epsilon*k0+gamma)=0.5
findParameters<-function(k0, epsilon){
  
  gamma <- epsilon*k0-k0/0.5
  lambda <- k0 + gamma
  params = list("epsilon"=epsilon, "lambda"=lambda, "gamma"=gamma)
  return(params)
  
}


# explanatory plots ####

# plot supply effect function for different lambda with constant kmin and gamma
supplyFunctionLambda<-ggplot()+
  stat_function(fun=supplyFunction,
                args = list(kmin = kmin, lambda = 0.5*lambda, gamma = gamma),
                aes(color="first"),
                xlim = c(0,xmax)
  )+
  stat_function(fun=supplyFunction,
                args = list(kmin = kmin, lambda = 1*lambda, gamma = gamma),
                aes(color="second"),
                xlim = c(0,xmax)
  )+
  stat_function(fun=supplyFunction,
                args = list(kmin = kmin, lambda = 2*lambda, gamma = gamma),
                aes(color="third"),
                xlim = c(0,xmax)
  )+
  stat_function(fun=supplyFunction,
                args = list(kmin = kmin, lambda = 5*lambda, gamma = gamma),
                aes(color="fourth"),
                xlim = c(0,xmax)
  )+
  geom_vline(xintercept = kmin, color="grey", linetype=2)+
  scale_color_manual(
    breaks = c("first", "second", "third", "fourth"),
    values = colors,
    labels = c(
      expression(paste("0.5",lambda)),
      expression(paste(lambda)),
      expression(paste("2",lambda)),
      expression(paste("5",lambda))
    )
  )+
  scale_x_continuous(expand = c(0,0),
                     breaks = c(kmin),
                     labels = expression(k[min]))+
  scale_y_continuous(expand = c(0,0),
                     limits = c(0, 10),
                     breaks = seq(0,10,1))+
  theme_minimal()+
  labs(
    x=expression(k[t]),
    y=bquote(f(k[t]))
  )+
  theme(
    panel.grid.minor = element_blank(),
    panel.grid.major.x  = element_blank(),
    panel.grid.major.y = element_blank(),
    plot.title = element_text(hjust = 0.5),
    axis.title.x = element_text(family = "CM", size=titleSize, margin=margin(7,0,0,0)),
    axis.title.y = element_text(family = "CM", size=titleSize, margin=margin(0,7,0,0)),
    legend.title = element_blank(),
    legend.justification = c(1,1),
    legend.position = c(1, 1),
    legend.key.size = unit(5, "pt"),
    legend.key.width = unit(10, "pt"),
    legend.spacing.y = unit(2, "pt"),
    legend.text = element_text(family="CM", size=textSize),
    legend.text.align = 0,
    axis.line = element_line(color="darkgrey"),
    axis.ticks = element_line(color="darkgrey"),
    axis.text.x = element_text(family = "CM", size=textSize, color="darkgrey"),
    axis.text.y = element_text(family = "CM", size=textSize, color="darkgrey"),
    plot.margin = margin(t=10, r=10, b=5, l=5, unit = "pt")
  )+
  guides(color = guide_legend(byrow = TRUE))

supplyFunctionLambda
ggsave(supplyFunctionLambda, file = "supplyFunctionLambda.png", height=3, width=6, bg='white', dpi=700)

# plot supply effect function for different gamma with constant kmin and lambda
supplyFunctionGamma<-ggplot()+
  stat_function(fun=supplyFunction,
                args = list(kmin = kmin, lambda = lambda, gamma = gamma+kmin),
                aes(color="first"),
                xlim = c(0,xmax)
  )+
  stat_function(fun=supplyFunction,
                args = list(kmin = kmin, lambda = lambda, gamma = gamma),
                aes(color="second"), 
                xlim = c(0,xmax)
  )+
  stat_function(fun=supplyFunction,
                args = list(kmin = kmin, lambda = lambda, gamma = gamma-kmin),
                aes(color="third"),
                xlim = c(0,xmax)
  )+
  stat_function(fun=supplyFunction,
                args = list(kmin = kmin, lambda = lambda, gamma = gamma-5*kmin),
                aes(color="fourth"),
                xlim = c(0,xmax)
  )+
  geom_vline(xintercept = kmin, color="grey", linetype = 2)+
  scale_color_manual(
    breaks = c("first", "second", "third", "fourth"),
    values = colors,
    labels = c(
      expression(paste(gamma,'='*k[min])),
      expression(paste(gamma,'=0')),
      expression(paste(gamma,'=-'*k[min])),
      expression(paste(gamma,'=-5'*k[min]))
    )
  )+
  scale_x_continuous(expand = c(0,0),
                     breaks = c(kmin),
                     labels = expression(k[min]))+
  scale_y_continuous(expand = c(0,0),
                     limits = c(0, 10),
                     breaks = seq(0,10,1))+
  theme_minimal()+
  labs(
    x=expression(k[t]),
    y=bquote(f(k[t]))
  )+
  theme(
    panel.grid.minor = element_blank(),
    panel.grid.major.x  = element_blank(),
    panel.grid.major.y = element_blank(),
    plot.title = element_text(hjust = 0.5),
    axis.title.x = element_text(family = "CM", size=titleSize, margin=margin(7,0,0,0)),
    axis.title.y = element_text(family = "CM", size=titleSize, margin=margin(0,7,0,0)),
    legend.title = element_blank(),
    legend.justification = c(1,1),
    legend.position = c(1, 1),
    legend.key.size = unit(5, "pt"),
    legend.key.width = unit(10, "pt"),
    legend.spacing.y = unit(2, "pt"),
    legend.text = element_text(family="CM", size=textSize),
    legend.text.align = 0,
    axis.line = element_line(color="darkgrey"),
    axis.ticks = element_line(color="darkgrey"),
    axis.text.x = element_text(family = "CM", size=textSize, color="darkgrey"),
    axis.text.y = element_text(family = "CM", size=textSize, color="darkgrey"),
    plot.margin = margin(t=10, r=10, b=5, l=5, unit = "pt")
  )+
  guides(color = guide_legend(byrow = TRUE))

supplyFunctionGamma
ggsave(supplyFunctionGamma, file = "supplyFunctionGamma.png", height=3, width=6, bg='white', dpi=700)


# solve equation system for illustrative plot with epsilon 2 and 4
parameters1<-findParameters(k0, 2)
parameters2<-findParameters(k0, 4)


# plot supply effect depending on epsilon
supplyFunctionEpsilon<-ggplot()+
  
  # vertical line at kmin
  geom_vline(xintercept = kmin, color="grey", linetype = 2)+
  
  # curve and marks with epsilon = 4
  stat_function(fun=supplyFunction,
                args = list(kmin = kmin, lambda = parameters2$lambda, gamma = parameters2$gamma),
                xlim = c(kmin, 5*k0),
                size = 0.5,
                aes(color="epsilon2")
  )+
  geom_point(aes(x=parameters2$epsilon*k0, y=0.5, color="epsilon2"), size=1)+
  geom_segment(aes(x=parameters2$epsilon*k0, xend=parameters2$epsilon*k0, y=0, yend=0.5, color="epsilon2"), linetype = 3, size = 0.5,)+
  geom_segment(aes(x=parameters1$epsilon*k0, xend=parameters2$epsilon*k0, y=0.5, yend=0.5, color="epsilon2"), linetype = 3, size = 0.5,)+
  
  # curve and marks with epsilon = 2
  stat_function(fun=supplyFunction,
                args = list(kmin = kmin, lambda = parameters1$lambda, gamma = parameters1$gamma),
                xlim = c(kmin, 5*k0),
                size = 0.5,
                aes(color="epsilon1")
  )+
  geom_point(aes(x=parameters1$epsilon*k0, y=0.5, color="epsilon1"), size=1)+
  geom_segment(aes(x=parameters1$epsilon*k0, xend=parameters1$epsilon*k0, y=0, yend=0.5, color="epsilon1"), linetype = 3, size = 0.5,)+
  geom_segment(aes(x=0, xend=parameters1$epsilon*k0, y=0.5, yend=0.5, color="epsilon1"), linetype = 3, size = 0.5,)+
  

  # marks at k0
  geom_point(aes(x=k0, y=1), color="black", size=1)+
  geom_segment(aes(x=k0, xend=k0, y=0, yend=1), color="black", linetype = 3, size = 0.5,)+
  geom_segment(aes(x=0, xend=k0, y=1, yend=1), color="black", linetype = 3, size = 0.5,)+
  
  # cosmetics
  scale_x_continuous(expand = c(0,0),
                     breaks = c(kmin, k0, parameters1$epsilon*k0, parameters2$epsilon*k0),
                     labels = c(expression(k[min]),
                                expression(k[0]),
                                bquote(.(parameters1$epsilon)*k[0]),
                                bquote(.(parameters2$epsilon)*k[0])
                                )
                     )+
  scale_y_continuous(expand = c(0,0),
                     limits = c(0,1.75),
                     breaks = seq(0,2,0.25)
                     )+
  scale_color_manual(
    breaks = c("epsilon1", "epsilon2"),
    values = colors[1:2],
    labels = c(
      expression(paste(epsilon,'=2')),
      expression(paste(epsilon,'=4'))
      )
    )+
  theme_minimal()+
  labs(
    x=expression(k[t]),
    y=bquote(f(k[t]))
  )+
  theme(
    panel.grid.minor = element_blank(),
    panel.grid.major.x  = element_blank(),
    panel.grid.major.y = element_blank(),
    plot.title = element_text(hjust = 0.5),
    axis.title.x = element_text(family = "CM", size=titleSize, margin=margin(7,0,0,0)),
    axis.title.y = element_text(family = "CM", size=titleSize, margin=margin(0,7,0,0)),
    legend.title = element_blank(),
    legend.justification = c(1,1),
    legend.position = c(1, 1),
    legend.key.size = unit(5, "pt"),
    legend.key.width = unit(10, "pt"),
    legend.spacing.y = unit(2, "pt"),
    legend.text = element_text(family="CM", size=textSize),
    legend.text.align = 0,
    axis.line = element_line(color="darkgrey"),
    axis.ticks.y = element_line(color="darkgrey"),
    axis.ticks.x = element_line(color=c("darkgrey", "black", colors[1], colors[2])),
    axis.text.x = element_text(family = "CM", size=textSize, color=c("darkgrey", "black", colors[1], colors[2])),
    axis.text.y = element_text(family = "CM", size=textSize, color = "darkgrey"),
    plot.margin = margin(t=10, r=10, b=5, l=5, unit = "pt")
  )+
  guides(color = guide_legend(byrow = TRUE))

supplyFunctionEpsilon
ggsave(supplyFunctionEpsilon, file = "supplyFunctionEpsilon.png", height=3, width=6, bg='white', dpi=700)


# plots based on real data ####

# real initial player pool size faced by team 
k0 = 304

# real kmin 
kmin = 168

# solve equation system for illustrative plot with epsilon 2 as assumption
parameters<-findParameters(k0, 2)

# plot real supply effect 
supplyFunctionReal<-ggplot()+
  
  
  # curve and marks with epsilon = 4
  stat_function(fun=supplyFunction,
                args = list(kmin = kmin, lambda = parameters$lambda, gamma = parameters$gamma),
                color="black",
                xlim=c(kmin, 2100), 
                size=0.5
  )+ 
  
  # cosmetics
  scale_x_continuous(expand = c(0,0),
                     breaks = seq(0,2000,200),
                     limits = c(0, 2100)
  )+
  scale_y_continuous(expand = c(0,0),
                     limits = c(0,1.5),
                     breaks = seq(0,2,0.5)
  )+
  theme_minimal()+
  labs(
    x=expression(k[t]),
    y=bquote(f(k[t]))
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
    legend.text.align = 0,
    axis.line = element_line(color="darkgrey"),
    axis.ticks = element_line(color="darkgrey"),
    axis.text.x = element_text(family = "CM", size=textSize, color=c("darkgrey")),
    axis.text.y = element_text(family = "CM", size=textSize, color = "darkgrey"),
    plot.margin = margin(t=10, r=10, b=5, l=5, unit = "pt")
  )

supplyFunctionReal
ggsave(supplyFunctionReal, file = "supplyFunctionReal.png", height=3, width=6, bg='white', dpi=700)


