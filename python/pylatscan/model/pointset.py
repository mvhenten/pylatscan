#!/bin/env python
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
""" Utility functions for importing and exporting pointcloud files """

import sys

import numpy as np
from math import *


def output_vrml_lineset( filename, points ):
    """
    Write a vrml lineset file
    
    argument filename Filename to be written
    argument points A 2D array of points [[X,Y,Z,R,G,B]]
        
    """
    #vrml template for indexlineset
    vrml = """
Shape {
  geometry IndexedLineSet {
    coord Coordinate {
      point [ %s
      ]
    }
    coordIndex [
        0, 1, 2, -1
    ]
    color Color {
        color [ %s
        ]
    }
    colorPerVertex TRUE
  }
}
"""    
    points = np.array(points);
    
    color = ["%0.2f, %0.2f, %0.2f\n" % (r,g,b) for _,_,_,b,g,r in points]    
    point = ["%0.2f, %0.2f, %0.2f\n" % (x,y,z) for x,y,z,_,_,_ in points]
    
    color = str.join("", color)
    point = str.join("", point)

    vrml = vrml % (point, color);

    out = open( filename, "w")
    out.write( vrml )
    out.close()
    

def output_vrml_pointset( filename, points ):
    """
    Write a vrml pointset to disk
    
    argument filename Filename to be written
    argument points A 2D array of points [[X,Y,Z,R,G,B]]
    
    """
    # vrml template
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
    points = np.array(points);
    
    
    color = ["%0.2f, %0.2f, %0.2f\n" % (r,g,b) for _,_,_,b,g,r in points]    
    point = ["%0.2f, %0.2f, %0.2f\n" % (x,y,z) for x,y,z,_,_,_ in points]
    
    color = str.join("", color)
    point = str.join("", point)


    vmrl = vmrl % (point, color);

    out = open( filename, "w")
    out.write( vmrl )
    out.close()
    
def output_asc_pointset( filename, points ):
    """
    Write pointset to disk in raw ASCII format .asc
    
    argument filename File to write
    argument points A 2D array of points [[X,Y,Z,R,G,B]]
    
    """
    points = ["%0.2f, %0.2f, %0.2f, %0.2f, %0.2f, %0.2f" % (x,y,z,r,g,b) for x,y,z,r,g,b in points]
    points = str.join( "\n", points )
    
    out = open( filename, "w")
    out.write( points )
    out.close()    