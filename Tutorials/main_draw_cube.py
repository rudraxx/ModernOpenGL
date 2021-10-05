# Help for installation
#https://stackoverflow.com/questions/65699670/pyopengl-opengl-error-nullfunctionerror-attempt-to-call-an-undefined-functio

# Tutorial
# https://www.stechies.com/opengl-python/
# https://www.oreilly.com/library/view/programming-computer-vision/9781449341916/ch04.html#ch04equ02

import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
import pygame

from pygame.locals import *

verti = (
    (1,-1,-1),
    (1,1,-1),
    (-1,1,-1),
    (-1,-1,-1),
    (1,-1,1),
    (1,1,1),
    (-1,-1,1),
    (-1,1,1)
)

edgez = (
    (0,1),
    (0,3),
    (0,4),
    (2,1),
    (2,3),
    (2,7),
    (6,3),
    (6,4),
    (6,7),
    (5,1),
    (5,4),
    (5,7)
)

def Cube():
    glBegin(GL_LINES)
    for edge in edgez:
        for vertex in edge:
            glVertex3fv(verti[vertex])
    glEnd()

def main():
    pygame.init()
    display = (900,700)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(35, display[0]/display[1], 0.1, 50.0)
    glTranslatef(0.0, 0.0, -25)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        glRotatef(3,1,1,1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        Cube()
        pygame.display.flip()
        pygame.time.wait(15)

main()
