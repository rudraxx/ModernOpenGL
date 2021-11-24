
import cv2
import numpy as np
import pyrr
from scipy.spatial.transform import Rotation as R
from ClassFiltering import *

class ClassImageProcessing():

    def __init__(self):
        #Load the dictionary that was used to generate the marker
        self.dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_100)

        #Initialize the detector parameters using the default values
        self.parameters = cv2.aruco.DetectorParameters_create()

        # Load the matrixes
        self.cameraMatrix = np.load("../res/calibration_iphone/calibration_matrix.npy")
        self.distCoeffs = np.load("../res/calibration_iphone/distCoeffs.npy")

        self.avg_rvecs =None
        self.avg_tvecs =None

        # self.ypr_buffer = np.zeros(shape=(3,3),dtype=np.float32)
        # self.tvec_buffer = np.zeros(shape=(3,3),dtype=np.float32)

        # Create objects for filtering the tvec and rvec values
        self.filter_size = 11 # Samples
        self.obj_ypr = ClassFiltering(self.filter_size)
        self.obj_tvec = ClassFiltering(self.filter_size)

    def reset_avg_filters(self):
        self.obj_ypr = ClassFiltering(self.filter_size)
        self.obj_tvec = ClassFiltering(self.filter_size)


    def update_avg_rvec(self, rvecs, tvecs):

        # Average the 3 values in the rpy buffer
        dst,jacob = cv2.Rodrigues(rvecs[0][0])
        # #Convert the dcm to euler angles
        # print('\n dst=\n ', dst)

        r = R.from_matrix(dst)
        # Use intrinsic rotations for euler angle calculation
        ypr_current = np.rad2deg(r.as_euler('ZYX'))

        # Update avg for angles
        self.obj_ypr.updateBuffer(ypr_current)
        ravg = R.from_euler('ZYX',self.obj_ypr.avg_value,degrees=True)
        self.avg_rvecs = ravg.as_rotvec().reshape(1, 1, 3)

        #Update avg for tvecs
        self.obj_tvec.updateBuffer(tvecs[0])
        self.avg_tvecs = self.obj_tvec.avg_value.reshape(1,1,3)
        # self.avg_tvecs = tvecs

    def detect_marker(self, frame):
        '''
        :param frame:
        :return:
        img_corners
        projMatrix
        viewMatrix
        '''
        projMatrix = None
        viewMatrix = None
        img_corners = None

        # frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

        frame_h, frame_w = frame.shape[:2]


        #Detect the marker in the image
        markerCorners, markerIds, rejectedCandidates = cv2.aruco.detectMarkers(frame, self.dictionary, parameters = self.parameters)

        if markerIds is not None:
            self.detectedMarkerID = markerIds[0][0]

            # Show marker
            img_corners = np.copy(frame)
            # img_corners = cv2.cvtColor(img_corners,cv2.COLOR_BGR2RGB)

            # cv2.aruco.drawDetectedMarkers(img_corners, markerCorners, markerIds)


            [rvecs, tvecs, objPts] = cv2.aruco.estimatePoseSingleMarkers(markerCorners, 1, self.cameraMatrix, self.distCoeffs);

            # Get average rvec
            self.update_avg_rvec(rvecs,tvecs)

            projMatrix, viewMatrix = self.get_gl_proj_and_view_matrices(self.cameraMatrix, frame_w, frame_h, self.avg_rvecs, self.avg_tvecs)

            #Draw axis
            cv2.aruco.drawAxis(img_corners, self.cameraMatrix, self.distCoeffs, self.avg_rvecs[0], self.avg_tvecs[0], 2)
            cv2.aruco.drawAxis(img_corners, self.cameraMatrix, self.distCoeffs, rvecs[0], tvecs[0], 2)

        return img_corners, projMatrix, viewMatrix


    def get_gl_proj_and_view_matrices(self, camMtx, frameW, frameH, rvec, tvec):

        # Projection matrix
        # https://stackoverflow.com/questions/46317246/ar-with-opencv-opengl
        zNear = 0.1
        zFar = 100.0
        projectionMat = np.ndarray(shape=(4,4), dtype=np.float32)
        viewMatrix    = np.ndarray(shape=(4,4), dtype=np.float32)
        # https://strawlab.org/2011/11/05/augmented-reality-with-OpenGL/
        # Buiilding as a transpose of what is shown in strawlab so dont need to do a transpose later
        fudege_factor = 1.0
        projectionMat[0,0]  = fudege_factor* 2*camMtx[0,0]/frameW
        projectionMat[0,1]  = 0.0
        projectionMat[0,2]  = 0.0
        projectionMat[0,3]  = 0.0
        projectionMat[1,0]  = 0.0
        projectionMat[1,1]  = fudege_factor* 2*camMtx[1,1]/frameH;
        projectionMat[1,2]  = 0.0
        projectionMat[1,3]  = 0.0
        projectionMat[2,0]  = 1.0 - 2.0*camMtx[0,2]/frameW
        projectionMat[2,1]  = -1.0 + (2.0*camMtx[1,2] + 2)/frameH
        projectionMat[2,2] = -(zNear + zFar)/(zFar - zNear)
        projectionMat[2,3] = -1.0
        projectionMat[3,0] = 0.0
        projectionMat[3,1] = 0.0
        projectionMat[3,2] = -2*zFar*zNear/(zFar - zNear)
        projectionMat[3,3] = 0.0

        # projectionMat = projectionMat.transpose()
        # Get the view matrix
        # https://answers.opencv.org/question/23089/opencv-opengl-proper-camera-pose-using-solvepnp/#:~:text=Opengl%20matrixes%20are%20column%20major%20order%20whereas%20they,to%20compute%20the%20camera%27s%20pose%20with%20solvePnP%20%28markerObjectPoints%29
        rotation = cv2.Rodrigues(rvec[0])
        rotation = rotation[0]
        tvec = tvec[0]
        for row in range(0,3):
            for col in range(0,3):
                viewMatrix[row, col] = rotation[row, col]

            viewMatrix[row, 3] = tvec[0,row]

        viewMatrix[3, 3] = 1.0

        # Invert the Y and Z axis
        rot_mat = pyrr.matrix44.create_from_axis_rotation([1.0,0.0,0.0], np.deg2rad(180.0))
        # Multiply the view matrix by the transfer matrix between OpenCV and OpenGL:
        viewMatrix2 = np.matmul(rot_mat, viewMatrix)
        viewMatrix2 = viewMatrix2.transpose()
        # viewMatrix2 = viewMatrix # Try with no multiplication

        # cvToGl = np.ndarray( shape = (4, 4), dtype = np.float32)
        # for row in range(0,4):
        #     for col in range(0,4):
        #         cvToGl[row, col] = 0.0
        #
        # cvToGl[0, 0] = 1.0
        # cvToGl[1, 1] = -1.0 # Invert the y axis
        # cvToGl[2, 2] = -1.0 # invert the z axis
        # cvToGl[3, 3] = 1.0
        # viewMatrix = cvToGl * viewMatrix


        # Because OpenCV's matrixes are stored by row you have to transpose the matrix
        # in order that OpenGL can read it by column:
        # viewMatrix = viewMatrix.transpose()

        return projectionMat, viewMatrix2
