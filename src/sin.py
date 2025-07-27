import cv2
import numpy as np

SIZE = 512
SCALE = SIZE // 8
BIAS = SIZE // 2
CENTER = (SIZE//2, SIZE//2)

XMAX = 720
ZMAX = 100

xBIAS = XMAX // 2
zBIAS = ZMAX // 2

BLACK = (0, 0, 0)
BLUE = (255, 0, 0)
GREEN = (0,128,0)
RED = (0,0,255)

FONT = cv2.FONT_HERSHEY_PLAIN
FONT_SIZE = 2
FONT_POS = (10,50)

rBALL = SCALE // 10

def callback(x):
    pass # do nothing

def warp(x, y):

    X = int(SCALE * x + BIAS)
    Y = int(SCALE * y + BIAS)

    return X, Y

def getPos(x,z):

    POS = []

    x0 = -np.sin(np.deg2rad(x))
    y0 = np.cos(np.deg2rad(x))
    
    X0, Y0 = warp(x0, -y0)
    X1, Y1 = warp(-x0, -y0)   

    scale0 = np.exp(-z)
    X2, Y2 = warp(scale0 * ( x0), scale0 * (-y0))

    scale1 = np.exp(z)
    X3, Y3 = warp(scale1 * (-x0), scale1 * (-y0))  

    POS.append((X0, Y0))
    POS.append((X1, Y1))
    POS.append((X2, Y2))
    POS.append((X3, Y3))

    return POS

def main():

    screen = np.ones((SIZE, SIZE, 3),np.uint8)
    screen *= 255

    cv2.imshow('screen', screen)
    cv2.circle(screen, CENTER, SCALE, BLACK, 1)

    cv2.createTrackbar('x','screen',0, XMAX, callback)
    cv2.setTrackbarPos('x','screen',XMAX // 2)
    X = cv2.getTrackbarPos('x','screen')

    cv2.createTrackbar('z','screen',0, ZMAX, callback)
    cv2.setTrackbarPos('z','screen',ZMAX // 2)
    Z = cv2.getTrackbarPos('z','screen')

    prevX = -1
    prevZ = -1

    print('Slide Trackbar to update parameter')
    print('Hit any key to terminate')

    fTerminate = False
    fUpdate = True

    while not fTerminate:

        X = cv2.getTrackbarPos('x','screen')
        Z = cv2.getTrackbarPos('z','screen')

        if X != prevX or Z != prevZ:

            fUpdate = True

            x = X - xBIAS
            z = (Z - zBIAS) / 10

            prevX = X
            prevZ = Z

        if fUpdate:

            clone = screen.copy()

            # draw parameters
            text = 'x:%.d(degree), z:%.2f' % (x, z)
            cv2.putText(clone, text, FONT_POS, FONT, FONT_SIZE, GREEN)

            # draw balls
            POS = getPos(x,z)
            cv2.circle(clone, POS[0], rBALL, BLUE, -1)
            cv2.line(clone, CENTER, POS[0],BLUE, 1)
            cv2.line(clone, CENTER, POS[2],BLUE, 3)

            cv2.circle(clone, POS[1], rBALL, GREEN, -1)
            cv2.line(clone, CENTER, POS[1], GREEN, 1)
            cv2.line(clone, CENTER, POS[3], GREEN, 3)

            cv2.line(clone, ((POS[2][0]+POS[3][0])//2,(POS[2][1]+POS[3][1])//2),POS[3],RED, 5)
       
            cv2.imshow('screen', clone)

            fUpdate = False

        key = cv2.waitKey(10)

        if key != -1:
            fTerminate = True

if __name__ == '__main__':
    main()

