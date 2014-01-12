PyLatScan - Python Laser Triangulation Scanning
===============================================

A set of python scripts for 3d scanning

installation
------------

You can install pylatscan by running setup.py in the 
python directory of this repository. 

The following commands are then available:

* pylatscan_cli  - Commandline tool to controll the arduino and record pictures
* pylatparse_cli - Commandline tool that processes a directory of scanned images into a pointcloud
* pylatscan      - A Gtk/Glade wrapper around pylatparse_cli
* pylatparse     - A Gtk/Glade wrapper around pylatparse

Installing the scripts globally works like this:

    git clone https://github.com/mvhenten/pylatscan
    cd pylatscan/python
    sudo python setup.py install

how it works
------------

__note: I do not own the scanner hardware anymore, but I've been receiving a
number of questions on how to operate one. I'll try and explain here__

Laser triangulation is relatively straight forward: by projecting a laser line onto
the model at a 30 degree angle, the countours of the object can be extracted from
an picture taken relatively easy. By rotating the object, and taking many pictures,
these countours can be combined into a 3d point cloud.

After constructing a 3d point cloud, a mesh is constructed. [meshlab](http://meshlab.sourceforge.net/)
is used to construct the mesh. The point cloud should not contain too much noise
for this to work.

### 1. Step one: take (many) pictures

The script `pylatscan_cli` is used to control a stepper motor, two lasers and a led "flash light"
to take pictures automatically. The script `pylatscan` is a Glade/GTK wrapper around this
commandline script, so a non-techie can operate the scanner. Pictures are taken using a webcam,
so the better your webcam, the better the final results. You should carefully calibrate the
webcam using some thing like [guvcview](http://guvcview.sourceforge.net/), it can be installed
on Ubuntu using `apt-get install guvcview`.

The process is very sensitive to changes in lighting conditions, so you should block out any environmental
light wile scanning. A third picture is taken on every rotation using a led light, providing colors
to the eventual point cloud.

Not that the extra laser and color pictures are actually optional, some models wil scan just fine with
only one laser. Our stepper motor provided 400 steps, more steps will increase scanning time but improves
the accuracy. It took us less then 10 minutes to scan a small clay model using this setup.

### 2. Step two: process the scanned images

After running the scanner, you will end up with a directory of 1200 images. The script `pylatparse_cli`
is used to convert the images into a point cloud.

Two lasers provide two point clouds, one from each side, giving us more raw points to work with. `pylatparse`
will try to merge the two point clouds as good as possible.


These pointclouds need to be merged into one point cloud. The point clouds will not match 100% in size,
so some extra interpolation steps are needed.

hardware
--------

Hardware development is currently in progress. I've written an [informal description](http://amsterdam.fablab.nl/node/3363/) 
of the hardware developemnt on the FabLab amsterdam website.

Furthermore, there's picures on [flicr](http://www.flickr.com/photos/57913158@N05/) and 
[blueprints](https://github.com/mvhenten/pylatscan/tree/master/blueprint/Model4) of the scanner

contact
-------
You can contact me at matthijs (at) waag (dot) org
