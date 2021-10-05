import glfw
from OpenGL.GL import *
import ShaderLoader
import numpy as np
import pyrr
from PIL import Image
from ObjLoader import *

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

    # Load the obj file in the application
    obj = ObjLoader()
    obj.load_model("./models/mickeymouse.obj")

    # vertices_size_bytes = len(obj.vertex_index) * 3 * 4 # Num vertices * each vertex has 3 float values * each float is 4 bytes
    vertices_size_bytes = obj.model.itemsize * len(obj.model)  # Num vertices * each vertex has 3 float values * each float is 4 bytes
    print(" Total vertices size in bytes is: ",  vertices_size_bytes, "bytes")

    # Set the params for vertex attributes for the vertex shader
    stride_position = 3 * obj.model.itemsize
    offset_position = 0
    stride_tex      = 2 * obj.model.itemsize
    offset_tex      = len(obj.vertex_index)*12

    print("stride_position: ", stride_position)
    print("offset_position: ", offset_position)
    print("stride_tex: ", stride_tex)
    print("offset_tex: ", offset_tex)

    # Create the vertex_shader
    shader = ShaderLoader.compile_shader("shaders/vertex_shader_objFile.vs",
                                         "shaders/fragment_shader_objFile.fs")

    # Send all vertex data to the graphics processor memory using Vertex Buffer Object VBO
    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER,VBO)
    #Upload the actual data
    # www.open.gl/drawing
    glBufferData(GL_ARRAY_BUFFER,vertices_size_bytes, obj.model, GL_STATIC_DRAW)

    # position
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride_position, ctypes.c_void_p(offset_position))
    glEnableVertexAttribArray(0)
    # texture_coords
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride_tex, ctypes.c_void_p(offset_tex))
    glEnableVertexAttribArray(1)

    # Create texture binding
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    # texture wrapping params
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    # texture filtering parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)


    # Load image
    im_type = "jpg" # "png" or "jpg"

    if im_type == "jpg":
        image = Image.open("./res/opengl_test.jpg")
        # image = Image.open("./res/butterfly/MONARCH."jpg)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        width, height = image.size
        print("Loaded Image size: ", image.size)
        img_data = np.array(list(image.getdata()), np.uint8)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB,
                     width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
        glEnable(GL_TEXTURE_2D)

    elif im_type == "png":
        image = Image.open("./res/opengl_test.png")
        # This causes flipped image for png
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        width, height = image.size
        print("Loaded Image size: ", image.size)

        img_data = image.convert("RGBA").tobytes()
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                     width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glEnable(GL_TEXTURE_2D)

    # print(type(image))#.shape, image.width, image.height)


    glUseProgram(shader)

    # Create color for window
    glClearColor(0.2,0.3,0.1,1.0)
    glEnable(GL_DEPTH_TEST)

    # Define viewMatrix
    view = pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, -3.0]))
    projection = pyrr.matrix44.create_perspective_projection_matrix(100, w_width/w_height, 0.1, 600.0)

    # Set position of cube/ model
    model =pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, -290.0 ]))

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
        rot_mat = pyrr.matrix44.create_from_axis_rotation([0.,1.,0.], 0.2 * glfw.get_time())

        # Update the transform variable in the vertex shader
        transformLoc = glGetUniformLocation(shader,"transform")
        glUniformMatrix4fv(transformLoc,1, GL_FALSE, rot_mat)

        glDrawArrays(GL_TRIANGLES, 0, len(obj.vertex_index))

        glfw.swap_buffers(window)

    # Terminate glfw
    glfw.terminate()

if __name__ == "__main__":
    main()