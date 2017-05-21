#! python3

import xml.etree.cElementTree as ET
import pprint
from collections import defaultdict

osm_file = "C:/Users/cguzm_000/Documents/udacity-projects/data/newyork.osm"
def count_tags(file):
    unique_tags = defaultdict(int)
    for event, elem in ET.iterparse(file, events=("start",)):
        unique_tags[elem.tag] += 1
    return unique_tags

pprint.pprint(count_tags(osm_file))
    
