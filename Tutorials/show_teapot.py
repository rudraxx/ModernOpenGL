from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import time


def init():
    # glClearColor(0.0, 0.0, 0.0, 0.0)
    # glClearDepth(1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.,1.,0.1,100.)
    #commented gluOrtho2D out since its inclusion would require different vertex coordinates (i.e. not between -1 and 1)
    #gluOrtho2D(0.0, 640.0, 0.0, 480.0)

    """ Draw a red teapot at the origin. """
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    # glEnable(GL_DEPTH_TEST)
    glClear(GL_DEPTH_BUFFER_BIT)

    # # draw red teapot
    glMaterialfv(GL_FRONT,GL_AMBIENT,[0,0,0,0])
    glMaterialfv(GL_FRONT,GL_DIFFUSE,[0.5,0.0,0.0,0.0])
    glMaterialfv(GL_FRONT,GL_SPECULAR,[0.7,0.6,0.6,0.0])
    glMaterialf(GL_FRONT,GL_SHININESS,0.25*128.0)


obj_rot = 0.0
world_rot = 0.0
obj_rot_speed = 0.0
world_rot_speed = -1.0

def display():
    global obj_rot
    global world_rot
    global obj_rot_speed
    global world_rot_speed

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()#not needed here, but good practice to reset state!
    gluLookAt(0,0,0,
              0,0,0,
              0,1,0)

    glClearColor(0.,0.,1.,1.)
    # glRotate(world_rot, 0.0, 0.0, 1.0)#this transformation is peformed last (STEP 5)
    # glTranslatef(0.3, 0.3, 0.0)#OPTIONAL (GLOBAL) TRANSLATION OF THE TRIANGLE
    # glTranslatef(0.17, 0.17, 0.0)
    glRotate(obj_rot, 0.0, 1.0, 0.0)
    glTranslatef(0,0, 2)#this transformation is performed first (STEP 1)


    glutSolidTeapot(0.6)
    glutSwapBuffers()

    # glBegin(GL_TRIANGLES)
    # glColor3f(0.5, 0.5, 0.9)
    # glVertex3f(0.5, 0.0, 0.0)
    # glVertex3f(0.0, 0.5, 0.0)
    # glVertex3f(0.0, 0.0, 0.0)
    # glEnd()

    obj_rot += obj_rot_speed
    world_rot += world_rot_speed
    obj_rot %= 360#simpler approach than if statement, which did not address negative rotation
    world_rot %= 360

    glFlush()
    time.sleep(1/60.0)#VERY simplistically run the app at ~60 fps, avoids high CPU usage!

if __name__ == '__main__':
    glutInit()
    glutCreateWindow('Rotating triangles')
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
    glutInitWindowSize(1280, 960)
    glutDisplayFunc(display)
    glutIdleFunc(display)
    init()
    glutMainLoop()