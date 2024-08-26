from dash import Dash
import flask

flask_server = flask.Flask(__name__)

app = Dash(__name__, server=flask_server, routes_pathname_prefix="/dash/", use_pages=True)
