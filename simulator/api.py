"""Contrato JSON para ferramentas de assistentes; não depende de Streamlit."""
from dataclasses import asdict
import numpy as np
from .model import Parameters, theoretical, monte_carlo
from .education import explain


def _plain(x):
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, np.generic):
        return x.item()
    if isinstance(x, dict):
        return {k: _plain(v) for k, v in x.items()}
    return x


def simulate(parameters: dict, include_distribution: bool = False) -> dict:
    """Recebe chaves de Parameters. Erros de entrada geram ValueError.

    Valores monetários são BRL nominais; taxas são frações, não percentuais.
    Não faz chamadas a modelos externos nem armazena dados pessoais.
    """
    if not isinstance(parameters, dict):
        raise ValueError("Os parâmetros devem ser um objeto JSON.")
    try:
        c = Parameters(**parameters)
    except TypeError as exc:
        raise ValueError(f"Parâmetros desconhecidos ou incompatíveis: {exc}") from exc
    t = theoretical(c)
    mc = monte_carlo(c)
    result = {"schema_version": "1.0", "currency": "BRL", "parameters": asdict(c),
              "theoretical": t, "simulation": mc["summary"], "seed_used": mc["seed_used"],
              "timeline": mc["timeline"], "explanations": explain(t, mc["summary"]),
              "assumptions": ["Apostas binárias i.i.d.; probabilidade e odd constantes.",
                              "Aportes no fim de cada intervalo; ano de 365 dias, mês de 1/12 de ano.",
                              "Pagamentos brutos das apostas preservados sem rendimento.",
                              "Valores nominais, sem impostos, custos ou inflação; sem previsão de resultados reais."]}
    if include_distribution:
        result["final_profit"] = mc["final"]
        result["final_betting_wealth"] = mc["final"] + t["budget"]
    return _plain(result)
