from __future__ import annotations
from os import path

import pygame
import pygame_gui
import abc
from typing import Union, Type


class Screen(abc.ABC):
    def __init__(self, surface: pygame.Surface):
        self.__surface = surface
        self.__manager = pygame_gui.UIManager(self.__surface.get_size())
        self.__manager.add_font_paths(font_name="roboto",
                                      regular_path=path.join("assets", "fonts", "roboto-regular.ttf"),
                                      bold_path=path.join("assets", "fonts", "roboto-bold.ttf"),
                                      italic_path=path.join("assets", "fonts", "roboto-italic.ttf"),
                                      bold_italic_path=path.join("assets", "fonts", "roboto-bold-italic.ttf"))
        self.__manager.ui_theme.load_theme(path.join("assets", "theme.json"))
        self.__initialized = False
        self.__next_screen: Union[Type[Screen], None] = None

    def _on_create_controls(self, manager: pygame_gui.UIManager):
        pass

    def _on_activated(self, previous_screen: Union[Type[Screen], None]):
        pass

    def _on_deactivated(self):
        pass

    def _on_event(self, event: pygame.event.Event) -> Union[Type[Screen], None]:
        pass

    def _on_loop(self):
        pass

    def _on_draw(self, surface: pygame.Surface):
        self.__manager.draw_ui(surface)

    def activate(self, previous_screen: Union[Type[Screen], None]):
        if not self.__initialized:
            self._on_create_controls(self.__manager)
            self.__initialized = True

        self._on_activated(previous_screen)

    def deactivate(self):
        self._on_deactivated()

    def handle_event(self, event: pygame.event.Event):
        self.__manager.process_events(event)
        next_screen = self._on_event(event)
        if next_screen is not None:
            self.__next_screen = next_screen

    def run(self, time_delta: float) -> Union[Type[Screen], None]:
        self._on_loop()
        self.__manager.update(time_delta)
        self.__surface.fill(pygame.Color('#000000'))
        self._on_draw(self.__surface)

        next_screen = self.__next_screen
        self.__next_screen = None
        return next_screen
