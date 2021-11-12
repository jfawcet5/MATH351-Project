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
GREEN = (10, 200, 10)

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
        self.selected = False

    def update(self, grid, dx, dy):
        cur_screen_x, cur_screen_y = self.screenPos

        self.screenPos = (cur_screen_x + dx, cur_screen_y + dy)

        wx, wy = grid.convertToWorld(self.screenPos[0], self.screenPos[1])
        self.coordinates = (round(wx, 6), round(wy, 6))
        return None

    def select(self, setValue=None):
        if setValue is not None:
            self.selected = not setValue
        
        if self.selected:
            self.color = BLUE
            self.selected = False
        else:
            self.color = GREEN
            self.selected = True

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

            ratio = oldx / newx # Ratio should be same for x and y assuming screen size is square
            self.xOffset *= ratio
            self.yOffset *= ratio
        return None

    def updatePosition(self, dx, dy):
        self.xOffset += dx
        self.yOffset -= dy
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

class openMenuButton(Button):
    def __init__(self, action, screen_size):
        super(openMenuButton, self).__init__(action, (40, 40))

        self.rect = self.screen.get_rect(center=(22, 22))
        
        pygame.draw.line(self.screen, BLACK, (10, 15), (30, 15), 2)
        pygame.draw.line(self.screen, BLACK, (10, 20), (30, 20), 2)
        pygame.draw.line(self.screen, BLACK, (10, 25), (30, 25), 2)

    def __repr__(self):
        return "Open Menu"

class addPointButton(Button):
    def __init__(self, action, screen_size):
        super(addPointButton, self).__init__(action, (40, 40))

        self.rect = self.screen.get_rect(center=(64, 22))

        self.selected = False
        self.__draw__()

    def __draw__(self):
        self.screen.fill(DARKGREY)
        #pygame.draw.circle(self.screen, BLUE, (self.rect.width //2, self.rect.height // 2), 7)

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

    def __repr__(self):
        return "Add point"

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

    def __repr__(self):
        return "delete point"

class Menu:
    def __init__(self, screen_size):
        self.screen = pygame.Surface((screen_size[0] // 4, screen_size[1]))

        self.rect = self.screen.get_rect(topleft = (0,0))

        self.pointDisplayRects = []

        self.selected = None

        self.drawBG()
        return None

    def drawBG(self):
        self.screen.fill(DARKGREY)

        tempRect = pygame.Rect(2, 2, 40, 40)
        pygame.draw.rect(self.screen, BLACK, tempRect, 1)
        pygame.draw.line(self.screen, BLACK, (9, 9), (33,33), 3)
        pygame.draw.line(self.screen, BLACK, (9, 33), (33,9), 3)

    def onClick(self, position):
        for rect,point in self.pointDisplayRects:
            if rect.collidepoint(position[0], position[1]):
                self.selected = (rect, point)
                return point
        self.selected = None
        return None

    def drawPoint(self, pointsList=[]):
        self.drawBG()

        self.pointDisplayRects = []

        font = pygame.font.SysFont("QuickType 2", 18, bold=True)
        
        rect = pygame.Rect(2, 44, self.rect.width - 4, 40)
        for point in pointsList:
            x,y = point.coordinates
            pygame.draw.rect(self.screen, WHITE, rect)

            temp = rect.copy()
            self.pointDisplayRects.append((temp, point))

            if point.selected:
                pygame.draw.rect(self.screen, GREEN, rect, 2)
            
            text = font.render(f"{round(x,6), round(y,6)}", True, BLACK)
            textRect = text.get_rect(center=(rect.centerx, rect.centery))
            self.screen.blit(text, textRect)
            rect.centery += 42

#####################
#    Graph Class    #
#####################


# Graph class extends the grid class in order to provide the graph interface,
# including the grid lines, labeled axes, buttons, and points
class Graph(Grid):
    def __init__(self, screen_size):
        # Call parent __init__()
        super(Graph, self).__init__(screen_size)

        self.points = []

        self.buttons = []

        self.buttons.append(resetButton(self.reset, screen_size))
        self.buttons.append(clearButton(self.clear, screen_size))
        self.buttons.append(zoomInButton(self.zoomIn, screen_size))
        self.buttons.append(zoomOutButton(self.zoomOut, screen_size))
        self.buttons.append(deletePointButton(lambda : (), screen_size))
        self.buttons.append(openMenuButton(self.toggleMenu, screen_size))
        self.buttons.append(addPointButton(lambda : (), screen_size))

        self.menu = Menu(screen_size)
        self.menuIsActive = False

        self.currentClickedPoint = None
        self.selectedPoint = None
        self.clickDownPosition = (0,0)
        return None

    def onClickDown(self, position):
        ''' This function defines the behavior of the graph object based on the location
            of the mouse when the left mouse button was pressed down. If a button was clicked on,
            then appropriate action will be taken (zoom, clear points, etc.). If a point was
            clicked on, then the graph prepares to reposition the point based on the mouse movements
            after the click
        '''
        self.clickDownPosition = position
        x, y = position

        status = False

        # If the menu is currently active, then check if user clicked on menu
        if self.menuIsActive:
            if self.menu.rect.collidepoint(position):
                status = True

        # Iterate through buttons to determine if user clicked on one
        for button in self.buttons:
            if button.rect.collidepoint(x, y):
                if type(button) == deletePointButton:
                    if self.selectedPoint is not None:
                        self.points.remove(self.selectedPoint)
                button.onClick()
                status = True
                break

        # If user clicked on the menu or a button, then exit function here,
        # as the rest of this function deals with dragging points
        if status:
            return True

        # Check if user is clicking on a point
        for point in self.points:
            if inCircle(point.screenPos, point.radius, position):
                # Save the point that was clicked on in the 'self.currentClickedPoint' object, in
                # order to move the point when the 'self.dragPoint()' method is called externally
                self.currentClickedPoint = point
                return False

        # If user is not clicking on a point, then set saved point reference to None in order to avoid
        # accidentally dragging a point that the user is no longer clicking on
        self.currentClickedPoint = None
        
        return False

    def onClickUp(self, position):

        if self.menuIsActive:
            if self.menu.rect.collidepoint(position[0], position[1]):
                pointToSelect = self.menu.onClick(position)
                if pointToSelect is not None:
                    for point in self.points:
                        if point == pointToSelect:
                            self.selectPoint(point)
                        else:
                            point.select(False)
                return None

        for button in self.buttons:
            if button.rect.collidepoint(position[0], position[1]):
                self.deselectPoints()
                return None
        
        dx = abs(position[0] - self.clickDownPosition[0])
        dy = abs(position[1] - self.clickDownPosition[1])

        for point in self.points:
            if inCircle(point.screenPos, point.radius, position):
                if dx < 4 and dy < 4:
                    if self.selectedPoint is not None and self.selectedPoint != point:
                        self.selectedPoint.select(False)
                    self.selectPoint(point)
                return False

        if dx < 4 and dy < 4:
            addPointButton = self.buttons[-1]
            if addPointButton.selected:
                self.addPoint(position[0], position[1])

        self.deselectPoints()
        return True

    def plot(self):
        ''' This function draws the interpolating polynomial to the screen. It does so by plotting
            a point for every pixel in the screen using the calculated interpolating polynomial and
            then draws a tiny line between each of these points
        '''
        if len(self.points) > 1:
            # 'data' is a list of the form: [(x1, f(x1)), (x1, f(x1)), ...], where each tuple (xi, f(xi))
            # represents a coordinate in screen space to be drawn to the screen
            data = []

            # sx1, sx2 define the range of points to be plotted. sx1 is the x coordinate of the leftmost pixel
            # in screen space, and x2 is the x coordinate of the rightmost pixel in screen space
            sx1, sx2 = self.rect.left, self.rect.right

            # sx stands for 'screen x', which is the x coordinate in screen space to be plotted
            for sx in range(sx1, sx2): # iterate from x1 to x2
                wx = self.convertToWorld(sx, 0)[0] # convert current screen coordinate 'sx' to a world space coordinate 'wx'

                # This following line will end up looking like: wy = P(wx), where P() is the interpolating
                # polynomial. For now, a default polynomial of degree 6 is used
                wy = 0.5*(wx**6) - 2*(wx**5) + 3*(wx**4) - 0.5*(wx**3) - 2*(wx**2) + wx - 1

                # store (screen space x, screen space f(x)) in a tuple called 'c'
                c = (sx, self.convertToScreen(0, wy)[1])
                # append the coordinate 'c' to the list of coordinates 'data'
                data.append(c)

            # Draw a line between each of the plotted points
            pygame.draw.lines(self.screen, (0,0,255), False, data, 2)
        return None
            

    def toggleMenu(self):
        self.menuIsActive = not self.menuIsActive
        if self.menuIsActive:
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

    def addPoint(self, x=math.inf, y=math.inf):
        # Adds a point at the center of the screen in screen space
        if x != math.inf and y != math.inf:
            sx, sy = x,y
            wx, wy = self.convertToWorld(sx, sy)
        else:
            sx, sy = (self.rect.width // 2, self.rect.height // 2)
            wx, wy = self.convertToWorld(sx, sy)
        p = Point((wx, wy), (sx, sy))

        self.points.append(p)
        self.menu.drawPoint(self.points)
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

    def scroll(self, dx, dy):
        self.updatePosition(dx, dy)
        self.plot()

        for point in self.points:
            point.update(self, dx, dy)
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
        
        self.scroll(-self.xOffset, self.yOffset)
        return None

    def dragPoint(self, dx, dy):
        ''' If the user is clicking/holding on a point object, update the
            point's position based on the movement of the mouse while
            the user holds the left mouse button down
        '''
        if self.currentClickedPoint is not None:
            self.currentClickedPoint.update(self, dx, dy)
            self.menu.drawPoint(self.points)
            return True
        return False

    def clear(self):
        ''' Deletes all of the user-created points from the graph
        '''
        self.points = []
        return None

    def displayToScreen(self, screen):
        ''' Copy the graph's local screen onto the main pygame display 'screen'
            in order to display the graph to the window
        '''
        self.__drawGrid__()
        self.plot()
        screen.blit(self.screen, self.rect)

        for point in self.points:
            pygame.draw.circle(screen, point.color, point.screenPos, 5, 0)

        for button in self.buttons:
            if type(button) == deletePointButton and self.selectedPoint is None:
                continue
            screen.blit(button.screen, button.rect)

        if self.menuIsActive:
            self.menu.drawPoint(self.points)
            screen.blit(self.menu.screen, self.menu.rect)
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
                if (ev.key == K_ESCAPE): # If pressed key was 'escape'
                    pygame.quit()
                    sys.exit()
            if (ev.type == MOUSEBUTTONDOWN): # If the user clicked on the screen
                if (ev.button == 1): # Left click
                    x,y = pygame.mouse.get_pos()
                    mouseDown = not graph.onClickDown((x,y))
                elif (ev.button == 4): # Scroll wheel
                    # Zoom in
                    graph.zoom(0)
                elif (ev.button == 5): # Scroll wheel
                    # Zoom out
                    graph.zoom(1)

            if (ev.type == MOUSEBUTTONUP):
                if ev.button == 1:
                    mouseDown = False
                    clickedPointObject = None
                    x,y = pygame.mouse.get_pos()
                    graph.onClickUp((x,y))

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
