from ClassAR import *

obj = ClassAR("My OpenGL Window")

flag_init_complete = obj.initialize_gl()
if flag_init_complete:
    # obj.load_background("./res/opengl_test.jpg")
    obj.create_background_quad()
    obj.background_texture_file = "camera"

    obj.object_texture_file = "./models/cube/cube_texture.jpg"
    obj.load_obj_file("./models/cube/cube.obj")
    obj.run_loop()
