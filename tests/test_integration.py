"""Regressão da integração: o simulador não altera o estado nem a tela do agente."""
from pathlib import Path
import hashlib
import json
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


def open_app():
    at = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=60).run()
    assert not at.exception
    return at


def test_agent_preserved_and_navigation():
    at = open_app()
    assert len(at.chat_input) == 1
    initial_markdown = [m.value for m in at.markdown]
    at.button(key='nav_simulador').click().run()
    at.radio(key='bw_sim_mode').set_value('Completo').run()
    assert not at.exception
    assert len(at.metric) == 4
    assert len(at.chat_input) == 0
    navigation = at.radio(key='bw_sim_input_analysis_page')
    for page in navigation.options:
        navigation.set_value(page).run()
        assert not at.exception, page
    at.button(key='nav_assistente').click().run()
    assert not at.exception
    assert len(at.chat_input) == 1
    assert [m.value for m in at.markdown] == initial_markdown
    assert len(at.metric) == 0


def test_parameters_survive_agent_roundtrip_and_reset_does_not_touch_chat():
    at = open_app()
    at.session_state['messages'] = [{'id':'existing', 'role':'user', 'content':'Mensagem preservada'}]
    at.session_state['input_notice'] = 'Aviso do agente preservado'
    at.button(key='nav_simulador').click().run()
    at.radio(key='bw_sim_mode').set_value('Completo').run()
    at.number_input(key='bw_sim_input_stake').set_value(40.).run()
    at.radio(key='bw_sim_input_method').set_value('Probabilidade informada').run()
    at.slider(key='bw_sim_input_p').set_value(0.).run()
    assert at.metric[2].value == '100,00%'
    budget = at.metric[0].value
    at.button(key='nav_assistente').click().run()
    assert at.session_state['messages'][0]['content'] == 'Mensagem preservada'
    at.button(key='nav_simulador').click().run()
    at.radio(key='bw_sim_mode').set_value('Completo').run()
    assert at.number_input(key='bw_sim_input_stake').value == 40.
    assert at.slider(key='bw_sim_input_p').value == 0.
    assert at.metric[0].value == budget
    assert at.metric[2].value == '100,00%'
    next(b for b in at.button if b.label == 'Redefinir parâmetros').click().run()
    assert not at.exception
    assert at.number_input(key='bw_sim_input_stake').value == 20.
    assert at.session_state['input_notice'] == 'Aviso do agente preservado'
    assert at.session_state['messages'][0]['content'] == 'Mensagem preservada'


def test_invalid_input_does_not_break_agent():
    at = open_app()
    at.button(key='nav_simulador').click().run()
    at.radio(key='bw_sim_mode').set_value('Completo').run()
    at.selectbox(key='bw_sim_input_duration_unit').set_value('anos').run()
    at.number_input(key='bw_sim_input_duration').set_value(600.).run()
    assert len(at.error) == 1
    assert not at.exception
    at.button(key='nav_assistente').click().run()
    assert not at.exception
    assert len(at.chat_input) == 1


def test_original_files_and_agent_prefix_hashes():
    manifest = json.loads((ROOT / 'tests' / 'original_hashes.json').read_text())
    for path, expected in manifest['preserved_files'].items():
        data = (ROOT / path).read_bytes()
        # Git no Windows pode converter LF em CRLF nos arquivos de texto.
        candidates = [data] if path.endswith('.npz') else [data, data.replace(b'\r\n', b'\n')]
        assert expected in [hashlib.sha256(value).hexdigest() for value in candidates], path
    prefix = (ROOT / 'app.py').read_bytes().split(b'elif pagina == "Simulador":')[0]
    assert manifest['agent_prefix_sha256'] in [hashlib.sha256(value).hexdigest() for value in (prefix, prefix.replace(b'\r\n', b'\n'))]
