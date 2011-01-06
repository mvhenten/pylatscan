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
# attempt at constructing an indexedface surface
import numpy as np
from string import Template
from scipy import interpolate
import csv

def load_asc( filename ):
    points = list( csv.reader( open( filename ) ) )
    points = np.array( points ).astype( np.float64 )    
    points =  np.array( list( csv.reader( open(filename) ) ) ).astype( np.float64 )
    
    return points[np.nonzero(points[:,0])]
    
def dump_asc( filename, points ):
    points = [str.join( ",", ["%0.2f" % p for p in point]) for point in points]
    points = str.join( "\n", points )
    
    output = open(filename,"w")
    output.write(points)
    output.close()


def run1():
    npoints = [];
    ncoords = [];
    
    points = load_asc( 'cloud.asc' );
    
    zmax, zmin = max(points[:,2]), min(points[:,2])
    
    
    #zmin = 50;

    a = points[np.where(points[:,2] == 50)];
    aa = np.arctan2( a[:,0], a[:,1] );

    a = a[np.argsort(aa)];

    b = points[np.where(points[:,2] == 52)];
    ab = np.arctan2( b[:,0], b[:,1] );
    b = b[np.argsort(ab)];
    
    idx = len(npoints);
    
    r = [p+idx for p in range(0, len(a))]
    
    for p in r:
        tl, tr, bl = p, p + 1, len(a) + p
        
        if bl >= (len(a)+len(b)):
            bl = len(a)
            
        br = bl + 1
        
        if br >= (len(a)+len(b)):
            bl = len(a)
            
        if tr >= len(a):
            tr = p
            
        ncoords.append((tl, bl, br, tr))
        
    
    npoints.extend(list(a));
    npoints.extend(list(b));
    
    #index = 0;
    #
    ##z = 60;
    #
    #for z in range(int(zmin)+10, int(zmax), 2):
    #    print "Z:", z;
    #
    #    ncoords.append( create_indexed_face( a,b, index ) );
    #    index = len(npoints)-1;
    #
    #    npoints.extend(list(b));
    #    
    #    aa = ab;
    #    a  = b;
    
    dump_wrl( npoints, ncoords )

def run3():
    npoints = [];
    ncoords = [];
    
    idx = 0;
    
    source = load_asc( 'cloud.asc' );
    
    zmax, zmin = max(source[:,2]), min(source[:,2])
    points = []

    for i in range(int(zmin), int(zmax)+1):
        points = sort_angles(source[np.where(source[:,2] == i)]);        
        indexes = [p+idx for p in range(0, len(points))]
        
        idx = idx + len(points)
        
        npoints.extend(points);
        ncoords.append(indexes);
        
    dump_wrl( npoints, ncoords )
    
def run():
    npoints = [];
    ncoords = [];
    
    idx = 0;
    
    source = load_asc( 'cloud.asc' );
    
    zmax, zmin = max(source[:,2]), min(source[:,2])
    points = None
    prevpoints = None
    previndexs = None



    for i in range(int(zmin), int(zmax)+1):
        row = np.where(source[:,2] == i);
        points = sort_angles(source[row]);        
        indexs = [p+idx for p in range(0, len(points))]
        
        if prevpoints != None:
            for i in range(0, len(points)):
                if i < len(prevpoints):
                    vertex = [indexs[i], previndexs[i], indexs[0]]
                    if i+1 < len(points):
                        #print i, len(points), len(indexs);
                        vertex = [indexs[i], previndexs[i], indexs[i+1]]
                    vertex.reverse()
                    ncoords.append(vertex)
                
            for i in range(0, len(prevpoints)):
                if i < len(points):
                    vertex = [previndexs[i], previndexs[0], indexs[0]]
                    
                    if i+1 < len(prevpoints):
                        vertex[1] = previndexs[i+1]

                    if i+1 < len(points):
                        vertex[2] = indexs[i+1]

                    vertex.reverse()
                    ncoords.append(vertex)
        
        idx = idx + len(points)
        
        prevpoints = points
        previndexs = indexs

        npoints.extend(points);
        
    dump_wrl( npoints, ncoords )


def sort_angles( points ):
    angles = np.arctan2( points[:,0], points[:,1] )
    if len(angles):
        #print angles
        return points[np.argsort( angles )]
        
    return points

def run2():
    npoints = [];
    ncoords = [];
    
    idx = 0;
    
    points = load_asc( 'cloud.asc' );
    
    zmax, zmin = max(points[:,2]), min(points[:,2])
    
    zmax, zmin = 65, 64

    a = points[np.where(points[:,2] == zmin)];
    aa = np.arctan2( a[:,0], a[:,1] );
    a = a[np.argsort(aa)];

    npoints.extend(list(a));

    for i in range(int(zmin)+1, int(zmax)+1):
        b = points[np.where(points[:,2] == i)];
        ab = np.arctan2( b[:,0], b[:,1] );
        b = b[np.argsort(ab)];
        
        
        r = [p+idx for p in range(0, len(a))]
        
        for p in r:
            tl, tr, bl = p, p + 1, len(a) + p
            
            if bl >= (len(a)+len(b)):
                bl = len(a)
                
            br = bl + 1
            
            if br >= (len(a)+len(b)):
                bl = len(a)
                
            if tr >= len(a):
                tr = p
                
            ncoords.append((tl, bl, br, tr))
        
        idx = idx + len(a)
        a  = b;
        aa = ab;
        npoints.extend(list(b));
    
    dump_wrl( npoints, ncoords )


    
def create_indexed_face( a, b, idx ):
    coords = []
    
    ca = [i+idx for i in range(0, len(a))];
    cb = [i+idx+len(a) for i in range(0, len(b))]
    
    ca.reverse()
    
    co = [idx]
    
    co.extend(cb);
    co.extend(ca);
    
    return co;
    


def dump_wrl( points, coords, filename="out.wrl" ):
    fp = open('template/template.wrl.tpl');
    
    #tpl = fp.read();
    
    out = Template(fp.read())
    
    color = ["%0.2f, %0.2f, %0.2f" % (r,g,b) for _,_,_,b,g,r in points]        
    color = str.join("\n", color)

    points = ["%0.2f %0.2f %0.2f" % (x,y,z) for x,y,z,_,_,_ in points]    
    points = str.join(",\n", points)


    coords = str.join( "\n", ["%s -1" % str.join( " ", ["%d" % p for p in line ] ) for line in coords])
    
    
    out = out.substitute(dict(points=points,coords=coords,colors=color))
    
    fp = open(filename,"w")
    fp.write( out )
    fp.close()

    

    
#<    points  = []
    
    




if __name__ == '__main__':
    run()    
