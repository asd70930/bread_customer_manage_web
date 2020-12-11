#!/bin/bash

while true
do
  ps -ef | grep "app_1_1.py" | grep -v "grep"
if [ "$?" -eq 1 ]
then
  cd /home/quantum/Downloads/darknet-master
  ./run.sh
  echo "process has been restarted!"
else
  echo "process already started!"
fi
sleep 10
done