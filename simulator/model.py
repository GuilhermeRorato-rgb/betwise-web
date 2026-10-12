"""Modelo i.i.d. de orçamento recorrente, sem banca inicial."""
from dataclasses import dataclass, asdict
from decimal import Decimal, ROUND_FLOOR, ROUND_CEILING
import math
import numbers
import numpy as np
from scipy.stats import binom

PER_YEAR = {"dia": 365.0, "semana": 365.0 / 7.0, "mês": 12.0}


@dataclass(frozen=True)
class Parameters:
    stake: float = 20.0
    frequency: float = 5.0
    frequency_unit: str = "semana"
    duration: float = 3.0
    duration_unit: str = "anos"
    odds: float = 2.0
    probability_mode: str = "margem"
    probability: float = 0.475
    disadvantage: float = 0.05
    annual_return: float = 0.08
    simulations: int = 10000
    seed: int | None = 42

    def __post_init__(self):
        bounds = {"stake": (0.01, 1e6), "frequency": (0.01, 1000),
                  "duration": (0.01, 600), "odds": (1.000001, 1000),
                  "probability": (0, 1), "disadvantage": (0, 1),
                  "annual_return": (-0.99, 1)}
        for name, (low, high) in bounds.items():
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, numbers.Real) or not math.isfinite(value) or not low <= value <= high:
                raise ValueError(f"Parâmetro {name} deve estar entre {low} e {high} e ser finito.")
        if self.frequency_unit not in PER_YEAR or self.duration_unit not in ("anos", "meses"):
            raise ValueError("Unidade de frequência ou duração inválida.")
        if self.probability_mode not in ("margem", "informada"):
            raise ValueError("Método de probabilidade inválido.")
        if type(self.simulations) is not int or not 100 <= self.simulations <= 100000:
            raise ValueError("Utilize de 100 a 100.000 simulações inteiras.")
        if self.seed is not None and (type(self.seed) is not int or not 0 <= self.seed <= 2**32 - 1):
            raise ValueError("A semente deve ser um inteiro entre 0 e 4.294.967.295.")
        if self.years > 50 or not 1 <= self.n <= 1000000:
            raise ValueError("Escolha um horizonte de até 50 anos e entre 1 e 1.000.000 de apostas.")

    @property
    def years(self):
        return self.duration / 12 if self.duration_unit == "meses" else self.duration

    @property
    def rate(self):
        return self.frequency * PER_YEAR[self.frequency_unit]

    @property
    def n(self):
        return math.floor(self.years * self.rate + 1e-10)

    @property
    def p(self):
        return (1 - self.disadvantage) / self.odds if self.probability_mode == "margem" else self.probability


def investment_value(stake, n, rate, annual_return, at_year):
    """Aportes s em i/rate, i=1..n; avaliação at_year >= n/rate."""
    n = np.asarray(n, dtype=float)
    a = math.log1p(annual_return) / rate
    if abs(a) < 1e-14:
        # A soma direta evita cancelamento perto da taxa zero.
        series = n if a == 0 else n + a * n * (n - 1) / 2
    else:
        series = np.expm1(n * a) / math.expm1(a)
    return stake * series * np.exp(math.log1p(annual_return) * (np.asarray(at_year) - n / rate))


def thresholds(n, odds):
    """Fronteiras estritas e empate, sem erro de ponto flutuante na odd decimal."""
    cutoff = Decimal(n) / Decimal(str(odds))
    floor = int(cutoff.to_integral_value(rounding=ROUND_FLOOR))
    ceil = int(cutoff.to_integral_value(rounding=ROUND_CEILING))
    return ceil - 1, floor, floor if cutoff == floor else None


def theoretical(c):
    roi = c.p * c.odds - 1
    per_variance = c.stake**2 * c.odds**2 * c.p * (1 - c.p)
    low, high, tie = thresholds(c.n, c.odds)
    expected = c.n * c.stake * roi
    budget = c.n * c.stake
    invested = float(investment_value(c.stake, c.n, c.rate, c.annual_return, c.years))
    return {"n": c.n, "years": c.years, "probability": c.p, "implied_probability": 1 / c.odds,
            "roi": roi, "per_bet_expected": c.stake * roi, "per_bet_variance": per_variance,
            "expected_profit": expected, "variance": c.n * per_variance,
            "std": math.sqrt(c.n * per_variance), "budget": budget,
            "loss_probability": float(binom.cdf(low, c.n, c.p)),
            "profit_probability": float(binom.sf(high, c.n, c.p)),
            "tie_probability": float(binom.pmf(tie, c.n, c.p)) if tie is not None else 0.,
            "p05": float(c.stake * (c.odds * binom.ppf(.05, c.n, c.p) - c.n)),
            "p95": float(c.stake * (c.odds * binom.ppf(.95, c.n, c.p) - c.n)),
            "investment_final": invested, "investment_profit": invested - budget,
            "betting_wealth_expected": budget + expected,
            "opportunity_cost": invested - (budget + expected)}


def monte_carlo(c):
    actual_seed = c.seed if c.seed is not None else int(np.random.SeedSequence().generate_state(1)[0])
    rng = np.random.default_rng(actual_seed)
    steps = np.unique(np.linspace(0, c.n, min(c.n, 240) + 1, dtype=np.int64))
    counts = np.zeros(c.simulations, dtype=np.int64)
    sample = np.zeros((12, len(steps)))
    means, p05, p95 = [0.], [0.], [0.]
    for j, delta in enumerate(np.diff(steps), 1):
        # Binomial(delta,p) é exatamente a soma de delta Bernoulli(p).
        counts += rng.binomial(int(delta), c.p, size=c.simulations)
        profits = c.stake * (c.odds * counts - int(steps[j]))
        means.append(float(profits.mean()))
        q = np.quantile(profits, [.05, .95])
        p05.append(float(q[0])); p95.append(float(q[1]))
        sample[:, j] = profits[:12]
    final = c.stake * (c.odds * counts - c.n)
    low, high, tie = thresholds(c.n, c.odds)
    times = steps / c.rate
    times[-1] = c.years  # Última avaliação inclui eventual fração sem novas apostas.
    summary = {"mean": float(final.mean()), "median": float(np.median(final)),
               "std": float(final.std(ddof=1)), "p05": p05[-1], "p95": p95[-1],
               "loss_probability": float(np.mean(counts <= low)),
               "profit_probability": float(np.mean(counts > high)),
               "tie_probability": float(np.mean(counts == tie)) if tie is not None else 0.,
               "mean_standard_error": float(final.std(ddof=1) / math.sqrt(c.simulations))}
    return {"seed_used": actual_seed, "summary": summary, "final": final,
            "timeline": {"bets": steps, "years": times, "mean": np.array(means),
                         "p05": np.array(p05), "p95": np.array(p95), "sample": sample,
                         "expected": steps * c.stake * (c.p * c.odds - 1),
                         "budget": steps * c.stake,
                         "investment": investment_value(c.stake, steps, c.rate, c.annual_return, times)}}


def overround(odds):
    if len(odds) < 2 or any(not math.isfinite(o) or o <= 1 for o in odds):
        raise ValueError("Informe pelo menos duas odds finitas maiores que 1.")
    return sum(1 / o for o in odds) - 1
