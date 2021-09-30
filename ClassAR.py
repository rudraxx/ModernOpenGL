import glfw
from OpenGL.GL import *
import ShaderLoader
import numpy as np
import pyrr
from PIL import Image
from ObjLoader import *
import cv2
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
        self.shader = ShaderLoader.compile_shader("shaders/vertex_shader_smvp_matrix.vs",
                                             "shaders/fragment_shader_smvp_matrix.fs")
        # self.shader = ShaderLoader.compile_shader("shaders/vertex_shader_tex_quad.vs",
        #                                      "shaders/fragment_shader_tex_quad.fs")

        init_complete = True

        # Init the camera feed
        self.cap = cv2.VideoCapture(0)

        return init_complete

    # Create callback for changing the size of window
    def fcn_window_resize(self, window, new_width, new_height):
        glViewport(0, 0,  new_width, new_height)

    def run_loop(self):

        glUseProgram(self.shader)

        # Create color for window
        glClearColor(0.2,0.3,0.1,1.0)
        glEnable(GL_DEPTH_TEST)

        #Define the projection matrix. This is equivalent to the intrinsic matrix
        projection = pyrr.matrix44.create_perspective_projection_matrix(45.0, self.w_width/self.w_height, 0.1, 100.0)
        print("Defined projection matrix is: ", projection)

        # Define viewMatrix - This is the camera pose
        view = pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, -3]))
        print("Defined view matrix is: ", view)

        # Set the default value of the model matrix. This is the object pose.
        model =pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, -5.0 ]))
        print("Defined model matrix is: ", model)

        # Define scaleMatrix - This is the model scale matrix 4x4
        scale_default = pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, 0]))
        print("Defined scale matrix is: ", scale_default)

        # Get the orientation data from the shader
        proj_loc  = glGetUniformLocation(self.shader, "projection")
        view_loc  = glGetUniformLocation(self.shader, "view")
        model_loc = glGetUniformLocation(self.shader, "model")
        scale_loc = glGetUniformLocation(self.shader, "scale")

        # Set the matrices for the background pane
        glBindVertexArray(self.VAO_background)

        # glUniformMatrix4fv(scale_loc, 1, GL_FALSE, scale_default)
        # background_pose = pyrr.matrix44.create_from_translation([0.,0.,-5.])
        # glUniformMatrix4fv(model_loc, 1, GL_FALSE, background_pose)
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)

        while not glfw.window_should_close(self.window):
            glfw.poll_events()
            # Clear the color buffer value
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # Background related

            # Vertex operations
            glBindVertexArray(self.VAO_background)
            background_pose = pyrr.matrix44.create_from_translation([0.,0.,-5.])
            glUniformMatrix4fv(model_loc, 1, GL_FALSE, background_pose)
            glUniformMatrix4fv(scale_loc, 1, GL_FALSE, scale_default)
            # Texture operations
            glBindTexture(GL_TEXTURE_2D,self.tex_background)

            # Read from camera
            # ret, frame = self.cap.read()
            ret = True
            frame = cv2.imread("X:/arvr_exploration/calibrate_camera/images/aruco_overlay/IMG_4807.jpg")
            if ret:
                updated_frame = self.detect_marker(frame)
                self.apply_texture(self.background_texture_file, updated_frame)

            glDrawArrays(GL_TRIANGLES, 0, 6)

            # Overlay object related

            # Vertex operations
            glBindVertexArray(self.VAO_object)
            model_pose = pyrr.matrix44.create_from_axis_rotation([1.,1.,0.], 0.4 * glfw.get_time())
            model_pose[3][0] = 1.0
            model_pose[3][1] = -1.0
            model_pose[3][2] = -3.0

            # Define the scale for the model
            # Define scaleMatrix - This is the model scale matrix 4x4
            scale = pyrr.matrix44.create_from_translation(pyrr.Vector3([0.0, 0.0, 0]))
            scale_factor = 0.5
            for i in range(0,3):
                scale[i][i] = scale_factor
                scale[i][i] = scale_factor
                scale[i][i] = scale_factor

            glUniformMatrix4fv(scale_loc, 1, GL_FALSE, scale)
            glUniformMatrix4fv(model_loc, 1, GL_FALSE, model_pose)

            # Texture opeations
            glBindTexture(GL_TEXTURE_2D,self.tex_object)
            # self.apply_texture(self.object_texture_file)

            glDrawArrays(GL_TRIANGLES, 0, len(self.model_obj.vertex_index))

            glfw.swap_buffers(self.window)

        # Terminate glfw
        glfw.terminate()

    def detect_marker(self, frame):
        frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

        #Load the dictionary that was used to generate the marker
        dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_100)

        #Initialize the detector parameters using the default values
        parameters = cv2.aruco.DetectorParameters_create()

        #Detect the marker in the image
        markerCorners, markerIds, rejectedCandidates = cv2.aruco.detectMarkers(frame, dictionary, parameters = parameters)

        self.detectedMarkerID = markerIds[0][0]

        # Show marker
        img_corners = np.copy(frame)
        # img_corners = cv2.cvtColor(img_corners,cv2.COLOR_BGR2RGB)

        cv2.aruco.drawDetectedMarkers(img_corners, markerCorners, markerIds);

        cameraMatrix = np.load("calibration_matrix.npy")
        distCoeffs = np.load("distCoeffs.npy")

        [rvecs, tvecs, objPts] = cv2.aruco.estimatePoseSingleMarkers(markerCorners, 1, cameraMatrix, distCoeffs);

        # print("tvecs are: \n ", tvecs)
        # print("rvec is rodrigues rotation vector: \n ", np.rad2deg(rvecs))
        # print("objPts are: \n ", objPts)

        dst,jacob = cv2.Rodrigues(rvecs[0][0])
        #Convert the dcm to euler angles

        # print('\n dst=\n ', dst)

        # r = R.from_dcm(dst)
        # print(np.rad2deg(r.as_euler('zyx')))
        # print(np.rad2deg(r.as_euler('ZYX')))

        # Draw the markers
        img_axis = np.copy(img_corners)

        for i in range(0,1):
            rvec = rvecs[0][i];
            tvec = tvecs[0][i];
            cv2.aruco.drawAxis(img_axis, cameraMatrix, distCoeffs, rvec, tvec, 2);

        # cv2.imshow("Overlay Image", img_axis)# plt.imshow(frame)
        # cv2.waitKey(0) # waits until a key is pressed

        return img_axis


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
