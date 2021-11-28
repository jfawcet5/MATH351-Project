""" This file implements the graphical interface for the polynomial interpolation demo

    Authors: Joshua Fawcett, Hans Prieto

    Sources:
            pygame: https://www.pygame.org/docs/
            roundToNearest function: https://www.kite.com/python/answers/how-to-round-to-the-nearest-multiple-of-5-in-python

    Design influenced by:
        - Desmos: https://www.desmos.com/calculator
        - Geogebra: https://www.geogebra.org/classic?lang=en
"""

import pygame
import sys
import math

from Interpolation import newtonsIP

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

FPS = 45

BLACK = (0,0,0)
WHITE = (255,255,255)
GREY = (170,170,170)
DARKGREY = (120,120,120)
BLUE = (50, 20, 170)
RED = (255, 10, 10)
GREEN = (10, 200, 10)

####################
# Helper Functions #
####################

def inCircle(pointpos, circleRadius, clickpos):
    collideX = abs(clickpos[0] - pointpos[0]) <= circleRadius #x > rect.left and x < rect.right
    collideY = abs(clickpos[1] - pointpos[1]) <= circleRadius #y > rect.top and y < rect.bottom
    return collideX and collideY

def roundToNearest(number, base):
    return base * round(number / base)

def isValidNumber(string):
    # Try-Except used to prevent program from crashing when trying to determine if 'string' contains a valid number
    try:
        if '.' in string: # Number is of the form "x.y" (ex: "3.5")
            temp = string.split(".") # Split string on '.' to obtain a list of the form ['x', 'y']

            if len(temp) != 2: # If we have an invalid floating point number EX: "x.", "x.y.z", etc.
                return False
            
            else: # If we have a valid floating point then check to make sure 'x' and 'y' are valid
                if '-' in temp[1]: # Make sure we dont have number of the form: "x.-y" or "x.y-"
                    return False
                
                for v in temp: # Try converting "x" and "y" to floats. If this fails, an exception is raised
                    float(v)
        else: # If number is not of the form: "x.y", then we can try to directly convert it to a float
            float(string) # If this fails, 'string' is not a valid number

    except Exception: # If an exception is raised, 'string' is not a valid number so we return False
        return False

    return True


################################################################################################
################################################################################################
##                                     Point Class                                            ##
################################################################################################
################################################################################################

class Point:
    def __init__(self, worldCoords, screenCoords, radius=5, color=BLUE):
        self.coordinates = worldCoords
        self.screenPos = screenCoords
        
        self.color = color
        self.radius = radius
        self.selected = False
        self.active = True
        self.str = ''

        self.updateStr()

    def update(self, grid, dx, dy):
        cur_screen_x, cur_screen_y = self.screenPos

        self.screenPos = (cur_screen_x + dx, cur_screen_y + dy)

        wx, wy = grid.convertToWorld(self.screenPos[0], self.screenPos[1])

        self.coordinates = (round(wx, 6), round(wy, 6))
        self.updateStr()
        return None

    def snapToGrid(self, grid):
        wx, wy = grid.snapToGrid(self.coordinates[0], self.coordinates[1])
        self.screenPos = grid.convertToScreen(wx, wy)
        self.coordinates = (wx, wy)
        self.updateStr()

    def updateStr(self):
        string = f"({self.coordinates[0]}, {self.coordinates[1]})"
        self.str = string

    def select(self, selectValue=None):
        if selectValue is not None:
            self.selected = not selectValue
        
        if self.selected:
            self.color = BLUE
            self.selected = False
        else:
            self.color = GREEN
            self.selected = True

    def __repr__(self):
        return f"P{self.coordinates}"


################################################################################################
################################################################################################
##                                     Grid Class                                             ##
################################################################################################
################################################################################################

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

        self.font = pygame.font.SysFont("QuickType 2", 16, bold=True)

        self.__drawGrid__()

    def snapToGrid(self, x, y):
        newx = x
        newy = y
        scale = self.worldScale / 2
        nearestValueX = roundToNearest(x, scale)
        nearestValueY = roundToNearest(y, scale)
        if (abs(x - nearestValueX) / scale) < 0.1:
            newx = nearestValueX
        if (abs(y - nearestValueY) / scale) < 0.1:
            newy = nearestValueY
        return newx,newy

    def convertToWorld(self, x, y):
        # Convert screen space coordinates to world space coordinates
        newX = (((x - self.xOffset) - (self.rect.width // 2)) / self.pixelsPerUnit) * self.worldScale
        newY = -1 * (((y + self.yOffset) - (self.rect.height // 2)) / self.pixelsPerUnit) * self.worldScale
        return (newX, newY)

    def convertToScreen(self, x, y):
        # Convert world space coordinates to screen space coordinates
        newX = (((self.rect.width // 2) + (x * self.pixelsPerUnit / self.worldScale)) + self.xOffset)
        newY = (((self.rect.width // 2) - (y * self.pixelsPerUnit / self.worldScale)) - self.yOffset)
        return newX, newY

    def __drawGrid__(self):
        self.screen.fill(WHITE)

        relativeOffsetX = self.xOffset % self.pixelsPerUnit
        relativeOffsetY = self.yOffset % self.pixelsPerUnit

        centerx = self.rect.centerx + relativeOffsetX
        centery = self.rect.centery - relativeOffsetY

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

            oldx = self.convertToWorld(self.xOffset, 0)[0]

            if zType == 0:
                self.zoomIndex -= 1
            else:
                self.zoomIndex += 1

            factor = self.zoomIndex // 3
            index = self.zoomIndex % 3

            self.worldScale = scales[index]
            if factor != 0:
                self.worldScale = self.worldScale * (10**factor)

            newx = self.convertToWorld(self.xOffset, 0)[0]

            # Ratio should be same for x and y assuming screen size is square
            ratio = oldx / newx
            self.xOffset *= ratio
            self.yOffset *= ratio # This may cause problems if the screen size is not square
        return None

    def updatePosition(self, dx, dy):
        self.xOffset += dx
        self.yOffset -= dy
        return None


################################################################################################
################################################################################################
##                                    Button Class                                            ##
################################################################################################
################################################################################################

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

class zoomInButton(Button):
    def __init__(self, action, screen_size):
        super(zoomInButton, self).__init__(action, (40, 40))

        self.rect = self.screen.get_rect(center=(screen_size[0] - 22, 106))

        pygame.draw.line(self.screen, BLACK, (10, 20), (30, 20), 3)
        pygame.draw.line(self.screen, BLACK, (20, 10), (20, 30), 3)

class zoomOutButton(Button):
    def __init__(self, action, screen_size):
        super(zoomOutButton, self).__init__(action, (40, 40))

        self.rect = self.screen.get_rect(center=(screen_size[0] - 22, 148))
        
        pygame.draw.line(self.screen, BLACK, (10, 20), (30, 20), 3)

class openMenuButton(Button):
    def __init__(self, action, screen_size):
        super(openMenuButton, self).__init__(action, (40, 40))

        self.rect = self.screen.get_rect(center=(22, 22))
        
        pygame.draw.line(self.screen, BLACK, (10, 15), (30, 15), 2)
        pygame.draw.line(self.screen, BLACK, (10, 20), (30, 20), 2)
        pygame.draw.line(self.screen, BLACK, (10, 25), (30, 25), 2)

class openBottomMenuButton(Button):
    def __init__(self, action, screen_size):
        super(openBottomMenuButton, self).__init__(action, (40, 40))

        self.rect = self.screen.get_rect(center=(screen_size[0] - 22, screen_size[1] - 22))

        self.selected = False

        self.__draw__()

    def __draw__(self):
        self.screen.fill(DARKGREY)
        if not self.selected:
            font = pygame.font.SysFont("QuickType 2", 18, bold=True)
            text = font.render("P(X)", True, BLACK)
            textRect = text.get_rect()
            textRect.center = (20, 20)
            self.screen.blit(text, textRect)
        else:
            pygame.draw.line(self.screen, BLACK, (10, 10), (30, 30), 2)
            pygame.draw.line(self.screen, BLACK, (10, 30), (30, 10), 2)

    def onClick(self):
        if self.selected:
            self.selected = False
        else:
            self.selected = True
        self.__draw__()
        self.fn()

class addPointButton(Button):
    def __init__(self, action, screen_size):
        super(addPointButton, self).__init__(action, (40, 40))

        self.rect = self.screen.get_rect(center=(64, 22))

        self.selected = False
        self.__draw__()

    def __draw__(self):
        self.screen.fill(DARKGREY)
        
        font = pygame.font.SysFont("QuickType 2", 14, bold=True)
        text1 = font.render("ADD", True, BLACK)
        text2 = font.render("POINTS", True, BLACK)
        textRect1 = text1.get_rect()
        textRect2 = text2.get_rect()
        textRect1.midtop = (20, 10)
        textRect2.midbottom = (20, 30)

        self.screen.blit(text1, textRect1)
        self.screen.blit(text2, textRect2)

        if self.selected:
            borderRect = pygame.Rect(0, 0, self.rect.width - 1, self.rect.height - 1)
            pygame.draw.rect(self.screen, (255,0,0), borderRect, 2)

    def onClick(self):
        if self.selected:
            self.selected = False
        else:
            self.selected = True
        self.__draw__()
        self.fn()

class deletePointButton(Button):
    def __init__(self, action, screen_size):
        super(deletePointButton, self).__init__(action, (40, 40))

        self.rect = self.screen.get_rect(center=(106, 22))

        self.__draw__()

    def __draw__(self):
        self.screen.fill(DARKGREY)
        #pygame.draw.circle(self.screen, BLUE, (self.rect.width //2, self.rect.height // 2), 7)

        font = pygame.font.SysFont("QuickType 2", 14, bold=True)
        text1 = font.render("DELETE", True, BLACK)
        text2 = font.render("POINT", True, BLACK)
        textRect1 = text1.get_rect()
        textRect2 = text2.get_rect()
        textRect1.midtop = (20, 10)
        textRect2.midbottom = (20, 30)

        self.screen.blit(text1, textRect1)
        self.screen.blit(text2, textRect2)

################################################################################################
################################################################################################
##                                     Menu Class                                             ##
################################################################################################
################################################################################################

class SideMenu:
    def __init__(self, screen_size):
        self.screen = pygame.Surface((screen_size[0] // 4, screen_size[1]))

        self.rect = self.screen.get_rect(topleft = (0,0))

        self.active = False

        self.pointList = []
        self.pointDisplayRects = []

        self.scrollPosition = 0
        self.scrollRect = pygame.Rect(self.rect.width - 17, 44, 17, 30)

        self.selected = None

        self.cursorPosition = 0
        self.pointText = ''

        self.drawBG()
        return None

    def drawBG(self):
        self.screen.fill(GREY)

        font = pygame.font.SysFont("Arial", 28, bold=True)

        self.__drawPointBGs__()

        headerRect = pygame.Rect(0, 0, self.rect.width, 43)
        pygame.draw.rect(self.screen, GREY, headerRect)
        pygame.draw.line(self.screen, BLACK, (0, 43), (self.rect.right,43), 1)

        text = font.render("POINTS", True, BLACK)
        textRect = text.get_rect(center=(headerRect.centerx + 18, headerRect.centery))
        self.screen.blit(text, textRect)

        tempRect = pygame.Rect(2, 2, 40, 40)
        pygame.draw.rect(self.screen, DARKGREY, tempRect)
        pygame.draw.rect(self.screen, BLACK, tempRect, 1)
        pygame.draw.line(self.screen, BLACK, (9, 9), (33,33), 3)
        pygame.draw.line(self.screen, BLACK, (9, 33), (33,9), 3)

        pygame.draw.rect(self.screen, DARKGREY, self.scrollRect)

    def clickOnPointDisplay(self, position):
        for rect,point in self.pointDisplayRects:
            if rect.collidepoint(position[0], position[1]):
                self.selected = (rect, point)
                self.cursorPosition = 0
                return point
        self.selected = None
        return None

    def moveCursor(self, direction):
        if self.selected is not None:
            if direction == 1: # Move cursor to right
                self.cursorPosition = (self.cursorPosition - 1) % len(self.pointText)
            else:
                self.cursorPosition = (self.cursorPosition + 1) % len(self.pointText)
        return None

    def insertChar(self, char):
        if self.selected is not None:
            index = (-1 * self.cursorPosition) - 1
            if index == -1: # User is trying to insert at an invalid index
                return None
            t = self.pointText
            if char == "": # User is deleting a character (replacing current char with "")
                t = t[:index] + t[index+1:]
                charToDelete = self.pointText[index]
                if charToDelete == '(' or charToDelete == ')' or charToDelete == ',':
                    return None
                
            else: # User is inserting a character
                t = t[:index+1] + char + t[index+1:]
            x = t.replace("(", "").replace(")", "").replace(" ", "")
            x = x.split(",")

            point = self.selected[1] # Store current selected point in 'point'
            point.str = t # Update the point's display string
            
            if isValidNumber(x[0]) and isValidNumber(x[1]): # If the current point has valid coordinates
                point.active = True # Set the point to be active
                point.coordinates = (float(x[0]), float(x[1])) # Update the point's coordinates
                
            else: # Else: the point does not have valid coordinates
                point.active = False # Set the point to be inactive
            return point

    def scroll(self, dy): # Semi-Functional - Needs fixing
        newPos = self.scrollRect.top + dy
        newPos = max(newPos, 44)
        newPos = min(newPos, self.rect.bottom - self.scrollRect.height)
        self.scrollRect.top = newPos
        self.drawBG()

    def __drawPointBGs__(self):
        font = pygame.font.SysFont("Courier New", 12, bold=True)
        self.pointDisplayRects = []

        top = self.scrollRect.top - 44
        
        pointBGRect = pygame.Rect(0, 44 - top, self.rect.width - 20, 40)
        for point in self.pointList:
            x,y = point.coordinates
            pygame.draw.rect(self.screen, WHITE, pointBGRect)

            temp = pointBGRect.copy()
            self.pointDisplayRects.append((temp, point))

            #displayString = f"{round(x,6), round(y,6)}"
            displayString = point.str
            
            text = font.render(displayString, True, BLACK)
            textRect = text.get_rect(center=(pointBGRect.centerx, pointBGRect.centery))

            if point.selected:
                pygame.draw.rect(self.screen, GREEN, pointBGRect, 2)

                # Hardcoded character width = 7
                cursorXPos = textRect.right - (self.cursorPosition * 7)

                pygame.draw.line(self.screen, BLACK, (cursorXPos, textRect.top - 1), (cursorXPos, textRect.bottom - 1), 1)

                self.pointText = displayString


            self.screen.blit(text, textRect)
            pointBGRect.centery += 42

    def updatePoints(self, pointsList=[]):
        self.pointList = pointsList
        self.drawBG()

class BottomMenu:
    def __init__(self, screen_size):
        self.screen = pygame.Surface((screen_size[0], screen_size[1] // 8))

        self.rect = self.screen.get_rect(bottomleft = (0,screen_size[0]))

        self.active = False

        self.displayText = "P(X) = 0"

        self.drawBG()
        return None

    def drawBG(self):
        self.screen.fill((120, 120, 255))
        fillRect = pygame.Rect(4, 8, self.rect.width - 8, self.rect.height - 16)
        pygame.draw.rect(self.screen, WHITE, fillRect)

        font = pygame.font.SysFont("Courier New", 30, bold=True)
        text = font.render(self.displayText, True, BLACK)
        textRect = text.get_rect()
        textRect.center = (self.rect.centerx, self.rect.height // 2)
        self.screen.blit(text, textRect)
        return None
        


################################################################################################
################################################################################################
##                                     Graph Class                                            ##
################################################################################################
################################################################################################


# Graph class extends the grid class in order to provide the graph interface,
# including the grid lines, labeled axes, buttons, and points
class Graph(Grid):
    def __init__(self, screen_size):
        # Call parent __init__()
        super(Graph, self).__init__(screen_size)

        self.points = []

        self.buttons = []

        self.buttons.append(resetButton(self.reset, screen_size))
        self.buttons.append(clearButton(self.clearAllPoints, screen_size))
        self.buttons.append(zoomInButton(self.zoomIn, screen_size))
        self.buttons.append(zoomOutButton(self.zoomOut, screen_size))
        self.buttons.append(openBottomMenuButton(self.toggleBottomMenu, screen_size))
        self.buttons.append(deletePointButton(self.deleteSelectedPoint, screen_size))
        self.buttons.append(openMenuButton(self.toggleMenu, screen_size))
        self.buttons.append(addPointButton(lambda : (), screen_size))

        self.menu = SideMenu(screen_size)
        self.bottomMenu = BottomMenu(screen_size)

        self.currentClickedPoint = None
        self.selectedPoint = None
        self.mouseMoveSinceClickDown = (0,0)

        self.objectClickedOn = 0
        return None

    ####################################
    #  Methods for rendering the graph #
    ####################################

    def displayToScreen(self, screen):
        ''' Copy the graph's local screen onto the main pygame display 'screen'
            in order to display the graph to the window
        '''
        self.__drawGrid__()
        self.plot()
        screen.blit(self.screen, self.rect)

        for point in self.points:
            if point.active:
                x,y = point.screenPos
                pygame.draw.circle(screen, point.color, (int(x+1), int(y)), 5, 0)

        for button in self.buttons:
            if type(button) == deletePointButton and self.selectedPoint is None:
                continue
            screen.blit(button.screen, button.rect)

        if self.menu.active:
            self.menu.updatePoints(self.points)
            screen.blit(self.menu.screen, self.menu.rect)

        if self.bottomMenu.active:
            screen.blit(self.bottomMenu.screen, self.bottomMenu.rect)
        return None

    # Important: This method draws the interpolating polynomial
    def plot(self):
        ''' This function draws the interpolating polynomial to the screen. It does so by plotting
            a point for every pixel in the screen using the calculated interpolating polynomial and
            then draws a tiny line between each of these points
        '''
        if len(self.points) > 1:
            # 'data' is a list of the form: [(x1, f(x1)), (x1, f(x1)), ...], where each tuple (xi, f(xi))
            # represents a coordinate in screen space to be drawn to the screen
            data = []

            xs = []
            ys = []

            for point in self.points:
                if point.active:
                    x,y = point.coordinates

                    xs.append(x)
                    ys.append(y)

            # sx1, sx2 define the range of points to be plotted. sx1 is the x coordinate of the leftmost pixel
            # in screen space, and x2 is the x coordinate of the rightmost pixel in screen space
            sx1, sx2 = self.rect.left, self.rect.right

            # sx stands for 'screen x', which is the x coordinate in screen space to be plotted
            for sx in range(sx1, sx2): # iterate from sx1 to sx2
                wx = self.convertToWorld(sx, 0)[0] # convert current screen coordinate 'sx' to a world space coordinate 'wx'

                # This following line evaluates the interpolating polynomial at 'wx'
                wy = newtonsIP(xs, ys, wx)
                # store (screen space x, screen space f(x)) in a tuple called 'c'
                c = (sx, self.convertToScreen(0, wy)[1])
                # append the coordinate 'c' to the list of coordinates 'data'
                data.append(c)

            # Draw a line between each of the plotted points
            pygame.draw.lines(self.screen, RED, False, data, 2)
        return None

    ##################################
    #         Button Methods:        #
    #    These methods define the    #
    # behaviors of different buttons #
    ##################################

    def reset(self):
        ''' Resets the position and scale of the graph back to the default.
            It does this by reversing the current zoom, and setting the offset
            to 0
        '''
        if self.zoomct < 2:
            zoomType = 0
        else:
            zoomType = 1
        for i in range(abs(self.zoomct - 2)):
            self.zoom(zoomType)
        
        self.dragScreen(-self.xOffset, self.yOffset)
        return None

    def clearAllPoints(self):
        ''' Deletes all of the user-created points from the graph
        '''
        self.points = []
        self.selectedPoint = None
        return None

    def zoomIn(self):
        ''' self.zoomIn() implements the functionality of the 'zoom in' button at the
            top right of the graph. It uses the self.zoom() function to avoid redundancy of code
        '''
        for i in range(4):
            self.zoom(0)

    def zoomOut(self):
        ''' self.zoomOut() implements the functionality of the 'zoom out' button at the
            top right of the graph. It uses the self.zoom() function to avoid redundancy of code
        '''
        for i in range(4):
            self.zoom(1)

    def deleteSelectedPoint(self):
        if self.selectedPoint is not None:
            self.points.remove(self.selectedPoint)
            self.selectedPoint = None
        return None

    def toggleMenu(self):
        self.menu.active = not self.menu.active
        if self.menu.active:
            addPointButton= self.buttons[-1]
            deletePointButton = self.buttons[-3]
            addPointButton.rect.left += self.menu.rect.width - 42
            deletePointButton.rect.left += self.menu.rect.width - 42
        else:
            addPointButton= self.buttons[-1]
            deletePointButton = self.buttons[-3]
            addPointButton.rect.left -= self.menu.rect.width - 42
            deletePointButton.rect.left -= self.menu.rect.width - 42
        return None

    def toggleBottomMenu(self):
        self.bottomMenu.active = not self.bottomMenu.active

        toggleMenuButton = self.buttons[-4]
        if self.bottomMenu.active:
            toggleMenuButton.rect.centery -= self.bottomMenu.rect.height
        else:
            toggleMenuButton.rect.centery += self.bottomMenu.rect.height
            pass
        return None

    ################################
    #  Methods for updating points #
    ################################

    def movePoint(self, pointToMove, changeInPosition):
        dx,dy = changeInPosition

        pointToMove.update(self, dx,dy)
        return None

    def selectPoint(self, point):
        point.select()
        if point.selected == True:
            self.selectedPoint = point
        else:
            if self.selectedPoint is not None:
                self.selectedPoint = None
        return None

    def deselectPoints(self):
        '''
        '''
        for point in self.points:
            point.select(False)
        self.selectedPoint = None

    def addPoint(self, x=math.inf, y=math.inf):
        # 
        addPointButton = self.buttons[-1]
        if not addPointButton.selected:
            return None
        
        if len(self.points) < 30:
            if x != math.inf and y != math.inf:
                sx, sy = x,y
                wx, wy = self.convertToWorld(sx, sy)
            else:
                sx, sy = (self.rect.width // 2, self.rect.height // 2)
                wx, wy = self.convertToWorld(sx, sy)

            p = Point((wx, wy), (sx, sy))
            p.snapToGrid(self)

            self.points.append(p)
        return None
    ##################################
    #        Input Methods:          #
    # These methods update the graph #
    #     based on user input        #
    ##################################

    def dragScreen(self, dx, dy):
        self.updatePosition(dx, dy)
        self.plot()

        for point in self.points:
            point.update(self, dx, dy)

        x, y = self.mouseMoveSinceClickDown
        self.mouseMoveSinceClickDown = (x + abs(dx), y+abs(dy))
        return None

    def zoom(self, zoomType):
        ''' self.zoom implements a single zoom in/out, based on the grid.__zoom__() implementation.
            This function is called from 3 different sources: the self.zoomIn() function, self.zoomOut()
            function, and it is called for every movement of the user's mouse scroll wheel
        '''
        self.__zoom__(zoomType)
        for point in self.points:
            px, py = point.coordinates
            point.screenPos = self.convertToScreen(px, py)
        self.plot()
        return None


################################################################################################
################################################################################################
##                                Input Manager Class                                         ##
################################################################################################
################################################################################################
    

class InputManager:
    def __init__(self, screen_size):
        self.graph = Graph(screen_size)

        self.mouseIsDown = False
        self.objectClickedOn = None
        self.mouseDeltaXY = [0,0] # change in mouse position since click down

    def getClickedObject(self, clickPosition):
        ''' This method determines what part of the graphical interface the user clicked on.

            The click hierarchy is determined here to prevent multiple objects from being interacted
            with at the same time. (ex: If a point is behind the side menu, clicking on the side menu should
            prevent the point from being clicked on, dragged, etc.)
            
            Click hierarchy (order in which objects are checked):
                1. button
                2. side menu
                3. bottom menu
                4. point
        '''
        x,y = clickPosition
        buttons = self.graph.buttons
        points = self.graph.points

        sidemenu = self.graph.menu
        bottomMenu = self.graph.bottomMenu

        # Check if clicked on a button
        for button in buttons:
            if button.rect.collidepoint(x, y):
                return button

        # Check if clicked on the side menu
        if sidemenu.active:
            if sidemenu.rect.collidepoint(x, y):
                return sidemenu

        # Check bottom menu
        if bottomMenu.active:
            if bottomMenu.rect.collidepoint(x, y):
                return bottomMenu

        # Check if clicked on a point
        for point in points:
            if point.active:
                if inCircle(point.screenPos, point.radius, clickPosition):
                    return point

        return None

    def onClick(self, clickType, clickPosition):
        """ This method determines what happens when the left mouse button is either pressed down or
            released
        """
        if clickType == 0: # left click down
            clickedObject = self.getClickedObject(clickPosition)

            self.objectClickedOn = clickedObject
            self.mouseIsDown = True
            self.mouseDeltaXY = [0,0]

        else: # Left click up

            # dx,dy = number of pixels the mouse moved in the x,y coordinates since mouse click down
            dx,dy = self.mouseDeltaXY

            if dx < 4 and dy < 4: # If mouse moved within this small margin, then the user clicked on something
                
                if self.objectClickedOn is None: # User did not click on any particular object
                    # Note: the graph will check to make sure the 'add point' button is selected
                    # before adding points. 
                    self.graph.addPoint(clickPosition[0], clickPosition[1])

                elif isinstance(self.objectClickedOn, Button): # User clicked on a button
                    self.objectClickedOn.onClick()

                elif isinstance(self.objectClickedOn, Point): # User clicked on a point
                    self.graph.selectPoint(self.objectClickedOn)

                elif isinstance(self.objectClickedOn, SideMenu): # User clicked on the side menu
                    if self.objectClickedOn.active:
                        selectedPoint = self.objectClickedOn.clickOnPointDisplay(clickPosition)
                        if selectedPoint is not None:
                            isActive = selectedPoint.selected
                            self.graph.deselectPoints()
                            selectedPoint.selected = isActive
                            self.graph.selectPoint(selectedPoint)

            else: # The user was dragging an object (a point, the graph, etc.)
                if isinstance(self.objectClickedOn, Point):
                    self.objectClickedOn.snapToGrid(self.graph)  

            self.objectClickedOn = None
            self.mouseIsDown = False
        return None

    def onMouseScroll(self, scrollType, mousePosition):
        ''' This method determines what happens when the mouse scroll wheel is moved
        '''
        clickedObject = self.getClickedObject(mousePosition)

        if clickedObject is None or isinstance(clickedObject, Point):
            self.graph.zoom(scrollType)

        elif isinstance(clickedObject, SideMenu):
            if scrollType == 0:
                dy = -10
            else:
                dy = 10
            self.graph.menu.scroll(dy)
        return None

    def pressKey(self, ev):
        ''' This method determines what happens when specific keyboard keys are pressed

            It takes a pygame KEYDOWN event as an argument, reads the key associated with
            the event, and takes the appropriate action based on the key
        '''
        key = ev.key
        if key == K_RIGHT:
            if self.graph.menu.active:
                self.graph.menu.moveCursor(1)

        if key == K_LEFT:
            if self.graph.menu.active:
                self.graph.menu.moveCursor(0)

        if ev.unicode.isdigit() or ev.unicode == "." or ev.unicode == "-" or key == K_BACKSPACE:
            if self.graph.menu.active:
                if key == K_BACKSPACE: # User is deleting a character
                    updatedPoint = self.graph.menu.insertChar("")
                    
                else: # User is inserting a character
                    updatedPoint = self.graph.menu.insertChar(ev.unicode)
                    
                if updatedPoint is None: # User has not selected a point to modify
                    return None

                else:
                    # update the point's screen position based on new world coordinates set by user. If this doesn't happen
                    # the menu will display the correct coordinates for the point, but it will be drawn at the wrong screen position
                    updatedPoint.screenPos = self.graph.convertToScreen(updatedPoint.coordinates[0], updatedPoint.coordinates[1])

    def update(self, changeInMousePosition):
        ''' This method updates the graphical interface based on the movement of the mouse. For example, if the user is attempting
            to drag a point (by clicking and holding on a point and moving the mouse), then the graphical interface should reflect
            these inputs by updating the point's position based on the user's mouse movement
        '''
        dx,dy = changeInMousePosition # Unpack 'changeInMousePosition' tuple

        # Update the self.mouseDeltaXY variable for the self.onClick() method
        self.mouseDeltaXY = [self.mouseDeltaXY[0] + abs(dx), self.mouseDeltaXY[1] + abs(dy)]

        if self.mouseIsDown: # If the user is holding the mouse down
            if self.objectClickedOn is None: # If the user is dragging the graph
                self.graph.dragScreen(dx,dy)
                
            elif isinstance(self.objectClickedOn, Point): # If the user is dragging a point
                self.graph.movePoint(self.objectClickedOn, changeInMousePosition)
                
            elif isinstance(self.objectClickedOn, SideMenu): # If the user is dragging the side menu scroll bar
                self.graph.menu.scroll(dy)
        return None

#####################
# Testing Functions #
#####################

def testProgram(screen, clock):
    tempRect = screen.get_rect() # Get main screen rect object
    screen_size = (tempRect.width, tempRect.height) # Retrieve initial screen size

    inputManager = InputManager(screen_size) # Create Graph

    mouseDown = False # Used to track mouse clicks
    
    while True:
        screen.fill(WHITE) # Fill screen with white every frame

        inputManager.graph.displayToScreen(screen)

        dx,dy = pygame.mouse.get_rel() # Get updated (x,y) mouse position for current frame
        
        for ev in pygame.event.get(): # Event handling
            if ev.type == KEYDOWN: # If user pressed a key
                if (ev.key == K_ESCAPE): # If pressed key was 'escape'
                    pygame.quit()
                    sys.exit()
                else:
                    inputManager.pressKey(ev)
            if (ev.type == MOUSEBUTTONDOWN): # If the user clicked on the screen
                x,y = pygame.mouse.get_pos()
                if (ev.button == 1): # Left click
                    inputManager.onClick(0, (x,y))
                    mouseDown = True
                elif (ev.button == 4): # Scroll wheel
                    # Zoom in
                    inputManager.onMouseScroll(0, (x,y))
                    pass
                elif (ev.button == 5): # Scroll wheel
                    # Zoom out
                    inputManager.onMouseScroll(1, (x,y))
                    pass

            if (ev.type == MOUSEBUTTONUP):
                if ev.button == 1:
                    mouseDown = False
                    clickedPointObject = None
                    x,y = pygame.mouse.get_pos()
                    inputManager.onClick(1, (x,y))

            if ev.type == QUIT:
                pygame.quit()
                sys.exit()

        inputManager.update((dx,dy))
        
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

    testProgram(screen, clock)
    
    return None

if __name__ == "__main__":
    main()

