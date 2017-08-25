#!/bin/bash

POSTGREP_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

$POSTGREP_DIR/../postgrep.py --hostname 127.0.0.1 -p 54322 -U test -d test test
