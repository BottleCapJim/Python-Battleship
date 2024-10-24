"""Modules and Initialization"""
import pygame
from GameClasses import Ships, Buttons, Player, EasyComputer, HardComputer
from circularImport import loadImage
import random

pygame.init()
pygame.mixer.init()

# GAME SETTING AND VARIABLES
# The height and width of the screen canvas
screenWidth = 1260
screenHeight = 960
ROWS = 10
COLS = 10
cellSize = 50
buttonImg = 'assets/images/buttons/button.png'
pGameGridImg = loadImage('assets/images/grids/player_grid.png', ((ROWS + 1) * cellSize, (COLS + 1) * cellSize))
cGameGridImg = loadImage('assets/images/grids/comp_grid.png', ((ROWS + 1) * cellSize, (COLS + 1) * cellSize))
deploymentStatus = True
SCANNER = False
INDNUM = 0
textFont = pygame.font.SysFont('Stencil', 60)
# 1 ship position
BLIPPOSITION = None
mainMenuScreenAsset = loadImage('assets/images/background/Battleship.jpg', (screenWidth // 3 * 2, screenHeight))
endScreenAsset = loadImage('assets/images/background/Carrier.jpg', (screenWidth // 3 * 2, screenHeight))
turnScreenAsset = loadImage('assets/images/background/Submarine.jpg', (screenWidth // 3 * 2, screenHeight))
MENU = True  # Added global menu variable
easyStatus = True
computer = HardComputer()
endStatus = False
turnScreenStatus = False
turnBasedStatus = True
playerPlaying = False

# PYGAME DISPLAY / INITIALISATION
gameScreen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption('Battle Ship')

# Game Lists/Dictionary
# This is a dictionary of all the ships and the guns and will be accessed later to make ship objects which will be drawn
# to the grid
# Each vertical ship is initially 75 pixels apart horizontally
# Sizes are adjusted for the scale
# I wanted ships that went into different rows/columns but I thought the amount of effort required for something so simple
# would just be a pain
FLEETS = {
    'battleship': ['battleship', 'assets/images/ships/battleship/battleship.png',
                   (125, 600), (40, 195), 4, 'assets/images/ships/battleship/battleshipgun.png',
                   (0.4, 0.125), [-0.525, -0.34, 0.67, 0.49]],

    'cruiser': ['cruiser', 'assets/images/ships/cruiser/cruiser.png',
                (200, 600), (40, 195), 2, 'assets/images/ships/cruiser/cruisergun.png',
                (0.4, 0.125), [-0.36, 0.64]],

    'destroyer': ['destroyer', 'assets/images/ships/destroyer/destroyer.png',
                  (275, 600), (30, 145), 2, 'assets/images/ships/destroyer/destroyergun.png', (0.5, 0.15),
                  [-0.52, 0.71]],

    'submarine': ['submarine', 'assets/images/ships/submarine/submarine.png',
                  (425, 600), (30, 145), 1, 'assets/images/ships/submarine/submarinegun.png', (0.25, 0.125), [-0.45]],

    'carrier': ['carrier', 'assets/images/ships/carrier/carrier.png', (350, 600), (45, 245), 0, None, None, None],

    'patrol boat': ['patrol boat', 'assets/images/ships/patrol boat/patrol boat.png', (50, 600), (20, 95), 0, None,
                    None, None],

    'rescue ship': ['rescue ship', 'assets/images/ships/rescue ship/rescue ship.png', (500, 600), (20, 95), 0, None,
                    None, None],
}

BUTTONS = [
    Buttons(buttonImg, (150, 50), (1100, 800), 'Randomize'),
    Buttons(buttonImg, (150, 50), (900, 800), 'Reset'),
    Buttons(buttonImg, (150, 50), (700, 800), 'Deployment'),
    Buttons(buttonImg, (150, 50), (500, 800), 'Bomb'),
    Buttons(buttonImg, (250, 100), (900, screenHeight // 2 - 150), 'Easy Computer'),
    Buttons(buttonImg, (250, 100), (900, screenHeight // 2 + 150), 'Hard Computer'),
    Buttons(buttonImg, (250, 100), (900, screenHeight // 2 - 150), 'Turn-by-Turn'),
    Buttons(buttonImg, (250, 100), (900, screenHeight // 2 + 150), 'Multi-shot'),
    Buttons(buttonImg, (250, 100), (900, screenHeight // 2), 'Player vs Player'),
]

def drawText(msg, font, text_col, x, y):
    global gameScreen
    img = font.render(msg, True, text_col)
    gameScreen.blit(img, (x, y))

def increaseAnimationImage(imageList, ind):
    if ind <= 359:
        return imageList[ind]

def displayRadarScanner(imageList, indNum, SCANNER):
    if SCANNER == True and indNum <= 359:
        image = increaseAnimationImage(imageList, indNum)
        return image
    else:
        return False


def displayRadarBlip(num, position):
    if SCANNER:
        image = None
        if position[0] >= 5 and position[1] >= 5:
            if num >= 0 and num <= 90:
                image = increaseAnimationImage(RADARBLIPIMAGES, num // 10)
        elif position[0] < 5 and position[1] >= 5:
            if num >= 90 and num <= 180:
                image = increaseAnimationImage(RADARBLIPIMAGES, (num // 2) // 10)
        elif position[0] < 5 and position[1] < 5:
            if num >= 180 and num <= 270:
                image = increaseAnimationImage(RADARBLIPIMAGES, (num // 3) // 10)
        elif position[0] >= 5 and position[1] < 5:
            if num >= 270 and num <= 360:
                image = increaseAnimationImage(RADARBLIPIMAGES, (num // 4) // 10)
        return image


def loadAnimationImages(path, size, numImages):
    imageList = []
    for imageIndex in range(0, numImages):
        if path == 'assets/images/radar_base/radar_anim' or path == 'assets/images/radar_blip/Blip_':
            if imageIndex < 10:
                imageList.append(loadImage(f'{path}00{imageIndex}.png', size))

            elif imageIndex < 100:
                imageList.append(loadImage(f'{path}0{imageIndex}.png', size))
            elif imageIndex >= 100:
                imageList.append(loadImage(f'{path}{imageIndex}.png', size))
        else:
            if imageIndex < 10:
                imageList.append(loadImage(f'{path} 00{imageIndex}.png', size))

            elif imageIndex < 100:
                imageList.append(loadImage(f'{path} 0{imageIndex}.png', size))
            elif imageIndex >= 100:
                imageList.append(loadImage(f'{path} {imageIndex}.png', size))
    return imageList


def seperateExplosionImages(explosionSheet, rows, cols, newSize, size):
    image = pygame.Surface((128, 128))
    # position on the sheets is topleft 0, 0 and the place where you get the picture from comes after
    image.blit(explosionSheet, (0, 0), (rows * size[0], cols * size[1], size[0], size[1]))
    # transforms it into the size of the grid
    image = pygame.transform.scale(image, (newSize[0], newSize[1]))
    # removes the background from the spreadsheet selected image
    image.set_colorkey((0, 0, 0))
    return image


fireExplosionList = loadAnimationImages('assets/images/tokens/fireloop/fire1_', (cellSize, cellSize), 13)

# loads in a collective of 128 by 128 images
explosionSheet = pygame.image.load("assets/images/tokens/explosion/explosion.png").convert_alpha()
explosionList = []

for row in range(8):
    for col in range(8):
        explosionList.append(seperateExplosionImages(explosionSheet, col, row, (cellSize, cellSize), (128, 128)))

EXPLOSIONS = []
RADARGRIDIMAGES = loadAnimationImages("assets/images/radar_base/radar_anim", (ROWS * cellSize, COLS * cellSize), 360)
# blip needs to be in cell so 50, 50
RADARBLIPIMAGES = loadAnimationImages("assets/images/radar_blip/Blip_", (cellSize, cellSize), 11)
RADARGRID = loadImage('assets/images/grids/grid_faint.png', (ROWS * cellSize, COLS * cellSize))
computerGridImage = loadImage('assets/images/grids/comp_grid.png', ((ROWS + 1) * cellSize, (COLS + 1) * cellSize))
#Loading in the sound
hitSound = pygame.mixer.Sound('assets/sounds/explosion.wav')
hitSound.set_volume(0.05)
shotSound = pygame.mixer.Sound('assets/sounds/gunshot.wav')
shotSound.set_volume(0.05)
missSound = pygame.mixer.Sound('assets/sounds/splash.wav')
missSound.set_volume(0.05)

def mainMenuScreen(gameScreen):
    # creates illusion of switching game screens
    global MENU
    global easyStatus
    global computer
    global turnScreenStatus
    global playerPlaying
    if turnScreenStatus == False:
        if MENU == True:
            gameScreen.blit(mainMenuScreenAsset, (0, 0))
            for button in BUTTONS:
                if button.msgClick == 'Easy Computer' or button.msgClick == 'Hard Computer' or button.msgClick == 'Player vs Player':
                    button.draw(gameScreen)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for button in BUTTONS:
                            if button.buttonRect.collidepoint(pygame.mouse.get_pos()):
                                if button.msgClick == 'Easy Computer':
                                    MENU = False
                                    easyStatus = True
                                    turnScreenStatus = True
                                    computer = EasyComputer()
                                    playerPlaying = False
                                elif button.msgClick == 'Hard Computer':
                                    MENU = False
                                    easyStatus = False
                                    turnScreenStatus = True
                                    playerPlaying = False
                                    computer = HardComputer()
                                elif button.msgClick == 'Player vs Player':
                                    MENU = False
                                    turnScreenStatus = True
                                    playerPlaying = True
                                return

def endScreen(gameScreen):
    # creates illusion of switching game screens
    global endStatus
    global easyStatus
    global MENU
    global turnScreenStatus
    global computer
    global pGameLogic
    global cGameLogic
    global turnScreenStatus
    global deploymentStatus
    gameScreen.blit(endScreenAsset, (0, 0))
    gameWinners = endGameLogic(pGameLogic, cGameLogic)

    if not gameWinners[0]:
        drawText('Computer won', textFont, ('green'), 150, 150)

    elif not gameWinners[1]:
        drawText('Player won', textFont, ('green'), 150, 150)

    for button in BUTTONS:
        if button.msgClick == 'Easy Computer' or button.msgClick == 'Hard Computer':
            button.draw(gameScreen)
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for button in BUTTONS:
                    if button.buttonRect.collidepoint(pygame.mouse.get_pos()):
                        if button.msgClick == 'Easy Computer':
                            endStatus = False
                            easyStatus = True
                            MENU = False
                            turnScreenStatus = False
                            cGameLogic = createGameLogic(ROWS, COLS)
                            pGameLogic = createGameLogic(ROWS, COLS)
                            EXPLOSIONS.clear()
                            for ship in pFleet:
                                ship.returnToDefaultPosition()
                                ship.returnToDefaultPosition()
                            deploymentStatus = True
                            computer = EasyComputer()
                        elif button.msgClick == 'Hard Computer':
                            endStatus = False
                            easyStatus = False
                            MENU = False
                            turnScreenStatus = False
                            cGameLogic = createGameLogic(ROWS, COLS)
                            pGameLogic = createGameLogic(ROWS, COLS)
                            EXPLOSIONS.clear()
                            for ship in pFleet:
                                ship.returnToDefaultPosition()
                                ship.returnToDefaultPosition()
                            deploymentStatus = True
                            computer = HardComputer()
                        return

def endGameLogic(PGAMELOGIC, CGAMELOGIC):
    global endStatus

    # Initialize flags to track if any ships are left
    playerShipsLeft = False
    computerShipsLeft = False

    # Check if there are any 'O's in the game logic grid
    for row in PGAMELOGIC:
        for cell in row:
            if cell == 'O':
                # If 'O' is found, then there are still ships left
                playerShipsLeft = True
                break
        if playerShipsLeft:
            break

    for row in CGAMELOGIC:
        for cell in row:
            if cell == 'O':
                # If 'O' is found, then there are still ships left
                computerShipsLeft = True
                break
        if computerShipsLeft:
            break

    # If no 'O' was found, set endStatus to True
    if not playerShipsLeft or not computerShipsLeft:
        endStatus = True
    else:
        endStatus = False

    winner = [playerShipsLeft, computerShipsLeft]
    return winner

def turnBasedScreen(gameScreen):
    # creates illusion of switching game screens
    global endStatus
    global easyStatus
    global turnScreenStatus
    global turnBasedStatus
    gameScreen.blit(turnScreenAsset, (0, 0))
    for button in BUTTONS:
        if button.msgClick == 'Turn-by-Turn' or button.msgClick == 'Multi-shot':
            button.draw(gameScreen)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if button.buttonRect.collidepoint(pygame.mouse.get_pos()):
                        if button.msgClick == 'Turn-by-Turn':
                            turnScreenStatus = False
                            turnBasedStatus = True
                        elif button.msgClick == 'Multi-shot':
                            turnScreenStatus = False
                            turnBasedStatus = False
                        return


# GAME UTILITY FUNCTIONS
def createGameGrid(rows, cols, cellsize, pos):
    startX = pos[0]
    startY = pos[1]
    coordGrid = []
    for row in range(rows):
        rowX = []
        for col in range(cols):
            rowX.append([startX, startY])
            startX += cellsize
        coordGrid.append(rowX)
        startX = pos[0]
        startY += cellsize
    return coordGrid


def createGameLogic(rows, cols):
    # creates gamelogic spaces ' ' for empty spaces on the grid, this will be used to represent and make changes to the grid
    gamelogic = []
    for row in range(rows):
        rowX = []
        for col in range(cols):
            rowX.append(' ')
        gamelogic.append(rowX)
    return gamelogic


def updateGameLogic(coordGrid, shipList, gameLogic):
    # Updates the gameGrid with the positions of the ships
    for i, rowX in enumerate(coordGrid):
        for j, colX in enumerate(rowX):
            # Checks for a hit or if a ship is there in a specific cell
            if gameLogic[i][j] == 'T' or gameLogic[i][j] == 'X':
                continue
            else:
                gameLogic[i][j] = ' '
                for ship in shipList:
                    if pygame.rect.Rect(colX[0], colX[1], cellSize, cellSize).colliderect(ship.rect):
                        gameLogic[i][j] = 'O'


def showGridOnScreen(window, cellsize, playerGrid, computerGrid):
    gamegrids = [playerGrid, computerGrid]
    for grid in gamegrids:
        for row in grid:
            #            print(row)
            for col in row:
                #                print(col)
                pygame.draw.rect(window, (255, 255, 255), (col[0], col[1], cellsize, cellsize), 1)


def printGameLogic():
    print('Player Grid'.center(50, '#'))
    for i in pGameLogic:
        print(i)
    print('Computer Grid'.center(50, '#'))
    for i in cGameLogic:
        print(i)


# loads the images
def loadImage(path, size, rotate=False):
    img = pygame.image.load(path).convert_alpha()
    img = pygame.transform.scale(img, size)
    # This will be used later once I create the rotate functionality
    if rotate == True:
        img = pygame.transform.rotate(img, -90)
    return img


def createFleet():
    # Empty list that will hold fleet information
    fleet = []
    # Number of keys is 7 so it cycles through the 7 keys
    for name in FLEETS.keys():
        fleet.append(
            Ships(name,
                  FLEETS[name][1],
                  FLEETS[name][2],
                  FLEETS[name][3],
                  FLEETS[name][4],
                  FLEETS[name][5],
                  FLEETS[name][6],
                  FLEETS[name][7])
        )
    return fleet


def updateGameScreen(GAMESCREEN):
    if MENU == True and endStatus == False and turnScreenStatus == False:
        mainMenuScreen(GAMESCREEN)

    if turnScreenStatus == True:
        GAMESCREEN.fill((0, 0, 0))
        turnBasedScreen(GAMESCREEN)

    if MENU == False and endStatus == True and turnBasedStatus == False:
        GAMESCREEN.fill((0, 0, 0))
        endScreen(gameScreen)

    if MENU == False and endStatus == False and turnScreenStatus == False:
        GAMESCREEN.fill((0, 0, 0))
        showGridOnScreen(GAMESCREEN, cellSize, pGameGrid, cGameGrid)
        GAMESCREEN.blit(pGameGridImg, (0, 0))

        for ship in pFleet:
            ship.draw(gameScreen)
            ship.snapShiptoGrid(pGameGrid)

        for ship in cFleet:
            ship.draw(gameScreen)
            ship.snapShiptoGrid(cGameGrid)
        GAMESCREEN.blit(cGameGridImg, (cGameGrid[0][0][0] - 50, cGameGrid[0][0][1] - 50))
        #    GAMESCREEN.blit(computerGridImage, (cGameGrid[0][0][0], cGameGrid[0][-1][-1]))

        for button in BUTTONS:
            button.updateButton(deploymentStatus)
            #        button.redeploy(deploymentStatus)
            if button.msgClick != 'Easy Computer' and button.msgClick != 'Hard Computer'  and \
                    button.msgClick != 'Turn-by-Turn' and button.msgClick != 'Multi-shot' and \
                    button.msgClick != 'Player vs Player':
                button.draw(gameScreen)


            radarScan = displayRadarScanner(RADARGRIDIMAGES, INDNUM, SCANNER)
            if radarScan == False:
                pass
            else:
                GAMESCREEN.blit(radarScan, (cGameGrid[0][0][0], cGameGrid[0][-1][-1]))

            RBlip = displayRadarBlip(INDNUM, BLIPPOSITION)
            if RBlip:
                GAMESCREEN.blit(RBlip, (cGameGrid[BLIPPOSITION[0]][BLIPPOSITION[1]][0],
                                        cGameGrid[BLIPPOSITION[0]][BLIPPOSITION[1]][1]))

            for explosion in EXPLOSIONS:
                explosion.draw(gameScreen)

#        computer.draw(gameScreen, cGameGrid)

        updateGameLogic(pGameGrid, pFleet, pGameLogic)
        updateGameLogic(cGameGrid, cFleet, cGameLogic)
    pygame.display.update()


def sortFleet(ship, shipList):
    # The ships overlap over each other this function moves the current selected ship to the top of the list so no overlap
    shipList.remove(ship)
    shipList.append(ship)


def randomizeShipPositions(shiplist, gamegrid):
    """Select random locations on the game grid for the battleships"""
    placedShips = []
    for i, ship in enumerate(shiplist):
        validPosition = False
        while validPosition == False:
            ship.returnToDefaultPosition()
            rotateShip = random.choice([True, False])
            if rotateShip == True:
                yAxis = random.randint(0, 9)
                xAxis = random.randint(0, 9 - (ship.hImage.get_width() // 50))
                ship.rotateShip(True)
                ship.rect.topleft = gamegrid[yAxis][xAxis]
            else:
                yAxis = random.randint(0, 9 - (ship.vImage.get_height() // 50))
                xAxis = random.randint(0, 9)
                ship.rect.topleft = gamegrid[yAxis][xAxis]
            if len(placedShips) > 0:
                for item in placedShips:
                    if ship.rect.colliderect(item.rect):
                        validPosition = False
                        break
                    else:
                        validPosition = True
            else:
                validPosition = True
        placedShips.append(ship)


def deploymentPhase(deployment):
    if deployment == True:
        return True
    else:
        return False


def pickRandomShipPosition(gameLogic):
    validChoice = False
    posX = 0
    posY = 0
    while not validChoice:
        posX = random.randint(0, 9)
        posY = random.randint(0, 9)
        if gameLogic[posX][posY] == 'O':
            validChoice = True

    return (posX, posY)


def takeTurns(p1, p2):
    if p1.turn == True:
        p2.turn = False
    else:
        p1.turn = False
        p2.turn = True
        while p2.turn:  # Ensure the computer takes its turn until it misses or changes turn
            if playerPlaying == False:
                p2.computerShoot(pGameLogic, pGameGrid, EXPLOSIONS, turnBasedStatus)
            else:
                p2.playerShoot(pGameGrid, pGameLogic, EXPLOSIONS, turnBasedStatus)
        if p2.turn == False:
            p1.turn = True

# LOADING GAME VARIABLES
# p stands for player and the grid in which the player has is initialised here
pGameGrid = createGameGrid(ROWS, COLS, cellSize, (50, 50))
pGameLogic = createGameLogic(ROWS, COLS)
pFleet = createFleet()

# c stands for computer and the grid in which the computer has is initialised here
cGameGrid = createGameGrid(ROWS, COLS, cellSize, (screenWidth - (ROWS * cellSize), 50))
cGameLogic = createGameLogic(ROWS, COLS)
cFleet = createFleet()
randomizeShipPositions(cFleet, cGameGrid)

player1 = Player()
player2 = Player()

# for i in pGameGrid:
#    print(i)

# for i in cGameGrid:
#    print(i)

# printGameLogic()

# code determines the status of pygame and ends the session if event type is quit
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if deploymentStatus == True:
                    for ship in pFleet:
                        if ship.rect.collidepoint(pygame.mouse.get_pos()):
                            sortFleet(ship, pFleet)
                            if not ship.checkShipCollision(pFleet):
                                ship.active = True
                                ship.shipMove()
                else:
                    if player1.turn:
                        player1.playerShoot(cGameGrid, cGameLogic, EXPLOSIONS, turnBasedStatus)
                        takeTurns(player1, computer)  # Switch turns after player shoots
                    while computer.turn:  # Ensure the computer takes its turn until it misses or changes turn
                        computer.computerShoot(pGameGrid, pGameLogic, EXPLOSIONS, turnBasedStatus)
                    takeTurns(player1, computer)  # Switch turns after computer shoots

                for button in BUTTONS:
                    if button.buttonRect.collidepoint(pygame.mouse.get_pos()):
                        #                        if button.msgClick == 'ReDeploy':
                        #                            deploymentStatus = button.redeploy(deploymentStatus)
                        if button.msgClick == 'Randomize':
                            if deploymentStatus == True:
                                button.randomizeShipPositions(pFleet, pGameGrid, randomizeShipPositions)
                                button.randomizeShipPositions(cFleet, cGameGrid, randomizeShipPositions)
                        elif button.msgClick == 'Reset':
                            if deploymentStatus == True:
                                # calling it twice cuz calling it once don't seem enough to return it to the proper position
                                button.resetPosition(pFleet)
                                button.resetPosition(pFleet)
                        elif button.msgClick == 'Deployment':
                            deploymentStatus = deploymentPhase(False)
                        elif button.msgClick == 'ReDeploy':
                            deploymentStatus = deploymentPhase(True)
                            for ship in pFleet:
                                ship.returnToDefaultPosition()
                                ship.returnToDefaultPosition()
                            EXPLOSIONS.clear()
                            button.msgClick = 'Deployment'
                        elif button.msgClick == 'Quit':
                            running = False
                        elif button.msgClick == 'Radar Scan':
                            SCANNER = True
                            INDNUM = 0
                            BLIPPOSITION = pickRandomShipPosition(cGameLogic)
                        elif button.msgClick == 'Bomb' and deploymentStatus == False:
                            button.gridExplosion(cGameGrid, cGameLogic, EXPLOSIONS)
                        if MENU == True:
                            if button.msgClick == 'Easy Computer':
                                MENU = False
                                easyStatus = True
                                computer = EasyComputer()
                                turnScreenStatus = True
                            elif button.msgClick == 'Hard Computer':
                                MENU = False
                                easyStatus = False
                                turnScreenStatus = True
                                computer = HardComputer()

                        if turnScreenStatus == True:
                            if button.msgClick == 'Turn-by-Turn':
                                turnScreenStatus = False
                                MENU = False
                                endStatus = False
                                turnBasedStatus = True

                            elif button.msgClick == 'Multi-shot':
                                turnScreenStatus = False
                                turnBasedStatus = False
                                MENU = False
                                endStatus = False


            elif event.button == 3:  # Right click
                for ship in pFleet:
                    if deploymentStatus == True:
                        ship.rotateShip()

            elif event.button == 2:
                printGameLogic()

        elif event.type == pygame.MOUSEBUTTONUP:
            for ship in pFleet:
                if event.button == 1:
                    sortFleet(ship, pFleet)
                    ship.offTheGrid(pGameGrid)
                    if not ship.checkShipCollision(pFleet):
                        ship.active = False

    for ship in pFleet:
        if deploymentStatus == True:
            ship.shipMove()

    updateGameScreen(gameScreen)
    if SCANNER == True:
        INDNUM += 1

    if easyStatus == True:
        if playerPlaying == True:
            takeTurns(player1, player2)
        else:
            takeTurns(player1, computer)
    if deploymentStatus == False:
        endGameLogic(pGameLogic, cGameLogic)

pygame.quit()
