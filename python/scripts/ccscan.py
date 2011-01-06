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

    def __init__( self, files, target ):
        cv.NamedWindow('preview', 1)
        cv.CreateTrackbar('t-low', 'preview', self.thresholdMin, 256, self.changeThresholdMin )
        cv.CreateTrackbar('t-upper', 'preview', self.thresholdMax, 256, self.changeThresholdMax )
        #cv.CreateTrackbar('c-size', 'preview', self.contourSize, 100000, self.changeContoursize )
        cv.SetMouseCallback( 'preview', self.onMouseEvent )

        self.files  = files
        self.target = target

        self.step = 360.000 / len(files)
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
        if not self.roi:
            self.roi = (x, y, x+1, y+1)

    def onMouseDrag( self, x, y ):
        """ MouseDrag handler. Drag to define the lower left corners of ROI """
        if self.roi:
            self.roi = (self.roi[0], self.roi[1], max(self.roi[0]+1, x), max(self.roi[1]+1, y) )

    def changeThresholdMax( self, value ):
        self.thresholdMax = value;

    def changeThresholdMin( self, value ):
        self.thresholdMin = value

    def changeContoursize( self, value ):
        self.contourSize = value

    def show( self ):
        """ Process and show the current frame """
        source  = cv.LoadImage( self.files[self.index] )
        width, height = cv.GetSize(source)

        #cv.Flip(source, None, 1);

        red     = cv.CreateImage( (width,height), cv.IPL_DEPTH_8U, 1 )
        mask     = cv.CreateImage( (width,height), cv.IPL_DEPTH_8U, 1 )
        
        test = cv.CreateImage( (width,height), cv.IPL_DEPTH_8U, 3);

        cv.Zero( mask );
        cv.Zero( test );

        hsv     = cv.CreateImage( (width, height), cv.IPL_DEPTH_8U, 3 )

        cv.CvtColor( source, hsv, cv.CV_RGB2HSV );


        # cv.CvtColor( source, red, cv.CV_RGB2GRAY );
        # cv.Split( source, None, None, red, None );

        cv.Split( hsv, None, None, red, None );
        cv.InRangeS( red, self.thresholdMin, self.thresholdMax, red )

        # cv.Copy( red, mask )



        if self.roi:
            # print self.roi
            x, y, x1, y1 = self.roi

            width = float(x1 - x)
            height = float(y1 - y)

            cv.Rectangle( source, (x, y), (x1, y1), (255.0, 255, 255, 0) );
            cv.Rectangle( test, (x, y), (x1, y1), (255.0, 255, 255, 0) );
            cv.Rectangle( mask, (x, y), (x1, y1), (128.0, 0, 0, 0) );
            #Line(img, pt1, pt2, color, thickness=1, lineType=8, shift=0) ? None?

            cv.Line( source, ( x + (width/2), y ), ( x + (width/2), y1 ), (0, 0, 255), 1 );

            cv.SetImageROI( red, (x, y, x1-x, y1-y) )
            cv.SetImageROI( source,(x, y, x1-x, y1-y) )
            cv.SetImageROI( test,(x, y, x1-x, y1-y) )

            points = self.lineScan( red, source );

            colors = [source[y,x+2] for x,y in points];
            cv.PolyLine(source, [points], False, (255, 0, 255), 3, 8, 0)

            # rotate the line back 
            def translate(x,y,arc):
                x,y = float(x), float(y)
                
                arc = atan(y/x) - arc;
                
                len = sqrt(pow(x,2)+pow(y,2))
                x,y = (cos(arc)*len), (sin(arc)*len)
                return x,y
            
            points = [translate(x,y,math.radians(-45)) for x,y in points];
            
            
            cv.PolyLine( test, [points], False, (255,0,255), 3, 8, 0);
            
            cv.ShowImage('test', test);
            
            


            # normalize points and mirror right of the x-axis, mirror bottom-top
            points = [(0.5-(x/width),1.0-(y/height),0.0) for x,y in points]

            def rotate( angle, x, y, z=0.0):
                angle = math.radians(angle);
                zn = z * (math.cos(angle)) - ( x * math.sin(angle) )
                xn = z * (math.sin(angle)) + ( x * math.cos(angle) )

                return (xn, y, zn)

            # points = [self.rotate( self.index * 1, (x, y), x1/2) for x,y in points]


            points = [rotate( (self.index*self.step), x, y, z) for x, y, z in points]
            #
            #points = [(x, y, self.index/100.00) for x,y in points]


            cv.ResetImageROI( red )
            cv.ResetImageROI( source )


        if self.mode == 'mask':
            cv.ShowImage( 'preview', mask )
            return

        if self.mode == 'record' and self.roi:
            #if self.index == 45:
            #    o = open('points.asc', 'w');
            #
            #    p = ["%f %f %f\n" % point for point in points];
            #    p = str.join("", p);
            #
            #    o.write(p);
            #    o.close();
            #    exit();

            if self.index == 1 or self.index == 76 or self.index == 38 or self.index == 114:
                font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX,0.5,0.5,1)
                cv.PutText( source, "recording %d" % self.index, (20,20), font, (0,0,255))
                self.points.extend(points);
                self.colors.extend(colors);



        cv.ShowImage( 'preview', source )

    def rotate( self, angle, point, center ):
        """ By rotating a set of 2d coordinate points, create an x-y-z mapping"""
        x, y = point;

        t_cos = math.cos( math.radians( angle ) );
        t_sin = math.sin( math.radians( angle ) );

        cx = x - center;

        x = float( cx ) * t_cos;
        z = float( cx ) * t_sin;

        return (x, y, z)

    def lineScan( self, image, source = None ):
        """ Performs contour detection on a single channel image.
            Returns a set of 2d points containing the outer left line for the
            detected contours.
        """
        storage = cv.CreateMemStorage()

        contours = cv.FindContours(image, storage, mode=cv.CV_RETR_EXTERNAL, method=cv.CV_CHAIN_APPROX_SIMPLE, offset=(0,0))
        points = [];

        width, height = cv.GetSize(source)

        mask     = cv.CreateImage( (width,height), cv.IPL_DEPTH_8U, 1 )
        cv.Zero(mask);


        if contours:
            while contours:
                size = cv.ContourArea( contours );

                if size < self.contourSize:
                    contours = contours.h_next()
                    continue

                cv.DrawContours( mask, contours, (255, 255, 255), (255, 255, 255), 0, -1 );
                contours = contours.h_next()

            #PolyLine(img, polys, is_closed, color, thickness=1, lineType=8, shift=0) ? None?

        #cv.ShowImage('mask', mask );

        storage = cv.CreateMemStorage()
        contours = cv.FindContours(mask, storage, mode=cv.CV_RETR_EXTERNAL, method=cv.CV_CHAIN_APPROX_SIMPLE, offset=(0,0))

        while contours:
            seq = [(x,y) for x,y in contours if x < width/2]

            points.extend(seq);

            contours = contours.h_next()

        #cv.PolyLine(source, [points], False, (0, 255, 0), 1, 8, 0)

        #cv.DrawContours( source, contours, (255, 0, 0), (0, 255, 0), 0, 1 );
        #
        #if contours:
        #    cv.DrawContours( source, contours, (255,0,0), (0,255,0), 7, -1 )
        #    cv.DrawContours( mask, contours, (255,0,0), (0,255,0), 7, -1 )
        #
        #    while contours:
        #        if cv.ContourArea( contours ) < 200:
        #            contours = contours.h_next()
        #            continue
        #
        #        y_max = max([y for _, y in contours])
        #        seq   = [(x,y) for x,y in contours]
        #
        #        #points.extend(seq);
        #        i = 0
        #
        #        # extract only the left side of the polygon
        #        for i in range( 0, len(seq)-1):
        #            if seq[i][1] == y_max:
        #                break;
        #
        #        seq = seq[:i];
        #
        #        if source: # draws the detected polygon line as feedback
        #
        #        points.extend(seq);
        #        contours = contours.h_next()
        #
        #
        #cv.ShowImage('mask', mask );

        return points;

    def next( self, key = None ):
        """ Updates index, do some housekeeping
            If "r" is pressed, reset index and set mode to "recording"
            If all images have been processed, output pointcloud.
        """
        self.index = self.index + 1

        if self.index >= len( self.files ):
            if self.mode == 'record':
                print "recorded %d points\n" % len(self.points)
                print "writing to %s\n" % self.target

                c = ["%f, %f, %f\n" % ((r/255.0),(g/255.0),(b/255.0)) for b,g,r in self.colors]
                c = str.join( "", c);

                p = ["%f, %f, %f\n" % (x,y,z) for x,y,z in self.points]
                p = str.join("", p);

                vmrl = """
#VRML V2.0 utf8

Shape{
	geometry PointSet {
		coord Coordinate {
				point [ %s
				]
	   }
    color Color {
        color [ %s
        ]
    }
    colorPerVertex TRUE
	}
}
                """;

                p = vmrl % (p, c);



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
