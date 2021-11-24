""" Polynomial Interpolation Graphical Demo main file

    Authors: Joshua Fawcett, Hans Prieto

    Citations:
            pygame module: https://www.pygame.org/docs/

            roundToNearest() function defined in Graphics.py:
                https://www.kite.com/python/answers/how-to-round-to-the-nearest-multiple-of-5-in-python


    Design influenced by:
        - Desmos: https://www.desmos.com/calculator
        - Geogebra: https://www.geogebra.org/classic?lang=en
"""

import pygame
import sys

from Graphics import InputManager

# Import pygame keyboard event constants
from pygame.locals import (
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
    MOUSEMOTION,
    KEYDOWN,
    K_RIGHT,
    K_LEFT,
    K_SPACE,
    K_ESCAPE,
    K_RETURN,
    K_BACKSPACE,
    QUIT,
)

FPS = 45 # Program runs at 45 frames per second
SCREEN_SIZE = (700,700) # Size of the polynomial interpolation demo window

# This program runs the polynomial interpolation demo
def runDemo(screen, clock):
    # Create input manager object. The input manager contains a graph object which is responsible for drawing the
    # the graph interface to the screen. The input manager updates the graph according to user input
    inputManager = InputManager(SCREEN_SIZE) 
    
    while True:
        # Draw the graph interface onto the main pygame display window stored in 'screen'
        inputManager.graph.displayToScreen(screen)
        
        for ev in pygame.event.get(): # Event handling
            if ev.type == KEYDOWN: # If user pressed a key
                if (ev.key == K_ESCAPE): # If pressed key was 'escape'
                    pygame.quit() # Shut down pygame (uninitialize pygame modules)
                    sys.exit() # Exit the program
                    
                else:
                    inputManager.pressKey(ev) # Send key press to input manager for handling
                    
            if (ev.type == MOUSEBUTTONDOWN): # If a mouse button was pressed down (left click down, scroll wheel)
                x,y = pygame.mouse.get_pos() # Get the current position of the mouse
                
                if (ev.button == 1): # Left click down
                    inputManager.onClick(0, (x,y)) # Notify input manager of left click down at position (x,y)
                    
                elif (ev.button == 4): # Scroll wheel forward
                    # Zoom in
                    inputManager.onMouseScroll(0, (x,y)) # Notify input manager of mouse wheel forward with mouse at position (x,y)
                
                elif (ev.button == 5): # Scroll wheel backward
                    # Zoom out
                    inputManager.onMouseScroll(1, (x,y)) # Notify input manager of mouse wheel backward with mouse at position (x,y)

            if (ev.type == MOUSEBUTTONUP): # If a mouse button was released
                if ev.button == 1: # Released button is left mouse button
                    x,y = pygame.mouse.get_pos() # Get the current position of the mouse
                    inputManager.onClick(1, (x,y)) # Notify input manager of left click up at position (x,y)

            if ev.type == QUIT: # If user closes pygame window
                pygame.quit() # Shut down pygame
                sys.exit() # Exit the program

        # Get the relative movement of the mouse since the previous frame
        dx,dy = pygame.mouse.get_rel()

        # Notify input manager of mouse movement
        inputManager.update((dx,dy))

        pygame.display.update() # Update the main pygame window
        clock.tick(FPS) # Update the pygame clock
    return None

# This is called when the program is executed
def main():
    pygame.init() # Initialize pygame

    screen = pygame.display.set_mode(SCREEN_SIZE) # Create main pygame window
    pygame.display.set_caption('Polynomial Interpolation Demo') # Set window caption
    clock = pygame.time.Clock() # Create pygame clock

    # Run the polynomial interpolation demo
    runDemo(screen, clock)
    return None

if __name__ == "__main__":
    main()

