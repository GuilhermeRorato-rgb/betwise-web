from dataclasses import asdict, replace
from .model import Parameters, theoretical


def default_scenarios():
    return [dict(nome="A · Menor frequência", valor=20., frequência=1., anos=1., odd=2., probabilidade=47.5, taxa=8.),
            dict(nome="B · Maior frequência", valor=20., frequência=5., anos=1., odd=2., probabilidade=47.5, taxa=8.),
            dict(nome="C · Maior horizonte", valor=20., frequência=5., anos=3., odd=2., probabilidade=47.5, taxa=8.)]


def compare(rows):
    results = []
    for row in rows:
        c = Parameters(stake=float(row["valor"]), frequency=float(row["frequência"]),
                       duration=float(row["anos"]), odds=float(row["odd"]), probability_mode="informada",
                       probability=float(row["probabilidade"]) / 100, annual_return=float(row["taxa"]) / 100)
        t = theoretical(c)
        results.append({"Cenário": str(row["nome"]), "Apostas": t["n"], "Orçamento": t["budget"],
                        "Resultado esperado": t["expected_profit"], "ROI esperado (%)": 100 * t["roi"],
                        "Prejuízo exato (%)": 100 * t["loss_probability"], "Investimento final": t["investment_final"],
                        "Patrimônio esperado das apostas": t["betting_wealth_expected"],
                        "Custo de oportunidade": t["opportunity_cost"]})
    return results


def sensitivity(c, parameter):
    current = c.p if parameter == "probability" else getattr(c, parameter)
    factors = [.5, .75, 1., 1.25, 1.5]
    result = []
    for factor in factors:
        value = current * factor
        updates = {parameter: value}
        if parameter == "probability":
            updates["probability_mode"] = "informada"
        try:
            cc = replace(c, **updates)
        except ValueError:
            continue
        t = theoretical(cc)
        result.append({"Parâmetro": value, "Resultado esperado": t["expected_profit"], "Orçamento": t["budget"]})
    return result
