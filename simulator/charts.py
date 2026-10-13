import numpy as np
import plotly.graph_objects as go
from .education import brl

TEAL, BLUE, AMBER = "#087E69", "#8570B4", "#A8783D"


def style(fig, title, x="Anos", y="Resultado líquido (R$)"):
    fig.update_layout(title=dict(text=title, font=dict(size=18, family="Manrope, sans-serif")), template="plotly_white",
                      font=dict(family="DM Sans, sans-serif", color="#253047"), height=440,
                      margin=dict(l=25, r=25, t=65, b=35), paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)", separators=",.",
                      xaxis_title=x, yaxis_title=y, hovermode="x unified",
                      legend=dict(orientation="h", y=-.22, x=0))
    fig.update_yaxes(gridcolor="#E6E8EF", tickprefix="R$ ", zerolinecolor="#9AAABA")
    return fig


def line(fig, x, y, name, color=TEAL, dash=None, width=3):
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name=name,
                            line=dict(color=color, width=width, dash=dash),
                            customdata=[brl(v) for v in y],
                            hovertemplate="%{customdata}<extra>%{fullData.name}</extra>"))


def band(fig, x, low, high):
    fig.add_trace(go.Scatter(x=x, y=low, mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=x, y=high, mode="lines", line=dict(width=0), fill="tonexty",
                            fillcolor="rgba(133,112,180,.13)", name="Faixa pontual P5–P95", hoverinfo="skip"))


def evolution(result, by_bet=False):
    t = result["timeline"]
    x = t["bets"] if by_bet else t["years"]
    fig = go.Figure()
    band(fig, x, t["p05"], t["p95"])
    for i, trajectory in enumerate(t["sample"][:6]):
        line(fig, x, trajectory, f"Trajetória {i + 1}", color="#B3A8C9", width=1)
    line(fig, x, t["mean"], "Média simulada")
    line(fig, x, t["expected"], "Valor esperado teórico", BLUE, "dash", 2)
    return style(fig, "Muitos percursos. As mesmas hipóteses.", "Número de apostas" if by_bet else "Anos")


def distribution(result):
    m = result["simulation"]
    fig = go.Figure(go.Histogram(x=result["final_profit"], nbinsx=60, marker_color=BLUE,
                                  name="Simulações", hovertemplate="Resultado: R$ %{x:,.2f}<br>Simulações: %{y}<extra></extra>"))
    fig.add_vrect(x0=m["p05"], x1=m["p95"], fillcolor=BLUE, opacity=.08, line_width=0)
    for val, label, color, pos in [(0, "Equilíbrio", "#394B60", "top left"),
                                   (m["mean"], "Média", BLUE, "top right"),
                                   (m["median"], "Mediana", AMBER, "bottom right")]:
        fig.add_vline(x=val, line_color=color, line_dash="dash", annotation_text=label, annotation_position=pos)
    fig = style(fig, "Como os resultados finais se distribuem", "Resultado líquido final (R$)", "Número de simulações")
    fig.update_yaxes(tickprefix="")
    fig.update_layout(hovermode="closest", annotations=list(fig.layout.annotations) + [
        dict(x=.02, y=.96, xref="paper", yref="paper", showarrow=False,
             text=f"P5: {brl(m['p05'])} · P95: {brl(m['p95'])}", bgcolor="white")])
    return fig


def observed(result):
    t = result["timeline"]
    fig = go.Figure()
    line(fig, t["bets"], t["sample"][0], "Trajetória simulada 1", AMBER)
    line(fig, t["bets"], t["expected"], "Valor esperado teórico", BLUE, "dash")
    return style(fig, "O valor esperado não é um destino", "Número de apostas")


def investment(result):
    t = result["timeline"]
    budget = np.array(t["budget"])
    fig = go.Figure()
    band(fig, t["years"], np.array(t["p05"]) + budget, np.array(t["p95"]) + budget)
    line(fig, t["years"], np.array(t["expected"]) + budget, "Apostas · patrimônio esperado", BLUE)
    line(fig, t["years"], t["investment"], "Investimento · hipótese determinística", TEAL)
    line(fig, t["years"], budget, "Recursos destinados", "#7A8593", "dot", 2)
    return style(fig, "O mesmo orçamento, dois caminhos", y="Patrimônio acumulado (R$)")


def sensitivity_plot(rows, label):
    fig = go.Figure()
    for name, color, dash in [("Resultado esperado", BLUE, None), ("Orçamento", AMBER, "dot")]:
        line(fig, [r["Parâmetro"] for r in rows], [r[name] for r in rows], name, color, dash)
    return style(fig, "O efeito de mudar uma hipótese", label, "Reais (R$)")


def scenario_plot(rows):
    fig = go.Figure()
    for name, color in [("Orçamento", "#B3A8C9"), ("Patrimônio esperado das apostas", BLUE), ("Investimento final", TEAL)]:
        fig.add_bar(x=[r["Cenário"] for r in rows], y=[r[name] for r in rows], name=name, marker_color=color,
                    customdata=[brl(r[name]) for r in rows], hovertemplate="%{customdata}<extra>%{fullData.name}</extra>")
    return style(fig, "Compare os recursos e os patrimônios", "Cenário", "Reais (R$)")
