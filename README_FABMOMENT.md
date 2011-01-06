### 1. Introduction

At the Waag Society, and Fablab Amsterdam, together with Miguel Jimenez and
Karim Amhali I have developed a 3d laser triangulation scanner.

[![][1]][2]

   [1]: http://farm6.static.flickr.com/5009/5329957324_157f7afec9.jpg

   [2]:
http://www.flickr.com/photos/57913158@N05/5329957324/in/set-72157625634848655/

A short introduction into 3d scanning can be found [ here][3],  also, the
following [ presentation][4] contains lots of useful information. The whole
setup is built around a webcam, a rotation platform and a focussed line laser.

   [3]: http://www.google.com/url?q=http%3A%2F%2Fen.wikipedia.org%2Fwiki%2F3D_
scanner%23Triangulation&sa=D&sntz=1&usg=AFQjCNG7AFVfDIuFWVbPSm5XPs-F5StGZA

   [4]: http://www.google.com/url?q=http%3A%2F%2Fwww.slideshare.net%2Fdlanman
%2Fbuild-your-own-3d-scanner-the-mathematics-of-3d-
triangulation-1882923&sa=D&sntz=1&usg=AFQjCNEg9H0aezBNw7Tkk8iuRo3gijdxJw

By taking pictures of the object from each angle while project the laser at
the object under a know degree, we can determine the position of points in
space by measuring the distance of the laser line from the center of the
projection.

In our final design of the scanner, we decided to add a number of
improvements, such as an arduino controlled rotary platform and a second laser
projecting at the opposite angle, to capture more detail and fill possible
gaps caused by self-casting shadows from the object.

You can find software and some more resources at the follow url: [
https://github.com/mvhenten/pylatscan][5]

   [5]: http://www.google.com/url?q=https%3A%2F%2Fgithub.com%2Fmvhenten%2Fpyla
tscan&sa=D&sntz=1&usg=AFQjCNEw4Kp_SM-u147iTIWFZ1HA3rGmGA

This document describes in somewhat more detail the construction of a body for
the 3d scanner out of plywood.

### 2. Considerations and partlist

The current hardware design for our prototype has evolved from extensive
testing with earlier setups. A laser angle of about 30 degrees seems to be the
most optimal position for the laser, and moving the laser to different angles
automatically might improve scan quality, but increases the complexity of the
overal design. Using a single laser proved to be insufficient, as objects
protubing too much in the horizontal plane tend to obscure the laser line
under certain circumstances. Therefore, a secondary laser was added under the
opposite angle of -30 degrees.

Fitting the lasers rigidly as to stay in place during transport is vital for
the usability of the scanner, since calibrating the whole setup is crucial in
order to produce good results, but can be quite cumbersome.

The lense of our camera must be centered at the exact center of the rotation,
but moving the camera up and own or closer to the object is needed to scan
different sized objects, and to move the focus point of the camera to the
vertical center of each object as much as possible ( to produce the best
results, an almost âorthogonal projectionâ is the best kind of input.)

Earlier designs used plexiglass, this current design, however, uses plywood as
the base material. Plywood is nice to work with, since you can cut, drill and
sand it into shape very easily, using both the shopbot and more conventional
tools such as a chisel and a hammer. This means the overall material is more
flexible and you can work around small mistakes or omissions in the design.

#### 2.1 Platform construction - partlist

Some of the bolts and screws could be exchanged for other parts you may have
lying around - it just happened to be the pieces we could get our hands on.
The SVG files for the shopbot also contain holes for the bolts, so keep that
in mind when taking different sizes.

The M6 pins may not have been ideal in this case, since a thicker guiding may
provide more stability.

##### partlist:

  1. 19mm plywood. dimensions of the platform are around 40x50mm and you need
two sheets

  2. âStandardâ 40mm âflightcaseâ or âtool caseâ suitcase

  3. about 50mm of 10M steel bar

  4. about 25mm of 6M screw wire

  5. one long 6M bold ( I found 12 cm the longest I managed to find )

  6. two long 6M pins ( The kind with a cap on the end )

  7. âdraai tappenâ ( or wood pivot, the kind you can slam into a piece of
wood )

  8. various bolts, nuts in 10M/6M

  9. 2mm round- head wood screws

#### 2.2 Scanner hardware  - partlist

Unfortunately the part number of the original stepper used in our prototypes
got lost, but Iâll assume the farnel part will do just fine. Also, some
exact details ( such as the type of white leds ) got lost as they were not
picked by me. The led mount is made of a plexiglass scrap and hot glue. At the
current time, I donât have any connection schematics but I will provide them
as soon as I have constructed the final prototype.

  1. 2 Green line lasers with focus ring ( [ LC532-5-3-F(16x65)][6] from [
laserfuchs.de][7] )

  2. 1 Logitech Webcam Pro 9000

  3. 1 Arduino board

  4. 1 Arduino motorshield

  5. 1 Stepper engine, 400 steps (for example ST2818S1006-B from Farnell)

  6. 6 bright white leds

  7. wires to connect everything

   [6]: http://www.google.com/url?q=http%3A%2F%2Fwww.laserfuchs.de%2Fproduct_i
nfo.php%2Finfo%2Fp87_Linienlaser-532nm--5mW--Laser-Klasse-1--2-7---3-3--
16x65mm---90-deg-.html%2FXTCsid%2Fa6f3d14cd24ed139f5aa08fcee168dff&sa=D&sntz=1
&usg=AFQjCNGlUFHv9lLAlTXCdGHvOogBAzBddg

   [7]: http://www.google.com/url?q=http%3A%2F%2Flaserfuchs.de&sa=D&sntz=1&usg
=AFQjCNFusev7NIirbdZRVWXnEJP1qIzUvA

#### 2.3 Schematics, blueprints

Since this project is under active developments, I cannot be bothered with
providing zipfiles, but everything will be provided [ here][8].

   [8]: http://www.google.com/url?q=https%3A%2F%2Fgithub.com%2Fmvhenten%2Fpyla
tscan&sa=D&sntz=1&usg=AFQjCNEw4Kp_SM-u147iTIWFZ1HA3rGmGA

The shopbot cutter we used was a 6 mm, which is pretty precise. The design
does not include any depth-milling, but smaller is better, since more precise.
The 6mm cutter just happened to be on the machine when I used it.

### 3. Construction

To explore the capabilities of the shopbot, I designed a âsnap fitâ laser
mount and platform fix that could be cut out of one piece of plywood and put
together as an IKEA package.

The platform consists of three layers: top, middle and bottom. The middle
layer can be used to guide cables and provides extra stabiltiy to the laser
mounts,  the bottom layer is for finishing and fixing the electronics. Overall
dimensions were choosen to be able to fit into a standard size suitcase, in
our case the biggest affordable aluminum suitcase we could buy at a local
hardware store. However, to be honest, each layer was designed along the way
in an iterative process.

#### 3.1 The Mark One

[![][9]][10]

   [9]: http://farm6.static.flickr.com/5209/5329341383_f5c53cf2c8.jpg

   [10]:
http://www.flickr.com/photos/57913158@N05/5329341383/in/set-72157625634848655/

Once the cutting was done, I constructed a camera mount out of plywood and
some large bolts that could be moved up and down by turning a screw. A strong
motorcycle spring provides some rigidity for t his construction, and it proved
to be rather stable.  I used standard bolts so I could fix the bolt heads
easily in a cavity on the bottom sinde of the the second layer. All this was
done by hand, improvizing along the way, but most of this work found itâs
way into the second attempt. Remember to keep a small chisel at hand for this
type of work! plywood is excellent to work with in this way :-)

[![][11]][12]

   [11]: http://farm6.static.flickr.com/5050/5329952168_bab2f60079.jpg

   [12]:
http://www.flickr.com/photos/57913158@N05/5329952168/in/set-72157625634848655/

Once this was finished, I started to fix the lasers on their mounts, this is
where I realised something had gone wrong in the milling - the cavities for
the lasers were too large. I finally found out that this was caused by the
transition from inkscape SVG to illustrator, for some strange reason. This can
be avoided by using .eps as an intermediate format.

[![][13]][14]

   [13]: http://farm6.static.flickr.com/5284/5329955202_b981f60c31.jpg

   [14]:
http://www.flickr.com/photos/57913158@N05/5329952168/in/set-72157625634848655/

I improvised again, by drilling 12mm holes into the other side of the mounts.
( it is very important to do a precise job here, since the laser angles must
be know and exact! ). I calibrated and ensured that the lasers were at a
straight 30 degree angle by switching them on. The two lines should merge at
exactly the center of your rotary platform! Again, some of this was improvised
in the first attempt, for example by adding a layer of black ducktape around
the laser casing to allow for more grip.

[![][15]][16]

   [15]: http://farm6.static.flickr.com/5210/5329344727_983b49b84f.jpg

   [16]:
http://www.flickr.com/photos/57913158@N05/5329344727/in/set-72157625634848655/

After this, it was time to fix the camera onto the mount. The packaging of the
9000 pro is not the most ideal for this setup, as it is hard to center the
lens and keep the whole thing straight and horizontal. One important thing to
do here is to switch on the lasers and camera, and keep looking at the
picture. Iâve written a small python script that shows a line trough the
center of the image, and while reassuring that everything stays straight and
centered by looking at the screen, I fixed both cameraâs, laser and platform
in one go.

[![][17]][18]

   [17]: http://farm6.static.flickr.com/5084/5329345459_36a9d5390a.jpg

   [18]:
http://www.flickr.com/photos/57913158@N05/5329345459/in/set-72157625634848655/

#### 3.2 Lessons learned: the Mark II

From the inital built, I learned that:

  1. The shopbot is much more precise then I had anticipated. donât hand-
drill. trust the shopbot!

  2. The camera mount works pretty reliable for up-and-down movement. However,
moving along the Z axis is a very nice to have, since itâll allow for
scanning small objects.

  3. The snap-fit approach works pretty nice, and plywood is sturdy anough for
this purpose

Altough the âMark Oneâ can be used within the project I intended it for,
Iâve started work on an improved design ( this time without the scaling bug
) that will actually fit the suitcase as intended.

I started out by making a constructive test of a Z-Y axis mount, much like a
CNC milling machine provides.

[![][19]][20] [![][21]][22]

   [19]: http://farm6.static.flickr.com/5281/5329962074_13ec42f365.jpg

   [20]:
http://www.flickr.com/photos/57913158@N05/5329962074/in/set-72157625634811369/

   [21]: http://farm6.static.flickr.com/5008/5329348537_6a85fbb61a.jpg

   [22]:
http://www.flickr.com/photos/57913158@N05/5329348537/in/set-72157625634811369/

This mount eventually made it into the next design, the top layer already cut.

[![Assembling the ZY axis system - it's a fit!][23]][24] [![3d scanner
assembly][25]][26]

   [23]: http://farm6.static.flickr.com/5050/5329971272_309ce3d1c6.jpg

   [24]: http://www.flickr.com/photos/57913158@N05/5329971272/ (Assembling the
ZY axis system - it's a fit! by mvhenten, on Flickr)

   [25]: http://farm6.static.flickr.com/5170/5329357199_c972149dd0.jpg

   [26]: http://www.flickr.com/photos/57913158@N05/5329357199/ (3d scanner
assembly by mvhenten, on Flickr)

...more to follow!

