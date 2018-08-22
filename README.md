# chroniclepy

This repository contains code to preprocess data from the Chronicle app.

## Installing the software

The program is written using docker.  This makes is straightforward to use and only requires installing *one* program.  Visit [docker's homepage](https://www.docker.com/get-started) to install.

After installing, get the chronicle docker container.  Go to a terminal:

    docker pull openlattice/chroniclepy

This will pull our container from https://hub.docker.com/r/openlattice/chroniclepy/.  If that worked, you're ready to preprocess your data !

## Tutorial for preprocessing and summary

### Get the example data

Click the button `clone or download` on github and click `Download ZIP`. Extract.
For what's next, we're assuming the data is in in `/Users/openlattice/chroniclepy/examples/`.   For your local application, replace `/Users/openlattice/chroniclepy/examples/` with the directory you put the data in.

### Run preprocessing and summary

To run the data processing, run in the terminal:

    docker run \
      -v /Users/openlattice/chroniclepy/examples/:/Users/openlattice/chroniclepy/examples/ \
      openlattice/chroniclepy \
      all \
      /Users/openlattice/chroniclepy/examples/rawdata \
      /Users/openlattice/chroniclepy/examples/preprocessed \
      /Users/openlattice/chroniclepy/examples/output

If you'd want to set a folder as an environment variable for easier readability, you could run:

    FOLDER=/Users/openlattice/chroniclepy/examples/

    docker run \
      -v $FOLDER:$FOLDER \
      openlattice/chroniclepy \
      all \
      $FOLDER/rawdata \
      $FOLDER/preprocessed \
      $FOLDER/output


##### A little bit of explanation of the parts  of this statement:
- `docker run`: Docker is a service of containers.  This statement allows to run our container.
- `-v $FOLDER:$FOLDER`: Docker can't access your local files.  This is very handy to re-run your analysis on a different computer since it only depends on itself.  However, that means that you have to tell Docker which folders on your computer it should be allowed to access.  This statement makes sure docker can read/write your files.
- `openlattice/chroniclepy`: This is the name of the container.  
- `all`: To run the everything.  You can also separately run `preprocessing` and `summary`
- `$FOLDER/rawdata`: This is the folder where the raw data sits (the data you can download on the chronicle website).
- `$FOLDER/preprocessed`.  This is the folder where the preprocessed data will go to.
- `$FOLDER/output`.  This is the folder where the preprocessed data will go to.

##### There are a few additional parameters passed to the program.  
- Preprocessing arguments:
    - `--recodefile`: This is a file that has some more information on apps, for example categorisation.  This information will be added to the preprocessed data.  Refer to the example data for the exact format.
    - `--precision`: This is the precision in seconds.  This default is 3600 seconds (1 hour).  This means that when an app was used when the hour was passed (eg. 21.45-22.15), the data will be split up in two lines: *21.45-22.00* and *22.00-22.15*.  This allows to analyze the data by any time unit (eg. seconds for biophysical data, quarters for diary data,...).
    - `--sessioninterval`: This is the minimal interval (in seconds) of non-activity for an engagement to be considered a *new* engagement.  There can be multiple session intervals defined (i.e. `--sessioninterval=60 --sessioninterval=300`).  The default is 60 seconds (1 minute).
- Summary arguments:
    - `--includestartend`: Flag to include the first and last day.  These are cut off by default to keep the summary unbiased (due to missing data in the beginning of the start date or the end of the end date).

An example statement for the example data with all custom arguments:

    docker run \
      -v $FOLDER:$FOLDER \
      openlattice/chroniclepy \
      all \
      $FOLDER/rawdata \
      $FOLDER/preprocessed \
      $FOLDER/output \
      --recodefile=$FOLDER/categorisation.csv \
      --precision=630 \
      --sessioninterval=300 --sessioninterval=3600 \
      --includestartend


## Description of output

#### Preprocessed data

When running the preprocessing, the data is transformed into a table for each participant with the following variables:
- *participant_id:* Cut out from the csv name.
- *app_fullname:* The name of the app as it appears on the raw data.
- *date:* The date.
- *start_timestamp:* The starttime of the app usage
- *end_timestamp:* The endtime of the app usage
- *day:* The day of the week.  The week starts on monday, i.e. 0 = Monday, 1 = Tuesday,...
- *weekday:* Whether or not this is a weekday: 0 = Mon-Fri, 1 = Sat+Sun
- *hour:* Hour of day
- *quarter:* Quarter of hour: 0 = first (.00-.15), 1 = second,...
- *duration:* Duration (in seconds)
- *new_engage_(duration):* Whether a new session was initiated with this app usage based on the definition(s) of sessioninterval.  
- ...: the columns in `recodefile` will appear here.

#### Summary data

The summary analysis created the following tables:
- **summary_daily.csv:** Averages per day.
    - *participant_id*
    - *duration_(mean/std):* mean/std daily usage (seconds)
    - *engage_(duration)_(mean/std):* mean/std number of sessions pre day (wrt newsession definition)
    - *appswitching_per_minute_(mean/std):* mean/std on number of times apps are switched per minute
- **summary_daily_hourly:** Averages per day for each hour of day.
    - *participant_id*
    - *hourly_duration_(h0-h23)_(mean/std)*
    - *hourly_appswitching_(h0-h23)_(mean/std)*
- **summary_daily_custom:** Average usage per day (and per hour of day) for custom categories recorded in `recodefile`.
