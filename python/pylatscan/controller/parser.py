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

#import pylatscan
#import pylatscan.pointcloud_gui as gui
import pygtk
import gobject
import gtk
import glib
import gtk.glade
import os
import glob
import subprocess as sp
import time
import optparse


def main():
    """process all files in a directory and output a pointcloud
        
        This script is a GUI wrapper around parser_cli.py
        
        @todo move looping an parsing into models
        @todo allow for red colored lasers
        @todo allow for scanning just left or right
        
        argument options Optparse object
        argument files Files to process as (left_images,right_images,color_images)
    """
    parser = optparse.OptionParser("pylatparse [options] <path>");
    parser.add_option("-f","--output-filename", action = "store", type="string", default="pointcloud", dest="filename", help="Output file")
    
    (options, args) = parser.parse_args()
    
    
    source_path = None
    
    if len(args) > 0:
        source_path = args[0]
    else:
        source_path = os.path.expanduser('~/Pictures')
        
    
    

    Main(source=source_path,filename=options.filename)

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
    pixbuf = None
    proc = None
    xml = None
    topleft = (0,0)
    
    current_safe_path = ''
    
    pixbuf_cache = {}
    
    sources = {
        'left':[],
        'right':[],
        'color':[]
    }
    
    events = []
    
    roi = [10, 10, 300, 220]

    def __init__( self, source=None, filename="pointcloud" ):
        width, height = 320, 240

        xmlpath =  os.path.abspath("%s/../../resources/glade/parser.glade" % os.path.dirname(__file__))        
        xml = gtk.glade.XML( xmlpath )
        self.xml = xml;
        
        self.xml.get_widget( 'main_window' ).connect("destroy", lambda w: gtk.main_quit())
        self.xml.get_widget( 'dialog_progress' ).connect("destroy", lambda w: self.on_cancel_processing(w))

        self.xml.signal_autoconnect({
            'on_fileselect_source_path_current_folder_changed': self.source_path_set,
            'on_hscale_image_select_change_value': self.on_slider_move,
            'on_button_process_cancel_clicked': self.on_cancel_processing,
            'on_button_record_clicked':    self.on_start_processing,
            'on_button_quit_clicked':   self.quit,
            'on_radio_image_source_left_toggled': self.on_toggle_source,
            'on_radio_image_source_color_toggled': self.on_toggle_source,
            'on_radio_image_source_right_toggled': self.on_toggle_source,
            'spin_roi_value_changed': self.on_spin_roi_change,
            'on_button_meshlab_clicked': self.open_meshlab,
        })
        
        self.xml.get_widget( 'frame_roi_settings' ).set_sensitive(False)
        self.xml.get_widget( 'frame_preview' ).set_sensitive(False)
        self.xml.get_widget( 'button_record' ).set_sensitive(False)
        self.xml.get_widget( 'button_meshlab' ).set_sensitive(False)
        self.xml.get_widget( 'entry_output_file').get_buffer().set_text(filename, 10)

        canvas = self.xml.get_widget('canvas')        
        
        self.pixmap = gtk.gdk.Pixmap(canvas.window, width, height)
        self.pixmap.draw_rectangle( canvas.get_style().white_gc, True, 0, 0, width, height )
        
        canvas = self.xml.get_widget('canvas')
        
        canvas.connect( 'expose_event', self.on_expose )
        canvas.connect( 'motion_notify_event', self.on_roi_changed )
        canvas.connect( 'button_press_event', self.on_canvas_click )

        canvas.add_events(gtk.gdk.EXPOSURE_MASK
                        | gtk.gdk.LEAVE_NOTIFY_MASK
                        | gtk.gdk.BUTTON_PRESS_MASK
                        | gtk.gdk.POINTER_MOTION_MASK
                        | gtk.gdk.POINTER_MOTION_HINT_MASK)

        
        self.xml.get_widget( 'fileselect_target_path' ).set_current_folder( os.path.expanduser('~/Desktop'))
        
        #print "Current folder: ", self.xml.get_widget( 'fileselect_target_path' ).get_current_folder()
        
        if source and os.path.isdir(source):
            path = self.xml.get_widget( 'fileselect_source_path' )
            path.set_current_folder(os.path.realpath(source))
        
        gtk.main()
        
    def open_meshlab( self, widget ):
        os.system('meshlab %s&' % self.current_safe_path);
        #self.xml.get_widget( 'button_meshlab' ).set_sensitive(False)
        
        
    def source_path_set( self, widget ):
        path = widget.get_current_folder()
        
        files = glob.glob( '%s/*.jpg' % path )
        

        self.sources['left'] = [n for n in files if os.path.basename(n).startswith('left')]
        self.sources['right'] = [n for n in files if os.path.basename(n).startswith('right')]
        self.sources['color'] = [n for n in files if os.path.basename(n).startswith('color')]

        if len(self.sources['left']) == 0 \
            or len(self.sources['right'])  == 0 \
            or len(self.sources['color']) == 0:

            self.set_status_bar("%s does not contain any 3d scanner images" % path )

            return;
        


        self.sources['left'].sort()
        self.sources['right'].sort()
        self.sources['color'].sort()
        
        self.load_pixmap(self.sources['left'][0])
        
        width  = self.pixbuf.get_width()
        height = self.pixbuf.get_height()

        
        #rect = gtk.gdk.Rectangle(0, 0, width, height)
        canvas = self.xml.get_widget( 'canvas' )
        
        canvas.set_size_request(width,height)
        #self.pixmap.set_size_request(width,height)

        self.pixmap = gtk.gdk.Pixmap(canvas.window, width, height)
        #self.pixmap.draw_rectangle( canvas.get_style().white_gc, True, 0, 0, width, height )

        self.roi = [40, 30, width-80, height-60]

        scale = self.xml.get_widget( 'hscale_image_select' )
        scale.set_range( 0, len(self.sources['left'])-1)

        self.xml.get_widget( 'spin_roi_top' ).set_range( 0, height )
        self.xml.get_widget( 'spin_roi_left' ).set_range( 0, width )
        self.xml.get_widget( 'spin_roi_width' ).set_range( 0, width )
        self.xml.get_widget( 'spin_roi_height' ).set_range( 0, height )
        
        t,l,w,h = self.roi

        self.xml.get_widget( 'spin_roi_top' ).set_value(t)
        self.xml.get_widget( 'spin_roi_left' ).set_value(l)
        self.xml.get_widget( 'spin_roi_width' ).set_value(w)
        self.xml.get_widget( 'spin_roi_height' ).set_value(h)

        self.cur_source = 'left'

        self.xml.get_widget( 'frame_roi_settings' ).set_sensitive(True)
        self.xml.get_widget( 'frame_preview' ).set_sensitive(True)
        self.xml.get_widget( 'button_record' ).set_sensitive(True)
        
        self.draw()

    def draw( self  ):
        width, height = 320, 240
        canvas = self.xml.get_widget('canvas')
        
        if not self.pixbuf:
            self.pixmap.draw_rectangle( canvas.get_style().black_gc, True, 0, 0, width, height )
        else:
            self.pixmap.draw_pixbuf( None, self.pixbuf, 0, 0, 0, 0, -1, -1 )
            
        top, left, width, height = [int(i) for i in self.roi]

        self.pixmap.draw_rectangle(canvas.get_style().white_gc, False, top,left,width,height)

        canvas.queue_draw()

    def load_pixmap( self, filename ):
        if filename not in self.pixbuf_cache.keys():
            self.pixbuf_cache[filename] = gtk.gdk.pixbuf_new_from_file( filename )

        self.pixbuf = self.pixbuf_cache[filename]
        
    def on_slider_move( self, widget, type=None, num=None ):
        idx = int(widget.get_value())
        
        self.load_pixmap(self.sources[self.cur_source][idx])
        self.set_status_bar(os.path.basename(self.sources[self.cur_source][idx]))
        
        self.draw()
        
    def set_status_bar( self, message ):
        s = self.xml.get_widget( 'statusbar_main' )
        s.push( s.get_context_id(message), message )
        
    def on_toggle_source( self, widget ):
        if widget.get_active():
            self.cur_source = widget.name.split( "_" )[-1]
            self.on_slider_move(self.xml.get_widget( 'hscale_image_select' ))
            
        
    def on_spin_roi_change( self, widget, pointer=None ):
        name = widget.name.split('_')[-1]
        idx = ['left', 'top', 'width', 'height'].index(name)
        
        self.roi[idx] = widget.get_value()        
        
        x,y,w,h = self.roi
        
        if name == "width":
            width = self.pixbuf.get_width()
            x = max(0,(width-w)/2)
        elif name == 'left':
            width = self.pixbuf.get_width()
            w = max(1, (width-x*2))
        elif name == 'top' or name == 'height':
            height = self.pixbuf.get_height()
            
            if ( y + h ) > height:
                h = max(1, height - y )
                

        self.set_roi((x,y,w,h))
        return False

    def on_roi_changed( self, widget, event ):
        x, y, mask = event.window.get_pointer()        
        top, left = self.topleft
        
        if mask & gtk.gdk.BUTTON1_MASK and self.pixmap != None:
            width = self.pixbuf.get_width()
            x_center = width/2
            
            if left < x_center:            
                w = (x_center - left)*2
            else:
                left = x_center-(left-x_center)
                w = abs((left - x_center)*2)
                
            self.set_roi((left, top, w, max(1, y-top)))

        self.draw()
        return True
    
    def set_roi( self, roi ):
        x,y,w,h = roi
        
        self.xml.get_widget( 'spin_roi_top' ).set_value(y)
        self.xml.get_widget( 'spin_roi_top' ).emit_stop_by_name('value-changed')
        self.xml.get_widget( 'spin_roi_left' ).set_value(x)
        self.xml.get_widget( 'spin_roi_left' ).emit_stop_by_name('value-changed')
        self.xml.get_widget( 'spin_roi_width' ).set_value(w)
        self.xml.get_widget( 'spin_roi_width' ).emit_stop_by_name('value-changed')
        self.xml.get_widget( 'spin_roi_height' ).set_value(h)
        self.xml.get_widget( 'spin_roi_height' ).emit_stop_by_name('value-changed')
            
        self.roi = [x,y,w,h]
        
        #self.roi[idx] = widget.get_value()        
        self.draw()        
        
    def on_canvas_click( self, event, widget ):
        x, y, mask = event.window.get_pointer()
        
        self.topleft = ( y, x )
        
        self.draw()
        return True
        

    def on_expose(self, widget, event):
        x , y, width, height = event.area
        widget.window.draw_drawable(widget.get_style().fg_gc[gtk.STATE_NORMAL],
                                    self.pixmap, x, y, x, y, width, height)
        return False        
        
    def update_preview( self, filename ):
        pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
        scaled = pixbuf.scale_simple(160,120,gtk.gdk.INTERP_NEAREST)
        
        canvas = self.xml.get_widget('canvas')
        
        canvas.window.draw_pixbuf( None, scaled, 0, 0, 0, 0, -1, -1, gtk.gdk.RGB_DITHER_NORMAL)
        
        canvas.window.show()
        canvas.show()

    def on_start_processing( self, widget ):
        dialog = self.xml.get_widget( 'dialog_progress' )
        self.xml.get_widget( 'main_window' ).set_sensitive(False)
        self.xml.get_widget( 'button_meshlab' ).set_sensitive(False)

        
        self.xml.get_widget( 'label_process' ).set_text('Start processing...')
        
        dialog.show()
        
        
        self.start_processing()
        
        return False
        
    def on_cancel_processing( self, widget ):
        dialog = self.xml.get_widget( 'dialog_progress' )
        self.xml.get_widget( 'main_window' ).set_sensitive(True)        
        self.xml.get_widget( 'button_meshlab' ).set_sensitive(False)



        if self.proc and self.proc.poll() is None:
            print "killing subprocess"
            self.proc.stdout.flush()
            self.proc.stdout.close()
            self.proc.kill()
            self.proc.terminate()
            self.proc.wait()

        for i in self.events:
            glib.source_remove(i)

        dialog.hide()
        
        
    def safe_filename(self,filename, basepath ):
        files = glob.glob( "%s%s%s*.wrl" % (basepath, os.sep, filename) )
        
        count = 1
        
        print files
        
        files.sort()
        
        if len( files ) > 0:
            num = files[-1].split('.')[0][-4:]
            
            print num
            
            if num.isdigit():
                count = int(num) + 1
            
        
        return "%s%04d" % ( filename, count )


    def start_processing( self ):
        script = os.path.realpath( '%s/parser_cli.py' % os.path.dirname(__file__));
        
        do_left = self.xml.get_widget('radiobutton_scan_left').get_active()
        do_right = self.xml.get_widget('radiobutton_scan_right').get_active()
        do_both = self.xml.get_widget('radiobutton_scan_both').get_active()
        
        #print "left, right, both?", do_left, do_right, do_both

        filename = self.xml.get_widget( "entry_output_file").get_text()
        basepath = self.xml.get_widget( 'fileselect_target_path' ).get_current_folder()
            
        path = "%s%s%s.wrl" % ( basepath, os.sep, self.safe_filename(filename,basepath) )
        
        left, top, width, height = [str(int(i)) for i in self.roi]
        

        cmd = [
            'python',
            '-u', script,
            '-x', left,
            '-y', top,
            '-w', width,
            '-g', height,
            '-f', path,
            self.xml.get_widget( 'fileselect_source_path' ).get_current_folder()            
        ]
        
        if do_both:
            #print "do both"
            cmd.extend(['-l','-r'])
        elif do_left:
            #print "do left"
            cmd.append('-r')
        elif do_right:
            #print "do right"
            cmd.append('-l')

        #
        #print str.join( ' ', cmd )
        
        self.current_safe_path = path
        
        self.set_status_bar( str.join( ' ', cmd ) )
        self.proc = sp.Popen(cmd,stdout=sp.PIPE)                

        self.events.append(glib.io_add_watch(self.proc.stdout, glib.IO_IN, self.status_processing))
        self.events.append(glib.io_add_watch(self.proc.stdout, glib.IO_HUP, self.stop_processing))
        
        
    def status_processing( self, fd, condition ):
        if condition == glib.IO_IN and not fd.closed and self.proc.poll() is None:
            line = fd.readline()

            if line.startswith('II'):
                i, total = [float(i) for i in line.split(' ')[1].split('/')]
                
                bar = self.xml.get_widget( 'progressbar_process' )
                
                bar.set_fraction( i/total )
                bar.set_text( os.path.basename(line.split()[-1]) )
            else:
                self.xml.get_widget( 'label_process' ).set_text(line)                
            return True
        else:
            return False
        
        
    def stop_processing( self, fd, condition ):
        #self.xml.get_widget( 'label_process' ).set_text("DONE!")
        dialog = self.xml.get_widget( 'dialog_progress' )
        
        self.xml.get_widget( 'button_meshlab' ).set_sensitive(True)
        self.xml.get_widget( 'main_window' ).set_sensitive(True)
        
        for i in self.events:
            glib.source_remove(i)
        
        print "killing subprocess"
        self.proc.stdout.flush()
        self.proc.stdout.close()

        self.proc.kill()
        self.proc.wait() # wait to kill of the zombies
        
        dialog.hide()

        return False


    def quit( self, widget ):
        print "bye!"
        #self.stop_scanner()
        gtk.main_quit()


if __name__ == "__main__":
    main()    
