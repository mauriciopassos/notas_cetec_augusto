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

df = pd.read_csv('https://raw.githubusercontent.com/mauriciopassos/notas_cetec_augusto/main/src/df_notas_cetec_augusto.csv')
# df = pd.read_csv('src/df_notas_cetec_augusto.csv')

lista_anos = df['Ano'].unique().tolist()
lista_disciplinas = sorted(df['Disciplina'].unique().tolist())
lista_periodos = df['Período'].unique().tolist()

dtotals = pd.DataFrame(columns = ['Ano', 'Disciplina', 'Período', 'Nota'])

load_figure_template("sketchy")
#*******************************************************************************************************
#*******************************************************************************************************
def addRowinTotals(ano, disciplina, periodo, nota):

    dtotalsrow = {
                    "Ano" : ano,
                    "Disciplina" : disciplina,
                    "Período" : periodo,
                    "Nota" : nota
    }

    #pd.concat(dtotals, dtotalsrow, ignore_index=True)
    dtotals.loc[len(dtotals)] = dtotalsrow

#*******************************************************************************************************
#*******************************************************************************************************

for a in lista_anos:
    for d in lista_disciplinas:
        media_final = 0
        for p in lista_periodos:
            query = "Ano == \'" + a + "\' & Disciplina == \'"+ d + "\' & Período == \'" + p + "\'"
            dff = df.query(query).sort_values(by=['Avaliação'], ascending=False)
            dff = dff[dff['Avaliação'] != 'Média da Turma']
            if p == '3º Trimestre':
                media_final += dff['Nota'].sum() * 0.4
            else:
                media_final += dff['Nota'].sum() * 0.3

            addRowinTotals(a, d, p, float("{:.1f}".format(dff['Nota'].sum())))

        # addRowinTotals(a, d, "Média Final", float("{:.1f}".format(soma / len(lista_periodos))))
        addRowinTotals(a, d, "Média Final", float("{:.1f}".format(media_final)))

dfpivot_totals = dtotals.pivot(index="Disciplina", columns="Período", values="Nota")

dfpivot_totals = dfpivot_totals.reset_index()
dfpivot_totals.columns.name = None


app.layout = dbc.Container(
    children = [
        html.H1("Notas CETEC Augusto Marques dos Passos", style={"text-align": "center", "color": px.colors.qualitative.Pastel[0]}),

        dcc.Graph(id="graph_histogram"),

        html.Div(
            children=[
                dbc.Switch(
                    label ="Mostrar parciais no gráfico",
                    value=False,
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

        html.Div(children=[
                    dbc.Table.from_dataframe(dfpivot_totals, responsive=True, striped=True, bordered=False, hover=True, dark=False)
                ],
                id="aprov_trimestral", 
            ),

        html.Div(
            className="row", children=[
                html.Div(className='four columns', children=[
                    dcc.Dropdown(options=lista_anos, value="6º", id='id_dd_ano', clearable=False, className="dbc"),
                    # dbc.Select(options=lista_anos, value="6º", id='id_dd_ano'),
                ],style=dict(width='34%')),
                
                html.Div(className='four columns', children=[
                    dcc.Dropdown(options=lista_periodos, value="1º Trimestre", id='id_dd_periodo', clearable=False, className="dbc"),
                    # dbc.Select(options=lista_periodos, value="1º Trimestre", id='id_dd_periodo'),
                ],style=dict(width='33%')),
                
                html.Div(className='four columns', children=[
                    dcc.Dropdown(options=lista_disciplinas, value="Língua Portuguesa", id='id_dd_disciplina', clearable=False, className="dbc"),
                    # dbc.Select(options=lista_disciplinas, value="Matemática", id='id_dd_disciplina'),
                ],style=dict(width='33%')),
            ], style=dict(display='flex')
        ),

        dcc.Graph(id="graph_pie"),

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

        dcc.Graph(id="graph_comparativo"),
    ],style={"text-align": "center"}
)

@app.callback(
    [
        Output("aprov_trimestral", "style"),
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


@app.callback(
    [
        Output("graph_histogram", "figure"),
        Output("graph_comparativo", "figure"),
        Output("graph_pie", "figure"),
        Output("id_tabela_pie", "children"),
    ],

    [
        Input("id_dd_ano", "value"),
        Input("id_dd_periodo", "value"),
        Input("id_dd_disciplina", "value"),
        Input("id_check_graph", "value"),
    ],
)

def update_graphs(ano, periodo, disciplina, parciais):

    query = "Ano == \'" + ano + "\'"
    dff = df.query(query).sort_values(by=['Disciplina', 'Período'])

    dff = dff[dff['Avaliação'] != 'Média da Turma']

    if parciais:
        dff = pd.DataFrame(dff.groupby(by=['Disciplina', 'Período', 'Avaliação'])['Nota'].sum())
    else:
        dff = pd.DataFrame(dff.groupby(by=['Disciplina', 'Período'])['Nota'].sum())

    dff.reset_index(inplace=True)

    titulo_histogram = "<b>Aproveitamento Trimestral - " + ano + " Ano</b>"

    if parciais:    
        fig_histogram = px.bar(dff, x="Período", y="Nota", color="Disciplina", barmode='group', hover_name='Disciplina', hover_data=['Avaliação'],
            text='Nota', height=500, color_discrete_sequence=px.colors.qualitative.Pastel).update_layout(
            title={"text": titulo_histogram, "x": 0.5}, title_font_color = px.colors.qualitative.Pastel[0],
            yaxis_title = "Média no Período",
            paper_bgcolor = 'rgba(0,0,0, 0)',
            # font = {"color": '#839496'},
            # font = {"color": '#EBEBEB'},
            # plot_bgcolor = 'rgba(0,0,0, 0)',
        )
        fig_histogram.update_yaxes(gridcolor="#CCC")
    else:
        fig_histogram = px.bar(dff, x="Período", y="Nota", color="Disciplina", barmode='group', hover_name='Disciplina',
            text='Nota', height=500, color_discrete_sequence=px.colors.qualitative.Pastel).update_layout(
            title={"text": titulo_histogram, "x": 0.5}, title_font_color = px.colors.qualitative.Pastel[0],
            yaxis_title = "Média no Período",
            paper_bgcolor = 'rgba(0,0,0,0)',
            # font = {"color": '#839496'},
            # font = {"color": '#EBEBEB'},
            # plot_bgcolor = 'rgba(0,0,0, 0)',
        )
        fig_histogram.update_yaxes(gridcolor="#CCC")

    titulo_comparativo = "<b>Comparativo com a Média da Turma no " + periodo + "</b>"

    query = "Ano == \'" + ano + "\' & Período == \'" + periodo + "\'"
    dff = df.query(query).sort_values(by=['Disciplina', 'Período'])

    dfm = dff[dff['Avaliação'] == 'Média da Turma']
    dfm = dfm.dropna(subset = ['Nota'])

    dt = dtotals.query(query).sort_values(by=['Disciplina', 'Período'])

    fig_comparativo = px.line().update_layout(
            title={"text": titulo_comparativo, "x": 0.5}, title_font_color = px.colors.qualitative.Pastel[0],
            yaxis_title="Média do " + periodo, xaxis_title="Disciplina",
            paper_bgcolor = 'rgba(0,0,0,0)'
            )

    fig_comparativo.add_scatter(x=dt['Disciplina'], y=dt['Nota'], text=dt['Nota'], name="Média do Augusto", marker_color=px.colors.qualitative.Prism[2], textfont_color=px.colors.qualitative.Prism[1])
    fig_comparativo.add_scatter(x=dfm['Disciplina'], y=dfm['Nota'], text=dfm['Nota'], name="Média da Turma", marker_color=px.colors.qualitative.Light24[23], textfont_color=px.colors.qualitative.Light24[22])
    fig_comparativo.update_traces(textposition='top center', mode="markers+lines+text", showlegend=True, line_shape='spline')
    fig_comparativo.update_layout(hovermode="x unified")

    query = "Ano == \'" + ano + "\' & Disciplina == \'"+ disciplina + "\' & Período == \'" + periodo + "\'"
    dff = df.query(query).sort_values(by=['Avaliação'])
    dff = dff[dff['Avaliação'] != 'Média da Turma']

    soma = float("{:.1f}".format(dff['Nota'].sum()))

    titulo_pie = "<b>" + disciplina + " - " + ano + " Ano - Média do " + periodo + ": " + str(soma) + "</b>"
    fig_pie = px.pie(dff, values="Nota", names="Avaliação", hole=.2, color_discrete_sequence=px.colors.qualitative.Pastel2).update_layout(
        title={"text": titulo_pie, "x": 0.5}, title_font_color = px.colors.qualitative.Pastel[0],
        paper_bgcolor = 'rgba(0,0,0,0)',
        # font = {"color": '#839496'},
        # font = {"color": '#EBEBEB'},
        # plot_bgcolor = 'rgba(0,0,0,0)',
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")

    # table = dbc.Table.from_dataframe(dff.dropna(subset = ['Nota']), responsive=True, striped=True, bordered=True, hover=True)
    table = dbc.Table.from_dataframe(dff.dropna(subset = ['Nota']), responsive=True, striped=True, bordered=False, hover=True, dark=False, style={'vertical-align' : 'middle'})
    
    return fig_histogram, fig_comparativo, fig_pie, table

if __name__ == '__main__':
    app.run_server(debug=False)