from datetime import datetime
from pathlib import Path

def printTimestamp(outputPath: Path, description: str) -> None:
    with open(str(outputPath / "times.txt"), "a") as f:
        line = f'{datetime.now().strftime("%H:%M:%S")}: {description}\n'
        f.write(line)
        print(line)