# Relatório de Avaliação do Sistema — JARVIS Acadêmico

Este documento apresenta a avaliação técnica e qualitativa do **JARVIS Acadêmico**, um assistente inteligente projetado para suporte ao estudante, utilizando uma arquitetura **RAG (Retrieval-Augmented Generation)** integrada com **Tool Calling manual** baseada no modelo de linguagem **Gemma 12B**.

---

## Especificações do Sistema

* **Nome do Sistema:** JARVIS Acadêmico
* **Arquitetura:** RAG + Tool Calling (Orquestração Manual)
* **Modelo de Linguagem Base (LLM):** Gemma 12B
* **Domínio de Aplicação:** Gerenciamento acadêmico, planejamento de estudos e consulta de materiais didáticos.

---

## Metodologia de Avaliação

O sistema foi submetido a uma bateria de **10 testes consecutivos** simulando interações reais de um usuário em um cenário de rotina acadêmica. Foram avaliadas as capacidades de:
1.  Recuperação de informações estruturadas via APIs (Tool Calling).
2.  Busca semântica em documentos não estruturados (RAG).
3.  Resistência a alucinações (Perguntas fora do escopo dos documentos).
4.  Raciocínio lógico e encadeamento de ações compostas (Multi-Tool e Hybrid RAG/Tool Calling).

### Critérios de Classificação:
* ✅ **Correta:** O sistema compreendeu a intenção, recuperou os documentos ou acionou as ferramentas adequadas e gerou uma resposta precisa e fidedigna.
* ⚠️ **Parcialmente Correta:** O sistema atendeu em parte a solicitação, mas falhou em algum detalhe menor ou omitiu alguma informação secundária.
* ❌ **Incorreta:** O sistema falhou na recuperação, alucinou a resposta ou tomou ações erradas.

---

## Tabela Resumo das Métricas

| Métrica | Resultado | Percentual |
| :--- | :---: | :---: |
| **Total de Interações Testadas** | 10 | 100% |
| **Classificação: Correta (✅)** | 10 | 100% |
| **Classificação: Parcialmente Correta (⚠️)** | 0 | 0% |
| **Classificação: Incorreta (❌)** | 0 | 0% |
| **Taxa de Sucesso Geral (Accuracy)** | **10 / 10** | **100%** |

---

## Detalhamento dos Casos de Teste

### Interação 1: Consulta de Tarefas Atuais
* **Pergunta:** `quais tarefas eu tenho`
* **Documentos / Recursos Recuperados:** `[Tool Calling]` Invocação da API de Banco de Dados de Tarefas (Método: `get_tasks()`).
* **Resposta do Sistema:** > "Você tem duas tarefas pendentes: Fazer comida as 12 (ID: 5), Fazer trabalho as 13 (ID: 6)... As tarefas já concluídas são: Revisar regressão logística (ID: 1)..."
* **Classificação:** ✅ Correta
* **Análise Técnica:** O modelo identificou perfeitamente a intenção de listagem e formatou a saída distinguindo de forma clara o status (pendente vs. concluída) junto aos identificadores únicos (IDs).

---

### Interação 2: Consulta de Calendário Acadêmico
* **Pergunta:** `qual prova tenho essa semana`
* **Documentos / Recursos Recuperados:** `[Tool Calling]` Invocação da API de Agenda/Calendário (Método: `get_events(period="week")`).
* **Resposta do Sistema:**
    > "Você tem uma prova agendada para esta semana. Será na quinta-feira, dia 18 de junho, às 09:00. Deseja que eu adicione um lembrete ou ajude a montar um plano de estudos para ela?"
* **Classificação:** ✅ Correta
* **Análise Técnica:** A ferramenta de calendário foi acionada com sucesso. O modelo demonstrou proatividade contextual ao oferecer ajuda para criar um cronograma de estudos para a data identificada.

---

### Interação 3: Geração de Plano de Estudos Híbrido (RAG + Tool Calling)
* **Pergunta:** `monte um plano de estudo para essa prova do dia 18, no qual o conteudo sera processos descritivos`
* **Documentos / Recursos Recuperados:** * `[RAG]` Arquivos: `4 - Processos Descritivos.pdf` e `3 - Processos Presctitivos.pdf`
    * `[Tool Calling]` Contexto interno do gerenciador de tarefas para conciliação de horários.
* **Resposta do Sistema:**
    > "Com certeza. Preparei um plano de estudos estratégico... Plano de Estudos Ativado: Missão 'Processos Descritivos' ... [Cronograma detalhado integrando as tarefas de fazer comida (ID 5) e fazer trabalho (ID 6)]"
* **Classificação:** ✅ Correta
* **Análise Técnica:** Caso de alta complexidade. O modelo demonstrou capacidade avançada de raciocínio lógico (*agentic reasoning*). Ele realizou o RAG para entender a matéria, identificou a necessidade de comparar com processos prescritivos e usou as tarefas do banco de dados do usuário para preencher os horários livres, criando um cronograma adaptativo e livre de conflitos.

---

### Interação 4: Resiliência contra Alucinação (Out of Domain)
* **Pergunta:** `Explique o que é [regressão logística / embeddings], segundo os meus materiais de estudo`
* **Documentos / Recursos Recuperados:** `[RAG]` Busca vetorial na base de conhecimento (Retorno: Nível de similaridade abaixo do limiar para os termos solicitados).
* **Resposta do Sistema:**
    > "Com base nos materiais de estudo que você forneceu, não encontrei uma definição direta para os termos 'regressão logística' e 'embeddings'. Os documentos parecem focar em processos de software... Gostaria que eu explicasse esses conceitos com base no meu conhecimento geral...?"
* **Classificação:** ✅ Correta
* **Análise Técnica:** Comportamento ideal para sistemas de missão crítica. Ao invés de alucinar ou usar o conhecimento pré-treinado fingindo que estava no texto, o sistema mapeou corretamente a ausência da informação na base RAG, reportou o fato ao usuário e solicitou autorização para transicionar para o conhecimento paramétrico geral.

---

### Interação 5: Consulta Conceitual Direta (RAG)
* **Pergunta:** `explique o que é processos descritivos, segundo os meus materiais de estudo`
* **Documentos / Recursos Recuperados:** `[RAG]` Extração de trechos do arquivo `4 - Processos Descritivos.pdf`.
* **Resposta do Sistema:**
    > "De acordo com seus materiais de estudo, Processos Descritivos são modelos que descrevem como algo é feito de fato em uma organização... Foco: Descrevem a realidade... Origem: criados a partir da observação..."
* **Classificação:** ✅ Correta
* **Análise Técnica:** O RAG funcionou perfeitamente. A resposta foi concisa, estruturada em tópicos e sintetizou fielmente os exatos pilares da modelagem descritiva presentes na literatura técnica fornecida.

---

### Interação 6: Resumo Restrito de Documento
* **Pergunta:** `Faça um resumo dos principais pontos do arquivo [conceitos.pdf].`
* **Documentos / Recursos Recuperados:** `[RAG]` Leitura direcionada e priorizada do arquivo `conceitos.pdf`.
* **Resposta do Sistema:**
    > "Com base no arquivo conceitos.pdf, aqui estão os principais pontos abordados: 1. Algoritmo K-Nearest Neighbors (KNN)... 2. Processos de Software (Prescritivos vs Descritivos)..."
* **Classificação:** ✅ Correta
* **Análise Técnica:** O modelo obedeceu à restrição de escopo de arquivo único imposta pelo prompt, isolando os conceitos do `conceitos.pdf` (como o algoritmo KNN) de forma clara e altamente estruturada.

---

### Interação 7: Execução em Cadeia e Atualização de Estado (Multi-Tool Calling)
* **Pergunta:** `Adicione a tarefa 'Ler artigo sobre Machine Learning' e, em seguida, liste todas as minhas tarefas pendentes.`
* **Documentos / Recursos Recuperados:** `[Tool Calling]` Execução sequencial:
    1.  `add_task(name="Ler artigo sobre Machine Learning")`
    2.  `get_tasks(status="pending")`
* **Resposta do Sistema:**
    > "Certo. A tarefa 'Ler artigo sobre Machine Learning' foi adicionada. Suas tarefas pendentes agora são: Fazer comida as 12 (ID: 5)... Ler artigo sobre Machine Learning (ID: 7)"
* **Classificação:** ✅ Correta
* **Análise Técnica:** O pipeline de Tool Calling interpretou com sucesso comandos múltiplos em uma única frase, garantindo a ordem lógica cronológica de execução (inserir antes de listar) e refletindo dinamicamente o novo ID gerado (ID 7).

---

### Interação 8: Atualização Cruzada de Estados (Multi-Tool Calling)
* **Pergunta:** `Cancele o evento da minha prova do dia 18 e marque a tarefa de ID 5 como concluída.`
* **Documentos / Recursos Recuperados:** `[Tool Calling]` Execução sequencial em diferentes microserviços:
    1.  `cancel_event(date="18/06", type="prova")`
    2.  `update_task_status(id=5, status="completed")`
* **Resposta do Sistema:**
    > "Certo. A prova do dia 18 foi cancelada e a tarefa 'Fazer comida as 12' foi marcada como concluída."
* **Classificação:** ✅ Correta
* **Análise Técnica:** O assistente demonstrou segurança ao extrair os parâmetros das entidades (`dia 18` e `ID 5`) e roteá-los adequadamente para as respectivas funções de escrita/mutação do sistema.

---

### Interação 9: Prompt de Multi-Intenção e Síntese de Conteúdo
* **Pergunta:** `O que eu devo priorizar hoje nos meus estudos? Gere 3 exercícios de múltipla escolha sobre processos descritivos para eu praticar.`
* **Documentos / Recursos Recuperados:**
    * `[Tool Calling]` `get_tasks()` + `get_events()` para análise de prioridade de tempo.
    * `[RAG]` Arquivos `7 - Guia-de-Avaliacao-2024-Parte-1.pdf` e `4 - Processos Descritivos.pdf`.
* **Resposta do Sistema:**
    > "Protocolo de planejamento ativado... Prioridades para Hoje (14/06): Foco Imediato: Finalizar o Trabalho Pendente (Guia-de-Avaliacao-2024-Parte-1.pdf)... Exercícios de Prática: Processos Descritivos [Apresenta 3 questões de múltipla escolha precisas]..."
* **Classificação:** ✅ Correta
* **Análise Técnica:** Excelente comportamento como agente autônomo. O sistema percebeu que a prova havia sido cancelada no turno anterior e recalculou a rota de estudos do dia instantaneamente, priorizando o Guia de Avaliação e o Artigo recém-adicionado. Além disso, formulou itens de avaliação coerentes com os PDFs recuperados.

---

### Interação 10: RAG Contextual + Ação Imediata
* **Pergunta:** `Eu não lembro o que é simules. Me explique o que é isso e crie uma tarefa para eu estudar esse assunto amanhã.`
* **Documentos / Recursos Recuperados:**
    * `[RAG]` Conteúdo extraído de `5 - SimulES.pdf`.
    * `[Tool Calling]` `add_task(name="Estudar sobre simules", date="15/06")`.
* **Resposta do Sistema:**
    > "De acordo com o documento 5 - SimulES.pdf, o SimulES é um jogo de competição focado em engenharia de software... A tarefa 'Estudar sobre simules' já foi adicionada à sua lista para amanhã."
* **Classificação:** ✅ Correta
* **Análise Técnica:** Fechamento de ciclo consistente. O modelo efetuou a busca semântica para sanar a dúvida informacional imediata do usuário (definição do SimulES) e usou a ferramenta de persistência de dados para garantir que a rotina de estudos futura absorvesse essa demanda de forma automatizada.

---

## 🔍 Conclusões Teóricas e Práticas da Avaliação

1.  **Orquestração e Tool Calling Robustos:** O sistema apresentou 100% de precisão na escolha de ferramentas de leitura e escrita. O mapeamento manual de funções provou-se altamente confiável usando o Gemma 12B, lidando com chamadas compostas e encadeadas de forma limpa.
2.  **Alinhamento de Contexto (RAG):** O mecanismo de recuperação vetorial trouxe trechos semanticamente ricos e corretos. O maior destaque reside no tratamento de perguntas fora do escopo, demonstrando que o sistema possui travas de segurança bem ajustadas contra o fenômeno de alucinação de dados.
3.  **Memória de Sessão e Atualização Dinâmica:** O comportamento na Interação 9 comprovou que o sistema mantém e processa as mutações de estado ocorridas na mesma sessão de chat de maneira inteligente (identificando a exclusão do evento anterior para redefinir as prioridades atuais do estudante).