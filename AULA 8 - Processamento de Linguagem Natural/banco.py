import streamlit as st
import spacy
from spacy.matcher import PhraseMatcher

# Configuração da página do Streamlit
st.set_page_config(page_title="Central de Atendimento", page_icon="🤖", layout="wide")

# Inicializa variáveis de estado
if "classe_detectada" not in st.session_state:
    st.session_state.classe_detectada = None
if "termo_detectado" not in st.session_state:
    st.session_state.termo_detectado = None

# Carrega o modelo do spaCy
@st.cache_resource
def load_nlp():
    return spacy.load("pt_core_news_sm")

nlp = load_nlp()

# Configuração do Matcher com as regras estritas
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

termos_bloqueio = [nlp.make_doc(text) for text in ["bloquear cartão", "bloqueio do cartão", "cancelar cartão", "perdi o cartão"]]
termos_2via_cartao = [nlp.make_doc(text) for text in ["segunda via do cartão", "2 via do cartão", "segunda via cartão", "2 via cartão"]]
termos_boleto = [nlp.make_doc(text) for text in ["segunda via de boleto", "2 via boleto", "segunda via do boleto", "novo boleto", "pdf do boleto"]]
termos_limite = [nlp.make_doc(text) for text in ["aumentar limite", "mais limite", "aumento de limite", "subir limite"]]
termos_fraude = [nlp.make_doc(text) for text in ["não reconheço essa compra", "compra indevida", "cartão clonado", "clonaram meu cartão", "golpe"]]
termos_cadastro = [nlp.make_doc(text) for text in ["mudar endereço", "atualizar cadastro", "trocar telefone", "alterar dados"]]
termos_senha = [nlp.make_doc(text) for text in ["esqueci a senha", "senha bloqueada", "recuperar senha", "trocar senha"]]

matcher.add("BLOQUEAR_CARTAO", termos_bloqueio)
matcher.add("2_VIA_CARTAO", termos_2via_cartao)
matcher.add("2_VIA_BOLETO", termos_boleto)
matcher.add("AUMENTO_LIMITE", termos_limite)
matcher.add("CONTESTACAO_FRAUDE", termos_fraude)
matcher.add("ATUALIZACAO_CADASTRAL", termos_cadastro)
matcher.add("PROBLEMA_SENHA", termos_senha)

def classificar_solicitacao(texto):
    doc = nlp(texto.lower())
    matches = matcher(doc)
    
    # 1. Tenta Match exato por palavra-chave (Alta Prioridade)
    if matches:
        match_id, start, end = matches[0]
        string_id = nlp.vocab.strings[match_id]
        return string_id, doc[start:end].text
    
    # 2. Heurística de Contexto Inteligente (Evita conflito entre Cartão e Boleto)
    texto_str = doc.text
    
    # Se falar em "via" ou "segunda" junto com "cartão", vai para 2ª via de cartão
    if ("via" in texto_str or "segunda" in texto_str) and "cart" in texto_str:
        return "2_VIA_CARTAO", "Identificado por contexto (2ª Via Cartão)"
        
    if any(palavra in texto_str for palavra in ["bloque", "perdi", "cancel", "extravio"]):
        return "BLOQUEAR_CARTAO", "Identificado por contexto (Bloqueio)"
        
    if "boleto" in texto_str or (any(p in texto_str for p in ["2 via", "segunda via"]) and "cart" not in texto_str):
        return "2_VIA_BOLETO", "Identificado por contexto (Boleto)"
        
    if any(palavra in texto_str for palavra in ["limite", "credito", "crédito", "aumenta"]):
        return "AUMENTO_LIMITE", "Identificado por contexto (Limite)"
    if any(palavra in texto_str for palavra in ["fraude", "clon", "roub", "indevid", "reconhec"]):
        return "CONTESTACAO_FRAUDE", "Identificado por contexto (Fraude)"
    if any(palavra in texto_str for palavra in ["endereço", "cadastro", "telefone", "dados", "mudei"]):
        return "ATUALIZACAO_CADASTRAL", "Identificado por contexto (Cadastro)"
    if any(palavra in texto_str for palavra in ["senha", "login", "entrar", "acesso", "bloqueada"]):
        return "PROBLEMA_SENHA", "Identificado por contexto (Senha)"
        
    return "DESCONHECIDO", None

# --- INTERFACE ---
st.title("🤖 Central de Atendimento Automatizada")
st.subheader("Identificação e execução de solicitações via PLN")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📝 Entrada do Cliente")
    user_input = st.text_area(
        "O que o cliente está solicitando?", 
        placeholder="Digite o texto ou problema relatado pelo cliente aqui..."
    )
    
    if st.button("Analisar Texto", type="primary"):
        if user_input.strip():
            classe, termo = classificar_solicitacao(user_input)
            st.session_state.classe_detectada = classe
            st.session_state.termo_detectado = termo
        else:
            st.warning("Por favor, digite um texto antes de analisar.")

with col2:
    st.markdown("### 🔍 Análise do Sistema")
    
    if st.session_state.classe_detectada:
        classe = st.session_state.classe_detectada
        termo = st.session_state.termo_detectado
        
        # Caso 1: Bloqueio de Cartão
        if classe == "BLOQUEAR_CARTAO":
            st.warning("⚠️ **Intenção Detectada:** Bloqueio de Cartão")
            if termo: st.info(f"**Gatilho:** '{termo}'")
            st.markdown("---")
            if st.button("🚀 EXECUTAR BLOQUEIO IMEDIATO", key="btn_bloqueio"):
                st.error("🔒 Cartão bloqueado com sucesso no sistema de forma 100% automatizada!")
                st.session_state.classe_detectada = None 
                
        # Caso 2: Segunda Via de Cartão (NOVO)
        elif classe == "2_VIA_CARTAO":
            st.success("💳 **Intenção Detectada:** Solicitação de 2ª Via do Cartão")
            if termo: st.info(f"**Gatilho:** '{termo}'")
            st.markdown("---")
            st.info("ℹ️ Solicitação de nova via do cartão físico registrada. Verifique o endereço de entrega na aba cadastro.")

        # Caso 3: Segunda Via de Boleto
        elif classe == "2_VIA_BOLETO":
            st.success("📄 **Intenção Detectada:** Solicitação de 2ª Via de Boleto")
            if termo: st.info(f"**Gatilho:** '{termo}'")
            st.markdown("---")
            st.info("ℹ️ Solicitação registrada. O boleto digital atualizado foi encaminhado ao e-mail cadastrado.")

        # Caso 4: Aumento de Limite
        elif classe == "AUMENTO_LIMITE":
            st.success("📈 **Intenção Detectada:** Alteração/Aumento de Limite")
            if termo: st.info(f"**Gatilho:** '{termo}'")
            st.markdown("---")
            st.info("ℹ️ Análise de crédito iniciada automaticamente.")

        # Caso 5: Contestação de Compra / Fraude
        elif classe == "CONTESTACAO_FRAUDE":
            st.error("🚨 **Intenção Detectada:** Contestação por Fraude / Roubo")
            if termo: st.info(f"**Gatilho:** '{termo}'")
            st.markdown("---")
            if st.button("🛡️ CONTESTAR E PREVENTIVAR CARTÃO", key="btn_fraude"):
                st.error("🔒 Transação congelada e cartão preventivamente bloqueado para análise da auditoria!")
                st.session_state.classe_detectada = None

        # Caso 6: Atualização Cadastral
        elif classe == "ATUALIZACAO_CADASTRAL":
            st.info("📋 **Intenção Detectada:** Atualização de Dados Cadastrais")
            if termo: st.info(f"**Gatilho:** '{termo}'")
            st.markdown("---")
            st.info("ℹ️ Sistema direcionou o cliente para o formulário seguro de revalidação de dados.")

        # Caso 7: Problemas com Senha
        elif classe == "PROBLEMA_SENHA":
            st.warning("🔑 **Intenção Detectada:** Problemas com Senha / Acesso")
            if termo: st.info(f"**Gatilho:** '{termo}'")
            st.markdown("---")
            st.info("ℹ️ Token de reset de senha enviado por SMS.")
                
        else:
            st.info("🤷‍♂️ **Intenção não identificada com clareza.**")
            st.write("Redirecionando para um atendente humano da fila geral...")