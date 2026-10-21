# Plano de início

## Responsabilidades sugeridas (substituir pelos nomes da equipe)

| Frente | Responsável sugerido | Até 30/10 |
|---|---|---|
| Dados + rede | Integrante 1 | Acesso SHOT, inspeção dos rótulos, splits e primeiro experimento |
| Métricas + detector | Integrante 2 | Extrator OpenCV padronizado, duração, unidades e saída estruturada |
| Evidências + RAG | Integrante 3 | Poucos artigos conferidos, metadados, recuperação e citações |
| Agente + API | Integrante 4 | Agente chama ferramentas reais e retorna relatório |
| Interface + MLOps | Integrante 5 | Upload simples, registro das execuções e demonstração |

MLOps e revisão são compartilhados. A rede não bloqueia o agente.

## Backlog imediato

- [ ] DADOS-01: baixar uma parte do SHOT; identificar vídeos e respectivas anotações; confirmar convenções de frames e tipos de transição.
- [ ] DADOS-02: inventariar arquivos com hashes; preservar teste oficial e criar validação apenas no treino; manter todo vídeo de origem no mesmo conjunto.
- [ ] MET-01: integrar o extrator já estudado; documentar resolução, FPS, intervalo temporal e unidades; converter pixels vibrantes em proporção.
- [ ] RAG-01: preparar fontes com título, DOI/URL, página, população, tarefa estudada e limitações; não presumir permissão para publicar PDFs.
- [ ] AG-01: implementar ferramentas de extração, comparação e busca; relatório com métricas e evidências rastreáveis.
- [ ] MLOPS-01: registrar primeira execução e reproduzi-la a partir de configuração e versão do código.
- [ ] UI-01: upload, andamento, resultado e erros claros; conectar ao fluxo real.
- [ ] REDE-01: baseline de CNN própria para pares de frames; comparação com anotações; parâmetros ajustados só na validação.

## Agenda do protótipo

| Data | Resultado |
|---|---|
| 21–22/10 | Contrato, ambiente, tarefas e dados conferidos |
| 23–24/10 | Extrator e recuperação de evidência funcionando isoladamente |
| 25–26/10 | Agente usando ferramentas e relatório ponta a ponta |
| 27–28/10 | Interface e avaliação em conjunto fixo de casos |
| 29/10 | Correções e versão congelada para demonstração |
| 30/10 | Protótipo e evidências de execução |

## Aceite em 30/10

- Vídeo real produz métricas reais, com configuração e unidades.
- Agente chama ferramentas; não é apenas texto estático ou resposta com números simulados.
- Fontes/páginas recuperadas sustentam a interpretação; ausência de evidência é explicitada.
- Sem regra aprovada, relatório descritivo; não emitir classe arbitrária.
- Cortes não implementados são indisponíveis, não zero.
- Execução e avaliação registradas; instalação documentada.
- Rede pode estar em experimento, separada da demonstração do agente.

## Até 11/12

02–13/11: rede própria, análise de erros, comparação com AutoShot e integração. 16–20/11: catálogo e recomendador. 23–27/11: integração e validação. 30/11–04/12: usuários, correções e documentação. 07–11/12: estabilização e apresentação.
