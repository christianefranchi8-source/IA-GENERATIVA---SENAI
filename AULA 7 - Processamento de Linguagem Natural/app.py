import streamlit as st
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from deep_translator import GoogleTranslator

# Baixa o dicionário do VADER (necessário apenas na primeira execução)
nltk.download('vader_lexicon')

# Inicializa o analisador de sentimentos
sia = SentimentIntensityAnalyzer()

# Configuração da interface com Streamlit
st.title("Análise de Sentimentos em Português")
st.write("Digite um texto em português para analisar o sentimento.")

# Campo para o usuário digitar o texto
user_input = st.text_area("Texto para análise:", "Eu adoro programar em Python! É simplesmente incrível.")

# Botão para disparar a análise
if st.button("Analisar Sentimento"):
    
    # Traduz o texto do português para o inglês para o VADER processar corretamente
    texto_traduzido = GoogleTranslator(source='pt', target='en').translate(user_input)
    
    # Executa a análise de sentimento no texto traduzido
    scores = sia.polarity_scores(texto_traduzido)
    compound_score = scores['compound']
    
    # Define a classificação com base no score compound
    if compound_score >= 0.05:
        label = "Positivo"
    elif compound_score <= -0.05:
        label = "Negativo"
    else:
        label = "Neutro"
        
    # Exibe os resultados na tela
    st.divider()
    st.subheader("Resultado da Análise")
    st.write(f"**Sentimento:** {label}")
    st.write(f"**Pontuação Compound:** {compound_score:.4f}")
    