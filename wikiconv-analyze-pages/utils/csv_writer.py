from glob import glob
from io import TextIOWrapper
from pathlib import Path
from typing import Iterable, TextIO, Union
from .. import file_utils

SEPARATOR = ','
SECONDARY_SEPARATOR = '|'

def writeline(file: Union[TextIOWrapper, TextIO, None], values: Iterable[str]):
    file.write(SEPARATOR.join(values) + '\n')

def writelineNumber(file: Union[TextIOWrapper, TextIO, None], values: Iterable[str]):
    file.write(SEPARATOR.join([str(v) for v in values]) + '\n')

def writelineMultiValueNumber(file: Union[TextIOWrapper, TextIO, None], multiValues: Iterable[Iterable[Union[int, float]]], preValues: Iterable[str] = [], postValues: Iterable[str] = []):
    writelineMultiValueStr(file, [[str(x) for x in y] for y in multiValues], preValues, postValues)


def writelineMultiValueStr(file: Union[TextIOWrapper, TextIO, None], multiValues: Iterable[Iterable[str]], preValues: Iterable[str] = [], postValues: Iterable[str] = []):
    line = [
        SEPARATOR.join(preValues),
        SEPARATOR.join([SECONDARY_SEPARATOR.join(x) for x in multiValues]),
        SEPARATOR.join(postValues)
        
    ]
    file.write(SEPARATOR.join(line) + '\n')

def writeHeaders(file: Union[TextIOWrapper, TextIO, None], headers: Iterable[str]):
    writeline(file, headers)

def joinCSVs(filesPattern: str, headers: Iterable[str], outputFile: str, compression = None):
    files = glob(filesPattern)
    outFile = file_utils.output_writer(path=outputFile, compression=compression)

    writeHeaders(outFile, headers)
    for f in files:
        with open(f) as infile:
            for line in infile:
                outFile.write(line)
    outFile.close()


