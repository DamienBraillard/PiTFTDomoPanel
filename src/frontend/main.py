import pygame
import locale
import logging
from typing import Type, Union
from screen import Screen
from main_screen import MainScreen
from communicator import Communicator
from eedomus_box import EedomusBoxInterface
from tft_manager import TftManager

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

# Initialize PyGame
pygame.init()

clock = pygame.time.Clock()

pygame.display.set_caption('Quick Start')
window_surface: pygame.Surface = pygame.display.set_mode((320, 240))

# Initialize fonts
locale.setlocale(locale.LC_ALL, 'fr_CH.utf8')

# Setup the screen management & home automation box communication
tft_manager = TftManager()
communicator = Communicator(EedomusBoxInterface())
communicator.refresh()

# Setup the initial screen
screen: Union[Type[Screen], None] = MainScreen(surface=window_surface, communicator=communicator)
screen.activate(None)

# PyGame main loop
isRunning = True
while isRunning:
    time_delta = clock.tick(60) / 1000.0

    # Enable/Disable the screen
    if tft_manager.update():
        # Start the communicator when the screen goes ON, and stop it when the screen goes OFF
        if tft_manager.is_on:
            communicator.start()
        else:
            communicator.stop()

    # Handles events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False
            break
        elif screen is not None:
            screen.handle_event(event)

    # Handles screen
    if screen is not None:
        next_screen = screen.run(time_delta)
        if next_screen is not None:
            screen.deactivate()
            next_screen.activate(screen)
            screen = next_screen

    # Update the PyGame display
    pygame.display.update()

# Cleanup on exit
screen.deactivate()
communicator.stop()
