def brl(v):
    return "R$ " + f"{v:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def pct(v):
    return f"{v * 100:.2f}%".replace(".", ",")


def explain(t, m):
    sign = "negativo" if t["roi"] < -1e-12 else "positivo" if t["roi"] > 1e-12 else "zero"
    return [
        f"Com estas hipóteses, o retorno esperado é {sign}: {pct(t['roi'])} por real apostado. Isso não determina o resultado de uma pessoa.",
        f"O orçamento acumulado é {brl(t['budget'])}, distribuído por {t['n']:,} apostas. Dobrar a frequência aproximadamente dobra esse orçamento e o resultado esperado; o arredondamento de apostas pode causar pequena diferença.",
        f"Nos sorteios, os percentis 5 e 95 ficaram em {brl(m['p05'])} e {brl(m['p95'])}. Resultados fora dessa faixa continuam possíveis; ela não é um intervalo de confiança da média.",
        f"A diferença esperada entre investir e preservar os pagamentos das apostas é {brl(t['opportunity_cost'])}. Um valor negativo favorece as apostas apenas sob as premissas informadas, sem comprovar uma vantagem real.",
        "Uma sequência de derrotas não aumenta a chance da próxima vitória neste modelo independente. Aumentar os gastos para recuperar perdas aumenta os recursos expostos.",
    ]


CONCEPTS = {
    "Valor esperado": "É a média ponderada dos resultados possíveis. Não é uma promessa nem o resultado mais provável de uma pessoa.",
    "Probabilidade e odds": "Probabilidade é a chance assumida de vencer. A odd inclui a devolução da aposta: R$ 20 na odd 2 devolvem R$ 40 se vencer, com lucro de R$ 20. O inverso da odd é a chance de equilíbrio, não a chance real.",
    "Desvantagem e overround": "A desvantagem h é uma hipótese sobre o retorno esperado. O overround soma os inversos das odds de um mercado completo e subtrai 1. Ele não identifica sozinho a perda esperada efetiva.",
    "Lei dos Grandes Números": "Sob independência e parâmetros constantes, a média por aposta tende ao valor esperado. Isso não garante recuperação: o desvio-padrão do lucro total cresce com a raiz do número de apostas, enquanto a dispersão por aposta diminui.",
    "Variância e risco": "Medem a dispersão dos resultados. Dois percursos com as mesmas hipóteses podem terminar muito longe um do outro. A probabilidade de prejuízo não mede o tamanho da perda.",
    "Monte Carlo": "Sorteios repetidos geram futuros hipotéticos. Mais simulações reduzem o erro numérico das estimativas, mas não corrigem hipóteses erradas.",
    "Custo de oportunidade": "É a diferença entre o patrimônio da alternativa de investir e o patrimônio das apostas, usando os mesmos aportes nas mesmas datas.",
}

BIASES = {
    "Falácia do jogador": "Acreditar que uma vitória está mais próxima porque ocorreram derrotas. Em eventos independentes, a probabilidade permanece igual.",
    "Excesso de confiança": "Tratar uma avaliação pessoal de probabilidade como se fosse uma medida precisa. Aqui ela continua sendo uma hipótese.",
    "Ilusão de controle": "Atribuir a rituais ou escolhas pessoais um controle sobre resultados aleatórios que eles não demonstram ter.",
    "Aversão à perda": "Dar peso maior a uma perda do que a um ganho equivalente pode alterar decisões sobre continuar gastando.",
    "Perseguição de perdas": "Aumentar os gastos para recuperar valores passados compromete mais recursos e não altera automaticamente a chance de vitória.",
    "Ilusão da mão quente": "Interpretar uma sequência de vitórias como prova de que a próxima chance aumentou. Isso não ocorre no modelo independente.",
    "Contabilidade mental": "Tratar pagamentos recebidos como dinheiro separado pode esconder que esses valores também fazem parte do patrimônio.",
    "Viés do presente": "Dar mais peso à experiência imediata do que ao efeito acumulado de pequenos gastos ao longo do tempo.",
}
