#!/usr/bin/env python3
"""
Framework   : OpenCV Aruco
Description : Calibration of camera and using that for finding pose of multiple markers
Status      : Working
References  :
    1) https://docs.opencv.org/3.4.0/d5/dae/tutorial_aruco_detection.html
    2) https://docs.opencv.org/3.4.3/dc/dbb/tutorial_py_calibration.html
    3) https://docs.opencv.org/3.1.0/d5/dae/tutorial_aruco_detection.html
"""

import numpy as np
import cv2
import cv2.aruco as aruco
import glob


aruco_dicts = [
    (aruco.DICT_4X4_100,        'DICT_4X4_100'),
    (aruco.DICT_4X4_1000,       'DICT_4X4_1000'),
    (aruco.DICT_4X4_250,        'DICT_4X4_250'),
    (aruco.DICT_4X4_50,         'DICT_4X4_50'),
    (aruco.DICT_5X5_100,        'DICT_5X5_100'),
    (aruco.DICT_5X5_1000,       'DICT_5X5_1000'),
    (aruco.DICT_5X5_250,        'DICT_5X5_250'),
    (aruco.DICT_5X5_50,         'DICT_5X5_50'),
    (aruco.DICT_6X6_100,        'DICT_6X6_100'),
    (aruco.DICT_6X6_1000,       'DICT_6X6_1000'),
    (aruco.DICT_6X6_250,        'DICT_6X6_250'),
    (aruco.DICT_6X6_50,         'DICT_6X6_50'),
    (aruco.DICT_7X7_100,        'DICT_7X7_100'),
    (aruco.DICT_7X7_1000,       'DICT_7X7_1000'),
    (aruco.DICT_7X7_250,        'DICT_7X7_250'),
    (aruco.DICT_7X7_50,         'DICT_7X7_50'),
    (aruco.DICT_APRILTAG_16H5,  'DICT_APRILTAG_16H5'),
    (aruco.DICT_APRILTAG_16h5,  'DICT_APRILTAG_16h5'),
    (aruco.DICT_APRILTAG_25H9,  'DICT_APRILTAG_25H9'),
    (aruco.DICT_APRILTAG_25h9,  'DICT_APRILTAG_25h9'),
    (aruco.DICT_APRILTAG_36H10, 'DICT_APRILTAG_36H10'),
    (aruco.DICT_APRILTAG_36H11, 'DICT_APRILTAG_36H11'),
    (aruco.DICT_APRILTAG_36h10, 'DICT_APRILTAG_36h10'),
    (aruco.DICT_APRILTAG_36h11, 'DICT_APRILTAG_36h11'),
    (aruco.DICT_ARUCO_ORIGINAL, 'DICT_ARUCO_ORIGINAL'),
]

cap = cv2.VideoCapture(0)

####---------------------- CALIBRATION ---------------------------
# termination criteria for the iterative algorithm
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
# checkerboard of size (7 x 6) is used
objp = np.zeros((6*7,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)

# arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

# iterating through all calibration images
# in the folder
images = glob.glob('calib_images/checkerboard/*.jpg')

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    # find the chess board (calibration pattern) corners
    ret, corners = cv2.findChessboardCorners(gray, (7,6),None)

    # if calibration pattern is found, add object points,
    # image points (after refining them)
    if ret == True:
        objpoints.append(objp)

        # Refine the corners of the detected corners
        corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        imgpoints.append(corners2)

        # Draw and display the corners
        img = cv2.drawChessboardCorners(img, (7,6), corners2,ret)


ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)

# detector parameters can be set here (List of detection parameters[3])
parameters = aruco.DetectorParameters_create()
parameters.adaptiveThreshConstant = 10

###------------------ ARUCO TRACKER ---------------------------
dict_index = 0
while (True):
    ret, frame = cap.read()
    #if ret returns false, there is likely a problem with the webcam/camera.
    #In that case uncomment the below line, which will replace the empty frame 
    #with a test image used in the opencv docs for aruco at https://www.docs.opencv.org/4.5.3/singlemarkersoriginal.jpg
    # frame = cv2.imread('./images/test image.jpg') 

    # operations on the frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # set dictionary size depending on the aruco marker selected
    #aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
    
    for aruco_dict, aruco_dict_name in aruco_dicts:

        # lists of ids and the corners belonging to each id
        corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco.Dictionary_get(aruco_dict), parameters=parameters)

        # font for displaying text (below)
        font = cv2.FONT_HERSHEY_SIMPLEX

        # check if the ids list is not empty
        # if no check is added the code will crash
        #if np.all(ids != None):
        if np.all(ids):

            # estimate pose of each marker and return the values
            # rvet and tvec-different from camera coefficients
            rvec, tvec ,_ = aruco.estimatePoseSingleMarkers(corners, 0.05, mtx, dist)
            #(rvec-tvec).any() # get rid of that nasty numpy value array error

            for i in range(0, ids.size):
                # draw axis for the aruco markers
                aruco.drawAxis(frame, mtx, dist, rvec[i], tvec[i], 0.1)

            # draw a square around the markers
            aruco.drawDetectedMarkers(frame, corners)


            # code to show ids of the marker found
            strg = ''
            for i in range(0, ids.size):
                strg += str(ids[i][0])+', '

            # cv2.putText(frame, "Id: " + strg, (0,64), font, 1, (0,255,0),2,cv2.LINE_AA)
            cv2.putText(frame, f'{aruco_dict_name}: Id: {strg}', (0, 64), font, 1, (0,255,0), 2, cv2.LINE_AA)


        else:
            # code to show 'No Ids' when no markers are found
            cv2.putText(frame, "No Ids", (0,256), font, 1, (0,255,0),2,cv2.LINE_AA)

        rvec, tvec ,_ = aruco.estimatePoseSingleMarkers(rejectedImgPoints, 0.05, mtx, dist)

        if rejectedImgPoints:
            cv2.putText(frame, "Rejected", (0,128), font, 1, (0,255,0),2,cv2.LINE_AA)

            for i,p in enumerate(rejectedImgPoints):
                aruco.drawAxis(frame, mtx, dist, rvec[i], tvec[i], 0.1)

        aruco.drawDetectedMarkers(frame, rejectedImgPoints)

        # display the resulting frame
        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()


