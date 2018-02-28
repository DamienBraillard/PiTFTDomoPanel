#!/usr/bin/python3

import RPi.GPIO as GPIO
import subprocess
import time
import argparse
import logging
import logging.handlers

# Constants
PIN_PIR = 4
PIN_BACKLIGHT = 18

# Configurable values
LOG_LEVEL = logging.DEBUG  # Could be e.g. "DEBUG" or "WARNING"
LOG_FILENAME = "/tmp/pirscreenmanager.log"
SCREEN_TIMEOUT = 30
DISPLAY = ":0"

# Log
LOGGER = logging.getLogger(__name__)

def parseCommandLine():
    ''' Parses the command line arguments and returns the argument values '''
    parser = argparse.ArgumentParser(description='PIR sensor screen service')
    parser.add_argument(
        "-l", "--log", 
        help="The path of the log file name; Default '" + LOG_FILENAME + "'.")
    parser.add_argument(
        '-t', "--timeout", type=int,
        help="The screen off timeout after last movement; Default '" + str(SCREEN_TIMEOUT) + "'.")
    parser.add_argument(
        "-d", "--display",
        help="The X display identifier; Default '" + DISPLAY + "'.")
    
    return parser.parse_args()

def setupLoging():
    ''' Configures a new logger and returns it '''
    global LOGGER

    # Prepares log formatting
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')

    # Set default log level
    LOGGER.setLevel(LOG_LEVEL)
    
    # Setup log file rotating handler
    fh = logging.handlers.RotatingFileHandler(
        LOG_FILENAME,
        maxBytes=1024*1024,
        backupCount=3)
    fh.setLevel(LOG_LEVEL)
    fh.setFormatter(formatter)

    # Setup console hanlder
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Apply
    LOGGER.addHandler(fh)
    LOGGER.addHandler(ch)

def setScreen(enabled):
    ''' Activates or deactivates the display '''
    
    if enabled:
        LOGGER.debug("Enabling display")
    else:
        LOGGER.debug("Disabling display")

    try:
        # Now we set the backlight
        GPIO.output(PIN_BACKLIGHT, enabled)

        # Execute xset to set the TFT on/off
        if enabled:
            subprocess.call(
                "xset -display {} -dpms".format(DISPLAY),
                shell=True)
        else:
            subprocess.call(
                "xset -display {} dpms force off".format(DISPLAY),
                shell=True)

    except Exception as err:
        if enabled:
            LOGGER.info("Display enable failed with error '%s'", err)
        else:
            LOGGER.error("Display disable failed with error '%s'", err)        

    else:
        if enabled:
            LOGGER.info("Display enabled")
        else:
            LOGGER.info("Display disabled")


def run():
    ''' Main program loop '''
    try:        
        # Setup the GPIO pins
        LOGGER.debug("Setting up GPIO pins using BMC scheme")
        GPIO.setmode(GPIO.BCM)
        LOGGER.debug("Configuring GPIO %i as input", PIN_PIR)
        GPIO.setup(PIN_PIR, GPIO.IN)
        LOGGER.debug("Configuring GPIO %i as output", PIN_BACKLIGHT)
        GPIO.setup(PIN_BACKLIGHT, GPIO.OUT)
        GPIO.output(PIN_BACKLIGHT, True)
        LOGGER.info("GPIO pins set-up complete.")

        # Initialize runtime values
        timeout = time.time() + SCREEN_TIMEOUT
        last_pir_value = None
        while True:

            # Wait for a change or a time-out and read PIR value
            GPIO.wait_for_edge(PIN_PIR, GPIO.RISING, timeout=1000)
            pir_value = GPIO.input(PIN_PIR) == GPIO.HIGH

            # Log a small message if the value changed
            if pir_value != last_pir_value:
                LOGGER.debug("PIR GPIO changed to '%s'", pir_value)

            # Activates or deactivate the screen with timeout 
            if pir_value:
                # Updates timeout
                timeout = time.time() + SCREEN_TIMEOUT
                LOGGER.debug("Reset screen timeout to %s sec", round(timeout - time.time()))
                # If PIR value changed to high, enable the screen !
                if not last_pir_value:
                    setScreen(True)
            elif timeout > 0:
                LOGGER.debug("Screen timeout in %s sec", round(timeout - time.time()))
                if time.time() > timeout:
                    timeout = 0
                    setScreen(False)

            # Updates the last seen PIR value
            last_pir_value = pir_value

    except KeyboardInterrupt:
        LOGGER.info("Bye !")
    except Exception as err:
        LOGGER.error("Fatal error: %s", err)
    finally:
        setScreen(True)
        LOGGER.debug("Performing GPIO cleanup before leaving")
        GPIO.cleanup()
        LOGGER.info("GPIO cleanup done")



# Entry point
if __name__ == "__main__":
    # Parse the command line arguments
    args = parseCommandLine()
    if args.log:
        LOG_FILENAME = args.log
    if args.timeout:
        SCREEN_TIMEOUT = args.timeout
    if args.display:
        DISPLAY = args.display

    # Initialize the logging
    setupLoging()

    # Print some debug info
    LOGGER.debug("Log file      : '%s'", LOG_FILENAME)
    LOGGER.debug("Screen timeout: %s", SCREEN_TIMEOUT)
    LOGGER.debug("X Display:      '%s'", DISPLAY)

    # Run the main loop
    run()