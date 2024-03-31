#!/usr/bin/python3

import sys
import re
import datetime

import json

if len(sys.argv) < 2:
    print(f"{sys.argv[0]} log_file")
    sys.exit(0)

filename = sys.argv[1]

authors = {}

log_data = ""
with open(filename, "r", encoding="latin1") as file_handle:
    log_data = file_handle.read()

date_format = "%a %b %d %H:%M:%S %Y %z"

pos = 0
commits = 0
last_commit = False
while not last_commit:
    commits += 1
    print(
        f"Left {len(log_data[pos:]):,}, "
        f"commits: {commits:,}, "
        f"len authors: {len(authors.keys()):,}                \r",
        end="",
    )
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
    parsed_date = datetime.datetime.strptime(date_match.group(1), date_format)

    if author not in authors:
        authors[author] = []

    authors[author].append(parsed_date)

    if last_commit:
        break

    pos += next_commit_match.span()[0] + 1

    # if commits > 100000:
    #     break


def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")


# Done
with open(f"{filename}.json", "w", encoding="latin1") as file_handle:
    json.dump(authors, fp=file_handle, default=datetime_handler)
