import streamlit as st
import spacy

# Configuração da página do Streamlit
st.set_page_config(page_title="Analisador de Sentimentos", page_icon="📊", layout="centered")

# Carrega o modelo do spaCy de forma eficiente com cache e fallback automático
@st.cache_resource
def load_nlp():
    try:
        # Tenta carregar o modelo instalado
        return spacy.load("pt_core_news_sm")
    except OSError:
        # Se não encontrar localmente, baixa o modelo oficial dinamicamente
        with st.spinner("Instalando modelo de linguagem em português (pt_core_news_sm)..."):
            spacy.cli.download("pt_core_news_sm")
        return spacy.load("pt_core_news_sm")

nlp = load_nlp()

# Dicionário de lemas (radicais das palavras) para classificação por regras
PALAVRAS_POSITIVAS = {
    "bom", "ótimo", "excelente", "maravilhoso", "gostar", "amar", "perfeito", 
    "parabéns", "rápido", "fácil", "eficiente", "sucesso", "recomendar", "ajudar"
}

PALAVRAS_NEGATIVAS = {
    "ruim", "péssimo", "horrível", "defeito", "quebrar", "atraso", "lento", 
    "difícil", "odiar", "problema", "erro", "falha", "pior", "caro", "suporte"
}

def analisar_sentimento(texto):
    """
    Analisa o texto usando tokenização e lematização do spaCy.
    Retorna a categoria, a cor correspondente e as pontuações.
    """
    doc = nlp(texto.lower())
    
    score_positivo = 0
    score_negativo = 0
    palavras_encontradas = []

    for token in doc:
        # Usamos o .lemma_ para capturar variações da mesma palavra (ex: "gostei", "gostou" -> "gostar")
        lema = token.lemma_
        
        if lema in PALAVRAS_POSITIVAS:
            score_positivo += 1
            palavras_encontradas.append((token.text, "Positiva"))
        elif lema in PALAVRAS_NEGATIVAS:
            score_negativo += 1
            palavras_encontradas.append((token.text, "Negativa"))
            
    # Regras condicionais para classificação simples em 3 categorias
    if score_positivo > score_negativo:
        sentimento = "Positivo"
        cor = "green"
    elif score_negativo > score_positivo:
        sentimento = "Negativo"
        cor = "red"
    else:
        sentimento = "Neutro"
        cor = "gray"
        
    return sentimento, cor, score_positivo, score_negativo, palavras_encontradas

# Interface do Usuário (Template Streamlit)
st.title("📊 Analisador de Sentimentos - Feedbacks")
st.write("Faça o upload de um arquivo `.txt` contendo feedbacks para classificar automaticamente.")

# Componente para upload do documento
uploaded_file = st.file_uploader("Escolha um arquivo TXT", type=["txt"])

if uploaded_file is not None:
    # Ler e decodificar o conteúdo do arquivo enviado
    conteudo_texto = uploaded_file.read().decode("utf-8")
    
    # Área expansível para visualizar o texto carregado
    with st.expander("Ver conteúdo do documento carregado"):
        st.text_area("Texto original:", conteudo_texto, height=200, disabled=True)
    
    # Botão para startar a leitura e processamento do documento
    if st.button("Iniciar Análise de Sentimento", type="primary"):
        with st.spinner("Processando PLN com spaCy..."):
            sentimento, cor, pos, neg, palavras = analisar_sentimento(conteudo_texto)
            
        st.write("---")
        st.subheader("Resultado da Classificação:")
        
        # Exibe o sentimento com formatação de cor nativa do Streamlit
        st.markdown(f"O sentimento predominante no documento é: **:{cor}[{sentimento}]**")
        
        # Exibição dos indicadores quantitativos (Métricas)
        col1, col2 = st.columns(2)
        col1.metric("Termos Positivos", pos)
        col2.metric("Termos Negativos", neg)
        
        # Detalhamento dos termos encontrados pelo pipeline de PLN
        if palavras:
            with st.expander("Detalhes das palavras-chave identificadas"):
                for palavra, tipo in palavras:
                    st.write(f"- Correspondência: `{palavra}` ({tipo})")