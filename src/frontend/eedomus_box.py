from communicator import BoxInterface, BoxStatus, HouseMode
import requests
import logging
import config


class EedomusBoxInterface(BoxInterface):
    def __init__(self):
        self.__str_to_house_mode = {
            "present": HouseMode.PRESENT,
            "away": HouseMode.AWAY,
            "cleaning": HouseMode.CLEANING,
        }
        self.__house_mode_to_str = {v: k for k, v in self.__str_to_house_mode.items()}

    def read_status(self) -> BoxStatus:
        try:
            result = requests.get(config.HOME_AUTOMATION_BOX_URL).json()

            status = BoxStatus(is_valid=True,
                               lights_on=result["lights_on"],
                               doors_opened=result["doors_opened"],
                               house_mode=self.__str_to_house_mode.get(result["house_mode"], None),
                               outside_temperature=result["outside_temperature"])
            return status
        except Exception as err:
            logging.error(f"Failed to read the status from the home automation box: {err}")
            return BoxStatus(is_valid=False, lights_on=[], doors_opened=[], house_mode=None, outside_temperature=None)

    def write_house_mode(self, mode: HouseMode):
        try:
            api_mode = self.__house_mode_to_str.get(mode, None)

            if api_mode is not None:
                url = f"{config.HOME_AUTOMATION_BOX_URL}&set_mode={api_mode}"
                requests.get(url)
        except Exception as err:
            logging.error(f"Failed to set the mode to '{api_mode}' on the home automation box: {err}")

