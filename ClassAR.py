import glfw
from OpenGL.GL import *
import ShaderLoader
import numpy as np
import pyrr
from PIL import Image
from ObjLoader import *
import cv2 as cv


class ClassAR():

    window_name = None
    w_height = None
    w_width = None
    window = None
    shader = None
    model_obj = None
    VAO_1 = None
    VAO_2 = None

    def __init__(self, window_name, w_width=800, w_height=600):
        self.window_name = window_name
        self.w_width  = w_width
        self.w_height = w_height



    def initialize_gl(self):

        init_complete = False
        if not glfw.init():
            return init_complete

        self.window  = glfw.create_window(self.w_width, self.w_height,
                                     self.window_name, None, None)

        # Set glfw context to window
        glfw.make_context_current(self.window)
        glfw.set_window_size_callback(self.window,self.fcn_window_resize )

        # Create the vertex_shader
        self.shader = ShaderLoader.compile_shader("shaders/vertex_shader_mvp_matrix.vs",
                                             "shaders/fragment_shader_mvp_matrix.fs")
        # self.shader = ShaderLoader.compile_shader("shaders/vertex_shader_tex_quad.vs",
        #                                      "shaders/fragment_shader_tex_quad.fs")

        init_complete = True

        # Init the camera feed
        self.cap = cv.VideoCapture(0)

        return init_complete

    # Create callback for changing the size of window
    def fcn_window_resize(self, window, new_width, new_height):
        glViewport(0, 0,  new_width, new_height)

    def create_background_quad(self):
        # Create vertices
        val  = 5
        #                   [positions        texture coordinates]
        quad =   np.array([  -val, -val, 0.0,  0.0, 0.0,
                              val, -val, 0.0,  1.0, 0.0,
                              val,  val, 0.0,  1.0, 1.0,
                              val,  val, 0.0,  1.0, 1.0,
                             -val,  val, 0.0,  0.0, 1.0,
                             -val, -val, 0.0,  0.0, 0.0,
                             ], dtype= np.float32)

        print("Quad size in bytes is: ",  quad.size * quad.itemsize, "bytes")

        # Set the params for vertex attributes for the vertex shader
        stride_position = 5 * quad.itemsize
        offset_position = 0
        stride_tex      = 5 * quad.itemsize
        offset_tex      = 3 * quad.itemsize

        print("stride_position: ", stride_position)
        print("offset_position: ", offset_position)
        print("stride_tex: ", stride_tex)
        print("offset_tex: ", offset_tex)

        # Send all vertex data to the graphics processor memory using Vertex Buffer Object VBO
        self.VAO_1 = glGenVertexArrays(1)
        glBindVertexArray(self.VAO_1)

        VBO_1 = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER,VBO_1)
        #Upload the actual data
        # www.open.gl/drawing
        glBufferData(GL_ARRAY_BUFFER,quad.size * quad.itemsize,quad,GL_STATIC_DRAW)

        # Create texture binding
        self.texture_1 = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_1)

        # texture wrapping params
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        # texture filtering parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # position = glGetAttribLocation(shader,"position")
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride_position, ctypes.c_void_p(offset_position))
        glEnableVertexAttribArray(0)

        # texture_coords = glGetAttribLocation(shader,"inTexCoords")
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride_tex, ctypes.c_void_p(offset_tex))
        glEnableVertexAttribArray(1)


    def run_loop(self):

        glUseProgram(self.shader)

        # Create color for window
        glClearColor(0.2,0.3,0.1,1.0)
        glEnable(GL_DEPTH_TEST)

        # Define viewMatrix - This is the camera pose
        view = pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, -3]))
        print("Defined view matrix is: ", view)

        #Define the projection matrix. This is equivalent to the intrinsic matrix
        projection = pyrr.matrix44.create_perspective_projection_matrix(100.0, self.w_width/self.w_height, 0.1, 100.0)
        print("Defined projection matrix is: ", projection)

        # # Set position of cube/ model. This is the object pose.
        # model =pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, -2.0 ]))
        # print("Defined model matrix is: ", model)

        # Get the orientation data from the shader
        view_loc        = glGetUniformLocation(self.shader, "view")
        proj_loc  = glGetUniformLocation(self.shader, "projection")
        model_loc  = glGetUniformLocation(self.shader, "model")

        # Set the values
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
        # glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)


        while not glfw.window_should_close(self.window):
            glfw.poll_events()

            # Clear the color buffer value
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # Show Background
            glBindVertexArray(self.VAO_1)
            self.load_texture("camera")
            background_pose = pyrr.matrix44.create_from_translation([0.,0.,-1.])
            glUniformMatrix4fv(model_loc, 1, GL_FALSE, background_pose)
            glDrawArrays(GL_TRIANGLES, 0, 6)

            # Show overlayed object
            glBindVertexArray(self.VAO_2)
            self.apply_obj_texture()

            model_pose = pyrr.matrix44.create_from_axis_rotation([1.,1.,0.], 0.4 * glfw.get_time())
            # model_pose = pyrr.matrix44.create_from_translation([0.,0.,-50.])
            glUniformMatrix4fv(model_loc, 1, GL_FALSE, model_pose)
            # view = pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, -2]))
            # glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
            glDrawArrays(GL_TRIANGLES, 0, len(self.model_obj.vertex_index))


            # model_pose = pyrr.matrix44.create_from_axis_rotation([1.,1.,0.], 0.4 * glfw.get_time())
            #
            # glUniformMatrix4fv(model_loc, 1, GL_FALSE, model_pose)
            #
            # glDrawArrays(GL_TRIANGLES, 0, len(self.model_obj.vertex_index))


            glfw.swap_buffers(self.window)

        # Terminate glfw
        glfw.terminate()

    def load_texture(self, fname_texture):
        # Load texture from image
        if ".jpg" in fname_texture:
            im_type = "jpg" # "png" or "jpg"
        elif ".png" in fname_texture:
            im_type = "png" # "png" or "jpg"
        elif "camera" in fname_texture:
            im_type = "camera"

        else:
            print("Error. Incorrect ftype for texture file. Can be png or jpg")
            return

        if im_type == "jpg":
            image = Image.open(fname_texture)
            # image = Image.open("./res/butterfly/MONARCH."jpg)
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            width, height = image.size
            # print("Loaded Image size: ", image.size)
            img_data = np.array(list(image.getdata()), np.uint8)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB,
                         width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
            glEnable(GL_TEXTURE_2D)

        elif im_type == "png":
            image = Image.open(fname_texture)
            # This causes flipped image for png
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            width, height = image.size
            # print("Loaded Image size: ", image.size)

            img_data = image.convert("RGBA").tobytes()
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                         width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
            glEnable(GL_TEXTURE_2D)

        elif im_type == "camera":

            ret, frame = self.cap.read()

            if ret ==True:
                frame = cv.rotate(frame,cv.cv2.ROTATE_180)
                frame = Image.fromarray(frame)                                                 # CONVERTING IMAGE FROM ARRAY FORM TO PILLOW IMAGE FORM
                width = frame.size[0]                                                          # CALCULATING WIDTH OF IMAGE
                height = frame.size[1]                                                         # CALCULATING HEIGHT OF IMAGE
                frame = frame.tobytes("raw", "BGRX")                                           # CONVERTING IMAGE TO BYTES

                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                             width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, frame) #CREATES A 2-D TEXTURE IMAGE
                glEnable(GL_TEXTURE_2D)



    def load_obj_file(self,fname_obj, fname_texture):
        # Load the obj file in the application
        obj = ObjLoader()
        obj.load_model(fname_obj)
        self.model_obj = obj

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

        # Send all vertex data to the graphics processor memory using Vertex Buffer Object VBO
        self.VAO_2 = glGenVertexArrays(1)
        glBindVertexArray(self.VAO_2)
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



    def apply_obj_texture(self):

        # Load image
        im_type = "jpg" # "png" or "jpg"

        if im_type == "jpg":
            image = Image.open("./models/cube/cube_texture.jpg")
            # image = Image.open("./res/butterfly/MONARCH."jpg)
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            width, height = image.size
            # print("Loaded Image size: ", image.size)
            img_data = np.array(list(image.getdata()), np.uint8)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB,
                         width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
            glEnable(GL_TEXTURE_2D)

        elif im_type == "png":
            image = Image.open("./res/opengl_test.png")
            # This causes flipped image for png
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            width, height = image.size
            # print("Loaded Image size: ", image.size)

            img_data = image.convert("RGBA").tobytes()
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                         width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
            glEnable(GL_TEXTURE_2D)


