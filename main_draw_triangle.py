# Help for installation
#https://stackoverflow.com/questions/65699670/pyopengl-opengl-error-nullfunctionerror-attempt-to-call-an-undefined-functio

# Tutorial
# https://www.stechies.com/opengl-python/
# https://www.oreilly.com/library/view/programming-computer-vision/9781449341916/ch04.html#ch04equ02

import numpy as np
from OpenGL.GL import *
import glfw

print("Imports successful")

# Set width and height of the window
w,h = 700,500


glfw.init()

# Create window
window = glfw.create_window(w,h,"PyOpenGL Triangle", None,None)
glfw.set_window_pos(window,500,300)
glfw.make_context_current(window)

# Set the vertices of the triangle
vertices = [-0.5, -0.5, 0.0,
            0.5, -0.5, 0.0,
            0.0, 0.5, 0.0]

# List color codes
colors = [0.5,0.5, 0,
          0.2, 0.3, 0.3,
          0, 0.8, 0.9,
          0, 0.2, 1.0]

v = np.array(vertices,dtype = np.float32)
c = np.array(colors,dtype = np.float32)

# This will draw the colorless triangle
glEnableClientState(GL_VERTEX_ARRAY)
glVertexPointer(3,GL_FLOAT,0,v)
glEnableClientState(GL_COLOR_ARRAY)
glColorPointer(4,GL_FLOAT,0,c)
# This will set color of the background
glClearColor(0.6,0.8,0.2,0.2)

while not glfw.window_should_close(window):
    # Will iterate through all functions below
    glfw.poll_events()
    glClear(GL_COLOR_BUFFER_BIT)
    # Create rotation animated motion
    glRotatef(0.1,0,1,0)
    glDrawArrays(GL_TRIANGLES,0,3)
    glfw.swap_buffers(window)

glfw.terminate()