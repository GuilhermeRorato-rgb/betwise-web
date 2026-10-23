"""Um único cenário para as duas apresentações do simulador."""
from simulator.model import Parameters

DEFAULTS = dict(stake=20., frequency=10., unit="mês", duration=12.,
                duration_unit="meses", odds=2., method="Margem hipotética",
                p=47.5, h=5., annual=0., sims=10000, fixed=True, seed=42)
PREFIX = "bw_sim_input_"


def restore(state, force=False):
    saved = state.setdefault("betwise_simulator_inputs", {})
    for name, default in DEFAULTS.items():
        key = PREFIX + name
        # Reatribuir também desassocia widgets ocultos da limpeza do Streamlit.
        state[key] = saved.get(key, default) if force else state.get(key, saved.get(key, default))


def save(state):
    saved = state.setdefault("betwise_simulator_inputs", {})
    for key in list(state):
        if key.startswith(PREFIX):
            saved[key] = state[key]


def configuration(state):
    v = {name: state[PREFIX + name] for name in DEFAULTS}
    return Parameters(stake=v['stake'], frequency=v['frequency'], frequency_unit=v['unit'],
                      duration=v['duration'], duration_unit=v['duration_unit'], odds=v['odds'],
                      probability_mode='margem' if v['method'] == 'Margem hipotética' else 'informada',
                      probability=v['p']/100, disadvantage=v['h']/100,
                      annual_return=v['annual']/100, simulations=v['sims'],
                      seed=v['seed'] if v['fixed'] else None)
