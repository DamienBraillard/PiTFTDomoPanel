# PiTFTDomoPanel
Raspberry PI + PiTFT based home automation web control panel with screen activated by PIR movement detector

This project was started so that I am able to control some basic functions of my home automation system at home. It uses a RaspberryPi with a 2.8" capacitive touch PiTFT display from Adafruit and a small PIR movement detection module.

The idea is to activate the screen only when movement is detected to avoid useless screen usage and wear when the panel is not in use. The device simply displays a web page from the home automation system.

This projects consists of many parts:
* A 3D box model to house everything
* The list of hardware needed to create the project
* The code that manages the PIR movement detector
* Setup instructions to enable the PiTFT display and setup X to display a web page in kiosk mode

## What does it look like ?
Here are some pictures of the final result:
![Front view](/img/completed-front.jpg)
![Back view](/img/completed-back.jpg)

# Make your own
In the following sections, you will find a detailled description of the steps to make one.

## Bill of materials
To realize this project, the following components are required:
* A Raspberry PI B+ (2 or 3)
* An Adafruit PiTFT PLUS 2.8" capacitive touch TFT screen
  ([Adafruit link](https://www.adafruit.com/product/2423))
* A PIR sensor module from Adafruit or any other vendor ([Adafruit link](https://www.adafruit.com/product/189))
* A 3D printer or access to one
* Some Screws:
    * 4x M4x25mm max with conic head to close the enclosure
    * 4x M3x5mm to tighten the PiTFT to the enclosure
    * 2x M2x5mm to tighten the PIR to the enclosure

## Installation of the RPi base system and the PiTFT
### Install raspbian
First of all, start with a fresh raspbian lite installation.
This project is based on Raspbian stretch.
Go to the [raspbian homepage](https://www.raspberrypi.org/downloads/raspbian/), download the "lite" image and follow the installation guide.

Don't forget to enable ssh and/or finetune your installation with the `raspi-config` utility.

### Configure the PiTFT hardware
Connect to the Raspberry using SSH.

Edit the file **/boot/config.txt**
```
#> sudo nano /boot/config.txt
```

Enable SPI and I2C interfaces by uncommenting the following lines. The former is required to send data to the TFT display, the later to handle the touch screen.
```
dtparam=spi=on
dtparam=i2c_arm=on
```

Then enable the overly for the PiTFT display by adding the following lines at the end of the file.
The first line sets the communication speed to 32Mhz, reduce to 16Mhz if your screen behaves strangly. It also sets the refresh speed to 25 frames per seconds which is enough in our case.
The second line performs a screen rotation of 270° then adapts the touch screen so that it matches the display. It maches the layout of the TFT in the box created for the project but feel free to tweak this.
```
# PiTFT overlay
dtoverlay=pitft28-capacitive,speed=32000000,fps=25
dtoverlay=pitft28-capacitive,rotate=270,touch-swapxy,touch-invy
```
It is important to use two lines because there is a maximum file length of something linke 79 characters and there are too many parameters to fit within this line length limit.

Last remark, the available orientation options are:
* rotate       : Rotation of the screen (0, 90, 180 or 270)
* touch-swapxy : Swaps the X and Y axis of the touch screen
* touch-invx   : Inverses the direction of the X axis (Y axis if swapped)
* touch-invy   : Inverses the direction of the Y axis (X axis if swapped)

Save and close nano 

### Display the boot console on the PiTFT at startup
Here we will modify the kernel boot parameters so that the boot messages are displayed on the PiTFT during boot. This will also give you a login prompt in case something goes really wrong.

Edit the file **/boot/cmdline.txt**
```
#> sudo nano /boot/cmdline.txt
```

Append the following options to the startup command line (after the **bootwait** argument)
```
fbcon=map:10 fbcon=font:VGA8x8
```

Save and close nano

Reboot your Raspberry Pi and enjoy the boot messages:
```
#> sudo reboot
```

You should see the boot screen upon reboot and end up with a prompt once the boot has completed.

## Installation and configuration of the X11 server and the web browser
Now that we have the TFT with it's framebuffer working, we can attack installing and setting up X11.

We will use the following software:
* X11: will be responsible for the graphical environment.
* matchbox: a minimal lightweight window manager.
* nodm: a minimal window manager
* midori: a small webkit based browser
* xset: a X tool that can be used to tweak stuff like the screen saver
* unclutter: a X tool that allows to hide the mouse cursor.

### Install the X11 server and configure the PiTFT framebuffer

Install the basic x11 packages with the matchbox windows manager a browser and the nodm lightweight desktop manager.
```
#> sudo apt install x11-xserver-utils xinit matchbox midori nodm
```

Create a new file **/usr/share/X11/xorg.conf.d/99-pitft.conf**:
```
#> sudo nano /usr/share/X11/xorg.conf.d/99-pitft.conf
```

Enter the following content:
```
Section "Device"
  Identifier "Adafruit PiTFT"
  Driver "fbdev"
  Option "fbdev" "/dev/fb1"
EndSection
```
An important point is the use of "/dev/fb1" here. The PiTFT will settle on the framebuffer 1 as framebuffer 0
is already taken by the HDMI output.

Just for safety, ensure that the file **/usr/share/X11/xorg.conf.d/99-fbturbo.conf** does not exists. If it does, just move it to your home folder for backup.
```
sudo mv /usr/share/X11/xorg.conf.d/99-fbturbo.conf ~
```
You are free to delete it.

## Setup web page auto-start at boot

### Setup nodm display manager

Edit the **/etc/default/nodm** file
```
#> sudo nano /etc/default/nodm
```

Ensure that the following values are set as below
```
NODM_ENABLED=true
NODM_USER=pi
```

### Create the X11 session startup file

Next step will tell the system what should be done when the graphical environment
starts. This is the place where the browser will be started.


Create the file **/home/pi/.xsession**. Beware, do not forget to replace "[YOUR_URL_TO_DISPLAY]"
with the URL that must be displayed on the screen.

```
#> nano /home/pi/.xsession
```

And enter the following content:
``` bash
#!/bin/bash

# disable the DPMS (Energy Star) features
xset -dpms

# disable the screen saver
xset s off

# hide the mouse cursor when not moving
unclutter -idle 0 &

# Run the window manager !
matchbox-window-manager -use_titlebar no &

# Starts the web browser with the desired URL
midori -e Fullscreen -a [YOUR_URL_TO_DISPLAY]

```

Then change the permissions of the file to **700**:
```
#> chmod 700 /home/pi/.xsession
```

### Enable boot to the graphical environment
As the lite version of Raspbian has been installed, it will boot to console by default.
In order to boot into graphical mode, it's necessary to tell **systemctl** to boot
to the graphical target.

To do so, type in the following command: 
```
#> sudo systemctl set-default graphical.target
```

Everything should be working now. The next thing to do is to reboot.
The raspberry should reboot in graphical mode with the Midori browser displaying
the web page in full screen mode.
```
#> sudo reboot
```

## Activating the PIR sensor to activate the screen when a movement is detected
One thing left to do is install and enable the python script that manages the IR movement detector. When movement is detected, the script will enable the script for a configurable duration and then disable it again.

### Installing required python and packages
The script requires **python3.x** and the **RPi.GPIO** python module.
Make sure these are installed using the following command:
```
#> sudo apt install python3 python3-rpi.gpio
```

### Installing the python script and the startup service
It's better to install the python script at a usual location for executables.

Copy the content of he `src/pir` folder to the `/home/pi` home directory of your Raspberry Pi.

Make the **install.sh** script executable and run it:
```
#> chmod -v 755 install.sh
#> ./install.sh
```

This script does the following:
1. Creates the folder */usr/local/bin/pirscreen**
1. Copies the **pirscreenmanager.py** to that folder
1. Makes the copied script executable
1. Copies the **pirscreen.sh** RC script to the **/etc/init.d** folder.
1. Eakes the copied RC script executable
1. Enables the script to run at boot

By default:
* The screen stays on for 30 seconds
* The X display is ':0'
* Log file located at **/tmp/pirscreenmanager.log**

To change any of these options, the **DAEMON_OPTS** variable in the **/etc/init.d/pirscreen.sh** file must be modified.
To do so, edit the file with nano and change it's content:
```
#> sudo nano /etc/init.d/pirscreen.sh
```

## Printing the case
The case that can be seen in the images is available in the `src/enclosure` folder.

The two `.stl` files are provided ready to print.

### Modification of the model before printing
In the case where you whish to change the model, open the source `.scad` with [OpenScad](http://www.openscad.org/).

The file starts with all parameters and two modules, one for each part of the box:
* front_part : The module to render the front part of the box.
* back_part  : The module to render the back part of the box.

Before exporting the STL file, don't forget to leave only the part to export uncommented at the end of the file and do a render (F6).