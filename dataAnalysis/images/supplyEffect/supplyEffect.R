# Load packages
source("../dependencies.R")

# load color palette
colors <- brewer.pal(4, "Set1")

# create supply effect function
supplyFunction <- function(k, kmin, theta, lambda){
  
  solution <- theta/(k+lambda)
  solution[k<kmin]<-NA
  solution
   
}

# parameters
xmax= 7500
kmin = 300
k0=350
theta = 500
lambda = 0

# function to find parameters theta and lambda based on solution to equation system:
#   theta/(k0+lambda)=1
#   theta/(epsilon*k0+lambda)=0.5
findParameters<-function(k0, epsilon){
  
  lambda <- epsilon*k0-k0/0.5
  theta <- k0 + lambda
  params = list("epsilon"=epsilon, "theta"=theta, "lambda"=lambda)
  return(params)
  
}


# explanatory plots ####

# plot supply effect function for different theta with constant kmin and lambda
supplyFunctionTheta<-ggplot()+
  stat_function(fun=supplyFunction,
                args = list(kmin = kmin, theta = 0.5*theta, lambda = lambda),
                aes(color="first"),
                xlim = c(0,xmax)
  )+
  stat_function(fun=supplyFunction,
                args = list(kmin = kmin, theta = 1*theta, lambda = lambda),
                aes(color="second"),
                xlim = c(0,xmax)
  )+
  stat_function(fun=supplyFunction,
                args = list(kmin = kmin, theta = 2*theta, lambda = lambda),
                aes(color="third"),
                xlim = c(0,xmax)
  )+
  stat_function(fun=supplyFunction,
                args = list(kmin = kmin, theta = 5*theta, lambda = lambda),
                aes(color="fourth"),
                xlim = c(0,xmax)
  )+
  geom_vline(xintercept = kmin, color="grey", linetype=2)+
  scale_color_manual(
    breaks = c("first", "second", "third", "fourth"),
    values = colors,
    labels = c(
      expression(paste("0.5",theta)),
      expression(paste(theta)),
      expression(paste("2",theta)),
      expression(paste("5",theta))
    )
  )+
  scale_x_continuous(expand = c(0,0),
                     breaks = c(kmin),
                     labels = expression(k[min]))+
  scale_y_continuous(expand = c(0,0),
                     limits = c(0, 10.5),
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
    axis.title.x = element_text(family = "CM", size=20, margin=margin(10,0,0,0)),
    axis.title.y = element_text(family = "CM", size=20, margin=margin(0,10,0,0)),
    legend.title = element_blank(),
    legend.position = c(0.95, 0.9),
    legend.text = element_text(family="CM", size=20),
    legend.text.align = 0,
    axis.line = element_line(color="darkgrey"),
    axis.ticks = element_line(color="darkgrey"),
    axis.text.x = element_text(family = "CM", size=16, color="darkgrey"),
    axis.text.y = element_text(family = "CM", size=16, color="darkgrey")
  )

supplyFunctionTheta
ggsave(supplyFunctionTheta, file = "supplyFunctionTheta.png", height=8, width=16, bg='white')

# plot supply effect function for different lambda with constant kmin and theta
supplyFunctionLambda<-ggplot()+
  stat_function(fun=supplyFunction,
                args = list(kmin = kmin, theta = theta, lambda = lambda+kmin),
                aes(color="first"),
                xlim = c(0,xmax)
  )+
  stat_function(fun=supplyFunction,
                args = list(kmin = kmin, theta = theta, lambda = lambda),
                aes(color="second"), 
                xlim = c(0,xmax)
  )+
  stat_function(fun=supplyFunction,
                args = list(kmin = kmin, theta = theta, lambda = lambda-kmin),
                aes(color="third"),
                xlim = c(0,xmax)
  )+
  stat_function(fun=supplyFunction,
                args = list(kmin = kmin, theta = theta, lambda = lambda-5*kmin),
                aes(color="fourth"),
                xlim = c(0,xmax)
  )+
  geom_vline(xintercept = kmin, color="grey", linetype = 2)+
  scale_color_manual(
    breaks = c("first", "second", "third", "fourth"),
    values = colors,
    labels = c(
      expression(paste(lambda,'='*+k[min])),
      expression(paste(lambda,'=0')),
      expression(paste(lambda,'='*-k[min])),
      expression(paste(lambda,'=-5'*k[min]))
    )
  )+
  scale_x_continuous(expand = c(0,0),
                     breaks = c(kmin),
                     labels = expression(k[min]))+
  scale_y_continuous(expand = c(0,0),
                     limits = c(0, 10.5),
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
    axis.title.x = element_text(family = "CM", size=20, margin=margin(10,0,0,0)),
    axis.title.y = element_text(family = "CM", size=20, margin=margin(0,10,0,0)),
    legend.title = element_blank(),
    legend.position = c(0.95, 0.9),
    legend.text = element_text(family="CM", size=20),
    legend.text.align = 0,
    axis.line = element_line(color="darkgrey"),
    axis.ticks = element_line(color="darkgrey"),
    axis.text.x = element_text(family = "CM", size=16, color="darkgrey"),
    axis.text.y = element_text(family = "CM", size=16, color="darkgrey")
  )

supplyFunctionLambda
ggsave(supplyFunctionLambda, file = "supplyFunctionLambda.png", height=8, width=16, bg='white')


# solve equation system for illustrative plot with epsilon 2 and 4
parameters1<-findParameters(k0, 2)
parameters2<-findParameters(k0, 4)


# plot supply effect depending on epsilon
supplyFunctionEpsilon<-ggplot()+
  
  # vertical line at kmin
  geom_vline(xintercept = kmin, color="grey", linetype = 2)+
  
  # curve and marks with epsilon = 4
  stat_function(fun=supplyFunction,
                args = list(kmin = kmin, theta = parameters2$theta, lambda = parameters2$lambda),
                xlim = c(kmin, 5*k0),
                aes(color="epsilon2")
  )+
  geom_point(aes(x=parameters2$epsilon*k0, y=0.5, color="epsilon2"))+
  geom_segment(aes(x=parameters2$epsilon*k0, xend=parameters2$epsilon*k0, y=0, yend=0.5, color="epsilon2"), linetype = 3)+
  geom_segment(aes(x=parameters1$epsilon*k0, xend=parameters2$epsilon*k0, y=0.5, yend=0.5, color="epsilon2"), linetype = 3)+
  
  # curve and marks with epsilon = 2
  stat_function(fun=supplyFunction,
                args = list(kmin = kmin, theta = parameters1$theta, lambda = parameters1$lambda),
                xlim = c(kmin, 5*k0),
                aes(color="epsilon1")
  )+
  geom_point(aes(x=parameters1$epsilon*k0, y=0.5, color="epsilon1"))+
  geom_segment(aes(x=parameters1$epsilon*k0, xend=parameters1$epsilon*k0, y=0, yend=0.5, color="epsilon1"), linetype = 3)+
  geom_segment(aes(x=0, xend=parameters1$epsilon*k0, y=0.5, yend=0.5, color="epsilon1"), linetype = 3)+
  

  # marks at k0
  geom_point(aes(x=k0, y=1), color="black")+
  geom_segment(aes(x=k0, xend=k0, y=0, yend=1), color="black", linetype = 3)+
  geom_segment(aes(x=0, xend=k0, y=1, yend=1), color="black", linetype = 3)+
  
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
                     limits = c(0,1.6),
                     breaks = seq(0,2,0.5)
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
    axis.title.x = element_text(family = "CM", size=20, margin=margin(10,0,0,0)),
    axis.title.y = element_text(family = "CM", size=20, margin=margin(0,10,0,0)),
    legend.title = element_blank(),
    legend.position = c(0.95, 0.95),
    legend.text = element_text(family="CM", size=20),
    legend.text.align = 0,
    axis.line = element_line(color="darkgrey"),
    axis.ticks.y = element_line(color="darkgrey"),
    axis.ticks.x = element_line(color=c("darkgrey", "black", colors[1], colors[2])),
    axis.text.x = element_text(family = "CM", size=16, color=c("darkgrey", "black", colors[1], colors[2])),
    axis.text.y = element_text(family = "CM", size=16, color = "darkgrey")
  )

supplyFunctionEpsilon
ggsave(supplyFunctionEpsilon, file = "supplyFunctionEpsilon.png", height=8, width=16, bg='white')


# plots based on real data ####

# real initial player pool size (from table playerPoolSize)
k0 = 352

# solve equation system for illustrative plot with epsilon 2 as assumption
parameters<-findParameters(k0, 2)

# plot real supply effect 
supplyFunctionReal<-ggplot()+
  
  
  # curve and marks with epsilon = 4
  stat_function(fun=supplyFunction,
                args = list(kmin = kmin, theta = parameters$theta, lambda = parameters$lambda),
                color="black",
                xlim=c(kmin, 2100)
  )+ 
  
  # cosmetics
  scale_x_continuous(expand = c(0,0),
                     breaks = seq(0,2000,100),
                     limits = c(0, 2100)
  )+
  scale_y_continuous(expand = c(0,0),
                     limits = c(0,1.6),
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
    axis.title.x = element_text(family = "CM", size=20, margin=margin(10,0,0,0)),
    axis.title.y = element_text(family = "CM", size=20, margin=margin(0,10,0,0)),
    legend.title = element_blank(),
    legend.position = c(0.95, 0.95),
    legend.text = element_text(family="CM", size=20),
    legend.text.align = 0,
    axis.line = element_line(color="darkgrey"),
    axis.ticks = element_line(color="darkgrey"),
    axis.text.x = element_text(family = "CM", size=16, color=c("darkgrey")),
    axis.text.y = element_text(family = "CM", size=16, color = "darkgrey")
  )

supplyFunctionReal
ggsave(supplyFunctionReal, file = "supplyFunctionReal.png", height=8, width=16, bg='white')


