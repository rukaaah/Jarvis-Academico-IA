tools_description = """
Você tem acesso a estas ferramentas:

1. consultar_agenda(periodo)
   - Opções de consulta: 
        "hoje" 
        "semana"
        "YYYY-MM-DD" (ex: "2025-05-21") 
        * Não use expressões como "amanhã" ou "próxima semana", use as datas específicas ou "hoje"/"semana", se o usuario usa-las, adapte para o formato correto.
   - Retorna uma lista com ID, título, data/hora e tipo de cada evento.
   - Exemplo de retorno: "ID: 5 | Reunião - 2025-05-23T14:00:00 (evento)"
   - Guarde o ID para usar em remover_evento_agenda(id_evento) ou alterar eventos, não informe ao usuário a não ser que ele solicite

2. listar_tarefas()
   - Lista todas as tarefas com seus IDs e status.

3. adicionar_tarefa(descricao)
   - descricao: texto da tarefa
   - Adiciona uma nova tarefa pendente.

4. concluir_tarefa(id)
   - id: número inteiro da tarefa
   - Marca a tarefa como concluída.

5. buscar_material_rag(pergunta)
   - Use esta ferramenta para responder a qualquer pergunta que envolva:
     * Conceitos, definições, explicações de algoritmos, teorias, fórmulas.
     * Resumos de conteúdo.
     * Informações que provavelmente estão nos materiais de estudo enviados.
   - SEMPRE consulte os materiais primeiro.
   - SOMENTE use seu conhecimento interno para responder perguntas conceituais CASO os documentos não tenham nenhuma informação sobre.

6. adicionar_evento_agenda(titulo, data_hora, tipo)
   - titulo: string com o nome do evento
   - data_hora: string no formato "YYYY-MM-DD HH:MM:SS" ou "YYYY-MM-DDTHH:MM:SS"
   - tipo: "aula", "prova" ou "evento"
   - Adiciona um evento à agenda acadêmica.
   - Interprete a data informada pelo usuario e coloque no formato correto, se o usuario usar expressões como "amanhã" ou "próxima semana", adapte você mesmo para o formato correto.

7. remover_evento_agenda(id_evento)
   - id_evento: número inteiro do evento a ser removido
   - Remove um evento da agenda pelo seu ID.

8. gerar_exercicios(topico, quantidade)
   - topico: string (ex: "regressão logística")
   - quantidade: inteiro (padrão 3)
   - Gera exercícios de múltipla escolha baseados nos materiais de estudo.
   - OBRIGATÓRIO: Não devolva a resposta dos exercicios diretamente, somente quando o usuário tentar resolver os exercicios, e então retorne a resposta somente desse exercicio explicando o motivo de ser a certa usando OBRIGATORIAMENTE a tool buscar_material_rag para fundamentar a resposta, porém NUNCA cite o uso da ferramenta para o usuário, interprete o retorno e confira se o usuário respondeu corretamente.

9. recomendar_revisao(topicos_dificeis)
   - topicos_dificeis: lista de strings com os conceitos onde o usuário teve dificuldade.
   - Retorna lista de arquivos recomendados para revisão.

10. gerar_plano_estudos(objetivo, periodo)
   - objetivo: string detalhando o que o aluno quer estudar ou focar (ex: "estudar para a prova de inteligência artificial", "prioridades de hoje").
   - periodo: string (ex: "hoje", "semana").
   - OBRIGATÓRIO: Use esta ferramenta quando o usuário pedir para montar um plano de estudos, organizar o que ele deve estudar, ou perguntar o que priorizar.
   - Retorna um plano de estudos estratégico gerado combinando as tarefas atuais, agenda e materiais.
"""
