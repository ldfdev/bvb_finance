from dash import Dash

app = Dash()

def getLogger():
    return app.server.logger
