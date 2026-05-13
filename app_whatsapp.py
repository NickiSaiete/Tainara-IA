from flask import Flask, request, jsonify
import main
import config

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Endpoint para receber mensagens do WhatsApp.
    Compatível com a maioria das APIs (Twilio, Evolution API, Z-API, etc.)
    """
    dados = request.json
    
    # Tentativa de extrair telefone e mensagem de diferentes formatos comuns
    telefone = dados.get("from") or dados.get("sender") or dados.get("remoteJid")
    mensagem = dados.get("text") or dados.get("message") or dados.get("content")
    
    if not telefone or not mensagem:
        # Se for um evento de status (delivery, seen), apenas ignoramos
        return jsonify({"status": "ignorado", "motivo": "evento_sem_mensagem"}), 200
    
    # Limpa o número de telefone (remove @s.whatsapp.net se houver)
    telefone = telefone.split("@")[0]
    
    print(f"--- 📩 Mensagem de {telefone}: {mensagem} ---")
    
    # Chama a lógica da Tainara
    resposta = main.responder_usuario(mensagem, telefone=telefone)
    
    print(f"--- 📤 Resposta da Tainara: {resposta[:50]}... ---")
    
    return jsonify({
        "status": "sucesso",
        "to": telefone,
        "reply": resposta
    })

if __name__ == "__main__":
    print(f"--- Servidor da {config.NOME_IA} pronto para Webhook! ---")
    print("Aguardando conexões em http://localhost:5000/webhook")
    app.run(port=5000, debug=True)
