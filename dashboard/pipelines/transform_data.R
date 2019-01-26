library(tidyverse)
library(lubridate)


# process_activities(data)

## combine everything
process_activities <- function(data){

  relatives <- process_relatives(data)
  device_by_activity <- process_devices(data)
  media_exposure_by_activity <- process_media_exposure(data)
  adults_by_activity <- process_adult_use(data)
  activity <- process_activity(data)
  
  activity <- activity %>%
    left_join(relatives, by = "primary_activity_id") %>%
    left_join(device_by_activity, by = "primary_activity_id") %>%
    left_join(media_exposure_by_activity, by = "primary_activity_id") %>%
    left_join(adults_by_activity, by = "primary_activity_id")

  return(activity)
}

# summarise relatives related to primary activities

process_relatives <- function(data) {
  adults_by_activity <- data$edges$relatives_primary_activity %>%
    # add relatives
    left_join(data$nodes$relatives, by = c(src = "openlattice.@id")) %>%
    # add activities
    left_join(data$nodes$primary_activity, by = c(dst = "openlattice.@id")) %>%
    # summarise
    rename(primary_activity_id = dst) %>%
    group_by(primary_activity_id) %>%
    summarise(
      adult_present = sum(str_detect(ol.name, "Mother|Father|Grandparent|Childcare"), na.rm=TRUE),
      otherkids_present = sum(str_detect(ol.name, "Sibling|kids"), na.rm=TRUE),
      alone = sum(str_detect(ol.name, "Alone"), na.rm=TRUE),
    )
  return(adults_by_activity)
}

# summarise devices by media exposures by activity

process_devices <- function(data){
  device_by_activity <- data$edges$devices_media_exposure %>%
    # add devices
    left_join(data$nodes$devices, by = c(src = "openlattice.@id")) %>%
    # add media_exposure
    left_join(data$nodes$media_exposure, by = c(dst = "openlattice.@id")) %>%
    rename(media_exposure_id = dst) %>%
    # add activities
    left_join(data$edges$media_exposure_primary_activity, by = c(media_exposure_id = "src")) %>%
    left_join(data$nodes$primary_activity, by = c(dst = "openlattice.@id")) %>%
    rename(primary_activity_id = dst) %>%
    # summarise
    group_by(primary_activity_id) %>%
    summarise(
      primary_tv = sum(str_detect(ol.name.x, 'TV'), na.rm=TRUE),
      primary_computer = sum(str_detect(ol.name.x, 'Computer'), na.rm=TRUE),
      primary_smartphone = sum(str_detect(ol.name.x, 'Smartphone'), na.rm=TRUE),
      primary_tablet = sum(str_detect(ol.name.x, 'Tablet'), na.rm=TRUE),
      primary_book = sum(str_detect(ol.name.x, 'Book'), na.rm=TRUE),
      primary_video = sum(str_detect(ol.name.x, 'Video'), na.rm=TRUE),
      primary_console = sum(str_detect(ol.name.x, 'Console'), na.rm=TRUE),
      primary_handheldgame = sum(str_detect(ol.name.x, 'HandheldGamingDevice'), na.rm=TRUE),
      primary_radio = sum(str_detect(ol.name.x, 'RadioCD'), na.rm=TRUE),
      primary_theater = sum(str_detect(ol.name.x, 'Theater'), na.rm=TRUE),
      primary_other = sum(str_detect(ol.name.x, 'Other'), na.rm=TRUE)
    )
  return(device_by_activity)
}

# summarise media exposures by activity

process_media_exposure <- function(data){
  media_exposure_by_activity <- data$edges$media_exposure_primary_activity %>%
    # add media_exposure
    left_join(data$nodes$media_exposure, by = c(src = "openlattice.@id")) %>%
    # add primary activities
    left_join(data$nodes$primary_activity, by = c(dst = "openlattice.@id")) %>%
    # summarise
    rename(primary_activity_id = dst) %>%
    group_by(primary_activity_id) %>%
    summarise(
      background_media_tv = str_detect(ol.type, "television") && str_detect(ol.priority, "secondary"),
      background_media_audio = str_detect(ol.type, "audio") && str_detect(ol.priority, "secondary"),
      background_media_other = str_detect(ol.type, "other") && str_detect(ol.priority, "secondary"),
      primary_media = sum(str_detect(ol.priority, "primary"), na.rm=TRUE),
      primary_media_age_younger = str_detect(ol.category, "Younger") && str_detect(ol.priority, "primary"),
      primary_media_age_older = str_detect(ol.category, "Older") && str_detect(ol.priority, "primary"),
      primary_media_age_adult = str_detect(ol.category, "Adults") && str_detect(ol.priority, "primary"),
      screen = sum(str_detect(ol.type, "television|video|Video|internet"), na.rm=TRUE)
    )
  return(media_exposure_by_activity)
}

# summarise adult coviewing by activity

process_adult_use <- function(data){
  adult_use_by_activity <- data$edges$primary_activity_adult_use %>%
    # add media_exposure
    left_join(data$nodes$primary_activity, by = c(src = "openlattice.@id")) %>%
    # add primary activities
    left_join(data$nodes$adult_use, by = c(dst = "openlattice.@id")) %>%
    # summarise
    rename(primary_activity_id = dst) %>%
    group_by(primary_activity_id) %>%
    summarise(
      adult_use = str_detect(ol.status, "Yes"),
      adult_no_use = str_detect(ol.status, "No")
    )
  return(adult_use_by_activity)
}

# clean up activity data (need to add child ID to find next sleep !)

process_activity <- function(data){
  activity <- data$edges$people_primary_activity %>%
    left_join(data$nodes$people, by = c(src = "openlattice.@id")) %>%
    left_join(data$nodes$primary_activity, by = c(dst = "openlattice.@id")) %>%
    rename(primary_activity_id = dst, child_id = src) %>%
    mutate(
      starttime = ymd_hms(ol.datetimestart),
      endtime = ymd_hms(ol.datetimeend)
      ) %>%
    mutate(duration = as.numeric(endtime - starttime) / 60) %>%
    mutate(duration = ifelse(duration < 0, duration + 24, duration)) %>% arrange(child_id, starttime)

  ## add time to sleep (OMG THIS WAS A DIFFICULT FUNCTION :-o )
  activity <- activity %>% 
    group_by(child_id) %>% 
    nest() %>% 
    mutate(data = map(data, add_time_to_sleep)) %>%
    unnest() %>%
    select("primary_activity_id", "child_id", "time_to_sleep", "starttime", "endtime", "duration")
  return(activity)
}



