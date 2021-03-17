from datetime import datetime
from pathlib import Path

timesOutputPath = Path('.')
def setOutputPath(outputPath: Path):
    global timesOutputPath
    timesOutputPath = outputPath

def printTimestamp(description: str) -> None:
    with open(str(timesOutputPath / 'times.txt'), "a") as f:
        line = f'{datetime.now().strftime("%H:%M:%S")}: {description}\n'
        f.write(line)
        print(line)