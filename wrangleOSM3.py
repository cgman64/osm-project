#! python3

import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict

osm_file = "C:/Users/cguzm_000/Documents/udacity-projects/data/sample.osm"
def count_tags(file):
    unique_tags = defaultdict(int)
    for event, elem in ET.iterparse(file, events=("start",)):
        unique_tags[elem.tag] += 1
    return unique_tags


LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version',
               'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset',
              'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

def shape_element(element, node_attr_fields=NODE_FIELDS,
                  way_attr_fields=WAY_FIELDS, problem_chars=PROBLEMCHARS,
                  default_tag_type='regular'):
    '''Clean and shape node or way XML element to python dict'''

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = [] # Handle secondary tags the same way for both node and way elements
    # MY CODE HERE
    if element.tag == 'node':
        for k in element.attrib:
            if k in node_attr_fields:
                node_attribs[k] = element.attrib[k]
        if len(element.findall('tag')) > 0:
            for tag in element.iter('tag'):
                problem = PROBLEMCHARS.search(tag.attrib['k'])
                if problem:
                    print(problem.group())
                    continue
                tag_dict = {}
                tag_dict['id'] = element.attrib['id']
                tag_dict['value'] = tag.attrib['v']
                # Dealing with colons
                m = LOWER_COLON.search(tag.attrib['k'])
                if m:
                    key_split = tag.attrib['k'].split(":")
                    key = ':'.join(key_split[1:])
                    tag_dict['key'] = key
                    tag_dict['type'] = key_split[0]
                else:
                    tag_dict['key'] = tag.attrib['k']
                    tag_dict['type'] = default_tag_type
                tags.append(tag_dict)
        
        return {'node': node_attribs, 'node_tags': tags}
    
    elif element.tag == 'way':
        for k in element.attrib:
            if k in way_attr_fields:
                way_attribs[k] = element.attrib[k]
        if len(element.findall('tag')) > 0:
            for tag in element.iter('tag'):
                problem = PROBLEMCHARS.search(tag.attrib['k'])
                if problem:
                    print(problem.group())
                    continue
                tag_dict = {}
                tag_dict['id'] = element.attrib['id']
                # Dealing with colons
                m = LOWER_COLON.search(tag.attrib['k'])
                if m:
                    key_split = tag.attrib['k'].split(":")
                    key = ':'.join(key_split[1:])
                    tag_dict['key'] = key
                    tag_dict['type'] = key_split[0]
                else:
                    tag_dict['key'] = tag.attrib['k']
                    tag_dict['type'] = default_tag_type
                tag_dict['value'] = tag.attrib['v']    
                
                tags.append(tag_dict)
        if len(element.findall('nd')) > 0:
            position = 0
            for nd in element.iter('nd'):
                node_dict = {}
                node_dict['id'] = element.attrib['id']
                node_dict['node_id'] = nd.attrib['ref']
                node_dict['position'] = position
                way_nodes.append(node_dict)
                position += 1
        
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

def test():
    for element in get_element(osm_file, tags=('node', 'way')):
        el = shape_element(element)
        pprint.pprint(el)
        
        

test()



