library(tidyverse)

##################
## READ IN DATA ##
##################

# read in data
basedir <-
  "/Users/jokedurnez/Downloads/Time use diary set up and analysis/WI time diary (v3)/CAFE Physio and CREATE Analysis 09.21.2018"
setwd(basedir)
TUfile <-
  "Time Diary Follow-Ups w Translations_September 21, 2018_10.26.csv"

TU <- read_csv(
  TUfile,
  col_types = cols(
    StartTime = col_time(),
    EndTime = col_time(),
    RecordedDate = col_datetime(),
    Q34_1 = col_double(), 
    Q47_1 = col_double(), 
    Q10_1 = col_double(), 
    Q26_1 = col_double(), 
    Q39_1 = col_double(), 
    Q56_1 = col_double())
  )
)

################
## CLEAN DATA ##
################

# fill na with empties
TU <- replace_na(TU, replace = list(
    PrimaryResponseID = "", 
    Deleted = "false"
  ))

# remove first header rows
TU <- TU[3:nrow(TU),]

# subset data based and deleted
removeIDs = '1234|asdf|test'
TU = filter(TU,!str_detect(TU$PrimaryResponseID, removeIDs))
TU = filter(TU,!TU$PrimaryResponseID == "")
TU = filter(TU, str_length(TU$PrimaryResponseID) > 4)
TU = filter(TU, TU$Deleted != "true")

# sort by diary entry ID
TU <- arrange(TU, ActionTime)

# parse parent ID
TU$ParentID <- str_detect(TU$PrimaryResponseID,"-02$|_02$|-2$|_2$|-02:space:_02:space:|-2:space:|_2:space:")+1

# get durations
duration = (TU$EndTime-TU$StartTime) / 3600
duration[duration < 0] <- duration[duration < 0] + 24
TU$ActivityDuration = duration

# parse booleans

parse_bool <- function(variable) {
  return (ifelse(variable == "Yes", TRUE, ifelse(variable == "No", FALSE, NA) ))
}

TU$Q8 = parse_bool(TU$Q8)
TU$Q11 = parse_bool(TU$Q11)
TU$Q12 = parse_bool(TU$Q12)
TU$Q20 = parse_bool(TU$Q20)
TU$Q21 = parse_bool(TU$Q21)
TU$Q25 = parse_bool(TU$Q25)
TU$Q27 = parse_bool(TU$Q27)
TU$Q30 = parse_bool(TU$Q30)
TU$Q36 = parse_bool(TU$Q36)
TU$Q38 = parse_bool(TU$Q38)
TU$Q43 = parse_bool(TU$Q43)
TU$Q46 = parse_bool(TU$Q46)
TU$Q50 = parse_bool(TU$Q50)
TU$Q54 = parse_bool(TU$Q54)
TU$Q57 = parse_bool(TU$Q57)
TU$Q58 = parse_bool(TU$Q58)

#####################
## PREPROCESS DATA ##
#####################

# background media
TU$bmedia = (TU$Q11 | TU$Q20 | TU$Q36 | TU$Q43 | TU$Q50 | TU$Q57)
TU$no_bmedia = (!TU$Q11 | !TU$Q20 | !TU$Q36 | !TU$Q43 | !TU$Q50 | !TU$Q57)
TU$bmedia_missing = is.na(TU$bmedia) & is.na(TU$no_bmedia)

# background tv
TU$btv = (TU$Q12 | TU$Q21 | TU$Q27 | TU$Q30 | TU$Q58)
TU$no_btv = (!TU$Q12 | !TU$Q21 | !TU$Q27 | !TU$Q30 | !TU$Q58)
TU$btv_missing = is.na(TU$btv) & is.na(TU$no_btv)

# adult using media or adult on device
TU$adult_phone = (TU$Q8 | TU$Q25 | TU$Q38 | TU$Q46 | TU$Q54)
TU$no_adult_phone = (!TU$Q8 | !TU$Q25 | !TU$Q38 | !TU$Q46 | !TU$Q54)
TU$adult_phone_missing = is.na(TU$adult_phone) & is.na(TU$no_adult_phone)

TU = replace_na(TU, list(Q34_1 = 0, Q47_1 = 0, Q10_1 = 0, Q26_1 = 0, Q39_1 = 0, Q56_1 = 0))
TU = mutate(TU, adult_percent = Q34_1 + Q47_1 + Q10_1 + Q26_1 + Q39_1 + Q56_1)
TU$adult_percent = ifelse(TU$adult_phone == TRUE, TU$adult_percent, 0)

# decode activities
TU$activity = gdata::case(
  TU$Section,
  "feeding" = "Eating-Drinking",
  "bathroom" = "Bathroom-Grooming",
  "childcare" = "Childcare-School",
  "traveling" = "Out of house (traveling-errands)",
  "play_inside" = "Play-recreation inside",
  "play_outside" = "Play-recreation-outside",
  "at_home_chores" = "In house (chores)",
  "media", "Media use",
  "other" = "AOther-don&#39;t Know",
  "sleeping" = "Sleeping-Resting",
  default="ERROR"
  )





