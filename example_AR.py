from ClassAR import *

obj = ClassAR("My OpenGL Window")

CheckDepth = True
flag_init_complete = obj.initialize_gl(CheckDepth)

if flag_init_complete:
    # obj.load_background("./res/opengl_test.jpg")
    obj.create_background_quad()
    obj.background_texture_file = "camera"

    obj.object_texture_file = "./models/cube/cube_texture.jpg"
    obj.load_obj_file("./models/cube/cube.obj")

    iter = 0
    # Init the camera feed
    cap = cv2.VideoCapture("C:/Users/AbhishekBhat/Downloads/IMG_4841.MOV")
    while True:

        # frame = cv2.imread("X:/arvr_exploration/calibrate_camera/images/aruco_overlay/IMG_4807.jpg")
        # frame = cv2.imread("X:/arvr_exploration/calibrate_camera/images/aruco_overlay/IMG_4809_mod.jpg")
        # frame = cv2.imread("C:/Users/AbhishekBhat/Downloads/Photos (7)/IMG_4905.jpg")

        # h,w = frame.shape[:2]
        # Resize window based on frame size
        # obj.fcn_window_resize(obj.window, w,h)

        ret, frame = cap.read()
        # ret = True
        if obj.window_status:

            if ret:
                print("Runing iter: ", iter)
                obj.show_object = True
                obj.show_background  = True
                obj.run_loop(frame)
                iter +=1

        else:
            print("Window closed. Closing program")
            break
