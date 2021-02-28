import threading
import abc
import enum
from typing import Union, List
import dataclasses
import logging

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

        self.__thread = threading.Thread(target=self.__thread_main)
        self.__thread.daemon = True
        self.__loop_event = threading.Event()
        self.__mode_to_set = None
        self.__exit_requested = False
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
        logging.debug(f"Setting house mode to {mode}")
        with self.__lock:
            self.__mode_to_set = mode
        self.__loop_event.set()

    def refresh(self):
        """ Refreshes the status of the home automation box """

        logging.debug('Refreshing home automation box values...')
        new_status = self.__box.read_status()
        with self.__lock:
            self.__current_status = new_status

    def start(self):
        """ Starts the home automation box background management """

        logging.info("Starting the home automation box background management")

        with self.__lock:
            self.__exit_requested = False

        self.refresh()
        self.__thread.start()

    def stop(self):
        """ Stops the home automation box background management """

        logging.info("Stopping the home automation box background management")

        with self.__lock:
            self.__exit_requested = True

        self.__loop_event.set()

    def __thread_main(self):
        """ Implements the main loop of the background management thread """
        next_refresh = 0
        self.__loop_event.set()

        while True:
            try:
                # Wait for the loop event and reset it if required
                if self.__loop_event.wait(1):
                    self.__loop_event.clear()

                # check exit condition and set mode requests
                set_house_mode = None
                with self.__lock:
                    if self.__exit_requested:
                        return
                    set_house_mode = self.__mode_to_set
                    self.__mode_to_set = None

                if set_house_mode is not None:
                    logging.info(f"Calling home automation box to set house mode to {set_house_mode}")
                    self.__box.write_house_mode(set_house_mode)
                    next_refresh = -5

                if next_refresh > 0:
                    next_refresh -= 1
                elif next_refresh < 0:
                    self.refresh()
                    next_refresh += 1

                if next_refresh == 0:
                    self.refresh()
                    next_refresh = 15
            except Exception as err:
                logging.error(f"Error while processing home automation box communications: {err}")
