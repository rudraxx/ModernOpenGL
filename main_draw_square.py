# Help for installation
#https://stackoverflow.com/questions/65699670/pyopengl-opengl-error-nullfunctionerror-attempt-to-call-an-undefined-functio

# import OpenGL
# import OpenGL.GL
# import OpenGL.GLUT
# import OpenGL.GLU
# print("Imports successful")

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *



w,h = 700,500

def square():
    '''
    Declare points in the given sequence: bottom left, bottom right, top right, top left
    '''

    glBegin(GL_QUADS) # Begin the sketch
    glVertex2f(100,100) # Coordinates of bottom left
    glVertex2f(200,100) # Coordinates of bottom right
    glVertex2f(200,200) # Coordinates of top right
    glVertex2f(100,200) # Coordinates of top left
    glEnd()  # Mark the end of drawing

def iterate():
    glViewport(0,0,500,500)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 500, 0.0, 500, 0.0,1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # Remove everything fro screen and show white screen
    glLoadIdentity() # Reset all graphic/shape's position
    iterate()
    glColor3f(1.0,0.0,3.0) # Set color to pink
    square() # Draw the square using our function
    glutSwapBuffers()


glutInit() # initialize a glut instance which will allow us to customize our window
glutInitDisplayMode(GLUT_RGBA) # Set the display mode to be colored
glutInitWindowSize(w,h)    # Set the width and height of your window
glutInitWindowPosition(0,0)    # Set the position at which this windo should open
wind = glutCreateWindow("OpenGL Code Practice")     # Give the window a title
glutDisplayFunc(showScreen)     # Tell OpenGL to call the showScreen method continuously
glutIdleFunc(showScreen)        # Draw any graphics or shapes in the ShowScreen function at all times
glutMainLoop()                  # Keeps te window created above displaying/running in a loop
