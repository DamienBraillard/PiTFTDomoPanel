import config
from gpiozero import Device, DigitalInputDevice, DigitalOutputDevice
from gpiozero.pins.mock import MockFactory
from typing import Optional
import subprocess
import logging

LOGGER = logging.getLogger(__name__)


class TftManager:
    def __init__(self):
        if config.DEBUG_MODE:
            LOGGER.warning("Using mocked GPIO pins")
            Device.pin_factory = MockFactory()

        LOGGER.debug(f"Setting up PIR sensor on GPIO {config.PIN_PIR}")
        self.__pir = DigitalInputDevice(config.PIN_PIR)

        LOGGER.debug(f"Setting up screen backlight on GPIO {config.PIN_BACKLIGHT}")
        self.__backlight = DigitalOutputDevice(config.PIN_BACKLIGHT)
        self.__backlight.on()

        LOGGER.debug(f"Using X Display '{config.SCREEN_DISPLAY}' and {config.SCREEN_TIMEOUT}s off timeout for screen.")

        self.__is_on: Optional[bool] = None
        self.__forced_is_on: Optional[bool] = None

    @property
    def is_on(self) -> Optional[bool]:
        """ Returns True if the TFT screen is currently ON; otherwise, False """
        return self.__is_on

    def set_forced_mode(self, is_on: Optional[bool]):
        """ For debug purposes this allows to force the status of the TFT on or off """
        LOGGER.debug(f"Forced TFT mode set to {is_on}")
        self.__forced_is_on = is_on

    def update(self) -> bool:
        """
        Updates the status of the TFT screen.

        returns: True if the state of the screen has changed; otherwise, False.
        """

        try:
            # determine whether the TFT must be ON/OFF
            tft_inactive_time = 0
            if not config.DEBUG_MODE:
                tft_inactive_time = self.__pir.inactive_time
                LOGGER.debug(f"TFT inactive time = {tft_inactive_time} (Screen timeout = {config.SCREEN_TIMEOUT})")

            if self.__forced_is_on is not None:
                new_is_on = self.__forced_is_on
            else:
                new_is_on = tft_inactive_time is None or tft_inactive_time < config.SCREEN_TIMEOUT

            # Update the members
            has_changed = new_is_on != self.__is_on
            self.__is_on = new_is_on

            # Toggle the screen ON or OFF if the state changed
            if has_changed:
                LOGGER.info(f"Screen state changed to {self.__is_on}")
                self.set_screen(self.is_on)

            # Done !
            return has_changed
        except Exception as err:
            LOGGER.error(f"Failed to set the TFT on/off: {err}")
            return False

    def set_screen(self, enabled: bool):
        """ Activates or deactivates the display """

        try:

            if enabled:
                LOGGER.debug("Enabling display")

                # Turn the backlight ON
                self.__backlight.on()

                # Execute xset to set the TFT on
                if not config.DEBUG_MODE:
                    subprocess.call(f"xset -display {config.SCREEN_DISPLAY} -dpms", shell=True)
            else:
                LOGGER.debug("Disabling display")

                # Turn the backlight OFF
                self.__backlight.off()

                # Execute xset to set the TFT off
                if not config.DEBUG_MODE:
                    subprocess.call(f"xset -display {config.SCREEN_DISPLAY} dpms force off", shell=True)

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
