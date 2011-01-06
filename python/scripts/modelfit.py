#!/usr/bin/env python
# model fitting script: fits two pointcloud .asc files
import numpy as np
from scipy import interpolate
import csv


def load_points( filename):
    points =  np.array( list( csv.reader( open(filename) ) ) ).astype( np.float64 )
    
    return points[np.nonzero(points[:,0])]

# a, b are arrays of angles
# return two arrays of indexes
def find_overlaps( a, b ):
    overlaps = []
    
    # filter out zero angles
    
    if len(b) == 0 or len(a) == 0:
        return overlaps

    a = a[np.nonzero(a)]
    b = b[np.nonzero(b)]
    
    for i, angle in enumerate( a ):
        difs = np.abs( b - angle )
        
        #print len(difs), 'DIFS'
        minv = np.min( difs )
        
        if minv < 0.1:
            if minv == 0:
                print "minv 0, why"
            idx = list( difs ).index(minv)
            overlaps.append( (i, idx) )
            
    #print "found %d overlaps" % len( overlaps )
    return overlaps
        


def distsquare( a, b ):
    return np.sum( np.hypot( (a[:,0]-b[:,0]), (a[:,1]-b[:,1]) ) )


# from each p   oint in a and b
# figure out the distance 
def lsquare( a, b, max_iter=100 ):
    scale = 1.0
    
    sum   = distsquare( a, b )
    iter = 0;

    while True:
        b = b * scale
        
        #print "square", distsquare(a, b);
        
        if distsquare(a, b) > sum:
            return scale
        
        #print "scale", scale
        
        scale = scale + 0.001
        iter += 1
        if iter >= max_iter:
            print "Max iter reached", sum, scale
            return scale
    
    return scale


#def fitmodel( model_a, model_b ):
#    zs = np.unique(model_a[:,2]);
#    min_z, max_z = min( model_a[:,2] ) , max( model_a[:,2])
#
#    model_n = []
#    
#    for z in range(int(min_z), int(max_z)):
#        
#        #print "on z", z;
#        idx = np.where( model_a[:,2] == z )
#        #print len(idx)
#        
#        a = model_a[idx][:,(0,1)]
#        
#        #print len(a), 'A'
#
#        idx = np.where( model_b[:,2] == z )
#        b = model_b[idx]; # [:,(0,1)]
#        #print len(b), 'B'
#        
#        angles = ( np.arctan2( a[:,0], a[:,1] ), np.arctan2( b[:,0], b[:,1] ) )
#        overlaps = np.array(find_overlaps( angles[0], angles[1] ) )
#        
#        if( len(overlaps) > 0 ):
#            overlap_a = a[overlaps[:,0]]
#            overlap_b = b[overlaps[:,1]]
#            
#            
#            #print "calculating dist"
#            
#            f = lsquare( overlap_a, overlap_b );
#            
#            
#            # scale b
#            b[:,(0,1)] = b[:,(0,1)] * f;            
#            model_n.append( list(b) )
#        
#    return model_n;

def fitmodel( model_a, model_b ):
    zs = np.unique(model_a[:,2]);
    min_z, max_z = min( model_a[:,2] ) , max( model_a[:,2])
   
    model_n = []
    
    for z in range(int(min_z), int(max_z)):
        
        #print "on z", z;
        idx = np.where( model_a[:,2] == z )
        a = model_a[idx]

        idx = np.where( model_b[:,2] == z )
        b = model_b[idx]; # [:,(0,1)]
        
        angles = ( np.arctan2( a[:,0], a[:,1] ), np.arctan2( b[:,0], b[:,1] ) )
        overlaps = np.array(find_overlaps( angles[0], angles[1] ) )

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
            
            # multiply b with the interpolated indexes
            
            b[start:end,0] = b[start:end,0] * sx
            b[start:end,1] = b[start:end,1] * sy
            
            # remove points that are outside of a bounding box
            # defined by min(x),min(y) and max(x), max(y) in a
            # box = ( (min(a[:,0]), min(a[:,1])), (max(a[:,0]), max(a[:1])))
            
            model_n.append( list(b) )
        
    return model_n;


if __name__ == '__main__':
    print "load model a"
    a = load_points( 'right.asc');
    print "load model b"
    b = load_points( 'left.asc');
    
    print "fitting model b to a"
    n = fitmodel( a, b );
    
    

    out = []
    for lines in n:
        for point in lines:
            point =  str.join( ",", ["%0.2f" % p for p in point])
            out.append(point)
            
    out = str.join( "\n", out )
    #n = [l for l in[y for y in n]]
    #
    #print n[0]
    #
    ##n = ["%0.2f,%0.2f,%0.2f,%0.2f,%0.2f,%0.2f" % (x,y,z,r,g,b) for x,y,z in [line for line in n]]
    #n = str.join( "\n", n )
    
    #out = []
    print "writing to fitted.asc"
    #for z in n:
    #    out.extend(["%0.2f, %0.2f, %0.2f" % (l[0], l[0], l[0]) for l in z])

    output = open('fitted.asc',"w")
    output.write( out )
    output.close()

    #print str.join( "\n", out );    
        
    
    #print n[0]
    
    
    
