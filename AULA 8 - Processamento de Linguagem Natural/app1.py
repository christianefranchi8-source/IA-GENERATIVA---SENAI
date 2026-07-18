import streamlit as st
import spacy

# Configuração da página
st.set_set_config = st.set_page_config(page_title="Analisador de Sentimentos", page_icon="📊", layout="centered")

st.title("📊 Analisador de Sentimento em Documentos")
st.write("Faça o upload de um arquivo `.txt` em português para analisar o sentimento.")

# Carrega o modelo spaCy para português
@st.cache_resource
def load_spacy():
    try:
        return spacy.load("pt_core_news_sm")
    except OSError:
        from spacy.cli import download
        download("pt_core_news_sm")
        return spacy.load("pt_core_news_sm")

nlp = load_spacy()

# Dicionários léxicos básicos
PALAVRAS_POSITIVAS = {"amo", "adoro", "gosto", "bom", "ótimo", "excelente", "maravilhoso", "feliz", "sucesso", "recomendo"}
PALAVRAS_NEGATIVAS = {"odeio", "odiei", "ruim", "péssimo", "horrível", "triste", "fracasso", "errado", "defeito", "problema", "trabalhar"}

# Área de Upload
uploaded_file = st.file_uploader("Escolha o arquivo de texto (.txt)", type=["txt"])

if uploaded_file is not None:
    bytes_data = uploaded_file.read()
    texto_documento = bytes_data.decode("utf-8")
    
    with st.expander("Visualizar conteúdo do documento"):
        st.write(texto_documento)
    
    if st.button("Iniciar Análise de Sentimento", type="primary"):
        with st.spinner("Analisando o documento com spaCy..."):
            
            doc = nlp(texto_documento.lower())
            
            score_positivo = 0
            score_negativo = 0
            
            for token in doc:
                # Verifica se há uma negação ("não", "nunca", "jamais") associada a esta palavra
                tem_negacao = any(dep.dep_ == "advmod" and dep.text in {"não", "n", "nunca", "jamais"} for dep in token.children)
                
                # Se a palavra for positiva
                if token.text in PALAVRAS_POSITIVAS or token.lemma_ in PALAVRAS_POSITIVAS:
                    if tem_negacao:
                        score_negativo += 1  # "Não gosto" vira negativo
                    else:
                        score_positivo += 1  # "Gosto" continua positivo
                        
                # Se a palavra for negativa
                elif token.text in PALAVRAS_NEGATIVAS or token.lemma_ in PALAVRAS_NEGATIVAS:
                    if tem_negacao:
                        score_positivo += 1  # "Não é ruim" vira positivo
                    else:
                        score_negativo += 1  # "Ruim" continua negativo
            
            st.markdown("---")
            st.subheader("Resultado da Análise")
            
            # Regra de decisão do sentimento
            if score_positivo > score_negativo:
                st.success(f"🟢 **Sentimento Predominantemente Positivo** (Termos positivos: {score_positivo})")
                st.balloons()
            elif score_negativo > score_positivo:
                st.error(f"🔴 **Sentimento Predominantemente Negativo** (Termos negativos: {score_negativo})")
            else:
                st.warning("🟡 **Sentimento Neutro / Misto** (Equilíbrio de termos)")
                
            st.markdown("### Estatísticas do Documento (Visualização NLP)")
            col1, col2 = st.columns(2)
            col1.metric("Total de Palavras", len([token for token in doc if not token.is_punct]))
            col2.metric("Total de Sentenças", len(list(doc.sents)))