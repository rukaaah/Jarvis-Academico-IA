import json
import re
from .llm_client import call_llm
from .prompts import SYSTEM_PROMPT, RESPONSE_SYSTEM_PROMPT
from tools import execute_tool_call

def extract_tool_calls(content: str):
    """Extrai múltiplos JSONs de tool calls de uma string."""
    tool_calls = []
    content = content.strip()
    # Tenta interpretar o conteúdo inteiro como um único JSON
    try:
        data = json.loads(content)
        if isinstance(data, dict) and "tool" in data and "arguments" in data:
            tool_calls.append(data)
            return tool_calls
    except:
        pass
    # Caso contrário, procura blocos delimitados por chaves balanceadas
    i = 0
    length = len(content)
    while i < length:
        if content[i] == '{':
            count = 1
            j = i + 1
            while j < length and count > 0:
                if content[j] == '{':
                    count += 1
                elif content[j] == '}':
                    count -= 1
                j += 1
            if count == 0:
                candidate = content[i:j]
                try:
                    data = json.loads(candidate)
                    if isinstance(data, dict) and "tool" in data and "arguments" in data:
                        tool_calls.append(data)
                except:
                    pass
                i = j
            else:
                i += 1
        else:
            i += 1
    return tool_calls

def run_agent(conversation_history):
    """
    Executa o agente com loop de tool calling.
    conversation_history: lista de dicionários {'role', 'content'} (sem system prompt).
    Retorna a resposta final em linguagem natural.
    """
    # Prepara as mensagens com o system prompt inicial
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history
    max_iter = 5
    for _ in range(max_iter):
        assistant_msg = call_llm(messages)
        print(f"🔧 RESPOSTA DO MODELO:\n{assistant_msg}")
        tool_calls = extract_tool_calls(assistant_msg)
        if not tool_calls:
            return assistant_msg
        # Executa todas as tools desta rodada
        results = []
        for tc in tool_calls:
            tool_name = tc["tool"]
            args = tc["arguments"]
            result = execute_tool_call(tool_name, args)
            results.append(f"Ferramenta {tool_name} ({args}) retornou: {result}")
        # Adiciona a resposta e os resultados ao histórico
        messages.append({"role": "assistant", "content": assistant_msg})
        messages.append({"role": "user", "content": "Resultados das ferramentas:\n" + "\n".join(results)})
    # Se estourar o limite, força uma resposta final usando outro system prompt
    final_messages = [{"role": "system", "content": RESPONSE_SYSTEM_PROMPT}] + messages[1:]
    return call_llm(final_messages)