#!/usr/bin/env python

# Creates images in the style of David Kaminsky (http://www.davidkaminsky.com/david/) where
# one row of vertical pixels is stretched out to create an image with a series 
# of horizontal lines.
#
# Usage:
# kaminsky.py photo.jpg 289 16/9

from PIL import Image
import sys

if len(sys.argv) != 4:
    print("This script requires the following arguments:")
    print("kaminsky.py <image_filename> <y-coordinate of selected pixels> <a/b: output image aspect ratio expressed as fraction>")
    exit(0)

im = Image.open(sys.argv[1])
selection = int(sys.argv[2])
ratio = sys.argv[3]

fraction = ratio.split('/')
if len(fraction) == 2:
    numerator = int(fraction[0])
    denominator = int(fraction[1])
else:
    print("Aspect ratio is not in a valid format. Using default format of 16/9.")
    numerator = 16
    denominator = 9    

width = im.size[0]
height = im.size[1]

if selection > (width - 1) or selection < 0:    
    selection = 0

box = (selection, 0, selection+1, height)
region = im.crop(box)

copy_size = (height * numerator/denominator, height)
copy = Image.new(im.mode, copy_size)
x = 0
while x < copy_size[0]:
    b = (x, 0)
    copy.paste(region, b)
    x += 1

copy.show()

