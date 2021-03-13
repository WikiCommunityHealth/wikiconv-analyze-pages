import json
import argparse
from ..utils.timestamp import printTimestamp
from pathlib import Path
from typing import Any, List, Mapping
from .analyzer import Analyzer
from .. import file_utils
from ..utils.discussion_graph import DiscussionGraph

class ReplyToAnalyzer(Analyzer):
    __mapper = {
        'CREATION': 'red',
        'ADDITION': 'blue',
        'MODIFICATION': 'green',
        'RESTORATION': 'brown',
        'DELETION': 'orange'
    }
    __file = None
    __outputPath = None
    __outputCounter = 0
    __compression = None

    def __init__(self):
        self.configureArgs()

    def configureArgs(self):
        parser = argparse.ArgumentParser(
            prog='reply_to',
            description='Graph snapshot features extractor.',
        )
        parser.add_argument(
            '--output_dir_path',
            metavar='OUTPUT_DIR',
            type=Path,
            required=True,
            help='XML output directory.',
        )
        parser.add_argument(
            '--output-compression',
            choices={None, '7z', 'bz2', 'gz'},
            required=False,
            default=None,
            help='Output compression format [default: no compression].',
        )
        parsed_args, _ = parser.parse_known_args()
        self.__outputPath = parsed_args.output_dir_path
        self.__compression = parsed_args.output_compression

    def finalizeSection(self, sectionCounter: int, currentSectionObjs: List[Mapping[str, Any]], currentSectionId: int) -> None:
        root_node = 'root'
        G = DiscussionGraph()
        users = {}

        for record in currentSectionObjs:

            # TODO: fix finale data
            # record['timestamp'] = datetime.datetime.strptime(record['timestamp'], "%Y-%m-%dT%H:%M:%S+00:00")

            # username = ''
            # if 'user' in record and 'text' in record['user']:
            #     username = record['user']['text']
            # elif 'user' in record and 'ip' in record['user']:
            #     username = record['user']['ip']
            # else:
            #     username = 'unknown'

            curr_id = record['id']
            users[curr_id] = None if 'user' not in record else record['user']
            # current_month_year = f"{record['timestamp'].month}/{record['timestamp'].year}"
            reply_to = record['replytoId'] if 'replytoId' in record else None
            parent_id = record['parentId'] if 'parentId' in record else None
            ancestor_id = record['ancestorId'] if 'ancestorId' in record else None

            if ancestor_id and ancestor_id != curr_id and not G.is_node_inside(ancestor_id):
                if parent_id:
                    ancestor_id = parent_id
                elif reply_to:
                    ancestor_id = reply_to
                else:
                    ancestor_id = curr_id
                #print(f"ancestor_id: {ancestor_id}")

            if reply_to and not G.is_node_inside(reply_to):
                #print(f"Reply_To: {reply_to}")
                G.add_node(
                    reply_to,
                    'unknown',
                    reply_to,
                    reply_to,
                    reply_to,
                    None,
                    'pink'
                )

            if parent_id and not G.is_node_inside(parent_id):
                #print(f"parent_id: {parent_id}")
                G.add_node(
                    parent_id,
                    'unknown',
                    parent_id,
                    parent_id,
                    parent_id,
                    None,
                    'pink'
                )

            G.add_node(
                curr_id,
                record['type'],
                parent_id,
                ancestor_id,
                reply_to,
                record['timestamp'],
                self.__mapper[record['type']]
            )

            if record['type'] in ['CREATION', 'ADDITION']:
                if reply_to != None:
                    if G.get_node(reply_to)['action'] in ['CREATION', 'ADDITION']:
                        G.add_edge(curr_id, reply_to)
                    else:
                        if G.get_node(reply_to)['ancestor_id'] is None:
                            print('culol', curr_id, reply_to)
                        G.add_edge(curr_id, G.get_node(reply_to)['ancestor_id'])
                else:
                    G.add_edge(curr_id, root_node)
                    
            elif record['type'] in ['MODIFICATION', 'DELETION', 'RESTORATION']:
                if parent_id != None:
                    if G.get_node(parent_id)['action'] in ['CREATION', 'ADDITION']:
                        G.add_edge(curr_id, parent_id)
                    else:
                        if G.get_node(parent_id)['ancestor_id'] is None:
                            print('culool', curr_id, parent_id)
                        G.add_edge(curr_id, G.get_node(parent_id)['ancestor_id'])
                else:
                    G.add_edge(curr_id, root_node)

        for record in currentSectionObjs:
            parentId = G.get_parent(record['id'])
            replyToValue = None
            if parentId == 'root':
                replyToValue = parentId
            elif parentId not in users:
                replyToValue = 'unknown'
            else:
                replyToValue = users[parentId]
            record['replyToUser'] = replyToValue
            self.__file.write(f"{json.dumps(record)}\n")

    def fileStart(self, number: int) -> None:
        if self.__file is not None:
            self.__file.close()
        newFilename = str(self.__outputPath / (f"reply-to-{str(number).zfill(4)}.json"))
        self.__file = file_utils.output_writer(path=newFilename, compression=self.__compression)
        self.__outputCounter += 1

    def finalize(self) -> None:
        if self.__file is not None:
            self.__file.close()