# libraries
library(tidyverse)
library(lubridate)
library(readxl)

# filenames
args <- commandArgs()
rawfile <- args[6]
cleanfile <- args[7]
participant_decoding_file <- args[8]
id_column <- args[9]
demographyfile <- args[10]
rawfile2 <- args[11]

if (!is.na(rawfile2)){
  rawfiles <- c(rawfile, rawfile2)
} else {
  rawfiles <- c(rawfile)
}

# read data
for (file in rawfiles){
  MAQ <- tibble()
  if (endsWith(file, "csv")){
    thisMAQ <- read_csv(file) %>% slice(3:n())
  } else {
    thisMAQ <- read_excel(file)
  }
  MAQ <- rbind(MAQ, thisMAQ)  
}

MAQ <- MAQ[,1:200]

if (!(is.na(demographyfile) | demographyfile == "")){
  demography <- read_csv(demographyfile) %>% group_by(appcode) %>%
    filter(row_number() == n()) %>% ungroup()
  MAQ <- MAQ %>% left_join(demography, by = c("Q281" = 'appcode'))
}

participants <- read_csv(participant_decoding_file)
participants <- participants %>% replace_na(list(respondent_id = 1))

MAQ <- MAQ %>%
  rename(maq_id = id_column) %>%
  left_join(participants, by = "maq_id") %>%
  mutate(respondent_id = paste0(child_id, respondent_id, separator="-"))

write_csv(MAQ, cleanfile, na="")
