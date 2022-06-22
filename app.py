import dash
from dash import dcc, html
import pandas as pd
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from jupyter_dash import JupyterDash
import plotly.express as px


# DATA PREPARATION AND PREPROCESSING
df = pd.read_csv("https://raw.githubusercontent.com/NanaK99/data_viz/master/spotify.csv")

df = df.drop('Unnamed: 0', axis=1)
df.rename(columns={'target': 'hit'}, inplace=True)

cols = list(df.columns)
num_cols = list(df.select_dtypes('number').columns)
cat_cols = ['key', 'mode', 'time_signature', 'hit', 'year']
cat_cols_without_year = ['key', 'mode', 'time_signature', 'hit']
num_cols = [col for col in num_cols if col not in cat_cols]
years = list(df['year'].unique())

for num_col in num_cols:
    df[num_col] = df[num_col].round(decimals=2)

df['duration_min'] = (round(df['duration_ms']/60000, 0)).astype('int32')
df = df.drop('duration_ms', axis=1)

num_cols.remove('duration_ms')
num_cols.append('duration_min')

num_cat_cols = num_cols + cat_cols


app = JupyterDash(__name__, external_stylesheets=[dbc.themes.DARKLY])

app.layout = dbc.Container([
        dbc.Row(dbc.Col(html.H2('SPOTIFY SONG ANALYSIS', className='text-center text-primary, mb-3'))),

        dbc.Row(dbc.Col(html.H5("The dataset contains approximately 15 features for the songs. Some features are self-descriptive, some are not.",
                                className='text-center text-primary, mb-3'))),

        dbc.Row([
            dbc.Col([
                html.H5('Top artists according to different criteria', className='text-center'),
                html.Div([dcc.Dropdown(id='first_col',
                                       options=[{'label': i, 'value': i} for i in num_cols],
                                       value='duration_min',
                                       style={'color': 'black'})]),
                html.Div([dcc.Dropdown(id='num_top_artists',
                                       options=[{'label': i, 'value': i} for i in range(5, 21, 5)],
                                       value=10,
                                       style={'color': 'black'})]),

                dcc.Graph(id='top_artists',
                          style={'height': 365}),
                html.Hr(),
            ], width={'size': 6, 'offset': 0, 'order': 1}),

            dbc.Col([
                html.H5('Relationship between two variables (categorical vs. numerical)', className='text-center'),
                html.Div([dcc.Dropdown(id='col',
                                       placeholder="Please choose the feature for the x-axis",
                                       value="mode",
                                       options=[{'label': i, 'value': i} for i in cat_cols_without_year],
                                       style={'color': 'black'})]),
                html.Div([dcc.Dropdown(id='second_col',
                                       placeholder="Please choose the feature for the y-axis",
                                       value="valence",
                                       options=[{'label': i, 'value': i} for i in num_cols],
                                       style={'color': 'black'})]),
                html.Div([dcc.Dropdown(id='year_col',
                                       options=[{'label': i, 'value': i} for i in range(1960, 2011, 10)],
                                       value=2000,
                                       style={'color': 'black'})]),


                dcc.Graph(id='boxplot',
                          style={'height': 330}),
                html.Hr(),
        ], width={'size': 6, 'offset': 0, 'order': 2})
    ]),

    dbc.Row([
        html.H5('Relationship between two variables (numerical)', className='text-center'),
        html.Div([dcc.Dropdown(id='first_num_col',
                               options=[{'label': i, 'value': i} for i in num_cols],
                               value='duration_min',
                               style={'color': 'black'})]),
        html.Div([dcc.Dropdown(id='second_num_col',
                               options=[{'label': i, 'value': i} for i in num_cols],
                               value="valence",
                               style={'color': 'black'})]),
        html.Div([dcc.Dropdown(id='year',
                               options=[{'label': i, 'value': i} for i in range(1960, 2011, 10)],
                               value=2000,
                               style={'color': 'black'})]),

        dcc.Graph(id='num_scatter_plot',
                  style={'height': 350}),
        html.Hr(),
    ])
])


@app.callback(
    Output(component_id='top_artists', component_property='figure'),
    [
    Input(component_id='first_col', component_property='value'),
    Input(component_id='num_top_artists', component_property='value')
     ]
    )

def plot_bar(col_1, top):
  df_col = df.sort_values(by=[col_1], ascending=False)

  labels = df_col['artist'][:top]
  values = df_col[col_1][:top]

  trace = go.Bar(x=values, y=labels, orientation="h", marker={'color': 'LimeGreen'})

  data = [trace]
  layout = dict(title=f"Artists with most {col_1} songs")

  return go.Figure(data, layout)


@app.callback(
    Output(component_id='boxplot', component_property='figure'),
    [
    Input(component_id='col', component_property='value'),
    Input(component_id='second_col', component_property='value'),
    Input(component_id='year_col', component_property='value'),
     ]
    )


def plot_boxplot_with_year_dropdown(x, y, year):

  df_year = df[df['year'] == year]

  return px.box(df_year, x=x, y=y)



@app.callback(
    Output(component_id='num_scatter_plot', component_property='figure'),
    [
    Input(component_id='first_num_col', component_property='value'),
    Input(component_id='second_num_col', component_property='value'),
    Input(component_id='year', component_property='value'),
     ]
    )


def scatterplot(x, y, year):
    df_year = df[df['year'] == year]
    trace = go.Scatter(x=df_year[x], y=df_year[y], mode='markers',
                       marker=dict(size=5, color="rgba(152,0,0,0.5)")
                       )

    layout = dict(title="Relationship between two numerical features",
                  xaxis=dict(title=x, showgrid=False, showline=False, zeroline=False),
                  yaxis=dict(title=y, showgrid=False, showline=False, zeroline=False)
                  )

    return go.Figure(trace, layout)


if __name__ == "__main__":
    app.run_server(debug=True, port=8058)