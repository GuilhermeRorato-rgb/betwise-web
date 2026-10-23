import json
from dataclasses import asdict
from pathlib import Path
import pandas as pd
import streamlit as st
from simulator.api import simulate
from simulator.model import Parameters, overround
from simulator.education import brl, pct, CONCEPTS, BIASES
from simulator.scenarios import default_scenarios, compare, sensitivity
from simulator import charts


@st.cache_data(max_entries=4, show_spinner=False)
def cached(params):
    return simulate(params, include_distribution=True)


def reset_inputs():
    st.session_state.pop("betwise_simulator_inputs", None)
    for key in list(st.session_state):
        if key.startswith("bw_sim_input_"):
            del st.session_state[key]



def mostrar_simulador():
    from simulator.shared import restore, save
    returning = "bw_sim_mode" not in st.session_state
    # A cópia permanente sobrevive à remoção de widgets na aba do assistente.
    if "bw_sim_mode" not in st.session_state:
        st.session_state["bw_sim_mode"] = st.session_state.get("betwise_mode_saved", "Simples")
    mode = st.radio("Como você quer usar o simulador?", ["Simples", "Completo"],
                    horizontal=True, key="bw_sim_mode", on_change=save, args=(st.session_state,))
    restore(st.session_state, force=returning or mode != st.session_state.get("betwise_mode_saved"))
    st.session_state["betwise_mode_saved"] = mode
    st.caption("Simples: três perguntas e uma explicação direta. Completo: todos os ajustes, gráficos e detalhes. Os dois modos usam os mesmos valores e hipóteses.")
    if mode == "Simples":
        from simulator.simple import mostrar_simples
        mostrar_simples()
    else:
        mostrar_completo()


def mostrar_completo():

    for key, value in st.session_state.get("betwise_simulator_inputs", {}).items():
        if key not in st.session_state:
            st.session_state[key] = value
    css = (Path(__file__).parent / "simulator" / "ui.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    with st.container(key="simulator_workspace"):
        st.markdown('<div class="sim-hero"><div class="welcome-eyebrow">SEU ESPAÇO PARA EXPLORAR</div><h1>Pequenas decisões.<br><span class="hero-accent">Mais perspectiva.</span></h1><p>Explore as probabilidades, os riscos e o efeito do tempo.<br>Compare o que os mesmos recursos poderiam acumular.</p><div class="topic-pills"><span>01 &nbsp; Probabilidade</span><span>02 &nbsp; Risco financeiro</span><span>03 &nbsp; Custo de oportunidade</span></div></div>', unsafe_allow_html=True)
        st.markdown('<div class="ethical-strip"><span aria-hidden="true">◇</span><span><b>Uma experiência educativa.</b> Hipóteses editáveis, não previsões de eventos reais. Sem promessa de ganhos.</span></div>', unsafe_allow_html=True)
        with st.expander("Configurar cenário", expanded=False):
            st.caption("Valores demonstrativos: hipóteses editáveis, não estatísticas do mercado.")
            st.button("Redefinir parâmetros", on_click=reset_inputs, width="stretch")
            left, middle, right = st.columns(3)
            with left:
                stake = st.number_input("Valor por aposta (R$)", .01, 1000000., 20., 5., key="bw_sim_input_stake")
                frequency = st.number_input("Quantidade por período", .01, 1000., 5., 1., key="bw_sim_input_frequency")
                unit = st.selectbox("Período", ["dia", "semana", "mês"], index=1, key="bw_sim_input_unit")
                duration = st.number_input("Duração", .01, 600., 3., 1., key="bw_sim_input_duration")
                duration_unit = st.selectbox("Unidade da duração", ["anos", "meses"], key="bw_sim_input_duration_unit")
            with middle:
                odds = st.number_input("Odd decimal média", 1.01, 1000., 2., .05, key="bw_sim_input_odds")
                method = st.radio("Como definir a chance?", ["Margem hipotética", "Probabilidade informada"], key="bw_sim_input_method")
                p, h = .475, .05
                if method == "Margem hipotética":
                    h = st.slider("Desvantagem esperada (%)", 0., 100., 5., .5, key="bw_sim_input_h") / 100
                    st.caption(f"Chance compatível: {pct((1-h)/odds)}. Desvantagem assumida; não observada.")
                else:
                    p = st.slider("Probabilidade hipotética de vitória (%)", 0., 100., 47.5, .5, key="bw_sim_input_p") / 100
                    st.caption("Sua estimativa é uma premissa, não uma previsão validada.")
                st.caption(f"Probabilidade implícita na odd: {pct(1/odds)}. Não revela a chance real.")
            with right:
                annual = st.number_input("Rentabilidade anual hipotética (%)", -99., 100., 8., .5, key="bw_sim_input_annual") / 100
                with st.expander("Precisão e reprodutibilidade"):
                    sims = st.selectbox("Simulações", [1000, 10000, 25000, 50000, 100000], index=1, key="bw_sim_input_sims")
                    fixed = st.checkbox("Usar semente fixa", True, key="bw_sim_input_fixed")
                    seed = int(st.number_input("Semente", 0, 4294967295, 42, key="bw_sim_input_seed")) if fixed else None
                    st.caption("Mais simulações reduzem o erro amostral, não a incerteza dos eventos.")
                run = st.button("Executar novos sorteios", type="primary", width="stretch")

        for key in list(st.session_state):
            if key.startswith("bw_sim_input_"):
                st.session_state.setdefault("betwise_simulator_inputs", {})[key] = st.session_state[key]
        params = dict(stake=stake, frequency=frequency, frequency_unit=unit, duration=duration,
                      duration_unit=duration_unit, odds=odds, probability_mode="margem" if method == "Margem hipotética" else "informada",
                      probability=p, disadvantage=h, annual_return=annual, simulations=sims, seed=seed)
        try:
            config = Parameters(**params)
        except ValueError as exc:
            st.error(str(exc))
            st.stop()

        # Uma semente aleatória permanece estável até mudar parâmetros ou pedir novos sorteios.
        if seed is None:
            import secrets
            fingerprint = json.dumps(params, sort_keys=True)
            if run or st.session_state.get("random_fingerprint") != fingerprint:
                st.session_state["random_seed"] = secrets.randbelow(2**32)
                st.session_state["random_fingerprint"] = fingerprint
            params["seed"] = st.session_state["random_seed"]
        with st.spinner("Calculando trajetórias e comparação financeira…"):
            result = cached(params)
        t, m = result["theoretical"], result["simulation"]

        cols = st.columns(4)
        cols[0].metric("Total destinado às apostas", brl(t["budget"]), help="Soma de todos os aportes. Não é a perda nem uma banca inicial.")
        cols[1].metric("Resultado líquido esperado", brl(t["expected_profit"]), help="Média teórica: pagamentos menos o total apostado.")
        cols[2].metric("Chance simulada de prejuízo", pct(m["loss_probability"]), help="Fração das simulações que terminou com lucro líquido estritamente negativo.")
        cols[3].metric("Custo de oportunidade esperado", brl(t["opportunity_cost"]), help="Investimento final menos patrimônio esperado das apostas.")
        years_label = f"{t['years']:.2f}".replace(".", ",")
        n_label, sims_label = f"{t['n']:,}".replace(",", "."), f"{sims:,}".replace(",", ".")
        st.caption(f"{n_label} apostas · {years_label} anos · {sims_label} simulações · semente {result['seed_used']}")

        page = st.radio("Explore a análise", ["Resultados financeiros", "Evolução temporal", "Apostas versus investimentos", "Comparação de cenários", "Entenda os resultados"], horizontal=True, label_visibility="collapsed", key="bw_sim_input_analysis_page")


        def plot(fig):
            st.plotly_chart(fig, width="stretch", config={"displaylogo": False, "displayModeBar": False, "locale": "pt-BR"})


        if page == "Resultados financeiros":
            plot(charts.distribution(result))
            c1, c2 = st.columns([1.2, 1])
            with c1:
                st.subheader("O que os sorteios mostram")
                data = [("Média", brl(m["mean"]), brl(t["expected_profit"])),
                        ("Mediana", brl(m["median"]), "—"), ("Desvio-padrão", brl(m["std"]), brl(t["std"])),
                        ("Percentil 5", brl(m["p05"]), brl(t["p05"])), ("Percentil 95", brl(m["p95"]), brl(t["p95"])),
                        ("Prejuízo", pct(m["loss_probability"]), pct(t["loss_probability"])),
                        ("Lucro", pct(m["profit_probability"]), pct(t["profit_probability"])),
                        ("Empate", pct(m["tie_probability"]), pct(t["tie_probability"]))]
                st.dataframe(pd.DataFrame(data, columns=["Indicador", "Simulado", "Teórico / binomial"]), hide_index=True, width="stretch")
            with c2:
                st.subheader("Como interpretar")
                st.write(result["explanations"][0].replace("$", r"\$"))
                st.write(result["explanations"][2].replace("$", r"\$"))
                st.caption(f"Erro-padrão estimado da média de Monte Carlo: {brl(m['mean_standard_error'])}. Ele mede a precisão da média simulada, não o risco de uma pessoa.")
                st.info("A probabilidade de prejuízo não é uma medida de ruína financeira. Este modelo não possui banca inicial nem interrupção por falta de saldo.")

        elif page == "Evolução temporal":
            by_bet = st.toggle("Mostrar número de apostas no eixo horizontal")
            plot(charts.evolution(result, by_bet))
            st.caption("Faixa P5–P95 em cada instante, sem garantia de que uma trajetória inteira permaneça dentro dela. Até 240 intervalos são mostrados; linhas conectam pontos de avaliação.")
            plot(charts.observed(result))
            st.write("Uma pessoa percorre uma trajetória, não a média. Com poucas apostas, o acaso pode predominar; com muitas, um retorno médio negativo pode coexistir com perdas acumuladas cada vez maiores.")

        elif page == "Apostas versus investimentos":
            plot(charts.investment(result))
            st.info("A cada oportunidade, o mesmo valor é destinado a uma das alternativas. Os pagamentos brutos das apostas são preservados sem rendimento e não são reapostados.")
            data = [
                ["Recursos destinados", brl(t["budget"]), brl(t["budget"])],
                ["Patrimônio final", brl(t["betting_wealth_expected"]) + " (esperado)", brl(t["investment_final"])],
                ["Resultado líquido", brl(t["expected_profit"]) + " (esperado)", brl(t["investment_profit"])],
                ["P5 do patrimônio simulado", brl(m["p05"] + t["budget"]), "Não simulado"],
                ["P95 do patrimônio simulado", brl(m["p95"] + t["budget"]), "Não simulado"],
            ]
            st.dataframe(pd.DataFrame(data, columns=["Medida", "Apostar", "Investir"]), hide_index=True, width="stretch")
            st.write(result["explanations"][3].replace("$", r"\$"))
            st.caption("Valores nominais. Inflação reduz poder de compra; impostos e custos podem reduzir rendimentos. A taxa constante é hipotética, inclusive podendo ser negativa. Não é aconselhamento financeiro personalizado.")
            st.caption("Aportes no fim de intervalos regulares: i/frequência anual. Ano = 365 dias; semana = 7 dias; mês = 1/12 de ano. O número de apostas é arredondado para baixo e eventual intervalo final sem aporte ainda rende no investimento.")

        elif page == "Comparação de cenários":
            st.subheader("Mude uma hipótese. Compare as consequências.")
            labels = {"stake": "Valor por aposta (R$)", "frequency": f"Frequência por {unit}", "duration": f"Duração em {duration_unit}", "odds": "Odd decimal", "probability": "Probabilidade (fração)"}
            field = st.selectbox("Sensibilidade do cenário atual", list(labels), format_func=lambda x: labels[x])
            plot(charts.sensitivity_plot(sensitivity(config, field), labels[field]))
            st.caption("Variações de 50% a 150% da hipótese atual, limitadas ao domínio válido. Ao variar a odd no método de margem, h permanece fixo e o retorno esperado permanece −h. Ao variar a probabilidade, ela é informada diretamente e a odd fica fixa.")
            st.subheader("Seus cenários")
            st.write("Edite as células e use a última linha para adicionar cenários. Aqui, frequência é semanal, duração é em anos e a probabilidade é informada diretamente.")
            if "scenario_version" not in st.session_state:
                st.session_state.scenario_version = 0
            if st.button("Redefinir cenários"):
                st.session_state.scenario_version += 1
                st.session_state["scenario_saved"] = default_scenarios()
            scenario_key = f"scenarios_{st.session_state.scenario_version}"
            if scenario_key not in st.session_state:
                st.session_state["scenario_base"] = st.session_state.get("scenario_saved", default_scenarios())
            edited = st.data_editor(pd.DataFrame(st.session_state["scenario_base"]), num_rows="dynamic", hide_index=True,
                                    key=scenario_key, width="stretch",
                                    column_config={"nome": st.column_config.TextColumn("Nome", required=True),
                                        "valor": st.column_config.NumberColumn("R$ por aposta", min_value=.01, max_value=1000000., required=True),
                                        "frequência": st.column_config.NumberColumn("Apostas/semana", min_value=.01, max_value=1000., required=True),
                                        "anos": st.column_config.NumberColumn("Anos", min_value=.01, max_value=50., required=True),
                                        "odd": st.column_config.NumberColumn("Odd", min_value=1.01, max_value=1000., required=True),
                                        "probabilidade": st.column_config.NumberColumn("Vitória (%)", min_value=0., max_value=100., required=True),
                                        "taxa": st.column_config.NumberColumn("Retorno anual (%)", min_value=-99., max_value=100., required=True)})
            st.session_state["scenario_saved"] = edited.to_dict("records")
            try:
                if len(edited) < 3:
                    st.warning("Mantenha pelo menos três cenários para a comparação acadêmica.")
                if len(edited) > 20:
                    raise ValueError("Compare até 20 cenários por vez.")
                rows = compare(edited.to_dict("records"))
                if rows:
                    plot(charts.scenario_plot(rows))
                    frame = pd.DataFrame(rows)
                    formatted = frame.copy()
                    for col in frame.columns:
                        if col not in ("Cenário", "Apostas"):
                            formatted[col] = frame[col].map(lambda v: pct(v/100) if "(%)" in col else brl(v))
                    st.dataframe(formatted, hide_index=True, width="stretch")
                    st.caption("Os orçamentos podem ser diferentes. O ROI normaliza o resultado esperado por real destinado. Probabilidades são binomiais exatas; esta tabela não executa novos sorteios.")
                    st.download_button("Baixar comparação (CSV)", frame.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"), "cenarios.csv", "text/csv")
            except (ValueError, TypeError, KeyError) as exc:
                st.error(f"Revise as células dos cenários: {exc}")

        else:
            st.subheader("Explicações a partir dos seus resultados")
            st.caption("Painel educativo baseado em regras e cálculos. Não é uma IA generativa em funcionamento.")
            for text in result["explanations"]:
                st.write(text.replace("$", r"\$"))
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Conceitos econômicos")
                for title, text in CONCEPTS.items():
                    with st.expander(title):
                        st.write(text.replace("$", r"\$"))
            with c2:
                st.subheader("Como percebemos as decisões")
                for title, text in BIASES.items():
                    with st.expander(title):
                        st.write(text)
            st.subheader("Overround de um mercado completo")
            raw = st.text_input("Odds de todos os resultados (separadas por ponto e vírgula)", "1,90; 1,90")
            exhaustive = st.checkbox("Os resultados são mutuamente exclusivos e cobrem todo o mercado")
            if exhaustive:
                try:
                    value = overround([float(s.strip().replace(",", ".")) for s in raw.split(";")])
                    st.metric("Overround", pct(value))
                    st.caption("Este valor não substitui h nem altera a simulação. Overround e perda esperada efetiva não são necessariamente iguais.")
                except ValueError as exc:
                    st.error(f"Odds inválidas: {exc}")
            st.markdown("Se as apostas estiverem causando dificuldades, consulte as fontes oficiais: [autoexclusão centralizada](https://www.gov.br/pt-br/servicos/plataforma-centralizada-de-autoexclusao-apostas) e [orientações do Ministério da Fazenda, incluindo busca de apoio em UBS e CAPS](https://www.gov.br/fazenda/pt-br/central-de-conteudo/publicacoes/apresentacoes/2025/dezembro/ppt-jogos-de-apostas-quarta-10h20-1.pdf).")

        st.divider()
        st.subheader("Transparência metodológica")
        st.caption("Sempre visível: premissas hipotéticas, apostas independentes, odd e chance constantes, aportes recorrentes, sem banca inicial. Não há previsão de eventos reais, estratégias de ganho ou promessa de rentabilidade. Nenhum dado pessoal é solicitado.")
        with st.expander("Fórmulas, convenções e limites"):
            st.latex(r"L=s(oX-1),\quad X\sim Bernoulli(p),\quad E[L]=s(po-1)")
            st.latex(r"Var(L)=s^2o^2p(1-p),\quad E[S_N]=NE[L],\quad Var(S_N)=NVar(L)")
            st.latex(r"p=(1-h)/o,\quad ROI=po-1,\quad K\sim Binomial(N,p)")
            st.latex(r"V_I(T)=\sum_{i=1}^N s(1+r)^{T-i/f},\quad V_A=soK,\quad CO=V_I-E[V_A]")
            st.write("N = piso(T × f), com f em apostas por ano. Aportes nos instantes i/f, em anos. O investimento usa taxas efetivas e juros compostos. O primeiro aporte não ocorre no instante zero.")
            st.write("As somas de Bernoulli são sorteadas por incrementos binomiais exatos entre até 240 intervalos, conservando a distribuição conjunta nos pontos exibidos. Não são armazenados todos os eventos individuais. Os percentis usam interpolação linear e o desvio-padrão amostral usa n−1.")
            st.write("Limites computacionais: até 100 mil simulações, 1 milhão de apostas e 50 anos. Correlações, mudanças de odds, resultados não binários, custos, impostos, inflação, reinvestimento de prêmios e comportamento adaptativo estão fora do modelo.")
            st.write("O workbook e a base de conhecimento citados na solicitação não foram recebidos. A aderência foi verificada contra o texto fornecido; os critérios específicos do workbook e sua bibliografia permanecem pendentes.")
            st.markdown("Referências técnicas: [NumPy — binomial](https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.binomial.html) · [SciPy — distribuição binomial](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binom.html). Documentação do módulo está em `docs/simulador/`.")

        compact = {k: v for k, v in result.items() if k not in ("final_profit", "final_betting_wealth")}
        dl1, dl2 = st.columns(2)
        dl1.download_button("Baixar resultados e premissas (JSON)", json.dumps(compact, ensure_ascii=False, indent=2, allow_nan=False), "simulacao.json", "application/json")
        final_df = pd.DataFrame({"resultado_liquido_brl": result["final_profit"], "patrimonio_apostas_brl": result["final_betting_wealth"]})
        dl2.download_button("Baixar distribuição simulada (CSV)", final_df.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"), "distribuicao.csv", "text/csv")




        for key in list(st.session_state):
            if key.startswith("bw_sim_input_"):
                st.session_state.setdefault("betwise_simulator_inputs", {})[key] = st.session_state[key]

