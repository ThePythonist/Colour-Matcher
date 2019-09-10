import pygame
import sys
import time
import random
from pygame.locals import *

pygame.init()

screen = pygame.display.set_mode((1600, 900), RESIZABLE)

pygame.display.set_caption("ColourMatch")

colours = {"background": (255,255,255),
           "button": (255, 200, 200),
           "buttonOutline": (0, 0, 0),
           "activeButton": (200, 200, 255),
           "titleStartColour": (255, 28, 88),
           "titleEndColour": (0, 2, 122),
           "infoColour": (0, 0, 0),
           "solveColour": (150, 255, 150)}

class Tile:
    moving = False
    dragging = False
    absX = 0
    absY = 0
    toX = 0
    toY = 0
    totalMoveTime = 0.5
    startMoveTime = 0
    def __init__(self, x, y, totalWidth, totalHeight, width, height, colour, fixed):
        self.x = x
        self.y = y
        self.correctX = x
        self.correctY = y
        self.totalWidth = totalWidth
        self.totalHeight = totalHeight
        self.width = width
        self.height = height
        self.colour = colour
        self.fixed = fixed
    def display(self, screen):
        startX = (1-self.totalWidth)/2.0 * screen.get_width()
        startY = (1-self.totalHeight)/2.0 * screen.get_height()
        realWidth = int(self.width*screen.get_width())
        realHeight = int(self.height*screen.get_height())
        xToUse = self.x
        yToUse = self.y
        if self.moving or self.dragging:
            xToUse = self.absX
            yToUse = self.absY
        pygame.draw.rect(screen, self.colour, (startX + xToUse * realWidth, startY + yToUse * realHeight, realWidth, realHeight))
        if self.fixed:
            pygame.draw.circle(screen, (0, 0, 0), (int(startX + (xToUse + 0.5) * realWidth), int(startY + (yToUse + 0.5) * realHeight)), int(max(realWidth/10.0, realHeight/10.0)))
            pygame.draw.circle(screen, (200, 200, 200), (int(startX + (xToUse + 0.5) * realWidth), int(startY + (yToUse + 0.5) * realHeight)), int(max(realWidth/10.0, realHeight/10.0))-2)
    def move(self, toX, toY):
        self.moving = True
        self.toX = toX
        self.toY = toY
        self.startMoveTime = time.time()
    def update(self):
        if self.moving:
            timeElapsed = time.time()-self.startMoveTime
            proportion = timeElapsed / self.totalMoveTime
            self.absX = lerp(self.x, self.toX, proportion)
            self.absY = lerp(self.y, self.toY, proportion)
            if proportion >= 1:
                self.moving = False
                self.x = self.toX
                self.y = self.toY
        


def lerp(a, b, t):
    return (b-a)*t + a

def lerpColour(a, b, t):
    aR, aG, aB = a
    bR, bG, bB = b
    return (lerp(aR, bR, t), lerp(aG, bG, t), lerp(aB, bB, t))

def populate():
    tiles = []
    horizontalCount = random.randint(5, 7)
    verticalCount = random.randint(5, 7)
    fixedProbability = 0.5
    if mode == 1:
        horizontalCount = random.randint(8, 11)
        verticalCount = random.randint(8, 11)
        fixedProbability = 0.35
    if mode == 2:
        horizontalCount = random.randint(12, 16)
        verticalCount = random.randint(12, 16)
        fixedProbability = 0.2
    totalWidth = 0.5
    totalHeight = 0.5
    width = totalWidth / float(horizontalCount)
    height = totalHeight / float(verticalCount)
    availableColours = [(0, 2, 122), (0, 255, 182), (239, 124, 212), (249, 216, 0), (0, 249, 8), (255, 28, 88)]
    random.shuffle(availableColours)
    cornerColours = availableColours[:4]
    for y in range(verticalCount):
        leftColour = lerpColour(cornerColours[0], cornerColours[1], float(y)/float(verticalCount-1))
        rightColour = lerpColour(cornerColours[2], cornerColours[3], float(y)/float(verticalCount-1))
        for x in range(horizontalCount):
            colour = lerpColour(leftColour, rightColour, float(x)/float(horizontalCount-1))
            fixed = random.random() < fixedProbability
            tile = Tile(x, y, totalWidth, totalHeight, width, height, colour, fixed)
            tiles.append(tile)
    return tiles

def shuffle(tiles):
    unfixed = []
    positions = []
    for tile in tiles:
        if not tile.fixed:
            unfixed.append(tile)
            positions.append([tile.x, tile.y])
    random.shuffle(positions)
    for i in range(len(unfixed)):
        unfixed[i].move(positions[i][0], positions[i][1])

def getMousePosInGrid(tiles):
    startX = (1-tiles[0].totalWidth) / 2
    startY = (1-tiles[0].totalHeight) / 2
    tileWidth = tiles[0].width
    tileHeight = tiles[0].height

    mouseX, mouseY = pygame.mouse.get_pos()
    mouseXNorm = mouseX/float(screen.get_width())
    mouseYNorm = mouseY/float(screen.get_height())

    mouseXRel = mouseXNorm - startX
    mouseYRel = mouseYNorm - startY

    return [mouseXRel/tileWidth, mouseYRel/tileHeight]
    
reset = True
timeReset = 0
shuffled = False
finishedShuffling = False
timeBeforeShuffle = 0.5
solved = False
timeAtSolve = 0
timeBeforeReset = 3

tiles = []

dragging = None
draggingDif = []

mode = 0
modes = ["Easy", "Medium", "Hard"]
buttonFont = pygame.font.SysFont("Courier", 30)
buttonWidth = 0.1
buttonHeight = 0.1
buttonPaddingX = 0.05
buttonPaddingY = (0.25 - buttonHeight) / 2.0
modeLabels = []
for m in modes:
    modeLabels.append(buttonFont.render(m, False, (colours["buttonOutline"])))

title = "ColourSwap"
titleFont = pygame.font.SysFont("Courier", 60, True)
titleLabels = []
titleWidth = 0
titleHeight = 0
for i in range(len(title)):
    colour = lerpColour(colours["titleStartColour"], colours["titleEndColour"], i/float(len(title)-1))
    label = titleFont.render(title[i], False, colour)
    titleLabels.append(label)
    titleWidth += label.get_width()
    titleHeight = max(titleHeight, label.get_height())

infoFont = pygame.font.SysFont("Courier", 30)
infoLabel = infoFont.render("Press 'R' to Generate a New Puzzle", False, colours["infoColour"])
infoPadding = 0.025

solveWidth = 0.9
solveHeight = 0.9

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == VIDEORESIZE:
            screen = pygame.display.set_mode(event.size, RESIZABLE)
        if event.type == KEYDOWN:
            if event.key == K_r:
                reset = True
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                totalWidth = (buttonWidth * len(modes) + buttonPaddingX * (len(modes)-1)) * screen.get_width()
                startX = (screen.get_width()-totalWidth)/2.0
                startY = (1-buttonPaddingY-buttonHeight) * screen.get_height()
                mousePos = pygame.mouse.get_pos()
                for i in range(len(modes)):
                    buttonX = startX + i * (buttonWidth + buttonPaddingX) * screen.get_width()
                    if buttonX <= mousePos[0] <= buttonX + buttonWidth * screen.get_width() and startY <= mousePos[1] <= startY + buttonHeight * screen.get_height():
                        if mode != i:
                            mode = i
                            reset = True
                if finishedShuffling and not solved:
                    mousePosInGrid = getMousePosInGrid(tiles)
                    for tile in tiles:
                        if int(mousePosInGrid[0]) == tile.x and int(mousePosInGrid[1]) == tile.y and not tile.fixed:
                            dragging = tile
                            draggingDif = [tile.x - mousePosInGrid[0], tile.y - mousePosInGrid[1]]
                            tile.dragging = True
        if event.type == MOUSEBUTTONUP:
            if event.button == 1:
                if dragging is not None:
                    dragging.dragging = False
                    found = False
                    for tile in tiles:
                        if tile != dragging and not tile.fixed and tile.x == round(dragging.absX) and tile.y == round(dragging.absY):
                            found = True
                            tile.move(dragging.x, dragging.y)
                            dragging.x = dragging.absX
                            dragging.y = dragging.absY
                            dragging.move(tile.x, tile.y)
                    if not found:
                        oldX = dragging.x
                        oldY = dragging.y
                        dragging.x = dragging.absX
                        dragging.y = dragging.absY
                        dragging.move(oldX, oldY)
                    dragging = None

    screen.fill(colours["background"])

    if solved:
        if time.time() - timeAtSolve >= timeBeforeReset:
            reset = True
        else:
            pygame.draw.rect(screen, colours["solveColour"], ((1-solveWidth)/2.0 * screen.get_width(), (1-solveHeight)/2.0 * screen.get_height(), solveWidth * screen.get_width(), solveHeight * screen.get_height()))

    startX = (screen.get_width()-titleWidth)/2.0
    startY = (0.25 * screen.get_height() - titleHeight)/2.0
    xOffset = 0
    for i in titleLabels:
        screen.blit(i, (startX+xOffset, startY))
        xOffset += i.get_width()
    screen.blit(infoLabel, ((screen.get_width()-infoLabel.get_width())/2.0, startY+titleHeight + infoPadding * screen.get_height()))

    totalWidth = (buttonWidth * len(modes) + buttonPaddingX * (len(modes)-1)) * screen.get_width()
    startX = (screen.get_width()-totalWidth)/2.0
    startY = (1-buttonPaddingY-buttonHeight) * screen.get_height()
    for i in range(len(modes)):
        pygame.draw.rect(screen, colours["activeButton"] if mode == i else colours["button"], (startX + i * (buttonWidth + buttonPaddingX) * screen.get_width(), startY, buttonWidth * screen.get_width(), buttonHeight * screen.get_height()))
        pygame.draw.rect(screen, colours["buttonOutline"], (startX + i * (buttonWidth + buttonPaddingX) * screen.get_width(), startY, buttonWidth * screen.get_width(), buttonHeight * screen.get_height()), 2)
        screen.blit(modeLabels[i], (startX + i * (buttonWidth + buttonPaddingX) * screen.get_width() + (buttonWidth * screen.get_width() - modeLabels[i].get_width())/2.0, startY + (buttonHeight * screen.get_height() - modeLabels[i].get_height())/2.0))
    
    if reset:
        tiles = populate()
        reset = False
        shuffled = False
        finishedShuffling = False
        solved = False
        timeReset = time.time()
    for tile in tiles:
        tile.update()
        if not tile.moving and not tile.dragging:
            tile.display(screen)
    for tile in tiles:
        if tile.moving:
            tile.display(screen)
    if time.time() - timeReset >= timeBeforeShuffle and not shuffled:
        shuffle(tiles)
        shuffled = True

    if shuffled and not finishedShuffling:
        finishedShuffling = True
        for tile in tiles:
            if tile.moving:
                finishedShuffling = False
    
    if finishedShuffling and not solved:
        if dragging is not None:
            mousePosInGrid = getMousePosInGrid(tiles)
            dragging.absX = mousePosInGrid[0] + draggingDif[0]
            dragging.absY = mousePosInGrid[1] + draggingDif[1]
            dragging.display(screen)
        solved = True
        for tile in tiles:
            if tile.x != tile.correctX or tile.y != tile.correctY:
                solved = False
        if solved:
            timeAtSolve = time.time()
    
    
    time.sleep(0.01)
    pygame.display.update()
