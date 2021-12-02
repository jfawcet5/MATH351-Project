""" This file implements the graphical interface for the polynomial interpolation demo

    Authors: Joshua Fawcett, Hans Prieto

    Sources:
            pygame: https://www.pygame.org/docs/
            roundToNearest function: https://www.kite.com/python/answers/how-to-round-to-the-nearest-multiple-of-5-in-python
            String Formatting: https://www.w3schools.com/python/ref_string_format.asp
            Lerp function from: Game Programming Algorithms and Techniques by Sanjay Madhav

    Design influenced by:
        - Desmos: https://www.desmos.com/calculator
        - Geogebra: https://www.geogebra.org/classic?lang=en
"""

import pygame
import sys
import math

from Interpolation import newtonsIP, evaluatePolynomial

# Import pygame key constants
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

# Defined colors (RGB)
BLACK = (0,0,0)
WHITE = (255,255,255)
GREY = (170,170,170)
DARKGREY = (120,120,120)
BLUE = (50, 20, 170)
RED = (255, 10, 10)
GREEN = (10, 200, 10)

# Maximum number of points the graph can interpolate
MAXPOINTS = 10

####################
# Helper Functions #
####################

def inCircle(pointpos, circleRadius, clickpos):
    ''' Helper function to determine if the mouse clicked on a point. 
    '''
    collideX = abs(clickpos[0] - pointpos[0]) <= circleRadius #x > rect.left and x < rect.right
    collideY = abs(clickpos[1] - pointpos[1]) <= circleRadius #y > rect.top and y < rect.bottom
    return collideX and collideY

def roundToNearest(number, base):
    ''' Helper function to round numbers to an arbitrary base
    '''
    return base * round(number / base)

def lerp(a, b, f):
    ''' Linear interpolation used to calculate a midpoint between two values (a, b)
        Formula: Lerp(a, b, f) = (a-f)a + fb
    '''
    return (1-f)*a + f*b 

def isValidNumber(string):
    ''' Helper function to determine if 'string' contains a valid floating point number or integer
    '''
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

def formatNumberString(string):
    ''' Helper function to format the number in 'string' in order to prevent the graphical display of certain numbers
        from taking up too much space. (rounds numbers with large number of decimal points, converts to scientific notation
        if the number is large, etc.)
    '''

    newStr = string

    roundDecimal = False
    convertToInt = False
    ScientificNotation = False

    index = string.find('.')
    if index != -1:
        numDecimals = len(string[index+1:])
        if numDecimals > 4:
            roundDecimal = True
        elif numDecimals == 1 and string[index+1] == '0':
            convertToInt = True

        magnitude = len(string[:index])
        if magnitude > 4:
            ScientificNotation = True

    else:
        if len(newStr) > 4:
            ScientificNotation = True

    if convertToInt:
        if ScientificNotation:
            newStr = '{:0.2e}'.format(int(float(newStr)))
        else:
            newStr = '{:d}'.format(int(float(newStr)))
    else:
        if ScientificNotation:
            newStr = '{:0.4e}'.format(float(newStr))
        else:
            newStr = '{:0.4f}'.format(float(newStr))

        while newStr[-1] == '0': # Remove unecessary trailing zeros
            newStr = newStr[:-1]

    return newStr

def getPolynomialString(xs, table):
    ''' Helper function that takes a list of x coordinates and a divided difference table and returns
        a string that represents the interpolation polynomial (ex: 'P(x) = 1 + 3(x - 2) + ...')
    '''
    returnString = 'P(x) = '

    n = len(table)

    startingValue = formatNumberString(str(table[0][0]))

    returnString = returnString + startingValue + ' '

    for i in range(1, n):
        add = ''
        coefficient = table[0][i]
        if coefficient < 0:
            s = formatNumberString(str(abs(coefficient)))
            add += f'- {s}'
        else:
            s = formatNumberString(str(coefficient))
            add += f'+ {s}'

        for j in range(i):
            add += '(x '
            xi = xs[j]
            if xi < 0:
                s = formatNumberString(str(abs(xi)))
                add += f'+ {s}'
            else:
                s = formatNumberString(str(xi))
                add += f'- {s}'
            add += ')'
        add += ' ' 
        
        returnString += add 
    return returnString


################################################################################################
################################################################################################
##                                     Point Class                                            ##
################################################################################################
################################################################################################

# The point class is a container to hold a single point in the graphical interface. 
class Point:
    def __init__(self, worldCoords, screenCoords, radius=5, color=BLUE):
        self.coordinates = worldCoords # Coordinates of point in world space (based on the coordinate axes of the grid)
        self.screenPos = screenCoords # Coordinates of point in screen space (location of the point relative to the pygame window)
        
        self.color = color
        self.radius = radius
        self.selected = False
        self.active = True
        self.str = ''

        self.updateStr()

    def update(self, grid, dx, dy):
        ''' Update the point's world coordinates and screen position based on the
            change in (screen space) x and y. 
        '''
        cur_screen_x, cur_screen_y = self.screenPos

        # Update current screen position
        self.screenPos = (cur_screen_x + dx, cur_screen_y + dy)

        # Get new world coordinates based on updated screen position
        wx, wy = grid.convertToWorld(self.screenPos[0], self.screenPos[1])

        self.coordinates = (round(wx, 6), round(wy, 6))

        # The point's string representation of itself
        self.updateStr()
        return None

    def snapToGrid(self, grid):
        ''' Update the point's position based on current grid lines. Uses the graph.snapToGrid()
            function to determine what the new coordinates are
        '''
        wx, wy = grid.snapToGrid(self.coordinates[0], self.coordinates[1])
        self.screenPos = grid.convertToScreen(wx, wy)
        self.coordinates = (wx, wy)
        self.updateStr()

    def updateStr(self):
        string = f"({self.coordinates[0]}, {self.coordinates[1]})"
        self.str = string

    def select(self, selectValue=None):
        ''' Toggles whether the point is selected or not. (if 'selectValue' is specified, then the
            point will be set to selected/deselected based on the specified value). Updates
            the point's color based on selected value
        '''
        if selectValue is not None:
            self.selected = not selectValue
        
        if self.selected:
            self.color = BLUE
            self.selected = False
        else:
            self.color = GREEN
            self.selected = True

    def __repr__(self):
        ''' Used for debugging
        '''
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
        ''' given world coordinates (x,y), this method determines if the coordinates
            are close enough to a grid line to change the coordinates from (x,y)
            to (newx, newy) where (newx, newy) are rounded numbers according to the
            current scale of the graph
        '''
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
        ''' Converts screen space coordinates (x,y) to world space coordinates
        '''
        newX = (((x - self.xOffset) - (self.rect.width // 2)) / self.pixelsPerUnit) * self.worldScale
        newY = -1 * (((y + self.yOffset) - (self.rect.height // 2)) / self.pixelsPerUnit) * self.worldScale
        return (newX, newY)

    def convertToScreen(self, x, y):
        ''' Converts world coordinates (x,y) to screen space coordinates
        '''
        newX = (((self.rect.width // 2) + (x * self.pixelsPerUnit / self.worldScale)) + self.xOffset)
        newY = (((self.rect.width // 2) - (y * self.pixelsPerUnit / self.worldScale)) - self.yOffset)
        return newX, newY

    def __drawGrid__(self):
        ''' Draws coordinate axes and all other grid lines at the correct position on the screen
        '''
        self.screen.fill(WHITE)

        relativeOffsetX = self.xOffset % self.pixelsPerUnit
        relativeOffsetY = self.yOffset % self.pixelsPerUnit

        centerx = self.rect.centerx + relativeOffsetX
        centery = self.rect.centery - relativeOffsetY

        scaledOffX = self.xOffset // self.pixelsPerUnit
        scaledOffY = self.yOffset // self.pixelsPerUnit
        
        cvalueX = 0 - scaledOffX # world space coordinate value at center of screen
        cvalueY = 0 - scaledOffY # world space coordinate value at center of screen

        # Draw the lines in the center of the screen. (These may or may not correspond with x = 0 and y = 0)
        pygame.draw.line(self.screen, GREY, (centerx, self.rect.top), (centerx, self.rect.bottom), 1)
        pygame.draw.line(self.screen, GREY, (self.rect.left, centery), (self.rect.right, centery), 1)

        # Label the horizontal and vertical center lines
        self.__labelAxis__(round(cvalueX * self.worldScale, 6), (centerx, self.rect.centery - self.yOffset), True)
        self.__labelAxis__(round(cvalueY * self.worldScale, 6), (self.rect.centerx + self.xOffset, centery), False)

        # Calculate the number of lines to draw
        numLines = int((self.rect.width // self.pixelsPerUnit) + 2)

        # This loop draws horizontal lines going up from the center, down from the center, and vertical lines going
        # to the right from the center and to the left from the center
        for i in range(numLines):
            x0 = centerx + ((i+1)*self.pixelsPerUnit)
            x1 = centerx - ((i+1)*self.pixelsPerUnit)
            y0 = centery + ((i+1)*self.pixelsPerUnit)
            y1 = centery - ((i+1)*self.pixelsPerUnit)

            # Draw horizontal and vertical lines
            pygame.draw.line(self.screen, GREY, (x0, self.rect.top), (x0, self.rect.bottom), 1)
            pygame.draw.line(self.screen, GREY, (x1, self.rect.top), (x1, self.rect.bottom), 1)
            pygame.draw.line(self.screen, GREY, (self.rect.left, y0), (self.rect.right, y0), 1)
            pygame.draw.line(self.screen, GREY, (self.rect.left, y1), (self.rect.right, y1), 1)

            # Calculate the coordinate located at each of the grid lines
            v1x = round((cvalueX + i + 1)* self.worldScale, 6)
            v2x = round((cvalueX - i - 1)* self.worldScale, 6)
            v1y = round((cvalueY - i - 1)* self.worldScale, 6)
            v2y = round((cvalueY + i + 1)* self.worldScale, 6)

            # Label the newly drawn lines
            self.__labelAxis__(v1x, (x0, self.rect.centery - self.yOffset), True)
            self.__labelAxis__(v2x, (x1, self.rect.centery - self.yOffset), True)
            self.__labelAxis__(v1y, (self.rect.centerx + self.xOffset, y0), False)
            self.__labelAxis__(v2y, (self.rect.centerx + self.xOffset, y1), False)

        return None

    def __labelAxis__(self, value, position, xAxis):
        ''' Helper method: draws axis label at the specified position. Used in order to
            give each grid line a coordinate
        '''
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
        ''' Updates the scale of the graph
        '''
        scales = [1, 2, 5]

        # Update the zoom count based on the type of zoom
        if zType == 0:
            self.zoomct += 1
        else:
            self.zoomct -= 1

        # Use zoom count to find new zoomFactor (zoomFactor is used to update the pixelsPerUnit
        # variable to determine how far apart the grid lines are drawn to create realistic zoom)
        zoomFactor = ((self.zoomct * 5) % 50)

        # Save old pixels per unit
        oldppu = self.pixelsPerUnit

        # Update the pixels per unit
        self.pixelsPerUnit = 50 + zoomFactor

        # Update self.zoomRatio (the ratio of the new pixels per unit to the old pixels
        # per unit. Used in order to update the offset of the grid origin)
        self.zoomRatio = (self.pixelsPerUnit / oldppu)

        # Update the offset of the origin in the x and y coordinates
        self.xOffset = self.xOffset * self.zoomRatio
        self.yOffset = self.yOffset * self.zoomRatio

        diff = abs(self.pixelsPerUnit - oldppu)

        # Since zoomFactor is calculated using modulo (remainder division), occasionally there will be a
        # big change in the pixels per unit. When this happens, the scale of the axis labels will change (for example
        # -2 -1 0 1 2 may change to -4 -2 0 2 4
        if (diff > 5):
            # Save the old x offset (in world coordinates)
            oldx = self.convertToWorld(self.xOffset, 0)[0]

            # Update the index into the 'scales' list based on the type of zoom
            if zType == 0:
                self.zoomIndex -= 1
            else:
                self.zoomIndex += 1

            # Since we use the 'scales' list as a circular buffer containing the base scale for the current
            # zoom index, we need to calculate the order of magnitude of the scale
            factor = self.zoomIndex // 3

            index = self.zoomIndex % 3

            # Update the world scale
            self.worldScale = scales[index]
            if factor != 0:
                # Multiply the world scale by the order of magnitude
                self.worldScale = self.worldScale * (10**factor)

            # Calculate the new x offset in world coordinates
            newx = self.convertToWorld(self.xOffset, 0)[0]

            # Get the ratio of the new x offset to the old x offset. This will be used to update the x and y
            # offsets in screen space. Note: ratio should be same for x and y assuming screen size is square
            # (default is (700,700))
            ratio = oldx / newx
            self.xOffset *= ratio
            self.yOffset *= ratio # This may cause problems if the screen size is not square
        return None

    def updatePosition(self, dx, dy):
        ''' Changes the offset of the graph origin in the x,y coordinates to move the coordinate
            axes
        '''
        self.xOffset += dx
        self.yOffset -= dy
        return None


################################################################################################
################################################################################################
##                                    Button Class                                            ##
################################################################################################
################################################################################################

# The button class is responsible for drawing the buttons on the screen and taking
# The appropriate action when a button is clicked on 
class Button:
    def __init__(self, action, buttonSize):
        self.screen = pygame.Surface(buttonSize)
        self.screen.fill(DARKGREY)
        self.fn = action

    def onClick(self):
        self.fn()

# Reset button: Resets the orientation of the graph to the default values
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

# Clear button: Removes all points from the screen
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

# Zoom in button: Zooms in on the graph
class zoomInButton(Button):
    def __init__(self, action, screen_size):
        super(zoomInButton, self).__init__(action, (40, 40))

        self.rect = self.screen.get_rect(center=(screen_size[0] - 22, 106))

        pygame.draw.line(self.screen, BLACK, (10, 20), (30, 20), 3)
        pygame.draw.line(self.screen, BLACK, (20, 10), (20, 30), 3)

# Zoom out button: Zooms out on the graph
class zoomOutButton(Button):
    def __init__(self, action, screen_size):
        super(zoomOutButton, self).__init__(action, (40, 40))

        self.rect = self.screen.get_rect(center=(screen_size[0] - 22, 148))
        
        pygame.draw.line(self.screen, BLACK, (10, 20), (30, 20), 3)

# Open menu button: Opens the side menu
class openMenuButton(Button):
    def __init__(self, action, screen_size):
        super(openMenuButton, self).__init__(action, (40, 40))

        self.rect = self.screen.get_rect(center=(22, 22))
        
        pygame.draw.line(self.screen, BLACK, (10, 15), (30, 15), 2)
        pygame.draw.line(self.screen, BLACK, (10, 20), (30, 20), 2)
        pygame.draw.line(self.screen, BLACK, (10, 25), (30, 25), 2)

# Open bottom menu buttton: Opens the bottom menu
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

# Add point button: Toggles the graph 'add point mode' where a point will be added to the graph
# at the location of each mouse click
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

# Delete point button: Deletes a currently selected point
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
##                                     Menu Classes                                           ##
################################################################################################
################################################################################################

###############
## Side Menu ##
###############

# Side menu is responsible for displaying the coordinates of all of the points on the graph.
# It allows the user to view what points are on the graph, where the points are, and allows
# them to modify the location of these points
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
        ''' Draws each aspect of the side menu
        '''
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

        #pygame.draw.rect(self.screen, DARKGREY, self.scrollRect)

    def clickOnPointDisplay(self, position):
        ''' This method defines what happens when the user clicks on a point
            display in the side menu:

            When a point display is clicked, it will either be selected,
            or deselected, and enables/disables modification of that point
        '''
        for rect,point in self.pointDisplayRects:
            if rect.collidepoint(position[0], position[1]):
                self.selected = (rect, point)
                self.cursorPosition = 0
                return point
        self.selected = None
        return None

    def moveCursor(self, direction):
        ''' Moves the cursor's position one character to the left/right based
            on user input
        '''
        if self.selected is not None:
            if direction == 1: # Move cursor to right
                self.cursorPosition = (self.cursorPosition - 1) % len(self.pointText)
            else: # Move cursor to the left
                self.cursorPosition = (self.cursorPosition + 1) % len(self.pointText)
        return None

    def insertChar(self, char):
        ''' This method is used to insert and delete characters from a point's coordinate display,
            based on user input.

            If 'char' is an empty string (''), then the user is deleting the character that is located
            directly to the left of the cursor.

            Otherwise, 'char' is a single numeric character ('123...' or '.' or '-') that the user is
            inserting at the position indicated by the cursor
        '''
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

    def scroll(self, dy):
        # This method does nothing. It was originally implemented to allow the user to scroll down through the points in the
        # side menu to be able to see them all. However, since the interpolating polynomial (p(x) = ...) gets very hard to
        # display as the number of points increases, the number of points is limited to 10 and this scroll feature is not needed
        #newPos = self.scrollRect.top + dy
        #newPos = max(newPos, 44)
        #newPos = min(newPos, self.rect.bottom - self.scrollRect.height)
        #self.scrollRect.top = newPos
        #self.drawBG()
        return None

    def __drawPointBGs__(self):
        ''' Draw the white background for each of the point displays as well as the point
            display text (showing each point's coordinates
        '''
        font = pygame.font.SysFont("Courier New", 12, bold=True)
        self.pointDisplayRects = []

        top = self.scrollRect.top - 44
        
        pointBGRect = pygame.Rect(0, 44 - top, self.rect.width - 2, 40)
        for point in self.pointList:
            x,y = point.coordinates
            pygame.draw.rect(self.screen, WHITE, pointBGRect)

            temp = pointBGRect.copy()
            self.pointDisplayRects.append((temp, point))

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


#################
## Bottom Menu ##
#################

# The bottom menu is responsible for graphically displaying the interpolating polynomial function
# to the user
class BottomMenu:
    def __init__(self, screen_size):
        self.screen = pygame.Surface((screen_size[0], screen_size[1] // 8))

        self.rect = self.screen.get_rect(bottomleft = (0,screen_size[0]))

        self.active = False

        self.displayText = "P(X) = 0"
        self.fontSize = 28

        scrollBarPosition = 0
        self.scrollRect = pygame.Rect(0, self.rect.height - 19, 30, 17)

        self.drawBG()
        return None

    def drawBG(self):
        ''' Draw the bottom menu background, scroll bar, and interpolation polynomial display text
        '''
        self.screen.fill((120, 120, 255))
        fillRect = pygame.Rect(4, 8, self.rect.width - 8, self.rect.height - 30)
        pygame.draw.rect(self.screen, WHITE, fillRect)

        font = self.__getFont__()
        text = font.render(self.displayText, True, BLACK)
        textRect = text.get_rect()

        X = self.getTextPosition(font)
        
        textRect.midleft = (X, fillRect.centery)
        self.screen.blit(text, textRect)
        pygame.draw.rect(self.screen, (90, 90, 160), self.scrollRect)
        return None

    def scroll(self, dx):
        ''' Move the scroll bar based on user input. 
        ''' 
        self.scrollRect.left += dx
        self.scrollRect.left = max(0, self.scrollRect.left)
        self.scrollRect.right = min(self.rect.right, self.scrollRect.right)

    def getTextPosition(self, font):
        ''' Gets the new position of the display text based on the position of the scroll bar. This
            method is what makes the interpolation polynomial display move when the user drags the
            scroll bar
        '''
        width, height = font.size(self.displayText)

        movement = lerp(0, 1, self.scrollRect.left / (self.rect.width- 30))

        textRight = 4 + width

        offset = self.rect.right - textRight

        if offset > 0:
            return 4

        position = lerp(0, offset, movement)
        return position + 4

    def __getFont__(self):
        ''' Returns a font with a size in the range [12,28], attempting to size the font
            as big as possible without the text going off the screen
        '''
        font = pygame.font.SysFont("Courier New", self.fontSize, bold=True)

        maxWidth = self.rect.width - 8
        
        width, height = font.size(self.displayText)

        # This while loop scales the font size up to be as big as possible within the screen
        while width < maxWidth:
            if self.fontSize == 28:
                return font
            self.fontSize += 2
            font = pygame.font.SysFont("Courier New", self.fontSize, bold=True)
            width, height = font.size(self.displayText)

        # This while loop scales the font size down to fit inside the screen
        while width > maxWidth:
            if self.fontSize == 12:
                return font
            self.fontSize -= 2
            font = pygame.font.SysFont("Courier New", self.fontSize, bold=True)
            width, height = font.size(self.displayText)
        return font

    def updateDisplay(self, newText):
        ''' Update the bottom menu display. The new interpolating polynomial to display
            will be provided in 'newText'
        '''
        self.displayText = newText
        self.drawBG()
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
        # Call parent class (grid) __init__() to set up the graph display
        super(Graph, self).__init__(screen_size)

        # List of points
        self.points = []

        # List of buttons
        self.buttons = []

        # Populate the list of buttons
        self.buttons.append(resetButton(self.reset, screen_size))
        self.buttons.append(clearButton(self.clearAllPoints, screen_size))
        self.buttons.append(zoomInButton(self.zoomIn, screen_size))
        self.buttons.append(zoomOutButton(self.zoomOut, screen_size))
        self.buttons.append(openBottomMenuButton(self.toggleBottomMenu, screen_size))
        self.buttons.append(deletePointButton(self.deleteSelectedPoint, screen_size))
        self.buttons.append(openMenuButton(self.toggleMenu, screen_size))
        self.buttons.append(addPointButton(lambda : (), screen_size))

        # Create side menu
        self.menu = SideMenu(screen_size)
        # Create bottom menu
        self.bottomMenu = BottomMenu(screen_size)

        # Useful state information
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
            in order to display the graphical interface to the window
        '''
        self.__drawGrid__() # draw the grid lines to the graph's local screen
        self.plot() # Plot the interpolating polynomial to the graph's local screen
        screen.blit(self.screen, self.rect) # copy the graph's local screen to the main pygame display

        # Iterate through the points and draw them to the main pygame display
        for point in self.points:
            if point.active:
                x,y = point.screenPos
                pygame.draw.circle(screen, point.color, (int(x+1), int(y)), 5, 0)

        # Iterate through the buttons and draw them to the main pygame display
        for button in self.buttons:
            if type(button) == deletePointButton and self.selectedPoint is None:
                continue
            screen.blit(button.screen, button.rect)

        # If the side menu is active, draw it to the main pygame display
        if self.menu.active:
            self.menu.updatePoints(self.points)
            screen.blit(self.menu.screen, self.menu.rect)

        # If the bottom menu is active, draw it to the main pygame display
        if self.bottomMenu.active:
            screen.blit(self.bottomMenu.screen, self.bottomMenu.rect)
        return None

    # Important: This method draws the interpolating polynomial
    def plot(self):
        ''' This function draws the interpolating polynomial to the screen. It does so by plotting
            a point for every pixel in the screen using the calculated interpolating polynomial and
            then draws a tiny line between each of these points
        '''
        if len(self.points) >= 1:
            # 'data' is a list of the form: [(x1, f(x1)), (x1, f(x1)), ...], where each tuple (xi, f(xi))
            # represents a coordinate in screen space to be drawn to the screen
            data = []

            # A list of the x coordinates of the points for polynomial interpolation
            xs = []
            # A list of the y coordinates of the points for polynomial interpolation
            ys = []

            for point in self.points:
                if point.active:
                    x,y = point.coordinates

                    if x in xs: # If the x values of the points are not distinct, then we can't calculate the interpolating polynomial
                        self.bottomMenu.updateDisplay('Error: x values must be distinct')
                        return None

                    xs.append(x)
                    ys.append(y)

            # Calculate the divided difference table based on Newton's polynomial interpolation method
            dividedDifferenceTable = newtonsIP(xs, ys)

            # generate the interpolation polynomial display string
            polynomialDisplay = getPolynomialString(xs, dividedDifferenceTable)
            # Update the bottom menu to display the interpolating polynomial
            self.bottomMenu.updateDisplay(polynomialDisplay)
        
            # sx1, sx2 define the range of points to be plotted. sx1 is the x coordinate of the leftmost pixel
            # in screen space, and x2 is the x coordinate of the rightmost pixel in screen space
            sx1, sx2 = self.rect.left, self.rect.right

            # sx stands for 'screen x', which is the x coordinate in screen space to be plotted
            for sx in range(sx1, sx2): # iterate from sx1 to sx2
                wx = self.convertToWorld(sx, 0)[0] # convert current screen coordinate 'sx' to a world space coordinate 'wx'

                # This following line evaluates the interpolating polynomial at world coordinate 'wx'
                wy = evaluatePolynomial(wx, xs, dividedDifferenceTable)
                # store (screen space x, screen space f(x)) in a tuple called 'c'
                c = (sx, self.convertToScreen(0, wy)[1])
                # append the coordinate 'c' to the list of coordinates 'data'
                data.append(c)

            # Draw a line between each of the plotted points
            pygame.draw.lines(self.screen, RED, False, data, 2)

        else: # If there are no points: display this message in the bottom menu
            self.bottomMenu.updateDisplay('Add points to interpolate')

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
        ''' Delete the currently selected point
        '''
        if self.selectedPoint is not None:
            self.points.remove(self.selectedPoint)
            self.selectedPoint = None
        return None

    def toggleMenu(self):
        ''' Open/close the side menu
        '''
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
        ''' Open/close the bottom menu
        '''
        self.bottomMenu.active = not self.bottomMenu.active

        toggleMenuButton = self.buttons[-4]
        if self.bottomMenu.active:
            toggleMenuButton.rect.centery -= self.bottomMenu.rect.height
        else:
            toggleMenuButton.rect.centery += self.bottomMenu.rect.height
        return None

    ################################
    #  Methods for updating points #
    ################################

    def movePoint(self, pointToMove, changeInPosition):
        ''' Update a point's position
        '''
        dx,dy = changeInPosition

        pointToMove.update(self, dx,dy)
        return None

    def selectPoint(self, point):
        ''' Select (or deselect) a single point specified by 'point'
        '''
        point.select()
        if point.selected == True:
            self.selectedPoint = point
        else:
            if self.selectedPoint is not None:
                self.selectedPoint = None
        return None

    def deselectPoints(self):
        ''' Deselect all points
        '''
        for point in self.points:
            point.select(False)
        self.selectedPoint = None

    def addPoint(self, x=math.inf, y=math.inf):
        ''' This method adds a new point to the graph at the specified x and y coordinates
            (in screen space). This method will only add up to 'MAXPOINTS' points

            Returns True if a point was added and False otherwise
        '''
        addPointButton = self.buttons[-1]
        if not addPointButton.selected:
            return False
        
        if len(self.points) < MAXPOINTS:
            if x != math.inf and y != math.inf:
                sx, sy = x,y
                wx, wy = self.convertToWorld(sx, sy)
            else:
                sx, sy = (self.rect.width // 2, self.rect.height // 2)
                wx, wy = self.convertToWorld(sx, sy)

            p = Point((wx, wy), (sx, sy))
            p.snapToGrid(self)

            self.points.append(p)
        return True
    ##################################
    #        Input Methods:          #
    # These methods update the graph #
    #     based on user input        #
    ##################################

    def dragScreen(self, dx, dy):
        ''' This method moves the graph's grid lines based on the user's mouse inputs. In order to make sure
            the graph works correctly, the points must also move with the graph background so that they are
            always located at the correct world coordinates and screen position
        '''
        self.updatePosition(dx, dy)
        self.plot()

        for point in self.points:
            point.update(self, dx, dy)

        return None

    def zoom(self, zoomType):
        ''' self.zoom implements a single zoom in/out, based on the grid.__zoom__() implementation.
            This function is called from 3 different sources: the self.zoomIn() function, self.zoomOut()
            function, and it is called for every movement of the user's mouse scroll wheel

            Both the graph's grid lines and each point's position must be updated based on the new scale
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

# The input manager class reads and handles user input events based on the type of input and the
# graph's internal state (which menus are active, etc.)
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
            prevent the point from being clicked on/dragged, etc.)
            
            Click hierarchy (order in which objects are checked):
                1. button
                2. bottom menu
                3. side menu
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

        # Check if clicked on bottom menu
        if bottomMenu.active:
            if bottomMenu.rect.collidepoint(x, y):
                return bottomMenu

        # Check if clicked on the side menu
        if sidemenu.active:
            if sidemenu.rect.collidepoint(x, y):
                return sidemenu

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
            # Get a reference to the object that was clicked on
            clickedObject = self.getClickedObject(clickPosition)

            self.objectClickedOn = clickedObject # save the clicked object
            self.mouseIsDown = True # self.mouseIsDown is true until the next left click up event
            self.mouseDeltaXY = [0,0] # Reset the relative mouse movement

        else: # Left click up

            # dx,dy = number of pixels the mouse moved in the x,y coordinates since mouse click down
            # Note: self.mouseDeltaXY is updated in self.update()
            dx,dy = self.mouseDeltaXY

            if dx < 4 and dy < 4: # If mouse moved within this small margin, then the user clicked on something
                
                if self.objectClickedOn is None: # User did not click on any particular object
                    # Note: the graph will check to make sure the 'add point' button is selected
                    # before adding points. 
                    if not self.graph.addPoint(clickPosition[0], clickPosition[1]):
                        self.graph.deselectPoints()

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

            else: # The user was dragging an object (a point, the graph, etc.) instead of clicking on an object
                if isinstance(self.objectClickedOn, Point): # If the user was dragging a point
                    # Use snapToGrid() function to move the point onto a grid line if the user placed
                    # the point close enough to the grid line
                    self.objectClickedOn.snapToGrid(self.graph)  

            self.objectClickedOn = None # Reset object clicked on for next click down event
            self.mouseIsDown = False # Left mouse button is no longer being held down
        return None

    def onMouseScroll(self, scrollType, mousePosition):
        ''' This method determines what happens when the mouse scroll wheel is moved
        '''
        clickedObject = self.getClickedObject(mousePosition)

        # If the mouse is hovering over the grid or over a point
        if clickedObject is None or isinstance(clickedObject, Point):
            self.graph.zoom(scrollType) # Zoom in/out

        # If the mouse is hovering over the side menu
        elif isinstance(clickedObject, SideMenu):
            # Scroll up/down 
            if scrollType == 0:
                dy = -10
            else:
                dy = 10
            self.graph.menu.scroll(dy)

        # If the menu is hovering over the bottom menu
        elif isinstance(clickedObject, BottomMenu):
            # Scroll the bottom menu left/right
            if scrollType == 0:
                dx = 10
            else:
                dx = -10
            self.graph.bottomMenu.scroll(dx)
        return None

    def pressKey(self, ev):
        ''' This method determines what happens when specific keyboard keys are pressed

            It takes a pygame KEYDOWN event as an argument, reads the key associated with
            the event, and takes the appropriate action based on the key
        '''
        key = ev.key
        if key == K_RIGHT: # If the user pressed the right arrow key
            if self.graph.menu.active: # If the side menu is active
                self.graph.menu.moveCursor(1) # Move the cursor to the right

        if key == K_LEFT: # If the user pressed the left arrow key
            if self.graph.menu.active: # If the side menu is active
                self.graph.menu.moveCursor(0) # Move the cursor to the left

        # If the user pressed a number key (0,1, 2, ...) or the minus key '-' or backspace
        if ev.unicode.isdigit() or ev.unicode == "." or ev.unicode == "-" or key == K_BACKSPACE:
            if self.graph.menu.active: # If the side menu is active
                if key == K_BACKSPACE: # User is deleting a character
                    updatedPoint = self.graph.menu.insertChar("")
                    
                else: # User is inserting a character
                    updatedPoint = self.graph.menu.insertChar(ev.unicode)

                # 'updatedPoint' holds a point that was modified by the user, or None if a point was not
                # modified (due to no points being selected)
                    
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

            elif isinstance(self.objectClickedOn, BottomMenu): # If the user is dragging the bottom menu scroll bar
                self.graph.bottomMenu.scroll(dx)
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

def runTest():
    pygame.init()

    screen = pygame.display.set_mode((700, 700))
    pygame.display.set_caption('Polynomial Interpolation Demo')
    clock = pygame.time.Clock()

    testProgram(screen, clock)
    
    return None

if __name__ == "__main__":
    runTest()

