#!/bin/bash

# Configuration script for redicorpus
# Takes directory as an input
# Copies redicorpus folder into directory
# Appends export RCDIR to bashrc in home directory
# Appends crontab command to run rcbuilder at 8pm local time

read -e -p "Enter directory for redicorpus" -i "~/redicorpus" RCDIR
export $RCDIR
echo '# Added to support RediCorpus' >> ~/.bashrc
echo 'RCDIR=$RCDIR' >> ~/.bashrc
mkdir -m 777 RCDIR
folder=$(pwd)
cp -r $folder/ RCDIR
( crontab -l | grep -v "python ~/redicorpus/rc_builder.py" ; echo "0 20 * * * python ~/redicorpus/rc_builder.py" ) | crontab -
