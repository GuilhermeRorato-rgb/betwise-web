"""Leitura guiada do mesmo modelo, com cenário compartilhado."""
from pathlib import Path
import streamlit as st
from simulator.model import Parameters, theoretical
from simulator.education import brl, pct
from simulator.shared import configuration, save


def simple_result(stake, count, months):
    return theoretical(Parameters(stake=stake, frequency=count, frequency_unit="mês",
                                  duration=months, duration_unit="meses",
                                  odds=2., disadvantage=.05, annual_return=0.))


def mostrar_simples():
    css = (Path(__file__).parent / "ui.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    with st.container(key="simulator_workspace"):
        with st.container(key="simple_workspace"):
            st.markdown('<div class="sim-hero"><div class="welcome-eyebrow">UM PASSO DE CADA VEZ</div><h1>Seu dinheiro.<br><span class="hero-accent">Veja a diferença.</span></h1><p>Quanto vai para as apostas? E se você guardar esse dinheiro?<br>Responda três perguntas para comparar.</p></div>', unsafe_allow_html=True)
            st.subheader("1. Conte como seria")
            stake = st.number_input("Quanto você coloca em cada aposta? (R$)", min_value=.01, max_value=1000000., step=5., key="bw_sim_input_stake")
            unit = st.session_state["bw_sim_input_unit"]
            duration_unit = st.session_state["bw_sim_input_duration_unit"]
            count = st.number_input(f"Quantas apostas você faz por {unit}?", min_value=.01, max_value=1000., step=1., key="bw_sim_input_frequency")
            duration = st.number_input(f"Por quanto tempo? ({duration_unit})", min_value=.01, max_value=600., step=1., key="bw_sim_input_duration")
            save(st.session_state)
            st.write("Os resultados mudam assim que você altera uma resposta. Para mudar a unidade de tempo ou as outras hipóteses, use o modo Completo.")
            try:
                config = configuration(st.session_state)
            except ValueError:
                st.error("Essa combinação precisa de ajuste: escolha um período de até 50 anos e uma frequência que resulte em pelo menos 1 e no máximo 1 milhão de apostas.")
                return
            t = theoretical(config)
            period = f"{duration:g} {duration_unit}".replace(".", ",")
            difference = t["expected_profit"]
            outcome = f"{brl(abs(difference))} a menos" if difference < -1e-8 else (f"{brl(difference)} a mais" if difference > 1e-8 else "O mesmo valor")
            savings = "Se guardar sem apostar" if config.annual_return == 0 else "Se aplicar sem apostar"
            savings_note = "Sem contar juros e sem gastar esse valor." if config.annual_return == 0 else f"Com a taxa escolhida de {pct(config.annual_return)} ao ano. É uma hipótese constante, não uma promessa de rendimento."
            st.info(f"Este é um exemplo para aprender, não uma previsão. Se acertar, cada {brl(stake)} apostados devolve {brl(stake * config.odds)}, incluindo o valor colocado. A chance de acerto escolhida é {pct(config.p)}. São as mesmas hipóteses do modo Completo.")
            st.caption(f"Odd usada neste cálculo: {config.odds:g}".replace(".", ","))
            if config.probability_mode == "margem":
                st.caption("Com a desvantagem fixa, mudar a odd também muda a chance de acerto. Por isso o valor médio pode continuar igual, mesmo com a nova odd. Para manter a chance fixa, escolha ‘Probabilidade informada’ no modo Completo.")
            st.subheader(f"2. Veja o dinheiro em {period}")
            st.markdown(f'<div class="simple-total"><span>Somando todas as suas apostas</span><strong>{brl(t["budget"])}</strong><p>{t["n"]} apostas de {brl(stake)} ao longo de {period}.<br>Esse é o total colocado nas apostas. Não é o valor perdido.</p></div>', unsafe_allow_html=True)
            left, right = st.columns(2)
            with left:
                st.markdown(f'<div class="simple-card"><span>Se apostar</span><h3>{brl(t["betting_wealth_expected"])}</h3><p>É o valor que voltaria, em média, neste exemplo.</p><p><b>{outcome}</b> que o total colocado.</p></div>', unsafe_allow_html=True)
            with right:
                st.markdown(f'<div class="simple-card simple-save"><span>{savings}</span><h3>{brl(t["investment_final"])}</h3><p>O mesmo dinheiro é separado nas mesmas datas das apostas.</p><p>{savings_note}</p></div>', unsafe_allow_html=True)
            st.write("“Em média” não é uma promessa. É o resultado médio de muitas repetições deste exemplo. Uma pessoa pode terminar com mais ou com menos dinheiro conforme as chances escolhidas.")
            st.subheader("3. Entenda o risco")
            people = round(t["loss_probability"] * 100)
            label = "Nenhuma das 100" if t["loss_probability"] == 0 else ("Todas as 100" if t["loss_probability"] == 1 else (f"Cerca de {people} em cada 100" if 0 < people < 100 else ("Menos de 1 em cada 100" if people == 0 else "Mais de 99 em cada 100")))
            st.markdown(f"**{label} pessoas terminariam com menos dinheiro do que colocaram nas apostas**, se todas seguissem este mesmo exemplo.")
            dots = ''.join(f'<span class="risk-dot {"risk-loss" if i < people else ""}"></span>' for i in range(100))
            st.markdown(f'<div class="risk-grid" aria-hidden="true">{dots}</div>', unsafe_allow_html=True)
            st.write("Cada bolinha representa uma pessoa imaginária. As bolinhas escuras mostram quem terminaria perdendo dinheiro. As claras incluem quem ganhou ou ficou no zero a zero. Quantidades arredondadas.")
            st.info("Um resultado não muda a chance do próximo. As chances e a taxa escolhidas são hipóteses do exemplo; elas não mostram o que vai acontecer em um jogo ou investimento real.")
            with st.expander("Como fizemos essa comparação?"):
                st.write(f"Usamos as mesmas regras em todas as apostas: se acertar, recebe {config.odds:g} vezes o valor apostado, incluindo o dinheiro colocado; se errar, perde o valor daquela aposta. Um resultado não muda a chance do próximo.")
                st.write(f"A chance de acerto de {pct(config.p)} vem do modo Completo. Não é um dado sobre um jogo real. O resultado médio por R$ 100 apostados é {brl(t['roi'] * 100)}: positivo é ganho, negativo é perda e zero é empate.")
                st.write(f"O dinheiro recebido nas apostas fica separado e não é apostado de novo. Na comparação sem apostas: {savings_note} Não contamos inflação, taxas nem impostos. A quantidade total de apostas é arredondada para baixo quando necessário.")
            st.write("Quer explorar outras possibilidades? Escolha **Completo** no início da página. Seus valores e hipóteses acompanham você ao alternar os modos.")
