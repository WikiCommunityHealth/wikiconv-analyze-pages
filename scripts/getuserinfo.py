from tqdm import tqdm
from pymongo import MongoClient
import sys

lingua = sys.argv[1]
print(lingua)

with open(f'{lingua}.tsv', 'w') as f:
    for x in tqdm(MongoClient(port=27017)['wikiusers'][f'{lingua}wiki'].find()):
        f.write(f"{x['id']}\t{x['username']}\t{x['is_bot']}\t{','.join(x['groups']['current'])}\n")
