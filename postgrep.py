#!/usr/bin/python3

import argparse
import os
import sys
import logging
from getpass import getpass
from logging import warning, debug, info, error
import psycopg2
import psycopg2.extras
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

conn = None

# try a first connection with no password, this should use ~.pgpass
try:
    conn = psycopg2.connect(dbname=args.database, host=args.hostname,
                            port=args.port,
                            user=args.username)
except psycopg2.OperationalError as e:
    # test if it's required password
    if 'no password' in str(e):
         conn = psycopg2.connect(dbname=args.database, host=args.hostname,
                                 port=args.port,
                                 user=args.username,
                                 password=getpass())
    else:
        raise e

# List database entity with type and length
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
cur.execute("""SELECT (information_schema.tables.table_schema || '.' ||  
                      information_schema.tables.table_name)::regclass::int AS oid,
                      information_schema.tables.table_schema AS schema,
                      information_schema.tables.table_name AS table,
                      column_name AS column,
                      ordinal_position AS position,
                      data_type AS type,
                      character_maximum_length AS length
               FROM information_schema.tables
               LEFT JOIN information_schema.columns ON (information_schema.tables.table_schema =
                                                          information_schema.columns.table_schema AND
                                                        information_schema.tables.table_name =
                                                          information_schema.columns.table_name)
               WHERE table_type = 'BASE TABLE'
               AND information_schema.tables.table_schema NOT IN ('pg_catalog','information_schema')""")
tables_by_oid = {}
table_to_oid = {}
for rec in cur:
    fqtn = "%s.%s" % (rec['schema'], rec['table'])
    oid = rec['oid'] 
    tables_by_oid[oid] = fqtn
    table_to_oid[fqtn] = oid
    print("%(oid)s %(schema)s.%(table)s.%(column)s %(position)s %(type)s %(length)s" % rec)

cur.execute("""SELECT
                   t.oid,
                   t.relname AS table_name,
                   i.relname AS index_name,
                   array_agg(a.attname) AS column_names
               FROM
                   pg_class t,
                   pg_class i,
                   pg_index ix,
                   pg_attribute a
               WHERE
                   t.oid = ix.indrelid
                   and i.oid = ix.indexrelid
                   and a.attrelid = t.oid
                   and a.attnum = ANY(ix.indkey)
                   and t.relkind = 'r'
               GROUP BY t.oid, t.relname, index_name
               ORDER BY
                   t.relname,
                   i.relname""")
for rec in cur:
    print("%(oid)s %(table_name)s %(index_name)s %(column_names)s" % rec)

# SELECT 'public.departments'::regclass::int;

# SELECT (table_schema || '.' || table_name)::regclass::int, table_name FROM information_schema.tables;

