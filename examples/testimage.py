"""
    This is the configuration to create a testimage for Camera
"""
import logging
import picamera
import modus

"""
    Application settings
"""
# Logging level. Default = logging.NOTSET
appLoggingLevel = logging.NOTSET
# Modus. Default = modus.TESTIMAGE
appModus = modus.TESTIMAGE

"""
    Global settings
"""
# Directory to store images. Default = "./images"
gbImageDir = "./images"
# Directory to store video files. Default = "./video"
gbVideoDir = "./video"
# Date/time format used in logging and annotation text. Default = "%Y-%m-%d %H:%M:%S"
gbDateTimeFormat = "%Y-%m-%d %H:%M:%S"

"""
    Motion settings
"""
# Motion find compared with x sec. ago? Default = 1
mtnMinimumStillSec = 1
# If there're more than 10 vectors with a magnitude specified, then motion was detected. Default = 80
mtnMagnitude = 80

"""
    PIR settings
"""
# Pin number on the GPIO port. Default = 11
pirSensorPin = 11

"""
    Camera settings
"""
# True = day (light), False = night (dark). Default = True
camDay = True
camHeight = 1080
camWidth = 1920
# Valid values are 0, 90, 180, and 270. Default = 0
camRotation = 0
# Flip image vertically. Default=False
camVFlip = False
# Flip image horizontally. Default=False
camHFlip = False
# Display date/time in image. Default = False
camAnnotate = False
# Default = 32
camAnnotateTextSize = 32
# Default = picamera.Color("#000000") (=black)
camAnnotateBackground = picamera.Color("#000000")
# Default = picamera.Color("#ffffff") (=white)
camAnnotateForeground = picamera.Color("#ffffff")
# Camera led on? Default = False
camLed = False
camFrameRate = 10

"""
    Image settings
"""
# Allowed values: bmp, gif, jpeg, png. Default = jpeg
imgFormat = "jpeg"

"""
    Timelapse settings
"""
# Start image sequence with this number. Default = 1
tlSequenceStart = 1
# Total number of images. Default = 5000
tlTotalImages = 5000
# Time between each picture in seconds. Default = 10
tlTimeBetween = 10
# Prefix for image filename. Default = "img"
tlPrefix = "img"
# Suffix for image filename. Default = ""
tlSuffix = ""
# Length of the sequence number of the image (prefixed with zero's and placed between tlPrefix and tlSuffix). Default = 7
tlSequenceSize = 7

"""
    Video settings
"""
# Length of the video after motion detected in sec. Default = 30
vidVideoTime = 30
