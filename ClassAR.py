import glfw
from OpenGL.GL import *
import ShaderLoader
import numpy as np
import pyrr
from PIL import Image
from ObjLoader import *
import cv2
from ClassImageProcessing import *

# from scipy.spatial.transform import Rotation as R


class ClassAR():

    window_name = None
    w_height = None
    w_width = None
    window = None
    shader = None
    model_obj = None
    VAO_background = None
    VAO_2 = None
    background_texture_file = None
    object_texture_file = None
    tex_background = None
    tex_object = None
    show_object = False
    show_background = False
    obj_cv = None # CV operations


    def __init__(self, window_name, w_width=800, w_height=600):
        self.window_name = window_name
        self.w_width  = w_width
        self.w_height = w_height
        self.obj_cv = ClassImageProcessing()



    def initialize_gl(self, CheckDepth):

        init_complete = False
        if not glfw.init():
            return init_complete

        self.window_status = True
        self.window  = glfw.create_window(self.w_width, self.w_height,
                                     self.window_name, None, None)

        # Set glfw context to window
        glfw.make_context_current(self.window)
        glfw.set_window_size_callback(self.window,self.fcn_window_resize )

        # Create color for window
        glClearColor(0.2,0.3,0.1,1.0)

        # Create the vertex_shader
        self.shader = ShaderLoader.compile_shader("shaders/vertex_shader_smvp_matrix.vs",
                                             "shaders/fragment_shader_smvp_matrix.fs")
        # self.shader = ShaderLoader.compile_shader("shaders/vertex_shader_tex_quad.vs",
        #                                      "shaders/fragment_shader_tex_quad.fs")


        glUseProgram(self.shader)

        if CheckDepth:
            self.CheckDepth = True
            glEnable(GL_DEPTH_TEST)
        else:
            self.CheckDepth = False

        #Define the projection matrix. This is equivalent to the intrinsic matrix
        self.projection_default = pyrr.matrix44.create_perspective_projection_matrix(100.0, self.w_width/self.w_height, 0.1, 100.0)
        print("Defined projection matrix is: ", self.projection_default)

        # Define viewMatrix - This is the camera pose
        self.view_default = pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, -3]))
        print("Defined view matrix is: ", self.view_default)

        # Set the default value of the model matrix. This is the object pose.
        self.model_default =pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, -5.0 ]))
        print("Defined model matrix is: ", self.model_default)

        # Define scaleMatrix - This is the model scale matrix 4x4
        self.scale_default = pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, 0]))
        print("Defined scale matrix is: ", self.scale_default)

        self.identity_mat = pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, 0]))

        # glBindVertexArray(self.VAO_background)
        # Get the orientation data from the shader
        self.proj_loc  = glGetUniformLocation(self.shader, "projection")
        self.view_loc  = glGetUniformLocation(self.shader, "view")
        self.model_loc = glGetUniformLocation(self.shader, "model")
        self.scale_loc = glGetUniformLocation(self.shader, "scale")


        init_complete = True


        return init_complete

    # Create callback for changing the size of window
    def fcn_window_resize(self, window, new_width, new_height):
        glViewport(0, 0,  new_width, new_height)

    def run_loop(self, frame):

        # Let top level know if window was closed
        if glfw.window_should_close(self.window):
            # Terminate glfw
            glfw.terminate()
            self.window_status = False

        else:
            glfw.poll_events()
            # Clear the color buffer value
            if self.CheckDepth:
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            else:
                glClear(GL_COLOR_BUFFER_BIT)

            if self.show_background:

                # Background related

                # Set all matrices to be identity. Keep the quad size to be +/- 1 so
                # that it covers the full viewport

                # Vertex operations
                glBindVertexArray(self.VAO_background)
                # Set all the matrices to identity so that the image covers the full viewport
                glUniformMatrix4fv(self.proj_loc, 1, GL_FALSE, self.identity_mat)
                glUniformMatrix4fv(self.view_loc, 1, GL_FALSE, self.identity_mat)
                glUniformMatrix4fv(self.model_loc, 1, GL_FALSE, self.identity_mat)
                glUniformMatrix4fv(self.scale_loc, 1, GL_FALSE, self.identity_mat)

                # Texture operations
                glBindTexture(GL_TEXTURE_2D,self.tex_background)

                # Detect the marker and  get the orientation matrix
                updated_frame, projMatrix, viewMatrix = self.obj_cv.detect_marker(frame)
                if updated_frame is not None:
                    self.apply_texture(self.background_texture_file, updated_frame)
                else:
                    self.apply_texture(self.background_texture_file, frame)


                glDrawArrays(GL_TRIANGLES, 0, 6)

            if self.show_object:
                updated_frame, projMatrix, viewMatrix = self.obj_cv.detect_marker(frame)

                if projMatrix is not None and viewMatrix is not None:

                    # Overlay object related
                    # Vertex operations
                    glBindVertexArray(self.VAO_object)
                    # model_pose = pyrr.matrix44.create_from_axis_rotation([0.,1.,0.], 0.0 * glfw.get_time())
                    model_pose = pyrr.matrix44.create_from_translation([0.,0.,0.])
                    # model_pose[3][0] = 0.0
                    # model_pose[3][1] = 0.0
                    # model_pose[3][2] = 0.0
                    # model_pose = model_pose.transpose()

                    # Define the scale for the model
                    # Define scaleMatrix - This is the model scale matrix 4x4
                    scale_obj = pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, 0]))
                    scale_factor = 1.0
                    for i in range(0,3):
                        scale_obj[i][i] = scale_factor
                        scale_obj[i][i] = scale_factor
                        scale_obj[i][i] = scale_factor

                    test_vec = np.array([1.0,0.0,0.0,1.0])
                    a = np.matmul(scale_obj, test_vec)
                    b = np.matmul(model_pose, a)
                    c = np.matmul(viewMatrix.transpose(), b)
                    d = np.matmul(projMatrix.transpose(),  c)
                    f = d /d[3]

                    glUniformMatrix4fv(self.scale_loc, 1, GL_FALSE, scale_obj)
                    glUniformMatrix4fv(self.model_loc, 1, GL_FALSE, model_pose)
                    glUniformMatrix4fv(self.proj_loc, 1, GL_FALSE, projMatrix)
                    glUniformMatrix4fv(self.view_loc, 1, GL_FALSE, viewMatrix)

                    # glUniformMatrix4fv(proj_loc, 1, GL_FALSE, self.projection_default)
                    # glUniformMatrix4fv(view_loc, 1, GL_FALSE, self.view_default)

                    # Texture opeations
                    glBindTexture(GL_TEXTURE_2D,self.tex_object)
                    self.apply_texture(self.object_texture_file)

                    glDrawArrays(GL_TRIANGLES, 0, len(self.model_obj.vertex_index))

            glfw.swap_buffers(self.window)

    def create_background_quad(self):
        # Create vertices
        val  = 1.0
        zdepth = -1.
        #                   [positions        texture coordinates]
        quad =   np.array([  -val, -val, zdepth,  0.0, 0.0,
                             val, -val, zdepth,  1.0, 0.0,
                             val,  val, zdepth,  1.0, 1.0,
                             val,  val, zdepth,  1.0, 1.0,
                             -val,  val, zdepth,  0.0, 1.0,
                             -val, -val, zdepth,  0.0, 0.0,
                             ], dtype= np.float32)

        num_bytes_quad = quad.size * quad.itemsize
        print("Quad size in bytes is: ", num_bytes_quad, "bytes")

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
        self.VAO_background = glGenVertexArrays(1)
        glBindVertexArray(self.VAO_background)

        VBO_background = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER,VBO_background)
        #Upload the actual data
        # www.open.gl/drawing
        glBufferData(GL_ARRAY_BUFFER,num_bytes_quad,quad,GL_STATIC_DRAW)

        # Create texture binding
        self.tex_background = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.tex_background)

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

    def load_obj_file(self,fname_obj):
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
        self.VAO_object = glGenVertexArrays(1)
        glBindVertexArray(self.VAO_object)
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
        self.tex_object = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.tex_object)

        # texture wrapping params
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        # texture filtering parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        self.apply_texture(self.object_texture_file)


    def apply_texture(self, fname_texture, frame = None):
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
            frame = cv2.flip(frame,0) # Flip up/down
            frame = Image.fromarray(frame)                                                 # CONVERTING IMAGE FROM ARRAY FORM TO PILLOW IMAGE FORM
            width = frame.size[0]                                                          # CALCULATING WIDTH OF IMAGE
            height = frame.size[1]                                                         # CALCULATING HEIGHT OF IMAGE
            frame = frame.tobytes("raw", "BGRX")                                           # CONVERTING IMAGE TO BYTES

            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                         width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, frame) #CREATES A 2-D TEXTURE IMAGE
            glEnable(GL_TEXTURE_2D)
