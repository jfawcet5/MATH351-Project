""" Testing functionality for Polynomial Interpolation graphical demo

    Sources:
            sorted() function: https://docs.python.org/3/howto/sorting.html
            pygame: https://www.pygame.org/docs/
"""

import pygame
import sys

from pygame.locals import (
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
    K_p,
    K_m,
    K_r,
    KEYDOWN, 
    K_SPACE,
    K_ESCAPE,
    K_RETURN,
    K_BACKSPACE,
    QUIT,
)

FPS = 60

BLACK = (0,0,0)
WHITE = (255,255,255)


####################
# Helper Functions #
####################


def sortList(listToSort):
    # Sorts a list of tuples
    return sorted(listToSort)

def inCircle(rect, pos):
    x,y = pos
    collideX = x > rect.left and x < rect.right
    collideY = y > rect.top and y < rect.bottom
    return collideX and collideY

def moveScreen(grid, points, dx, dy):
    grid.updatePosition(dx, dy)
    for point in points:
        point.move((point.rect.centerx + dx, point.rect.centery + dy))


#####################
# Class Definitions #
#####################


class Point:
    def __init__(self, position, color=BLACK):
        x,y = position
        radius = 5
        self.rect = pygame.Rect(x - radius, y - radius, radius*2, radius*2)
        self.color = color

    def move(self, newpos):
        self.rect.center = newpos

    def __str__(self):
        return f"({self.rect.centerx}, {self.rect.centery})"

    def __repr__(self):
        return f"P{self.__str__()}"

class Grid:
    def __init__(self, size):
        x,y = size[0]*2, size[1]*2
        self.screen = pygame.Surface((x,y))
        self.rect = self.screen.get_rect()

        self.origin = (size[0] // 2, size[1] // 2)

        self.xAxis = pygame.Rect(0, self.rect.top, size[0], size[1])
        self.yAxis = pygame.Rect(0, self.rect.top, size[0], size[1])

        self.__drawGrid__()

    def __drawGrid__(self):
        self.screen.fill(WHITE)
        pygame.draw.line(self.screen, BLACK, self.xAxis.midleft, self.xAxis.midright)
        pygame.draw.line(self.screen, BLACK, self.yAxis.midtop, self.yAxis.midbottom)

    def getOffset(self):
        dx = self.origin[0] - self.yAxis.centerx
        dy = self.origin[1] - self.xAxis.centery
        print(f"dx:{dx}, dy:{dy}")
        return dx,dy

    def updatePosition(self, dx, dy):
        #self.rect.center = (self.rect.centerx + dx, self.rect.centery + dy)
        self.xAxis.centery += dy
        self.yAxis.centerx += dx
        self.__drawGrid__()
        return None

class Menu:
    def __init__(self, size, position):
        self.screen = pygame.Surface(size)
        self.rect = self.screen.get_rect(center=position)

class SideMenu(Menu):
    def __init__(self, screen_size):
        x = screen_size[0]
        y = screen_size[1]
        super(SideMenu, self).__init__((x//4, y), (x//8, y//2))

        self.screen.fill((180, 60, 160))

        rectToDraw = pygame.Rect(1, 1, self.rect.width - 2, (y // 6) - 1)
        pygame.draw.rect(self.screen, WHITE, rectToDraw)

        font = pygame.font.SysFont("QuickType 2", 14, bold=True)
        text = font.render("ADD POINT", False, BLACK)
        textRect = text.get_rect(center=rectToDraw.center)
        textRect.centery = rectToDraw.top + textRect.height + 1
        self.screen.blit(text, textRect)

        pygame.draw.circle(self.screen, BLACK, rectToDraw.center, 5, 0)
        self.circleButton = rectToDraw

    def isClickedOn(self, pos):
        x,y = pos
        return False


#####################
# Testing Functions #
#####################


def testGraphBG(screen, clock):
    tempRect = screen.get_rect() # Get main screen rect object
    screen_size = (tempRect.width, tempRect.height) # Retrieve initial screen size
    center = (screen_size[0] // 2, screen_size[1] // 2)

    point1 = Point(center) # Create a point in the center of the screen
    sm = SideMenu(screen_size) # Create side menu object
    grid = Grid(screen_size) # Create grid object

    mouseDown = False # Used to track mouse clicks
    clickOnCircle = None # If user clicks on a point, that point instance will be stored in this variable

    points = [] # List of all points
    points.append(point1)

    drawLines = False # Temporary. Toggles lines between points
    showMenu = False # Boolean variable handles the state of the sideMenu

    x1,y1 = 0,0 # Mouse (x,y) position on the screen from the previous frame
    
    while True:
        screen.fill(WHITE) # Fill screen with white every frame
        
        screen.blit(grid.screen, grid.rect) # Draw the x,y axes to the screen
        
        for point in points: # Draw each point on the screen
            pygame.draw.circle(screen, point.color, point.rect.center, 5, 0)

        if drawLines and len(points) > 1: # If drawLines is toggled 'True' => Draw lines between points
            li = []
            for point in points:
                li.append(point.rect.center)
            li = sortList(li)
            pygame.draw.lines(screen, (0,0,255), False, li)

        if showMenu: # If showMenu is True, draw side menu on screen
            screen.blit(sm.screen, sm.rect)

        x,y = pygame.mouse.get_pos() # Get updated (x,y) mouse position for current frame
        
        for ev in pygame.event.get(): # Event handling
            if ev.type == KEYDOWN: # If user pressed a key
                if (ev.key == K_RETURN): # If pressed key was 'Return'/'Enter'
                    points.append(Point(center))
                if (ev.key == K_SPACE): # If pressed key was 'space'
                    if drawLines:
                        drawLines = False
                    else:
                        drawLines = True
                if (ev.key == K_BACKSPACE): # If pressed key was 'backspace'
                    if (len(points) > 1):
                        points.pop(-1)
                if (ev.key == K_p):
                    print(points)
                if (ev.key == K_m): # If pressed key was 'm'
                    if showMenu:
                        showMenu = False
                    else:
                        showMenu = True
                if (ev.key == K_r): # If pressed key was 'r'
                    dx,dy = grid.getOffset()
                    moveScreen(grid, points, dx, dy)
                if (ev.key == K_ESCAPE): # If pressed key was 'escape'
                    pygame.quit()
                    sys.exit()
            if (ev.type == MOUSEBUTTONDOWN): # If the user clicked on the screen
                mouseDown = True
                for point in points:
                    if inCircle(point.rect, (x,y)):
                        clickOnCircle = point
                        break
            if (ev.type == MOUSEBUTTONUP):
                #print("MOUSE UP")
                mouseDown = False
                clickOnCircle = None
            if ev.type == QUIT:
                pygame.quit()
                sys.exit()

        if mouseDown: # If the mouse button is currently down
            if clickOnCircle:# If clickOnCircle => user is dragging a point
                clickOnCircle.rect.center = (x,y) # Update the point's position to follow the mouse
                
            else: # User is scrolling on the screen
                dx = x - x1
                dy = y - y1
                moveScreen(grid, points, dx, dy)

        x1,y1 = x,y
        
        pygame.display.update()
        clock.tick(FPS)
    return None

########
# Main #
########

def main():
    pygame.init()

    screen = pygame.display.set_mode((600, 600))
    clock = pygame.time.Clock()

    testGraphBG(screen, clock)
    
    return None

if __name__ == "__main__":
    main()
