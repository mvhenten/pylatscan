#!/usr/bin/env python
import sys
import math
import optparse
import cv
import serial
import time

cam = cv.CaptureFromCAM(0);
cv.SetCaptureProperty(cam, cv.CV_CAP_PROP_FRAME_WIDTH, 960)
cv.SetCaptureProperty(cam, cv.CV_CAP_PROP_FRAME_WIDTH, 720)

img = cv.QueryFrame(cam)
width, height = cv.GetSize(img)




if __name__=="__main__":
    while True:

        line = [(width/2,0),(width/2,height),(0,height/2),(width,height/2)]

        cv.PolyLine( img, [line], False, (255,0,0), 2, 8)


        key = ( cv.WaitKey(10) ) % 0x100

        cv.ShowImage( 'source', img );


        img = cv.QueryFrame(cam)
        if key == 27:
            break;
