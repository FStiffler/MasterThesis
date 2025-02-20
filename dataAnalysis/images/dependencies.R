##### Set dependencies
dependecies <- c("MASS", "tidyverse", "RColorBrewer", "showtext", "wesanderson", "EnvStats", "xtable", "broom", "margins")

##### Install and load packages
missing <- dependecies[!(dependecies %in% installed.packages()[,"Package"])]
if(length(missing)) install.packages(missing)
lapply(dependecies, library, character.only = T)