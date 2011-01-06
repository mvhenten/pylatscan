#!/usr/bin/env python
"""
opencv calibration script. writes camera calibration to .xml files
Large chunks have been taken from the original openCV calibrate_camera.py 
"""

import cv
import math

cam = None
device = 2

# globals
have_corners  = False
store_corners = []

rowcols = (4,4)
corners      = None

distortion = None
intrinsics = None

def mk_object_points(nimages, rowcols, squaresize = 1):
    r,c = rowcols    
    num_pts = r * c
    
    opts = cv.CreateMat(nimages * num_pts, 3, cv.CV_32FC1)
    
    for i in range(nimages):
        for j in range(num_pts):
            opts[i * num_pts + j, 0] = (j / r) * squaresize
            opts[i * num_pts + j, 1] = (j % r) * squaresize
            opts[i * num_pts + j, 2] = 0
    return opts

def mk_image_points(goodcorners, rowcols):
    r,c = rowcols    
    num_pts = r * c

    ipts = cv.CreateMat(len(goodcorners) * num_pts, 2, cv.CV_32FC1)
    
    for (i, co) in enumerate(goodcorners):
        for j in range(num_pts):
            ipts[i * num_pts + j, 0] = co[j][0]
            ipts[i * num_pts + j, 1] = co[j][1]
    return ipts

def mk_point_counts(nimages, rowcols):
    r,c = rowcols    
    num_pts = r * c

    npts = cv.CreateMat(nimages, 1, cv.CV_32SC1)
    for i in range(nimages):
        npts[i, 0] = num_pts
    return npts

def on_key_space(frame):
    global have_corners, corners, store_corners
    
    if have_corners:
        store_corners.append(corners)
        print "Stored %d corners" % len(corners)

def on_enter_frame( frame ):
    global have_corners, corners, rowcols, intrinsics, distortion
    
    w,h = cv.GetSize( frame )
        
    img = cv.CreateImage( (w,h), cv.IPL_DEPTH_8U, 1 )
    cv.CvtColor( frame, img, cv.CV_RGB2GRAY );
    
    have_corners, corners = cv.FindChessboardCorners( img, rowcols )

    if have_corners:
        cv.DrawChessboardCorners( frame, rowcols, corners, True )

    if intrinsics and distortion:
        new = cv.CreateImage((w,h), cv.IPL_DEPTH_8U, 3)
        cv.Undistort2( frame, new, intrinsics, distortion )
        cv.ShowImage( 'Calibrated', new )

    cv.ShowImage( 'Frame', frame )

    
def on_key_s( frame ):
    global store_corners, rowcols, intrinsics, distortion
    
    if len(store_corners) < 1:
        print "No calibration yet. hold a chessboard in front of the cam and pres <space>"
        return
    
    ipts = mk_image_points(store_corners, rowcols)
    opts = mk_object_points(len(store_corners), rowcols, 1)
    npts = mk_point_counts(len(store_corners), rowcols)
    
    intrinsics = cv.CreateMat(3, 3, cv.CV_64FC1)
    distortion = cv.CreateMat(4, 1, cv.CV_64FC1)
    
    cv.SetZero(intrinsics)
    cv.SetZero(distortion)
    
    # focal lengths have 1/1 ratio
    intrinsics[0,0] = 1.0
    intrinsics[1,1] = 1.0
    
    cv.CalibrateCamera2(opts, ipts, npts,
               cv.GetSize(frame),
               intrinsics,
               distortion,
               cv.CreateMat(len(store_corners), 3, cv.CV_32FC1),
               cv.CreateMat(len(store_corners), 3, cv.CV_32FC1),
               flags = 0) # cv.CV_CALIB_ZERO_TANGENT_DIST)

    print [[distortion[i,j] for j in range(0,distortion.cols)] for i in range(0,distortion.rows)]
    print [[intrinsics[i,j] for j in range(0,intrinsics.cols)] for i in range(0,intrinsics.rows)]
    
    cv.Save( 'intrinsics.xml', intrinsics)
    cv.Save( 'distortion.xml', distortion)
    
    intrinsics = cv.Load( 'intrinsics.xml' )
    distortion = cv.Load( 'distortion.xml' )
    
    store_corners = []


def main( device ):
    print """
        calibrate your camera. Hold a chessboard pattern in front of the camera
        if the pattern is detected correctly, press <space> a couple of times
        press <s> to save the calibration. press <esc> to quit.
    """
    cam = cv.CaptureFromCAM( device )
    
    while True:
        frame = cv.QueryFrame(cam)

        key = ( cv.WaitKey(20) ) % 0x100
        if key == 27:
            exit( 'bye bye!' )
        if key == 32:
            on_key_space( frame )
        if key == 115:
            on_key_s( frame )

        on_enter_frame(frame)

if __name__ == "__main__":
    main( device )