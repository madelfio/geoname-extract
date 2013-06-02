import sys
import re
import csv

header_re = '>([^<>]+)</th>'
cell_re = '>([^<>]+)</td>'

plural_map = {
    'country, state, region,...': 'countries, states, or administrative regions',
    'stream, lake, ...': 'streams, lakes, or hydrological features',
    'parks,area, ...': 'parks or areas',
    'city, village,...': 'cities or villages',
    'road, railroad': 'roads or railroads',
    'spot, building, farm': 'spots, buildings, or farms',
    'mountain,hill,rock,... ': 'mountains, hills, or rocky areas',
    'undersea': 'undersea areas',
    'forest,heath,...': 'forests or areas of vegetation',
}

cur_header = None
types = []
with open(sys.argv[1]) as f:
    for line in f:
        header = re.search(header_re, line)
        cells = re.findall(cell_re, line)

        if header:
            cur_header = header.group(1)[0]
            cur_type = header.group(1)[2:].strip()
            types.append({'t1': cur_header, 'type': cur_type})

        if cur_header and cells:
            types.append({'t1': cur_header,
                          't2': cells[0][:3],
                          't3': cells[0],
                          'type': cells[1].strip()})
            if len(cells) == 3:
                types[-1]['desc'] = cells[2].strip()

# add plurals column
for t in types:
    s = t['type']
    last = s.split()[-1]
    p = None

    if s in plural_map:
        t['plural'] = plural_map[s]
        continue

    # Handle:
    # - 'seat of government of a political entity'
    if s.startswith('section of'):
        s = 'sections of' + s[len('section of'):]
    elif s.startswith('seat of a'):
        s = 'seats of' + s[len('seat of a'):]
    elif 'capital of a' in s:
        s = s.replace('capital of a', 'capitals of')


    if last[-2:] in ['sh', 'ch', 'ss']:
        p = s + 'es'
    elif last[-1] == 'y' and last[-2:] not in ['ay', 'ey']:
        p = s[:-1] + 'ies'
    elif last[-1] == 's':
        p = s
    elif '(s)' in s:
        p = s.replace('(s)', 's')
    elif '(es)' in s:
        p = s.replace('(es)', 'es')
    elif 'y(-ies)' in s:
        p = s.replace('y(-ies)', 'ies')
    elif 'is(-es)' in s:
        p = s.replace('is(-es)', 'es')
    elif 'f(-ves)' in s:
        p = s.replace('f(-ves)', 'ves')
    else:
        p = s + 's'
    t['plural'] = p

# add intermediate types (pseudotypes)
lookup = lambda x, y, z: '|'.join([x, y or '', z or ''])
t_set = set([lookup(t['t1'], t.get('t2'), t.get('t3')) for t in types])
pseudotypes = []
for t in types:
    if lookup(t['t1'], None, None) not in t_set:
        pt = t.copy()
        pt['t2'] = None
        pt['t3'] = None
        pseudotypes.append(pt)
        t_set.add(lookup(pt['t1'], None, None))
    if lookup(t['t1'], t.get('t2'), None) not in t_set:
        pt = t.copy()
        pt['t3'] = None
        pseudotypes.append(pt)
        t_set.add(lookup(pt['t1'], t['t2'], None))

types.extend(pseudotypes)


writer = csv.DictWriter(sys.stdout, ['t1', 't2', 't3', 'type', 'plural',
                                     'desc'], extrasaction='ignore')

for t in types:
    writer.writerow(t)
