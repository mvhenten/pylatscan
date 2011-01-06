#!/usr/bin/env python
"""
@title Spline scanning using OpenCV
"""
import sys
import math
import optparse
import cv

parser = optparse.OptionParser("scan.py <arguments> <source>\n\nFile mask for the path containing images. Note that this does not use natural sorting!");
parser.add_option("-o","--outfile", action = "store", type="string", dest="target", default="out.wrl")

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
    thresholdMax = 220
    thresholdMin = 35

    roi   = None
    rot   = 1.0
    mode  = None
    frame = None
    points = None

    prevpoints = None
    faces      = []

    def __init__( self, files, target ):
        cv.NamedWindow('preview', 1)
        cv.CreateTrackbar('t-low', 'preview', 35, 254, self.changeThresholdMin )
        cv.CreateTrackbar('t-upper', 'preview', 220, 254, self.changeThresholdMax )
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

    def show( self ):
        """ Process and show the current frame """
        source  = cv.LoadImage( self.files[self.index] )
        width, height = cv.GetSize(source)

        red     = cv.CreateImage( (width,height), cv.IPL_DEPTH_8U, 1 )
        mask     = cv.CreateImage( (width,height), cv.IPL_DEPTH_8U, 1 )

        cv.CvtColor( source, red, cv.CV_RGB2GRAY );

        #cv.Split( source, None, None, red, None )
        cv.InRangeS( red, self.thresholdMin, self.thresholdMax, red )

        cv.Copy( red, mask )

        if self.roi:
            # print self.roi
            x, y, x1, y1 = self.roi
            font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX,0.5,0.5,1)
            cv.PutText( source, "ROI %d,%d,%d,%d" % self.roi , (20,35), font, (0,0,255))
            cv.PutText( source, "%d x %d" % (x1-x, y1-y) , (20,50), font, (0,0,255))

            cv.Rectangle( source, (x, y), (x1, y1), (255.0, 0, 0, 0) );
            cv.Rectangle( mask, (x, y), (x1, y1), (128.0, 0, 0, 0) );

            cv.SetImageROI( red, (x, y, x1-x, y1-y) )
            cv.SetImageROI( source,(x, y, x1-x, y1-y) )

            points = self.lineScan( red, source );
            points = [self.rotate( (self.index*self.step), (x, y), x1/2) for x,y in points]

        cv.ResetImageROI( red )
        cv.ResetImageROI( source )

        if self.mode == 'mask':
            cv.ShowImage( 'preview', mask )
            return

        if self.mode == 'record' and self.roi:
            font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX,0.5,0.5,1)
            cv.PutText( source, "recording %d" % self.index, (20,20), font, (0,0,255))

            if self.prevpoints:
                # for each Y in our ROI
                # check if we can create a face between
                # points from previous and current

                a    = [y for _,y,_ in points]
                b   = [y for _,y,_ in self.prevpoints]

                itr = a if len(a) > len(b) else b
                p = 0;

                for n in itr:
                    size = len(self.points) - len(self.prevpoints)
                    asize = size + len(self.prevpoints)
                    if n in a and n in b and p in a and p in b:
                        face = ( size + b.index(n), asize+ a.index(n), asize + a.index(p), size + b.index(p) )
                        self.faces.append(face);

                    p = n

            self.points.extend(points);




            self.prevpoints = points;

        cv.ShowImage( 'preview', source )

    def rotate( self, angle, points, center ):
        """ By rotating a set of 2d coordinate points, create an x-y-z mapping"""
        x, y = points;

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
        contours = cv.FindContours(image, storage, mode=cv.CV_RETR_EXTERNAL, method=cv.CV_CHAIN_APPROX_NONE, offset=(0,0))
        points = [];

        if contours:
            cv.DrawContours( source, contours, (0,0,0), (0,0,0), 7, -1 )

            while contours:
                y_max = max([y for _, y in contours])
                seq   = [(x,y) for x,y in contours]
                i = 0

                # extract only the left side of the polygon
                for i in range( 0, len(seq)-1):
                    if seq[i][1] == y_max:
                        break;

                seq = seq[:i];

                if source: # draws the detected polygon line as feedback
                    cv.PolyLine(source, [seq], False, (0, 255, 0), 1, 8, 0)

                points.extend(seq);
                contours = contours.h_next()

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
                print "recorded %d faces\n" % len(self.faces)
                print "writing to %s\n" % self.target


                template = """#VRML V2.0 utf8
Transform {
    translation 0 0 0
	children [
		Shape {
			geometry IndexedFaceSet {
			   coord Coordinate {
			      point [
                    %s
			      ]
			   }
			   coordIndex [
                %s
			   ]
			   solid FALSE
			}
		}
	]
}

Viewpoint {
    position 1 -5 1
    orientation 1 0 0 1.57
    description "default viewpoint"
}
                """

                p = ["%f %f %f,\n" % (x,y,z) for x,y,z in self.points]
                p = str.join("", p);

                f = ["%d, %d, %d, %d -1\n" % (a,b,c,d) for a,b,c,d in self.faces]
                f = str.join("", f)
                #output.write(f)

                # print f

                template = template % (p, f)

                output = open(self.target,"w")
                output.write( template )
                output.close()
                self.mode = 'normal'

            self.index = 0

        key = chr(key % 0x100);

        if key == 'r':
            self.mode = 'record'
            self.index = 0
            self.points = []

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
