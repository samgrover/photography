#!/usr/bin/env python

# A helper script for uploading my photos to Tumblr as draft posts. Take a photo
# as input and asks some questions whose answers which are then used to
# determine the final uploaded draft post.
#
# Usage:
# tumpostphoto.py /path/to/photo.jpg

import sys
import json
import os.path
from datetime import datetime as dt
from datetime import date
from ConfigParser import SafeConfigParser
import pytumblr

# Utils
def printjson(json_string):
    print json.dumps(json_string, indent=4)

# Date formatting functions from:
# http://stackoverflow.com/questions/5891555/display-the-date-like-may-5th-using-pythons-strftime
def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))

# Main
if __name__ == "__main__":
    if len(sys.argv) == 1:
        print "This script requires at least one filename argument."
        exit(0)
    
    parser = SafeConfigParser()
    parser.read(os.path.expanduser('~/config/tumblr.ini'))
    
    consumer_key = parser.get('consumer', 'key')
    consumer_secret = parser.get('consumer', 'secret')
    
    oauth_token = parser.get('oauth', 'token')
    oauth_secret = parser.get('oauth', 'secret')
    
    blog_name = parser.get('blog', 'name')
    
    # Authenticate via OAuth
    client = pytumblr.TumblrRestClient(consumer_key, consumer_secret, oauth_token, oauth_secret)
    
    print 'Processing files:'
    filenames = sys.argv[1:]
    for a_filename in filenames:
        print '    ' + a_filename
    
    # Ask about camera
    camera = raw_input('\nLeica, iPhone 6s, Nikon FM10, Nikon D70s, Bessa, or Other? (L/i/f/d/b/o): ')
    if len(camera) == 0:
        camera = 'Leica'
    
    date_string = ''
    camera_tags = []
    camera = camera.upper()
    if camera[0] == 'L':
        # Get date and focal length from first filename
        # Assumes photo is named like: 20151209-L1002761-35 mm-Tumblr.jpg
        filename_for_info = os.path.basename(filenames[0])
        filename_parts = filename_for_info.split('-')
        
        focal_length_string = ''.join(filename_parts[2].split(' '))
        # If it is a panorama, compute focal length using next part
        if focal_length_string == "Pano":
            focal_length_string = ''.join(filename_parts[3].split(' '))
        
        # Extract and format date, so '20151209' becomes '9th December, 2015'
        the_date = dt.strptime(filename_parts[0], "%Y%m%d").date()
        date_string = custom_strftime('{S} %B, %Y', the_date)
        
        camera_tags = ['Leica M', focal_length_string]
    elif camera[0] == 'I':
        camera_tags = ['iPhone 6s']
    elif camera[0] == 'F':
        camera_tags = ['Nikon FM10', '50mm', 'Film']
    elif camera[0] == 'D':
        camera_tags = ['Nikon D70s', '18-70mm']
    elif camera[0] == 'B':
        camera_tags = ['Voigtlander Bessa r2a', '50mm', 'Film']
    elif camera[0] == 'O':
        camera_tags = []
        
    # Ask if street photography
    street_tags = []
    street = raw_input('\nStreet Photography? (Y/n): ')
    if len(street) == 0 or street[0].upper() == 'Y':
        street_tags.append('Street Photography')
    
    computed_tags = 'Computed tags: ' + ', '.join(camera_tags)
    if len(street_tags) != 0:
        computed_tags += ', ' + ', '.join(street_tags)
    
    print computed_tags
    if date_string != '':
        print 'Extracted date: ' + date_string
    
    # Ask for tags
    tags = []
    raw_tags = raw_input('\nEnter additional tags separated by commas:\n').split(',')
    for a_tag in raw_tags:
        cleaned_up_tag = a_tag.lstrip().rstrip()
        if len(cleaned_up_tag) > 0:
            tags.append(cleaned_up_tag)
    
    # Process all tags
    tags.extend(street_tags)
    tags.extend(camera_tags)
    
    # Create Instagram/Ello tags
    instagram_tags = []
    for a_tag in tags:
        transformed_tag = ''.join(t.capitalize() for t in a_tag.split(' '))
        instagram_tags.append('#' + transformed_tag)
    
    # Add tumblr specific tags
    tumblr_tags = ['Photographers on Tumblr', 'Original Photographers']
    tags.extend(tumblr_tags)
    
    # Ask for caption
    caption = raw_input('\nEnter caption:\n')
    if len(caption) > 0:
        caption = caption + ' ' + date_string + '.'
    
    print
    print 'Final tags are:\n' + ', '.join(tags)
    print 'Instagram tags are:\n' + ', '.join(instagram_tags)
    print 'Full caption is:\n' + caption.lstrip().rstrip()
    
    # Upload confirmation
    ok = raw_input('\nUpload? (Y/n): ')
    if len(ok) == 0 or ok[0].upper() == 'Y':
        print "Uploading draft..."
        output = client.create_photo(blog_name, state='draft', tags=tags, data=filenames, caption=caption)
        printjson(output)
    
    print 'All drafts at: https://www.tumblr.com/blog/' + blog_name + '/drafts'
