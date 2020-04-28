# Camera
Python program to take pictures or movies triggered by motion or time on a RPi with the PiCamera attached. Code also supports the use of a PIR connected to the GPIO pins.

## Prerequisites

### Picamera
Install `picamera` and `gpiozero` (Python 3):
```
sudo apt install python3-picamera python3-gpiozero -y
```

Be sure the Raspberry Pi camera module is connected and enabled in `raspi-config`:
```
sudo raspi-config
```

1. Go to `5 Interfacing Options`
1. Choose `P1 Camera`
1. Choose `Yes`
1. Choose `Ok`
1. Choose `Finish`, and boot your RPi if required

### PIR (optional)
Buy a PIR like the one which can be found at [Kiwi](https://www.kiwi-electronics.nl/pir-bewegingssensor). 

Connect the pins of the PIR to the GPIO pins on the Raspberry Pi in the following way:

| PIR  | GPIO |
| :--- | ---: |
| VCC  |    2 |
| OUT  |   11 |
| GND  |   14 |

## Installation
Be sure `git` is installed:
```
sudo apt install git
```

Now install this camera program:
```
git clone https://github.com/Xorfor/Camera.git
```
This will create a `Camera` directory with all the software.

## Update
Go to `Camera` folder and pull new version:
```
cd Camera
git pull
```

## Get started
Try this program:

```
cd Camera
python3 camera.py
```

The output generated will look like (with logging.INFO):
```
[INFO    ] 2020-02-01 21:44:56 Starting Camera 0.2
[INFO    ] 2020-02-01 21:44:56 Modus = TESTIMAGE
[INFO    ] 2020-02-01 21:44:56 Checking configuration
[INFO    ] 2020-02-01 21:44:56 Folder /mnt/usba/images
[INFO    ] 2020-02-01 21:44:56 startTestImage
[INFO    ] 2020-02-01 21:44:56 Initializing camera
[INFO    ] 2020-02-01 21:44:56 camera version: V2.x
[INFO    ] 2020-02-01 21:44:56 camera.resolution = (1920,1080)
[INFO    ] 2020-02-01 21:44:56 camera.rotation = 0
[INFO    ] 2020-02-01 21:44:56 camera.vflip = False
[INFO    ] 2020-02-01 21:44:56 camera.hflip = False
[INFO    ] 2020-02-01 21:44:56 camAnnotate = False
[INFO    ] 2020-02-01 21:44:56 camera.framerate = 10
[INFO    ] 2020-02-01 21:44:56 camera.led = False
[INFO    ] 2020-02-01 21:44:58 camera.exposure_mode = auto
[INFO    ] 2020-02-01 21:44:58 camera.awb_mode = auto
[INFO    ] 2020-02-01 21:44:58 camera.shutter_speed = 0
[INFO    ] 2020-02-01 21:44:58 camera.iso = 0
[INFO    ] 2020-02-01 21:44:58 Camera initialized
[INFO    ] 2020-02-01 21:44:58 Making test image
[INFO    ] 2020-02-01 21:44:58 image = /mnt/usba/images/imgtest_roos.jpg
[INFO    ] 2020-02-01 21:44:59 Test image ended
[INFO    ] 2020-02-01 21:44:59 Actions: 1
[INFO    ] 2020-02-01 21:44:59 Camera turned off
[INFO    ] 2020-02-01 21:44:59 Camera ended
```

## Screen
Under normal conditions, if our connection drops, everything that was running inside of it is terminated. This may result in a lot of hard work being lost. The application `screen` allows us to create a session, which you can detach and re-attach as required. While detached, everything will continue to run as normal. If the connection drops, you can simply re-attach to the screen session and continue where you left off.

Unfortunately, Raspbian does not come with screen preinstalled, so run the following command to install it:
```
sudo apt install screen
```
Once installed, it can be launched by running the following command:
```
screen
```
You will receive a welcome screen. Now you can enter your command, eg:
```
python3 camera.py
```
Once detached, you can return back to the screen session by running the following command:
```
screen -x
```
