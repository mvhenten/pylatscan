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

args = {'source':'test_cube.ply'}

def run( args ):
    points = load_ply(args['source']);
    
    sorted = {}
    
    #print points[0]
    #exit()
    
    for line in points:
        if line[2] not in sorted:
            sorted[line[2]] = []
            
        sorted[line[2]].append(line)
            
    sort_keys = sorted.keys()
    
    print len(sort_keys)
    
    sort_keys.sort()
    
    print len(sort_keys)
    #sort_keys = sort_keys.reverse()
    #sort_keys.reverse()
    
    #print sorted[92.958]
    #return
    
    for key in sort_keys:
        points = np.array(sorted[key])
        
        print key, len(points)
        
        #print points
        
        #exit()
        #angles = np.arctan2(points[:,0], points[:,1])
        #
        #print list(angles)
        #exit();
        
        
    
    
    
    #
    #print sort_keys[0:10]            
    #print sorted.items()[0:10]
    #for z in sorted:
    #    line = sorted[z]
    #
    #print sorted.index()        
    #print sorted[0]
        
        
def load_ply( filename ):
    f = file(filename)
    data = f.read()
    _, data = data.split("end_header\n")
    lines = data.split("\n")
    
    collect = []
    
    for i, line in enumerate(lines):
        line = line.strip().split(' ')
        
        if len(line) < 7:
            break;
        
        x,y,z,r,g,b,a = line
        collect.append([float(n) for n in [x,y,round(float(z)),r,g,b,a]])
        
        #collect.append([n for x,y,z,r,g,b,a in line])
        
    return collect

if __name__ == '__main__':
    run( args )    
