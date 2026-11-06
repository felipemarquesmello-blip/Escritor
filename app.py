import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. MEMÓRIA DO APLICATIVO
# ==========================================
if 'manuscrito' not in st.session_state:
    st.session_state.manuscrito = ""
    
if 'personagens' not in st.session_state:
    st.session_state.personagens = [
        {"nome": "Daru", "cla": "Ñuke", "descricao": "Guerreiro focado, ágil e em constante adaptação."},
        {"nome": "Skrull", "cla": "Velociraptor", "descricao": "Líder implacável, astuto e letal nas caçadas."},
        {"nome": "Lila", "cla": "Minimus", "descricao": "Sobrevivente humana engenhosa."}
    ]
    
if 'locais' not in st.session_state:
    st.session_state.locais = [
        {"nome": "Terras Altas", "regiao": "Pangeia", "descricao": "Região montanhosa de difícil acesso, com vegetação densa."}
    ]

# ==========================================
# 2. FUNÇÃO DE BUSCA E IA (RAG com Gemini)
# ==========================================
def gerar_sugestoes_gemini(texto, api_key):
    # Configura a chave da sua conta
    genai.configure(api_key=api_key)
    
    # Busca personagens e locais citados no texto para criar o contexto
    contexto = []
    for p in st.session_state.personagens:
        if p["nome"].lower() in texto.lower():
            contexto.append(f"Personagem: {p['nome']} (Clã {p['cla']}) - {p['descricao']}")
            
    for l in st.session_state.locais:
        if l["nome"].lower() in texto.lower():
            contexto.append(f"Local: {l['nome']} ({l['regiao']}) - {l['descricao']}")
            
    texto_contexto = "\n".join(contexto) if contexto else "Nenhum personagem ou local específico identificado neste trecho."
    
    # Monta o prompt instruindo o Gemini
    prompt = f"""
    Você é um co-piloto de escrita criativa de dark fantasy e ficção.
    Sua função é ler o último trecho do manuscrito e sugerir 3 opções de como a história pode continuar.
    
    [CONTEXTO DO SEU UNIVERSO (Fichas)]
    {texto_contexto}
    
    [ÚLTIMO TRECHO ESCRITO]
    "{texto}"
    
    Forneça 3 sugestões numeradas para o próximo parágrafo.
    1. Focada em Ação ou Tensão.
    2. Focada em Diálogo.
    3. Focada em Descrição do Ambiente.
    Mantenha as sugestões curtas e fiéis ao contexto.
    """
    
    # Chama o modelo do Gemini
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text

# ==========================================
# 3. MENU LATERAL E CONFIGURAÇÃO
# ==========================================
st.sidebar.title("Navegação do Projeto")
menu = st.sidebar.radio("Ir para:", ["📖 Manuscrito", "👤 Personagens", "🗺️ Locais"])

st.sidebar.divider()
st.sidebar.subheader("Configuração da IA")
chave_api = st.sidebar.text_input("Chave API do Gemini", type="password", help="Pegue sua chave gratuita no Google AI Studio")

# ==========================================
# 4. PÁGINA: MANUSCRITO
# ==========================================
if menu == "📖 Manuscrito":
    st.title("Editor de História")
    
    texto_atual = st.text_area("Escreva seu capítulo aqui:", value=st.session_state.manuscrito, height=400)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("💾 Salvar Texto"):
            st.session_state.manuscrito = texto_atual
            st.success("Salvo!")
            
    with col2:
        if st.button("✨ Sugerir Continuação (Gemini)"):
            if texto_atual.strip() == "":
                st.warning("Escreva um pouco da história primeiro!")
            elif not chave_api:
                st.error("Por favor, insira sua Chave API do Gemini no menu lateral esquerdo.")
            else:
                with st.spinner("O Gemini está analisando sua história e lendo as fichas..."):
                    try:
                        sugestoes = gerar_sugestoes_gemini(texto_atual, chave_api)
                        st.write(sugestoes)
                    except Exception as e:
                        st.error(f"Erro ao conectar com o Gemini: {e}")

# ==========================================
# 5. PÁGINA: PERSONAGENS
# ==========================================
elif menu == "👤 Personagens":
    st.title("Fichas de Personagens")
    
    with st.expander("➕ Adicionar Novo Personagem", expanded=False):
        novo_nome = st.text_input("Nome")
        novo_cla = st.selectbox("Clã/Espécie", ["Ñuke", "Kani", "Velociraptor", "T-Rex", "Minimus", "Outro"])
        nova_desc = st.text_area("Descrição / Personalidade")
        
        if st.button("Cadastrar Personagem"):
            if novo_nome:
                st.session_state.personagens.append({"nome": novo_nome, "cla": novo_cla, "descricao": nova_desc})
                st.success(f"{novo_nome} cadastrado com sucesso!")
            else:
                st.error("O nome é obrigatório.")
                
    st.subheader("Cadastros Atuais")
    for p in st.session_state.personagens:
        st.markdown(f"**{p['nome']}** *(Clã: {p['cla']})* — {p['descricao']}")
        st.divider()

# ==========================================
# 6. PÁGINA: LOCAIS
# ==========================================
elif menu == "🗺️ Locais":
    st.title("Geografia")
    
    with st.expander("➕ Adicionar Novo Local", expanded=False):
        novo_local = st.text_input("Nome do Local")
        nova_regiao = st.text_input("Região")
        nova_desc_local = st.text_area("Detalhes e características")
        
        if st.button("Cadastrar Local"):
            if novo_local:
                st.session_state.locais.append({"nome": novo_local, "regiao": nova_regiao, "descricao": nova_desc_local})
                st.success(f"{novo_local} cadastrado com sucesso!")
                
    st.subheader("Locais Conhecidos")
    for l in st.session_state.locais:
        st.markdown(f"**{l['nome']}** *(Região: {l['regiao']})* — {l['descricao']}")
        st.divider()
