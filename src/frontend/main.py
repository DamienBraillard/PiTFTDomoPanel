import pygame
import sys
import locale
import logging
import logging.config
from typing import Optional
import config
from screen import Screen
from main_screen import MainScreen
from communicator import Communicator
from eedomus_box import EedomusBoxInterface
from tft_manager import TftManager


class Frontend:
    def __init__(self):
        # Initialize PyGame
        pygame.init()
        self.__clock = pygame.time.Clock()

        pygame.display.set_caption('Domo panel')
        self.__window_surface: pygame.Surface = pygame.display.set_mode((320, 240))

        # Configure the locale
        if config.LOCALE != "":
            locale.setlocale(locale.LC_ALL, config.LOCALE)

        # Setup the screen management & home automation box communication
        self.__tft_manager = TftManager()
        self.__communicator = Communicator(EedomusBoxInterface())

        # Setup the initial screen
        self.__screen: Optional[Screen] = MainScreen(surface=self.__window_surface,
                                                     communicator=self.__communicator)
        self.__screen.activate(None)

    def run(self):
        """ Executes the PyGame main loop """

        is_running = True
        while is_running:
            time_delta = self.__clock.tick(5) / 1000.0

            # Enable/Disable the screen
            tft_state_changed = self.__tft_manager.update()

            # Start the communicator when the screen goes ON, and stop it when the screen goes OFF
            if tft_state_changed:
                if self.__tft_manager.is_on:
                    self.__communicator.start()
                else:
                    self.__communicator.stop()

            # Handles events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_running = False
                    break
                elif self.__screen is not None:
                    self.__screen.handle_event(event)

            # Handles screen
            if self.__screen is not None:
                next_screen = self.__screen.run(time_delta)
                if next_screen is not None:
                    self.__screen.deactivate()
                    next_screen.activate(self.__screen)
                    self.__screen = next_screen

            # Update the PyGame display
            pygame.display.update()

        # Cleanup on exit
        self.__screen.deactivate()
        self.__communicator.stop()


if __name__ == "__main__":
    try:
        # Configure the logging
        logging.config.dictConfig(config.LOGGING_CONFIG)

        # Run the frontend
        frontend = Frontend()
        frontend.run()
    except Exception:
        logging.exception(f"Fatal error occurred. The application has crashed !")
