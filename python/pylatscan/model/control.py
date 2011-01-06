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
@title 
"""
import serial
import time


class Control:
    def __init__( self, port='/dev/ttyUSB0' ):
        self.open( port )
        
    def __del__( self ):
        self.close()
        
    def open( self, port ):
        self.serial = serial.Serial(port)
    
    def step( self ):
        self.write(1)
        time.sleep(0.2)
        
    def reset( self ):
        #self.write(0)
        self.write(3)
        self.write(5)
        self.write(7)
        #time.sleep(0.5) # wait for the turn
    
    def write( self, cmd ):
        self.serial.write( "%d" % cmd )
        time.sleep(0.1)
        
    def close( self ):
        self.serial.close()

#class Control:
#    def __init__( self, port='/dev/ttyUSB0' ):
#        return None
#        
#    def open( self, port ):
#        return 0
#    
#    def step( self ):
#        return 0
#        
#    def reset( self ):
#        return 0
#    
#    def write( self, cmd ):
#        return 0
#    
#    def close( self ):
#        return 0
