# libraries
library(tidyverse)
library(lubridate)

# filenames
args <- commandArgs()
rawfile <- args[6]
cleanfile <- args[7]

participant_decoding_file = "/Users/jokedurnez/Box/CAFE Consortium/ParticipantIDs/participant_master/Participants_2019-03-05.csv"

# read data
MAQ <- read_csv(rawfile) %>% slice(3:n())


clean_id <- function(x){
    if (x == "" | is.na(x)){return (NA)}
    if (str_detect(x, "PM|Pm|pm")){

        pid <- x %>% toupper() %>% str_replace("_", "-")

        # if in perfect shape : return
        if (!is.na(str_match(pid, "PM-\\d{2}-\\d{3,4}.*"))) {
            return(pid)
        }

        # if PM00000
        pidh <- pid %>% str_replace("_", "") %>% str_replace("-", "") %>% str_replace(" ","")
        if (!is.na(str_match(pidh, "PM\\d{5}.*"))){
            return(paste0("PM-", substr(pidh,3,5), "-", substr(pidh, 6, 7)))
        }

        return(pid)
    }
    return(x %>% toupper() %>% str_replace("_", "") %>% str_replace("-", ""))
}

MAQ = MAQ %>% rowwise() %>% mutate(clean_ID = clean_id(Q262))
write_csv(MAQ, cleanfile, na="")
