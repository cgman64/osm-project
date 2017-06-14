
# coding: utf-8

# # Project 3 - Wrangle OpenStreetMap
# 
# Christian Guzman
# 
# June 2017

# In[1]:

import csv
import codecs
import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict
import os

import cerberus

import schema


# In[2]:

#Main OSM
OSM_FILE = "C:/Users/cguzm_000/Documents/udacity-projects/data/newyork.osm"


# In[3]:

osm_file = "C:/Users/cguzm_000/Documents/udacity-projects/data/sample.osm"

SCHEMA = schema.schema
NODES_PATH = "data/nodes.csv"
NODE_TAGS_PATH = "data/nodes_tags.csv"
WAYS_PATH = "data/ways.csv"
WAY_NODES_PATH = "data/ways_nodes.csv"
WAY_TAGS_PATH = "data/ways_tags.csv"

# In[51]:

#AUDITING STREET NAMES
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place",
            "Square", "Lane", "Road", "Trail", "Parkway", "Commons"]
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


# In[100]:

pprint.pprint(dict(audit(osm_file)))


# In[53]:

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

def update_name(name, mapping):
    m = street_type_re.search(name)
    if m and m.group() in mapping.keys():
        name = street_type_re.sub(mapping[m.group()], name)
    return name


# In[101]:

def test():
    for st_type, ways in audit(osm_file).iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            if name is not better_name:
                print name, "=>", better_name
test()


# ## Updating "Sr" to "State Road"
# 
# Some of the adresses contained the abbreviation **Sr** which stands for **State Road**.

# In[102]:

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

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


for element in get_element(osm_file, tags=('node','way')):
    for tag in element.iter("tag"):
        if tag.attrib['k'] == "addr:street":
            print update_name(tag.attrib['v'], mapping)
            


# In[103]:

def test():
    for st_type, ways in audit(osm_file).iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            if name is not better_name:
                print name, "=>", better_name

test()


# ## Auditing Postal Codes

# In[122]:

postal_re = re.compile(r'\d{5}', re.IGNORECASE)

def key_type(element, keys):
    if element.attrib['k'] == "addr:postcode":
        if postal_re.search(element.attrib['v']):
            #print(element.attrib['v'])
            keys["5-digit postal"] += 1
        else:
            #print(element.attrib['v'])
            keys["other"] += 1
    return keys

def process_map(filename):
    keys = {"5-digit postal": 0, "other": 0}
    for element in get_element(filename):
        for tag in element.iter("tag"):
            keys = key_type(tag, keys)

    return keys

process_map(osm_file)


# In[58]:

s = '123RANDOM45WALK456'
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


# In[59]:

update_post(s)


# ## Auditing City Name

# In[105]:

cities = defaultdict(int)
for element in get_element(osm_file):
    if element.tag == "node" or "way":
        for tag in element.iter("tag"):
            if tag.attrib['k'] == "addr:city":
                cities[tag.attrib['v']] += 1
pprint.pprint(dict(cities))
                


# In[111]:

city_mapping = ['new york city', 'brooklyn', 'bronx', 'queens', 'staten island',
               'astoria', 'corona', 'elmhurst', 'flushing', 'forest hills', 'jamaica',
               'kew gardens', 'long island city', 'rego park', 'roosevelt island', 
               'sunnyside', 'woodside']

def update_city_name(name, mapping):
    if name.lower() in mapping:
        name = 'New York'
    return name


for element in get_element(osm_file, tags=('node','way')):
    for tag in element.iter("tag"):
        if tag.attrib['k'] == "addr:city" and tag.attrib['v'].lower() in city_mapping:
            better_name = update_city_name(tag.attrib['v'], mapping=city_mapping)
            print tag.attrib['v'],"=>", better_name


# In[123]:

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version',
               'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset',
              'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


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

def test_shape_element():
    i = 0
    for element in get_element(osm_file, tags=('node', 'way')):
        el = shape_element(element)
        pprint.pprint(el)
        i += 1
        if i == 2000:
            break


# In[63]:

def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# In[125]:

def main_function(file_in, validate):
    '''Iteratively process each XML element'''
    
    with codecs.open(NODES_PATH, 'w') as nodes_file,          codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file,          codecs.open(WAYS_PATH, 'w') as ways_file,          codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file,          codecs.open(WAY_TAGS_PATH,'w') as way_tags_file:
             
         nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
         node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
         ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
         way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
         way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

         nodes_writer.writeheader()
         node_tags_writer.writeheader()
         ways_writer.writeheader()
         way_nodes_writer.writeheader()
         way_tags_writer.writeheader()
         
         validator = cerberus.Validator()
         
         for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])
                    
if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    main_function(OSM_FILE, validate=False)


# ## SQL PART

# In[4]:

import sqlite3


# In[5]:

conn = sqlite3.connect("nymetro.db")
cursor = conn.cursor()
tables = ['nodes', 'nodes_tags', 'ways', 'ways_nodes', 'ways_tags']
for t in tables:
    cursor.execute('DROP TABLE IF EXISTS {}'.format(t))
#   cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
#   tables=(cursor.fetchall())
#   print tables
cursor.execute('''CREATE TABLE IF NOT EXISTS 
                    nodes(
                    id INT PRIMARY KEY NOT NULL,
                    lat FLOAT, lon FLOAT, 
                    user VARCHAR, uid INT, 
                    version INT, changeset INT, 
                    timestamp DATETIME);''')
cursor.execute('''CREATE TABLE IF NOT EXISTS
                    nodes_tags(
                    id INT NOT NULL,
                    key VARCHAR, value VARCHAR, 
                    type VARCHAR);''')
cursor.execute('''CREATE TABLE IF NOT EXISTS
                    ways(
                    id INT PRIMARY KEY NOT NULL, user VARCHAR, 
                    uid INT, version INT, changeset INT, 
                    timestamp DATETIME);''')
cursor.execute('''CREATE TABLE IF NOT EXISTS
                    ways_nodes(
                    id INT NOT NULL, 
                    node_id INT, position INT);''')
cursor.execute('''CREATE TABLE IF NOT EXISTS
                    ways_tags(
                    id INT NOT NULL, 
                    key VARCHAR, value VARCHAR, 
                    type VARCHAR);''')
conn.commit()


# In[8]:

cursor.execute('SELECT COUNT(*) FROM ways;')
results = cursor.fetchall()
print results


# In[129]:

conn.close()


# In[6]:

# Read in the csv file as a dictionary, format the
# data as a list of tuples:
for t in tables:
    with open('./data/{}.csv'.format(t), 'rb') as f:
        dr = csv.DictReader(f) # comma is default delimiter
        if t == 'nodes':
            to_db = [(i['id'].decode("utf-8"), i['lat'].decode("utf-8"), i['lon'].decode("utf-8"), i['user'].decode("utf-8"), 
                      i['uid'].decode("utf-8"), i['version'].decode("utf-8"), i['changeset'].decode("utf-8"),
                     i['timestamp'].decode("utf-8")) for i in dr]
        # insert the formatted data
            cursor.executemany('''INSERT INTO nodes(id, lat, lon, user, uid, version, changeset, timestamp)
                            VALUES(?, ?, ?, ?, ?, ?, ?, ?);''', to_db)
            conn.commit()
        elif t == 'nodes_tags':
            to_db = [(i['id'].decode("utf-8"), i['key'].decode("utf-8"), i['value'].decode("utf-8"), 
                      i['type'].decode("utf-8")) for i in dr]
            cursor.executemany('''INSERT INTO nodes_tags(id, key, value, type)
                            VALUES(?, ?, ?, ?);''', to_db)
            conn.commit()
        elif t == 'ways':
            to_db = [(i['id'].decode("utf-8"), i['user'].decode("utf-8"), i['uid'].decode("utf-8"), i['version'].decode("utf-8"), 
                     i['changeset'].decode("utf-8"), i['timestamp'].decode("utf-8")) for i in dr]
            cursor.executemany('''INSERT INTO ways(id, user, uid, version, changeset, timestamp)
                            VALUES(?, ?, ?, ?, ?, ?);''', to_db)
            conn.commit()
        elif t == 'ways_nodes':
            to_db = [(i['id'].decode("utf-8"), i['node_id'].decode("utf-8"), 
                      i['position'].decode("utf-8")) for i in dr]
            cursor.executemany('''INSERT INTO ways_nodes(id, node_id, position)
                            VALUES(?, ?, ?);''', to_db)
            conn.commit()
        elif t == 'ways_tags':
            to_db = [(i['id'].decode("utf-8"), i['key'].decode("utf-8"), i['value'].decode("utf-8"), 
                      i['type'].decode("utf-8")) for i in dr]
            cursor.executemany('''INSERT INTO ways_tags(id, key, value, type)
                            VALUES(?, ?, ?, ?);''', to_db)
            conn.commit()
            
    


# In[7]:

cursor.execute('SELECT * FROM nodes LIMIT 10;')
all_rows = cursor.fetchall()
print('1):')
pprint.pprint(all_rows, width=150, indent=2)


# ## CHECK IF AUDITS WERE GOOD
# 1. postcodes
# 2. city
# 3. state
# 4. county_name

# In[15]:

def countQuery(key, limit=10):
    '''
    Sorts the values of 'key' argument by count descending 
    number of results limited by value of 'limit' argument.
    '''
    cursor.execute('''SELECT tags.value, COUNT(*) AS total FROM
                        (SELECT * FROM nodes_tags 
                        UNION ALL
                        SELECT * FROM ways_tags) AS tags
                        WHERE tags.key = '{}'
                        GROUP BY tags.value 
                        ORDER BY total DESC
                        LIMIT {};'''.format(key, limit))
    results = cursor.fetchall()
    return results


# In[31]:

countQuery(key='postcode', limit=100)


# In[40]:

query = cursor.execute('''SELECT tags.value, COUNT(*) AS total FROM
                        (SELECT * FROM nodes_tags 
                        UNION ALL
                        SELECT * FROM ways_tags) AS tags
                        WHERE tags.key = 'postcode' GROUP BY tags.value 
                        HAVING total < 4
                        ORDER BY total DESC;''')
printQuery(query, all=True)


# In[28]:

countQuery('city', limit=100)


# In[29]:

countQuery('state', limit=100)


# In[30]:

countQuery('county', limit=100)


# ## Overview Statistics of Data

# ## File sizes

# In[9]:

#Show files and their sizes:

dirpath = "C:/Users/cguzm_000/Documents/udacity-projects/OpenStreetMapProject_Files"

files_list = []
for path, dirs, files in os.walk(dirpath):
    files_list.extend([(filename, os.path.getsize(os.path.join(path, filename))) for filename in files])
for filename, size in files_list:
    if size < 1*10**6:
        print '{:.<40s}: {:0d}KB'.format(filename,size/1000)
    else:
        print '{:.<40s}: {:0d}MB'.format(filename,size/1000000)


# ## Number of nodes

# In[10]:

def printQuery(query, all=False):
    query
    if all:
        pprint.pprint(cursor.fetchall())
    else:
        print cursor.fetchall()[0][0]

query = cursor.execute('''SELECT COUNT(*) FROM nodes;''')
printQuery(query)


# ## Number of ways

# In[11]:

query = cursor.execute('''SELECT COUNT(*) FROM ways;''')
printQuery(query)


# ## Number of unique users

# In[12]:

query = cursor.execute('''SELECT COUNT(DISTINCT(uniques.uid)) FROM (SELECT uid FROM nodes
                  UNION
                  SELECT uid FROM ways) AS uniques;
                    ''')
printQuery(query)


# ## Top 10 contributing users

# In[13]:

query = cursor.execute('''SELECT elems.user, COUNT(*) as total
                        FROM (SELECT user FROM nodes 
                        UNION ALL 
                        SELECT user FROM ways) elems
                        GROUP BY elems.user
                        ORDER BY total DESC
                        LIMIT 10;''')

printQuery(query, all=True)


# ## Top user contribution percentages

# In[42]:

cursor.execute('SELECT e.user, COUNT(e.user), (SELECT count(*) FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways)) as tot, ROUND(COUNT(e.user)*100.0/(SELECT COUNT(*) FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways)),2) as num FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) e GROUP BY e.user ORDER BY num DESC LIMIT 10;')

all_rows = cursor.fetchall()
pprint.pprint(all_rows)


# ## Top ten amenities

# In[17]:

countQuery(key='amenity', limit=10)


# ## Places of leisure

# In[19]:

countQuery(key='leisure', limit=10)


# ## Types of shops

# In[22]:

countQuery(key='shop', limit=10)


# ## Sports

# In[24]:

countQuery(key='sport', limit=10)


# ## Number of delis

# In[55]:

query = cursor.execute('''
                       SELECT COUNT(*) as total FROM (SELECT * FROM nodes_tags 
                       UNION ALL SELECT * FROM ways_tags) AS t
                       WHERE t.value LIKE '%deli'; 
                       ''')
printQuery(query)


# ## Top 10 cuisines

# In[58]:

printQuery(cursor.execute('''SELECT nodes_tags.value, COUNT(*) as num
FROM nodes_tags 
    JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='restaurant') i
    ON nodes_tags.id=i.id
WHERE nodes_tags.key='cuisine'
GROUP BY nodes_tags.value
ORDER BY num DESC LIMIT 10;'''), all=True)


# In[ ]:

conn.close() # closes connection

