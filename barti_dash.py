import dash
#import numpy as np
import pandas as pd
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px

#read data into DF
reference_df = pd.read_csv("Reference_sheet_IV_BCG.csv")
df = pd.read_csv("Samples_threshold_data.csv")

# remove extra characters from sample_number
df['run'] = df['run'].map(lambda x: x.split("_")[0])


# wrangling data
#df = df.replace(np.nan,0)
#df[['percent']] = df[['percent']].apply(pd.to_numeric).round(0).astype('Int64', copy=False)

# add monkey and sample name from reference_df
df['monkey'] = df['run'].map(reference_df.set_index('sample_number')['monkey_id'])
df['sample'] = df['run'].map(reference_df.set_index('sample_number')['plot_name'])
df[['monkey']] = df[['monkey']].apply(pd.to_numeric).round(0).astype('Int64', copy=False)
df['ratio'] = df['percent']/100

df.head()

df_pass = df.loc[df['call_pass_fail'] == True]

monkey_list = ['All'] + list(pd.unique(df_pass['monkey']))
sample_list = df_pass['sample'].unique().tolist()

# make dash application
app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([html.H1(children="Heatmap Analysis"),
             #first dropdown
             html.Div([dcc.Dropdown(
                id='monkey-dropdown',
                options=[{'label': str(i), 'value': str(i)} for i in monkey_list],
                value='All',
                searchable=True,
                placeholder='Select a monkey',
             ),
            #heatmap figure
            html.Div(dcc.Graph(id='sucess-heatmap')),
             ])
              ]),
    html.Div([html.H1(children="Scatter Analysis"),
              html.Div([
                  dcc.Dropdown(
                      id='sample-dropdown',
                      options=[{'label': str(i), 'value': str(i)} for i in sample_list],
                      searchable=True,
                      placeholder='Select a sample',
                  ),
                  html.Div(dcc.Graph(id='sample-scatter')),
                  dcc.Dropdown(
                      id='scatter2-dropdown',
                      options=[{'label': str(i), 'value': str(i)} for i in df.columns],
                      searchable=True,
                      placeholder='Select a plot',
                  ),
                  html.Div(dcc.Graph(id='sample2-scatter')),
              ])
              ])

])


# call back to make heatmap
@app.callback(
    Output(component_id='sucess-heatmap', component_property='figure'),
    [Input(component_id='monkey-dropdown', component_property='value')]
)
def update_heatmap (monkey_dropdown):
    if (monkey_dropdown == 'All' or monkey_dropdown == 'None'):
        dfp = df_pass.pivot_table(index='monkey', columns='qbid', values='ratio')
        dfp.to_csv('out.csv')
        dfhm = pd.read_csv('out.csv')
        fig = px.imshow(
            dfhm,
            labels=dict(x="QBID", y="Monkey"),
            y=dfhm['monkey'])
        fig.update_yaxes(type='category')
    else:
        df_m = df_pass.loc[df_pass['monkey'] == int(monkey_dropdown)]
        dfp = df_m.pivot_table(index='sample', columns='qbid', values='ratio')
        dfp.to_csv('out.csv')
        dfhm = pd.read_csv('out.csv')
        fig = px.imshow(dfhm,
                        labels=dict(x="QBID", y="Sample", color = "Ratio"),
                        y=dfhm['sample'],
                        )
    return fig

@app.callback(
    Output(component_id='sample-scatter', component_property='figure'),
    [Input(component_id='monkey-dropdown', component_property='value'),
     Input(component_id="sample-dropdown", component_property="value")]
)
def update_scatter (monkey_dropdown, sample_dropdown):
    df_m = df.loc[df['monkey'] == int(monkey_dropdown)]
    df_m2 = df_m.loc[df_m['sample'] == sample_dropdown]
    fig = px.scatter(
        df_m2,
        x="index",
        y='counts',
        title='mcounts',
        hover_name='index',
        hover_data=[
            'monkey',
            'sample',
            'index',
            'qbid',
            'counts'
        ]
    )
    return fig

@app.callback(
    Output(component_id='sample2-scatter', component_property='figure'),
    [Input(component_id='monkey-dropdown', component_property='value'),
     Input(component_id="sample-dropdown", component_property="value"),
     Input(component_id="scatter2-dropdown", component_property="value")]
)
def update_scatter2 (monkey_dropdown, sample_dropdown, scatter):
    df_m = df.loc[df['monkey'] == int(monkey_dropdown)]
    df_m2 = df_m.loc[df_m['sample'] == sample_dropdown]
    print(df_m.head())
    fig = px.scatter(
        df_m2,
        x="index",
        y=scatter,
        title=scatter,
        hover_data=[
            'monkey',
            'sample',
            'index',
            'counts'
        ]
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)