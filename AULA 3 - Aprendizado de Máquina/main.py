# NOTAS DE ESTUDOS 


import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression


st.header('ANALISE DE NOTAS - PREVENDO')


estudos = pd.DataFrame({
'notas':[1,2,4,6,8,10,2,8],
'horas':[2,4,5,7,9,10,1,6]
})


st.line_chart(estudos, x = 'horas', y= 'notas')
modelo_escola = LinearRegression() 
modelo_escola.fit(estudos[['horas']], estudos['notas'])


h_estudo = st.slider('horas de estudos', 0,12,5)
# h_estudo2 = st.text_input('horas de estudos')
nota_final = modelo_escola.predict([[h_estudo]])
print(nota_final)


st.metric(f'sua nota seria' ,f'{min(nota_final[0], 10.0):.1f}')