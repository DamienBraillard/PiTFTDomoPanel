import pygame
from pygame import Rect
import pygame_gui
import pygame_gui.elements as elements
from screen import Screen
from communicator import Communicator, HouseMode
from typing import Union, Type
from datetime import datetime


class MainScreen(Screen):
    def __init__(self, surface: pygame.Surface, communicator: Communicator):
        super().__init__(surface)
        self.__communicator = communicator

    def _on_create_controls(self, manager: pygame_gui.UIManager):
        # panels
        elements.UIPanel(relative_rect=Rect((0, 0), (320, 60)),
                         starting_layer_height=1,
                         manager=manager)
        # elements.UIPanel(relative_rect=Rect((0, 70), (110, 170)),
        #                  starting_layer_height=1,
        #                  manager=manager)
        elements.UIPanel(relative_rect=Rect((120, 70), (200, 170)),
                         starting_layer_height=1,
                         manager=manager)

        # Top labels
        self.__time_label = elements.UILabel(relative_rect=Rect((5, 5), (115, 50)),
                                             text="-",
                                             manager=manager,
                                             object_id="@time-label")
        self.__date_labels = [
            elements.UILabel(relative_rect=Rect((130, 6), (60, 16)),
                             text="-",
                             manager=manager,
                             object_id="@date-label"),
            elements.UILabel(relative_rect=Rect((130, 22), (60, 16)),
                             text="-",
                             manager=manager,
                             object_id="@date-label"),
            elements.UILabel(relative_rect=Rect((130, 38), (60, 16)),
                             text="-",
                             manager=manager,
                             object_id="@date-label")
        ]

        self.__temp_label = elements.UILabel(relative_rect=Rect((195, 5), (120, 50)),
                                             text="°C",
                                             manager=manager,
                                             object_id="@temp-label")

        # Mode buttons
        self.__present_button = elements.UIButton(relative_rect=Rect((0, 70), (110, 50)),
                                                  text='Présent',
                                                  manager=manager,
                                                  object_id="@button_present")
        self.__away_button = elements.UIButton(relative_rect=Rect((0, 130), (110, 50)),
                                               text='Absent',
                                               manager=manager,
                                               object_id="@button_away")
        self.__cleaning_button = elements.UIButton(relative_rect=Rect((0, 190), (110, 50)),
                                                   text='Ménage',
                                                   manager=manager,
                                                   object_id="@button_cleaning")

        # Status for doors and lights
        self.__lights_icon_pos = (151, 90)
        self.__doors_icon_pos = (246, 90)

        self.__lights_label_ok = elements.UILabel(relative_rect=Rect((130, 160), (85, 30)),
                                                  text="-",
                                                  manager=manager,
                                                  object_id="@status-label-ok")
        self.__lights_label_warning = elements.UILabel(relative_rect=Rect((130, 160), (85, 30)),
                                                       text="-",
                                                       manager=manager,
                                                       object_id="@status-label-warning")
        self.__lights_label_error = elements.UILabel(relative_rect=Rect((130, 160), (85, 30)),
                                                     text="-",
                                                     manager=manager,
                                                     object_id="@status-label-error")

        self.__doors_label_ok = elements.UILabel(relative_rect=Rect((225, 160), (85, 30)),
                                                 text="-",
                                                 manager=manager,
                                                 object_id="@status-label-ok")
        # self.__doors_label_warning = elements.UILabel(relative_rect=Rect((225, 160), (85, 30)),
        #                                               text="-",
        #                                               manager=manager,
        #                                               object_id="@status-label-warning")
        self.__doors_label_error = elements.UILabel(relative_rect=Rect((225, 160), (85, 30)),
                                                    text="-",
                                                    manager=manager,
                                                    object_id="@status-label-error")

        # Current mode label
        self.__mode_label_present = elements.UILabel(relative_rect=Rect((125, 205), (190, 30)),
                                                     text="Présent",
                                                     manager=manager,
                                                     object_id="@mode-label-present")
        self.__mode_label_away = elements.UILabel(relative_rect=Rect((125, 205), (190, 30)),
                                                  text="Absent",
                                                  manager=manager,
                                                  object_id="@mode-label-away")
        self.__mode_label_cleaning = elements.UILabel(relative_rect=Rect((125, 205), (190, 30)),
                                                      text="Ménage",
                                                      manager=manager,
                                                      object_id="@mode-label-cleaning")

        # images
        self.__image_lights_ok = pygame.image.load("assets/images/lights-ok.png");
        self.__image_lights_warning = pygame.image.load("assets/images/lights-warning.png");
        self.__image_lights_error = pygame.image.load("assets/images/lights-error.png");
        self.__image_doors_ok = pygame.image.load("assets/images/doors-ok.png");
        # self.__image_doors_warning = pygame.image.load("assets/images/doors-warning.png");
        self.__image_doors_error = pygame.image.load("assets/images/doors-error.png");

    def _on_activated(self, previous_screen: Union[Type[Screen], None]):
        pass

    def _on_deactivated(self):
        pass

    def _on_event(self, event: pygame.event.Event) -> Union[Type[Screen], None]:
        if event.type == pygame.USEREVENT and event.user_type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.__present_button:
                self.__communicator.set_house_mode(HouseMode.PRESENT)
            elif event.ui_element == self.__away_button:
                self.__communicator.set_house_mode(HouseMode.AWAY)
            elif event.ui_element == self.__cleaning_button:
                self.__communicator.set_house_mode(HouseMode.CLEANING)
        return None

    def _on_draw(self, surface: pygame.Surface):
        super()._on_draw(surface)

        on_lights = len(self.__communicator.current_status.lights_on)
        if on_lights == 0:
            surface.blit(self.__image_lights_ok, self.__lights_icon_pos)
        elif on_lights == 1:
            surface.blit(self.__image_lights_warning, self.__lights_icon_pos)
        else:
            surface.blit(self.__image_lights_error, self.__lights_icon_pos)

        open_doors = len(self.__communicator.current_status.doors_opened)
        if open_doors == 0:
            surface.blit(self.__image_doors_ok, self.__doors_icon_pos)
        else:
            surface.blit(self.__image_doors_error, self.__doors_icon_pos)

    def _on_loop(self):
        self.__time_label.set_text(datetime.now().strftime("%H:%M"))
        self.__date_labels[0].set_text(datetime.now().strftime("%d"))
        self.__date_labels[1].set_text(datetime.now().strftime("%b"))
        self.__date_labels[2].set_text(datetime.now().strftime("%Y"))
        self.__temp_label.set_text(f"{self.__communicator.current_status.outside_temperature}°C")

        on_lights = len(self.__communicator.current_status.lights_on)
        self.__lights_label_ok.visible = on_lights == 0
        self.__lights_label_ok.set_text(str(on_lights))
        self.__lights_label_warning.visible = on_lights == 1
        self.__lights_label_warning.set_text(str(on_lights))
        self.__lights_label_error.visible = on_lights > 1
        self.__lights_label_error.set_text(str(on_lights))

        open_doors = len(self.__communicator.current_status.doors_opened)
        self.__doors_label_ok.visible = open_doors == 0
        self.__doors_label_ok.set_text(str(open_doors))
        self.__doors_label_error.visible = open_doors != 0
        self.__doors_label_error.set_text(str(open_doors))

        mode = self.__communicator.current_status.house_mode
        self.__mode_label_present.visible = mode == HouseMode.PRESENT
        self.__mode_label_away.visible = mode == HouseMode.AWAY
        self.__mode_label_cleaning.visible = mode == HouseMode.CLEANING
