#!/usr/bin/python3

import argparse
import os
import sys
import logging
from logging import warning, debug, info, error
import psycopg2
import progressbar

# Parse command line argument
parser = argparse.ArgumentParser(description="Search string occurence in "
                                 "postgres database like \"grep\"")

parser.add_argument("--hostname",
                    help="database server host or socket directory",
                    default="/var/run/postgresql")
parser.add_argument("-p", "--port", help="database server port",
                    default=5432, type=int)
parser.add_argument("-U", "--username", help="database user name",
                    default=os.environ['USER'])
parser.add_argument("-v", "--verbose", action="count",
                    help="increase output verbosity", default=0)
parser.add_argument("-d", "--database", help="database name to connect to",
                    default=os.environ['USER'])
parser.add_argument("pattern", help="pattern to search in database")

args = parser.parse_args()

# Set logging level
if args.verbose >= 2:
        log_level = logging.DEBUG
elif args.verbose == 1:
        log_level = logging.INFO
else:
        log_level = logging.WARN
logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')
logging.StreamHandler(sys.stdout)

debug("Connecting to database...")

conn = psycopg2.connect(dbname=args.database, host=args.hostname,
                        user=args.username)

