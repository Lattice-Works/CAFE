# libraries
library(tidyverse)
library(lubridate)
library(readxl)
library(stringi)

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
MAQ <- tibble()
for (file in rawfiles){
  if (endsWith(file, "csv")){
    thisMAQ <- read_csv(file) %>% slice(3:n())
  } else {
    thisMAQ <- read_excel(file) %>% slice(3:n())
  }
  MAQ <- rbind(MAQ, thisMAQ)  
}

if ("Q71_1" %in% names(MAQ)){
  MAQ <- MAQ %>% mutate(
    Q71_1 = iconv(Q71_1,"UTF-8", sub=''),
    Q71_7 = iconv(Q71_1,"UTF-8", sub='')
  )
}

if (!(is.na(demographyfile) | demographyfile == "")){
  demography <- read_csv(demographyfile) %>% group_by(appcode) %>%
    filter(row_number() == n()) %>% ungroup()
  MAQ <- MAQ %>% left_join(demography, by = c("Q281" = 'appcode'))
}

participants <- read_csv(participant_decoding_file)
participants <- participants %>% replace_na(list(respondent_id = 1))

MAQ <- MAQ %>% drop_na(id_column) %>%
  rename(maq_id = id_column) %>%
  left_join(participants, by = "maq_id") %>%
    rowwise() %>%
  mutate(respondent_id = paste0(child_id, respondent_id, collapse="-"))

write_csv(MAQ, cleanfile, na="")
