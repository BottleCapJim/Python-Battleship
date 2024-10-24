import pygame

pygame.init()
pygame.mixer.init()

cellSize = 50
screenWidth = 1260
screenHeight = 960
ROWS = 10
COLS = 10
hitSound = pygame.mixer.Sound('assets/sounds/explosion.wav')
hitSound.set_volume(0.05)
shotSound = pygame.mixer.Sound('assets/sounds/gunshot.wav')
shotSound.set_volume(0.05)
missSound = pygame.mixer.Sound('assets/sounds/splash.wav')
missSound.set_volume(0.05)

gameScreen = pygame.display.set_mode((screenWidth,screenHeight))

def loadImage(path, size, rotate=False):
    img = pygame.image.load(path).convert_alpha()
    img = pygame.transform.scale(img, size)
    if rotate:
        img = pygame.transform.rotate(img, -90)
    return img

redExplosion = loadImage("assets/images/tokens/redtoken.png", (cellSize, cellSize))
blueExplosion = loadImage("assets/images/tokens/bluetoken.png", (cellSize, cellSize))
greenExplosion = loadImage("assets/images/tokens/greentoken.png", (cellSize, cellSize))

def seperateExplosionImages(explosionSheet, rows, cols, size, newSize):
    image = pygame.Surface((128,128))
    #position on the sheets is topleft 0, 0 and the place where you get the picture from comes after
    image.blit(explosionSheet, (0, 0), (rows * size[0], cols * size[1], size[0], size[1]))
    #transforms it into the size of the grid
    image = pygame.transform.scale(image, (newSize[0], newSize[1]))
    #removes the background from the spreadsheet selected image
    image.set_colorkey((0, 0, 0))
    return image

def loadExplosionImages(size):
    imageList = []
    for imageIndex in range(0,13):
        if imageIndex < 10:
            imageList.append(loadImage(f'assets/images/tokens/fireloop/fire1_ 00{imageIndex}.png', size))

        elif imageIndex < 20:
            imageList.append(loadImage(f'assets/images/tokens/fireloop/fire1_ 0{imageIndex}.png', size))
    return imageList

fireExplosionList = loadExplosionImages((cellSize, cellSize))

#loads in a collective of 128 by 128 images
explosionSheet = pygame.image.load("assets/images/tokens/explosion/explosion.png").convert_alpha()
explosionList = []

for row in range(8):
    for col in range(8):
        explosionList.append(seperateExplosionImages(explosionSheet, col, row,  (cellSize, cellSize), (128, 128)))