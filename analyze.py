#!/usr/bin/python3

import sys
import re
from datetime import datetime

import json

if len(sys.argv) < 2:
    print(f"{sys.argv[0]} log_file")
    sys.exit(0)

filename = sys.argv[1]

data = {}

log_data = ""
with open(filename, "r", encoding="latin1") as file_handle:
    log_data = file_handle.read()

date_format = "%a %b %d %H:%M:%S %Y %z"

pos = 0
last_commit = False
while not last_commit:
    print(f"Left {len(log_data[pos:]):,}")
    if pos >= len(log_data):
        break

    next_commit_match = re.search(
        pattern=r"^commit ", string=log_data[pos + 1 :], flags=re.MULTILINE
    )

    chunk = ""
    if next_commit_match is None:
        # No commit line
        chunk = log_data[pos:]
        last_commit = True
    else:
        chunk = log_data[pos : pos + 1 + next_commit_match.span()[0]]

    author_match = re.search(
        pattern=r"^Author:\s+(.*)", string=chunk, flags=re.MULTILINE
    )
    date_match = re.search(pattern=r"^Date:\s+(.*)", string=chunk, flags=re.MULTILINE)
    if author_match is None or date_match is None:
        raise ValueError("Missing Author/Date")

    author = author_match.group(1)
    parsed_date = datetime.strptime(date_match.group(1), date_format)

    if author not in data:
        data[author] = []

    data[author].append(parsed_date)

    if last_commit:
        break

    pos += next_commit_match.span()[0] + 1


# Done
print(json.dumps(data))
