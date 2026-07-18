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

# Criando o botão que dispara a análise
botao_analise = st.button("🚀 Executar Análise Completa", type="primary")

# Só executa o código se o botão for clicado ou já tiver sido analisado
if botao_analise or st.session_state.get('analisado', False):
    st.session_state['analisado'] = True  

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

        # Listas de termos para validação e regras de negócio
        termos_positivos = ["excelente", "bom", "ótimo", "maravilhoso", "recomendo", "gostei", "perfeito", "ajudou"]
        palavras_negativas = ["ruim", "péssimo", "erro", "problema", "defeito", "demorou", "horrível", "atrasou"]
        
        contem_negativa = any(p in palavras_tokenizadas for p in palavras_negativas)
        
        # Contagem de palavras presentes no texto do usuário
        total_positivas = sum(1 for p in palavras_filtradas if p in termos_positivos)
        total_negativas = sum(1 for p in palavras_filtradas if p in palavras_negativas)

        # Classificação de Setor (Atividade 8)
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

        # --- CÁLCULO SISTÊMICO DA NOTA (1 A 10) ---
        # Mapeia matematicamente a escala de -1 a 1 do VADER para 1 a 10
        # Fórmula ajustada para também considerar bônus/ônus do nosso dicionário local em português
        ajuste_local = (total_positivas - total_negativas) * 0.1
        score_combinado = max(-1.0, min(1.0, score_geral + ajuste_local))
        
        # Converte para escala 1-10 e arredonda
        nota_final = round(((score_combinado + 1) / 2) * 9 + 1)
        
        # Classificação com base na sua regra definida
        if 1 <= nota_final <= 5:
            classificacao_nota = "Ruim 😡"
            sentimento_final = "negativo"
        elif 6 <= nota_final <= 7:
            classificacao_nota = "Regular 😐"
            sentimento_final = "neutro"
        elif 8 <= nota_final <= 9:
            classificacao_nota = "Bom 🙂"
            sentimento_final = "positivo"
        else:
            classificacao_nota = "Muito Bom 🥰"
            sentimento_final = "positivo"

    # --- CRIAÇÃO DAS ABAS ---
    nomes_abas = ["📋 Análise Completa"] + [f"Atividade {i}" for i in range(1, 11)]
    abas = st.tabs(nomes_abas)

    # =========================================================
    # ABA 📋: ANÁLISE COMPLETA (DASHBOARD CONSOLIDADO)
    # =========================================================
    with abas[0]:
        st.header("📋 Relatório Consolidado da Mensagem")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("🎯 Classificação")
            st.metric(label="Setor Destinado", value=setor_final)
        with col2:
            st.subheader("⚠️ Urgência")
            if sentimento_final == "negativo" or contem_negativa:
                st.error("Prioridade Máxima: Crítica")
            else:
                st.success("Prioridade Normal")
        with col3:
            st.subheader("🎭 Avaliação IA (Nota 1-10)")
            # Exibe a nota de forma gigante e amigável
            st.metric(label=f"Classificação: {classificacao_nota}", value=f"Nota {nota_final} / 10")

        st.markdown("---")
        
        col4, col5 = st.columns(2)
        with col4:
            st.subheader("🔍 Detalhes de Palavras Encontradas")
            st.write(f"Palavras positivas detectadas: `{total_positivas}`")
            st.write(f"Palavras negativas detectadas: `{total_negativas}`")
            st.write("**Lista sem Stopwords:**", palavras_filtradas)
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
        score_lexico = total_positivas - total_negativas
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
        st.write("**Métricas brutas do VADER:**", scores_vader)
        st.markdown(f"### Nota Calculada: **{nota_final} / 10**")
        
        # Ativa as animações de acordo com a sua nova regra de notas
        if nota_final == 10:
            st.success(f"🥰 **Incrível!** Feedback espetacular recebido.")
            st.balloons()
        elif 8 <= nota_final <= 9:
            st.success(f"🙂 **Bom!** Cliente satisfeito com a experiência.")
            st.balloons()  
        elif 6 <= nota_final <= 7:
            st.warning(f"😐 **Regular.** Atendimento morno ou com pontos a melhorar.")
        else:
            st.error(f"😡 **Ruim.** Cliente insatisfeito com problemas críticos.")
            st.snow()      
else:
    st.info("💡 Digite o texto acima e clique no botão para visualizar os resultados e liberar as abas.")