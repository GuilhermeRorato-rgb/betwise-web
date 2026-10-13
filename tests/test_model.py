from dataclasses import replace
import json
import math
import numpy as np
import pytest
from simulator.model import Parameters, theoretical, monte_carlo, investment_value, overround
from simulator.api import simulate
from simulator.scenarios import compare, default_scenarios, sensitivity
from simulator import charts


@pytest.mark.parametrize("p", [0., 1.])
def test_deterministic_extremes(p):
    c = Parameters(probability_mode="informada", probability=p)
    t, mc = theoretical(c), monte_carlo(c)
    expected = c.n * c.stake * (c.odds * p - 1)
    assert t["expected_profit"] == expected
    assert t["variance"] == 0
    assert np.all(mc["final"] == expected)
    assert t["loss_probability"] == 1-p
    assert t["profit_probability"] == p


def test_fair_and_margin():
    fair = Parameters(probability_mode="informada", probability=.5)
    assert theoretical(fair)["expected_profit"] == 0
    assert theoretical(Parameters())["roi"] == pytest.approx(-.05)
    assert theoretical(replace(fair, probability=.475))["roi"] == pytest.approx(-.05)


def test_variance_and_mean_statistical_agreement():
    c = Parameters(simulations=100000)
    t, mc = theoretical(c), monte_carlo(c)
    assert t["per_bet_variance"] == pytest.approx(c.stake**2*c.odds**2*c.p*(1-c.p))
    assert t["variance"] == pytest.approx(c.n*t["per_bet_variance"])
    assert abs(mc["summary"]["mean"]-t["expected_profit"]) < 5*t["std"]/math.sqrt(c.simulations)
    assert mc["summary"]["std"] == pytest.approx(t["std"], rel=.015)
    se = math.sqrt(t["loss_probability"]*(1-t["loss_probability"])/c.simulations)
    assert abs(mc["summary"]["loss_probability"]-t["loss_probability"]) < 5*se + 1/c.simulations


def test_reproducibility_and_random_seed_capture():
    a = monte_carlo(Parameters())
    b = monte_carlo(Parameters())
    np.testing.assert_array_equal(a["final"], b["final"])
    np.testing.assert_array_equal(a["timeline"]["sample"], b["timeline"]["sample"])
    c = monte_carlo(Parameters(seed=None))
    d = monte_carlo(Parameters(seed=c["seed_used"]))
    np.testing.assert_array_equal(c["final"], d["final"])


@pytest.mark.parametrize("rate", [0., .08, -.5, 1e-12])
def test_compounding_matches_direct_sum(rate):
    n, f, horizon, s = 24, 12, 2.04, 20
    exact = sum(s*(1+rate)**(horizon-i/f) for i in range(1, n+1))
    assert float(investment_value(s, n, f, rate, horizon)) == pytest.approx(exact, rel=1e-11)


def test_deposit_timing_and_single_bet():
    c = Parameters(frequency=1., frequency_unit="mês", duration=1., duration_unit="meses")
    t = theoretical(c)
    assert c.n == 1
    assert t["investment_final"] == pytest.approx(c.stake)
    assert t["betting_wealth_expected"] == pytest.approx(c.stake*c.odds*c.p)
    assert t["opportunity_cost"] == pytest.approx(t["investment_final"]-t["betting_wealth_expected"])


@pytest.mark.parametrize("updates", [
    {"probability": -.1}, {"probability": 1.1}, {"probability": float("nan")},
    {"odds": 1.}, {"stake": 0}, {"stake": float("inf")}, {"stake": True},
    {"frequency": 0}, {"frequency_unit": "hora"}, {"duration_unit": "séculos"},
    {"duration": 51}, {"annual_return": -1}, {"simulations": 0}, {"simulations": 1.5},
    {"simulations": True}, {"seed": -1}, {"seed": 1.5}, {"seed": True},
    {"disadvantage": 1.1}, {"probability_mode": "real"},
    {"duration": .01, "frequency": .01}, {"frequency": 1000, "frequency_unit": "dia", "duration": 50},
])
def test_invalid(updates):
    with pytest.raises(ValueError):
        Parameters(**updates)


def test_large_valid_input_finite_and_bounded_points():
    c = Parameters(frequency=1000, frequency_unit="mês", duration=50, annual_return=1, simulations=100)
    r = simulate(c.__dict__, True)
    assert len(r["timeline"]["bets"]) <= 241
    assert r["theoretical"]["n"] == 600000
    json.dumps(r, allow_nan=False)


def test_tie_classification_decimal_odds():
    # N=11, odd=1.1: K=10 produz empate matemático.
    c = Parameters(frequency=11, frequency_unit="mês", duration=1, duration_unit="meses", odds=1.1, simulations=100000)
    t, mc = theoretical(c), monte_carlo(c)
    assert t["tie_probability"] > 0
    assert sum(t[k] for k in ("loss_probability", "profit_probability", "tie_probability")) == pytest.approx(1)
    assert sum(mc["summary"][k] for k in ("loss_probability", "profit_probability", "tie_probability")) == pytest.approx(1)


def test_json_and_chart_coherence():
    r = simulate({}, True)
    json.dumps(r, allow_nan=False)
    t, m, series = r["theoretical"], r["simulation"], r["timeline"]
    assert series["mean"][-1] == m["mean"]
    assert series["p05"][-1] == m["p05"]
    assert series["investment"][-1] == pytest.approx(t["investment_final"])
    assert series["expected"][-1] == pytest.approx(t["expected_profit"])
    np.testing.assert_allclose(np.array(r["final_profit"])+t["budget"], r["final_betting_wealth"])
    np.testing.assert_allclose(np.array(series["sample"])[:, -1], r["final_profit"][:12])
    figures = [charts.evolution(r), charts.distribution(r), charts.observed(r), charts.investment(r),
               charts.sensitivity_plot(sensitivity(Parameters(), "stake"), "Valor"), charts.scenario_plot(compare(default_scenarios()))]
    for fig in figures:
        assert len(fig.data) > 0
        json.loads(fig.to_json())
    np.testing.assert_allclose(figures[2].data[1].y, series["expected"])
    np.testing.assert_allclose(figures[3].data[3].y, series["investment"])


def test_scenarios_and_sensitivity_semantics():
    rows = compare(default_scenarios())
    assert len(rows) == 3
    assert rows[2]["Orçamento"] > rows[1]["Orçamento"] > rows[0]["Orçamento"]
    assert all(r["ROI esperado (%)"] == pytest.approx(-5) for r in rows)
    values = sensitivity(Parameters(), "odds")
    assert all(r["Resultado esperado"] == pytest.approx(values[0]["Resultado esperado"]) for r in values)


def test_overround_and_api_errors():
    assert overround([2., 2.]) == 0
    assert overround([1.9, 1.9]) == pytest.approx(2/1.9-1)
    for values in [[2.], [0, 2], [float("nan"), 2]]:
        with pytest.raises(ValueError):
            overround(values)
    with pytest.raises(ValueError):
        simulate({"unknown": 2})
    with pytest.raises(ValueError):
        simulate([])
