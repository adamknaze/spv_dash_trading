import pandas as pd
import numpy as np
from uuid import uuid4

def read_prices_from_rds(rds):

    companies = rds_get_companies(rds)
    row_count = int(rds.get('last_row').decode('utf-8'))
    data = np.zeros((row_count, len(companies)), dtype=float)
    times = []

    for i in range(row_count):
        row = [x.decode('utf-8') for x in rds.lrange('row_'+str(i), 0, -1)]
        times.append(row[0])
        data[i] = np.array(row[1:]).astype(float)

    prices_df = pd.DataFrame(columns=companies, data=data, index=pd.to_datetime(times))

    return prices_df


def rds_get_current_prices(rds):

    last_row = rds_get_last_row(rds)
    row = [x.decode('utf-8') for x in rds.lrange('row_'+str(last_row - 1), 0, -1)]
    return [float(x) for x in row[1:]]


def rds_get_last_row(rds):

    return int(rds.get('last_row').decode('utf-8'))


def rds_get_companies(rds):

    return [x.decode('utf-8') for x in rds.lrange('companies', 0, -1)]


def rds_get_user_cash(rds, user, token=None):

    if token is not None and not rds_check_token(rds, user, token):
        return 0

    user_cash = rds.get('cash_' + user)
    if user_cash is None:
        return 0
    return float(user_cash.decode('utf-8'))


def rds_get_user_portfolio_df(rds, user, token):

    if not rds_check_token(rds, user, token):
        return None
    
    balance_row = [float(x.decode('utf-8')) for x in rds.lrange('user_balance_' + user, 0, -1)]
    timestamps = [x.decode('utf-8') for x in rds.lrange('balance_timestamps', 0, -1)]

    if len(timestamps) > len(balance_row):
        timestamps = timestamps[:len(balance_row)]

    return pd.DataFrame(columns=['value'], data=balance_row, index=pd.to_datetime(timestamps))


def rds_check_pass_generate_token(rds, user, passw):

    if not rds.exists('pass_' + user):
        return None
    if not rds.get('pass_' + user).decode('utf-8') == passw:
        return None
    
    token = str(uuid4())
    rds.set('token_' + user, token)
    return token


def rds_check_token(rds, user, token):

    res = rds.get('token_' + user)
    if res is None or res.decode('utf-8') != token:
        return False
    return True


def rds_get_user_companies(rds, user, token=None):

    if token is not None and not rds_check_token(rds, user, token):
        return []

    if not rds.exists('companies_' + user):
        return []
    return [x.decode('utf-8') for x in rds.smembers('companies_' + user)]


def rds_get_user_cmp_share_cnt(rds, user, company, token=None):

    if token is not None and not rds_check_token(rds, user, token):
        return 0

    share_cnt = rds.get('shares_' + user + '_' + company)
    if share_cnt is None:
        return 0
    return int(share_cnt.decode('utf-8'))


def rds_buy_shares(rds, user, company, share_cnt, price, token):

    if not rds_check_token(rds, user, token):
        return False

    user_cash = rds_get_user_cash(rds, user, token)
    if share_cnt * price > user_cash:
        return False

    rds.set('cash_' + user, user_cash - share_cnt * price)
    rds.incrby('shares_' + user + '_' + company, share_cnt)
    rds.sadd('companies_' + user, company)
    return True


def rds_sell_shares(rds, user, company, share_cnt, price, token):

    if not rds_check_token(rds, user, token):
        return False

    share_cnt_owned = rds.get('shares_' + user + '_' + company)
    if share_cnt_owned is None:
        return False
    
    share_cnt_owned = int(share_cnt_owned.decode('utf-8'))
    if share_cnt_owned < share_cnt:
        return False

    user_cash = rds_get_user_cash(rds, user, token)
    rds.set('cash_' + user, user_cash + share_cnt * price)
    new_shares_cnt = rds.decrby('shares_' + user + '_' + company, share_cnt)
    if new_shares_cnt < 1:
        rds.srem('companies_' + user, company)
    return True
