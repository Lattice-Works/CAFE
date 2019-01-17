library(tidyverse)

##################
## READ IN DATA ##
##################

read_TU <- function(filename) {
  # grab data
  TU <- read_csv(
    filename,
    col_types = cols(
      StartTime = col_time(),
      EndTime = col_time(),
      RecordedDate = col_datetime()
    )
  )
  
  # save mapping of questions to variable names
  write.csv(get_mapping(TU), "/Users/jokedurnez/Documents/accounts/CAFE/CAFE/time_use_diary/map.csv")
  
  # remove first header rows
  TU <- TU[3:nrow(TU),]
  
  # parse boolean columns as TRUE/FALSE
  booleancols = colnames(TU)[
    str_detect(colnames(TU), "^Q") &
      !str_detect(colnames(TU), "TEXT|Language") &
      !str_detect(colnames(TU), "Q3$")
      ]
  
  for (col in booleancols){
    TU[col] = parse_bool(TU[col])
  }

  return(TU)
}

################
## CLEAN DATA ##
################

clean_TUD <- function(TU){
  # fill na with empties
  TU <- replace_na(TU, replace = list(
      PrimaryResponseID = "", 
      Deleted = "false"
    ))
  
  # subset data based and deleted
  removeIDs = '1234|asdf|test'
  TU = filter(TU,!str_detect(TU$PrimaryResponseID, removeIDs))
  TU = filter(TU,!TU$PrimaryResponseID == "")
  TU = filter(TU, str_length(TU$PrimaryResponseID) > 4)
  
  # remove DiaryEntries that were deleted
  TU = TU %>% group_by(DiaryEntryID) %>% filter(all(Deleted == "false")) %>% ungroup
  
  TU <- arrange(TU, PrimaryResponseID, ActionTime)
  TU = group_by(TU, DiaryEntryID) %>% filter(row_number()==n())
  
  # parse parent ID
  TU$ParentID <- str_detect(TU$PrimaryResponseID,"-02$|_02$|-2$|_2$|-02:space:_02:space:|-2:space:|_2:space:")+1
  
  # get durations
  
  duration <- as.numeric(TU$EndTime-TU$StartTime) / 3600
  duration[duration < 0] <- duration[duration < 0] + 24
  TU$ActivityDuration = duration
  
  return(TU)
}

# this commented code helps finding people with > 24h days
# mins <- TU %>%
#   group_by(PrimaryResponseID) %>%
#   summarise(
#     min = min(StartTime),
#     max = max(EndTime),
#     sum = sum(ActivityDuration)
#     )

# sums = group_by(TU, PrimaryResponseID) %>% summarise(sum=sum(ActivityDuration))
# sub = TU[str_detect(TU$PrimaryResponseID,'PM-064'),] %>% arrange(StartTime)
# sub = sub[c("EndTime", "StartTime", "ActivityDuration", "DiaryEntryID")]
# write.csv(sub, "/Users/jokedurnez/Desktop/subset_WI.csv")

####################################
## PREPROCESS DATA ACTIVITY LEVEL ##
####################################

preprocess_TUD <- function(TU){
    
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
    "media" = "Media use",
    "other" = "AOther-don&#39;t Know",
    "sleeping" = "Sleeping-Resting",
    default="ERROR"
    )
  
  # number of screen devices as primary device
  
  screencols <- c("Q2_1", "Q2_2", "Q2_3", "Q2_4", "Q2_5", "Q2_6", "Q2_7", "Q2_8", "Q2_9", "Q2_10", "Q2_11")
  TU$primary_screen_devices_n <- rowSums(TU[,screencols], na.rm=TRUE)
  
  # adult coviewing
  TU$adult_coviewing = (TU$Q6_1 | TU$Q6_2 | TU$Q6_3 | TU$Q6_6) |
    (TU$Q18_1 | TU$Q18_2 | TU$Q18_3 | TU$Q18_6) |
    (TU$Q41_1 | TU$Q41_2 | TU$Q41_3 | TU$Q41_6) |
    (TU$Q49_1 | TU$Q49_2 | TU$Q49_3 | TU$Q49_6)
  
  # distance to next sleep
  
  next_sleep <- function(StartTime, activity){
    dat <- tibble(StartTime, activity)
    names(dat) <- c("StartTime", "activity")
    
    sleeptimes = dat$StartTime[dat$activity=='sleeping']
    nextsleep <- unlist(lapply(dat$StartTime, function(x) abs(min(x - sleeptimes))/3600))
    nextsleep[dat$activity=='sleeping'] = 0
    return(nextsleep)
  }
  
  TU <- TU %>% group_by(PrimaryResponseID) %>% mutate(time_to_sleep = next_sleep(StartTime, activity))
  
  # adult_percent
  
  TU = mutate(TU, adult_media_percent = Q34_1 + Q47_1 + Q10_1 + Q26_1 + Q39_1 + Q56_1)
  
  # background media
  TU$background_media = TU$Q11 | TU$Q20 | TU$Q36 | TU$Q43 | TU$Q50 | TU$Q57
  TU$background_tv = TU$Q12 | TU$Q21 | TU$Q30 | TU$Q58
  
  return(TU)
}

#########################
## SUMMARY CHILD LEVEL ##
#########################

summarise_TUD <- function(TU){
  TUsummary <- TU %>% 
    group_by(PrimaryResponseID) %>%
    summarise(
      
      total_hours = sum(ActivityDuration, na.rm=TRUE),
      
      # background media
      background_media_hours = sum(ActivityDuration[background_media], na.rm=TRUE),
      background_media_blocks = sum(background_media, na.rm=TRUE),
      
      # background TV
      background_tv_hours = sum(ActivityDuration[background_tv], na.rm=TRUE),
      background_tv_blocks = sum(background_tv, na.rm=TRUE),
      
      # total TV (i.e. previous with primary media == TV)
      total_tv_hours = sum(ActivityDuration[Q12 | Q21 | Q30 | Q58 | Q2_1], na.rm=TRUE),
      total_tv_blocks = sum(Q12 | Q21 | Q30 | Q58 | Q2_1, na.rm=TRUE),
      
      # primary media 
      primary_media_hours = sum(ActivityDuration[str_detect(activity, "media")], na.rm=TRUE),
      primary_media_blocks = sum(str_detect(activity, "media"), na.rm=TRUE),
      primarymedia_books_hours = sum(ActivityDuration[Q3 == "3"], na.rm=TRUE),
      primarymedia_video_hours = sum(ActivityDuration[Q3 == "1"], na.rm=TRUE),
      primarymedia_tvvideo_hours = sum(ActivityDuration[str_detect(Q3, "1|4|8")], na.rm=TRUE),
      primarymedia_videochat_hours = sum(ActivityDuration[Q3 == "5"], na.rm=TRUE),
      primarymedia_screen_hours = sum(ActivityDuration[str_detect(Q3, "1|5|8")], na.rm=TRUE),
      primarymedia_screens_sum = sum(primary_screen_devices_n, na.rm=TRUE),
      primarymedia_screens_avg = mean(primary_screen_devices_n, na.rm=TRUE),
      
      # screens around
      screen_hours = sum(ActivityDuration[str_detect(Q3, "1|5|8") | Q11 | Q20 | Q36 | Q43 | Q50 | Q57 | Q12 | Q21 | Q30 | Q58], na.rm=TRUE),
      screen_blocks = sum(str_detect(Q3, "1|5|8") | Q11 | Q20 | Q36 | Q43 | Q50 | Q57 | Q12 | Q21 | Q30 | Q58, na.rm=TRUE),
      screen_mean_hours = mean(ActivityDuration[str_detect(Q3, "1|5|8") | Q11 | Q20 | Q36 | Q43 | Q50 | Q57 | Q12 | Q21 | Q30 | Q58], na.rm=TRUE),
      screen_median_hours = median(ActivityDuration[str_detect(Q3, "1|5|8") | Q11 | Q20 | Q36 | Q43 | Q50 | Q57 | Q12 | Q21 | Q30 | Q58], na.rm=TRUE),
  
      # screens before sleeping
      screen_1hfromsleeping_hours = sum(ActivityDuration[time_to_sleep<1 & (str_detect(Q3, "1|5|8") | Q11 | Q20 | Q36 | Q43 | Q50 | Q57 | Q12 | Q21 | Q30 | Q58)], na.rm=TRUE),
      screen_1hfromsleeping_blocks = sum(time_to_sleep<1 & (str_detect(Q3, "1|5|8") | Q11 | Q20 | Q36 | Q43 | Q50 | Q57 | Q12 | Q21 | Q30 | Q58), na.rm=TRUE),
      screen_whilefeeding_hours = sum(ActivityDuration[activity == "feeding" & (str_detect(Q3, "1|5|8") | Q11 | Q20 | Q36 | Q43 | Q50 | Q57 | Q12 | Q21 | Q30 | Q58)], na.rm=TRUE),
      
      # adult coviewing
      adult_coviewing_hours = sum(ActivityDuration[adult_coviewing], na.rm=TRUE),  
      adult_coviewing_blocks = sum(adult_coviewing, na.rm=TRUE),  
      
      # sleeping
      sleeping_hours = sum(ActivityDuration[str_detect(activity, "sleeping")],na.rm=TRUE),
      sleeping_blocks = sum(str_detect(activity, "sleeping"), na.rm=TRUE),
      sleeping_btv_hours = sum(ActivityDuration[str_detect(activity, "sleeping") & (Q12 | Q21 | Q30 | Q58)],na.rm=TRUE),
      
      # feeding
      feeding_hours = sum(ActivityDuration[str_detect(activity, "feeding")], na.rm=TRUE),
      feeding_blocks = sum(str_detect(activity, "feeding"), na.rm=TRUE),
      feeding_btv_hours = sum(ActivityDuration[str_detect(activity, "feeding") & (Q12 | Q21 | Q30 | Q58)], na.rm=TRUE),
      
      # activity durations
      bathroom_hours = sum(ActivityDuration[str_detect(activity, "bathroom")], na.rm=TRUE),
      childcare_hours = sum(ActivityDuration[str_detect(activity, "childcare")], na.rm=TRUE),
      travel_hours = sum(ActivityDuration[str_detect(activity, "travel")], na.rm=TRUE),
      playinside_hours = sum(ActivityDuration[str_detect(activity, "play_inside")], na.rm=TRUE),
      playoutside_hours = sum(ActivityDuration[str_detect(activity, "play_outside")], na.rm=TRUE),
      play_hours = sum(ActivityDuration[str_detect(activity, "play")], na.rm=TRUE),
      chores_hours = sum(ActivityDuration[str_detect(activity, "chores")], na.rm=TRUE),
      other_hours = sum(ActivityDuration[str_detect(activity, "other")], na.rm=TRUE),
  
      # activity durations with background media
      bathroom_hours = sum(ActivityDuration[str_detect(activity, "bathroom") & background_media], na.rm=TRUE),
      childcare_hours = sum(ActivityDuration[str_detect(activity, "childcare") & background_media], na.rm=TRUE),
      travel_hours = sum(ActivityDuration[str_detect(activity, "travel") & background_media], na.rm=TRUE),
      playinside_hours = sum(ActivityDuration[str_detect(activity, "play_inside") & background_media], na.rm=TRUE),
      playoutside_hours = sum(ActivityDuration[str_detect(activity, "play_outside") & background_media], na.rm=TRUE),
      play_hours = sum(ActivityDuration[str_detect(activity, "play") & background_media], na.rm=TRUE),
      chores_hours = sum(ActivityDuration[str_detect(activity, "chores") & background_media], na.rm=TRUE),
      other_hours = sum(ActivityDuration[str_detect(activity, "other") & background_media], na.rm=TRUE),
      
      # ages
      age_child_media = sum(ActivityDuration[Q3 == "1"], na.rm=TRUE),
      age_older_media = sum(ActivityDuration[Q3 == "2"], na.rm=TRUE),
      age_younger_media = sum(ActivityDuration[Q3 == "3"], na.rm=TRUE),
      age_adult_media = sum(ActivityDuration[Q3 == "4"], na.rm=TRUE),
    
    )
  return (TUsummary)
}

######################
## HELPER FUNCTIONS ##
######################

strip_import <- function(x) {
  splitter = str_split(x, '\"')[[1]]
  if (length(splitter)<8){
    return (splitter[4])
  } else {
    return (paste0(splitter[4], "_", splitter[8]))
  }
}

get_mapping <- function(TU) {
  mapping <- unlist(lapply(TU[2,], strip_import), use.names=FALSE)
  qs <- unlist(TU[1,], use.names=FALSE)
  nms = names(TU)
  return(
    tibble(
      "header" = nms,
      "mapping" = mapping,
      "question" = qs
    )
  )
}

parse_bool <- function(variable) {
  return (ifelse(variable == "1", TRUE, ifelse(variable == "2", FALSE, NA) ))
}



