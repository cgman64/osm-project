#This script prepared my database as apython dictionary to
#extract data into CSV files.


import re
import xml.etree.cElementTree as ET

OSM_PATH = "C:/Users/cguzm_000/Documents/udacity-projects/" \
            "data/preparingForDatabaseExample.xml"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

# Make sure the fields order in the csvs matches the column order
# in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version',
               'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset',
              'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

mapping = { "St": "Street",
            "St.": "Street",
            "Rd": "Road",
            "Rd.": "Road",
            "Ave": "Avenue",
            "Ave.": "Avenue",
            "N": "North",
            "S": "South",
            "E": "East",
            "W": "West",
            "Hl": "Hill",
            "Ter": "Terrace",
            "Pkwy": "Parkway",
            "Sr": "State Road"
           }
           
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)           
sr_re = re.compile(r'\bSr\b', re.IGNORECASE)
def update_name(name, mapping):
    '''Locates and updates abbreviated street types 
    for each street name.'''
    m = street_type_re.search(name) #street type match object
    state_road = sr_re.search(name) #state road match object
    if m and m.group() in mapping.keys():
        name = street_type_re.sub(mapping[m.group()], name)
    if state_road:
        name = sr_re.sub(mapping[state_road.group()], name)
    return name
    
city_mapping = ['new york city', 'brooklyn', 'bronx', 'queens', 'staten island',
               'astoria', 'corona', 'elmhurst', 'flushing', 'forest hills', 'jamaica',
               'kew gardens', 'long island city', 'rego park', 'roosevelt island', 
               'sunnyside', 'woodside']

def update_city_name(name, mapping):
    if name.lower() in mapping:
        name = 'New York'
    return name

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def update_post(code):
    better_code = ''
    for e in list(code):
        if is_number(e):
            better_code += e
            if len(better_code) == 5:
                break
    return better_code
    
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
    # 
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
                #UPDATING STREETNAMES
                if tag.attrib['k'] == "addr:street":
                    tag_dict['value'] = update_name(tag.attrib['v'], mapping)
                #UPDATING CITY NAMES
                elif tag.attrib['k'] == "addr:city":
                    tag_dict['value'] = update_city_name(tag.attrib['v'], city_mapping)
                #UPDATING POSTCODES
                elif tag.attrib['k'] == "addr:postcode":
                    tag_dict['value'] = update_post(tag.attrib['v'])
                else:
                    tag_dict['value'] = tag.attrib['v']
                    
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
                #UPDATING STREETNAMES
                if tag.attrib['k'] == "addr:street":
                    tag_dict['value'] = update_name(tag.attrib['v'], mapping)
                #UPDATING CITY NAMES
                elif tag.attrib['k'] == "addr:city":
                    tag_dict['value'] = update_city_name(tag.attrib['v'], city_mapping)
                #UPDATING POSTCODES
                elif tag.attrib['k'] == "addr:postcode":
                    tag_dict['value'] = update_post(tag.attrib['v'])
                else:
                    tag_dict['value'] = tag.attrib['v']
                    
                tags.append(tag_dict)
		#OBTAINING POSITION FOR 'nd' TAGS
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


        
        
    
    








