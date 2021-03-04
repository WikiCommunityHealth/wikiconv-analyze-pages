import argparse
import pathlib
from . import analyze
from .analyzers import getAnalyzer, getAnalyzersNames

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
    parser.add_argument(
        'analyzer',
        choices=getAnalyzersNames(),
        metavar='ANALYZER',
        type=str,
        help='Analyzer module name.',
    )

    parsed_args, _ = parser.parse_known_args()


    return parsed_args


def main():
    args = get_args()
    files = args.files

    # from .analyzers import mean_var as analyzer
    analyzer = getAnalyzer(args.analyzer)
    analyzer.configureArgs()
    print(f"Using analyzer {args.analyzer}")

    analyze.analyze(files=files, analyzer=analyzer)


if __name__ == '__main__':
    main()
