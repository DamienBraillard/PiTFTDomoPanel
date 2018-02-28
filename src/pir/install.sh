#!/bin/bash

sudo mkdir -v -p /usr/local/bin/pirscreen              
sudo cp -v pirscreenmanager.py /usr/local/bin/pirscreen/pirscreenmanager.py
sudo chmod -v 755 /usr/local/bin/pirscreen/pirscreenmanager.py

sudo cp -v pirscreen.sh /etc/init.d/pirscreen.sh
sudo chmod -v 755 /etc/init.d/pirscreen.sh
sudo update-rc.d pirscreen.sh defaults
