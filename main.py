import config
import google.generativeai as genai
import sys
import io

# Configura o terminal para suportar emojis no Windows
if sys.platform == "win32":
    try:
        # Usa um wrapper que não fecha o stream original ao ser destruído
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    except (io.UnsupportedOperation, AttributeError):
        pass

from brain.personalidade import PROMPT_SISTEMA
from database.memoria_logica import iniciar_banco, guardar_mensagem, buscar_historico, obter_ou_criar_perfil, atualizar_perfil

# Configuração Inicial
iniciar_banco()
genai.configure(api_key=config.API_KEY_GOOGLE)

# Seleção do Modelo
model = genai.GenerativeModel(config.MODELO_IA)

def responder_usuario(mensagem_recebida, telefone="usuario_local"):
    # 1. Guardar o que o usuário disse
    guardar_mensagem(telefone, "Usuário", mensagem_recebida)
    
    # 2. Buscar perfil e histórico para dar contexto
    perfil = obter_ou_criar_perfil(telefone)
    historico = buscar_historico(telefone)
    
    # 3. Montar o prompt com a personalidade, perfil e histórico
    contexto_usuario = f"""
Dados do Usuário (Telefone: {telefone}):
- Nome: {perfil['nome'] if perfil['nome'] else 'Ainda não sei'}
- Preferências: {perfil['preferencias'] if perfil['preferencias'] else 'Ainda não conheço'}
- Rotina: {perfil['rotina'] if perfil['rotina'] else 'Ainda não me contou'}
"""

    prompt_final = f"""{PROMPT_SISTEMA}

{contexto_usuario}

Histórico das últimas conversas:
{historico}

Usuário: {mensagem_recebida}
Tainara.IA:"""

    try:
        # 4. Gerar resposta
        resposta = model.generate_content(prompt_final)
        texto_resposta = resposta.text
        
        # 5. Guardar a resposta da IA
        guardar_mensagem(telefone, "Tainara.IA", texto_resposta)
        
        # 6. Atualização automática do perfil (Extração simples por palavras-chave)
        # Nota: No futuro, podemos usar uma chamada secundária da IA para processar o perfil.
        if "meu nome é" in mensagem_recebida.lower():
            nome = mensagem_recebida.lower().split("meu nome é")[-1].strip().capitalize()
            atualizar_perfil(telefone, "nome", nome)
        elif "gosto de" in mensagem_recebida.lower():
            preferencias = mensagem_recebida.lower().split("gosto de")[-1].strip()
            atualizar_perfil(telefone, "preferencias", preferencias)
        elif "minha rotina é" in mensagem_recebida.lower():
            rotina = mensagem_recebida.lower().split("minha rotina é")[-1].strip()
            atualizar_perfil(telefone, "rotina", rotina)
        
        return texto_resposta
    except Exception as e:
        erro_str = str(e)
        print(f"\n[ERRO DETALHADO] {erro_str}")
        
        if "429" in erro_str:
            return "Eita! O Google me deu um 'gelo' agora por causa do limite de mensagens gratuitas 🧊. Espera uns minutinhos e tenta falar comigo de novo? Prometo que volto logo! ✨"
        elif "API_KEY_INVALID" in erro_str:
            return "Ops! Parece que a minha chave secreta (API Key) está com problemas. Dá uma olhadinha no config.py? 🧐"
        else:
            return "Eita! Tive um pequeno apagão aqui 😅. Parece que algo me deixou confusa. Tenta de novo em um instante!"

if __name__ == "__main__":
    print(f"--- {config.NOME_IA} Online e Atenta! 🚀 ---")
    print("(Podes começar a conversar. Digita 'sair' para encerrar)\n")
    
    # Simulador de Usuário (Permite trocar o número para testar multiusuário no terminal)
    telefone_atual = "usuario_local"
    
    while True:
        conversa = input(f"Você [{telefone_atual}]: ")
        
        if conversa.lower() in ["sair", "exit", "quit"]:
            break
            
        # Comando especial para trocar de usuário no teste
        if conversa.lower().startswith("/tel "):
            telefone_atual = conversa.split("/tel ")[1].strip()
            print(f"--- Agora simulando o telefone: {telefone_atual} ---\n")
            continue
            
        resposta = responder_usuario(conversa, telefone=telefone_atual)
        print(f"{config.NOME_IA}: {resposta}\n")