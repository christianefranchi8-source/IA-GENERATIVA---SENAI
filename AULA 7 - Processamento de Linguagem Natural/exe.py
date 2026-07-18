import streamlit as st
import string
from collections import Counter

# Importação das bibliotecas de IA
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from deep_translator import GoogleTranslator

# Garante o download do dicionário do VADER
@st.cache_resource
def iniciar_vader():
    nltk.download('vader_lexicon', quiet=True)
    return SentimentIntensityAnalyzer()

sia = iniciar_vader()

# --- CONFIGURAÇÃO DA INTERFACE STREAMLIT ---
st.set_page_config(page_title="Dashboard PLN", page_icon="📊", layout="wide")

st.title("📊 Painel Avançado de Processamento de Texto")
st.markdown("Insira a mensagem do cliente abaixo e clique em **Executar Análise** para processar os dados.")

# Entrada de texto global
mensagem_usuario = st.text_area(
    "Mensagem do Cliente para Análise:",
    value="O produto é EXCELENTE! Porém, o suporte técnico demorou muito para responder e deu um erro horrível no pagamento.",
    height=100
)

# Criando o botão que faltava para disparar a análise
botao_analise = st.button("🚀 Executar Análise Completa", type="primary")

# Só executa o código pesado se o botão for clicado
if botao_analise or st.session_state.get('analisado', False):
    st.session_state['analisado'] = True  # Mantém o estado ativo ao navegar nas abas

    with st.spinner("A IA está analisando o texto..."):
        # --- PROCESSAMENTO GLOBAL DOS DADOS ---
        # Tradução para o VADER
        texto_en = GoogleTranslator(source='pt', target='en').translate(mensagem_usuario)
        scores_vader = sia.polarity_scores(texto_en)
        score_geral = scores_vader['compound']

        # Limpeza básica (Atividade 9)
        texto_limpo = "".join([c for c in mensagem_usuario if c not in string.punctuation]).lower()

        # Tokenização básica (Atividade 1)
        palavras_tokenizadas = texto_limpo.split()

        # Remoção de Stopwords (Atividade 4)
        stopwords_pt = ["o", "a", "os", "as", "um", "uma", "de", "da", "do", "para", "em", "com", "é", "e", "porém"]
        palavras_filtradas = [p for p in palavras_tokenizadas if p not in stopwords_pt]

        # Regras de Negócio Reutilizáveis
        palavras_negativas = ["ruim", "péssimo", "erro", "problema", "defeito", "demorou", "horrível"]
        contem_negativa = any(p in palavras_tokenizadas for p in palavras_negativas)

        palavras_suporte = ["suporte", "técnico", "erro", "sistema", "login", "responder"]
        palavras_financeiro = ["pagamento", "boleto", "fatura", "cobrança", "reembolso"]
        pontos_sup = sum(1 for p in palavras_filtradas if p in palavras_suporte)
        pontos_fin = sum(1 for p in palavras_filtradas if p in palavras_financeiro)

        if pontos_sup > pontos_fin:
            setor_final = "🔧 Suporte Técnico"
        elif pontos_fin > pontos_sup:
            setor_final = "💰 Financeiro"
        else:
            setor_final = "👥 Triagem Geral (Empate)"

    # --- CRIAÇÃO DAS ABAS ---
    # Adicionada a aba "Análise Completa" na primeira posição
    nomes_abas = ["📋 Análise Completa"] + [f"Atividade {i}" for i in range(1, 11)]
    abas = st.tabs(nomes_abas)

    # =========================================================
    # ABA NOVA: ANÁLISE COMPLETA (DASHBOARD CONSOLIDADO)
    # =========================================================
    with abas[0]:
        st.header("📋 Relatório Consolidado da Mensagem")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("🎯 Classificação")
            st.metric(label="Setor Destinado", value=setor_final)
        with col2:
            st.subheader("⚠️ Urgência")
            if contem_negativa or score_geral < -0.05:
                st.error("Prioridade Máxima: Crítica")
            else:
                st.success("Prioridade Normal")
        with col3:
            st.subheader("🎭 Sentimento IA")
            if score_geral >= 0.05:
                st.success(f"😊 Positivo ({score_geral})")
            elif score_geral <= -0.05:
                st.error(f"😡 Negativo ({score_geral})")
            else:
                st.warning(f"😐 Neutro ({score_geral})")

        st.markdown("---")
        
        col4, col5 = st.columns(2)
        with col4:
            st.subheader("🔍 Palavras-Chave Relevantes")
            st.write(palavras_filtradas)
        with col5:
            st.subheader("📈 Termos Mais Repetidos")
            contador = Counter(palavras_filtradas)
            for pal, qtd in contador.most_common(3):
                st.markdown(f"- **{pal}**: {qtd}x")

    # =========================================================
    # ABA 1: TOKENIZAÇÃO
    # =========================================================
    with abas[1]:
        st.header("Atividade 1: Tokenização")
        st.json(palavras_tokenizadas)

    # =========================================================
    # ABA 2: FREQUÊNCIA DE PALAVRAS
    # =========================================================
    with abas[2]:
        st.header("Atividade 2: Frequência das Palavras")
        frequencia = {}
        for p in palavras_tokenizadas:
            frequencia[p] = frequencia.get(p, 0) + 1
        st.write(frequencia)

    # =========================================================
    # ABA 3: REGRA CONDICIONAL NEGATIVA
    # =========================================================
    with abas[3]:
        st.header("Atividade 3: Detecção de Palavras Negativas")
        st.write("**Palavras buscadas:**", palavras_negativas)
        if contem_negativa:
            st.error("🚨 Alerta: Palavra negativa encontrada! Prioridade: ALTA.")
        else:
            st.success("🟢 Nenhuma palavra negativa encontrada.")

    # =========================================================
    # ABA 4: REMOVER STOPWORDS
    # =========================================================
    with abas[4]:
        st.header("Atividade 4: Remoção de Stopwords")
        st.write("**Filtro aplicado:**", stopwords_pt)
        st.write("**Resultado:**", palavras_filtradas)

    # =========================================================
    # ABA 5: CLASSIFICAÇÃO DE SENTIMENTO CONDICIONAL
    # =========================================================
    with abas[5]:
        st.header("Atividade 5: Classificação de Sentimento Simples")
        termos_positivos = ["excelente", "bom", "ótimo", "maravilhoso", "recomendo"]
        score_lexico = sum(1 for p in palavras_filtradas if p in termos_positivos) - sum(1 for p in palavras_filtradas if p in palavras_negativas)
        st.write(f"Score léxico básico: {score_lexico}")
        if score_lexico > 0: st.success("😊 Sentimento: Positivo")
        elif score_lexico < 0: st.error("😡 Sentimento: Negativo")
        else: st.warning("😐 Sentimento: Neutro")

    # =========================================================
    # ABA 6: CHATBOT - PALAVRAS-CHAVE DE DIRECIONAMENTO
    # =========================================================
    with abas[6]:
        st.header("Atividade 6: Lógica de Direcionamento do Chatbot")
        msg_analise = mensagem_usuario.lower()
        if "cancelar" in msg_analise or "cancelamento" in msg_analise: st.info("🤖 Setor: Cancelamento")
        elif "erro" in msg_analise or "problema" in msg_analise: st.info("🤖 Setor: Suporte Técnico")
        elif "pagamento" in msg_analise or "boleto" in msg_analise: st.info("🤖 Setor: Financeiro")
        else: st.info("🤖 Setor: Atendimento Geral")

    # =========================================================
    # ABA 7: MAIS FREQUENTES EM RECLAMAÇÕES
    # =========================================================
    with abas[7]:
        st.header("Atividade 7: Palavras mais Frequentes (Análise Limpa)")
        contador = Counter(palavras_filtradas)
        st.write(contador.most_common(3))

    # =========================================================
    # ABA 8: CLASSIFICAR EM SUPORTE OU FINANCEIRO
    # =========================================================
    with abas[8]:
        st.header("Atividade 8: Classificação Automática de Mensagens")
        st.write(f"Pontos Suporte: `{pontos_sup}` | Pontos Financeiro: `{pontos_fin}`")
        st.markdown(f"### Categoria Atribuída: **{setor_final}**")

    # =========================================================
    # ABA 9: REMOVER PONTUAÇÃO E NORMALIZAR
    # =========================================================
    with abas[9]:
        st.header("Atividade 9: Limpeza e Normalização de Texto")
        st.code(texto_limpo, language="text")

    # =========================================================
    # ABA 10: PIPELINE DE SENTIMENTO COMPLETO COM NLTK VADER + ANIMAÇÕES
    # =========================================================
    with abas[10]:
        st.header("Atividade 10: Pipeline Inteligente (Tokenização + IA NLTK Vader)")
        st.write(f"**Tradução para IA:** *\"{texto_en}\"*")
        st.write(scores_vader)
        
        if score_geral >= 0.05:
            st.success(f"😊 **Cliente Satisfeito** (Score: {score_geral})")
            st.balloons()  # 🎈 Balões se for positivo!
        elif score_geral <= -0.05:
            st.error(f"😡 **Cliente Insatisfeito** (Score: {score_geral})")
            st.snow()      # ❄️ Neve se for negativo!
        else:
            st.warning(f"😐 **Opinião Neutra** (Score: {score_geral})")
else:
    st.info("💡 Digite o texto acima e clique no botão para visualizar os resultados e liberar as abas.")