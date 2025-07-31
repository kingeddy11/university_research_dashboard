from dash import Dash, html, dcc, Input, Output, State, ctx, no_update
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import mysql.connector

# Utility imports
from utils import mysql_utils, mongodb_utils, neo4j_utils


## Using Bootstrap for styling
app = Dash(external_stylesheets = [dbc.themes.BOOTSTRAP])


## Defining color palette
palette = {
    "dark_slate": "#354551", # RGB(53, 69, 81)
    "navy": "#1c4c74", # RGB(28, 76, 116)
    "bright_blue": "#349ce4", # RGB(52, 156, 228)
    "sky_blue": "#6cb4e4", # RGB(108, 180, 228)
    "blue_gray": "#648cac", # RGB(100, 140, 172)
    "gray": "#b2b6b0" # RGB(178, 182, 176)
}


## Illinois logo
logo_url = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAKoAAACtCAMAAAAXrRQIAAAAM1BMVEUZKErtaBr////2s4z0oHA2Q2H4xqmprrvFydHvezfxjVP97OL3vZr1qn7zl2H72cbucij3f17tAAAA8ElEQVR4nO3bQQ6CMBRFURBEAUH3v1qnKE1oBD+QnDtvOGHYvBaFJEmSJEmSpJgum3ZFRf0rtao3aAihduUGtaioqKioqKioqKioqKgnoTbVtDEX1w3TY48Q6ld9m/UXn3vcA8ysrwxqnzoZf7syLEvH5MF4arNMreKps2751HsoDBUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFRUVFXU3anLYc8xFUPKL9TK1Owa1X5aWZWpnd9RNYGppF7u0HLInonssLU+0X0VFRUVFRUVFRUVFRUVdT/18G/hju7wNXBEqqiRJkiRJkqSI3piBLYHQTbD9AAAAAElFTkSuQmCC"


## Get dropdown options for universities from MySQL
university_options_mysql = mysql_utils.get_all_universities()


## Get dropdown options for universities from MongoDB
university_options_mongo = mongodb_utils.get_all_universities()


## Get [min, max] publication year range for year range slider
publication_year_range = mongodb_utils.get_publication_year_range()


## Alter university table to set name in university table to not null and unique (only run once)
# mysql_utils.alter_university_table()


## Creating widgets and components
# Widget card outline
def create_widget_card(title, content = None, bg_color = palette["navy"], text_color = "#FFFFFF", size = "large"):
    # Style variants for size
    size_styles = {
        "large": {"fontSize": "24px"},
        "small": {"fontSize": "20px"},
    }

    style = size_styles[size]

    return dbc.Card(
        dbc.CardBody([
            html.H4(
                title, 
                style = {
                    "fontSize": style["fontSize"],
                    "textAlign": "center",
                    "alignItems": "center"
                }
            ),
            content if content else html.Div("No content available", style={"textAlign": "center"}),
        ]),
        style = {
            "backgroundColor": bg_color,
            "color": text_color,
            "height": "100%",
            "display": "flex"
        }
    ) 

# Top Left Widget
def create_top_left_widget():
    return html.Div([
        dbc.Label("Select University:"),
        dcc.Dropdown(
            id = "citation-search-input",
            options = [{"label": univ, "value": univ} for univ in university_options_mongo],
            value = university_options_mongo[0] if university_options_mongo else None,
            multi = False,
            placeholder = "Select a university",
            style = {"color": "#000000"},
            className = "mb-2"

        ),
        dcc.Graph(id='citation-ranking-chart', style={"width": "100%", "height": "400px"}),
    ])

# Top Right Widget
def create_top_right_widget():
    return html.Div(
        [
            # University dropdown
            dbc.Label("Select Universities:"),
            dcc.Dropdown(
               id = "university-dropdown",
               options = [{"label": univ, "value": univ} for univ in university_options_mongo],
               multi = True,
               placeholder = "Select one or more universities",
               style = {"color": "#000000"},
               className = "mb-2"
            ),

            # Year range slider
            dbc.Label("Select Year Range:"),
            dcc.RangeSlider(
                id = "year-range-slider",
                min = publication_year_range[0],
                max = publication_year_range[1],
                step = 1,
                marks = {
                    year: {"label": str(year), "style": {"color": "#FFFFFF"}}
                    for year in range(publication_year_range[0], publication_year_range[1] + 1, 10)
                },
                value = publication_year_range,
                tooltip = {"always_visible": False, "placement": "bottom"},
                className = "mb-2"
            ),

            # Line chart
            dcc.Graph(
                id = "university-publications-over-time", 
                style = {"width": "100%", "height": "100%"}   
            )
        ]
    )

# Middle Left Widget
def create_middle_left_widget():
    return html.Div(
        [
            # Auto-complete input for keywords
            dbc.Label("Enter Keywords:"),
            dcc.Dropdown(
                id = "keyword-input",
                options = [],
                multi = True,
                placeholder = "Type to search or select keywords",
                style = {"color": "#000000"},
                className = "mb-2"
            ),

            # Bar chart
            dcc.Graph(
                id = "top-universities-by-keyword-score",
                style = {"width": "100%", "height": "400px"}
            )
        ]
    )

# Middle Right Widget
def create_middle_right_widget():
    return html.Div([
        dbc.Label("Enter Keyword:"),
        dcc.Dropdown(
                id = "krc-keyword-input",
                options = [],
                multi = False,
                placeholder = "Type to search or select keywords",
                style = {"color": "#000000"},
                className = "mb-2"
            ),
        dcc.Graph(id="krc-bar-chart", style={"width": "100%", "height": "400px"})
    ])

# Bottom Left Widget 1
def create_bottom_left_widget1():
    return html.Div(
        [
            # Input fields for add operation
            dbc.Input(
                id = "add-univ-name", 
                placeholder = "University Name (Required)", 
                type = "text", 
                className = "mb-2"
            ),
            dbc.Input(
                id = "add-univ-photo", 
                placeholder = "Photo URL (Optional)", 
                type = "text", 
                className = "mb-2"
            ),

            # add operation button
            dbc.Button("Add", id = "add-univ-btn", color = "success", className = "mt-2"),
            html.Div(id = "add-status", className = "mt-3")  
        ]
    )

# Bottom Left Widget 2
def create_bottom_left_widget2():
    return html.Div(
        [
            # University dropdown for delete operation
            dcc.Dropdown(
                id = "delete-univ",
                options = [{"label": univ, "value": univ} for univ in university_options_mysql],
                placeholder = "Select a university to delete"
            ),

            # Delete button
            dbc.Button("Delete", id = "delete-univ-btn", color = "danger", className = "mt-2"),
            html.Div(id = "delete-status", className = "mt-3")
        ]
    )

def create_bottom_right_widget():
    return html.Div([
        dbc.Label("Select University:"),
        dcc.Dropdown(
            id = "update-pub-univ-input",
            options = [{"label": univ, "value": univ} for univ in university_options_mongo],
            value = university_options_mongo[0] if university_options_mongo else None,
            multi = False,
            placeholder = "Select a university",
            style = {"color": "#000000"},
            className = "mb-2"
        ),
        dcc.Dropdown(
            id='faculty-dropdown', 
            placeholder="Select Faculty",
            className="mb-2"
        ),
        html.Div(
            dcc.Dropdown(
                id='publication-dropdown',
                placeholder="Select Publication",
                className="mb-2"
            ),
            id="publication-dropdown-container"
        ),
        html.Div(
            dbc.Button("Add", id="add-publication-btn", color="success", className="me-1"),
            className="mt-2",
            id="add-btn-container"
        ),
        html.Div([
            dbc.Button("Edit", id="edit-publication-btn", color="warning", className="me-1"),
            dbc.Button("Delete", id="delete-publication-btn", color="danger")
        ], className="mt-2", id="edit-delete-btn-container"),
        html.Div(id="delete-pub-status", className="mt-2"), 
        html.Div(id="add-pub-status", className="mt-2"),
    ])

# Add Publication Modal
add_pub_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Add Publication")),
        dbc.ModalBody([
            dbc.Input(id="add-pub-title", placeholder="Title", type="text", className="mb-2"),
            dbc.Input(id="add-pub-venue", placeholder="Venue", type="text", className="mb-2"),
            dbc.Input(id="add-pub-year", placeholder="Year", type="number", className="mb-2"),
        ]),
        dbc.ModalFooter([
            dbc.Button("Add", id="confirm-add-pub", color="success", className="me-2"),
            dbc.Button("Cancel", id="cancel-add-pub", color="secondary")
        ]),
    ],
    id="add-pub-modal",
    is_open=False,
)

# Update Publication Modal
update_pub_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Update Publication")),
        dbc.ModalBody([
            dbc.Input(id="update-pub-title", placeholder="Title", type="text", className="mb-2"),
            dbc.Input(id="update-pub-venue", placeholder="Venue", type="text", className="mb-2"),
            dbc.Input(id="update-pub-year", placeholder="Year", type="number", className="mb-2"),
            dbc.Input(id="update-pub-num-citations", placeholder="Number of Citations", type="number", className="mb-2"),
        ]),
        dbc.ModalFooter([
            dbc.Button("Update", id="confirm-update-pub", color="primary", className="me-2"),
            dbc.Button("Cancel", id="cancel-update-pub", color="secondary")
        ]),
    ],
    id="update-pub-modal",
    is_open=False,
)
## Layout of the app
# Main layout
app.layout = [
    dcc.Store(id="add-refresh-trigger", data=0),
    dcc.Store(id="delete-refresh-trigger", data=0),
    dcc.Store(id="pub-refresh-trigger", data=0),
    html.Div(
        style = {"backgroundColor": palette["dark_slate"], "minHeight": "100vh"},
        children = [
            # Header
            html.Div(
                style = {
                    "backgroundColor": palette["blue_gray"], 
                    "padding": "5px",
                    "margin": "0 auto",
                    "textAlign": "center",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "space-between",
                    "marginBottom": "16px"
                },
                children = [
                    html.H1(
                        children = "University Research Insights",
                        style = {
                            "textAlign": "center", 
                            "color": "#FFFFFF",
                            "margin": "0 auto",
                        }
                    ),
                    html.Img(
                        src = logo_url,
                        style = {
                            "height": "50px"
                        }
                    )
                ]
            ),
            # Widget rows
            dbc.Container(
                fluid = True,
                style = {
                    # "height": "calc(100vh - 140px)"
                    "flex": "1",
                    "display": "flex",
                    "flexDirection": "column",
                    "height": "100%",
                    "overflow": "hidden",
                    "padding": "0 16px"
                },
                children =[
                    # First row widgets
                    dbc.Row([
                       dbc.Col(create_widget_card(
                            title="Faculty Citation Rankings by University",
                            content=create_top_left_widget(),
                            bg_color=palette["navy"],
                            text_color = "#FFFFFF",
                            size="large"
                        ), width=6),
                        dbc.Col(create_widget_card(
                            title = "University Publications Over Time", 
                            content = create_top_right_widget(),
                            bg_color = palette["navy"], 
                            text_color = "#FFFFFF",
                            size = "large"
                        ), width = 6),
                    ], style = {"flex": "3"}, className = "mb-3"),

                    # Second row widgets
                    dbc.Row([
                        dbc.Col(create_widget_card(
                            title = "Top Universities by Faculty Keyword Score", 
                            content = create_middle_left_widget(),
                            bg_color = palette["bright_blue"], 
                            text_color = "#FFFFFF",
                            size = "large"
                        ), width = 6),
                        dbc.Col(create_widget_card(
                            title = "Top Universities by Publication Keyword-Relevant Citation Score (KRC)", 
                            content = create_middle_right_widget(),
                            bg_color = palette["bright_blue"], 
                            text_color = "#FFFFFF",
                            size = "large"
                        ), width = 6),
                    ], style = {"flex": "3"}, className = "mb-3"),

                    # Third row widgets
                    dbc.Row([
                        dbc.Col(create_widget_card(
                            title = "Add University", 
                            content = create_bottom_left_widget1(),
                            bg_color = palette["gray"], 
                            text_color = "#000000",
                            size = "large"
                        ), width = 6),
                        dbc.Col(create_widget_card(
                            title = "Update Publications",
                            content = create_bottom_right_widget(),  
                            bg_color = palette["gray"], 
                            text_color = "#000000",
                            size = "large"
                        ), width = 6),
                    ], style = {"flex": "2"}, className = "mb-3"),

                    # Fourth row widgets
                    dbc.Row([
                        dbc.Col(create_widget_card(
                            title = "Delete University",
                            content = create_bottom_left_widget2(),
                            bg_color = palette["gray"], 
                            text_color = "#000000",
                            size = "large"
                        ), width = 6),
                    ], style = {"flex": "2"})
                ]
            ),
            # Add Publication Modal
            dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Add Publication")),
        dbc.ModalBody([
            dbc.Input(id="add-pub-title", placeholder="Title", type="text", className="mb-2"),
            dbc.Input(id="add-pub-venue", placeholder="Venue", type="text", className="mb-2"),
            dbc.Input(id="add-pub-year", placeholder="Year", type="number", className="mb-2"),
        ]),
        dbc.ModalFooter([
            dbc.Button("Add", id="confirm-add-pub", color="success", className="me-2"),
            dbc.Button("Cancel", id="cancel-add-pub", color="secondary")
        ]),
    ],
    id="add-pub-modal",
    is_open=False,
),

# Update Publication Modal
dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Update Publication")),
        dbc.ModalBody([
            dbc.Input(id="update-pub-title", placeholder="Title", type="text", className="mb-2"),
            dbc.Input(id="update-pub-venue", placeholder="Venue", type="text", className="mb-2"),
            dbc.Input(id="update-pub-year", placeholder="Year", type="number", className="mb-2"),
            dbc.Input(id="update-pub-num-citations", placeholder="Number of Citations", type="number", className="mb-2"),
        ]),
        dbc.ModalFooter([
            dbc.Button("Update", id="confirm-update-pub", color="primary", className="me-2"),
            dbc.Button("Cancel", id="cancel-update-pub", color="secondary")
        ]),
    ],
    id="update-pub-modal",
    is_open=False,
)
        ]
    )
]


## Callbacks for interactivity
# Callback to update the citation ranking chart in top left widget
@app.callback(
    Output("citation-ranking-chart", "figure"),
    Input("citation-search-input", "value")
)

def update_citation_table(search_value):
    if not search_value:
        return []
    try:
        rows = mysql_utils.get_citation_ranking(search_value)
        if not rows:
            return go.Figure()  # Return empty if no data
    
        df = pd.DataFrame(rows)
        # Convert Decimal to int
        df['totalCitations'] = df['totalCitations'].apply(int)
    
        fig = px.pie(df, names='name', values='totalCitations', title='Total Citations by Faculty')
        fig.update_layout(margin=dict(t=40, b=40, l=40, r=40))
        return fig
    except Exception as e:
        print("Error fetching citations:", e)
        return []
    

# Callback to update line chart in top right widget
@app.callback(
    Output("university-publications-over-time", "figure"),
    Input("university-dropdown", "value"),
    Input("year-range-slider", "value")
)

def update_line_chart(selected_universities, selected_years):
    """
    Update the line chart based on selected universities and publication year range.

    Parameters
    ----------
    selected_universities : list
        List of selected universities from the dropdown.
    selected_years : list of length 2
        List of selected years from the year range slider, i.e. [start_year, end_year].
    
    Returns
    -------
    go.Figure
        A Plotly line chart showing university publication counts over time.
    """

    # Return empty figure if no years are selected
    if not selected_years:
        return go.Figure()
    
    # Query MongoDB for data
    data = mongodb_utils.top_right_query(
        universities = selected_universities,
        years = selected_years
    )

    # Return empty figure if no data is returned
    if not data:
        return go.Figure()
    
    # Create dataframe
    df = pd.DataFrame(data)
    df["university"] = df["_id"].apply(lambda x: x["university"])
    df["year"] = df["_id"].apply(lambda x: x["year"])
    df = df[["university", "year", "university_publications"]]
    df = df.sort_values(by = ["university", "year"])

    # Create line chart
    fig = px.line(
        df,
        x = "year",
        y = "university_publications",
        color = "university",
        markers = True,
        labels = {
            "year": "Publication Year", 
            "university_publications": "Number of Publications", 
            "university": "University/Universities"
        }
    )

    fig.update_layout(
        plot_bgcolor = "white",
        margin = dict(l = 40, r = 20, t = 40, b = 40),
        autosize = True,
        legend = dict(
            font = dict(size = 10),
            x = 1.02,
            y = 1,
            xanchor = "left"
        )
    )

    return fig


# Callback to update keyword search options in middle left and right widgets
@app.callback(
    Output("keyword-input", "options"),
    Output("krc-keyword-input", "options"),
    Output("krc-keyword-input", "value"),
    Input("keyword-input", "search_value"),
    Input("krc-keyword-input", "search_value"),
    State("keyword-input", "value"),
    State("krc-keyword-input", "value")
)

def update_keyword_dropdown(search_value1, search_value2, selected_1, selected_2):
    """
    Shared callback to provide keyword options for both dropdowns independently.
    """
    # Ensure both selected values are lists
    selected_1 = selected_1 if isinstance(selected_1, list) else [selected_1] if selected_1 else []
    selected_2 = selected_2 if isinstance(selected_2, list) else [selected_2] if selected_2 else []

    # Prioritize whichever search input was used
    search_value = search_value1 or search_value2

    if not search_value:
        default_keywords = mysql_utils.get_all_keywords()
        merged_1 = list(dict.fromkeys(selected_1 + default_keywords))
        merged_2 = list(dict.fromkeys(selected_2 + default_keywords))
    else:
        matches = mysql_utils.search_keywords_by_prefix(search_value)
        merged_1 = list(dict.fromkeys(selected_1 + matches))
        merged_2 = list(dict.fromkeys(selected_2 + matches))

    dropdown_options_1 = [{"label": kw, "value": kw} for kw in merged_1]
    dropdown_options_2 = [{"label": kw, "value": kw} for kw in merged_2]

    # Decide the default value for krc-keyword-input dropdown:
    # If the current selected value is None or not in the options, set it to the first option
    current_value = selected_2[0] if selected_2 else None
    if current_value not in [opt["value"] for opt in dropdown_options_2]:
        default_value = dropdown_options_2[0]["value"] if dropdown_options_2 else None
    else:
        default_value = current_value

    return dropdown_options_1, dropdown_options_2, default_value


# Callback to update bar chart in middle left widget
@app.callback(
    Output("top-universities-by-keyword-score", "figure"),
    Input("keyword-input", "value")
)

def update_bar_chart(selected_keywords):
    """
    Update the bar chart based on selected keywords.
    
    Parameters
    ----------
    selected_keywords: list
        List of selected keywords from the dropdown.
        
    Returns
    -------
    go.Figure
        A Plotly bar chart showing the top universities by keyword score for selected keywords.
    """

    # If no keywords selected, return empty figure
    if not selected_keywords:
        return go.Figure()
    
    # Query MySQL for top universities by keyword score
    data = mysql_utils.middle_left_query(selected_keywords)

    # Return empty figure if no data is returned
    if not data:
        return go.Figure()
    
    # Create dataframe
    df = pd.DataFrame(data, columns = ["university_name", "total_keyword_score"])

    # Create bar chart
    fig = px.bar(
        df,
        x = "university_name",
        y = "total_keyword_score",
        color = "university_name",
        labels = {
            "university_name": "University",
            "total_keyword_score": "Total Keyword Score"
        }
    )

    fig.update_layout(
        plot_bgcolor = "white",
        margin = dict(l = 40, r = 20, t = 40, b = 40),
        autosize = True,
        xaxis_tickangle = 45,
        showlegend = False
    )

    return fig

# Callback to update the KRC bar chart in middle right widget
@app.callback(
    Output("krc-bar-chart", "figure"),
    Input("krc-keyword-input", "value"),
    prevent_initial_call=True
)
def update_krc_chart(keyword):
    if not keyword:
        return go.Figure()

    try:
        data = neo4j_utils.get_krc(keyword)
        if not data:
            return go.Figure()

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Plot
        fig = px.bar(
            df,
            x="university",
            y="totalKRC",
            color="university",
            labels={
                "university": "University",
                "totalKRC": "Total KRC"
            }
        )
        fig.update_layout(
            plot_bgcolor="white",
            margin=dict(l=40, r=20, t=40, b=40),
            xaxis_tickangle=45,
            showlegend=False
        )
        return fig

    except Exception as e:
        print(f"Error in KRC query: {e}")
        return go.Figure()

# Callback to insert a new university into university table (bottom left widget 1)
@app.callback(
    Output("add-status", "children"),
    Output("add-univ-name", "value"),
    Output("add-univ-photo", "value"),
    Output("add-refresh-trigger", "data"),
    Input("add-univ-btn", "n_clicks"),
    State("add-univ-name", "value"),
    State("add-univ-photo", "value"),
    prevent_initial_call=True
)

def add_university(n_clicks, name, photo_url):
    """
    Insert a new university into the university table.

    Parameters
    ----------
    n_clicks : int
        Number of times the add button has been clicked.
    name : str
        The name of the university to add.
    photo_url : str, optional
        The URL of the university's photo to add.
    """

    if not name:
        return "University name is required.", no_update, no_update, no_update

    try:
        new_id = mysql_utils.insert_university(name, photo_url)
        return (f'University "{name}" added successfully.', None, None, n_clicks)

    except mysql.connector.errors.IntegrityError as e:
        if "Duplicate entry" in str(e):
            return f'A university named "{name}" already exists.', no_update, no_update, no_update
        return f'Integrity error: {e}', no_update, no_update, no_update

    except Exception as e:
        return f'Error adding university: {e}', no_update, no_update, no_update


# Callback to delete university from university table (bottom left widget 2)
@app.callback(
    Output("delete-status", "children"),
    Output("delete-univ", "value"),
    Output("delete-refresh-trigger", "data"),
    Input("delete-univ-btn", "n_clicks"),
    State("delete-univ", "value"),
    prevent_initial_call=True
)

def delete_university(n_clicks, name):
    """
    Delete a university from the university table.
    
    Parameters
    ----------
    n_clicks : int
        Number of times the delete button has been clicked.
    name : str
        The name of the university to delete.
    """

    if not name:
        return "University name is required.", no_update, no_update

    try:
        mysql_utils.delete_university(name)
        return (f'University "{name}" deleted successfully.', None, n_clicks)

    except mysql.connector.errors.IntegrityError as e:
        if "Foreign key constraint" in str(e):
            return f'Cannot delete "{name}" as it is a foreign key and is referenced by other records in the faculty table.'
        return f'Integrity error: {e}', no_update, no_update

    except Exception as e:
        return f'Error deleting university: {e}', no_update, no_update

# Callback to refresh university dropdown options after add/delete operations
@app.callback(
    Output("delete-univ", "options"),
    Input("add-refresh-trigger", "data"),
    Input("delete-refresh-trigger", "data")
)

def refresh_delete_dropdown(_, __):
    """ 
    Refresh the dropdown options for the delete university widget.
    """

    universities = mysql_utils.get_all_universities()
    return [{"label": univ, "value": univ} for univ in universities]

@app.callback(
    Output("faculty-dropdown", "options"),
    Input("update-pub-univ-input", "value")
)
def update_faculty_options(university_name):
    if not university_name:
        return []
    faculty = mysql_utils.get_faculty_by_university(university_name)
    if not faculty:
        return []
    return [{"label": f["name"], "value": f["id"]} for f in faculty]

@app.callback(
    Output("publication-dropdown", "options"),  # <-- Add this line
    Input("faculty-dropdown", "value"),
    Input("pub-refresh-trigger", "data"),
)
def update_publication_options(faculty_id, pub_refresh):
    if not faculty_id:
        return []
    pubs = mysql_utils.get_publications_by_faculty(faculty_id)
    if not pubs:
        return []
    def abbreviate(title, max_len=60):
        return title if len(title) <= max_len else title[:max_len] + "..."
    return [{"label": abbreviate(p["title"]), "value": p["id"]} for p in pubs]

@app.callback(
    Output("add-pub-modal", "is_open"),
    [Input("add-publication-btn", "n_clicks"), Input("confirm-add-pub", "n_clicks"), Input("cancel-add-pub", "n_clicks")],
    [State("add-pub-modal", "is_open")],
    prevent_initial_call=True
)
def toggle_add_pub_modal(open_click, confirm_click, cancel_click, is_open):
    triggered = ctx.triggered_id
    if triggered == "add-publication-btn":
        return True
    elif triggered in ("confirm-add-pub", "cancel-add-pub"):
        return False
    return is_open

@app.callback(
    Output("update-pub-modal", "is_open"),
    [Input("edit-publication-btn", "n_clicks"), Input("confirm-update-pub", "n_clicks"), Input("cancel-update-pub", "n_clicks")],
    [State("update-pub-modal", "is_open")],
    prevent_initial_call=True
)
def toggle_update_pub_modal(open_click, confirm_click, cancel_click, is_open):
    triggered = ctx.triggered_id
    if triggered == "edit-publication-btn":
        return True
    elif triggered in ("confirm-update-pub", "cancel-update-pub"):
        return False
    return is_open

@app.callback(
    Output("update-pub-title", "value"),
    Output("update-pub-venue", "value"),
    Output("update-pub-year", "value"),
    Output("update-pub-num-citations", "value"),
    Input("edit-publication-btn", "n_clicks"),
    State("publication-dropdown", "value"),
    prevent_initial_call=True
)
def fill_update_pub_modal(edit_clicks, pub_id):
    if not pub_id:
        return "", "", "", ""
    pub = mysql_utils.get_publication(pub_id)
    if not pub:
        return "", "", "", ""
    return pub.get("title", ""), pub.get("venue", ""), pub.get("year", ""), pub.get("num_citations", "")

@app.callback(
    Output("update-pub-modal", "is_open", allow_duplicate=True),
    Input("confirm-update-pub", "n_clicks"),
    State("publication-dropdown", "value"),
    State("update-pub-title", "value"),
    State("update-pub-venue", "value"),
    State("update-pub-year", "value"),
    State("update-pub-num-citations", "value"),
    prevent_initial_call=True
)
def update_publication(confirm_click, pub_id, title, venue, year, num_citations):
    if confirm_click and pub_id:
        mysql_utils.update_publication(pub_id, {
            "title": title,
            "venue": venue,
            "year": year,
            "num_citations": num_citations
        })
        return False  # Close modal
    return no_update


@app.callback(
    Output("publication-dropdown-container", "style"),
    Output("add-btn-container", "style"),
    Output("edit-delete-btn-container", "style"),
    Input("faculty-dropdown", "value"),
    Input("publication-dropdown", "value"),
)
def toggle_pub_dropdown_and_buttons(faculty_id, pub_id):
    # Show publication dropdown only if faculty is selected
    pub_dropdown_style = {} if faculty_id else {"display": "none"}
    # Show Add button only if faculty is selected
    add_btn_style = {} if faculty_id else {"display": "none"}
    # Show Edit/Delete only if publication is selected
    edit_delete_style = {} if pub_id else {"display": "none"}
    return pub_dropdown_style, add_btn_style, edit_delete_style

@app.callback(
    Output("add-pub-modal", "is_open", allow_duplicate=True),
    Output("add-pub-title", "value"),
    Output("add-pub-venue", "value"),
    Output("add-pub-year", "value"),
    Output("add-pub-status", "children"),
    Output("delete-pub-status", "children"),
    Output("publication-dropdown", "value"),
    Output("pub-refresh-trigger", "data"),
    Input("confirm-add-pub", "n_clicks"),
    Input("delete-publication-btn", "n_clicks"),
    State("add-pub-title", "value"),
    State("add-pub-venue", "value"),
    State("add-pub-year", "value"),
    State("faculty-dropdown", "value"),
    State("publication-dropdown", "value"),
    State("pub-refresh-trigger", "data"),
    prevent_initial_call=True
)
def add_or_delete_publication(
    add_click, delete_click,
    title, venue, year, faculty_id, pub_id, pub_refresh
):
    triggered = ctx.triggered_id
    # Add publication
    if triggered == "confirm-add-pub" and add_click and faculty_id and title:
        try:
            pub_id_new = mysql_utils.add_publication(faculty_id, {
                "title": title,
                "venue": venue,
                "year": year,
                "num_citations": 0
            })
            return False, "", "", "", "Publication added successfully.", no_update, no_update, (pub_refresh or 0) + 1
        except Exception as e:
            return no_update, no_update, no_update, no_update, f"Error adding publication: {e}", no_update, no_update, no_update

    # Delete publication
    if triggered == "delete-publication-btn" and delete_click and pub_id:
        try:
            mysql_utils.delete_publication(pub_id)
            return no_update, no_update, no_update, no_update, no_update, "Publication deleted successfully.", None, (pub_refresh or 0) + 1
        except Exception as e:
            return no_update, no_update, no_update, no_update, no_update, f"Error deleting publication: {e}", no_update, no_update

    return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update
# Run the app
if __name__ == '__main__':
    app.run(debug = False)
