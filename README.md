# chroniclepy

This repository contains code to preprocess data from the Chronicle app.

## Installing the software

The program is written using docker.  This makes is straightforward to use and only requires installing *one* program.  Visit [docker's homepage](https://www.docker.com/get-started) to install.

After installing, get the chronicle docker container.  Go to a terminal:

    docker pull openlattice/chroniclepy

If that worked, you're ready to preprocess your data !

## Tutorial for preprocessing

#### Get the example data

Open a terminal and go into the directory you want to store the data. For example, my homedirectory is `Users/openlattice`

    cd /Users/openlattice

Clone the github repository (install github if necessary):

    git clone git@github.com:Lattice-Works/chroniclepy.git

Go into the directory above your data.

    cd chroniclepy

And then run (where you replace `/Users/openlattice` with the directory you put the data in):

    docker run \
      -v /Users/openlattice:/Users/openlattice \
      openlattice/chroniclepy \
      preprocessing \
      /Users/openlattice/chroniclepy/examples/rawdata \
      /Users/openlattice/chroniclepy/examples/preprocessed \
      --recodefile=/Users/openlattice/chroniclepy/examples/categorisation.csv \
      --precision=3600 \
      --sessioninterval=60

A little bit of explanation of the parts  of this statement:
- `docker run`: Docker is a service of containers.  The container `openlattice/chronicle` mimicks a linux machine with all the necessary software installed.  Using the command `docker run openlattice/chroniclepy` will try to run the container.  Without arguments, this will give you an error and tell you what other arguments you should and could add.
- `-v somedirectory:somedirectory`: Docker can't access your local files.  This is very handy to re-run your analysis on a different computer since it only depends on itself.  However, that means that you have to tell Docker which folders on your computer it should be allowed to access.  The `-v`-flag tells docker that a mountpoint between the local machine and the container follows.  The part before `:` is the local folder, and the part after `:` is the folder in the container.  The easiest thing is to keep the same name (before and after the `:`) and bind a folder that holds all of the data.  If you'd want to bind different folders, you could add `-v onefolder:onefolder -v otherfolder:otherfolder`.
- `openlattice/chroniclepy`: This is the name of the container.  You can also find some details here: https://hub.docker.com/r/openlattice/chroniclepy/.  If you didn't run `docker pull openlattice/chroniclepy` before, it will automatically pull.
- `preprocessing`: To tell the container to run the preprocessing, put `preprocessing` here.  Replacing this with `summary` instead will summarise the data.
- `/Folderto/rawdata`: This is the folder where the raw data sits (the data you can download on the chronicle website).
- `/Folderto/preprocessed`.  This is the folder where the preprocessed data will go to.
- The next parameters are parameters passed to the program.  The ones we use right now:
    - `--recodefile`: This is a file that has some more information on apps, for example categorisation.  This information will be added to the preprocessed data.
    - `--precision`: This is the precision in seconds.  This example has a precision of 3600s or 1 hour.  This means that when an app was used when the hour was passed (eg. 21.45-22.15), the data will be split up in two lines: `21.45-22.00` and `22.00-22.15`.  This allows to analyse the data by hour of day.
    - `--sessioninterval`: This is the minimal interval (in seconds) of non-activity for an engagement to be considered a *new* engagement.  There can be multiple session intervals defined (i.e. `--sessioninterval=60 --sessioninterval=300`).

When running the preprocessing, the data is transformed into data tables with the following variables:
- *participant_id:* Cut out from the csv name.
- *app_fullname:* The name of the app as it appears on the raw data.
- *date:* The date.
- *start_timestamp:* The starttime of the app usage
- *end_timestamp:* The endtime of the app usage
- *day:* The day of the week.  The week starts on monday, i.e. 0 = Monday, 1 = Tuesday,...
- *weekday:* Whether or not this is a weekday: 0 = Mon-Fri, 1 = Sat+Sun
- *hour:* Hour of day
- *quarter:* Quarter of hour: 0 = first (.00-.15), 1 = second,...
- *newsession_\*:* Whether a new session was initiated with this app usage based on the definition(s) of sessioninterval.  
- ...: the columns in `recodefile` will appear here.
