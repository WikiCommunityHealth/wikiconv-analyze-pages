from tqdm import tqdm
from pymongo import MongoClient
import sys
from datetime import datetime

lingua = sys.argv[1]
print(lingua)

with open(f'{lingua}.tsv', 'w') as f:
    for x in tqdm(MongoClient(port=27017)['wikiusers'][f'{lingua}wiki_raw'].find()):
        id = x['id']
        username = x['username']
        bot = x['is_bot']
        last = 'None'
        if 'activity' in x and 'total' in x['activity'] and 'last_event_timestamp' in x['activity']['total']:
            last = x['activity']['total']['last_event_timestamp'].strftime("%Y-%m-%dT%H:%M:%SZ")
        gr = ','.join(x['groups'])

        f.write(f"{id}\t{username}\t{bot}\t{last}\t{gr}\n")
