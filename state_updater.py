import datetime
import time
import redis
import db_utils as utils
import numpy as np
import pandas as pd


def iterate_prices(rds, time=None):

    print('generating new prices')

    trend = np.random.randint(-50,60)
    price_row = np.array(utils.rds_get_current_prices(rds))
    random_elements = np.random.randint(-70, 85, price_row.shape[0])

    new_prices = (price_row * (trend + random_elements + 1000)) / 1000

    last_row = rds.get('last_row').decode('utf-8')

    last_time = time
    if last_time is None:
        last_time = datetime.datetime.now()
    last_time = pd.to_datetime(last_time)

    rds.rpush('row_'+last_row, *([str(last_time)] + list(new_prices)))
    rds.incr('last_row')


def store_account_balances(rds, users, companies):

    print('updating account balances')

    share_prices = {}
    price_row = utils.rds_get_current_prices(rds)

    for i, cmp in enumerate(companies):
        share_prices[cmp] = price_row[i]

    rds.rpush('balance_timestamps', str(datetime.datetime.now()))

    for user in users:
        user_value = utils.rds_get_user_cash(rds, user)
        user_companies = utils.rds_get_user_companies(rds, user)
        for cmp in user_companies:
            user_value += utils.rds_get_user_cmp_share_cnt(rds, user, cmp) * share_prices[cmp]
        
        rds.rpush('user_balance_' + user, str(user_value))


def main_loop(update_freq=60):

    rds = redis.Redis()

    users = [x.decode('utf-8') for x in rds.keys('pass_*')]
    users = [x[5:] for x in users]
    companies = utils.rds_get_companies(rds)

    while True:

        print('new interation at', datetime.datetime.now())

        iterate_prices(rds)

        store_account_balances(rds, users, companies)

        time.sleep(update_freq)


if __name__ == '__main__':

    main_loop()
