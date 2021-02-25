import argparse
import pathlib

from . import analyze

def get_args():
    parser = argparse.ArgumentParser(
        prog='wikiconv-analyze-pages',
        description='Graph snapshot features extractor.',
    )
    parser.add_argument(
        'files',
        metavar='FILE',
        type=pathlib.Path,
        nargs='+',
        help='Wikidump file to parse, can be compressed.',
    )

    parsed_args = parser.parse_args()
    return parsed_args



def main():
    args = get_args()
    files = args.files
    analyze.analyze(files=files)

if __name__ == '__main__':
    main()
