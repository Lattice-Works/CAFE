library(tidyverse)
library(lubridate)

# filenames
args <- commandArgs()
tud_file <- args[6]
tud_file_cleaned <- args[7]
participant_decoding_file <- args[8]
presurvey_file <- args[9]

# read data
TU <- read_csv(tud_file,
  col_types = cols(
    Progress = col_integer(),
    ActionTime = col_datetime()
    )
)

#######################################
# FILTER TO ONE ENTRY PER DIARY ENTRY #
#######################################

# the following piece of code recodes the PID's
codes <- read_csv(participant_decoding_file)
TU <- TU %>%
    left_join(codes, by = c(PrimaryResponseID = "tud_id")) %>%
    filter(!is.na(study_id))

# this piece of code does the following:
# - sort by action time
# - group by DiaryEntryID:
# - remove deleted DiaryEntryID's

TU_grouped <- TU %>%
  arrange(PrimaryResponseID, ActionTime) %>%
  replace_na(list(Deleted = "false")) %>%
  group_by(DiaryEntryID) %>%
  filter(all(Deleted == "false"))

# keep times from **LAST** entry
TU_times = TU_grouped  %>%
  filter(row_number() == n()) %>%
  ungroup() %>% select(StartTime, EndTime,ResponseId)

# keep questions from most complete entry and then last
TU = TU_grouped %>%
  filter(Progress == max(Progress)) %>%
  filter(row_number() == n()) %>%
  ungroup() %>% select(-c(StartTime, EndTime))

# combine
TU <- TU %>% left_join(TU_times) %>%
  filter(!is.na(StartTime))

####################
# EXTRACT DURATION #
####################

# extract duration
TU = TU %>% mutate(
    starttime = hm(StartTime),
    endtime = hm(EndTime),
    duration = as.numeric(endtime - starttime) / 60,
    duration = ifelse(duration < 0, duration + 24*60, duration),
    ActionDate = floor_date(ActionTime, unit="day")
    ) %>% select(-c(starttime, endtime))

# look at times
counts1 = TU %>% group_by(PrimaryResponseID) %>% summarise(totalh1 = sum(duration/60))

TU = TU %>% left_join(counts1)
print("SUBJECTS WITH 24h of data:") #411 --> 422
print(sum(counts1$totalh1==24,na.rm=TRUE))
print("SUBJECTS WITH < 24h of data:") #455 --> 469
print(sum(counts1$totalh1<24,na.rm=TRUE))
print("SUBJECTS WITH > 24h of data:") #381 --> 374
print(sum(counts1$totalh1>24,na.rm=TRUE))

############################
# SPLIT > 24h by presurvey #
############################

presurveys = read_csv(presurvey_file) %>% arrange(PrimaryResponseID, PS_StartDate)%>%
    group_by(PrimaryResponseID) %>%
    mutate(day = row_number()) %>%
    ungroup()

# TU has 25214 rows

groupers = names(TU)
TU <- TU %>%
  left_join(presurveys, all=TRUE, by=c('tud_ps_id' = 'PrimaryResponseID')) %>%
  replace_na(list(PS_StartDate = as_datetime(0))) %>%
  mutate(counter = ymd_hms(PS_StartDate) < ymd_hms(StartDate)) %>%
  group_by_at(vars(one_of(groupers))) %>%
  summarise(day = ifelse(all(is.na(counter)),1 , sum(counter))) %>%
  ungroup() %>%
  left_join(presurveys)

counts2 = TU %>% group_by(PrimaryResponseID, day) %>% summarise(totalh2 = sum(duration/60))
TU = TU %>% left_join(counts2)

print("SUBJECTS WITH 24h of data:")
print(sum(counts2$totalh2==24,na.rm=TRUE))
print("SUBJECTS WITH < 24h of data:")
print(sum(counts2$totalh2<24,na.rm=TRUE))
print("SUBJECTS WITH > 24h of data:")
print(sum(counts2$totalh2>24,na.rm=TRUE))

############################################
# SPLIT > 24h by filled on different dates #
############################################

TU = TU %>% mutate(ActionDateString = format(ActionDate, format="%D"))
TUr = TU %>% filter(totalh2 > 26)
TUleq = TU %>% filter(totalh2 <= 26)

dates = TUr %>%
    filter(!is.na(clean_id)) %>%
    mutate(ActionDateString = format(ActionDate, format="%D")) %>%
    select(clean_id, ActionDateString, day) %>% unique() %>%
    group_by(clean_id, day) %>%
    mutate(day_filled = 1:n()) %>% ungroup()

TU = TU %>% left_join(dates) %>%
    replace_na(list(day_filled = 1))

counts3 = TU %>%
    group_by(PrimaryResponseID, day, day_filled) %>%
    summarise(totalh = sum(duration/60))
print("SUBJECTS WITH 24h of data:")
print(sum(counts3$totalh==24,na.rm=TRUE))
print("SUBJECTS WITH < 24h of data:")
print(sum(counts3$totalh<24,na.rm=TRUE))
print("SUBJECTS WITH > 24h of data:")
print(sum(counts3$totalh>24,na.rm=TRUE))


###########################
# SPLIT > 24h at midnight #
###########################

TUmore24h = TU %>% group_by(PrimaryResponseID, day_filled, day) %>% filter(sum(duration/60)>26) %>% ungroup()
TUless24h = TU %>% group_by(PrimaryResponseID, day_filled, day) %>% filter(sum(duration/60)<=26) %>% ungroup()

TUmore24h = TUmore24h %>% arrange(PrimaryResponseID, day, day_filled, ActionTime) %>%
  group_by(PrimaryResponseID, day, day_filled, midnight=(StartTime=="00:00")) %>%
  mutate(num_midnight=row_number()) %>% ungroup() %>%
  mutate(num_midnight = ifelse(midnight, num_midnight, NA)) %>%
  fill(num_midnight)

TU = bind_rows(TUmore24h, TUless24h)

counts4 = TU %>%
  group_by(PrimaryResponseID, day, day_filled, num_midnight) %>%
  summarize(totalh = sum(duration)/60)
print("SUBJECTS WITH 24h of data:")
print(sum(counts4$totalh==24,na.rm=TRUE))
print("SUBJECTS WITH < 24h of data:")
print(sum(counts4$totalh<24,na.rm=TRUE))
print("SUBJECTS WITH > 24h of data:")
print(sum(counts4$totalh>24,na.rm=TRUE))

#############################
# SPLIT > 24h over midnight #
#############################

TU <- TU %>% mutate(
    startfixed = StartTime,
    endfixed = EndTime
)

# TUmore24h = TU %>% group_by(PrimaryResponseID, day_filled, day, num_midnight) %>% filter(sum(duration/60)>26) %>% ungroup()
# TUless24h = TU %>% group_by(PrimaryResponseID, day_filled, day, num_midnight) %>% filter(sum(duration/60)<=26) %>% ungroup() %>%
#     mutate(
#         startfixed = StartTime,
#         endfixed = EndTime
#     )
#
# TUmore24h <- TUmore24h %>%
#   mutate(
#     startfixed = ifelse(hm(StartTime)>hm(EndTime), paste(StartTime, "00:00", sep="; "), ""),
#     endfixed = ifelse(hm(StartTime)>hm(EndTime), paste("00:00", EndTime, sep="; "), ""),
#     daysplit = ifelse(hm(StartTime)>hm(EndTime), paste("1", "2", sep="; "), NA)
#   ) %>%
#   mutate(
#     startfixed = str_split(startfixed, "; "),
#     endfixed = str_split(endfixed, "; "),
#     daysplit = str_split(daysplit, "; ")) %>%
#   unnest() %>%
#   mutate(
#     startfixed = ifelse(startfixed=="", as.character(StartTime), startfixed),
#     endfixed = ifelse(endfixed=="", as.character(EndTime), endfixed),
#     daysplit = as.integer(daysplit)
#   ) %>% fill(daysplit) %>% replace_na(list(daysplit = 1))
#
# daysplit = TUmore24h$daysplit
# TUmore24h$newday = 1
# for (day in 2:(length(daysplit))){
#   if (is.na(TUmore24h$PrimaryResponseID[day])){next}
#   if (is.na(TUmore24h$PrimaryResponseID[day-1])){next}
#   if (!(TUmore24h$PrimaryResponseID[day] == TUmore24h$PrimaryResponseID[day-1])){
#     TUmore24h$newday[day] = 1
#   } else {
#     if (daysplit[day] == daysplit[day-1]){
#       TUmore24h$newday[day] = TUmore24h$newday[day-1]
#     } else if (daysplit[day] > daysplit[day-1]) {
#       TUmore24h$newday[day] = TUmore24h$newday[day-1]+1
#     } else {
#       TUmore24h$newday[day] = TUmore24h$newday[day-1]
#     }
#   }
# }
#
# TU = bind_rows(TUmore24h, TUless24h)
#
# counts5 = TU %>% group_by(PrimaryResponseID, day, ActionDate, num_midnight, newday) %>% summarise(totalh = sum(duration/60))
# print("SUBJECTS WITH 24h of data:")
# print(sum(counts5$totalh==24,na.rm=TRUE))
# print("SUBJECTS WITH < 24h of data:")
# print(sum(counts5$totalh<24,na.rm=TRUE))
# print("SUBJECTS WITH > 24h of data:")
# print(sum(counts5$totalh>24,na.rm=TRUE))

TU$unique_id = 1:(dim(TU)[1])

write_csv(TU, tud_file_cleaned, na="")
