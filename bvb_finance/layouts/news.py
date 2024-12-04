import dash
import pandas as pd
import dash
import itertools
import random
import typing
import dash_bootstrap_components as dbc
from bvb_finance.news import static as static_news
from bvb_finance.news import UIActiveComponent
from bvb_finance import logging

logger = logging.getLogger()

def get_layout():
    return dash.html.Div([
        dash.html.H3(children="Stock Market News Aggregator"),
        dbc.Nav([
                dbc.NavItem(dbc.NavLink("World", id="nav-link-world")),
                dbc.NavItem(dbc.NavLink("Romania", id="nav-link-romania", active=True)),
            ],
            pills=True
        ),
        dash.html.Br(),
        dash.html.Div(id='output-container')
    ])

output_container_flex_grid_style = {
    "padding-left": "2%",
    "padding-right": "2%",
    "display": "flex",
    "flex-direction": "row",
}

nav_menu_component_name = "nav_menu_component_name"
UIActiveComponent.register_components(nav_menu_component_name, 2)

@dash.callback(
    dash.Output(component_id='output-container', component_property='children', allow_duplicate=True),
    dash.Input(component_id='nav-link-world', component_property='n_clicks'),
    dash.Input(component_id='nav-link-romania', component_property='n_clicks'),
    prevent_initial_call=True
)
def nav_menu_callback(nav_link_world, nav_link_romania):
    global nav_menu_component_name
    nav_states = ["world", "romania"]
    active_component: UIActiveComponent.ActiveComponent =\
      UIActiveComponent.update_components(nav_menu_component_name, [nav_link_world, nav_link_romania])
    last_clicked: str = nav_states[active_component.index]

    return dash.html.Div(id='output-container-flex-grid',
                         style=output_container_flex_grid_style,
                         children=[
            get_sidebar(last_clicked),
            dash.html.Div([dash.html.P("news content")],
                          id='news_page-container',
                          style={
                              "margin": "auto",
                              "border": "3px solid red",
                              "flex": "3",
                          })
        ])


sidebar_style = {
    "padding": "2rem 1rem",
    "flex": "1"
}

news_source_btns_component_name = "news_source_btns_component_name"

def get_sidebar(news_region: str):
    global news_source_btns_component_name
    
    news_sources_btns: list[dash.html.Button] = new_romania_layout()

    UIActiveComponent.register_components(news_source_btns_component_name, len(news_sources_btns))
    
    sidebar = dash.html.Div(
        [
            # dash.dcc.Location(id="news-url"),
            dash.html.P(f"News for {news_region} region", className="lead"),
            *news_sources_btns
        ],
         style=sidebar_style,
    )
    return sidebar


@dash.callback(
    dash.Output(component_id='news_page-container', component_property='children', allow_duplicate=True),
    # dash.Input(component_id='news-url', component_property='pathname'),
    dash.Input(component_id={"type": "news-source-btn", "index": dash.ALL}, component_property="n_clicks"),
    dash.State(component_id={"type": "news-source-btn", "index": dash.ALL}, component_property="data-*"),
    prevent_initial_call=True
)
def load_news_callback(news_source_btn_clicks_list, news_source_btn_url_list):
    global news_source_btns_component_name
    active_component: UIActiveComponent.ActiveComponent =\
      UIActiveComponent.update_components(news_source_btns_component_name, news_source_btn_clicks_list)
    clicked_btn_url: str = news_source_btn_url_list[active_component.index]

    return [
        dash.html.Div(f"News Source {clicked_btn_url}")
    ]
    return [
        dash.html.P(f"Displaying url {url}", className="lead"),
        dash.html.Iframe(src="https://cursdeguvernare.ro/")
    ]

def new_romania_layout():
    theme_colors = [
        "AntiqueWhite",
        "Aqua",
        "LightYellow",
        "Chocolate",
        "DarkGreen",
        "DarkSlateGrey",
        "FireBrick",
        "Lavender",
        "LawnGreen",
        "MistyRose"
    ]
    buttons = list()
    for news in static_news.romania_news:
        buttons.append(
            dash.html.Button(news.description,
                             className="news-source-button",
                       id={
                           "type": "news-source-btn",
                           "index": news.description,
                       },
                       **{
                           "data-*": news.url,
                       },
                       style={
                           "background-color": random.choice(theme_colors),
                       }),
        )
    return buttons