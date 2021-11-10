""" Testing functionality for Polynomial Interpolation graphical demo

    Sources:
            sorted() function: https://docs.python.org/3/howto/sorting.html
            pygame: https://www.pygame.org/docs/
"""

import pygame
import sys
import math

from pygame.locals import (
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
    MOUSEMOTION,
    K_p,
    K_m,
    K_r,
    K_x,
    K_z,
    K_t,
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
DARKGREY = (120,120,120)
BLUE = (50, 20, 170)
RED = (255, 10, 10)

DEBUG = False


####################
# Helper Functions #
####################


def sortList(listToSort):
    # Sorts a list of tuples
    return sorted(listToSort)


def inCircle(pointpos, circleRadius, clickpos):
    #x,y = pos
    #print(f"px: {pointpos[0]}, cx: {clickpos[0]}")
    collideX = abs(clickpos[0] - pointpos[0]) <= circleRadius #x > rect.left and x < rect.right
    collideY = abs(clickpos[1] - pointpos[1]) <= circleRadius #y > rect.top and y < rect.bottom
    return collideX and collideY


#####################
#    Point Class    #
#####################
class Point:
    def __init__(self, worldCoords, screenCoords, radius=5, color=BLUE):
        self.coordinates = worldCoords
        self.screenPos = screenCoords
        
        self.color = color
        self.radius = radius

    def update(self, grid, dx, dy):
        cur_screen_x, cur_screen_y = self.screenPos

        self.screenPos = (cur_screen_x + dx, cur_screen_y + dy)

        wx, wy = grid.convertToWorld(self.screenPos[0], self.screenPos[1])
        self.coordinates = (round(wx, 6), round(wy, 6))
        return None

    def __repr__(self):
        return f"P{self.coordinates}"


#####################
#     Grid Class    #
#####################

# Grid class defines functionality for drawing and updating the grid lines for the graph
# This includes drawing, labeling, and updating the coordinate axes. This class serves as a
# base class for the graph class
class Grid:
    def __init__(self, size):
        x,y = size[0], size[1]
        self.screen = pygame.Surface(size)
        self.rect = self.screen.get_rect()

        self.xOffset = 0
        self.yOffset = 0

        self.worldScale = 1
        self.zoomIndex = 0
        self.zoomct = 2
        self.pixelsPerUnit = 60

        self.zoomFactor = 1
        
        self.font = pygame.font.SysFont("QuickType 2", 16, bold=True)

        self.__drawGrid__()

    def convertToWorld(self, x, y):
        # Convert screen space coordinates to world space coordinates
        newX = (((x - self.xOffset) - (self.rect.width // 2)) / self.pixelsPerUnit) * self.worldScale
        newY = -1 * (((y + self.yOffset) - (self.rect.height // 2)) / self.pixelsPerUnit) * self.worldScale
        return (newX, newY)

    def convertToScreen(self, x, y):
        # Convert world space coordinates to screen space coordinates
        newX = ((self.rect.width // 2) + (x * self.pixelsPerUnit)) + self.xOffset
        newY = ((self.rect.width // 2) - (y * self.pixelsPerUnit)) - self.yOffset
        return newX, newY

    def __drawGrid__(self):
        self.screen.fill(WHITE)

        relativeOffsetX = self.xOffset % self.pixelsPerUnit
        relativeOffsetY = self.yOffset % self.pixelsPerUnit

        centerx = self.rect.centerx + relativeOffsetX
        centery = self.rect.centery - relativeOffsetY

        screenCoord = self.rect.centerx
        val = self.convertToWorld(screenCoord,0)[0]

        scaledOffX = self.xOffset // self.pixelsPerUnit
        scaledOffY = self.yOffset // self.pixelsPerUnit
        
        cvalueX = 0 - scaledOffX # world space coordinate value at center of screen
        cvalueY = 0 - scaledOffY # world space coordinate value at center of screen
        
        pygame.draw.line(self.screen, GREY, (centerx, self.rect.top), (centerx, self.rect.bottom), 1)
        pygame.draw.line(self.screen, GREY, (self.rect.left, centery), (self.rect.right, centery), 1)

        self.__labelAxis__(round(cvalueX * self.worldScale, 6), (centerx, self.rect.centery - self.yOffset), True)
        self.__labelAxis__(round(cvalueY * self.worldScale, 6), (self.rect.centerx + self.xOffset, centery), False)

        numLines = int((self.rect.width // self.pixelsPerUnit) + 2)

        for i in range(numLines):
            x0 = centerx + ((i+1)*self.pixelsPerUnit)
            x1 = centerx - ((i+1)*self.pixelsPerUnit)
            y0 = centery + ((i+1)*self.pixelsPerUnit)
            y1 = centery - ((i+1)*self.pixelsPerUnit)

            pygame.draw.line(self.screen, GREY, (x0, self.rect.top), (x0, self.rect.bottom), 1)
            pygame.draw.line(self.screen, GREY, (x1, self.rect.top), (x1, self.rect.bottom), 1)
            pygame.draw.line(self.screen, GREY, (self.rect.left, y0), (self.rect.right, y0), 1)
            pygame.draw.line(self.screen, GREY, (self.rect.left, y1), (self.rect.right, y1), 1)

            v1x = round((cvalueX + i + 1)* self.worldScale, 6)
            v2x = round((cvalueX - i - 1)* self.worldScale, 6)
            v1y = round((cvalueY - i - 1)* self.worldScale, 6)
            v2y = round((cvalueY + i + 1)* self.worldScale, 6)

            self.__labelAxis__(v1x, (x0, self.rect.centery - self.yOffset), True)
            self.__labelAxis__(v2x, (x1, self.rect.centery - self.yOffset), True)
            self.__labelAxis__(v1y, (self.rect.centerx + self.xOffset, y0), False)
            self.__labelAxis__(v2y, (self.rect.centerx + self.xOffset, y1), False)

        return None

    def __labelAxis__(self, value, position, xAxis):
        x, y = position
        
        text = self.font.render(f"{value}", True, BLACK)
        textRect = text.get_rect()

        if xAxis:
            if y < self.rect.top:
                y = self.rect.top + 2 + textRect.height
            elif y > self.rect.bottom - textRect.height:
                y = self.rect.bottom - 2 - textRect.height
            else:
                y += textRect.height
            textRect.center = (x, y)
        else:
            if x < self.rect.left:
                x = self.rect.left + 2 + textRect.width
            elif x > self.rect.right:
                x = self.rect.right - 2 - textRect.width
            else:
                x -= textRect.width
            textRect.center = (x, y)

        textRect.height += 2
        textRect.width += 2

        pygame.draw.rect(self.screen, WHITE, textRect)
        self.screen.blit(text, textRect)
        return None

    def __zoom__(self, zType):
        scales = [1, 2, 5]

        if zType == 0:
            self.zoomct += 1
        else:
            self.zoomct -= 1

        zoomFactor = ((self.zoomct * 5) % 50)

        oldppu = self.pixelsPerUnit

        self.pixelsPerUnit = 50 + zoomFactor

        self.zoomFactor = (self.pixelsPerUnit / oldppu)

        self.xOffset = self.xOffset * self.zoomFactor
        self.yOffset = self.yOffset * self.zoomFactor

        diff = abs(self.pixelsPerUnit - oldppu)

        if (diff > 5):

            if zType == 0:
                self.zoomIndex -= 1
            else:
                self.zoomIndex += 1

            factor = self.zoomIndex // 3
            index = self.zoomIndex % 3

            self.worldScale = scales[index]
            if factor != 0:
                self.worldScale = self.worldScale * (10**factor)
        
        self.__drawGrid__()
        return None

    def updatePosition(self, dx, dy):
        self.xOffset += dx
        self.yOffset -= dy

        self.__drawGrid__()
        return None

#####################
#   Button Class    #
#####################

class Button:
    def __init__(self, action, buttonSize):
        self.screen = pygame.Surface(buttonSize)
        self.screen.fill(DARKGREY)
        self.fn = action

    def onClick(self):
        self.fn()

class resetButton(Button):
    def __init__(self, action, screen_size):
        super(resetButton, self).__init__(action, (40, 40))

        self.rect = self.screen.get_rect(center=(screen_size[0] - 22, 22))

        font = pygame.font.SysFont("QuickType 2", 14, bold=True)
        text1 = font.render("RESET", True, BLACK)
        text2 = font.render("ZOOM", True, BLACK)
        textRect1 = text1.get_rect()
        textRect2 = text2.get_rect()
        textRect1.midtop = (20, 10)
        textRect2.midbottom = (20, 30)

        self.screen.blit(text1, textRect1)
        self.screen.blit(text2, textRect2)
        
    def __repr__(self):
        return "Reset"

class clearButton(Button):
    def __init__(self, action, screen_size):
        super(clearButton, self).__init__(action, (40, 40))

        self.rect = self.screen.get_rect(center=(screen_size[0] - 22, 64))

        font = pygame.font.SysFont("QuickType 2", 14, bold=True)
        text1 = font.render("CLEAR", True, BLACK)
        text2 = font.render("POINTS", True, BLACK)
        textRect1 = text1.get_rect()
        textRect2 = text2.get_rect()
        textRect1.midtop = (20, 10)
        textRect2.midbottom = (20, 30)

        self.screen.blit(text1, textRect1)
        self.screen.blit(text2, textRect2)

        self.currentClickedPoint = None
        
    def __repr__(self):
        return "Clear"

class zoomInButton(Button):
    def __init__(self, action, screen_size):
        super(zoomInButton, self).__init__(action, (40, 40))

        self.rect = self.screen.get_rect(center=(screen_size[0] - 22, 106))

        pygame.draw.line(self.screen, BLACK, (10, 20), (30, 20), 3)
        pygame.draw.line(self.screen, BLACK, (20, 10), (20, 30), 3)

    def __repr__(self):
        return "Zoom In"

class zoomOutButton(Button):
    def __init__(self, action, screen_size):
        super(zoomOutButton, self).__init__(action, (40, 40))

        self.rect = self.screen.get_rect(center=(screen_size[0] - 22, 148))
        
        pygame.draw.line(self.screen, BLACK, (10, 20), (30, 20), 3)

    def __repr__(self):
        return "Zoom Out"

#####################
#    Graph Class    #
#####################

# Graph class extends the grid class in order to provide the graph interface,
# including the grid lines, labeled axes, buttons, and points
class Graph(Grid):
    def __init__(self, screen_size):

        super(Graph, self).__init__(screen_size)

        self.points = []

        self.buttons = []

        self.buttons.append(resetButton(self.reset, screen_size))
        self.buttons.append(clearButton(self.clear, screen_size))
        self.buttons.append(zoomInButton(self.zoomIn, screen_size))
        self.buttons.append(zoomOutButton(self.zoomOut, screen_size))

        self.currentClickedPoint = None   
        return None

    def onClick(self, position):
        x, y = position

        for button in self.buttons:
            if button.rect.collidepoint(x, y):
                button.onClick()
                return True

        for point in self.points:
            if inCircle(point.screenPos, point.radius, position):
                self.currentClickedPoint = point
                return False

        self.currentClickedPoint = None
        
        return False

    def addPoint(self):
        # Adds a point at the center of the screen in screen space
        sx, sy = (self.rect.width // 2, self.rect.height // 2)
        wx, wy = self.convertToWorld(sx, sy)
        p = Point((wx, wy), (sx, sy))

        self.points.append(p)
        return None

    def scroll(self, dx, dy):
        self.updatePosition(dx, dy)

        for point in self.points:
            point.update(self, dx, dy)
        return None

    def zoomIn(self):
        for i in range(4):
            self.zoom(0)

    def zoomOut(self):
        for i in range(4):
            self.zoom(1)

    def zoom(self, zoomType):
        self.__zoom__(zoomType)
        for point in self.points:
            px, py = point.coordinates
            point.screenPos = self.convertToScreen(px/self.worldScale, py/self.worldScale)
        return None

    def reset(self):
        if self.zoomct < 2:
            zoomType = 0
        else:
            zoomType = 1
        for i in range(abs(self.zoomct - 2)):
            self.zoom(zoomType)
        
        self.scroll(-self.xOffset, self.yOffset)
        return None

    def dragPoint(self, dx, dy):
        if self.currentClickedPoint is not None:
            self.currentClickedPoint.update(self, dx, dy)
            return True
        return False

    def clear(self):
        # Delete all points
        self.points = []
        return None

    def displayToScreen(self, screen):
        screen.blit(self.screen, self.rect)

        for point in self.points:
            pygame.draw.circle(screen, point.color, point.screenPos, 5, 0)

        for button in self.buttons:
            screen.blit(button.screen, button.rect)
        return None


#####################
# Testing Functions #
#####################

def testGraph(screen, clock):
    tempRect = screen.get_rect() # Get main screen rect object
    screen_size = (tempRect.width, tempRect.height) # Retrieve initial screen size

    graph = Graph(screen_size) # Create Graph

    mouseDown = False # Used to track mouse clicks
    
    while True:
        screen.fill(WHITE) # Fill screen with white every frame

        graph.displayToScreen(screen)

        dx,dy = pygame.mouse.get_rel() # Get updated (x,y) mouse position for current frame
        
        for ev in pygame.event.get(): # Event handling
            if ev.type == KEYDOWN: # If user pressed a key
                if (ev.key == K_RETURN): # If pressed key was 'Return'/'Enter'
                    graph.addPoint()
                if (ev.key == K_ESCAPE): # If pressed key was 'escape'
                    pygame.quit()
                    sys.exit()
            if (ev.type == MOUSEBUTTONDOWN): # If the user clicked on the screen
                if (ev.button == 1): # Left click
                    x,y = pygame.mouse.get_pos()
                    mouseDown = not graph.onClick((x,y))
                elif (ev.button == 4): # Scroll wheel
                    # Zoom in
                    graph.zoom(0)
                elif (ev.button == 5): # Scroll wheel
                    # Zoom out
                    graph.zoom(1)

            if (ev.type == MOUSEBUTTONUP):
                mouseDown = False
                clickedPointObject = None

            if ev.type == QUIT:
                pygame.quit()
                sys.exit()

        if mouseDown: # If the mouse button is currently down
            draggingPoint = graph.dragPoint(dx, dy)
            if not draggingPoint:
                graph.scroll(dx, dy)
        
        pygame.display.update()
        clock.tick(FPS)
    return None

########
# Main #
########

def main():
    pygame.init()

    screen = pygame.display.set_mode((700, 700))
    pygame.display.set_caption('Polynomial Interpolation Demo')
    clock = pygame.time.Clock()

    testGraph(screen, clock)
    
    return None

if __name__ == "__main__":
    main()
