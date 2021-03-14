import config
from gpiozero import Device, DigitalInputDevice, DigitalOutputDevice
from gpiozero.pins.mock import MockFactory
from typing import Optional
import subprocess
import logging

LOGGER = logging.getLogger(__name__)


class TftManager:
    def __init__(self):
        if config.MOCK_PINS:
            LOGGER.warning("Using mocked GPIO pins")
            Device.pin_factory = MockFactory()

        LOGGER.debug(f"Setting up PIR sensor on GPIO {config.PIN_PIR}")
        self.__pir = DigitalInputDevice(config.PIN_PIR)

        LOGGER.debug(f"Setting up screen backlight on GPIO {config.PIN_BACKLIGHT}")
        self.__backlight = DigitalOutputDevice(config.PIN_BACKLIGHT)
        self.__backlight.on()

        LOGGER.debug(f"Using X Display '{config.SCREEN_DISPLAY}' and {config.SCREEN_TIMEOUT}s off timeout for screen.")

        self.__is_on: Optional[bool] = None

    @property
    def is_on(self) -> Optional[bool]:
        """ Returns True if the TFT screen is currently ON; otherwise, False """
        return self.__is_on

    def update(self) -> bool:
        """
        Updates the status of the TFT screen.

        returns: True if the state of the screen has changed; otherwise, False.
        """

        try:
            # determine whether the TFT must be ON/OFF
            new_is_on = True
            if config.MOCK_PINS:
                new_is_on = True
            else:
                new_is_on = self.__pir.inactive_time is None or self.__pir.inactive_time < config.SCREEN_TIMEOUT

            # Update the members
            has_changed = new_is_on != self.__is_on
            self.__is_on = new_is_on

            # Toggle the screen ON or OFF if the state changed
            if has_changed:
                LOGGER.info(f"Screen state changed to {'ON' if new_is_on else 'OFF'}")
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
                subprocess.call(f"xset -display {config.SCREEN_DISPLAY} -dpms", shell=True)
            else:
                LOGGER.debug("Disabling display")

                # Turn the backlight OFF
                self.__backlight.off()

                # Execute xset to set the TFT off
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
