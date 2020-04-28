#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ================================================================================
# Based on:
#   //github.com/pageauc/pi-timolo
# ================================================================================
# import RPi.GPIO as GPIO
import os
import datetime
import sys
import time
import picamera
import picamera.array
import logging
import modus
import signal
import io
import numpy as np
from fractions import Fraction
from config import *

# ================================================================================
# Constants
# ================================================================================
# Constant for converting Shutter Speed in Seconds to Microseconds
SECONDS2MICRO = 1000000

camNightISO = 800
camNightShutSpeed = 6 * SECONDS2MICRO

# ================================================================================
# System Variables, should not need to be customized
# ================================================================================
appName = "Camera"
appVersion = "0.2"
camera = picamera.PiCamera()
procesTime = 1

# --------------------------------------------------------------------------------
# Globals
# --------------------------------------------------------------------------------
actionCount = 0
imageCount = 1
motion_detected = False
last_still_capture_time = datetime.datetime.now()
imgExtension = "jpg"

# --------------------------------------------------------------------------------
# Logging
# --------------------------------------------------------------------------------
logging.basicConfig(
    level=logging.WARNING,
    format="[%(levelname)-8s] %(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.setLevel(appLoggingLevel)


__MODI = [
    modus.MOTIONIMAGE,
    modus.MOTIONVIDEO,
    modus.PIRIMAGE,
    modus.PIRVIDEO,
    modus.TESTIMAGE,
    modus.TIMELAPSE,
]

# --------------------------------------------------------------------------------
# Setup PIR
# --------------------------------------------------------------------------------
# Setting the GPIO (General Purpose Input Output) pins up so we can detect if they are HIGH or LOW (on or off)
# GPIO.setmode(GPIO.BOARD)
# GPIO.setup(pirSensorPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# --------------------------------------------------------------------------------
# The 'analyse' method gets called on every frame processed while picamera
# is recording h264 video.
# It gets an array (see: "a") of motion vectors from the GPU.
# --------------------------------------------------------------------------------
def check_folders():
    """
    This procedure will check for the image and video folders. If they don't exist,
    the procedure will create them.
    """

    logger.info("check_folders")

    # Checks for image folders and creates them if they do not already exist.
    if (
        appModus == modus.TESTIMAGE
        or appModus == modus.MOTIONIMAGE
        or appModus == modus.TIMELAPSE
    ):
        if not os.path.isdir(gbImageDir):
            logger.debug("Creating image folder {}".format(gbImageDir))
            os.makedirs(gbImageDir)
        logger.debug("Folder {}".format(gbImageDir))

    if appModus == modus.MOTIONVIDEO:
        if not os.path.isdir(gbVideoDir):
            logger.debug("Creating video folder {}".format(gbVideoDir))
            os.makedirs(gbVideoDir)
        logger.debug("Folder {}".format(gbVideoDir))


# --------------------------------------------------------------------------------
def signal_term_handler(signal, frame):

    logger.critical("signal_term_handler")
    # this raises SystemExit(0) which fires all "try...finally" blocks:
    sys.exit(0)


# this is useful when this program is started at boot via init.d
# or an upstart script, so it can be killed: i.e. kill some_pid:
signal.signal(signal.SIGTERM, signal_term_handler)


# --------------------------------------------------------------------------------
def show_time():
    return datetime.datetime.now().strftime(gbDateTimeFormat)


# --------------------------------------------------------------------------------
def ctrl_c():
    logger.critical("ctrl_c")
    # GPIO.cleanup()


# --------------------------------------------------------------------------------
def close_camera():
    logger.info("close_camera")
    camera.close()
    # GPIO.cleanup()
    logger.info("Actions: {}".format(actionCount))
    logger.debug("Camera turned off")


# --------------------------------------------------------------------------------
def init_camera():
    logger.info("init_camera")
    revision = camera.revision
    if revision == "ov5647":
        version = "V1.x"
    elif revision == "imx219":
        version = "V2.x"
    else:
        version = "unknown"
    logger.info("camera version: {}".format(version))
    # Global settings
    camera.resolution = (camHeight, camWidth)
    camera.rotation = camRotation
    camera.vflip = camVFlip
    camera.hflip = camHFlip
    logger.debug("camera.resolution = ({},{})".format(camWidth, camHeight))
    logger.debug("camera.rotation = {}".format(camera.rotation))
    logger.debug("camera.vflip = {}".format(camera.vflip))
    logger.debug("camera.hflip = {}".format(camera.hflip))

    # Specific settings
    # Video settings
    if appModus == modus.MOTIONVIDEO:
        logger.debug("vidVideoTime = {}".format(vidVideoTime))
    # Image settings
    else:
        logger.debug("camAnnotate = {}".format(camAnnotate))
        if camAnnotate:
            camera.annotate_text_size = camAnnotateTextSize
            # camera.annotate_foreground  = camAnnotateForeground
            # camera.annotate_background  = camAnnotateBackground
            logger.debug(
                "camera.annotate_text_size = {}".format(camera.annotate_text_size)
            )
            # logger.info( "camera.annotate_foreground = %s" % ( camera.annotate_foreground ) )
            # logger.info( "camera.annotate_background = %s" % ( camera.annotate_background ) )

        camera.framerate = camFrameRate
        camera.led = camLed

        camera.awb_mode = "auto"
        if camDay:
            camera.exposure_mode = "auto"
        else:
            camera.exposure_mode = "night"

    logger.debug("camera.framerate = {}".format(camera.framerate))
    logger.debug("camera.led = {}".format(camLed))
    logger.debug("camera.exposure_mode = {}".format(camera.exposure_mode))
    logger.debug("camera.awb_mode = {}".format(camera.awb_mode))
    logger.debug("camera.shutter_speed = {}".format(camera.shutter_speed))
    logger.debug("camera.iso = {}".format(camera.iso))
    logger.info("Camera initialized")


# --------------------------------------------------------------------------------


def capture_image(fname):
    """ This procedure will actually take the image and save the image as specified
    by fname

    Args:
        fname   : The filename to save the image
    """
    logger.info("capture_image")
    if camAnnotate:
        camera.annotate_text = show_time()
    logger.debug("image = {}".format(fname))
    camera.capture(fname, imgFormat)


# --------------------------------------------------------------------------------


def write_video(stream):
    """ Write the entire content of the circular buffer to disk. No need to
    lock the stream here as we're definitely not writing to it simultaneously.
    """
    logger.info("write_video")
    with io.open("before.h264", "wb") as output:
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


################################################################################
# Main procedures
################################################################################


def start_test_image():
    """ This will make an image which can be used to position the camera and set
    the configuration.
    """
    logger.info("start_test_image")

    global actionCount

    init_camera()
    logger.debug("Making test image")
    capture_image(fname("test"))
    actionCount += 1
    logger.debug("Test image ended")
    close_camera()


# --------------------------------------------------------------------------------


def start_timelapse():
    """ This will take timelapse images. Images are stored with a sequence number.
    """
    global imageCount
    global actionCount

    logger.info("start_timelapse")
    try:
        init_camera()
        logger.info(
            "This will take approx. {} sec.".format(tlTotalImages * tlTimeBetween)
        )
        imageCount = 0
        while imageCount < tlTotalImages:
            capture_image(
                fname(str(tlSequenceStart + imageCount).zfill(tlSequenceSize))
            )
            logger.debug(
                "TimeLapse {} = {}".format(imageCount, tlSequenceStart + imageCount)
            )
            imageCount += 1
            actionCount += 1
            # Takes roughly 6 seconds to take a picture
            time.sleep(tlTimeBetween - procesTime)

    except KeyboardInterrupt as e:
        ctrl_c()

    finally:
        logger.info("Timelapse has ended.")
        close_camera()


# --------------------------------------------------------------------------------


def start_motion_image():

    logger.info("start_motion_image")

    global motion_detected
    global imageCount
    global actionCount

    init_camera()
    imageCount = 1
    with detect_motion(camera) as output:
        try:
            # record video to nowhere, as we are just trying to capture images:
            camera.start_recording("/dev/null", format="h264", motion_output=output)
            motion_detected = False
            logger.debug("Waiting for motion...")
            while True:
                camera.wait_recording(mtnMinimumStillSec)
                if motion_detected:
                    logger.debug("Stop recording and capture an image...")
                    camera.stop_recording()
                    capture_image(None)
                    imageCount += 1
                    actionCount += 1
                    camera.start_recording(
                        "/dev/null", format="h264", motion_output=output
                    )
                    motion_detected = False
                    logger.debug("Waiting for motion...")

        except KeyboardInterrupt as e:
            ctrl_c()

        finally:
            logger.info("Detect motion has ended.")
            close_camera()


# --------------------------------------------------------------------------------


def start_motion_video():

    logger.info("start_motion_video")

    global motion_detected
    global imageCount
    global actionCount

    init_camera()
    imageCount = 1
    fileStr = gbVideoDir + "/" + "mov" + "%s" + tlSuffix + ".h264"
    with detect_motion(camera) as output:
        try:
            # record video to nowhere, as we are just trying to capture images:
            camera.start_recording("/dev/null", format="h264", motion_output=output)
            motion_detected = False
            logger.debug("Waiting for motion...")
            while True:
                camera.wait_recording(mtnMinimumStillSec)
                if motion_detected:
                    logger.debug("Recording video...")
                    camera.stop_recording()
                    camera.start_recording(fileStr % imageCount, format="h264")
                    camera.wait_recording(vidVideoTime)
                    camera.stop_recording()
                    imageCount += 1
                    actionCount += 1
                    camera.start_recording(
                        "/dev/null", format="h264", motion_output=output
                    )
                    motion_detected = False
                    logger.debug("Waiting for motion...")

        except KeyboardInterrupt as e:
            ctrl_c()

        finally:
            logger.debug("Detect motion has ended.")
            close_camera()


# --------------------------------------------------------------------------------


def start_pir_image():

    logger.info("start_pir_image")

    global imageCount
    global actionCount

    init_camera()
    imageCount = 1
    try:
        # Defining our default states so we can detect a change
        prev_state = False
        curr_state = False
        logger.debug("Waiting for motion...")
        while True:
            time.sleep(0.1)
            prev_state = curr_state
            # Map the state of the camera to our input pins (jumper cables connected to your PIR)
            # curr_state = GPIO.input(pirSensorPin)
            # Checking whether the state has changed
            if curr_state != prev_state:
                # Check if our new state is HIGH or LOW
                new_state = "HIGH" if curr_state else "LOW"
                logger.debug("GPIO pin {} is {}".format(pirSensorPin, new_state))
                if (
                    curr_state
                ):  # State has changed to HIGH, so that must be a trigger from the PIR
                    capture_image(None)
                    imageCount += 1
                    actionCount += 1

    except KeyboardInterrupt as e:
        KeyboardInterrupt()

    finally:
        logger.debug("Detect PIR Image has ended.")
        close_camera()


# --------------------------------------------------------------------------------


def start_pir_motion():
    logger.info("start_pir_motion")


# ================================================================================
# Helper functions
# ================================================================================


def fname(name):
    logger.debug("fname")
    return "{}/{}{}{}{}".format(gbImageDir, tlPrefix, name, tlSuffix, imgExtension)


# ********************************************************************************


class detect_motion(picamera.array.PiMotionAnalysis):
    def analyse(self, a):

        global motion_detected, last_still_capture_time

        if datetime.datetime.now() > last_still_capture_time + datetime.timedelta(
            seconds=mtnMinimumStillSec
        ):
            a = (
                np.sqrt(
                    np.square(a["x"].astype(np.float))
                    + np.square(a["y"].astype(np.float))
                )
                .clip(0, 255)
                .astype(np.uint8)
            )
            # experiment with the following "if" as it may be too sensitive ???
            # if there're more than 10 vectors with a magnitude greater than 60, then motion was detected:
            if (a > mtnMagnitude).sum() > 10:
                logger.debug("Motion detected")
                motion_detected = True


def main():

    global imgExtension

    logger.info("Starting {} {}".format(appName, appVersion))
    logger.info("Modus = {}".format(appModus))

    check_folders()

    if imgFormat == "jpeg":
        imgExtension = ".jpg"
    else:
        imgExtension = "." + imgFormat

    if appModus == modus.TESTIMAGE:
        start_test_image()
    elif appModus == modus.TIMELAPSE:
        start_timelapse()
    elif appModus == modus.MOTIONIMAGE:
        start_motion_image()
    elif appModus == modus.MOTIONVIDEO:
        start_motion_video()
    elif appModus == modus.PIRIMAGE:
        start_pir_image()
    elif appModus == modus.PIRVIDEO:
        start_pir_motion()
    else:
        logger.error("Invalid modus: {}".format(appModus))


# ********************************************************************************


if __name__ == "__main__":
    try:
        main()
    finally:
        logger.debug("{} ended".format(appName))
