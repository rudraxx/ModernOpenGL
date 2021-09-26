import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np

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

    # Create vertices
    triangle = np.array([-0.5, -0.5, 0.0,
                0.5,-0.5,0.0,
                0, 0.5, 0], dtype= np.float32)

    # Create the vertex_shader
    # Input position is in homogeneous world coordinates xyzw
    # Output of the vertex shader is in device coordinates
    # ie display screen coordinates
    vertex_shader_code = """
    #version 330
    in vec3 position;
    void main()
    {
        gl_Position = vec4(position, 1.0);
    }
    """
    fragment_shader_code = """
    #version 330
    void main()
    {
        gl_FragColor = vec4(1.0f, 0.0f, 0.0f,1.0f);
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
    glBufferData(GL_ARRAY_BUFFER,9*4,triangle,GL_STATIC_DRAW)

    position = glGetAttribLocation(shader,"position")
    glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 0, None)

    glEnableVertexAttribArray(position)

    glUseProgram(shader)

    # Create color for window
    glClearColor(0.2,0.3,0.1,1.0)

    while not glfw.window_should_close(window):
        glfw.poll_events()

        # Clear the color buffer value
        glClear(GL_COLOR_BUFFER_BIT)

        glDrawArrays(GL_TRIANGLES, 0,3)


        glfw.swap_buffers(window)

    # Terminate glfw
    glfw.terminate()

if __name__ == "__main__":
    main()