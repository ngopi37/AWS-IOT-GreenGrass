#!/bin/bash

python createGGCoreGroup.py >& outputlog.txt
echo "Group details configured ......"
cat outputlog.txt
sudo cp config.json /greengrass/config/config.json
sudo cp iot-pem-crt /greengrass/certs/iot-pem-crt
sudo cp iot-pem-key /greengrass/certs/iot-pem-key
echo "Starting Greengrass service ....."
cd /greengrass/ggc/core/ 
sudo ./greengrassd start