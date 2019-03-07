#!/usr/bin/bash

directory=/opt/joke/accounts/CAFE/CAFE_code/chronicle-preprocessing/

# PREPROCESS CHRONICLE --> need bigmem !
docker run --memory=50G -v $directory:/chroniclepy --name chronicle-prep-2 --entrypoint python openlattice/chroniclepy:v1.1-rc1 -u /chroniclepy/preprocess.py  > $directory/logs/chroniclepreprocessing_b.txt 2>&1 &
docker run --memory=30G -v $directory:/chroniclepy --name chronicle-integrate-1 openlattice/shuttle:v0.2 python -u /chroniclepy/integrate.py  > $directory/logs/chronicleintegrating.txt 2>&1 &
