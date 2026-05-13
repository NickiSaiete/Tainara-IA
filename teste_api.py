import google.generativeai as genai
import config

# Chave para teste direto
minha_chave = config.API_KEY_GOOGLE

print("--- Iniciando Diagnóstico de Conexão ---")
try:
    genai.configure(api_key=minha_chave)
    
    print("1. Listando modelos disponíveis...")
    modelos = genai.list_models()
    encontrou_flash = False
    for m in modelos:
        if 'generateContent' in m.supported_generation_methods:
            print(f"   - [OK] {m.name}")
            if config.MODELO_IA in m.name:
                encontrou_flash = True
    
    print(f"\n2. Testando resposta básica com {config.MODELO_IA}...")
    model = genai.GenerativeModel(config.MODELO_IA)
    resposta = model.generate_content("Diga: Olá Usuário, o sistema está pronto!")
    print(f"   - RESPOSTA: {resposta.text}")
    print("\n--- TUDO OK! O PROJETO VAI FUNCIONAR ---")

except Exception as e:
    print(f"\n--- ERRO DETECTADO ---")
    print(f"Tipo do erro: {type(e).__name__}")
    print(f"Mensagem: {e}")
    print("----------------------")