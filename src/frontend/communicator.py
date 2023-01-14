import config
import threading
import abc
import enum
from typing import Union, List
import dataclasses
import logging

LOGGER = logging.getLogger(__name__)


class HouseMode(enum.Enum):
    AWAY = "away"
    PRESENT = "present"
    CLEANING = "cleaning"


@dataclasses.dataclass()
class BoxStatus:
    is_valid: bool
    lights_on: List[str]
    doors_opened: List[str]
    outside_temperature: Union[float, None]
    house_mode: Union[HouseMode, None]


class BoxInterface(abc.ABC):
    def read_status(self) -> BoxStatus:
        """ Reads the status of the home automation box """
        pass

    def write_house_mode(self, mode: HouseMode):
        """ writes the house mode of the home automation box """
        pass


class Communicator:
    def __init__(self, box: BoxInterface):
        self.__box = box

        self.__thread = None
        self.__loop_event = threading.Event()
        self.__exit_requested = False
        self.__mode_to_set = None
        self.__lock = threading.Lock()
        self.__current_status = BoxStatus(is_valid=False,
                                          lights_on=[],
                                          doors_opened=[],
                                          outside_temperature=None,
                                          house_mode=None)

    @property
    def current_status(self) -> BoxStatus:
        """ Returns the current status of the home automation box """
        with self.__lock:
            return self.__current_status

    def set_house_mode(self, mode: HouseMode):
        """ Sets the house mode on the home automation box """
        LOGGER.debug(f"Setting house mode to {mode}")
        with self.__lock:
            self.__mode_to_set = mode
        self.__loop_event.set()

    def refresh(self):
        """ Refreshes the status of the home automation box """

        LOGGER.debug('Refreshing home automation box values...')
        new_status = self.__box.read_status()
        with self.__lock:
            self.__current_status = new_status

    def start(self):
        """ Starts the home automation box background management """

        LOGGER.info("Starting the home automation box background management")

        with self.__lock:
            self.__exit_requested = False

        self.refresh()
        self.__thread = threading.Thread(target=self.__thread_main)
        self.__thread.daemon = True
        self.__thread.start()

    def stop(self):
        """ Stops the home automation box background management """

        LOGGER.info("Stopping the home automation box background management")

        with self.__lock:
            self.__exit_requested = True

        self.__loop_event.set()

    def __thread_main(self):
        """ Implements the main loop of the background management thread """
        fast_refresh_counter = 0
        self.__loop_event.set()

        while True:
            try:
                # Wait for the loop event and reset it if required
                wait_time = 1 if fast_refresh_counter > 0 else config.NORMAL_REFRESH_INTERVAL
                LOGGER.debug(f"Next refresh in {wait_time} seconds (fast refresh count = {fast_refresh_counter})")
                if self.__loop_event.wait(wait_time):
                    self.__loop_event.clear()

                # Decrement the refresh counter
                if fast_refresh_counter > 0:
                    fast_refresh_counter -= 1

                # check exit condition and set mode requests
                local_mode_to_set = None
                with self.__lock:
                    if self.__exit_requested:
                        return
                    local_mode_to_set = self.__mode_to_set
                    self.__mode_to_set = None

                if local_mode_to_set is not None:
                    LOGGER.info(f"Calling home automation box to set house mode to {local_mode_to_set}")
                    self.__box.write_house_mode(local_mode_to_set)
                    fast_refresh_counter = config.AFTER_ACTION_FAST_REFRESH_DURATION

                # Refresh
                self.refresh()
            except Exception as err:
                LOGGER.error(f"Error while processing home automation box communications: {err}")
