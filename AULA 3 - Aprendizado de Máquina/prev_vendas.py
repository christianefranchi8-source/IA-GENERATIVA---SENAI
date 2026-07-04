import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression

st.header("Previsão de Vendas")

# Dados: [Investimento em Marketing] -> Faturamento
dados_vendas = pd.DataFrame({
    'investimento': [100, 200, 300, 400, 500, 600],
    'faturamento': [1200, 2500, 3200, 4800, 5100, 6300]
})

st.line_chart(dados_vendas, x = 'faturamento', y= 'investimento')
modelo_vendas = LinearRegression() 
modelo_vendas.fit(dados_vendas[['investimento']], dados_vendas['faturamento'])


fat = st.slider('faturamento', 0,8000)
# h_estudo2 = st.text_input('horas de estudos')
faturamento_final = modelo_vendas.predict([[fat]])
print(faturamento_final)


st.metric(f'Seu investimento seria' ,f'{min(faturamento_final[0], 6300):.1f}')
# objetivo: previsão de FATURAMENTO baseado nos investimentos