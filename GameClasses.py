import pygame
import random
from circularImport import redExplosion, blueExplosion, fireExplosionList, explosionList, hitSound, shotSound, missSound

EXPLOSIONS = []


# Did not import loadImage from main.py because of the circular import issue
def loadImage(path, size, rotate=False):
    img = pygame.image.load(path).convert_alpha()
    img = pygame.transform.scale(img, size)
    if rotate:
        img = pygame.transform.rotate(img, -90)
    return img


class Ships:
    # The offset is the how many pixels the gun is from the center
    def __init__(self, name, img, pos, size, numGuns=0, gunPath=None, gunsize=None, gunCoordsOffset=None):
        self.name = name
        #        self.shots = shots
        self.pos = pos
        # v means vertical image size it's originally a vertical image
        self.vImage = loadImage(img, size)
        self.vImageRect = self.vImage.get_rect()
        # This moves the image to the place I need it to be
        self.vImageRect.topleft = self.pos
        # Load horizontal image
        # this is for when the player chooses to rotate the image you know to place it
        # h means horizontal image since Imma transform it
        self.hImage = pygame.transform.rotate(self.vImage, -90)
        self.hImageRect = self.hImage.get_rect()
        self.hImageRect.topleft = pos
        # Images and Rectanges
        self.Image = self.vImage
        self.rect = self.vImageRect
        self.rotation = False
        self.active = False
        self.numGuns = numGuns

        self.gunList = []
        if numGuns > 0:
            for guns in range(numGuns):
                self.gunList.append(Guns(gunPath,
                                         self.rect.center,
                                         (size[0] * gunsize[0], size[1] * gunsize[1]),
                                         gunCoordsOffset[guns]))

    def drawShip(self, window):
        # draws the ships onto the screen
        window.blit(self.Image, self.rect)

    def offTheGrid(self, gridCoords):
        grid_start_x = gridCoords[0][0][0]
        grid_start_y = gridCoords[0][0][1]
        grid_end_x = gridCoords[-1][-1][0] + 50  # Adjust for the cell size
        grid_end_y = gridCoords[-1][-1][1] + 50  # Adjust for the cell size

        if not (grid_start_x <= self.rect.left < grid_end_x and
                grid_start_y <= self.rect.top < grid_end_y and
                grid_start_x < self.rect.right <= grid_end_x and
                grid_start_y < self.rect.bottom <= grid_end_y):
            self.returnToDefaultPosition()

    def draw(self, window):
        # draws the ships onto the screen
        window.blit(self.Image, self.rect)
        for guns in self.gunList:
            guns.drawGuns(window, self)

    def shipMove(self):
        if self.active:
            self.rect.center = pygame.mouse.get_pos()
            self.hImageRect.center = self.vImageRect.center = self.rect.center
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    self.rotateShip()

    def shootbasedMode(self, deployment, pFleet, turn):
        if deployment == True:
            self.rect.center = pygame.mouse.get_pos()
            for guns in range(1, self.numGuns):
                if guns > self.numGuns:
                    turn = True
                else:
                    turn = False
        return turn

    def checkShipCollision(self, shipList):
        # make a copy of pFleet because I don't wanna ruin that one yet
        # if it isn't copied the original list item is removed not the copy
        sList = shipList.copy()
        sList.remove(self)
        for item in sList:
            if self.rect.colliderect(item.rect):
                return True
        return False

    def returnToDefaultPosition(self):
        # Returns the ship to its default position
        self.rect.topleft = self.pos
        self.hImageRect.center = self.vImageRect.center = self.rect.center
        # adding this part made it stop going off the grid because it’s set to its default vertical position
        self.rotation = False
        self.switchImageAndRect()

    def adjustShipPosition(self):
        # I'm sure there's a better way to do this, possibly by equating the position of the ships to the center of the grid
        # but I took a more manual approach, I could later change this to make the program more future proof
        if self.Image == self.vImage:
            if self.name == 'patrol boat':
                self.rect.x += 15  # Adjust the x position for the patrol boat
            elif self.name == 'rescue ship':
                self.rect.x += 15  # Adjust the x position for the rescue ship
            elif self.name == 'cruiser':
                self.rect.x += 5  # Adjust the x position for the cruiser
            elif self.name == 'destroyer':
                self.rect.x += 10  # Adjust the x position for the destroyer
            elif self.name == 'submarine':
                self.rect.x += 10  # Adjust the x position for the submarine
            elif self.name == 'battleship':
                self.rect.x += 5  # Adjust the x position for battleship

        elif self.Image == self.hImage:
            if self.name == 'patrol boat':
                self.rect.y += 15  # Adjust the y position for the patrol boat
            elif self.name == 'rescue ship':
                self.rect.y += 15  # Adjust the y position for the rescue ship
            elif self.name == 'cruiser':
                self.rect.y += 5  # Adjust the y position for the cruiser
            elif self.name == 'destroyer':
                self.rect.y += 10  # Adjust the y position for the destroyer
            elif self.name == 'submarine':
                self.rect.y += 10  # Adjust the y position for the submarine
            elif self.name == 'battleship':
                self.rect.y += 5  # Adjust the y position for the battleship

    def snapShiptoGrid(self, gridCoords):
        snapped = False
        cellSize = 50  # Define the cell size here
        for row in gridCoords:
            for cell in row:
                cell_rect = pygame.Rect(cell[0], cell[1], cellSize, cellSize)
                if self.rect.colliderect(cell_rect):
                    self.rect.topleft = (cell[0], cell[1])
                    self.adjustShipPosition()

                    self.vImageRect.center = self.hImageRect.center = self.rect.center
                    snapped = True
                    break
            if snapped:
                break
        if not snapped:
            self.returnToDefaultPosition()

            if not snapped:
                self.returnToDefaultPosition()

    def rotateShip(self, doRotation=False):
        """switch ship between vertical and horizontal"""
        if self.active or doRotation == True:
            if self.rotation == False:
                self.rotation = True
            else:
                self.rotation = False
            self.switchImageAndRect()

    def switchImageAndRect(self):
        """Switches from Horizontal to Vertical and vice versa"""
        if self.rotation == True:
            self.Image = self.hImage
            self.rect = self.hImageRect
        else:
            self.Image = self.vImage
            self.rect = self.vImageRect
        self.hImageRect.center = self.vImageRect.center = self.rect.center


class Guns:
    def __init__(self, gunImage, pos, size, offset):
        self.gunImage = loadImage(gunImage, size, True)
        self.offset = offset
        self.gunImageRect = self.gunImage.get_rect()

    def update(self, ship):
        # Updates the gun position on the ship
        self.gunImageRect.center = (ship.rect.centerx, ship.rect.centery + (ship.Image.get_height() // 2 * self.offset))

    #    def numberOfShots(self, turn, fleets, numGuns):
    #        if turn == True:
    #            self.gunImageRect.center = pygame.mouse.get_pos()
    #            for ship in fleets:
    #                if self.gunImageRect.center == ship.rect.center:
    #                    if len(numGuns) > self.guns:
    #                        turn = False
    #                        self.guns += 1
    #                    else:
    #                        turn = True

    #       for event in pygame.event.get():
    #           if event.type == pygame.MOUSEBUTTONDOWN:
    #               if event.button == 3:
    #                   self.rotateShip()
    #
    def drawGuns(self, window, ship):
        self.update(ship)
        window.blit(self.gunImage, self.gunImageRect)


class Buttons:
    def __init__(self, Img, size, pos, msg):
        self.pos = pos
        self.buttonImg = loadImage(Img, size)
        self.buttonRect = self.buttonImg.get_rect()
        self.ImageLarger = pygame.transform.scale(self.buttonImg, (size[0] + 10, size[1] + 10))
        self.buttonRect.topleft = pos
        # centerizes the text with the buttonrect so it don't look like it's in the corner
        self.msgClick = msg
        self.msg = self.addText(msg)
        self.msgRect = self.msg.get_rect(center=self.buttonRect.center)

    def addText(self, msg):
        """add font of the image button"""
        font = pygame.font.SysFont('Stencil', 22)
        message = font.render(msg, 1, (255, 255, 255))
        return message

    def focusOnButton(self, window):
        if self.buttonRect.collidepoint(pygame.mouse.get_pos()):
            window.blit(self.ImageLarger,
                        (self.buttonRect[0] - 5, self.buttonRect[1] - 5, self.buttonRect[2], self.buttonRect[3]))
        else:
            window.blit(self.buttonImg, self.buttonRect)

    def actionOnPress(self, pFleet, shipList, gameGrid):
        pass

    def updateButton(self, gameStatus):
        if self.msgClick == 'Reset' and gameStatus == False:
            self.msgClick = 'Quit'
        if self.msgClick == 'Quit' and gameStatus == True:
            self.msgClick = 'Reset'
        elif self.msgClick == 'Deployment' and gameStatus == False:
            self.msgClick = 'ReDeploy'
        elif self.msgClick == 'ReDeploy' and gameStatus == True:
            self.msgClick = 'Deployment'
        elif self.msgClick == 'Randomize' and gameStatus == False:
            self.msgClick = 'Radar Scan'
        elif self.msgClick == 'Radar Scan' and gameStatus == True:
            self.msgClick = 'Randomize'
        self.msg = self.addText(self.msgClick)
        self.msgRect = self.msg.get_rect(center=self.buttonRect.center)

    def randomizeShipPositions(self, shipList, gameGrid, randomizePos):
        randomizePos(shipList, gameGrid)

    def resetPosition(self, shipList):
        for ship in shipList:
            ship.returnToDefaultPosition()

    def draw(self, window):
        self.focusOnButton(window)
        window.blit(self.msg, self.msgRect)

    def gridExplosion(self, coordGrid, gameLogic, EXPLOSIONS):
        # Choose a random cell in the grid
        random_row = random.randint(0, len(coordGrid) - 2)
        random_col = random.randint(0, len(coordGrid[0]) - 2)

        # Create a 2x2 area to "shoot"
        for i in range(2):
            for j in range(2):
                cell_x, cell_y = random_row + i, random_col + j
                if gameLogic[cell_x][cell_y] != ' ':
                    if gameLogic[cell_x][cell_y] == 'O':
                        gameLogic[cell_x][cell_y] = 'T'
                        EXPLOSIONS.append(Explosion(redExplosion, coordGrid[cell_x][cell_y], 'Hit', None, None, None))
                    else:
                        EXPLOSIONS.append(Explosion(blueExplosion, coordGrid[cell_x][cell_y], 'Miss', None, None, None))
                else:
                    if gameLogic[cell_x][cell_y] != 'T':
                        gameLogic[cell_x][cell_y] = 'X'
                        EXPLOSIONS.append(Explosion(blueExplosion, coordGrid[cell_x][cell_y], 'Miss', None, None, None))

        return EXPLOSIONS


class Player:
    def __init__(self):
        self.turn = True

    def playerShoot(self, coordGrid, gameLogic, EXPLOSIONS, turnBased):
        posX, posY = pygame.mouse.get_pos()
        # first one is the original bottom left pos, second on is 1 cell up and next is right bottom last is top right this makes up the grid
        # tbh I don't know what these represent
        if posX >= coordGrid[0][0][0] and posX <= coordGrid[0][-1][0] + 50 and posY >= coordGrid[0][0][1] and posY <= \
                coordGrid[-1][0][1] + 50:
            for i, rowX in enumerate(coordGrid):
                for j, colX in enumerate(rowX):
                    if posX >= colX[0] and posX < colX[0] + 50 and posY >= colX[1] and posY <= colX[1] + 50:
                        # Checks for a hit or if a ship is there in a specific cell
                        if gameLogic[i][j] != ' ':
                            if gameLogic[i][j] == 'O':
                                gameLogic[i][j] = 'T'
                                if turnBased == True:
                                    self.turn = False
                                else:
                                    self.turn = True
                                print('Hit')
                                shotSound.play()
                                missSound.play()
                                EXPLOSIONS.append(Explosion(redExplosion, coordGrid[i][j], 'Hit', None, None, None))
                        else:
                            gameLogic[i][j] = 'X'
                            print('Miss')
                            shotSound.play()
                            missSound.play()
                            EXPLOSIONS.append(Explosion(blueExplosion, coordGrid[i][j], 'Hit', None, None, None))
                            self.turn = False
        return EXPLOSIONS


class EasyComputer:
    def __init__(self):
        self.turn = False
        self.status = self.computerStatus('Thinking')
        self.name = 'Easy Computer'

    def computerStatus(self, msg):
        image = pygame.font.SysFont('Stencil', 22)
        message = image.render(msg, 1, (0, 0, 0))
        return message

    def computerShoot(self, gameLogic, pGameGrid, EXPLOSIONS, turnBased):
        validChoice = False
        while not validChoice:
            rowX = random.randint(0, 9)
            colX = random.randint(0, 9)

            if gameLogic[rowX][colX] == ' ' or gameLogic[rowX][colX] == 'O':
                validChoice = True

            if gameLogic[rowX][colX] == 'O':
                gameLogic[rowX][colX] = 'T'
                print('Hit')
                shotSound.play()
                hitSound.play()
                EXPLOSIONS.append(
                    Explosion(redExplosion, pGameGrid[rowX][colX], 'Hit', fireExplosionList, explosionList, None))
                if turnBased == True:
                    self.turn = False
                else:
                    self.turn = True
            else:
                if gameLogic[rowX][colX] != 'T':
                    gameLogic[rowX][colX] = 'X'
                    print('Miss')
                    shotSound.play()
                    missSound.play()
                    EXPLOSIONS.append(Explosion(blueExplosion, pGameGrid[rowX][colX], 'Hit', None, None, None))
                    self.turn = False
                else:
                    self.turn = True

        return EXPLOSIONS

    def draw(self, window, cGameGrid):
        cellSize = 50
        if self.turn:
            window.blit(self.status, (cGameGrid[0][0][0] - cellSize, cGameGrid[-1][-1][1] + cellSize))


class HardComputer(EasyComputer):
    def __init__(self):
        # inherits easy computers attributes
        super().__init__()
        self.moves = []

    def computerShoot(self, gameLogic, pGameGrid, EXPLOSIONS, turnBased):
        if len(self.moves) == 0:
            validChoice = False
            while not validChoice:
                rowX = random.randint(0, 9)
                rowY = random.randint(0, 9)

                if gameLogic[rowX][rowY] == ' ' or gameLogic[rowX][rowY] == 'O':
                    validChoice = True

                if gameLogic[rowX][rowY] == 'O':
                    gameLogic[rowX][rowY] = 'T'
                    print('Hit')
                    shotSound.play()
                    hitSound.play()
                    EXPLOSIONS.append(
                        Explosion(redExplosion, pGameGrid[rowX][rowY], 'Hit', fireExplosionList, explosionList, None))
                    self.generateMoves((rowX, rowY), gameLogic)
                    if turnBased == True:
                        self.turn = False
                    else:
                        self.turn = True
                else:
                    if gameLogic[rowX][rowY] != 'T':
                        gameLogic[rowX][rowY] = 'X'
                        print('Miss')
                        shotSound.play()
                        missSound.play()
                        EXPLOSIONS.append(Explosion(blueExplosion, pGameGrid[rowX][rowY], 'Hit', None, None, None))
                        self.turn = False
                    else:
                        self.turn = True

        elif len(self.moves) > 0:
            rowX, rowY = self.moves[0]
            EXPLOSIONS.append(
                Explosion(redExplosion, pGameGrid[rowX][rowY], 'Hit', fireExplosionList, explosionList, None))
            gameLogic[rowX][rowY] = 'T'
            self.moves.remove((rowX, rowY))
            self.turn = False

        return EXPLOSIONS

    def generateMoves(self, coords, grid, lstDir=None):
        x, y = coords
        nx, ny = 0, 0
        for direction in ['North', 'South', 'East', 'West']:
            if direction == 'North' and lstDir != 'North':
                nx = x - 1
                ny = y
                if not (nx > 9 or ny > 9 or nx < 0 or ny < 0):
                    if (nx, ny) not in self.moves and grid[nx][ny] == 'O':
                        self.moves.append((nx, ny))
                        self.generateMoves((nx, ny), grid, 'South')

            if direction == 'South' and lstDir != 'South':
                nx = x + 1
                ny = y
                if not (nx > 9 or ny > 9 or nx < 0 or ny < 0):
                    if (nx, ny) not in self.moves and grid[nx][ny] == 'O':
                        self.moves.append((nx, ny))
                        self.generateMoves((nx, ny), grid, 'North')

            if direction == 'East' and lstDir != 'East':
                nx = x
                ny = y + 1
                if not (nx > 9 or ny > 9 or nx < 0 or ny < 0):
                    if (nx, ny) not in self.moves and grid[nx][ny] == 'O':
                        self.moves.append((nx, ny))
                        self.generateMoves((nx, ny), grid, 'East')

            if direction == 'West' and lstDir != 'West':
                nx = x
                ny = y - 1
                if not (nx > 9 or ny > 9 or nx < 0 or ny < 0):
                    if (nx, ny) not in self.moves and grid[nx][ny] == 'O':
                        self.moves.append((nx, ny))
                        self.generateMoves((nx, ny), grid, 'East')

        return


class Explosion:
    # This class will animate the explosition in the cell which got hit or missed factors determine the image shown
    def __init__(self, image, pos, action, imageList=None, explositionList=None, soundFile=None):
        self.image = image
        self.pos = pos
        # set up rect with topleft cuz thats where the grid is
        self.rect = self.image.get_rect(topleft=pos)
        self.imageList = imageList
        self.action = action
        self.timer = pygame.time.get_ticks()
        self.imageIndex = 0
        self.explosionList = explositionList
        self.explosionIndex = 0
        self.explosion = False

    def animateExplosion(self):
        # Look into this
        self.explosionIndex += 1
        if self.explosionIndex < len(self.explosionList):
            return self.explosionList[self.explosionIndex]
        else:
            return self.animateFire()

        # Fill in later

    #        if gameLogic[rowX][colX] == 'T':
    #            self.explosion = True
    #            if self.explosion == True:
    #                for i in self.imageList:
    #                    window.blit()

    def animateFire(self):
        # Gives room to the animation does not look instant
        if pygame.time.get_ticks() >= self.timer >= 100:
            self.timer = pygame.time.get_ticks()
            self.imageIndex += 1
        """makes it so the image iterates with the amount of images"""
        if self.imageIndex < len(self.imageList):
            return self.imageList[self.imageIndex]
        else:
            # once the animation is finished the animation occurs again
            self.imageIndex = 0
            return self.imageList[self.imageIndex]

    #        if gameLogic[rowX][colX] == 'T':
    #                self.explosion = True
    #                if self.explosion == True:
    #                    for i in self.explosionList:
    #                        window.blit()

    def draw(self, window):
        # if the value is still none
        if not self.imageList:
            window.blit(self.image, self.rect)
        else:
            self.image = self.animateExplosion()
            self.rect = self.image.get_rect(topleft=self.pos)
            self.rect[1] = self.pos[1] - 10
            if pygame.time.get_ticks() >= self.timer >= 100:
                window.blit(self.image, self.rect)
