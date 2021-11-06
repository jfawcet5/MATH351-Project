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
GREY = (150,150,150)
BLUE = (50, 20, 170)


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
    def __init__(self, position, color=BLUE):
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

        self.xRange = (-5, 5)
        self.yRange = (-5, 5)

        self.scale = 1

        self.font = pygame.font.SysFont("QuickType 2", 16, bold=True)

        self.__drawGrid__()

    def __drawGrid__(self):
        # Draws the x and y axes and the grid lines
        self.screen.fill(WHITE)
        pygame.draw.line(self.screen, BLACK, self.xAxis.midleft, self.xAxis.midright, 3)
        pygame.draw.line(self.screen, BLACK, self.yAxis.midtop, self.yAxis.midbottom, 3)
 
        dx,dy = self.getOffset()

        valuex = dx // self.xAxis.width
        valuey = dy // self.yAxis.height
        x0 = self.xRange[0] + valuex
        x1 = self.xRange[1] + valuex

        y0 = self.yRange[0] + valuey
        y1 = self.yRange[1] + valuey
        
        numlines = (x1 - x0) + 1

        offsetX = self.xAxis.width / numlines
        offsetY = self.yAxis.height / numlines
        curX = (self.xAxis.centerx) % self.xAxis.width
        curY = (self.yAxis.centery) % self.yAxis.height

        centerPointX = ((x0 + x1) // 2) - valuex
        centerPointY = ((y0 + y1) // 2) - valuey

        curX = curX - offsetX - dx

        i = -1
        while curX > self.xAxis.left:
            pygame.draw.line(self.screen, GREY, (curX, self.yAxis.top), (curX, self.yAxis.bottom), 1)

            v = (centerPointX + i) * self.scale
            self.__labelAxis__(v, (curX, self.xAxis.centery + 4), True)

            i -= 1
            curX = curX - offsetX

        curX = (self.xAxis.centerx) % self.xAxis.width
        curX = curX + offsetX - dx

        i = 1
        while curX < self.xAxis.right:
            pygame.draw.line(self.screen, GREY, (curX, self.yAxis.top), (curX, self.yAxis.bottom), 1)

            v = (centerPointX + i) * self.scale
            self.__labelAxis__(v, (curX, self.xAxis.centery + 4), True)

            i += 1
            curX = curX + offsetX

        curY = (self.yAxis.centery) % self.yAxis.height
        curY = curY + offsetY - dy
        
        i = -1
        while curY < self.yAxis.bottom:
            pygame.draw.line(self.screen, GREY, (self.xAxis.left, curY), (self.xAxis.right, curY), 1)

            v = (centerPointX + i) * self.scale
            self.__labelAxis__(v, (self.yAxis.centerx - 4, curY), False)

            i -= 1
            curY = curY + offsetY

        curY = (self.yAxis.centery) % self.yAxis.height
        curY = curY - offsetY - dy

        i = 1
        while curY > self.yAxis.top:
            pygame.draw.line(self.screen, GREY, (self.xAxis.left, curY), (self.xAxis.right, curY), 1)

            v = (centerPointX + i) * self.scale
            self.__labelAxis__(v, (self.yAxis.centerx - 4, curY), False)

            i += 1
            curY = curY - offsetY

        return None

    def __labelAxis__(self, value, position, xAxis):
        # Draws a character 'value' at the specified position. Uses 'xAxis' bool parameter
        # to determine the offset of the position
        x,y = position
        
        text = self.font.render(f"{value}", True, BLACK)
        textRect = text.get_rect()
        if xAxis:
            if y < self.yAxis.top:
                y = self.yAxis.top + 2 + textRect.height
            elif (y + textRect.height) > self.yAxis.bottom:
                y = self.yAxis.bottom - 2 - textRect.height
            else:
                y = y + textRect.height
            textRect.center = (x, y)
        else:
            if (x - textRect.width) < self.xAxis.left:
                x = self.xAxis.left + 2 + textRect.width
            elif x > self.xAxis.right:
                x = self.xAxis.right - 2 - textRect.width
            else:
                x = x - textRect.width
            textRect.center = (x, y)

        pygame.draw.rect(self.screen, WHITE, textRect)
        self.screen.blit(text, textRect)
        return None

    def getOffset(self):
        # Returns the offset in the x and y coordinates from the origin. This is used to
        # reset the grid to (0,0)
        dx = self.origin[0] - self.yAxis.centerx
        dy = self.origin[1] - self.xAxis.centery
        return dx,dy

    def updatePosition(self, dx, dy):
        # Scroll the grid based on the user's mouse drag, which is specified by dx, dy
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
