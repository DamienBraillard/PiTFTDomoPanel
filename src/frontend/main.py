import pygame
import locale
import pygame_gui
from typing import Type, Union
from screen import Screen
from main_screen import MainScreen
from communicator import Communicator
from eedomus_box import EedomusBoxInterface

pygame.init()

clock = pygame.time.Clock()

pygame.display.set_caption('Quick Start')
window_surface: pygame.Surface = pygame.display.set_mode((320, 240))

# Initialize fonts
locale.setlocale(locale.LC_ALL, 'fr_CH.utf8')

# Setup the initial screen
communicator = Communicator(EedomusBoxInterface())
communicator.start()
screen: Union[Type[Screen], None] = MainScreen(surface=window_surface, communicator=communicator)

screen.activate(None)

# print(pygame.font.get_fonts())

isRunning = True
while isRunning:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False
            break
        elif screen is not None:
            screen.handle_event(event)

    if screen is not None:
        next_screen = screen.run(time_delta)
        if next_screen is not None:
            screen.deactivate()
            next_screen.activate(screen)
            screen = next_screen

    pygame.display.update()

# print("Done !")
screen.deactivate()
communicator.stop()
