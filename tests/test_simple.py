from streamlit.testing.v1 import AppTest
from pathlib import Path
import pytest
from simulator.simple import simple_result

ROOT = Path(__file__).resolve().parents[1]


def test_simple_money_and_risk():
    t = simple_result(20., 10, 12)
    assert t['n'] == 120
    assert t['budget'] == 2400
    assert t['expected_profit'] == pytest.approx(-120)
    assert t['betting_wealth_expected'] == pytest.approx(2280)
    assert t['investment_final'] == 2400
    assert 0 < t['loss_probability'] < 1
    for inputs in [(1., 1, 1), (1000000., 1000, 24)]:
        assert simple_result(*inputs)['n'] >= 1


def test_shared_scenario_and_dynamic_explanations():
    at = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=60).run()
    at.button(key='nav_simulador').click().run()
    at.number_input(key='bw_sim_input_stake').set_value(35.).run()
    at.number_input(key='bw_sim_input_duration').set_value(3.).run()
    at.radio(key='bw_sim_mode').set_value('Completo').run()
    assert at.number_input(key='bw_sim_input_stake').value == 35.
    at.number_input(key='bw_sim_input_odds').set_value(3.).run()
    at.radio(key='bw_sim_input_method').set_value('Probabilidade informada').run()
    at.slider(key='bw_sim_input_p').set_value(100.).run()
    at.number_input(key='bw_sim_input_annual').set_value(-10.).run()
    at.radio(key='bw_sim_mode').set_value('Simples').run()
    text = ' '.join(m.value for m in at.markdown)
    assert '2.100,00 a mais' in text
    assert '100,00%' in text
    assert '-10,00%' in text
    assert 'Nenhuma das 100' in text
    assert not at.exception
    at.number_input(key='bw_sim_input_stake').set_value(40.).run()
    at.button(key='nav_assistente').click().run()
    at.button(key='nav_simulador').click().run()
    assert at.number_input(key='bw_sim_input_stake').value == 40.
    at.radio(key='bw_sim_mode').set_value('Completo').run()
    assert at.number_input(key='bw_sim_input_stake').value == 40.
    assert at.slider(key='bw_sim_input_p').value == 100.
    at.number_input(key='bw_sim_input_odds').set_value(2.).run()
    at.slider(key='bw_sim_input_p').set_value(50.).run()
    at.radio(key='bw_sim_mode').set_value('Simples').run()
    assert any('O mesmo valor' in m.value for m in at.markdown)
    at.radio(key='bw_sim_mode').set_value('Completo').run()
    at.slider(key='bw_sim_input_p').set_value(0.).run()
    at.radio(key='bw_sim_mode').set_value('Simples').run()
    assert any('Todas as 100' in m.value for m in at.markdown)
    at.radio(key='bw_sim_mode').set_value('Completo').run()
    at.radio(key='bw_sim_input_method').set_value('Margem hipotética').run()
    at.slider(key='bw_sim_input_h').set_value(20.).run()
    at.radio(key='bw_sim_mode').set_value('Simples').run()
    assert any('40,00%' in m.value for m in at.markdown)
    assert any('240,00 a menos' in m.value for m in at.markdown)
    assert not at.exception
