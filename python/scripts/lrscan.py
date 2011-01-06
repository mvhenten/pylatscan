#!/usr/bin/env python
"""
@title Spline scanning using OpenCV
"""
import sys
import optparse
import cv
import math

from math import *

parser = optparse.OptionParser("scan.py <arguments> <source>\n\nFile mask for the path containing images. Note that this does not use natural sorting!");
parser.add_option("-o","--outfile", action = "store", type="string", dest="target", default="splinescan.wrl")

(options, files) = parser.parse_args()

if not len(files):
    parser.error("No files found matching %s" % str(files))

class SplineScan:
    """
        SplineScan: produces a point cloud from a set of images

        This software takes a set of images and detects red lines. The outer left
        coordinates are then converted into a 3D point cloud by rotating the points
        for each image.
    """
    files   = []
    target  = ''
    index   = 0
    thresholdMax = 256
    thresholdMin = 65
    contourSize  = 300

    roi   = None
    rot   = 1.0
    mode  = None
    frame = None
    points = None
    colors = None
    center = 0
    camAngle = 30
    offset = 0

    def __init__( self, files, target ):
        cv.NamedWindow('preview', 1)
        cv.CreateTrackbar('threshold low', 'preview', self.thresholdMin, 256, self.changeThresholdMin )
        cv.CreateTrackbar('threshold high', 'preview', self.thresholdMax, 256, self.changeThresholdMax )
        cv.CreateTrackbar('offset center', 'preview', 100, 200, self.changeCenterOffset )
        #cv.CreateTrackbar('c-size', 'preview', self.contourSize, 100000, self.changeContoursize )
        cv.SetMouseCallback( 'preview', self.onMouseEvent )

        self.files  = files
        self.target = target

        self.step = math.radians(360.000 / len(files))

        self.angles = [radians(i*(360.00/len(files))) for i in range(0,len(files))]
        self.run();

    def onMouseEvent( self, event, x, y, flag, _ ):
        """ Mouse event callback.
            Examines the event and forwards to specific handlers
        """
        if event == 1:
            self.onMouseDown( x, y )
        elif event == 7:
            self.onMouseDblClick( x, y )
        elif event == 0 and flag == 33:
            self.onMouseDrag( x, y )

    def onMouseDblClick( self, x, y ):
        """ Doubleclick handler. clears the ROI """
        self.roi = None;

    def onMouseDown( self, x, y ):
        """ MouseDown handler. Initializes upper right corners of a new ROI """
        frame = self.getCurrentFrame()
        width,height = cv.GetSize(frame)
        
        center = (width/2) + self.offset
        
        if not self.roi and x > center:
            self.roi = (center, y, x, y+1)

    def onMouseDrag( self, x, y ):
        """ MouseDrag handler. Drag to define the lower left corners of ROI """
        if self.roi:
            p,q,r,s = self.roi
            self.roi = (p, q, max(p+1, x), max(q+1, y) )

    def changeThresholdMax( self, value ):
        self.thresholdMax = value;

    def changeThresholdMin( self, value ):
        self.thresholdMin = value
    
    def changeCenterOffset( self, value ):
        self.offset = value - 100
        
    def getCurrentFrame( self ):
        if not self.frame:
            self.frame = cv.LoadImage( self.files[self.index] )
            
        return self.frame;

    def show( self ):
        """ Process and show the current frame """
        source  = cv.LoadImage( self.files[self.index] )
        width, height = cv.GetSize(source)
        
        center = (width/2) + self.offset;
        
        cv.Line( source, (center,0), (center,height), (0,255,0), 1)


        if self.roi:
            x,y,a,b = self.roi;
            
            width, height = ((a - x), (b - y))
            mask = cv.CreateImage( (width, height), cv.IPL_DEPTH_8U, 1)
        
            cv.SetImageROI( source, (x, y, width, height))           
            cv.Split( source, None, None, mask, None );
            
            gray = cv.CloneImage( mask );
        
            cv.InRangeS( mask, self.thresholdMin, self.thresholdMax, mask );
            cv.And( mask, gray, gray );            
        
            line    = [];
            points  = []; 
        
            for i in range(0,height-1):
                point   = (0, 0, 0)
                row     = cv.GetRow( gray, i)
                
                minVal,minLoc,maxLoc,maxVal = cv.MinMaxLoc(row);
                
                y = i;
                x = maxVal[0]
                
                if x > 0:
                    line.append((x,y));
        
                    s = x / sin(radians(self.camAngle))
                    x = s * cos(self.angles[self.index])                    
                    z = height - y
                    y = s * sin(self.angles[self.index])
                    
                    point = (round(x,2),round(y,2),z);
                
                points.append(point)
        
        
            cv.PolyLine( source, [line], False, (255,0,0), 2, 8)
            cv.ResetImageROI( source )
            x,y,a,b = self.roi;
            cv.Rectangle( source, (int(x), int(y)), (int(a), int(b)), (255.0, 255, 255, 0) );

        if self.roi:
            x,y,a,b = self.roi;
            
            width, height = ((a - x), (b - y))
            mask = cv.CreateImage( (width, height), cv.IPL_DEPTH_8U, 1)
        
            cv.SetImageROI( source, (x-width, y, width, height)) # moves roi to the left
            cv.Split( source, None, None, mask, None );
            
            gray = cv.CloneImage( mask );
        
            cv.InRangeS( mask, self.thresholdMin, self.thresholdMax, mask );
            cv.And( mask, gray, gray );            
        
            line    = [];
            #points  = []; 
        
            for i in range(0,height-1):
                point   = (0, 0, 0)
                row     = cv.GetRow( gray, i)
                
                minVal,minLoc,maxLoc,maxVal = cv.MinMaxLoc(row);
                
                y = i;
                x = maxVal[0]
                
                if x > 0:
                    line.append((x,y));
                    
                    x = width - x; # left to the x-axis
        
                    s = x / sin(radians(self.camAngle))
                                        
                    x = s * cos(self.angles[self.index])                    
                    z = height - y# 500 higher then the other.
                    y = s * sin(self.angles[self.index])


                    #x' = x*cos q - y*sin q
                    #y' = x*sin q + y*cos q
                    #z' = z
                    
                    a = radians(300)
                    
                    nx = ( cos(a) * x ) - ( sin(a) * y )
                    ny = ( sin(a) * x ) + ( cos(a) * y )
                    
                    point = (nx,ny,z);
                
                #if point[0] != 0:
                #    points[i] = point;
                
                points.append(point)
                
            cv.PolyLine( source, [line], False, (255,0,0), 2, 8)
            cv.ResetImageROI( source )
            x,y,a,b = self.roi;
            cv.Rectangle( source, (int(x), int(y)), (int(a), int(b)), (255.0, 255, 255, 0) );


        #if self.roi:
        #    x,y,a,b = self.roi;
        #    
        #    width, height = ((a - x), (b - y))
        #    
        #    roi = [x-width, y, x, b];
        #    
        #    x,y,a,b = roi;
        #    
        #    
        #    mask = cv.CreateImage( (width, height), cv.IPL_DEPTH_8U, 1)
        #
        #    cv.SetImageROI( source, (x, y, width, height))           
        #    cv.Split( source, None, None, mask, None );
        #    
        #    gray = cv.CloneImage( mask );
        #
        #    cv.InRangeS( mask, self.thresholdMin, self.thresholdMax, mask );
        #    cv.And( mask, gray, gray );            
        #    cv.ShowImage('tmp', gray)
        #
        #    line    = [];
        #    #points  = []; 
        #
        #    for i in range(0,height-1):
        #        point   = (0, 0, 0)
        #        row     = cv.GetRow( gray, i)
        #        
        #        minVal,minLoc,maxLoc,maxVal = cv.MinMaxLoc(row);
        #        
        #        y = i;
        #        x = maxVal[0]
        #        
        #        if x > 0:
        #            line.append((x,y));
        #            
        #            x = x - width
        #
        #            s = x / sin(-330)
        #            x = s * cos(self.angles[self.index])                    
        #            z = y/2.0
        #            y = s * sin(self.angles[self.index])
        #            
        #            point = (x,y,z);
        #        
        #        points.append(point)
        #
        #
        #    cv.PolyLine( source, [line], False, (255,0,0), 2, 8)
        #    cv.ResetImageROI( source )
        #    x,y,a,b = self.roi;
        #    
        #    cv.Rectangle( source, (roi[0], roi[1]), (roi[2], roi[3]), (255.0, 255, 255, 0) );
        #
        if self.mode == 'mask':
            cv.ShowImage( 'preview', mask )
            return

        if self.mode == 'record' and self.roi:
            font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX,0.5,0.5,1)
            cv.PutText( source, "recording %d" % self.index, (20,20), font, (0,0,255))
            self.points.extend(points);
            #self.colors.extend(colors);



        cv.ShowImage( 'preview', source )

    def next( self, key = None ):
        """ Updates index, do some housekeeping
            If "r" is pressed, reset index and set mode to "recording"
            If all images have been processed, output pointcloud.
        """
        self.index = self.index + 1
        self.frame = None;

        if self.index >= len( self.files ):
            if self.mode == 'record':
                print "recorded %d points\n" % len(self.points)
                print "writing to %s\n" % self.target

                p = str.join("\n", ["%0.2f, %0.2f, %0.2f" % (x,y,z) for x,y,z in self.points])
                #p = str.join("", p);
                
                vmrl = str.join("\n",
                    [ '#VRML V2.0 utf8'
                    , 'Shape{'
                    , '	geometry PointSet {'
                    , '		coord Coordinate {'
                    , '				point [ %s' 
                    , '				]'
                    , '   }'
                    , '  }'
                    , '}'
                ])

                p = vmrl % p;



                output = open(self.target,"w")
                output.write( p )
                output.close()
                self.mode = 'normal'

            self.index = 0

        key = chr(key % 0x100);

        if key == 'r':
            self.mode = 'record'
            self.index = 0
            self.points = []
            self.colors = []

        if key == 'a':
            self.mode = 'normal'

        if key == 'm':
            self.mode = 'mask'


    def run( self ):
        """ Main loop """
        while True:
            key = cv.WaitKey(2)

            if( key % 0x100 == 27 ):
                break;

            self.next( key )
            self.show()

if __name__=="__main__":
    SplineScan( files, options.target );
