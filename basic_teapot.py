
'''
Welcome to OpenGL Programming Examples!
How to make an OpenGL/Glut Teapot in Python
OpenGL (Open Graphics Library)[2] is a cross-language, multi-platform application programming interface (API) for rendering 2D and 3D computer graphics.
The API is typically used to interact with a Graphics processing unit (GPU), to achieve hardware-accelerated rendering. OpenGL was developed by Silicon Graphics Inc. (SGI) from 1991 and released in January 1992[3] and is widely used in CAD, virtual reality, scientific visualization, information visualization, flight simulation, and video games.
OpenGL is managed by the non-profit technology consortium Khronos Group.

The OpenGL Utility Toolkit (GLUT) is a library of utilities for OpenGL programs, which primarily perform system-level I/O with the host operating system. Functions performed include window definition, window control, and monitoring of keyboard and mouse input. Routines for drawing a number of geometric primitives (both in solid and wireframe mode) are also provided, including cubes, spheres and the Utah teapot. GLUT also has some limited support for creating pop-up menus.

In this tutorial we will set up an OpenGL/GLUT teapot.


Installation

We assume you use (Ubuntu) Linux and already have Python installed. If not type
sudo apt-get install python*


Install PyOpenGL using the command:
sudo easy_install PyOpenGL


The Code
We assume you have previous programming experience; Simply copy the code displayed below into a text editor.
Save the file as example.py


'''
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys

name = 'OpenGL Python Teapot'

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(400,400)
    glutCreateWindow(name)

    glClearColor(0.,0.,1.,1.)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_CULL_FACE)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    lightZeroPosition = [-20.,2.,-2.,1.]
    lightZeroColor = [1.8,1.0,0.8,1.0] #green tinged
    glLightfv(GL_LIGHT0, GL_POSITION, lightZeroPosition)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightZeroColor)
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.1)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
    glEnable(GL_LIGHT0)

    glutDisplayFunc(display)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(40.,1.,1.,40.)
    glMatrixMode(GL_MODELVIEW)
    gluLookAt(0,0,10,
              0,0,0,
              0,1,0)
    glPushMatrix()
    glutMainLoop()
    return

def display():

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    # glPushMatrix()
    color = [1.0,0.,0.,1.]
    glMaterialfv(GL_FRONT,GL_DIFFUSE,color)
    glRotatef(2, 1, 0 ,0)
    # glRotatef(180,1,0,0);
    # glRotatef(-45,0,1,0);
    glutSolidTeapot(1.2)

    # glPopMatrix()
    glutSwapBuffers()

    return

if __name__ == '__main__': main()
