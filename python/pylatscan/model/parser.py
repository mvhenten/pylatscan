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
"""Functions for extracting point cloud data out of laser-scan images"""

import math
import cv
import numpy as np


#from math import *
from scipy import interpolate
import time

def points_triangulate( points, angle,cam_degree ):
    x,y = points
    cam_angle=math.radians(cam_degree)    
    radius = x / math.sin(cam_angle)

    return [
        radius * math.cos(angle),
        radius * math.sin(angle),
        y * 1.00
    ]

    
def points_max_cols( img,color='green',threshold=(30,255)):
    """
    Read maximum pixel value in one color channel for each row
    """
    
    tmin, tmax = threshold
    w, h = cv.GetSize( img )
    xy = list()
    
    gray = cv.CreateImage( (w,h), cv.IPL_DEPTH_8U, 1 )
    
    if color == 'red':
        cv.Split( img, None, None, gray, None )
    else:
        cv.Split( img, None, gray, None, None )

    for i in range( 0, h):
        row = cv.GetRow( gray, i );
        minv, maxv, minl, maxl = cv.MinMaxLoc( row )
        
        if maxv > tmin:
            xy.append((maxl[0], i))

    return xy


def points_rotate_zaxis( points, angle ):
    """
    Translate a set of points around the z-axis for a given degree
    """
    
    if len(points) < 1:
        return points
    
    points = np.array(points)
    
    
    x = points[:,0]
    y = points[:,1]
                
    nx = ( math.cos(angle) * x ) - ( math.sin(angle) * y )
    ny = ( math.sin(angle) * x ) + ( math.cos(angle) * y )
    
    points[:,0] = nx
    points[:,1] = ny

    return points

def points_find_overlaps_xy( a, b, dif=0.1 ):
    """
    Return indexes for points on overlapping radials between a and b on the X-Y plane for b

    named argument dif is the allowed deviation in absolute radials        
    """
    overlaps = []
    
    if len(b) == 0 or len(a) == 0:
        return overlaps

    a = a[np.nonzero(a)]
    b = b[np.nonzero(b)]
    
    for i, angle in enumerate( a ):
        difs = np.abs( b - angle )
       
        #print len(difs), 'DIFS'
        minv = np.min( difs )
        
        if minv < dif:
            #if minv == 0:
            #    print "minv 0, why"
            idx = list( difs ).index(minv)
            overlaps.append( (i, idx) )

    return overlaps


def points_fit_interpolate( model_a, model_b ):
    """
    Fit points from model_b onto model_a, and remove points that overlap
    
    This is a trick to merge two point clouds that may not be exactly the
    same, using points from one cloud to close gaps in the other.
    
    @todo smooth out spikes in interpolation that originate from noise 
    """
    model_a = np.array(model_a)
    model_b = np.array(model_b)
    
    zs = np.unique(model_a[:,2]);
    
    
    min_z, max_z = min( model_a[:,2] ) , max( model_a[:,2])
   
    model_n = []
    
    #min_z, max_z = 265, 266
    
    for z in range(int(min_z), int(max_z)):
        idx = np.where( model_a[:,2] == z )
        a = model_a[idx]

        idx = np.where( model_b[:,2] == z )
        b = model_b[idx]; # [:,(0,1)]
        
        angles = ( np.arctan2( a[:,0], a[:,1] ), np.arctan2( b[:,0], b[:,1] ) )
        overlaps = np.array(points_find_overlaps_xy( angles[0], angles[1] ) )

        if( len(overlaps) > 1 ):
            # overlaps[:,1] = set of indexes
            start, end =  min(overlaps[:,1]), max(overlaps[:,1])

            # scale = scale factors for those indexes
            overlap_a = a[overlaps[:,0]]
            overlap_b = b[overlaps[:,1]]
            
            # scale_x = overlaps # a two colum array
            # put scaling on indexes for b
            scale = overlap_a[:,(0,1)]/overlap_b[:,(0,1)]
            
            sx = np.column_stack((overlaps[:,1],scale[:,0]))
            sy = np.column_stack((overlaps[:,1],scale[:,1]))

            # sort the indexes
            idx = np.argsort(sx,axis=0)[:,0]
            sx = sx[idx]
            
            idx = np.argsort(sy,axis=0)[:,0]
            sy = sy[idx]
            
            # create interpolation
            fn = interpolate.interp1d(sx[:,0], sx[:,1])
            sx = fn( range(start,end) )
            

            fn = interpolate.interp1d(sy[:,0], sy[:,1])
            sy = fn( range(start,end) )
            
            
            #print "%02d: Scaling %d to %d, removing %d overlaps" % (z, start, end, len(overlap_b))
            
            # multiply b with the interpolated indexes
            b[start:end,0] = b[start:end,0] * sx
            b[start:end,1] = b[start:end,1] * sy
            
            # delete overlapping points: there are available from model a
            # and may be considered noise
            b = np.delete(b,overlaps[:,1],axis=0)
            
            #print b[0:10,0]
            if len(b):
                b = b[np.isfinite(b[:,0]) & np.isfinite(b[:,1])]
            
            
            model_n[-1:] = list(b)
        
    return model_n;

def points_process_images( images, roi, cam_degree=30,color=True,
        color_images=[],threshold_min=30,threshold_max=255,intrinsics=None,distortion=None):
    """
    extract 3d pixels and colors from either left or right set of images
    """
    
    angles = [math.radians(i*(360.00/len(images))) for i in range(0,len(images))]
    points = []
    xypoints = []
    w, h = roi[2:4] 
    
    for i, path in enumerate(images):        
        print "II: %03d/%03d processing %s" % ( i, len(images), path )

        img   = cv.LoadImage( path )
        
        if intrinsics and distortion:
            source = cv.CloneImage( source_color )
            cv.Undistort2( source, img, intrinsics, distortion )

        cv.SetImageROI( img, roi )
        xy = points_max_cols( img,threshold=(threshold_min,threshold_max))
        
        xyz = [points_triangulate((x-(w/2), y), angles[i], cam_degree) for x,y in xy]

        if color:
            color = cv.LoadImage(color_images[i])
            
            if intrinsics and distortion:
                source = cv.CloneImage( color )
                cv.Undistort2( source, color, intrinsics, distortion )

            cv.SetImageROI( color, roi )
            colors = [list(color[y,x]) for x, y in xy]
            [xyz[i].extend([r,g,b]) for i, (b,g,r) in enumerate(colors)]
        
        else:
            xyz = [[x,y,z,1.0,1.0,1.0] for x,y,z in xyz]
        
        points.extend(xyz)
        
    return points

def parse_images( files, roi, cam_angle=math.radians(30),
        do_left=True,do_right=True,do_color=True,
        threshold_min=30,threshold_max=255,intrinsics=None,distortion=None):
    """
    Process a set of images (left, right, color) into colored 3d points.    
    """

    images_left = files[0]
    images_right = files[1]
    color_images = files[2]
    
    points_left = []
    points_right = []
    
    if do_left:
        points_left = points_process_images( images_left,roi,
            color_images=color_images,threshold_min=threshold_min,color=do_color)
        
        points_left = points_rotate_zaxis( points_left, math.radians(240) )
    
    if do_right:
        points_right = points_process_images( images_right,roi,
            color_images=color_images,threshold_min=threshold_min,color=do_color)
    
    return (points_left, points_right)