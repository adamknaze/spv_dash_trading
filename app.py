import dash
import redis
import datetime
import db_utils as utils

UPDATE_COOLDOWN = datetime.timedelta(0, 30)
last_prices_update = datetime.datetime.now()

rds = redis.Redis()

companies = utils.rds_get_companies(rds)
prices_df = utils.read_prices_from_rds(rds)
global_last_row = utils.rds_get_last_row(rds)

stylesheets = ['assets\\styles.css']

dash_app = dash.Dash(__name__, external_stylesheets=stylesheets, suppress_callback_exceptions=True)

application = dash_app.server
