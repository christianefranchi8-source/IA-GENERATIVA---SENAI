import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np


st.header('ANALISE DE NOTAS - PREVENDO')



d = pd.read_csv('teste.csv')


# print(d)


estudos = pd.DataFrame({
'vendas': d['vendas'],
'temperatura':d['temperatura']
})


print(estudos)


st.bar_chart(estudos, x = 'temperatura', y= 'vendas')
modelo_escola = LinearRegression() 
modelo_escola.fit(estudos[['temperatura']], estudos['vendas'])


# h_estudo = st.slider('horas de estudos', 0,12,5)
temperatura = st.number_input('Temperarura', value = 0)
# n  =  np.array(temperatura)
nota_final = modelo_escola.predict([[temperatura]])
st.write(nota_final)


st.metric(f'sua Venda' ,f'{min(nota_final[0], 1000.0):.1f}')