#================================================================================
# Based on:
#   //github.com/pageauc/pi-timolo
#================================================================================
import os
import datetime
import time
import picamera
import picamera.array
import logging
import signal
import numpy as np
from fractions import Fraction
from config import *

#Constants
SECONDS2MICRO           = 1000000  # Constant for converting Shutter Speed in Seconds to Microseconds

camNightISO             = 800
camNightShutSpeed       = 6 * SECONDS2MICRO

#================================================================================
# System Variables, should not need to be customized
#================================================================================
appName                 = "Camera"
appVersion              = "0.1"
camera                  = picamera.PiCamera()
procesTime              = 1

#--------------------------------------------------------------------------------
# Globals
#--------------------------------------------------------------------------------
actionCount             = 0
imageCount              = 1
motion_detected         = False
last_still_capture_time = datetime.datetime.now()
imgExtension            = "jpg"

#--------------------------------------------------------------------------------
# Logging
#--------------------------------------------------------------------------------
logging.basicConfig( level = logging.INFO, format = "[%(levelname)-8s] %(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S" )
logger = logging.getLogger( __name__ )
logger.disabled = not appLogging
logger.setLevel( appLoggingLevel )

#--------------------------------------------------------------------------------
# The 'analyse' method gets called on every frame processed while picamera
# is recording h264 video.
# It gets an array (see: "a") of motion vectors from the GPU.
#--------------------------------------------------------------------------------
class DetectMotion(picamera.array.PiMotionAnalysis):

  def analyse(self, a):

    global motion_detected, last_still_capture_time

    if datetime.datetime.now() > last_still_capture_time + \
        datetime.timedelta( seconds = mtnMinimumStillSec ):
        a = np.sqrt(
                np.square( a['x'].astype( np.float ) ) +
                np.square( a['y'].astype( np.float ) )
            ).clip( 0, 255 ).astype( np.uint8 )
        # experiment with the following "if" as it may be too sensitive ???
        # if there're more than 10 vectors with a magnitude greater than 60, then motion was detected:
        if ( a > mtnMagnitude ).sum() > 10:
            logger.info( "Motion detected" )
            motion_detected = True

#--------------------------------------------------------------------------------
def check_config():

    logger.info("Checking configuration")

    # Checks for image folders and creates them if they do not already exist.
    if appModus == modusTESTIMAGE or appModus == modusMOTIONIMAGE or appModus == modusTIMELAPSE:
        if not os.path.isdir(gbImageDir):
            logger.info( "Creating image folder %s" % gbImageDir )
            os.makedirs(gbImageDir)
        logger.info("Folder %s" % gbImageDir)

    if appModus == modusMOTIONVIDEO:
        if not os.path.isdir(gbVideoDir):
            logger.info( "Creating video folder %s" % gbVideoDir )
            os.makedirs(gbVideoDir)
        logger.info("Folder %s" % gbVideoDir)

    return
#--------------------------------------------------------------------------------
def signal_term_handler(signal, frame):

    logger.info( "Shutting down..." )
    # this raises SystemExit(0) which fires all "try...finally" blocks:
    sys.exit(0)

# this is useful when this program is started at boot via init.d
# or an upstart script, so it can be killed: i.e. kill some_pid:
signal.signal(signal.SIGTERM, signal_term_handler)

#--------------------------------------------------------------------------------
def showTime():

    return datetime.datetime.now().strftime( gbDateTimeFormat )

#--------------------------------------------------------------------------------
def CtrlC():
    logger.info("Received KeyboardInterrupt via Ctrl-C")
    pass

#--------------------------------------------------------------------------------
def closeCamera():
    camera.close()
    logger.info("# Actions: %s" % actionCount )
    logger.info("Camera turned off!")

#--------------------------------------------------------------------------------
def initCamera():

    logger.info( "Initializing camera" )

    # Global settings
    camera.resolution           = ( camHeight, camWidth )
    camera.rotation             = camRotation
    camera.vflip                = camVFlip
    camera.hflip                = camHFlip
    logger.info( "camera.resolution = ( %s,%s )" % ( camHeight, camWidth ) )
    logger.info( "camera.rotation = %s" % ( camera.rotation ) )
    logger.info( "camera.vflip = %s" % ( camera.vflip ) )
    logger.info( "camera.hflip = %s" % ( camera.hflip ) )

    # Specific settings
    # Video settings
    if appModus == modusMOTIONVIDEO:
        logger.info("vidVideoTime = %s" % vidVideoTime )
    # Image settings
    else:
        logger.info("camAnnotate = %s" % (camAnnotate))
        if camAnnotate:
            camera.annotate_text_size   = camAnnotateTextSize
            # camera.annotate_foreground  = camAnnotateForeground
            # camera.annotate_background  = camAnnotateBackground
            logger.info("camera.annotate_text_size = %s" % (camera.annotate_text_size))
            # logger.info( "camera.annotate_foreground = %s" % ( camera.annotate_foreground ) )
            # logger.info( "camera.annotate_background = %s" % ( camera.annotate_background ) )

        camera.framerate            = camFrameRate
        camera.led                  = camLed
        logger.info("camera.framerate = %s" % (camera.framerate))
        logger.info("camera.led = %s" % (camLed))

        if camDay:
            camera.exposure_mode    = "auto"
            camera.awb_mode         = "auto"
            # Give the camera time to measure AWB
            # time.sleep( 2 )
        else:
            # Night time low light settings have long exposure times
            # Settings for Low Light Conditions
            # Set a frame rate of 1/6 fps, then set ISO to 800
            camera.framerate        = Fraction( 1, 6 )
            #camera.iso              = camNightISO
            # Give the camera a good long time to measure AWB
            # time.sleep( 30 )
            # Now fix the values
            camera.shutter_speed = camera.exposure_speed
            camera.exposure_mode = 'off'
            g = camera.awb_gains
            camera.awb_mode = 'off'
            camera.awb_gains = g

    # Corrections for light/dark
    if camDay:
        time.sleep(2)
    else:
        camera.iso = camNightISO
        time.sleep(30)

    logger.info( "camera.exposure_mode = %s" % ( camera.exposure_mode ) )
    logger.info( "camera.awb_mode = %s" % ( camera.awb_mode ) )
    # logger.info( "camera.awb_gains = %s" % ( camera.awb_gains ) )
    logger.info( "camera.shutter_speed = %s" % ( camera.shutter_speed ) )
    logger.info( "camera.iso = %s" % ( camera.iso ) )
    logger.info( "Camera initialized" )

#--------------------------------------------------------------------------------
def CaptureImage():
    imageNumber = str( imageCount ).zfill( tlSequenceSize )
    if camAnnotate:
        camera.annotate_text = showTime()
    fileStr = gbImageDir + "/" + tlPrefix + "%s" + tlSuffix + imgExtension
    logger.info( "image = " + fileStr % imageNumber )
    camera.capture( fileStr % imageNumber, imgFormat )

#--------------------------------------------------------------------------------
def write_video(stream):
    # Write the entire content of the circular buffer to disk. No need to
    # lock the stream here as we're definitely not writing to it
    # simultaneously
    with io.open('before.h264', 'wb') as output:
        for frame in stream.frames:
            if frame.frame_type == picamera.PiVideoFrameType.sps_header:
                stream.seek(frame.position)
                break
        while True:
            buf = stream.read1()
            if not buf:
                break
            output.write(buf)
    # Wipe the circular stream once we're done
    stream.seek(0)
    stream.truncate()

#--------------------------------------------------------------------------------
def startTimelapse():

    global imageCount
    global actionCount

    try:
        initCamera()
        logger.info( "Start timelapse" )
        logger.info( "This will take approx. %s sec." % ( tlTotalImages * tlTimeBetween ) )
        imageCount = 1
        while imageCount <= tlTotalImages:
            CaptureImage()
            imageCount += 1
            actionCount += 1
            time.sleep( tlTimeBetween - procesTime )  # Takes roughly 6 seconds to take a picture

    except KeyboardInterrupt as e:
        CtrlC()

    finally:
        logger.info( "Timelapse has ended." )
        closeCamera()

#--------------------------------------------------------------------------------
def startMotionPicture():

    logger.info( "startMotionPicture" )

    global motion_detected
    global imageCount
    global actionCount

    initCamera()
    imageCount = 1
    with DetectMotion(camera) as output:
        try:
            # record video to nowhere, as we are just trying to capture images:
            camera.start_recording( '/dev/null', format = 'h264', motion_output = output )
            motion_detected = False
            logger.info("Waiting for motion...")
            while True:
                camera.wait_recording( mtnMinimumStillSec )
                if motion_detected:
                    logger.info( "Stop recording and capture an image..." )
                    camera.stop_recording()
                    CaptureImage()
                    imageCount += 1
                    actionCount += 1
                    camera.start_recording( '/dev/null', format = 'h264', motion_output = output )
                    motion_detected = False
                    logger.info("Waiting for motion...")

        except KeyboardInterrupt as e:
            CtrlC()

        finally:
            logger.info( "Detect motion has ended." )
            closeCamera()

#--------------------------------------------------------------------------------
def startTestImage():

    global actionCount

    initCamera()
    logger.info( "Making test image" )
    fileStr = gbImageDir + "/" + tlPrefix + "%s" + tlSuffix + imgExtension
    camera.annotate_text = showTime()
    imageNumber = "test"
    logger.info( "image = " + fileStr % imageNumber )
    camera.capture( fileStr % imageNumber )

    actionCount += 1

#--------------------------------------------------------------------------------
def startPIRImage():

    logger.info( "startMotionVideo" )

    try:
        pass

    except KeyboardInterrupt as e:
        KeyboardInterrupt()

    finally:
        logger.info("Detect PIR Image has ended.")
        closeCamera()

#--------------------------------------------------------------------------------
def startPIRMotion():
    pass

#--------------------------------------------------------------------------------
def startMotionVideo():

    logger.info( "startMotionVideo" )

    global motion_detected
    global imageCount
    global actionCount

    initCamera()
    imageCount = 1
    fileStr = gbVideoDir + "/" + "mov" + "%s" + tlSuffix + ".h264"
    with DetectMotion(camera) as output:
        try:
            # record video to nowhere, as we are just trying to capture images:
            camera.start_recording( '/dev/null', format = 'h264', motion_output = output )
            motion_detected = False
            logger.info("Waiting for motion...")
            while True:
                camera.wait_recording( mtnMinimumStillSec )
                if motion_detected:
                    logger.info( "Recording video..." )
                    camera.stop_recording()
                    camera.start_recording( fileStr % imageCount, format = "h264" )
                    camera.wait_recording( vidVideoTime )
                    camera.stop_recording()
                    imageCount += 1
                    actionCount += 1
                    camera.start_recording( '/dev/null', format = 'h264', motion_output = output )
                    motion_detected = False
                    logger.info( "Waiting for motion..." )

        except KeyboardInterrupt as e:
            CtrlC()

        finally:
            logger.info( "Detect motion has ended." )
            closeCamera()

#********************************************************************************
def main():

    global imgExtension

    logger.info( "Starting " + appName + " " + appVersion )
    logger.info( "Modus = %s" % appModus )

    check_config()

    if imgFormat == "jpeg":
        imgExtension = ".jpg"
    else:
        imgExtension = "." + imgFormat

    if appModus == modusTIMELAPSE:
        startTimelapse()
    elif appModus == modusTESTIMAGE:
        startTestImage()
    elif appModus == modusMOTIONIMAGE:
        startMotionPicture()
    elif appModus == modusMOTIONVIDEO:
        startMotionVideo()
    else:
        logger.error( "Invalid modus: %s " % ( appModus ) )

#********************************************************************************

if __name__ == '__main__':
    try:
        main()
    finally:
        logger.info( "%s ended" % appName )
