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
@title control the pylatscan hardware. this script captures images with uvccapture
"""
import optparse
import subprocess
import time
import os

from pylatscan.model.control import Control


def grab_frame( options, filename ):
    cmd = [
        options.path,
        '-x%d' % options.width,
        '-y%d' % options.height,
        '-o%s' % filename,
        '-d%s' % options.device,
        '-q%d' % 90,
        '-B%d' % 128,
        '-C%d' % 32,
        '-S%d' % 32,
        '-G%d' % 40
    ]

    proc = subprocess.Popen( cmd, shell=False,stderr=subprocess.STDOUT,stdout=subprocess.PIPE)
    proc.wait()


def main():
    parser = optparse.OptionParser("pylatscan_cli <options> <target>");
    parser.add_option("-d","--device", action = "store", type="string", dest="device", default="/dev/video0")
    parser.add_option("-t","--tty", action = "store", type="string", dest="port", default="/dev/ttyUSB0")
    parser.add_option("-x","--width", action = "store", type="int", dest="width", default="640")
    parser.add_option("-y","--height", action = "store", type="int", dest="height", default="480")
    parser.add_option("-s","--steps", action = "store", type="choice", choices = ['1','2','4','8'], dest="steps", default="4", help="steps per turn")
    parser.add_option("-p","--path", action = "store", type="string", default="/usr/bin/uvccapture", dest="path", help="path to uvcapture binary")
    
    (options, target) = parser.parse_args()
    
    if len(target) == 0:
        parser.error( "You need to provide a target directory" )
    
    
    target = target[0]    
    control = Control(options.port)
    steps   = int(options.steps)
    target  = str.rstrip( target, '/' )
    pfx    = time.strftime("%Y%m%d%H%M%S");
    
    control.reset();
    
    start = time.time();    
    max = 400/int(options.steps);
    
    for i in range( 0, max):
        #print "I: scanning %s of %s" % ( i, 400/steps)
        control.write(2);

        filename = os.path.realpath('%s/left_%s_%04d.jpg' % ( target, pfx, i ))
        grab_frame( options, filename )
        print "I: %03d/%d recorded %s" % ( i, max, filename )
        
        control.write(3);
        control.write(4);

        filename = os.path.realpath('%s/right_%s_%04d.jpg' % ( target, pfx, i ))
        grab_frame( options, filename )
        
        print "I: %03d/%d recorded %s" % ( i, max, filename )
        
        control.write(5);
        control.write(6);

        filename = os.path.realpath('%s/color_%s_%04d.jpg' % ( target, pfx, i ))
        grab_frame( options, filename )
        print "I: %03d/%d recorded %s" % ( i, max, filename )

        control.write(7);

        for i in range(0,steps):
            control.step()
    
    duration = time.time() - start

if __name__=="__main__":
    main()





