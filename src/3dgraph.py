import cv2, os, sys
import glfw
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *

# f(x,z)の定義式を格納したファイル
FILE_EQUATION = 'equation.txt'
expression = None

fRedefineSurface = False

# マウスドラッグ中かどうか
isDragging = False

# マウスのクリック位置
oldPos = [0, 0]
newPos = [0, 0]

# 操作の種類
MODE_NONE = 0x00
MODE_TRANSLATE = 0x01
MODE_ROTATE = 0x02
MODE_SCALE = 0x04

# マウス移動量と回転、平行移動の倍率
ROTATE_SCALE = 10.0
TRANSLATE_SCALE = 50.0

# 座標変換のための変数
Mode = MODE_NONE
Scale = 6.0
Xscale = 1.0
Yscale = 1.0
Zscale = 1.0

#MODEL_SIZE = 1.0
MODEL_SIZE = 0.2

# スキャンコード定義
SCANCODE_LEFT  = 331
SCANCODE_RIGHT = 333
SCANCODE_UP    = 328
SCANCODE_DOWN  = 336
SCANCODE_ESC   = 1

# キーコード定義
KEY_A = 65
KEY_R = 82
KEY_S = 83
KEY_I = 73
KEY_X = 88
KEY_Y = 89
KEY_Z = 90

KEY_MINUS = 45
KEY_ESC = 256

KEY_STATE_NONE = 0
KEY_STATE_PRESS_R = 1

KeyState = KEY_STATE_NONE
PrevKeyState = KEY_STATE_NONE

# 方位角、仰角
AZIMUTH = 0.0
ELEVATION = 0.0
ROLL = 0.0

dAZIMUTH = 0.0
dELEVATION = 0.0

# モデル位置
ModelPos = [0.0, 0.0]

WIN_WIDTH = 512  # ウィンドウの幅 / Window width
WIN_HEIGHT = 512  # ウィンドウの高さ / Window height
WIN_TITLE = "Translucent"  # ウィンドウのタイトル / Window title

idxModel = -1

frameNo = 1

NUM = 50

v = np.empty((NUM, NUM, 3), np.float32)
#n = np.empty((NUM, NUM, 3), np.float32)

light_ambient = [0.2, 0.2, 0.2, 1.0]
light_diffuse = [0.8, 0.8, 0.8, 1.0]
light_specular = [0.8, 0.8, 0.8, 1.0]

mat_ambient1 = [0.7, 0.7, 0.7, 1.0]
mat_diffuse1 = [1.0, 1.0, 1.0, 1.0]
mat_specular1 = [1.0, 1.0, 1.0, 1.0]
mat_shininess1 = [100.0]

mat_ambient = [0.5, 0.5, 0.7, 0.85]
mat_diffuse = [0.1, 0.5, 0.8, 0.85]
mat_specular = [1.0, 1.0, 1.0, 0.85]
mat_shininess = [100.0]

NR_DIVS = 10

# テクスチャー画像
textureImages = []

textureIds = []
idxCubeFaces = []

points = np.empty((12, 3), np.float32)
faces = np.empty((6, 4), np.int32)
TexCoords = np.empty((4,2), np.float32)

filename_x = 'x.png'
filename_y = 'y.png'
filename_z = 'z.png'

# flags
flagRunning = True

flagInertia = False

flagAmbient = True
flagDiffuse = True
glagSpecular = True

flagAxis = True

def defineSurface():

    for i in range(NUM):
        for j in range(NUM):
            z = i / 10.0 - NUM / 10.0 / 2.0
            x = j / 10.0 - NUM / 10.0 / 2.0

            z *= Zscale
            x *= Xscale

            y = eval(expression)
            
            v[i][j][0] = x / Xscale
            v[i][j][1] = y
            v[i][j][2] = z / Zscale

            #r = np.sqrt((x * 2.0) ** 2 + 1.0 + (z * 2.0) ** 2)

            #n[i][j][0] = (x * 2.0) / r
            #n[i][j][1] = 1.0 / r
            #n[i][j][2] = -(z * 2.0) / r

def createPlate(size):

    # points for x
    points[ 0] = ( -size/2,  size/2, 0)
    points[ 1] = (  size/2,  size/2, 0)
    points[ 2] = (  size/2, -size/2, 0)
    points[ 3] = ( -size/2, -size/2, 0)

    # points for y
    points[ 4] = ( -size/2,  size/2, 0)
    points[ 5] = (  size/2,  size/2, 0)
    points[ 6] = (  size/2, -size/2, 0)
    points[ 7] = ( -size/2, -size/2, 0)

    # points for z
    points[ 8] = ( -size/2,  size/2, 0)
    points[ 9] = (  size/2,  size/2, 0)
    points[10] = (  size/2, -size/2, 0)
    points[11] = ( -size/2, -size/2, 0)

    TexCoords[0] = (1.0, 0.0)
    TexCoords[1] = (1.0, 1.0)
    TexCoords[2] = (0.0, 1.0)
    TexCoords[3] = (0.0, 0.0)
    
    faces[0] = (  0,  1,  2,  3)
    faces[1] = (  4,  5,  6,  7)
    faces[2] = (  8,  9, 10, 11)
    faces[3] = ( 12, 13, 14, 15)
    faces[4] = ( 16, 17, 18, 19)
    faces[5] = ( 20, 21, 22, 23)

def createFace(i):

    glBegin(GL_POLYGON)

    idx0 = faces[i][0]
    idx1 = faces[i][1]
    idx2 = faces[i][2]
    idx3 = faces[i][3]

    glVertex3fv(points[idx0])
    glTexCoord2fv(TexCoords[0])

    glVertex3fv(points[idx1])
    glTexCoord2fv(TexCoords[1])

    glVertex3fv(points[idx2])
    glTexCoord2fv(TexCoords[2])

    glVertex3fv(points[idx3])
    glTexCoord2fv(TexCoords[3])
    
    glEnd()

def createArrow(base, height):

    center = (0.0, 0.0, 0.0)
    bottom = np.empty((NR_DIVS, 3), np.float32)
    top = (0.0, 0.0, height)

    bottom[0] = (base, 0.0, 0.0)
    for i in range(1, NR_DIVS):
        theta = np.pi * 2 / NR_DIVS * i
        x = np.cos(theta) * bottom[0][0] - np.sin(theta) * bottom[0][1]
        y = np.sin(theta) * bottom[0][0] + np.sin(theta) * bottom[0][1]
        bottom[i] = (x, y, 0.0)

    glBegin(GL_TRIANGLES)

    for i in range(NR_DIVS):
        n = (i + 1) % NR_DIVS
        
        glNormal3fv(center)
        glVertex3fv(center)
        
        glNormal3fv(bottom[i])
        glVertex3fv(bottom[i])
        
        glNormal3fv(bottom[n])
        glVertex3fv(bottom[n])

        glNormal3fv(bottom[i])
        glVertex3fv(bottom[i])
        
        glNormal3fv(bottom[n])
        glVertex3fv(bottom[n])
        
        glNormal3fv(top)
        glVertex3fv(top)

    glEnd()

def subAxis(d, s, c = (1.0, 1.0, 1.0, 1.0)):

    glBegin(GL_QUAD_STRIP)

    glMaterial(GL_FRONT, GL_AMBIENT, c)
    glMaterial(GL_FRONT, GL_DIFFUSE, c)
    glMaterial(GL_FRONT, GL_SPECULAR, c)

    for i in range(7):
        t = i * 2 * np.pi / 6
        glNormal3f(np.cos(t), 0.0, np.sin(t))
        glVertex3f(d * np.cos(t), -s, d * np.sin(t))
        glVertex3f(d * np.cos(t),  s, d * np.sin(t))

    glEnd()

    glTranslatef(0.0, s, 0.0)
    glRotatef(-90.0, 1.0, 0.0, 0.0)
    createArrow(3.0 * d, 6.0 * d)

def axis(d, s):

    # Y-axis: Red
    glPushMatrix()
    c = (1.0, 0.0, 0.0, 1.0)
    subAxis(d, s, c)
    glPopMatrix()

    # Z-axis: Green
    glPushMatrix()
    glRotatef(90.0, 1.0, 0.0, 0.0)
    c = (0.0, 1.0, 0.0, 1.0)
    subAxis(d, s, c)
    glPopMatrix()

    # X-axis: Blue
    glPushMatrix()
    glRotatef(-90.0, 0.0, 0.0, 1.0)
    c = (0.3, 0.3, 1.0, 1.0)
    subAxis(d, s, c)
    glPopMatrix()

# OpenGLの初期化関数
def initializeGL():

    global idxModel
    global textureIds, idxCubeFaces
    
    # 背景色の設定 (黒)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    
    light0 = [ 0.0, 10.0, -10.0, 1.0]
    light1 = [ 10.0,  -10.0, -10.0, 1.0]
    light2 = [ -10.0, 10.0, -10.0, 1.0]
    light3 = [ -10.0,  10.0, -10.0, 1.0]
    light4 = [  10.0, -10.0, -10.0, 1.0]

    glLightfv(GL_LIGHT0, GL_POSITION, light0)
    glLightfv(GL_LIGHT1, GL_POSITION, light1)
    glLightfv(GL_LIGHT2, GL_POSITION, light2)
    glLightfv(GL_LIGHT3, GL_POSITION, light3)
    glLightfv(GL_LIGHT4, GL_POSITION, light4)

    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_LIGHT2)
    glEnable(GL_LIGHT3)
    glEnable(GL_LIGHT4)
    glEnable(GL_LIGHTING)

    glEnable(GL_DEPTH_TEST)

    idxModel = glGenLists(1)
    
    glNewList(idxModel, GL_COMPILE)
    
    for i in range(NUM-1):
        glBegin(GL_TRIANGLE_STRIP)
        for j in range(NUM):
            #glNormal3fv(n[i][j])
            glVertex3fv(v[i][j])
            #glNormal3fv(n[i+1][j])
            glVertex3fv(v[i+1][j])

        glEnd()
    
    glEndList()

    # テクスチャの有効化
    glEnable(GL_TEXTURE_2D)

    createPlate(MODEL_SIZE * 3)

    for i in range(3): # x, y, z
   
        # テクスチャの設定
        image = textureImages[i]

        texHeight, texWidth, _ = image.shape
    
        # テクスチャの生成と有効化
        textureIds.append(glGenTextures(1))
        glBindTexture(GL_TEXTURE_2D, textureIds[i])
    
        image_data = np.array(image, dtype=np.uint8)
        gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA8, texWidth, texHeight, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
    
    
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    
        # テクスチャ境界の折り返し設定
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    
        # テクスチャの無効化
        glBindTexture(GL_TEXTURE_2D, 0)
    
        idxCubeFaces.append(glGenLists(1))
    
        glNewList(idxCubeFaces[-1], GL_COMPILE)
        glBindTexture(GL_TEXTURE_2D, textureIds[i])  # テクスチャの有効化
        createFace(i)
        glEndList()

# OpenGLの描画関数
def paintGL():

    global fRedefineSurface, idxModel

    if WIN_WIDTH <= 0 or WIN_HEIGHT <= 0:
        return
    
    d = 0.05
    s = 2.5
 
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # 投影変換行列
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluPerspective(45.0, WIN_WIDTH / WIN_HEIGHT, 1.0, 100.0)
    
    # モデルビュー行列
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    gluLookAt(25.0, 25.0, 50.0,  # 視点
            0.0, 0.0, 0.0,       # 注視方向
            0.0, 1.0, 0.0)       # カメラの上方向

    glBindTexture(GL_TEXTURE_2D, 0)  # テクスチャの無効化
    
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_LIGHT2)
    glEnable(GL_LIGHT3)
    glEnable(GL_LIGHT4)
    glEnable(GL_LIGHTING)

    if flagAmbient:
        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv(GL_LIGHT1, GL_AMBIENT, light_ambient)

    if flagDiffuse:
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        glLightfv(GL_LIGHT1, GL_DIFFUSE, light_diffuse)

    if glagSpecular:
        glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
        glLightfv(GL_LIGHT1, GL_SPECULAR, light_specular)

    glMaterialfv(GL_FRONT, GL_AMBIENT, mat_ambient1)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, mat_diffuse1)
    glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular1)
    glMaterialfv(GL_FRONT, GL_SHININESS, mat_shininess1)

    if flagAxis:

        glPushMatrix()
        glScalef(Scale, Scale, Scale)
        glTranslatef(ModelPos[0], ModelPos[1], 0.0)
        glRotatef(ELEVATION, 1.0, 0.0, 0.0)
        glRotatef(AZIMUTH, 0.0, 1.0, 0.0)
        glRotatef(ROLL, 0.0, 0.0, 1.0)
        axis(d, s)
        glPopMatrix()

    glEnable(GL_BLEND)
    glBlendFunc(GL_ONE, GL_ZERO)
    
    glDepthMask(False)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_LIGHT2)
    glEnable(GL_LIGHT3)
    glEnable(GL_LIGHT4)
    glEnable(GL_LIGHTING)

    if flagAmbient:
        glMaterial(GL_FRONT, GL_AMBIENT, mat_ambient)

    if flagDiffuse:
        glMaterial(GL_FRONT, GL_DIFFUSE, mat_diffuse)

    if glagSpecular:
        glMaterial(GL_FRONT, GL_SPECULAR, mat_specular)

    glMaterialfv(GL_FRONT, GL_SHININESS, mat_shininess)

    glPushMatrix()
    glScalef(Scale, Scale, Scale)
    glTranslatef(ModelPos[0], ModelPos[1], 0.0)
    glRotatef(ELEVATION, 1.0, 0.0, 0.0)
    glRotatef(AZIMUTH, 0.0, 1.0, 0.0)
    glRotatef(ROLL, 0.0, 0.0, 1.0)
    glScalef(1.0, Yscale, 1.0)
    
    if fRedefineSurface:

        defineSurface()
        glDeleteLists(idxModel, 1)
        idxModel = glGenLists(1)
        glNewList(idxModel, GL_COMPILE)
    
        for i in range(NUM-1):
            glBegin(GL_TRIANGLE_STRIP)
            for j in range(NUM):
                #glNormal3fv(n[i][j])
                glVertex3fv(v[i][j])
                #glNormal3fv(n[i+1][j])
                glVertex3fv(v[i+1][j])
            glEnd()
        glEndList()

        fRedefineSurface = False

    else:
    
        glCallList(idxModel)
    
    glPopMatrix()

    # テクスチャの無効化
    glBindTexture(GL_TEXTURE_2D, 0)

    if flagAxis:

        glDisable(GL_LIGHT0)
        glDisable(GL_LIGHT1)
        glDisable(GL_LIGHT2)
        glDisable(GL_LIGHT3)
        glDisable(GL_LIGHT4)
        glDisable(GL_LIGHTING)
        
        glPushMatrix()
        glScalef(Scale, Scale, Scale)
        glRotatef(ELEVATION, 1.0, 0.0, 0.0)
        glRotatef(AZIMUTH, 0.0, 1.0, 0.0)
        glRotatef(ROLL, 0.0, 0.0, 1.0)
        glTranslatef(3.2, 0.0, 0.0)
        glRotatef(ROLL, 0.0, 0.0, -1.0)
        glRotatef(AZIMUTH, 0.0, -1.0, 0.0)
        glRotatef(ELEVATION, -1.0, 0.0, 0.0)
        glTranslatef(ModelPos[0], ModelPos[1], 0)
        #glRotatef(ELEVATION, 1.0, 0.0, 0.0)
        #glRotatef(AZIMUTH, 0.0, 1.0, 0.0)
        #glRotatef(ROLL, 0.0, 0.0, 1.0)
    
        glCallList(idxCubeFaces[0])
    
        glPopMatrix()
    
        glPushMatrix()
        glScalef(Scale, Scale, Scale)
        glRotatef(ELEVATION, 1.0, 0.0, 0.0)
        glRotatef(AZIMUTH, 0.0, 1.0, 0.0)
        glRotatef(ROLL, 0.0, 0.0, 1.0)
        glTranslatef(0.0, 3.2, 0.0)
        glRotatef(ROLL, 0.0, 0.0, -1.0)
        glRotatef(AZIMUTH, 0.0, -1.0, 0.0)
        glRotatef(ELEVATION, -1.0, 0.0, 0.0)
        glTranslatef(ModelPos[0], ModelPos[1], 0)
        #glRotatef(ELEVATION, 1.0, 0.0, 0.0)
        #glRotatef(AZIMUTH, 0.0, 1.0, 0.0)
        #glRotatef(ROLL, 0.0, 0.0, 1.0)
    
        glCallList(idxCubeFaces[1])
    
        glPopMatrix()
    
        glPushMatrix()
        glScalef(Scale, Scale, Scale)
        glRotatef(ELEVATION, 1.0, 0.0, 0.0)
        glRotatef(AZIMUTH, 0.0, 1.0, 0.0)
        glRotatef(ROLL, 0.0, 0.0, 1.0)
        glTranslatef(0.0, 0.0, 3.2)
        glRotatef(ROLL, 0.0, 0.0, -1.0)
        glRotatef(AZIMUTH, 0.0, -1.0, 0.0)
        glRotatef(ELEVATION, -1.0, 0.0, 0.0)
        glTranslatef(ModelPos[0], ModelPos[1], 0.0)
        #glRotatef(ELEVATION, 1.0, 0.0, 0.0)
        #glRotatef(AZIMUTH, 0.0, 1.0, 0.0)
        #glRotatef(ROLL, 0.0, 0.0, 1.0)
    
        glCallList(idxCubeFaces[2])
    
        glPopMatrix()

    glDepthMask(True)
    glDisable(GL_BLEND)

    glFlush()

# ウィンドウサイズ変更のコールバック関数
def resizeGL(window, width, height):
    global WIN_WIDTH, WIN_HEIGHT

    # ユーザ管理のウィンドウサイズを変更
    WIN_WIDTH = width
    WIN_HEIGHT = height

    # GLFW管理のウィンドウサイズを変更
    glfw.set_window_size(window, WIN_WIDTH, WIN_HEIGHT)

    # 実際のウィンドウサイズ (ピクセル数) を取得
    renderBufferWidth, renderBufferHeight = glfw.get_framebuffer_size(window)

    # ビューポート変換の更新
    glViewport(0, 0, renderBufferWidth, renderBufferHeight)

# アニメーションのためのアップデート
def animate():
    global AZIMUTH, ELEVATION

    # 慣性モード中は回転し続ける
    if flagInertia and not isDragging:
        AZIMUTH -= dAZIMUTH
        ELEVATION += dELEVATION

def save_screen():
    global frameNo

    width = WIN_WIDTH
    height = WIN_HEIGHT

    glReadBuffer(GL_FRONT)
    screen_shot = np.zeros((height, width, 3), np.uint8)
    glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE, screen_shot.data)
    screen_shot = cv2.cvtColor(screen_shot, cv2.COLOR_RGB2BGR)
    screen_shot = cv2.flip(screen_shot, 0)
    filename = 'screenshot_%04d.png' % frameNo
    cv2.imwrite(filename, screen_shot)
    print('saved %s' % filename)
    frameNo += 1

# キーボードの押し離しを扱うコールバック関数
def keyboardEvent(window, key, scancode, action, mods):

    global AZIMUTH, ELEVATION, dAZIMUTH, dELEVATION, KeyState
    global idxModel, flagInertia, Xscale, Yscale, Zscale, flagRunning, flagAxis
    global fRedefineSurface

    # 矢印キー操作

    if scancode == SCANCODE_LEFT:
        dAZIMUTH = 0.1
        AZIMUTH += dAZIMUTH * 10

    if scancode == SCANCODE_RIGHT:
        dAZIMUTH = -0.1
        AZIMUTH += dAZIMUTH * 10

    if scancode == SCANCODE_DOWN:
        dELEVATION = 0.1
        ELEVATION += dELEVATION * 10

    if scancode == SCANCODE_UP:
        dELEVATION = -0.1
        ELEVATION += dELEVATION * 10
    
    # sキー押下でスクリーンショット
    if key == KEY_S and action == 1: # press, releaseで2回キャプチャーしないように
        save_screen()

    # ホィールモードの選択

    if key == KEY_R:
        if action == glfw.PRESS:
            KeyState = KEY_STATE_PRESS_R
        elif action == 0:
            KeyState = KEY_STATE_NONE

    # 慣性モードのトグル

    if key == KEY_I and action == 1:
        flagInertia = not flagInertia

    if key == KEY_X and action == 1 and mods & glfw.MOD_SHIFT == 0:
        Xscale *= 0.9
        fRedefineSurface = True

    if key == KEY_X and action == 1 and mods & glfw.MOD_SHIFT == 1:
        Xscale *= 1.1
        fRedefineSurface = True

    if key == KEY_Y and action == 1 and mods & glfw.MOD_SHIFT == 0:
        Yscale *= 0.9

    if key == KEY_Y and action == 1 and mods & glfw.MOD_SHIFT == 1:
        Yscale *= 1.1

    if key == KEY_Z and action == 1 and mods & glfw.MOD_SHIFT == 0:
        Zscale *= 0.9
        fRedefineSurface = True

    if key == KEY_Z and action == 1 and mods & glfw.MOD_SHIFT == 1:
        Zscale *= 1.1
        fRedefineSurface = True

    if key == KEY_MINUS and action == 1:
        Yscale *= -1

    if scancode == SCANCODE_ESC:
        flagRunning = False

    if key == KEY_A and action == 1:
        flagAxis = not flagAxis

# マウスのクリックを処理するコールバック関数
def mouseEvent(window, button, action, mods):
    global isDragging, newPos, oldPos, Mode, flagInertia

    # クリックしたボタンで処理を切り替える
    if button == glfw.MOUSE_BUTTON_LEFT:
        Mode = MODE_ROTATE
    
    elif button == glfw.MOUSE_BUTTON_MIDDLE:
        if action == 1:
            flagInertia = not flagInertia

    elif button == glfw.MOUSE_BUTTON_RIGHT:
        Mode = MODE_TRANSLATE

    # クリックされた位置を取得
    px, py = glfw.get_cursor_pos(window)

    # マウスドラッグの状態を更新
    if action == glfw.PRESS:
        if not isDragging:
            isDragging = True
            oldPos = [px, py]
            newPos = [px, py]
    else:
        isDragging = False
        oldPos = [0, 0]
        newPos = [0, 0]

# マウスの動きを処理するコールバック関数
def motionEvent(window, xpos, ypos):
    global isDragging, newPos, oldPos, AZIMUTH, dAZIMUTH, ELEVATION, dELEVATION, ModelPos

    if isDragging:
        # マウスの現在位置を更新
        newPos = [xpos, ypos]

        dx = newPos[0] - oldPos[0]
        dy = newPos[1] - oldPos[1]
        
        # マウスがあまり動いていない時は処理をしない
        #length = dx * dx + dy * dy
        #if length < 2.0 * 2.0:
        #    return
        #else:
        if Mode == MODE_ROTATE:
            dAZIMUTH = (xpos - oldPos[0]) / ROTATE_SCALE
            dELEVATION = (ypos - oldPos[1]) / ROTATE_SCALE
            AZIMUTH -= dAZIMUTH
            ELEVATION += dELEVATION
        elif Mode == MODE_TRANSLATE:
            ModelPos[0] += (xpos - oldPos[0]) / TRANSLATE_SCALE
            ModelPos[1] -= (ypos - oldPos[1]) / TRANSLATE_SCALE

        oldPos = [xpos, ypos]

# マウスホイールを処理するコールバック関数
def wheelEvent(window, xoffset, yoffset):
    global Scale, idxModel, ROLL

    if KeyState == KEY_STATE_NONE:
        Scale += yoffset / 10.0

    elif KeyState == KEY_STATE_PRESS_R:
        ROLL += yoffset

def main():

    global expression

    argv = sys.argv
    argc = len(argv)

    print('[uasge] python %s                      : \"equation.txt\" is used' % argv[0])
    print('[usage] python %s <equation text file>' % argv[0])

    if argc > 1:

        with open(argv[1], 'r', encoding='utf-8') as f:
            expression = f.read().strip()
    else:

        with open(FILE_EQUATION, 'r', encoding='utf-8') as f:
            expression = f.read().strip()

    print('equation:')
    print(expression)

    defineSurface()

    # 座標軸ラベル用画像をロード 
    path_x = os.path.join(os.path.dirname(__file__), filename_x)
    texture = cv2.imread(path_x, cv2.IMREAD_UNCHANGED)
    texture = cv2.cvtColor(texture, cv2.COLOR_BGRA2RGBA)
    textureImages.append(texture)

    path_y = os.path.join(os.path.dirname(__file__), filename_y)
    texture = cv2.imread(path_y, cv2.IMREAD_UNCHANGED)
    texture = cv2.cvtColor(texture, cv2.COLOR_BGRA2RGBA)
    textureImages.append(texture)

    path_z = os.path.join(os.path.dirname(__file__), filename_z)
    texture = cv2.imread(path_z, cv2.IMREAD_UNCHANGED)
    texture = cv2.cvtColor(texture, cv2.COLOR_BGRA2RGBA)
    textureImages.append(texture)
    
    # OpenGLを初期化する
    if glfw.init() == glfw.FALSE:
        raise Exception("Failed to initialize OpenGL")

    # Windowの作成
    window = glfw.create_window(WIN_WIDTH, WIN_HEIGHT, WIN_TITLE, None, None)
    if window is None:
        glfw.terminate()
        raise Exception("Failed to create Window")

    # OpenGLの描画対象にWindowを追加
    glfw.make_context_current(window)

    # ウィンドウのリサイズを扱う関数の登録
    glfw.set_window_size_callback(window, resizeGL)

    # キーボードのイベントを処理する関数を登録
    glfw.set_key_callback(window, keyboardEvent)

    # マウスのイベントを処理する関数を登録
    glfw.set_mouse_button_callback(window, mouseEvent)

    # マウスの動きを処理する関数を登録
    glfw.set_cursor_pos_callback(window, motionEvent)

    # マウスホイールを処理する関数を登録
    glfw.set_scroll_callback(window, wheelEvent)
    
    # ユーザ指定の初期化
    initializeGL()

    # メインループ
    while glfw.window_should_close(window) == glfw.FALSE and flagRunning:

        # 描画
        paintGL()

        # アニメーション
        animate()

        # 描画用バッファの切り替え
        glfw.swap_buffers(window)
        glfw.poll_events()

    # 後処理
    glfw.destroy_window(window)
    glfw.terminate()

if __name__ == "__main__":
    main()
