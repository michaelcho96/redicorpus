#!/bin/bash
## Configuration script for redicorpus

folder=$(pwd)
mkdir -m 777 ~/redicorpus/
cp -r $folder/ ~/redicorpus/
## Need to add in command to append 'EXPORT RCDIR=~/redicorpus/
( crontab -l | grep -v "python ~/redicorpus/rc_builder.py" ; echo "0 20 * * * python ~/redicorpus/rc_builder.py" ) | crontab -
