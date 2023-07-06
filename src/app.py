from dash import Dash, dcc, html, Output, Input, State, dash_table

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

app = Dash(__name__, external_stylesheets=[dbc.themes.LUMEN],
            meta_tags=[{'name': 'viewport',
                        'content': 'width=device-width, initial-scale=1.0'},
                        {'http-equiv': 'content-language',
                            'content': 'pt-br'},
                    ]
        )
server = app.server

app.title = 'Notas CETEC Augusto Marques dos Passos'

df = pd.read_csv('src/df_notas_cetec_augusto.csv')

lista_anos = df['Ano'].unique().tolist()
lista_disciplinas = sorted(df['Disciplina'].unique().tolist())
lista_periodos = df['Período'].unique().tolist()

dtotals = pd.DataFrame(columns = ['Ano', 'Disciplina', 'Período', 'Nota'])

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
        soma = 0
        for p in lista_periodos:
            query = "Ano == \'" + a + "\' & Disciplina == \'"+ d + "\' & Período == \'" + p + "\'"
            dff = df.query(query).sort_values(by=['Avaliação'], ascending=False)
            soma += dff['Nota'].sum()

            addRowinTotals(a, d, p, float("{:.1f}".format(dff['Nota'].sum())))

        addRowinTotals(a, d, "Avaliação Final", float("{:.1f}".format(soma / len(lista_periodos))))

dfpivot_totals = dtotals.pivot(index="Disciplina", columns="Período", values="Nota")

dfpivot_totals = dfpivot_totals.reset_index()
dfpivot_totals.columns.name = None


app.layout = dbc.Container(
    children = [
        html.H1("Notas CETEC Augusto Marques dos Passos", style={"text-align": "center"}),

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
                    dbc.Table.from_dataframe(dfpivot_totals, responsive=True, striped=True, bordered=True, hover=True)
                ],
                id="aprov_trimestral", 
            ),

        html.Div(
            className="row", children=[
                html.Div(className='four columns', children=[
                    # dcc.Dropdown(options=lista_anos, value="6º", id='id_dd_ano'),
                    dbc.Select(options=lista_anos, value="6º", id='id_dd_ano'),
                ],style=dict(width='34%')),
                
                html.Div(className='four columns', children=[
                    # dcc.Dropdown(options=lista_periodos, value="1º Trimestre", id='id_dd_periodo'),
                    dbc.Select(options=lista_periodos, value="1º Trimestre", id='id_dd_periodo'),
                ],style=dict(width='33%')),
                
                html.Div(className='four columns', children=[
                    # dcc.Dropdown(options=lista_disciplinas, value="Língua Portuguesa", id='id_dd_disciplina'),
                    dbc.Select(options=lista_disciplinas, value="Matemática", id='id_dd_disciplina'),
                ],style=dict(width='33%')),
            ], style=dict(display='flex')
        ),

        dcc.Graph(id="graph_pie"),
        html.Div(id="id_tabela", style={"text-align": "center", "font-size": "0.875em"}),
        html.Div(id="nothing")
    ],style={"text-align": "center"}
)

@app.callback(
    Output("aprov_trimestral", "style"),
    Input("id_check_table", "value"),
)

def showTotalsTable(check):

    if check:
        return {"text-align": "center", "font-size": "0.875em", "display": "block",}
    else:
        return {"text-align": "center", "font-size": "0.875em", "display": "none",}

@app.callback(
    [
        Output("graph_histogram", "figure"),
        Output("graph_pie", "figure"),
        Output("id_tabela", "children"),
        Output("nothing", "disable_n_clicks")
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

    if parciais:
        dff = pd.DataFrame(dff.groupby(by=['Disciplina', 'Período', 'Avaliação'])['Nota'].sum())
    else:
        dff = pd.DataFrame(dff.groupby(by=['Disciplina', 'Período'])['Nota'].sum())

    dff.reset_index(inplace=True)

    titulo_histogram = "Aproveitamento Trimestral - " + ano + " Ano"

    if parciais:    
        fig_histogram = px.bar(dff, x="Período", y="Nota", color="Disciplina", barmode='group', hover_name='Disciplina', hover_data=['Avaliação'], text='Nota', height=500).update_layout(
            title={"text": titulo_histogram, "x": 0.5}, yaxis_title="Média Final do Trimestre",
            paper_bgcolor = 'rgba(0,0,0,0)',
            # font = {"color": '#839496'},
            # font = {"color": '#EBEBEB'},
            # plot_bgcolor = 'rgba(0,0,0,0)',
        )
    else:
        fig_histogram = px.bar(dff, x="Período", y="Nota", color="Disciplina", barmode='group', hover_name='Disciplina', text='Nota', height=500).update_layout(
            title={"text": titulo_histogram, "x": 0.5}, yaxis_title="Média Final do Trimestre",
            paper_bgcolor = 'rgba(0,0,0,0)',
            # font = {"color": '#839496'},
            # font = {"color": '#EBEBEB'},
            # plot_bgcolor = 'rgba(0,0,0,0)',
        )

    query = "Ano == \'" + ano + "\' & Disciplina == \'"+ disciplina + "\' & Período == \'" + periodo + "\'"
    dff = df.query(query).sort_values(by=['Avaliação'])

    soma = float("{:.1f}".format(dff['Nota'].sum()))

    titulo_pie = disciplina + " - " + ano + " Ano - " + periodo + " - Média Final: " + str(soma)
    fig_pie = px.pie(dff, values="Nota", names="Avaliação", hole=.2).update_layout(
        title={"text": titulo_pie, "x": 0.5},
        paper_bgcolor = 'rgba(0,0,0,0)',
        # font = {"color": '#839496'},
        # font = {"color": '#EBEBEB'},
        # plot_bgcolor = 'rgba(0,0,0,0)',
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")

    table = dbc.Table.from_dataframe(dff.dropna(subset = ['Nota']), responsive=True, striped=True, bordered=True, hover=True)

    return fig_histogram, fig_pie, table, parciais

if __name__ == '__main__':
    app.run_server(debug=False)