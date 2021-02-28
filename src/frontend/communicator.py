import threading
import abc
import enum
import time
from typing import Union, List
import dataclasses


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
        pass

    def write_house_mode(self, mode: HouseMode):
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
    def current_status(self):
        with self.__lock:
            return self.__current_status

    def set_house_mode(self, mode: HouseMode):
        # print(f"Setting house mode to {mode}")
        with self.__lock:
            self.__mode_to_set = mode
        # print("setting loop event")
        self.__loop_event.set()
        # print("loop event set")

    def refresh(self):
        # print('Refreshing values...')
        new_status = self.__box.read_status()
        with self.__lock:
            self.__current_status = new_status
            # print('New status = ', new_status)

    def start(self):
        with self.__lock:
            self.__exit_requested = False

        self.refresh()
        self.__thread.start()

    def stop(self):
        with self.__lock:
            self.__exit_requested = True

        self.__loop_event.set()

    def __thread_main(self):
        next_refresh = 0
        self.__loop_event.set()

        while True:
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
                # print(f"Calling domo box to set house mode to {set_house_mode}")
                self.__box.write_house_mode(set_house_mode)
                # print(f"House mode set to {set_house_mode}")
                next_refresh = -5

            # print(f"next_refresh = {next_refresh}")
            if next_refresh > 0:
                next_refresh -= 1
            elif next_refresh < 0:
                self.refresh()
                next_refresh += 1

            if next_refresh == 0:
                self.refresh()
                next_refresh = 15

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
