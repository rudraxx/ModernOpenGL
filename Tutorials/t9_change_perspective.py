import ctypes

import glfw
from OpenGL.GL import *
import ShaderLoader
import numpy as np
from PIL import Image
import pyrr

# Create callback for changing the size of window
def fcn_window_resize(window, width, height):
    glViewport(0, 0, width, height)

def main():

    #Initialize glfw
    if not glfw.init():
        return

    w_width, w_height = 800, 600

    # # Set if you want the window size to stay fixed
    # glfw.window_hint(glfw.RESIZABLE, GL_FALSE)
    window  = glfw.create_window(w_width, w_height, "My OpenGL Window", None, None)

    if not window:
        glfw.terminate()
        return

    #Needs context
    glfw.make_context_current(window)
    glfw.set_window_size_callback(window,fcn_window_resize)

    # Create vertices for cube
    #         positions          colors         texture coordinates
    mShape = [-0.5, -0.5,  0.5,  1.0, 0.0, 0.0,  0.0, 0.0,
              0.5, -0.5,  0.5,  0.0, 1.0, 0.0,  1.0, 0.0,
              0.5,  0.5,  0.5,  0.0, 0.0, 1.0,  1.0, 1.0,
              -0.5,  0.5,  0.5,  1.0, 1.0, 1.0,  0.0, 1.0,

              -0.5, -0.5, -0.5,  1.0, 0.0, 0.0,  0.0, 0.0,
              0.5, -0.5, -0.5,  0.0, 1.0, 0.0,  1.0, 0.0,
              0.5,  0.5, -0.5,  0.0, 0.0, 1.0,  1.0, 1.0,
              -0.5,  0.5, -0.5,  1.0, 1.0, 1.0,  0.0, 1.0,

              0.5, -0.5, -0.5,  1.0, 0.0, 0.0,  0.0, 0.0,
              0.5,  0.5, -0.5,  0.0, 1.0, 0.0,  1.0, 0.0,
              0.5,  0.5,  0.5,  0.0, 0.0, 1.0,  1.0, 1.0,
              0.5, -0.5,  0.5,  1.0, 1.0, 1.0,  0.0, 1.0,

              -0.5,  0.5, -0.5,  1.0, 0.0, 0.0,  0.0, 0.0,
              -0.5, -0.5, -0.5,  0.0, 1.0, 0.0,  1.0, 0.0,
              -0.5, -0.5,  0.5,  0.0, 0.0, 1.0,  1.0, 1.0,
              -0.5,  0.5,  0.5,  1.0, 1.0, 1.0,  0.0, 1.0,

              -0.5, -0.5, -0.5,  1.0, 0.0, 0.0,  0.0, 0.0,
              0.5, -0.5, -0.5,  0.0, 1.0, 0.0,  1.0, 0.0,
              0.5, -0.5,  0.5,  0.0, 0.0, 1.0,  1.0, 1.0,
              -0.5, -0.5,  0.5,  1.0, 1.0, 1.0,  0.0, 1.0,

              0.5,  0.5, -0.5,  1.0, 0.0, 0.0,  0.0, 0.0,
              -0.5,  0.5, -0.5,  0.0, 1.0, 0.0,  1.0, 0.0,
              -0.5,  0.5,  0.5,  0.0, 0.0, 1.0,  1.0, 1.0,
              0.5,  0.5,  0.5,  1.0, 1.0, 1.0,  0.0, 1.0]

    mShape = np.array(mShape, dtype = np.float32)

    vertices_size_bytes = mShape.size * mShape.itemsize
    print(" Total vertices size in bytes is: ",  vertices_size_bytes, "bytes")


    indices = [ 0,  1,  2,  2,  3,  0,
                4,  5,  6,  6,  7,  4,
                8,  9, 10, 10, 11,  8,
                12, 13, 14, 14, 15, 12,
                16, 17, 18, 18, 19, 16,
                20, 21, 22, 22, 23, 20]

    indices = np.array(indices, dtype= np.uint32)

    indices_size_bytes = indices.size * indices.itemsize
    print("Indices size in bytes is: ", indices_size_bytes , "bytes")

    numElementsToDraw  = indices.size
    print("numElementsToDraw: ", numElementsToDraw, "elements")

    # Set the params for vertex attributes for the vertex shader
    stride_position = 8 * mShape.itemsize
    offset_position = 0
    stride_color    = 8 * mShape.itemsize
    offset_color    = 3 * mShape.itemsize
    stride_tex      = 8 * mShape.itemsize
    offset_tex      = 6 * mShape.itemsize

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

    shader = ShaderLoader.compile_shader("shaders/vertex_shader.vs",
                                         "shaders/fragment_shader.fs")

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
    glBufferData(GL_ARRAY_BUFFER,vertices_size_bytes,mShape,GL_STATIC_DRAW)

    # Create an Element Buffer Object for the indices
    EBO = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices_size_bytes, indices, GL_STATIC_DRAW)

    # Create texture binding
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    # texture wrapping params
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    # texture filtering parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # position
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride_position, ctypes.c_void_p(offset_position))
    glEnableVertexAttribArray(0)

    # color
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride_color, ctypes.c_void_p(offset_color))
    glEnableVertexAttribArray(1)

    # texture_coords
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
    glEnable(GL_DEPTH_TEST)

    # Define viewMatrix
    view = pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, -3.0]))
    projection = pyrr.matrix44.create_perspective_projection_matrix(45, w_width/w_height, 0.1, 100.0)

    # Set position of cube/ model
    model =pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, 0.0 ]))

    # Get the orientation data from the shader
    view_loc        = glGetUniformLocation(shader, "view")
    proj_loc  = glGetUniformLocation(shader, "projection")
    model_loc  = glGetUniformLocation(shader, "model")

    # Set the values
    glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
    glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)


    while not glfw.window_should_close(window):
        glfw.poll_events()

        # Clear the color buffer value
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Generate the transform
        rot_mat = pyrr.matrix44.create_from_axis_rotation([1.,1.,1.], 0.8 * glfw.get_time())

        # Update the transform variable in the vertex shader
        transformLoc = glGetUniformLocation(shader,"transform")
        glUniformMatrix4fv(transformLoc,1, GL_FALSE, rot_mat)

        glDrawElements(GL_TRIANGLES, numElementsToDraw, GL_UNSIGNED_INT, None)


        glfw.swap_buffers(window)

    # Terminate glfw
    glfw.terminate()

if __name__ == "__main__":
    main()