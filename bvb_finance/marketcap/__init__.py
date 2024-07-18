import bvb_finance

flask_server = bvb_finance.app.serverss

@flask_server.route("/marketcap")
def hello_world():
    return "<p>Hello, World!</p>"