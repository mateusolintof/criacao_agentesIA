# Formulário de Feedback - Agente de IA

**Versão:** 1.0
**Data:** [DATA]
**Tipo:** Pós-conversa

---

## Instruções de Implementação

Este template deve ser apresentado ao usuário **ao final de uma conversa** com o agente de IA. Pode ser implementado como:
- Modal/popup no chat
- Email de follow-up
- Link enviado pelo próprio agente
- Integração com plataforma de feedback (Typeform, Google Forms, etc)

---

## Perguntas do Formulário

### 1. Satisfação Geral (CSAT)

**Pergunta:**
> Como você avaliaria sua experiência com nosso assistente virtual?

**Formato:** Escala de estrelas (1-5)

⭐ ⭐⭐ ⭐⭐⭐ ⭐⭐⭐⭐ ⭐⭐⭐⭐⭐

**Labels:**
- 1 estrela: Muito insatisfeito
- 2 estrelas: Insatisfeito
- 3 estrelas: Neutro
- 4 estrelas: Satisfeito
- 5 estrelas: Muito satisfeito

**Métrica:** CSAT Score (Customer Satisfaction Score)
**Meta:** >= 4.0/5.0

---

### 2. Resolução do Problema

**Pergunta:**
> O assistente conseguiu resolver sua dúvida ou ajudar com o que você precisava?

**Formato:** Múltipla escolha (única resposta)

- [ ] Sim, completamente
- [ ] Sim, parcialmente
- [ ] Não conseguiu resolver
- [ ] Não tinha uma dúvida específica

**Lógica condicional:**
- Se "Sim, completamente" → Pular para pergunta 4
- Se "Sim, parcialmente" → Mostrar pergunta 3
- Se "Não conseguiu resolver" → Mostrar pergunta 3

---

### 3. O que faltou? (Condicional)

**Mostrar apenas se:** Resposta anterior foi "Parcialmente" ou "Não conseguiu"

**Pergunta:**
> O que o assistente poderia ter feito melhor?

**Formato:** Caixas de seleção (múltiplas respostas)

- [ ] Não entendeu o que eu estava pedindo
- [ ] Informações incompletas ou imprecisas
- [ ] Resposta muito genérica
- [ ] Não tinha a informação que eu precisava
- [ ] Demorou muito para responder
- [ ] Outro (campo de texto)

---

### 4. Qualidade das Respostas

**Pergunta:**
> As respostas do assistente foram claras e úteis?

**Formato:** Escala Likert (1-5)

1 - Discordo totalmente | 2 - Discordo | 3 - Neutro | 4 - Concordo | 5 - Concordo totalmente

**Dimensões:**
- **Clareza:** As respostas foram fáceis de entender
- **Relevância:** As informações foram relevantes para minha necessidade
- **Completude:** Recebi todas as informações que precisava
- **Velocidade:** O assistente respondeu em tempo adequado

---

### 5. Naturalidade da Conversa

**Pergunta:**
> A conversa com o assistente pareceu natural?

**Formato:** Múltipla escolha

- [ ] Sim, pareceu muito natural
- [ ] Razoável, mas percebi que era um bot
- [ ] Não, pareceu muito robótico
- [ ] Indiferente

---

### 6. Comparação com Expectativa

**Pergunta:**
> Como o assistente se comparou ao que você esperava?

**Formato:** Múltipla escolha

- [ ] Superou minhas expectativas
- [ ] Atendeu minhas expectativas
- [ ] Ficou abaixo das minhas expectativas

---

### 7. Confiança nas Informações

**Pergunta:**
> Você confia nas informações fornecidas pelo assistente?

**Formato:** Escala Likert (1-5)

1 - Não confio | 2 - Confio pouco | 3 - Neutro | 4 - Confio | 5 - Confio completamente

---

### 8. Preferência de Atendimento (Opcional)

**Pergunta:**
> Para esse tipo de atendimento, você prefere:

**Formato:** Múltipla escolha

- [ ] Assistente virtual (mais rápido, disponível 24/7)
- [ ] Atendimento humano (mais personalizado)
- [ ] Tanto faz, desde que resolva
- [ ] Depende da complexidade da dúvida

---

### 9. Intenção de Uso Futuro

**Pergunta:**
> Você usaria o assistente novamente?

**Formato:** Múltipla escolha

- [ ] Sim, com certeza
- [ ] Sim, provavelmente
- [ ] Talvez
- [ ] Não

---

### 10. NPS (Net Promoter Score)

**Pergunta:**
> Em uma escala de 0 a 10, o quanto você recomendaria nosso assistente para um amigo ou colega?

**Formato:** Escala numérica (0-10)

[0] [1] [2] [3] [4] [5] [6] [7] [8] [9] [10]

Muito improvável ← → Muito provável

**Categorias:**
- 0-6: Detratores
- 7-8: Neutros
- 9-10: Promotores

**Métrica:** NPS = % Promotores - % Detratores
**Meta:** >= 50

---

### 11. Feedback Aberto

**Pergunta:**
> Tem algum comentário adicional ou sugestão de melhoria?

**Formato:** Campo de texto aberto (opcional)

Placeholder: "Compartilhe suas ideias, sugestões ou qualquer feedback adicional..."

**Max caracteres:** 500

---

### 12. Informações Demográficas (Opcional)

**Para segmentação e análise:**

**Como você nos conheceu?**
- [ ] Google/busca
- [ ] Indicação
- [ ] Redes sociais
- [ ] Email marketing
- [ ] Outro

**Qual seu perfil?**
- [ ] Potencial cliente (pesquisando)
- [ ] Cliente atual
- [ ] Apenas curiosidade
- [ ] Outro

---

## Mensagem de Agradecimento

Após envio do formulário:

```
Obrigado pelo seu feedback! 🙏

Sua opinião é muito importante para melhorarmos continuamente nosso atendimento.

[Se CSAT >= 4]:
Ficamos felizes que você teve uma boa experiência! Se precisar de algo mais, estamos por aqui.

[Se CSAT < 3]:
Lamentamos que a experiência não tenha sido ideal. Vamos usar seu feedback para melhorar. Se quiser conversar com nossa equipe, clique aqui: [LINK]

---
Quer falar com um humano? [BOTÃO: Falar com equipe]
```

---

## Análise e Métricas

### KPIs Principais

1. **CSAT (Customer Satisfaction Score)**
   - Fórmula: Média das avaliações (pergunta 1)
   - Meta: >= 4.0/5.0
   - Frequência: Diária

2. **Taxa de Resolução**
   - Fórmula: % de "Sim, completamente" (pergunta 2)
   - Meta: >= 70%
   - Frequência: Diária

3. **NPS (Net Promoter Score)**
   - Fórmula: % Promotores (9-10) - % Detratores (0-6)
   - Meta: >= 50
   - Frequência: Mensal

4. **Taxa de Resposta do Formulário**
   - Fórmula: (Formulários respondidos / Total de conversas) * 100
   - Meta: >= 30%
   - Frequência: Semanal

### Segmentações Importantes

Analisar métricas por:
- **Canal:** Web chat, WhatsApp, Email
- **Tipo de dúvida:** Produtos, Preços, Suporte, Vendas
- **Horário:** Comercial vs Fora do horário
- **Duração da conversa:** < 2min, 2-5min, 5-10min, > 10min
- **Perfil do usuário:** Prospect vs Cliente

### Alertas

Configurar alertas para:
- CSAT < 3.5 por 3 dias consecutivos
- Taxa de resolução < 60% por 1 semana
- NPS < 30
- Aumento de 20%+ em feedback negativo (semana vs semana anterior)

---

## Ações Baseadas em Feedback

### CSAT 1-2 (Muito insatisfeito/Insatisfeito)
**Ação imediata:**
- Notificar equipe de sucesso do cliente
- Entrar em contato em até 24h
- Investigar conversa completa
- Identificar padrão (se múltiplos casos)

### CSAT 3 (Neutro)
**Ação:**
- Revisar conversa para identificar gap
- Analisar em agregado para patterns
- Testar melhorias

### CSAT 4-5 (Satisfeito/Muito satisfeito)
**Ação:**
- Se for lead qualificado, priorizar follow-up
- Considerar solicitar review público (se adequado)
- Usar como caso de sucesso

### NPS Detratores (0-6)
**Ação:**
- Follow-up personalizado
- Investigar causa raiz
- Oferecer compensação se adequado

### NPS Promotores (9-10)
**Ação:**
- Solicitar review/testemunhal
- Programa de indicação
- Caso de sucesso

---

## Versões do Formulário

### Versão Curta (3 perguntas - para mobile)
1. CSAT (pergunta 1)
2. Resolução (pergunta 2)
3. Feedback aberto (pergunta 11)

**Quando usar:** WhatsApp, SMS, contextos mobile

### Versão Completa (12 perguntas)
Todas as perguntas acima

**Quando usar:** Web, email, após interações importantes

### Versão Follow-up (1 semana depois)
1. Você precisou entrar em contato novamente?
2. O assistente ajudou a resolver seu problema a longo prazo?
3. NPS

**Quando usar:** Para medir impacto a longo prazo

---

## Implementação Técnica

### Tracking

Cada resposta deve incluir:
```json
{
  "response_id": "uuid",
  "conversation_id": "uuid",
  "user_id": "string",
  "agent_id": "string",
  "timestamp": "ISO-8601",
  "csat_score": 1-5,
  "resolution": "complete|partial|no",
  "nps_score": 0-10,
  "feedback_text": "string",
  "metadata": {
    "channel": "web|whatsapp|email",
    "conversation_length": number,
    "messages_count": number,
    "intent": "sales|support|product_info"
  }
}
```

### Integração

- Armazenar em banco de dados
- Enviar para ferramenta de analytics (Mixpanel, Amplitude)
- Sincronizar com CRM (Salesforce, HubSpot)
- Dashboard em tempo real (Grafana, Metabase)

---

## Testes A/B

**Experimentos sugeridos:**

1. **Timing:** Final da conversa vs 5min depois
2. **Incentivo:** Com vs sem incentivo (desconto, brinde)
3. **Formato:** Modal vs Email vs WhatsApp message
4. **Tamanho:** Versão curta vs completa
5. **Framing:** "Nos ajude a melhorar" vs "Conte sua experiência"

**Métrica de sucesso:** Taxa de resposta

---

## Privacidade e Compliance

- [ ] Adicionar aviso de privacidade
- [ ] Opção de opt-out de comunicações futuras
- [ ] Não coletar dados sensíveis
- [ ] Respeitar LGPD/GDPR
- [ ] Permitir exclusão de dados (right to deletion)

---

## Revisão e Iteração

**Frequência de revisão do formulário:** Trimestral

**Checklist de revisão:**
- [ ] Perguntas ainda são relevantes?
- [ ] Taxa de resposta está adequada?
- [ ] Dados coletados estão sendo usados?
- [ ] Há novas perguntas importantes a adicionar?
- [ ] Alguma pergunta pode ser removida?

---

**Última atualização:** [DATA]
**Próxima revisão:** [DATA]
**Owner:** [NOME/EQUIPE]
