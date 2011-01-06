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
@title Graphical interface to control the pylatscan scanner.
        This script simply wraps the commandline script pylatscan.
"""
import pygtk
import gobject
import gtk
import glib
import gtk.glade
import os
import glob
import subprocess as sp
import time

from pylatscan.model.control import Control


def main():
    Main()

""" utility function: populate a combobox with items non-trivially """
def gtk_combobox_fill( items, combo ):
    list = gtk.ListStore(gobject.TYPE_STRING)
    
    for item in items:
        list.append([item])
        
    combo.set_model( list )
    
    cell = gtk.CellRendererText()
    
    combo.pack_start(cell, True)
    combo.add_attribute(cell, 'text', 0)
    
""" a user-friendly graphical front-end for the scan controller """
class Main(object):
    proc = None
    xml = None
    
    device_list = {
            'tty': [],
            'video': []
        }

    def __init__( self ):
        xmlpath =  os.path.abspath("%s/../../resources/glade/scanner.glade" % os.path.dirname(__file__))        
        xml = gtk.glade.XML( xmlpath )
        self.xml = xml;

        self.text = xml.get_widget( 'progress-textview' )
        self.progressbar = xml.get_widget( 'scan-progress' )
        
        
        xml.get_widget( 'main_stop' ).set_sensitive(False)
        
        
        self.video_combo = xml.get_widget( 'video-device-combo' )
        self.tty_combo = xml.get_widget( 'serial-device-combo' )
        self.degree_combo = xml.get_widget( 'scan-degree-combo' )
        
        self.device_list['video'] = glob.glob( '/dev/video*' )
        self.device_list['tty'] = glob.glob( '/dev/tty*' )
        self.device_list['tty'].extend(glob.glob('/dev/ttyUSB'))
        
        gtk_combobox_fill(  self.device_list['video'], self.video_combo )
        gtk_combobox_fill( self.device_list['tty'], self.tty_combo )
        
        for combo in (self.video_combo, self.tty_combo, self.degree_combo):
            combo.set_active(0)
            
        self.target_filechooser = xml.get_widget( 'target_path' )
        
        xml.signal_autoconnect({
            'on_main_quit_clicked': self.quit,
            'on_main_record_clicked': self.start_scanner,
            'on_main_stop_clicked': self.stop_scanner,
            'on_main_test_clicked': self.test_scanner
        })
        
        self.xml.get_widget( 'main_stop' ).set_sensitive(False)
        
        self._count = 0
        
        gtk.main()

    def start_scanner( self, widget ):
        self._count = 0
        buf = self.text.get_buffer().set_text('')

        video_dev   = self.device_list['video'][self.video_combo.get_active()]
        tty_dev     = self.device_list['tty'][self.tty_combo.get_active()]
        path        = self.xml.get_widget( 'target_path' ).get_current_folder()
        steps       = [1,2,4,8][int(self.xml.get_widget( 'scan-degree-combo' ).get_active())]
        #steps       = [steps]

        widget.set_sensitive( False )
        self.xml.get_widget( 'main_stop' ).set_sensitive(True)

        frame = self.xml.get_widget('scanner-settings-frame')
        frame.set_sensitive( False )

        #script = 'pylatscan_cli'        
        #script = os.path.realpath('%s/../run_scanner.py' % os.path.dirname(__file__));
        
        script = os.path.realpath( '%s/scanner_cli.py' % os.path.dirname(__file__));
        
        cmd = ['python', '-u', script, '-s%d'%steps, '-x', '640', '-y', '480', '-t', tty_dev, '-d', video_dev, path]
        
        print str.join( ' ', cmd )
        
        self.proc = sp.Popen(cmd,stdout=sp.PIPE)                
        glib.io_add_watch(self.proc.stdout, glib.IO_IN, self.update_status)
        glib.io_add_watch(self.proc.stdout, glib.IO_HUP, self.stop_scanner)


    def stop_scanner( self, widget=None, foo=None):
        self.xml.get_widget( 'main_stop' ).set_sensitive(False)
        self.xml.get_widget( 'main_record' ).set_sensitive(True)
        
        if self.proc and self.proc.poll() is None:
            self.proc.stdout.flush()
            self.proc.stdout.close()
            self.proc.kill()
            self.proc.terminate()
            self.proc.wait()
        
        frame = self.xml.get_widget('scanner-settings-frame')        
        frame.set_sensitive( True )
        return False
    
    def test_scanner( self, widget = None ):
        self.xml.get_widget( 'main_stop' ).set_sensitive(False)
        self.xml.get_widget( 'main_record' ).set_sensitive(False)

        tty_dev = self.device_list['tty'][self.tty_combo.get_active()]
        
        control = Control( tty_dev )
        control.reset();
        
        control.write(0)
        time.sleep(3)
        
        control.close()
        
        self.xml.get_widget( 'main_stop' ).set_sensitive(True)
        self.xml.get_widget( 'main_record' ).set_sensitive(True)
        return False
        
    def update_status( self, fd, condition ):
        if condition == glib.IO_IN and not fd.closed and self.proc.poll() is None:
            #print "done"
            line = fd.readline()
            
            pieces = line.split(' ')
            filename = str.strip(pieces[-1]) # os.path.realpath(pieces[-1])
            idx,total = str.strip(pieces[1]).split('/');
            
            self.update_preview( filename )
            
            
            #buf = gtk.gdk.pixbuf_new_from_file(filename)
            #self.xml.get_widget( 'canvas' ).set_from_pixbuf(buf)
            
            buf = self.text.get_buffer()
            buf.insert(buf.get_start_iter(), line)
            self.progressbar.set_fraction(float(idx)/float(total))
                        
            self.progressbar.set_text( 'Scanning %s/%s' % (idx,total) )            
            return True
        else:
            return False
        
    def update_preview( self, filename ):
        pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
        scaled = pixbuf.scale_simple(160,120,gtk.gdk.INTERP_NEAREST)        
        self.xml.get_widget('canvas').set_from_pixbuf(pixbuf)

    def quit( self, widget ):
        self.stop_scanner()
        gtk.main_quit()


if __name__=="__main__":
    main()
