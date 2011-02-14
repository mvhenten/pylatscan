#!/usr/bin/env python
#import sys
#import math
#import optparse
import cv
import serial
import time

from PIL import Image


p_port = '/dev/ttyUSB0'
p_cam = 1
p_width, p_height = (920,720)


s = serial.Serial(p_port);

mode = -1
turns = 1

win = ['right', 'left', 'color']

#for w in win:
#    cv.NamedWindow(w)



if __name__=="__main__":
    while True:
        mode +=1

        #print win[mode]
        
        #name = win[mode]
        
        if mode == 0:
            s.write('7')
            s.write('2')
            
        elif mode == 1:
            s.write('3')
            s.write('4')
        else:
            print "%03d/400" % turns
            s.write('5')
            s.write('6')
            s.write('1')
            turns += 1
            mode = -1


        cam = cv.CaptureFromCAM(p_cam);
        cv.SetCaptureProperty(cam, cv.CV_CAP_PROP_FRAME_WIDTH, p_width)
        cv.SetCaptureProperty(cam, cv.CV_CAP_PROP_FRAME_HEIGHT, p_height)
        src = cv.QueryFrame(cam);
        

        #cv.ShowImage( win[mode], src );
        
        size = cv.GetSize(src);
        
        r = cv.CreateImage( size, cv.IPL_DEPTH_8U, 1 )
        g = cv.CreateImage( size, cv.IPL_DEPTH_8U, 1 )
        b = cv.CreateImage( size, cv.IPL_DEPTH_8U, 1 )

        
        
        cv.Split( src, b, g, r, None );
        cv.Merge( r, g, b, None, src );
        
        #print cv.GetSize(src);
        #src = cv.CvtColor(src, src, CV_BGR2RGB)
        
        name = 'color'
        if mode != -1:
            name = win[mode]

        pil_im = Image.fromstring("RGB", cv.GetSize(src), src.tostring())
        pil_im.save('%s_img_%04d.jpg'%(name,max(1,turns-1)))
        

        
        cam = None;
        
        
        key = ( cv.WaitKey(10) ) % 0x100
        
        


        #img = cv.QueryFrame(cam)

        if key == 27:
            break;
        
        if turns > 401:
            break;
