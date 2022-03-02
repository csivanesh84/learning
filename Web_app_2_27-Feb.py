import dash
import dash_core_components as dcc
import pandas as pd
import os
import numpy as np
import dash
import plotly.express as px
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Sign, Format, Scheme
from dash_extensions import Download
from dash_extensions.snippets import send_data_frame
from datetime import datetime
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash_extensions.enrich import DashProxy, MultiplexerTransform, Input, Output, NoOutputTransform, BlockingCallbackTransform
#rom dash_bootstrap_templates import load_figure_template
#import snowflake.connector


dfITT = pd.read_csv(r"C:\Users\85102758\Desktop\ITT_PP.csv")
dfITT['year']=pd.to_datetime(dfITT['NEW_DATE']).dt.year
dfITT2=dfITT.groupby(['CG','Vendor','year','CoO_Vendor'],as_index=False).sum('ADD_SUPPLY_BY_VENDOR')
dfITT2= dfITT2[['CG','Vendor','year','ADD_SUPPLY_BY_VENDOR','CoO_Vendor']]
dfITT2= dfITT2.pivot(index={'CG','year'}, columns='CoO_Vendor', values='ADD_SUPPLY_BY_VENDOR')
dfITT2=dfITT2.reset_index()
dfITT3= dfITT[['CG','Vendor','year','ADD_SUPPLY_BY_VENDOR','CoO_Vendor']]
dfITT3=dfITT3.groupby(['CG','Vendor','year','CoO_Vendor'],as_index=False).sum('ADD_SUPPLY_BY_VENDOR')
dfITT3['type']="Baseline"
dfITT3['ADD_SUPPLY_BY_VENDOR']=round(dfITT3['ADD_SUPPLY_BY_VENDOR'])
dfITT3a=dfITT3.copy()
dfITT3a['type']="Edit"
dfITT3 = pd.concat([dfITT3, dfITT3a], ignore_index=True)
dfITT3 = dfITT3[['CG', 'Vendor', 'year', 'CoO_Vendor','type', 'ADD_SUPPLY_BY_VENDOR' ]]
dfITT3['total']=  dfITT3.iloc[:,5:].sum(axis=1)
col_type = ['text', 'numeric', 'numeric', 'text', 'text', 'numeric', 'numeric']
#col_type = ['text', 'text', 'text', 'text', 'text', 'text', 'numeric']

dfITT3 = dfITT3.sort_values(by=['CG', 'Vendor', 'year', 'CoO_Vendor'], ascending=True)
dfITT3 = dfITT3.astype(str)
dfITT3_ab = dfITT3.copy()
dfITT3_ab = dfITT3_ab.astype(str)

def merge_two_dicts(x, y):
    z = x.copy()   # start with keys and values of x
    z.update(y)    # modifies z with keys and values of y
    return z

def generate_table(dataframe, max_rows=100, df_new = dfITT3_ab):
    cols = list(dataframe.columns)
    cols = list(set(cols) - set(['CG', 'Vendor', 'year', 'CoO_Vendor', 'type', 'total']) | set(list(df_new['CoO_Vendor'].unique())))
    return html.Div(id='div1', children=[dash_table.DataTable(
                            id='table-editing-simple',
                            columns=([{'id': p, 'name': p, 'type': q} if p not in ['CG', 'Vendor', 'year', 'CoO_Vendor', 'type'] else {'id': p, 'name': p, 'presentation': 'dropdown'}  for p,q in zip(dataframe.columns, col_type)]), #if p not in ['Vendor', 'year', 'ADD_SUPPLY_BY_VENDOR'] els
                            data=dataframe.to_dict('records'),
                            sort_action="native",
                            editable=True,
                            row_deletable=True,
                            page_action='native',
                            page_current= 0,
                            css=[{"selector": ".Select-menu-outer", "rule": "display: block !important"}],
                            page_size= 10,
                            style_data_conditional=[
                                {
                                    'if': {
                                        'filter_query': '{type} eq "Baseline"',
                                        #'column_id': 'type', 
                                    },
                                    'color': 'black',
                                    'pointer-events': 'none'
                                },
                                {
                                    'if': {
                                        'filter_query': '{type} eq "Edit"',
                                    },
                                    'color': 'black',
                                    'pointer-events': 'none'
                                },
                                {
                                    'if': {
                                        'filter_query': '{type} eq "Edit"',
                                        'column_id': cols,
                                    },
                                    'color': 'black',
                                    'pointer-events': 'auto',
                                    'backgroundColor': 'yellow',
                                },
                        
                                {
                                    'if': {
                                        'filter_query': '{type} ne "Edit" and {type} ne "Baseline"',
                                        #'column_id': cols,
                                    },
                                    'color': 'black',
                                    'pointer-events': 'auto',
                                    'backgroundColor': 'yellow',
                                },
                    
                            ],
                            dropdown_conditional=[
                                {
                                    'if': {
                                        'filter_query': '{type} ne "Edit" or {type} ne "Baseline"',
                                        'column_id': 'type',
                                        },
                                    'options': [
                                                {'label': i, 'value': i}
                                                for i in ['New']
                                            ]
                                },
                                {
                                    'if': {
                                        'filter_query': '{type} eq "Edit"',
                                        'column_id': 'type',
                                        },
                                    'options': [
                                                {'label': i, 'value': i}
                                                for i in ['Edit']
                                            ]
                                },
                                {
                                    'if': {
                                        'filter_query': '{type} eq "Baseline"',
                                        'column_id': 'type',
                                        },
                                    'options': [
                                                {'label': i, 'value': i}
                                                for i in ['Baseline']
                                            ]
                                },

                            ],
                            dropdown = {    
                                        'CG': {
                                            'options': [
                                                {'label': i, 'value': i, }
                                                for i in df_new['CG'].unique()
                                            ]
                                        },
                                        'Vendor': {
                                            'options': [
                                                {'label': i, 'value': i}
                                                for i in df_new['Vendor'].unique()
                                            ]
                                        },
                                        'year': {
                                            'options': [
                                                {'label': i, 'value': i}
                                                for i in df_new['year'].unique()
                                            ]
                                        },
                                        'CoO_Vendor': {
                                            'options': [
                                                {'label': i, 'value': i}
                                                for i in df_new['CoO_Vendor'].unique()
                                            ]
                                        },
                                        

                                    }
                        ),
                        html.Button('Add CG', id='editing-rows-button', n_clicks=0, style={"margin-left": "1%", }),
                        html.Button('Save table', id='Save-rows-button', n_clicks=0, style={"margin-left": "2.5%",}),
                    ], style= {"width": "100%", 'align-items': 'center', 'justify-content': 'center'})

app = DashProxy(
    prevent_initial_callbacks=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    transforms=[MultiplexerTransform(), NoOutputTransform(), BlockingCallbackTransform()]
)


# =============================================================================
# print(dfITT3['ADD_SUPPLY_BY_VENDOR'][1000])
# numbers = ("{:,}".format(dfITT3['ADD_SUPPLY_BY_VENDOR'][1000]))
# 
# print("{:,}".format(dfITT3['ADD_SUPPLY_BY_VENDOR'][1000]))
# print(numbers)
# =============================================================================

dfDOM = pd.read_csv(r"C:\Users\85102758\Desktop\DOM_PP.csv")


#app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container(fluid=True,style={'margin':'0 auto','background': '#e3e4e6'},children=[
     dbc.Row([
        dbc.Col(
             html.Img(src="https://www.bat.com/group/control.nsf/vwFiles/logo/$file/logo_UK__9D9KCY_x2.png",
                     alt="fail",style={'width': '100%'}),
             style={'margin-top':'20px','margin-left':'20px'},
             width='1'
             ),
        dbc.Col(
             html.H2(children='GLP Digital Crop Purchase Planning WebApp',
                    style={'margin-top':'20px','width': '70%','color':'#000000','font-family':'Segoe UI','font-weight': 'bold',})),
                ],),
     
     dcc.Tabs(id='dcpp_tabs',style = {
               # 'borderBottom': '1px solid #d6d6d6',
                'padding': '6px',
               #'fontWeight': 'bold'
                   },
             
        children=[
            dcc.Tab(label='ITT PP Sim',style={'background': '#e3e4e6'}, children= #html.Div(style={'backgroundColor': colors['background']}, )
                html.Div([
                    html.Div([
                        #Saumaan Edit
                            
                        html.Div(
                            children=[
                                dbc.Row([
                                    #dbc.Col([html.H6(children = "CG")], width={"size": 1, "offset": 1}),
                                        dbc.Col([ 
                                            dcc.Dropdown(
                                                id='dropdown_1',
                                                ## extend the options to consider unique Fund values as well
                                                options=[{'label': i, 'value': i} for i in dfITT3['CG'].unique()],
                                                multi=True, searchable=True, placeholder='Select CG', clearable=True,),
                                                ],style={"width": "8%", 'display': 'inline-block'}),
                                    #dbc.Col([html.H6(children = "CoO_Vendor")], width={"size": 1, "offset": 1}),
                                            dbc.Col([dcc.Dropdown(
                                                id='dropdown_2',
                                                ## extend the options to consider unique Fund values as well
                                                options= [{'label': i, 'value': i} for i in dfITT3['Vendor'].unique()],
                                                multi=True, searchable=True, placeholder='Select Vendor', clearable=True,),
                                                ],style={"width": "8%", 'display': 'inline-block'}),
                                            dbc.Col([dcc.Dropdown(
                                                id='dropdown_4',
                                                ## extend the options to consider unique Fund values as well
                                                options= [{'label': i, 'value': i} for i in dfITT3['CoO_Vendor'].unique()],
                                                multi=True, searchable=True, placeholder='Select CoO_Vendor', clearable=True,),
                                                ],style={"width": "8%",'display': 'inline-block'}),
                                            dbc.Col([dcc.Dropdown(
                                                id='dropdown_3',
                                                ## extend the options to consider unique Fund values as well
                                                options= [{'label': i, 'value': i} for i in dfITT3['year'].unique()],
                                                multi=True, searchable=True, placeholder='Select year', clearable=True,),
                                                ],style={"width": "8%", 'display': 'inline-block'}),
                                
                                    ]),
                                html.Div(id = 'hide-input-button', children=[
                                                            dbc.Col([dcc.Dropdown(
                                                                                    id='dropdown_5',
                                                                                    ## extend the options to consider unique Fund values as well
                                                                                    options= [{'label': i, 'value': i} for i in dfITT3['CoO_Vendor'].unique()],
                                                                                    multi=True, searchable=True, placeholder='Select CoO_Vendor', clearable=True,),
                                                                                    ],style={"width": "20%", }),
                                                            html.Button('Add Supplier', id='adding-rows-button', n_clicks=0, style={'display': 'inline-block'})
                                                            ], style={'display': 'none'}),
                                html.Div(id='table-container')
                                ], style={"width": "99%", 'display': 'inline-block'}
                            ),
                                
                        # saumaan edit ends   
                    ])
                ])
            ),
            dcc.Tab(label='DOM PP Sim',style={'background': '#e3e4e6'}, children= [
                
                dbc.Row([
                    dbc.Col([
                    html.Br(),
                    dbc.Row([
                      dbc.Col([html.H6(children = "Leaf Operation")], width={"size": 1, "offset": 1}),
                 dbc.Col([dcc.Dropdown(
                    id='PlantDOM',
                    options=[{'label': i, 'value': i} for i in dfDOM.Plant.unique()],
                    multi=False, searchable=True, placeholder='Please Select', clearable=True,
                    )],width=3),
                 dbc.Col([html.H6(children = "Year")], width={"size": 1, "offset": 1}),
                 dbc.Col([dcc.Dropdown(
                    id='YearDOM',
                    options=[{'label': i, 'value': i} for i in dfDOM.CP_Year.unique()],
                    multi=False, searchable=True, placeholder='Please Select', clearable=True,
                    )],width=3)
                    ]),
                    html.Br(),
                    
                  
                    html.Br(),
                    dcc.Slider(
                            id='DOM_Slider',
                            min=0,
                            max=1,
                            step=0.1,
                            marks={
                                0: {'label': '0%', 'style': {'color': '#77b0b1'}},
                                0.5: {'label': '50%'},
                                0.7: {'label': '70%'},
                                1: {'label': '100%',}
                            }
                    ),
                dbc.Col([
                    dash_table.DataTable(
                    id='tableDOM1',
                    style_cell={'overflow': 'hidden','textOverflow': 'ellipsis','maxWidth': 0,'border': 'none','font_size': '12px'},
                    style_cell_conditional=[{'if': {'column_id': 'Week'},'width': '25%','font_size': '16px','textAlign': 'center'},],
                    style_header={
                           #'backgroundColor': 'white',
                           'fontWeight': 'bold'
                       },
                    editable=False
               
                    ) ], width={"size": 10, "offset": 1}),
                    
                ] )
                      ])])
            ]
            
            )])


####Call back for ITT Sim
@app.callback(Output('table-container', 'children'),
    Input('dropdown_1', 'value'), 
    Input('dropdown_2', 'value'),
    Input('dropdown_3', 'value'), 
    Input('dropdown_4', 'value'),
    State('dropdown_5', 'value'),
    Output('dropdown_1', 'options'), 
    Output('dropdown_2', 'options'),
    Output('dropdown_3', 'options'),
    Output('dropdown_4', 'options'),
    Output('hide-input-button', 'style'),
    Output('dropdown_5', 'options'),
    prevent_initial_call=False)
##['CG', 'Vendor', 'year', 'CoO_Vendor','type', 'ADD_SUPPLY_BY_VENDOR', 'total' ]
def display_table(dropdown_value_1, dropdown_value_2, dropdown_value_3, dropdown_value_4, dropdown_value_5):
    dfITT3 = dfITT3_ab.copy()
    d_style = {'display': 'block', 'marginTop': 15}
    if ((dropdown_value_1 is not None) and (len(dropdown_value_1) > 0)) and ((dropdown_value_2 is not None) and (len(dropdown_value_2) > 0)) and ((dropdown_value_4 is not None) and (len(dropdown_value_4) > 0)) and (dropdown_value_3 is None or (len(dropdown_value_3) < 1)):
        dfITT3f = dfITT3[dfITT3.CG.str.contains('|'.join(dropdown_value_1)) & dfITT3.Vendor.str.contains('|'.join(dropdown_value_2)) & dfITT3.CoO_Vendor.str.contains('|'.join(dropdown_value_4))]
        dfITT3f_ = dfITT3[dfITT3.CG.str.contains('|'.join(dropdown_value_1))]
        dfITT3f__ = dfITT3[dfITT3.CG.str.contains('|'.join(dropdown_value_1)) & dfITT3.Vendor.str.contains('|'.join(dropdown_value_2))]
        dfITT3f = dfITT3f[['CG', 'Vendor', 'year', 'CoO_Vendor','type', 'ADD_SUPPLY_BY_VENDOR', 'total' ]]
        options_1 = [{'label': i, 'value': i} for i in dfITT3['CG'].unique()]
        options_2 = [{'label': i, 'value': i} for i in dfITT3f_['Vendor'].unique()]
        options_3 = [{'label': i, 'value': i} for i in dfITT3f['year'].unique()]
        options_4 = [{'label': i, 'value': i} for i in dfITT3f__['CoO_Vendor'].unique()]

        return generate_table(dfITT3f),  options_1, options_2,options_3, options_4, d_style, options_4
        
    elif (dropdown_value_1 is None or (len(dropdown_value_1) < 1)) and (dropdown_value_2 is None or (len(dropdown_value_2) < 1))  and ((dropdown_value_4 is not None) and (len(dropdown_value_4) > 0)) and (dropdown_value_3 is None or (len(dropdown_value_3) < 1)):
        dfITT3f = dfITT3[dfITT3.CoO_Vendor.str.contains('|'.join(dropdown_value_4))]
        dfITT3f = dfITT3f[['CG', 'Vendor', 'year', 'CoO_Vendor','type', 'ADD_SUPPLY_BY_VENDOR', 'total' ]]
        options_1 = [{'label': i, 'value': i} for i in dfITT3f['CG'].unique()]
        options_2 = [{'label': i, 'value': i} for i in dfITT3f['Vendor'].unique()]
        options_3 = [{'label': i, 'value': i} for i in dfITT3f['year'].unique()]
        options_4 = [{'label': i, 'value': i} for i in dfITT3['CoO_Vendor'].unique()]

        return generate_table(dfITT3f),  options_1, options_2,options_3, options_4, d_style, options_4


    elif (dropdown_value_1 is None or (len(dropdown_value_1) < 1)) and ((dropdown_value_2 is not None) and (len(dropdown_value_2) > 0)) and (dropdown_value_4 is None or (len(dropdown_value_4) < 1)) and (dropdown_value_3 is None or (len(dropdown_value_3) < 1)):
        dfITT3f = dfITT3[dfITT3.Vendor.str.contains('|'.join(dropdown_value_2))] #
        dfITT3f = dfITT3f[['CG', 'Vendor', 'year', 'CoO_Vendor','type', 'ADD_SUPPLY_BY_VENDOR', 'total' ]]
        options_1 = [{'label': i, 'value': i} for i in dfITT3f['CG'].unique()]
        options_2 = [{'label': i, 'value': i} for i in dfITT3['Vendor'].unique()]
        options_3 = [{'label': i, 'value': i} for i in dfITT3f['year'].unique()]
        options_4 = [{'label': i, 'value': i} for i in dfITT3f['CoO_Vendor'].unique()]

        return generate_table(dfITT3f),  options_1, options_2, options_3, options_4, d_style, options_4

    elif ((dropdown_value_1 is not None) and (len(dropdown_value_1) > 0)) and (dropdown_value_2 is None or (len(dropdown_value_2) < 1)) and (dropdown_value_4 is None or (len(dropdown_value_4) < 1)) and (dropdown_value_3 is None or (len(dropdown_value_3) < 1)):
        dfITT3f = dfITT3[dfITT3.CG.str.contains('|'.join(dropdown_value_1))]
        dfITT3f = dfITT3f[['CG', 'Vendor', 'year', 'CoO_Vendor','type', 'ADD_SUPPLY_BY_VENDOR', 'total' ]]
        options_1 = [{'label': i, 'value': i} for i in dfITT3['CG'].unique()]
        options_2 = [{'label': i, 'value': i} for i in dfITT3f['Vendor'].unique()]
        options_3 = [{'label': i, 'value': i} for i in dfITT3f['year'].unique()]
        options_4 = [{'label': i, 'value': i} for i in dfITT3f['CoO_Vendor'].unique()]

        return generate_table(dfITT3f),  options_1, options_2,options_3, options_4, d_style, options_4


    elif ((dropdown_value_1 is not None) and (len(dropdown_value_1) > 0)) and ((dropdown_value_2 is not None) and (len(dropdown_value_2) > 0)) and (dropdown_value_4 is None or (len(dropdown_value_4) < 1)) and (dropdown_value_3 is None or (len(dropdown_value_3) < 1)):
        dfITT3f = dfITT3[dfITT3.CG.str.contains('|'.join(dropdown_value_1)) & dfITT3.Vendor.str.contains('|'.join(dropdown_value_2))]
        dfITT3f_ = dfITT3[dfITT3.CG.str.contains('|'.join(dropdown_value_1))]
        dfITT3f = dfITT3f[['CG', 'Vendor', 'year', 'CoO_Vendor','type', 'ADD_SUPPLY_BY_VENDOR', 'total' ]]
        options_1 = [{'label': i, 'value': i} for i in dfITT3['CG'].unique()]
        options_2 = [{'label': i, 'value': i} for i in dfITT3f_['Vendor'].unique()]
        options_3 = [{'label': i, 'value': i} for i in dfITT3f['year'].unique()]
        options_4 = [{'label': i, 'value': i} for i in dfITT3f['CoO_Vendor'].unique()]

        return generate_table(dfITT3f),  options_1, options_2,options_3, options_4, d_style, options_4


    elif ((dropdown_value_1 is not None) and (len(dropdown_value_1) > 0)) and (dropdown_value_2 is None or (len(dropdown_value_2) < 1)) and ((dropdown_value_4 is not None) and (len(dropdown_value_4) > 0)) and (dropdown_value_3 is None or (len(dropdown_value_3) < 1)):
        dfITT3f = dfITT3[dfITT3.CG.str.contains('|'.join(dropdown_value_1)) & dfITT3.CoO_Vendor.str.contains('|'.join(dropdown_value_4))]
        dfITT3f_ = dfITT3[dfITT3.CG.str.contains('|'.join(dropdown_value_1))]
        dfITT3f = dfITT3f[['CG', 'Vendor', 'year', 'CoO_Vendor','type', 'ADD_SUPPLY_BY_VENDOR', 'total' ]]
        options_1 = [{'label': i, 'value': i} for i in dfITT3['CG'].unique()]
        options_2 = [{'label': i, 'value': i} for i in dfITT3f['Vendor'].unique()]
        options_3 = [{'label': i, 'value': i} for i in dfITT3f['year'].unique()]
        options_4 = [{'label': i, 'value': i} for i in dfITT3f_['CoO_Vendor'].unique()]

        return generate_table(dfITT3f),  options_1, options_2,options_3, options_4, d_style, options_4



    elif (dropdown_value_1 is None or (len(dropdown_value_1) < 1)) and ((dropdown_value_2 is not None) and (len(dropdown_value_2) > 0)) and ((dropdown_value_4 is not None) and (len(dropdown_value_4) > 0)) and (dropdown_value_3 is None or (len(dropdown_value_3) < 1)):
        dfITT3f = dfITT3[dfITT3.Vendor.str.contains('|'.join(dropdown_value_2)) & dfITT3.CoO_Vendor.str.contains('|'.join(dropdown_value_4))]
        dfITT3f_ = dfITT3[dfITT3.CG.str.contains('|'.join(dropdown_value_1))]
        dfITT3f = dfITT3f[['CG', 'Vendor', 'year', 'CoO_Vendor','type', 'ADD_SUPPLY_BY_VENDOR', 'total' ]]
        options_1 = [{'label': i, 'value': i} for i in dfITT3f['CG'].unique()]
        options_2 = [{'label': i, 'value': i} for i in dfITT3['Vendor'].unique()]
        options_3 = [{'label': i, 'value': i} for i in dfITT3f['year'].unique()]
        options_4 = [{'label': i, 'value': i} for i in dfITT3f_['CoO_Vendor'].unique()]

        return generate_table(dfITT3f),  options_1, options_2,options_3, options_4, d_style, options_4




    elif ((dropdown_value_1 is not None) and (len(dropdown_value_1) > 0)) and ((dropdown_value_2 is not None) and (len(dropdown_value_2) > 0)) and ((dropdown_value_4 is not None) and (len(dropdown_value_4) > 0)) and ((dropdown_value_3 is not None) and (len(dropdown_value_3) > 0)):
        #dfITT3f = dfITT3.loc[(dfITT3.CG == dropdown_value_1) & (dfITT3.Vendor == dropdown_value_2) & (dfITT3.CoO_Vendor == dropdown_value_4) & (dfITT3.CG == dropdown_value_1)]
        dfITT3f = dfITT3[dfITT3.CG.str.contains('|'.join(dropdown_value_1)) & dfITT3.Vendor.str.contains('|'.join(dropdown_value_2)) & dfITT3.CoO_Vendor.str.contains('|'.join(dropdown_value_4)) & dfITT3.year.str.contains('|'.join(dropdown_value_3))]
        dfITT3f_ = dfITT3[dfITT3.CG.str.contains('|'.join(dropdown_value_1))]
        dfITT3f__ = dfITT3[dfITT3.CG.str.contains('|'.join(dropdown_value_1)) & dfITT3.Vendor.str.contains('|'.join(dropdown_value_2))]
        dfITT3f___ = dfITT3[dfITT3.CG.str.contains('|'.join(dropdown_value_1)) & dfITT3.Vendor.str.contains('|'.join(dropdown_value_2)) & dfITT3.CoO_Vendor.str.contains('|'.join(dropdown_value_4))]
        dfITT3f = dfITT3f[['CG', 'Vendor', 'year', 'CoO_Vendor','type', 'ADD_SUPPLY_BY_VENDOR', 'total' ]]
        options_1 = [{'label': i, 'value': i} for i in dfITT3['CG'].unique()]
        options_2 = [{'label': i, 'value': i} for i in dfITT3f_['Vendor'].unique()]
        options_3 = [{'label': i, 'value': i} for i in dfITT3f___['year'].unique()]
        options_4 = [{'label': i, 'value': i} for i in dfITT3f__['CoO_Vendor'].unique()]

        return generate_table(dfITT3f),  options_1, options_2,options_3, options_4, d_style, options_4

    elif (dropdown_value_1 is None or (len(dropdown_value_1) < 1)) and (dropdown_value_2 is None or (len(dropdown_value_2) < 1))  and ((dropdown_value_4 is not None) and (len(dropdown_value_4) > 0)) and ((dropdown_value_3 is not None) and (len(dropdown_value_3) > 0)):
        dfITT3f = dfITT3[dfITT3.CoO_Vendor.str.contains('|'.join(dropdown_value_4)) & dfITT3.year.str.contains('|'.join(dropdown_value_3))]
        dfITT3f___ = dfITT3[dfITT3.CoO_Vendor.str.contains('|'.join(dropdown_value_4))]
        dfITT3f = dfITT3f[['CG', 'Vendor', 'year', 'CoO_Vendor','type', 'ADD_SUPPLY_BY_VENDOR', 'total' ]]
        options_1 = [{'label': i, 'value': i} for i in dfITT3f['CG'].unique()]
        options_2 = [{'label': i, 'value': i} for i in dfITT3f['Vendor'].unique()]
        options_3 = [{'label': i, 'value': i} for i in dfITT3f___['year'].unique()]
        options_4 = [{'label': i, 'value': i} for i in dfITT3['CoO_Vendor'].unique()]

        return generate_table(dfITT3f),  options_1, options_2,options_3, options_4, d_style, options_4


    elif (dropdown_value_1 is None or (len(dropdown_value_1) < 1)) and ((dropdown_value_2 is not None) and (len(dropdown_value_2) > 0)) and (dropdown_value_4 is None or (len(dropdown_value_4) < 1)) and ((dropdown_value_3 is not None) and (len(dropdown_value_3) > 0)):
        dfITT3f = dfITT3[dfITT3.Vendor.str.contains('|'.join(dropdown_value_2)) & dfITT3.year.str.contains('|'.join(dropdown_value_3))]
        dfITT3f___ = dfITT3[dfITT3.Vendor.str.contains('|'.join(dropdown_value_2))]
        dfITT3f = dfITT3f[['CG', 'Vendor', 'year', 'CoO_Vendor','type', 'ADD_SUPPLY_BY_VENDOR', 'total' ]]
        options_1 = [{'label': i, 'value': i} for i in dfITT3f['CG'].unique()]
        options_2 = [{'label': i, 'value': i} for i in dfITT3['Vendor'].unique()]
        options_3 = [{'label': i, 'value': i} for i in dfITT3f___['year'].unique()]
        options_4 = [{'label': i, 'value': i} for i in dfITT3f['CoO_Vendor'].unique()]

        return generate_table(dfITT3f),  options_1, options_2, options_3, options_4, d_style, options_4

    elif ((dropdown_value_1 is not None) and (len(dropdown_value_1) > 0)) and (dropdown_value_2 is None or (len(dropdown_value_2) < 1)) and (dropdown_value_4 is None or (len(dropdown_value_4) < 1)) and ((dropdown_value_3 is not None) and (len(dropdown_value_3) > 0)):
        dfITT3f = dfITT3[dfITT3.CG.str.contains('|'.join(dropdown_value_1)) & dfITT3.year.str.contains('|'.join(dropdown_value_3))]
        dfITT3f___ = dfITT3[dfITT3.CG.str.contains('|'.join(dropdown_value_1))]
        dfITT3f = dfITT3f[['CG', 'Vendor', 'year', 'CoO_Vendor','type', 'ADD_SUPPLY_BY_VENDOR', 'total' ]]
        options_1 = [{'label': i, 'value': i} for i in dfITT3['CG'].unique()]
        options_2 = [{'label': i, 'value': i} for i in dfITT3f['Vendor'].unique()]
        options_3 = [{'label': i, 'value': i} for i in dfITT3f___['year'].unique()]
        options_4 = [{'label': i, 'value': i} for i in dfITT3f['CoO_Vendor'].unique()]

        return generate_table(dfITT3f),  options_1, options_2,options_3, options_4, d_style, options_4


    elif ((dropdown_value_1 is not None) and (len(dropdown_value_1) > 0)) and ((dropdown_value_2 is not None) and (len(dropdown_value_2) > 0)) and (dropdown_value_4 is None or (len(dropdown_value_4) < 1)) and ((dropdown_value_3 is not None) and (len(dropdown_value_3) > 0)):
        dfITT3f = dfITT3[dfITT3.CG.str.contains('|'.join(dropdown_value_1)) & dfITT3.Vendor.str.contains('|'.join(dropdown_value_2)) & dfITT3.year.str.contains('|'.join(dropdown_value_3))]
        dfITT3f_ = dfITT3[dfITT3.CG.str.contains('|'.join(dropdown_value_1))]
        dfITT3f___ = dfITT3[dfITT3.CG.str.contains('|'.join(dropdown_value_1)) & dfITT3.Vendor.str.contains('|'.join(dropdown_value_2))]
        dfITT3f = dfITT3f[['CG', 'Vendor', 'year', 'CoO_Vendor','type', 'ADD_SUPPLY_BY_VENDOR', 'total' ]]
        options_1 = [{'label': i, 'value': i} for i in dfITT3['CG'].unique()]
        options_2 = [{'label': i, 'value': i} for i in dfITT3f_['Vendor'].unique()]
        options_3 = [{'label': i, 'value': i} for i in dfITT3f___['year'].unique()]
        options_4 = [{'label': i, 'value': i} for i in dfITT3f['CoO_Vendor'].unique()]

        return generate_table(dfITT3f),  options_1, options_2,options_3, options_4, d_style, options_4


    elif ((dropdown_value_1 is not None) and (len(dropdown_value_1) > 0)) and (dropdown_value_2 is None or (len(dropdown_value_2) < 1)) and ((dropdown_value_4 is not None) and (len(dropdown_value_4) > 0)) and ((dropdown_value_3 is not None) and (len(dropdown_value_3) > 0)):
        dfITT3f = dfITT3[dfITT3.CG.str.contains('|'.join(dropdown_value_1)) & dfITT3.CoO_Vendor.str.contains('|'.join(dropdown_value_4)) & dfITT3.year.str.contains('|'.join(dropdown_value_3))]
        dfITT3f_ = dfITT3[dfITT3.CG.str.contains('|'.join(dropdown_value_1))]
        dfITT3f___ = dfITT3[dfITT3.CG.str.contains('|'.join(dropdown_value_1)) & dfITT3.CoO_Vendor.str.contains('|'.join(dropdown_value_4))]
        dfITT3f = dfITT3f[['CG', 'Vendor', 'year', 'CoO_Vendor','type', 'ADD_SUPPLY_BY_VENDOR', 'total' ]]
        options_1 = [{'label': i, 'value': i} for i in dfITT3['CG'].unique()]
        options_2 = [{'label': i, 'value': i} for i in dfITT3f['Vendor'].unique()]
        options_3 = [{'label': i, 'value': i} for i in dfITT3f___['year'].unique()]
        options_4 = [{'label': i, 'value': i} for i in dfITT3f_['CoO_Vendor'].unique()]

        return generate_table(dfITT3f),  options_1, options_2,options_3, options_4, d_style, options_4



    elif (dropdown_value_1 is None or (len(dropdown_value_1) < 1)) and ((dropdown_value_2 is not None) and (len(dropdown_value_2) > 0)) and ((dropdown_value_4 is not None) and (len(dropdown_value_4) > 0)) and ((dropdown_value_3 is not None) and (len(dropdown_value_3) > 0)):
        dfITT3f = dfITT3[dfITT3.Vendor.str.contains('|'.join(dropdown_value_2)) & dfITT3.CoO_Vendor.str.contains('|'.join(dropdown_value_4)) & dfITT3.year.str.contains('|'.join(dropdown_value_3))]
        dfITT3f_ = dfITT3[dfITT3.CG.str.contains('|'.join(dropdown_value_1))]
        dfITT3f___ = dfITT3[dfITT3.Vendor.str.contains('|'.join(dropdown_value_2)) & dfITT3.CoO_Vendor.str.contains('|'.join(dropdown_value_4))]
        dfITT3f = dfITT3f[['CG', 'Vendor', 'year', 'CoO_Vendor','type', 'ADD_SUPPLY_BY_VENDOR', 'total' ]]
        options_1 = [{'label': i, 'value': i} for i in dfITT3f['CG'].unique()]
        options_2 = [{'label': i, 'value': i} for i in dfITT3['Vendor'].unique()]
        options_3 = [{'label': i, 'value': i} for i in dfITT3f___['year'].unique()]
        options_4 = [{'label': i, 'value': i} for i in dfITT3f_['CoO_Vendor'].unique()]

        return generate_table(dfITT3f),  options_1, options_2,options_3, options_4, d_style, options_4



    else:
        
        options_1 = [{'label': i, 'value': i} for i in dfITT3['CG'].unique()]
        options_2 = [{'label': i, 'value': i} for i in dfITT3['Vendor'].unique()]
        options_3 = [{'label': i, 'value': i} for i in dfITT3['year'].unique()]
        options_4 = [{'label': i, 'value': i} for i in dfITT3['CoO_Vendor'].unique()]
        return generate_table(dfITT3), options_1, options_2,options_3, options_4, d_style, options_4


@app.callback(
    Output('table-editing-simple', 'data'),
    Input('editing-rows-button', 'n_clicks'),
    State('table-editing-simple', 'data'),
    State('table-editing-simple', 'columns'),
    State('table-editing-simple', 'page_current'))
def add_row(n_clicks, rows, columns, page_current):
    if n_clicks > 0:
            rows.insert(((page_current)*10),{c['id']: None if c in ['CG', 'Vendor', 'year', 'CoO_Vendor','type'] else 0 for c in columns })
            #rows.append({c['id']: temp['id'] if c in ['CG', 'Vendor', 'year', 'CoO_Vendor','type'] else 0 for c in columns })
    return rows

@app.callback(
    Output('table-editing-simple', 'columns'),
    Input('adding-rows-button', 'n_clicks'),
    State('dropdown_5', 'value'),
    #State('adding-rows-name', 'value'),
    State('table-editing-simple', 'columns'),)
def update_columns(n_clicks, value, existing_columns):
    if n_clicks > 0:
        ll = []
        for j in existing_columns:
            print(j)
            ll.append(j['id'])
        for i in value:
            if i not in ll:
                existing_columns.insert(-1,{
                    'id': i, 'name': i, 'type': 'numeric',
                    'renamable': False, 'deletable': True
                }) 
    return existing_columns
    
@app.callback(
    Output('table-editing-simple', 'data'),
    Input('table-editing-simple', 'data_timestamp'),
    State('table-editing-simple', 'data'),
    )
def update_total(timestamp, rows):
    for row in rows:
        row['total'] = np.sum(float(value) for key, value in row.items() if key not in  ['CG', 'Vendor', 'year', 'CoO_Vendor','type', 'total'])
    return rows

@app.callback(
    Input('Save-rows-button', 'n_clicks'),
    Input('table-editing-simple', 'data'),
     Input('table-editing-simple', 'columns'))
def Save_df(n_clicks, rows, columns):
    if n_clicks > 0:
        df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
        df3 = pd.concat([df, dfITT3], axis=0, ignore_index=True)
        df3.to_csv('final.csv', index =False)
        



#### Call back for DOM Sim
@app.callback(
    [Output(component_id='tableDOM1', component_property='data'),
     Output(component_id='tableDOM1', component_property='columns')
     ],
    [Input(component_id='PlantDOM', component_property='value'),
     Input(component_id='YearDOM', component_property='value'),
     Input(component_id='tableDOM1', component_property='data'),
     Input(component_id='DOM_Slider', component_property='value')

     ],
   [#State(component_id='tableITT1', component_property='data'),
     State(component_id='tableDOM1', component_property='columns'),
     State(component_id='tableDOM1', component_property='active_cell'),
     State(component_id='tableDOM1', component_property='data_previous'),

     ], 
    prevent_initial_call=True)

def update_rows_DOM(plant_DOM,year_DOM,data_prop_DOM,DOM_Slider_value,columns_prop_DOM,active_cell_prop_DOM,data_prev_prop_DOM):

    if plant_DOM:
        
        #plant_DOM='AR01_CU'
        dfDOM_1=dfDOM
        dfDOM_1=dfDOM_1[(dfDOM_1['Plant']==plant_DOM) & (dfDOM_1['CP_FAD_Mth']==dfDOM_1['MonthNum'])]
        #dfDOM_1.info()
        dfDOM_1=dfDOM_1[['Plant','CG','CP_Year','NewCap']]
        dfDOM_1['CP_Year'] = dfDOM_1.CP_Year.astype(str)

        #type(dfDOM_1['CP_Year'])
        dfDOM_1=dfDOM_1.pivot(index={'Plant','CG'}, columns='CP_Year', values='NewCap')
        dfDOM_1=dfDOM_1.reset_index()

        mycolumnsDOM_1 = [{'name': i, 'id': i} for i in dfDOM_1.columns]
        
        for i in range(len(mycolumnsDOM_1[2:])):
        #print(i)
            mycolumnsDOM_1[2+i]['type']='numeric'
            mycolumnsDOM_1[2+i]['format']=percentage
        
        print(DOM_Slider_value)

        #return dfDOM_1.to_dict("rows"),mycolumnsDOM_1
        #type(dfDOM1)

    else:
        ''
# =============================================================================
#         if addCG_click:
#             dfITT_table1 = dfITT_table1.append({'PLANT': option_plant, 'FB_SFB': option_blend,'CG_SFB':row["CG_SFB"],
#                                 'Type_CG_SFB':'','SFBHOME_childitem':'',
#                                 'type_SFBHOME':'','CG_INCLUSION_KG':0,
#                                 'CG_NEW_INCLUSION_KG':row["CG_NEW_INCLUSION_KG"],
#                                 'VALID_FROM':'','CPT_VALID_FROM':row["CPT_VALID_FROM"],
#                                 'VALID_TO':'','CPT_VALID_TO':row["CPT_VALID_TO"],'CHANGE_TYPE':'INSERTED',
#                                 'New_ID':max(dfB['New_ID']) + 1}, ignore_index=True)
# =============================================================================

    
    #dfITT_table1=pd.DataFrame(data_prop)
    #dfITT_table1['CG TOTAL']=dfITT_table1.iloc[:,3:].sum(axis=1)
    #print((mycolumns))
    #testrow=[{'CG': '126LB4S', 'year': 2022, 'type': 'Baseline', 'GR_9506': 0.0, 'GR_9903': 0.0, 'CG TOTAL': 0.0}, {'CG': '126LB4S', 'year': 2022, 'type': 'Edit', 'GR_9506': 0.0, 'GR_9903': 0.0, 'CG TOTAL': 0.0}]
    #testcolumn=[{'name': 'CG', 'id': 'CG'}, {'name': 'year', 'id': 'year'}, {'name': 'type', 'id': 'type'}, {'name': 'GR_9506', 'id': 'GR_9506', 'editable': True}, {'name': 'GR_9903', 'id': 'GR_9903', 'editable': True}, {'name': 'CG TOTAL', 'id': 'CG TOTAL', 'editable': True}]
    #print(' mycolumnsDOM_1:',mycolumnsDOM_1)
    
    #print('testcolumn',testcolumn)
    return dfDOM_1.to_dict("rows"),mycolumnsDOM_1
    #return testrow,testcolumn

#### End of Call back for DOM Sim



if __name__ == '__main__':
     app.run_server(debug=True,port=3000,use_reloader=False)


