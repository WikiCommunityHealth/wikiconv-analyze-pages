from io import TextIOWrapper
from typing import Iterable

SEPARATOR = '\t'
SECONDARY_SEPARATOR = '|'

def writeline(file: TextIOWrapper, values: Iterable[str]):
    file.write(SEPARATOR.join(values) + '\n')

def writelineMultiValueInt(file: TextIOWrapper, multiValues: Iterable[Iterable[int]], preValues: Iterable[str] = [], postValues: Iterable[str] = []):
    writelineMultiValueStr(file, [[str(x) for x in y] for y in multiValues], preValues, postValues)


def writelineMultiValueStr(file: TextIOWrapper, multiValues: Iterable[Iterable[str]], preValues: Iterable[str] = [], postValues: Iterable[str] = []):
    line = [
        SEPARATOR.join(preValues),
        SEPARATOR.join([SECONDARY_SEPARATOR.join(x) for x in multiValues]),
        SEPARATOR.join(postValues)
        
    ]
    file.write(SEPARATOR.join(line) + '\n')

def writeHeaders(file: TextIOWrapper, headers: Iterable[str]):
    writeline(file, headers)
