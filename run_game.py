import argparse
import json
from datetime import datetime
from subprocess import Popen, CREATE_NEW_CONSOLE
import redis
import numpy as np
import pandas as pd
from state_updater import iterate_prices

WAITRESS_THREADS = 8

parser = argparse.ArgumentParser(description='Stock platform management console')
subparsers = parser.add_subparsers(help='Select action')

prs_init = subparsers.add_parser('init', help='Init db state for the game, load companies and users')
prs_init.set_defaults(action='init')

prs_db = subparsers.add_parser('db', help='Db management helpers')
prs_db_grp = prs_db.add_mutually_exclusive_group(required=True)
prs_db_grp.add_argument('-flush', action='store_true', help='Flush db')
prs_db_grp.add_argument('-dump', action='store_true', help='Save db to disk')
prs_db_grp.add_argument('-copy', type=int, help='Copy whole db to another db specified by index')
prs_db_grp.add_argument('-select', type=int, help='Select db index')
prs_db_grp.add_argument('-info', action='store_true', help='Get the number of keys in db')
prs_db.set_defaults(action='db')

prs_run = subparsers.add_parser('run', help='Run game component')
prs_run.add_argument('-db', action='store_true', help='Start Redis server in separate console')
prs_run.add_argument('-web', action='store_true', help='Start Dash web app in separate console')
prs_run.add_argument('-game', action='store_true', help='Start stock price generation and user value logging')
prs_run.set_defaults(action='run')

# prs_run = subparsers.add_parser('', help='Run game component')
# prs_run.add_argument('-db', action='store_true', help='Start Redis server in separate console')
# prs_run.add_argument('-web', action='store_true', help='Start Dash web app in separate console')
# prs_run.add_argument('-game', action='store_true', help='Start stock price generation and user value logging')
# prs_run.set_defaults(action='run')

prs_stop = subparsers.add_parser('stop', help='Stop game component if it is running')
prs_stop.add_argument('-web', action='store_true', help='Stop Dash web app and close its console')
prs_stop.add_argument('-game', action='store_true', help='Stop stock price generation and user value logging')
prs_stop.set_defaults(action='stop')

prs_exit = subparsers.add_parser('exit', help='Kill all and die')
prs_exit.set_defaults(action='exit')

try:
    print('connecting to db...')
    rds = redis.Redis()
    rds.info()
    print('connected')
except Exception:
    print('could not connect to the db')
    print('if not running then "run -db"')
    rds = None

while(True):

    input_str = str(input())

    args = None
    try:
        args = parser.parse_args(input_str.split(' '))
    except SystemExit as e:
        continue
    
    if args is not None:

        if args.action == 'db':

            if rds is None:
                print('no db connection, cannot perform')
                continue

            if args.dump:
                rds.bgsave()
                print('background save initiated')
            if args.flush:
                print('cleaning the selected DB, all data is lost')
                rds.flushdb()
            if args.select is not None:
                print('selecting another db')
                rds = redis.Redis(db=args.select)
            if args.copy is not None:
                print('copying selected db to new index')
                rds.migrate('127.0.0.1', '6379', '', args.copy, 5000, copy=True, replace=True)
            if args.info:
                print('there are', rds.dbsize(), 'keys in selected db')
                print(rds.info(section='keyspace'))

        
        elif args.action == 'run':

            if args.web:
                PROC_WEB = Popen('cmd /k conda activate dash && waitress-serve \
                                 --threads='+str(WAITRESS_THREADS)+' --listen=*:8050 index:dash_app.server',
                                 creationflags=CREATE_NEW_CONSOLE, stdin=None, stdout=None, stderr=None)
            if args.game:
                PROC_UPDATER = Popen('cmd /k conda activate dash && python state_updater.py',
                                      creationflags=CREATE_NEW_CONSOLE, stdin=None, stdout=None, stderr=None)
            
            if args.db:
                PROC_DB = Popen('cmd /k cd redis && redis-server.exe',
                                creationflags=CREATE_NEW_CONSOLE, stdin=None, stdout=None, stderr=None)
                rds = redis.Redis()

        elif args.action == 'stop' or args.action == 'exit':
            print('stopping not implemented yet, close the terminals manually instead')
            break

        elif args.action == 'init':

            if rds is None:
                print('no db connection, cannot perform')
                continue
            
            print('loading users and companies from init_state.json')

            with open('init_state.json', 'r') as file:
                init_state = json.load(file)

            len_companies = len(init_state['companies'])

            prices = pd.DataFrame(
                columns=init_state['companies'],
                data=np.random.randint(50, 150, len_companies).reshape((1, len_companies))
            )
            now_time = pd.to_datetime(datetime.now())
            prices['time'] = now_time - pd.Timedelta(minutes=20)
            prices.set_index('time', inplace=True)

            rds.set('last_row', 0)
            rds.rpush('companies', *list(prices.columns))
            
            for idx, row in prices.iterrows():
                last_row = rds.get('last_row').decode('utf-8')
                rds.rpush('row_'+last_row, *([str(idx)] + list(row)))
                rds.incr('last_row')

            for i in range(19, 0, -1):
                iterate_prices(rds, time=now_time - pd.Timedelta(minutes=i))

            for user, passw in init_state['users'].items():
                rds.set('pass_' + user, passw)
                rds.set('cash_' + user, init_state['cash'])

            print('all set, feel free to "run -web -game"')
