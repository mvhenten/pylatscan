#!/usr/bin/env python

# PyLatScan - a Laser Triangulation Point Cloud Scanner
#
# Copyright (C) 2010 - 2011 Waag Society <society@waag.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""
@title Spline scanning using OpenCV
"""
import numpy as np

import sys
import optparse
import cv
import os
import math
import time

from math import *
import glob

from pylatscan.model.pointset import *
from pylatscan.model.parser import *

def main():
    """process all files in a directory and output a pointcloud
        
        This script is still a work in progress.
        
        @todo move looping an parsing into models
        @todo allow for red colored lasers
        @todo allow for scanning just left or right
        
        argument options Optparse object
        argument files Files to process as (left_images,right_images,color_images)
    
    """
    parser = optparse.OptionParser("pylatparse [options] <path>");
    parser.add_option("-e","--path", action = "store", type="string", default="/usr/bin/uvccapture", dest="path", help="path to uvcapture binary")
    parser.add_option("-o","--center-offset", action = "store", type="int", default="0", dest="offset", help="Offset from center")
    parser.add_option("-l","--scan-left", action = "store_false", default=True, dest="do_left", help="Scan for left-side laser")
    parser.add_option("-r","--scan-right", action = "store_false", default=True, dest="do_right", help="Scan for right-side laser")
    parser.add_option("-c","--scan-color", action = "store_true", default="True", dest="do_color", help="Extract color information")
    parser.add_option("-x","--roi-top", action = "store", type="int", default="0", dest="left", help="ROI offset left")
    parser.add_option("-y","--roi-left", action = "store", type="int", default="0", dest="top", help="ROI offset top")
    parser.add_option("-w","--roi-width", action = "store", type="int", default="640", dest="width", help="ROI width")
    parser.add_option("-g","--roi-height", action = "store", type="int", default="480", dest="height", help="ROI height")
    parser.add_option("-i","--threshold-min", action = "store", type="int", default="30", dest="min", help="Threshold minimum value")
    parser.add_option("-a","--threshold-max", action = "store", type="int", default="255", dest="max", help="Threshold maximum value")
    parser.add_option("-f","--output-filename", action = "store", type="string", default="pylatscan_pointcloud.wrl", dest="filename", help="Output file")
    
    
    (options, target) = parser.parse_args()
    
    if not target or len( target ) == 0:
        parser.error( "please provide a source directory" )
        exit()
    if not options.do_left and not options.do_right:
        parser.error( "invalid options: you must enable either left or right or both")
        exit()

    
    left, right, color = ([],[],[])
    path = target[0]
    

    #print "Scanning %s for files" % path
        
        
    if options.do_left:
        left = glob.glob( "%s/left*" % path.rstrip( '/' ) )
        left.sort()
    
    if options.do_right:
        right = glob.glob( "%s/right*" % path.rstrip( '/' ) )
        right.sort()
    
    if options.do_color:
        color = glob.glob( "%s/color*" % path.rstrip( '/' ) )
        color.sort()
        
    roi = (options.left, options.top, options.width, options.height )

    xmlpath =  os.path.abspath("%s/../../resources/calibrate" % os.path.dirname(__file__))        


    intrinsics = cv.Load( "%s%s%s" % (xmlpath, os.path.sep, 'intrinsics.xml') )
    distortion = cv.Load( "%s%s%s" % (xmlpath, os.path.sep, 'distortion.xml') )
    
    if max( len(right), len(left)) < 99:
        print "Not enough files: %d" % len(right)
        exit()
        
    steps = len(right)


    print "I: processing %d steps" % steps
    
    (left, right) = parse_images( (left,right,color), roi,
        do_left=options.do_left,
        do_right=options.do_right,
        do_color=options.do_color,
        intrinsics=intrinsics,distortion=distortion )
    
    
    if options.do_left and options.do_right:
        print "I: Merging left and right pointclouds"    
        right[-1:] = points_fit_interpolate(right, left)
    elif options.do_left:
        right = left
        
    print "I: Writing pointcloud to %s" % options.filename

    output_vrml_pointset( options.filename, right );
    
    
if __name__=="__main__":
    main()





