from dash import Dash, dcc, html, Output, Input, State, dash_table
import dash_bootstrap_components as dbc

import pandas as pd

import plotly.express as px
from dash_bootstrap_templates import load_figure_template

# stylesheet with the .dbc class from dash-bootstrap-templates library
# dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.css"

app = Dash(__name__, external_stylesheets=[dbc.themes.SKETCHY],
            meta_tags=[ {'name': 'viewport',
                        'content': 'width=device-width, initial-scale=1.0'},
                        {'http-equiv': 'content-language',
                        'content': 'pt-br'},
                      ]
        )
server = app.server

app.title = 'Notas CETEC Augusto Marques dos Passos'

# df = pd.read_csv('https://raw.githubusercontent.com/mauriciopassos/notas_cetec_augusto/main/src/df_notas_cetec_augusto.csv')
# df_apo = pd.read_csv('https://raw.githubusercontent.com/mauriciopassos/notas_cetec_augusto/main/src/df_pareceres_cetec_augusto.csv')
df = pd.read_csv('https://github.com/mauriciopassos/notas_cetec_augusto/raw/refs/heads/main/src/df_notas_cetec_augusto.csv')
df_apo = pd.read_csv('https://github.com/mauriciopassos/notas_cetec_augusto/raw/refs/heads/main/src/df_pareceres_cetec_augusto.csv')

# df = pd.read_csv('src/df_notas_cetec_augusto.csv')
# df_apo = pd.read_csv('src/df_pareceres_cetec_augusto.csv')

lista_anos = df['Ano'].unique().tolist()
lista_disciplinas = sorted(df['Disciplina'].unique().tolist())
lista_periodos = df['Período'].unique().tolist()

lista_periodos_apo = df_apo['Período'].unique().tolist()
ddc_periodo_apo = dcc.Dropdown(id='id_dd_periodo_apo', clearable=False, className="dbc")
ddc_disciplina_apo = dcc.Dropdown(id='id_dd_disciplina_apo', clearable=False, className="dbc")

dtotals = pd.DataFrame(columns = ['Ano', 'Disciplina', 'Período', 'Nota'])
dfa = pd.DataFrame(columns = ['Ano','Disciplina','Período','Avaliação','Data da Avaliação','Descrição da Avaliação','Pontuação','Nota','%','Turma','Época'])
dfa['Nota'] = dfa['Nota'].astype(float)

load_figure_template("sketchy")
#*******************************************************************************************************
#*******************************************************************************************************
def addRowinDFA(ano, disciplina, periodo, avaliacao, data, descricao, pontuacao, nota, percentual, turma, epoca):

    dfarow = {
              "Ano" : ano,
              "Disciplina" : disciplina,
              "Período" : periodo,
              "Avaliação" : avaliacao,
              "Data da Avaliação" : data,
              "Descrição da Avaliação" : descricao,
              "Pontuação" : pontuacao,
              "Nota" : nota,
              "%": percentual,
              "Turma": turma,
              "Época": epoca
            }

    dfa.loc[len(dfa)] = dfarow
  
#*******************************************************************************************************
#*******************************************************************************************************
def addRowinTotals(ano, disciplina, periodo, nota):

    dtotalsrow = {
                    "Ano" : ano,
                    "Disciplina" : disciplina,
                    "Período" : periodo,
                    "Nota" : nota
    }

    dtotals.loc[len(dtotals)] = dtotalsrow
#*******************************************************************************************************
#*******************************************************************************************************
def get_Epoca_Turma(ano):
    query = "Ano == \'" + ano + "\'"
    dff = df.query(query)
    epoca = dff['Época'].values[0]
    turma = dff['Turma'].values[0]

    # {'label': '6º Ano B - 2023', 'value': '6º'},
    l = ano + " Ano " + str(turma) + " - " + str(epoca)
    return {'label': l, 'value': ano}

#*******************************************************************************************************
#*******************************************************************************************************
lista_anos_epoca_turma = []
for a in lista_anos:
    lista_anos_epoca_turma.append(get_Epoca_Turma(a))

#*******************************************************************************************************
#*******************************************************************************************************
for a in lista_anos:
    for d in lista_disciplinas:
        media_final = 0
        for p in lista_periodos:
            query = "Ano == \'" + a + "\' & Disciplina == \'"+ d + "\' & Período == \'" + p + "\'"
            dff = df.query(query).sort_values(by=['Avaliação'], ascending=False)

            dff = dff[dff['Avaliação'] != 'Média da Turma']

            rec = dff[dff['Avaliação'] == 'Prova Recuperação Pós Trimestre']['Nota']
            rec_flag = not rec.isnull().values.any()
            if rec_flag:
                p1 = dff[dff['Avaliação'] == 'Prova 1']['Nota']
                p2 = dff[dff['Avaliação'] == 'Prova 2']['Nota']
                
                if not p1.isnull().values.any():
                    p1_value = p1.values[0]
                else:
                    p1_value = 0

                if not p2.isnull().values.any():
                    p2_value = p2.values[0]
                else:
                    p2_value = 0

                if rec.values[0] > (p1_value + p2_value):
                    dff = dff[dff['Avaliação'] != 'Prova 1']
                    dff = dff[dff['Avaliação'] != 'Prova 2']
                else:
                    dff = dff[dff['Avaliação'] != 'Prova Recuperação Pós Trimestre']

            if p == '3º Trimestre':
                media_final += dff['Nota'].sum() * 0.4
            else:
                media_final += dff['Nota'].sum() * 0.3

            addRowinTotals(a, d, p, float("{:.1f}".format(dff['Nota'].sum())))

            # dfs = [dfa, dff]
            # dfa = pd.concat(dfs)

            for row in dff.iterrows():
                addRowinDFA(a, d, p, row[1]["Avaliação"], row[1]["Data da Avaliação"], row[1]["Descrição da Avaliação"], row[1]["Pontuação"], float("{:.1f}".format(row[1]["Nota"])), "NaN", row[1]["Turma"], row[1]["Época"])


        # addRowinTotals(a, d, "Média Final", float("{:.1f}".format(soma / len(lista_periodos))))
        addRowinTotals(a, d, "Média Final", float("{:.1f}".format(media_final)))

#*******************************************************************************************************
#*******************************************************************************************************
dfpivot_totals = dtotals.pivot(index=["Ano","Disciplina"], columns="Período", values="Nota")

dfpivot_totals = dfpivot_totals.reset_index()
dfpivot_totals.columns.name = None

dfa = dfa.set_index('Ano')
#*******************************************************************************************************
#*******************************************************************************************************

app.layout = dbc.Container(
    children = [
        html.H1("Notas CETEC Augusto Marques dos Passos", style={"text-align": "center", "color": px.colors.qualitative.Prism[2]}),

        html.Div(
            className="row", children=[
                html.Div(className='four columns', children=[
                    dcc.Dropdown(options=lista_anos_epoca_turma, value="8º", id='id_dd_ano', clearable=False, className="dbc"),
                    # dcc.Dropdown(options=lista_anos, value="7º", id='id_dd_ano', clearable=False, className="dbc"),
                ],style=dict(width='100%')),
            ], style=dict(display='flex')
        ),


        dcc.Graph(id="graph_histogram"),

        html.Div(
            children=[
                dbc.Switch(
                    label ="Mostrar linha de média no gráfico",
                    value=False,
                    id="id_check_avarage_line",
                ),
            ],style={"text-align": "left", "font-size": "0.875em"}
        ),

        html.Div(
            children=[
                dbc.Switch(
                    label ="Mostrar parciais no gráfico",
                    value=False,cd 
                    id="id_check_graph",
                ),
            ],style={"text-align": "left", "font-size": "0.875em"}
        ),

        html.Div(
            children=[
                dbc.Switch(
                    label ="Mostrar tabela dos totais dos períodos",
                    value=False,
                    id="id_check_table",
                ),
            ],style={"text-align": "left", "font-size": "0.875em"}
        ),

        html.Div(id="id_tabela_totais"),

        html.Div(
            className="row", children=[
                html.Div(className='four columns', children=[
                    dcc.Dropdown(options=lista_periodos, value="3º Trimestre", id='id_dd_periodo', clearable=False, className="dbc"),
                    # dbc.Select(options=lista_periodos, value="1º Trimestre", id='id_dd_periodo'),
                ],style=dict(width='50%')),
                
                html.Div(className='four columns', children=[
                    dcc.Dropdown(options=lista_disciplinas, value="Matemática", id='id_dd_disciplina', clearable=False, className="dbc"),
                    # dbc.Select(options=lista_disciplinas, value="Matemática", id='id_dd_disciplina'),
                ],style=dict(width='50%')),
            ], style=dict(display='flex')
        ),

        html.Div(
            children=[
                dbc.Switch(
                    label ="Mostrar gráfico de evolução trimestral",
                    value=False,
                    id="id_check_graph_trimestre",
                ),
            ],style={"text-align": "left", "font-size": "0.875em", "padding-top": "15px"}
        ),

        html.Div(
            className="row", id="g_trimestre", children=[
                dcc.Graph(id="graph_trimestre", className="mt-3"),
            ],
        ),

        html.Div(
            children=[
                dbc.Switch(
                    label ="Mostrar tabela das notas parciais",
                    value=False,
                    id="id_check_table_pie",
                ),
            ],style={"text-align": "left", "font-size": "0.875em"}
        ),

        html.Div(id="id_tabela_pie"),

        dcc.Graph(id="graph_pie", className="mt-3"),

        dcc.Graph(id="graph_comparativo"),

        html.H1(id = "id_pareceres_title", className="mt-5", style={"font-size": "180%", "text-align": "center", "color": px.colors.qualitative.Prism[2]}),

        html.Div(
            className="row", children=[

                html.Div(className='four columns', 
                            id = "id_ddc_periodo_apo",
                            children = ddc_periodo_apo,
                            style=dict(width='50%')
                        ),

                html.Div(className='four columns', 
                            id = "id_ddc_disciplina_apo",
                            children = ddc_disciplina_apo,
                            style=dict(width='50%')
                        ),
            ],style=dict(display='flex')
        ),

        html.H4(id = "id_pareceres_subtitle", className="mt-5", style={"font-weight": "bold", "text-align": "center", "color": px.colors.qualitative.Prism[2]}),

        dcc.Markdown(className="mt-4", id="id_dcm_parecer_apo", style={"text-align": "left"},),


    ],style={"text-align": "center"}
)

#*******************************************************************************************************
#*******************************************************************************************************

@app.callback(
  [
    Output("id_ddc_periodo_apo", "children"),
    Output("id_ddc_disciplina_apo", "children"),
  ],

  [
    Input("id_dd_ano", "value"),
  ],
)

def dcc_entradas_apo(ano):
    
    ddc_periodo_apo = dcc.Dropdown(options=lista_periodos_apo, value=lista_periodos_apo[0], id='id_dd_periodo_apo', clearable=False, className="dbc")

    query = "Ano == \'%s\'" % str(ano)
    dff_apo = df_apo.query(query)

    lista_disciplinas_apo = sorted(dff_apo['Disciplina'].unique().tolist())

    ddc_disciplina_apo = dcc.Dropdown(options=lista_disciplinas_apo, value=lista_disciplinas_apo[0], id='id_dd_disciplina_apo', clearable=False, className="dbc"),

    return ddc_periodo_apo, ddc_disciplina_apo

#*******************************************************************************************************
#*******************************************************************************************************

@app.callback(
    [
      Output("id_pareceres_title", "children"),
      Output("id_pareceres_subtitle", "children"),
      Output("id_dcm_parecer_apo", "children"),
    ],

    [
      Input("id_dd_ano", "value"),
      Input("id_dd_periodo_apo", "value"),
      Input("id_dd_disciplina_apo", "value"),
    ],
)

def pareceres(ano, periodo_apo, disciplina_apo):

    pareceres_titulo = "Pareceres do %s Ano" % str(ano)
    pareceres_subtitulo = "Parecer do %s da %s" % (str(periodo_apo), str(disciplina_apo))

    query = "Ano == \'%s\' & Período == \'%s\' & Disciplina == \'%s\'" % (str(ano), str(periodo_apo), str(disciplina_apo))
    dff_apo = df_apo.query(query)

    parecer = dff_apo['Parecer']

    if parecer.isnull().values.any():
      parecer_apo = '''Parecer da disciplina não cadastrado no período.'''
    else:
      parecer_apo = parecer

    return pareceres_titulo, pareceres_subtitulo, parecer_apo


#*******************************************************************************************************
#*******************************************************************************************************

@app.callback(
    [
        Output("id_tabela_totais", "style"),
        Output("id_tabela_pie", "style"),
    ],
    
    [
        Input("id_check_table", "value"),
        Input("id_check_table_pie", "value"),
    ]
)

def showTables(check, checkpie):

    tr = {"text-align": "center", "font-size": "0.875em", "display": "block",}
    fl = {"text-align": "center", "font-size": "0.875em", "display": "none",}

    if check & checkpie:
        return tr, tr
    else:
        if check & (not checkpie):
            return tr, fl
        else:
            if (not check) & checkpie:
                return fl, tr
            else:
                return fl, fl

#*******************************************************************************************************
#*******************************************************************************************************

@app.callback(
    [
        Output("graph_histogram", "figure"),
        Output("graph_comparativo", "figure"),
        Output("graph_pie", "figure"),
        Output("id_tabela_pie", "children"),
        Output("graph_trimestre", "figure"),
        Output("g_trimestre", "style"),
        Output("id_tabela_totais", "children"),
    ],

    [
        Input("id_dd_ano", "value"),
        Input("id_dd_periodo", "value"),
        Input("id_dd_disciplina", "value"),
        Input("id_check_graph", "value"),
        Input("id_check_graph_trimestre", "value"),
        Input("id_check_avarage_line", "value"),
    ],
    # prevent_initial_call=True,
    # suppress_callback_exceptions=True,
)

def update_graphs(ano, periodo, disciplina, parciais, graph_trimestre, linha_media):

    query = "Ano == \'" + ano + "\'"
    dff = dfa.query(query).sort_values(by=['Disciplina', 'Período'])
    # dff = df.query(query).sort_values(by=['Disciplina', 'Período'])
    # dff = dff[dff['Avaliação'] != 'Média da Turma']

    if parciais:
        dff = pd.DataFrame(dff.groupby(by=['Disciplina', 'Período', 'Avaliação'])['Nota'].sum())
    else:
        dff = pd.DataFrame(dff.groupby(by=['Disciplina', 'Período'])['Nota'].sum())

    dff.reset_index(inplace=True)

    titulo_histogram = "<b>Aproveitamento Trimestral - " + ano + " Ano</b>"

    if parciais:    
        fig_histogram = px.bar(dff, x="Período", y="Nota", color="Disciplina", barmode='group', hover_name='Disciplina', hover_data=['Avaliação'],
            text='Nota', height=500, color_discrete_sequence=px.colors.qualitative.Pastel).update_layout(
            title={"text": titulo_histogram, "x": 0.5}, title_font_color = px.colors.qualitative.Prism[2],
            yaxis_title = "Média no Período",
            paper_bgcolor = 'rgba(0,0,0, 0)',
            # font = {"color": '#839496'},
            # font = {"color": '#EBEBEB'},
            # plot_bgcolor = 'rgba(0,0,0, 0)',
        )
        fig_histogram.update_yaxes(gridcolor="#CCC")
    else:
        fig_histogram = px.bar(dff, x="Período", y="Nota", color="Disciplina", barmode='group', hover_name='Disciplina',
            text="Nota", height=500, color_discrete_sequence=px.colors.qualitative.Pastel).update_layout(
            title={"text": titulo_histogram, "x": 0.5}, title_font_color = px.colors.qualitative.Prism[2],
            yaxis_title = "Média no Período",
            paper_bgcolor = 'rgba(0,0,0,0)',
            # font = {"color": '#839496'},
            # font = {"color": '#EBEBEB'},
            # plot_bgcolor = 'rgba(0,0,0, 0)',
        )
        fig_histogram.update_yaxes(gridcolor="#CCC")

    if linha_media:
        fig_histogram.add_hline(y=7, line_color="#e06666")


    if ano == "6º":
      titulo_comparativo = "<b>Comparativo com a Média da Turma no " + periodo + "</b>"
    else:
      titulo_comparativo = "<b>Comparativo com a Média dos outros Anos no " + periodo + "</b>"

    query = "Ano == \'" + ano + "\' & Período == \'" + periodo + "\'"
    dff = df.query(query).sort_values(by=['Disciplina', 'Período'])

    dfm = dff[dff['Avaliação'] == 'Média da Turma']
    dfm = dfm.dropna(subset = ['Nota'])

    dt = dtotals.query(query).sort_values(by=['Disciplina', 'Período'])

    fig_comparativo = px.line().update_layout(
            title={"text": titulo_comparativo, "x": 0.5}, title_font_color = px.colors.qualitative.Prism[2],
            yaxis_title="Média do " + periodo, xaxis_title="Disciplina",
            paper_bgcolor = 'rgba(0,0,0,0)'
            )

    i = 0
    for a in lista_anos:
      if ano == "6º":
        fig_comparativo.add_scatter(x=dt['Disciplina'], y=dt['Nota'], text=dt['Nota'], name="Média do Augusto", marker_color=px.colors.qualitative.Prism[2], textfont_color=px.colors.qualitative.Prism[1])
        fig_comparativo.add_scatter(x=dfm['Disciplina'], y=dfm['Nota'], text=dfm['Nota'], name="Média da Turma", marker_color=px.colors.qualitative.Light24[23], textfont_color=px.colors.qualitative.Light24[22])
        break

      if a != ano:
        query = "Ano == \'" + a + "\' & Período == \'" + periodo + "\'"
        dtb = dtotals.query(query).sort_values(by=['Disciplina', 'Período'])

        # fig_comparativo.add_scatter(x=dt['Disciplina'], y=dt['Nota'], text=dt['Nota'], name="Média do " + ano + " Ano", marker_color=px.colors.qualitative.Prism[2], textfont_color=px.colors.qualitative.Prism[1])
        fig_comparativo.add_scatter(x=dtb['Disciplina'], y=dtb['Nota'], text=dtb['Nota'], name="Média do " + a + " Ano", marker_color=px.colors.qualitative.Light24[23-i], textfont_color=px.colors.qualitative.Light24[23-i])
        i = i + 1

      if a == ano:
        fig_comparativo.add_scatter(x=dt['Disciplina'], y=dt['Nota'], text=dt['Nota'], name="Média do " + ano + " Ano", marker_color=px.colors.qualitative.Prism[2], textfont_color=px.colors.qualitative.Prism[1], line={'width': 4})
    
    fig_comparativo.update_traces(textposition='top center', mode="markers+lines+text", showlegend=True, line_shape='spline')
    fig_comparativo.update_layout(hovermode="x unified")

    query = "Ano == \'" + ano + "\' & Disciplina == \'"+ disciplina + "\' & Período == \'" + periodo + "\'"
    dff = dfa.query(query).sort_values(by=['Avaliação'])

    soma = float("{:.1f}".format(dff['Nota'].sum()))

    titulo_pie = "<b>" + disciplina + " - " + ano + " Ano - Média do " + periodo + ": " + str(soma) + "</b>"
    fig_pie = px.pie(dff, values="Nota", names="Avaliação", hole=.2, color_discrete_sequence=px.colors.qualitative.Pastel2).update_layout(
        title={"text": titulo_pie, "x": 0.5}, title_font_color = px.colors.qualitative.Prism[2],
        paper_bgcolor = 'rgba(0,0,0,0)',
        # font = {"color": '#839496'},
        # font = {"color": '#EBEBEB'},
        # plot_bgcolor = 'rgba(0,0,0,0)',
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")

    dff = df.query(query).sort_values(by=['Avaliação'])
    dff = dff[dff['Avaliação'] != 'Média da Turma']
    dff = dff.dropna(subset = ['Nota'])

    dff['%'] = dff['Nota'] / dff['Pontuação']
    dff['%'] = dff['%'].apply(lambda x: "{:.2f}%".format(x * 100))

    table = dbc.Table.from_dataframe(dff, responsive=True, striped=True, bordered=False, hover=True, dark=False, style={'vertical-align' : 'middle'})

    titulo_trimestre = "<b>Evolução Trimestral da Disciplina de " + disciplina + "</b>"

    fig_trimestre = px.line().update_layout(
            title={"text": titulo_trimestre, "x": 0.5}, title_font_color = px.colors.qualitative.Prism[2],
            yaxis_title="Média do Período", xaxis_title="Período",
            paper_bgcolor = 'rgba(0,0,0,0)'
            )    

    i = 0
    for a in lista_anos:
      query = "Ano == \'" + a + "\' & Disciplina == \'" + disciplina + "\'"
      dff = df.query(query).sort_values(by=['Período'])

      dfm = dff[dff['Avaliação'] == 'Média da Turma']
      dfm = dfm.dropna(subset = ['Nota'])

      dt = dtotals.query(query).sort_values(by=['Período'])

      if a == ano:
        fig_trimestre.add_scatter(x=dt['Período'], y=dt['Nota'], text=dt['Nota'], name=a, marker_color=px.colors.qualitative.Prism[2], textfont_color=px.colors.qualitative.Prism[1], line={'width': 4})
        # fig_trimestre.update_traces(line={'width': 4})
      else:
        fig_trimestre.add_scatter(x=dt['Período'], y=dt['Nota'], text=dt['Nota'], name=a, marker_color=px.colors.qualitative.Light24[23-i], textfont_color=px.colors.qualitative.Light24[23-i])
        i = i + 1


    fig_trimestre.update_traces(textposition='top center', mode="markers+lines+text", showlegend=True, line_shape='spline')
    fig_trimestre.update_layout(hovermode="x unified")

    g_trimestre_style = {"display": "none",}

    if graph_trimestre:
        g_trimestre_style = {"display": "block",}
    else: 
        g_trimestre_style = {"display": "none",}

    query = "Ano == \'" + ano + "\'"
    dfp_totals = dfpivot_totals.query(query)
    tabela_totais = dbc.Table.from_dataframe(dfp_totals, responsive=True, striped=True, bordered=False, hover=True, dark=False)

    return fig_histogram, fig_comparativo, fig_pie, table, fig_trimestre, g_trimestre_style, tabela_totais

if __name__ == '__main__':
    app.run_server(debug=False)