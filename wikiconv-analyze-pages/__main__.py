import argparse
import pathlib
from . import analyze
from .analyzers import getAnalyzersNames
from .utils.timestamp import setOutputPath

def get_args():

    parser = argparse.ArgumentParser(
        prog='wikiconv-analyze-pages',
        description='Graph snapshot features extractor.',
    )
    parser.add_argument(
        'analyzer',
        choices=getAnalyzersNames(),
        metavar='ANALYZER',
        type=str,
        help='Analyzer module name.',
    )
    parser.add_argument(
        'files',
        metavar='FILE',
        type=pathlib.Path,
        nargs='+',
        help='Wikidump file to parse, can be compressed.',
    )
    parser.add_argument(
        '--parallel', '-n',
        action='store_true'
    )
    parser.add_argument(
        '--max-workers',
        type=int,
        required=False,
        default=4
    )
    parser.add_argument(
        '--output-dir-path',
        type=pathlib.Path,
        required=False,
        default=None
    )

    parsed_args, a = parser.parse_known_args()
    if parsed_args.output_dir_path is not None:
        setOutputPath(parsed_args.output_dir_path)
    return parsed_args


def main():
    args = get_args()
    
    files = args.files
    analyzerName = args.analyzer
    parallel = args.parallel
    max_workers = args.max_workers

    print(f"Using analyzer {analyzerName}")
    analyze.analyze(files=files, analyzerName=analyzerName, parallel=parallel, max_workers=max_workers)

# python -m wikiconv-analyze-pages reply-to /mnt/d --output_dir_path . --output-compression gz --parallel --max-workers 5
if __name__ == '__main__':
    main()
