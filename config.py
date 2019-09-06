import logging
import picamera

# Allowed values for modus
modusTESTIMAGE          = "TESTIMAGE"                   # Test image
modusMOTIONIMAGE        = "MOTIONIMAGE"                 # Make images after motion detection
modusMOTIONVIDEO        = "MOTIONVIDEO"                 # Make video after motion detection
modusPIRIMAGE           = "PIRIMAGE"                    # Make image when PIR is triggered
modusPIRVIDEO           = "PIRVIDEO"                    # Make video when PIR is triggered
modusTIMELAPSE          = "TIMELAPSE"                   # Make timelapse images

# Application settings
appLogging              = True                          # Default = False
appLoggingLevel         = logging.INFO                  # Default = logging.CRITICAL
appModus                = modusTESTIMAGE                # Default = modusTESTIMAGE

# Global settings
gbImageDir              = "/mnt/usba/images"            # Directory to store images for timelapse
gbVideoDir              = "/mnt/usba/video"             # Directory to store video files
gbDateTimeFormat        = "%Y-%m-%d %H:%M:%S"           # Date/time format used in logging and annotation text

# Motion settings
mtnMinimumStillSec      = 1                             # Motion find compared with x sec. ago?
mtnMagnitude            = 80                            # If there're more than 10 vectors with a magnitude specified, then motion was detected:

# Camera settings
camDay                  = True                          # True = day (light), False = night (dark). Default = True
camHeight               = 1200
camWidth                = 720
camRotation             = 0                             # Valid values are 0, 90, 180, and 270. Default = 0
camVFlip                = False                         # Flip image vertically. Default=False
camHFlip                = False                         # Flip image horizontally. Default=False
camAnnotate             = False                         # Display date/time in image. Default = False
camAnnotateTextSize     = 32                            # Default = 32
camAnnotateBackground   = picamera.Color( "#000000" )   # Default = picamera.Color( "#000000" )
camAnnotateForeground   = picamera.Color( "#ff0000" )   # Default = picamera.Color( "#ffffff" )
camLed                  = False                         # Camera led on? Default = False
camFrameRate            = 10

# Image settings
imgFormat               = "jpeg"                        # Allowed values: bmp, gif, jpeg, png. Default = jpeg
tlSequenceStart         = 1                             # Start image sequence with this number. Default = 1
tlTotalImages           = 10                            # Total number of images. Default = 5000
tlTimeBetween           = 10                            # Time between each picture in seconds. Default = 10
tlPrefix                = "img"                         # Prefix for image filename. Default = "img"
tlSuffix                = ""                            # Suffix for image filename. Default = ""
tlSequenceSize          = 7                             # Length of the sequence number of the image ( prefixed with zero's and placed between tlPrefix and tlSuffix). Default = 7

# Video settings
vidVideoTime            = 30                            # Length of the video after motion detected in sec. Default = 30
