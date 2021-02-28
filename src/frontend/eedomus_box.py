from communicator import BoxInterface, BoxStatus, HouseMode
import requests
import time

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
            result = requests.get('http://10.10.10.29/script/?exec=info_display.php').json()

            status = BoxStatus(is_valid=True,
                               lights_on=result["lights_on"],
                               doors_opened=result["doors_opened"],
                               house_mode=self.__str_to_house_mode.get(result["house_mode"], None),
                               outside_temperature=result["outside_temperature"])
            return status
        except Exception as e:
            return BoxStatus(is_valid=False, lights_on=[], doors_opened=[], house_mode=None, outside_temperature=None)

    def write_house_mode(self, mode: HouseMode):
        try:
            api_mode = self.__house_mode_to_str.get(mode, None)

            if api_mode is not None:
                url = f"http://10.10.10.29/script/?exec=info_display.php&set_mode={api_mode}"
                # print(f"Executing http action: {url}")
                requests.get(url)
        except:
            pass

