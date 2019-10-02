# Camera
Python program to take pictures or movies triggered by motion or time on a RPi with the PiCamera attached. Code also supports the use of a PIR connected to the GPIO pins.

## Prerequisites

### Picamera
Install `picamera`:
```
$ sudo apt-get install python-picamera python3-picamera
```

Be sure the Raspberry Pi camera module is connected and enabled in `raspi-config`:
```
$ sudo raspi-config
```

1. Go to `5 Interfacing Options`
1. Choose `P1 Camera`
1. Choose `Yes`
1. Choose `Ok`
1. Choose `Finish`, and boot your RPi if required

### PIR (optional)
Buy a PIR like the one which can be found at [Kiwi](https://www.kiwi-electronics.nl/pir-bewegingssensor). Connect the pins of the PIR to the GPIO pins on the Raspberry Pi in the following way:

| PIR  | GPIO |
| :--- | ---: |
| VCC  |    2 |
| OUT  |   11 |
| GND  |   14 |

## Installation
Be sure `git` is installed:
```
$ sudo apt install git
```

Now install this camera program:
```
$ git clone https://github.com/Xorfor/Camera.git
```

## Get started
Try this program:

```
$ cd camera
$ python camera.py
```

The output generated will look like:
```
[INFO    ] 2019-09-06 20:33:15 Starting Camera 0.1
[INFO    ] 2019-09-06 20:33:15 Modus = TESTIMAGE
[INFO    ] 2019-09-06 20:33:15 Checking configuration
[INFO    ] 2019-09-06 20:33:15 Creating image folder /mnt/usba/images
[INFO    ] 2019-09-06 20:33:15 Folder /mnt/usba/images
[INFO    ] 2019-09-06 20:33:15 Initializing camera
[INFO    ] 2019-09-06 20:33:15 camera.resolution = ( 1200,720 )
[INFO    ] 2019-09-06 20:33:15 camera.rotation = 0
[INFO    ] 2019-09-06 20:33:15 camera.vflip = False
[INFO    ] 2019-09-06 20:33:15 camera.hflip = False
[INFO    ] 2019-09-06 20:33:15 camAnnotate = False
[INFO    ] 2019-09-06 20:33:15 camera.framerate = 10
[INFO    ] 2019-09-06 20:33:15 camera.led = False
[INFO    ] 2019-09-06 20:33:17 camera.exposure_mode = auto
[INFO    ] 2019-09-06 20:33:17 camera.awb_mode = auto
[INFO    ] 2019-09-06 20:33:17 camera.shutter_speed = 0
[INFO    ] 2019-09-06 20:33:17 camera.iso = 0
[INFO    ] 2019-09-06 20:33:17 Camera initialized
[INFO    ] 2019-09-06 20:33:17 Making test image
[INFO    ] 2019-09-06 20:33:17 image = /mnt/usba/images/imgtest.jpg
[INFO    ] 2019-09-06 20:33:18 Camera ended
```