import ctypes

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import pyrr

def main():

    #Initialize glfw
    if not glfw.init():
        return

    window  = glfw.create_window(800,600,"My OpenGL Window",None, None)

    if not window:
        glfw.terminate()
        return

    #Needs context
    glfw.make_context_current(window)

    # Create vertices for cube
    #                   [positions          colors
    cube =   np.array([  -0.5, -0.5, 0.5,   1.0, 0.0, 0.0,
                          0.5, -0.5, 0.5,   0.0, 1.0, 0.0,
                          0.5,  0.5, 0.5,   0.0, 0.0, 1.0,
                         -0.5,  0.5, 0.5,   1.0, 1.0, 1.0,

                         -0.5, -0.5, -0.5,   1.0, 0.0, 0.0,
                          0.5, -0.5, -0.5,   0.0, 1.0, 0.0,
                          0.5,  0.5, -0.5,   0.0, 0.0, 1.0,
                         -0.5,  0.5, -0.5,   1.0, 1.0, 1.0
                         ], dtype= np.float32)

    print("Cube size in bytes is: ",  cube.size * cube.itemsize, "bytes")

    # Set the indices of the vertices
    indices = np.array([0, 1, 2, 2, 3, 0,
                        4, 5, 6, 6, 7, 4,
                        4, 5, 1, 1, 0, 4,
                        6, 7, 3, 3, 2, 6,
                        5, 6, 2, 2, 1, 5,
                        7, 4, 0, 0, 3, 7
                        ],
                       dtype=np.uint32)

    print("Indices size in bytes is: ",  indices.size * indices.itemsize, "bytes")

    numTrianglesToDraw  = indices.size
    print("numTrianglesToDraw: ", numTrianglesToDraw, "triangles")

    # Create the vertex_shader
    # Input position is in homogeneous world coordinates xyzw
    # Output of the vertex shader is in device coordinates
    # ie display screen coordinates
    vertex_shader_code = """
    #version 330
    in vec3 position;
    in vec3 color;
    uniform mat4 transform;
    out vec3 newColor;
    void main()
    {
        gl_Position = transform * vec4(position,1.0f);
        newColor   = color;
    }
    """
    fragment_shader_code = """
    #version 330
    in vec3 newColor;
    out vec4 outColor;
    
    void main()
    {
        outColor = vec4(newColor,1.0f);
        
    }
    """

    shader  = OpenGL.GL.shaders.compileProgram(OpenGL.GL.shaders.compileShader(vertex_shader_code,GL_VERTEX_SHADER),
                                               OpenGL.GL.shaders.compileShader(fragment_shader_code,GL_FRAGMENT_SHADER))

    # # Check if the shader compiled properly. glGetError wont report
    # # and error in this compilation
    # strInfoLog = glGetShaderInfoLog(shader)
    # print("shader strInfoLog:\n" + strInfoLog)
    #
    # # status = glGetShaderiv(shader, GL_COMPILE_STATUS)
    # # print(status)
    #
    # Send all vertex data to the graphics processor memory using Vertex Buffer Object VBO
    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER,VBO)
    #Upload the actual data
    # www.open.gl/drawing
    glBufferData(GL_ARRAY_BUFFER,cube.size * cube.itemsize,cube,GL_STATIC_DRAW)

    # Create an Element Buffer Object for the indices
    EBO = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.size*indices.itemsize, indices, GL_STATIC_DRAW)


    position = glGetAttribLocation(shader,"position")
    glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
    glEnableVertexAttribArray(position)

    color = glGetAttribLocation(shader,"color")
    glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
    glEnableVertexAttribArray(color)

    glUseProgram(shader)

    # Create color for window
    glClearColor(0.2,0.3,0.1,1.0)

    # Enable the depth test
    glEnable(GL_DEPTH_TEST)

    # Show as wireframe
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    while not glfw.window_should_close(window):
        glfw.poll_events()

        # Clear the color buffer value
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Generate the transform
        rot_mat = pyrr.matrix44.create_from_axis_rotation([1.,1.,1.], 0.8 * glfw.get_time())
        # rot_y = pyrr.matrix44.create_from_y_rotation(0.8 * glfw.get_time())

        # print("rot_mat is: \n", glfw.get_time())

        transformLoc = glGetUniformLocation(shader,"transform")
        glUniformMatrix4fv(transformLoc,1, GL_FALSE, rot_mat)


        glDrawElements(GL_TRIANGLES, numTrianglesToDraw, GL_UNSIGNED_INT, None)


        glfw.swap_buffers(window)

    # Terminate glfw
    glfw.terminate()

if __name__ == "__main__":
    main()