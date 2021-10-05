import ctypes

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
from PIL import Image

def main():

    #Initialize glfw
    if not glfw.init():
        return

    window  = glfw.create_window(1600,1200,"My OpenGL Window",None, None)

    if not window:
        glfw.terminate()
        return

    #Needs context
    glfw.make_context_current(window)

    # Create vertices
    #                   [positions          colors         texture coordinates
    quad =   np.array([  -0.5, -0.5, 0.0,   1.0, 0.0, 0.0,  0.0, 0.0,
                          0.5, -0.5, 0.0,   0.0, 1.0, 0.0,  1.0, 0.0,
                          0.5,  0.5, 0.0,   0.0, 0.0, 1.0,  1.0, 1.0,
                         -0.5,  0.5, 0.0,   1.0, 1.0, 1.0,  0.0, 1.0
                         ], dtype= np.float32)

    print("Quad size in bytes is: ",  quad.size * quad.itemsize, "bytes")

    # Set the indices of the vertices
    indices = np.array([0, 1, 2,
                        2, 3, 0],
                       dtype=np.uint32)

    print("Indices size in bytes is: ",  indices.size * indices.itemsize, "bytes")

    # Set the params for vertex attributes for the vertex shader
    stride_position = 8 * quad.itemsize
    offset_position = 0
    stride_color    = 8 * quad.itemsize
    offset_color    = 3 * quad.itemsize
    stride_tex      = 8 * quad.itemsize
    offset_tex      = 6 * quad.itemsize

    print("stride_position: ", stride_position)
    print("offset_position: ", offset_position)
    print("stride_color: ", stride_color)
    print("offset_color: ", offset_color)
    print("stride_tex: ", stride_tex)
    print("offset_tex: ", offset_tex)


    # Create the vertex_shader
    # Input position is in homogeneous world coordinates xyzw
    # Output of the vertex shader is in device coordinates
    # ie display screen coordinates
    vertex_shader_code = """
    #version 330
    in layout(location = 0) vec3 position;
    in layout(location = 1) vec3 color;
    in layout(location = 2) vec2 inTexCoords;

    out vec3 newColor;
    out vec2 outTexCoords;
    
    void main()
    {
        gl_Position = vec4(position,1.0f);
        newColor   = color;
        outTexCoords = inTexCoords;
    }
    """
    fragment_shader_code = """
    #version 330
    in vec3 newColor;
    in vec2 outTexCoords;
    
    out vec4 outColor;
    uniform sampler2D samplerTex;
    void main()
    {
        //outColor = texture(samplerTex,outTexCoords) * vec4(newColor, 1.0f);
        outColor = texture(samplerTex,outTexCoords);
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
    glBufferData(GL_ARRAY_BUFFER,quad.size * quad.itemsize,quad,GL_STATIC_DRAW)

    # Create an Element Buffer Object for the indices
    EBO = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.size*indices.itemsize, indices, GL_STATIC_DRAW)

    # Create texture binding
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    # texture wrapping params
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    # texture filtering parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # position = glGetAttribLocation(shader,"position")
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride_position, ctypes.c_void_p(offset_position))
    glEnableVertexAttribArray(0)

    # color = glGetAttribLocation(shader,"color")
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride_color, ctypes.c_void_p(offset_color))
    glEnableVertexAttribArray(1)

    # texture_coords = glGetAttribLocation(shader,"inTexCoords")
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride_tex, ctypes.c_void_p(offset_tex))
    glEnableVertexAttribArray(2)

    # Load image
    im_type = "jpg" # "png" or "jpg"

    if im_type == "jpg":
        image = Image.open("./res/crate.jpg")
        width, height = image.size
        print("Loaded Image size: ", image.size)
        img_data = np.array(list(image.getdata()), np.uint8)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB,
                     width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)

    elif im_type == "png":
        image = Image.open("./res/opengl_test.png")
        # This causes flipped image for png
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        width, height = image.size
        print("Loaded Image size: ", image.size)

        img_data = image.convert("RGBA").tobytes()
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                     width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

    # print(type(image))#.shape, image.width, image.height)


    glUseProgram(shader)

    # Create color for window
    glClearColor(0.2,0.3,0.1,1.0)

    while not glfw.window_should_close(window):
        glfw.poll_events()

        # Clear the color buffer value
        glClear(GL_COLOR_BUFFER_BIT)

        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)


        glfw.swap_buffers(window)

    # Terminate glfw
    glfw.terminate()

if __name__ == "__main__":
    main()