#! python3

import xml.etree.cElementTree as ET
import pprint
from collections import defaultdict

osm_file = "C:/Users/cguzm_000/Documents/udacity-projects/data/bronx.osm"
def count_tags(file):
	'''Counts all the tags in an XML document and returns a dictionary'''
    unique_tags = defaultdict(int)
    for event, elem in ET.iterparse(file, events=("start",)):
        unique_tags[elem.tag] += 1
    return unique_tags

pprint.pprint(count_tags(osm_file))

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def key_type(element, keys):
	'''Counts number of key types'''
    if element.tag == "tag":
        
        if lower.search(element.attrib['k']):
            #print(element.attrib['k'])
            keys["lower"] += 1
        elif lower_colon.search(element.attrib['k']):
            #print(element.attrib['k'])
            keys["lower_colon"] += 1
        elif problemchars.search(element.attrib['k']):
            #print(element.attrib['k'])
            keys["problemchars"] += 1
        else:
            #print(element.attrib['k'])
            keys["other"] += 1
    return keys

def process_map(filename):
	'''Inputs number of key types in a dictionary format.'''
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys
    
