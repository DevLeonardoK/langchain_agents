from pathlib import Path
import subprocess

p = Path("/home/").iterdir()

for r in p:
    print(r.name)