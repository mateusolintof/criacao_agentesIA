# Guia: Teste de Prompts

## Visão Geral

Testes sistemáticos de prompts garantem qualidade e consistência. Este guia ensina como criar datasets de teste, avaliar prompts e iterar para melhorar resultados.

## Metodologia de Teste

### 1. Criar Dataset de Teste

```python
# tests/data/prompt_test_cases.py
TEST_CASES = [
    {
        "id": "greeting_01",
        "category": "greeting",
        "input": "Olá",
        "expected_elements": ["saudação", "oferecer ajuda"],
        "should_not_contain": ["preço", "desconto"],
        "max_length": 200
    },
    {
        "id": "objection_price_01",
        "category": "objection",
        "input": "Está muito caro",
        "expected_elements": ["entender preocupação", "pergunta", "valor"],
        "should_not_contain": ["desculpa", "é barato"],
    },
    # ... mais casos
]
```

### 2. Executar Testes

```python
def test_prompt(prompt: str, test_case: Dict) -> Dict:
    """Testa prompt contra um caso."""
    response = generate_response(prompt, test_case["input"])

    results = {
        "passed": True,
        "scores": {},
        "failures": []
    }

    # Verificar elementos esperados
    for element in test_case.get("expected_elements", []):
        if element.lower() not in response.lower():
            results["passed"] = False
            results["failures"].append(f"Missing: {element}")

    # Verificar elementos proibidos
    for element in test_case.get("should_not_contain", []):
        if element.lower() in response.lower():
            results["passed"] = False
            results["failures"].append(f"Contains forbidden: {element}")

    # Verificar comprimento
    if "max_length" in test_case:
        if len(response) > test_case["max_length"]:
            results["passed"] = False
            results["failures"].append("Too long")

    return results
```

### 3. Métricas de Avaliação

```python
class PromptEvaluator:
    """Avalia qualidade de prompts."""

    def evaluate(self, prompt: str, test_cases: List[Dict]) -> Dict:
        """Executa avaliação completa."""
        results = {
            "total_tests": len(test_cases),
            "passed": 0,
            "failed": 0,
            "by_category": {},
            "metrics": {}
        }

        for test_case in test_cases:
            result = test_prompt(prompt, test_case)

            if result["passed"]:
                results["passed"] += 1
            else:
                results["failed"] += 1

            # Agrupar por categoria
            category = test_case.get("category", "other")
            if category not in results["by_category"]:
                results["by_category"][category] = {"passed": 0, "failed": 0}

            if result["passed"]:
                results["by_category"][category]["passed"] += 1
            else:
                results["by_category"][category]["failed"] += 1

        # Calcular métricas
        results["metrics"]["pass_rate"] = results["passed"] / results["total_tests"]

        return results
```

## Testes Automatizados

```python
# tests/prompts/test_sales_prompt.py
import pytest
from prompts.sales_agent_prompts import SYSTEM_PROMPT_V1, SYSTEM_PROMPT_V2

@pytest.mark.parametrize("test_case", load_test_cases("sales_agent"))
def test_sales_prompt_v1(test_case):
    """Testa prompt v1 contra todos casos."""
    result = test_prompt(SYSTEM_PROMPT_V1, test_case)
    assert result["passed"], f"Failed: {result['failures']}"


def test_prompt_version_comparison():
    """Compara versões de prompts."""
    test_cases = load_test_cases("sales_agent")

    v1_results = evaluate_prompt(SYSTEM_PROMPT_V1, test_cases)
    v2_results = evaluate_prompt(SYSTEM_PROMPT_V2, test_cases)

    # v2 deve ser melhor ou igual a v1
    assert v2_results["metrics"]["pass_rate"] >= v1_results["metrics"]["pass_rate"]
```

## Avaliação por LLM (LLM-as-Judge)

```python
def llm_evaluate_response(
    prompt: str,
    user_input: str,
    response: str,
    criteria: List[str]
) -> Dict:
    """
    Usa LLM para avaliar qualidade da resposta.

    Args:
        prompt: Prompt sendo testado
        user_input: Input do usuário
        response: Resposta gerada
        criteria: Critérios de avaliação

    Returns:
        Scores por critério
    """
    eval_prompt = f"""
    Avalie a seguinte resposta do agente:

    USER INPUT: {user_input}
    AGENT RESPONSE: {response}

    Critérios de avaliação (score 1-5):
    {', '.join(criteria)}

    Para cada critério, forneça:
    - Score (1-5)
    - Justificativa

    Retorne em JSON format.
    """

    evaluation = llm.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": eval_prompt}],
        response_format={"type": "json_object"}
    )

    return json.loads(evaluation.choices[0].message.content)


# Uso
scores = llm_evaluate_response(
    prompt=SYSTEM_PROMPT,
    user_input="Está muito caro",
    response=agent_response,
    criteria=["relevância", "empatia", "profissionalismo", "utilidade"]
)
```

## A/B Testing de Prompts

```python
class PromptABTest:
    """Framework para A/B test de prompts."""

    def __init__(self, prompt_a: str, prompt_b: str):
        self.prompt_a = prompt_a
        self.prompt_b = prompt_b
        self.results = {"a": [], "b": []}

    def run_test(self, test_cases: List[Dict], sample_size: int = 100):
        """Executa A/B test."""
        import random

        for test_case in random.sample(test_cases, sample_size):
            # Randomizar qual prompt usar
            use_a = random.choice([True, False])

            if use_a:
                result = test_prompt(self.prompt_a, test_case)
                self.results["a"].append(result["passed"])
            else:
                result = test_prompt(self.prompt_b, test_case)
                self.results["b"].append(result["passed"])

    def get_winner(self) -> Dict:
        """Determina vencedor estatisticamente."""
        from scipy import stats

        # Test estatístico (chi-square)
        contingency = [
            [sum(self.results["a"]), len(self.results["a"]) - sum(self.results["a"])],
            [sum(self.results["b"]), len(self.results["b"]) - sum(self.results["b"])]
        ]

        chi2, p_value = stats.chi2_contingency(contingency)[:2]

        pass_rate_a = sum(self.results["a"]) / len(self.results["a"])
        pass_rate_b = sum(self.results["b"]) / len(self.results["b"])

        winner = "a" if pass_rate_a > pass_rate_b else "b"

        return {
            "winner": winner if p_value < 0.05 else "inconclusive",
            "pass_rate_a": pass_rate_a,
            "pass_rate_b": pass_rate_b,
            "p_value": p_value,
            "statistically_significant": p_value < 0.05
        }
```

## Benchmarks

```python
# Criar benchmark padrão
BENCHMARK_SUITE = {
    "greeting": [
        "Olá",
        "Oi, tudo bem?",
        "Bom dia"
    ],
    "product_inquiry": [
        "Quais produtos vocês têm?",
        "Me fala sobre o CRM",
        "Quanto custa?"
    ],
    "objection": [
        "Está caro",
        "Não tenho orçamento",
        "Preciso pensar"
    ],
    # ... mais categorias
}

def run_benchmark(prompt: str) -> Dict:
    """Executa benchmark padrão."""
    results = {}

    for category, test_inputs in BENCHMARK_SUITE.items():
        category_results = []

        for test_input in test_inputs:
            response = generate_response(prompt, test_input)
            score = evaluate_response(response, category)
            category_results.append(score)

        results[category] = {
            "avg_score": np.mean(category_results),
            "min_score": min(category_results),
            "max_score": max(category_results)
        }

    return results
```

## Continuous Testing

```python
# CI/CD para prompts
# .github/workflows/test-prompts.yml
name: Prompt Tests

on:
  pull_request:
    paths:
      - 'prompts/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Test prompts
        run: |
          pytest tests/prompts/ -v
          python scripts/evaluate_all_prompts.py

      - name: Compare with baseline
        run: |
          python scripts/compare_prompts.py \
            --baseline prompts/production/ \
            --new prompts/staging/

      - name: Comment results
        uses: actions/github-script@v5
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              body: 'Prompt test results: ...'
            })
```

## Próximos Passos

- [Engenharia de Prompts](engenharia-prompts.md)
- [Testes de Conversação](testes-conversacao.md)

## Referências

- [Prompt Testing Best Practices](https://www.promptingguide.ai/introduction/testing)
