#!/usr/bin/bash


# directory=/Users/jokedurnez/Documents/accounts/CAFE/CAFE_code/chronicle-preprocessing/
directory=/opt/joke/accounts/CAFE/CAFE_code/chronicle-preprocessing/

# PREPROCESS CHRONICLE --> need bigmem !
docker run --memory=50G -v $directory:/chroniclepy --name chronicle-prep-2 --entrypoint python openlattice/chroniclepy:v1.1-rc1 -u /chroniclepy/preprocess.py  > $directory/logs/chroniclepreprocessing_b.txt 2>&1 &
docker run --memory=30G -v $directory:/chroniclepy --name chronicle-integrate-1 openlattice/shuttle:v0.2 python -u /chroniclepy/integrate.py  > $directory/logs/chronicleintegrating.txt 2>&1 &

# rsync -azP $directory openlattice@bifrost.openlattice.com:/opt/openlattice/chronicle-processing/
scp -i ~/.ssh/openlattice-aws-gc.pem /Users/jokedurnez/Documents/accounts/CAFE/CAFE_code/dashboard/secrets.yaml ubuntu@ec2-52-61-151-182.us-gov-west-1.compute.amazonaws.com:/srv/shiny-server/cafe/
