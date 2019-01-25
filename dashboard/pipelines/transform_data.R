library(tidyverse)
library(lubridate)

TUD_entities <- c(
  "primary_activity", 
  "survey_metadata", 
  "people", 
  "relatives", 
  "devices", 
  "adult_use", 
  "media_exposure", 
  "locations"
)

# summarise adults related to primary activities
data$nodes$primary_activity %>% 
  # add edges table
  left_join(data$edges$relatives_primary_activity, by = c("openlattice.@id" = "dst")) %>%
  # add relatives table
  left_join(data$nodes$relatives, by = c("src" = "openlattice.@id")) %>%
  # group by primary_activity and count
  group_by(ol.id.x) %>%
  summarise(
    adults = sum(str_detect(ol.name, "Mother|Father|Grandparent|Childcare")),
    otherkids = sum(str_detect(ol.name, "Sibling|kids")),
    alone = sum(str_detect(ol.name, "Alone")),
  )

# summarise media exposures --> later join with primary activity
data$nodes$media_exposure %>% 
  # add edges table
  left_join(data$edges$devices_media_exposure, by = c("openlattice.@id" = "dst")) %>%
  # add devices table
  left_join(data$nodes$devices, by = c("src" = "openlattice.@id"))












# data$nodes$primary_activity["openlattice.@id"]
# data$edges$relatives_primary_activity["dst"]
# 
# out = data$nodes$primary_activity %>% 
#   select('ol.behaviorafter', 
#          'ol.behaviorbefore', 
#          'ol.activity', 
#          'ol.datetimestart', 
#          'ol.datetimeend') %>% 
#   mutate(
#     ol.datetimeend = ymd_hms(ol.datetimeend),
#     ol.datetimestart = ymd_hms(ol.datetimestart),
#     duration = ol.datetimeend-ol.datetimestart
#     ) %>%
#   left_join()
# 
#  %>%
#   mutate(duration = ymd_hms(ol.datetimeend) - ymd_hms(ol.datetimestart))

