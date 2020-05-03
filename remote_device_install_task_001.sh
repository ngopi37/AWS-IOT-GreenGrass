#!/bin/bash
cd /etc/sysctl.d
if [ ! -f 00-defaults.conf ]; then
    echo "Got No file"
    sudo touch 00-defaults.conf
fi
grepOutput=`grep protected_hardlinks 00-defaults.conf|wc -l`
if [ $grepOutput == 0 ]; then
    echo "Got No Match"
    echo 'fs.protected_hardlinks = 1' | sudo tee --append 00-defaults.conf
    echo 'fs.protected_symlinks = 1' | sudo tee --append 00-defaults.conf
fi
cd ~/aws_gg
echo "Downloading core Software  ............."
curl https://raw.githubusercontent.com/tianon/cgroupfs-mount/951c38ee8d802330454bdede20d85ec1c0f8d312/cgroupfs-mount > cgroupfs-mount.sh
sudo chmod +x cgroupfs-mount.sh 
sudo bash ./cgroupfs-mount.sh
echo "Installing Core software  ........."
wget https://s3.amazonaws.com/ggfiles123/greengrass-linux-x86-64-1.6.0.tar.gz -O gg.tar.gz
sudo tar xvzf gg.tar.gz -C /
sudo apt -y install git
git clone https://github.com/aws-samples/aws-greengrass-samples.git 
sudo apt -y install python-pip
pip install awscli --upgrade --user
pip install pandas --user
pip install boto3 --user
cd /greengrass/certs/ 
echo "Installing Certrificate for Greengrass ..."
sudo wget -O root.ca.pem https://www.amazontrust.com/repository/AmazonRootCA1.pem
cd ~/aws_gg
echo "Validation is in progress ...."
echo "Showing the Greengrass directory & files ..."
ls -ltr /greengrass
echo "Showing the Greengrass certificates ..."
ls -ltr /greengrass/certs/
