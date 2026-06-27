# procoding 
# vou  usar a biblioteca
import streamlit as st


st.title('CALCULADORA...')


n1  = st.number_input('numero:', )
n2  = st.number_input('numero:', value = 0.0)


soma, sub, div, mult = st.columns(4)
if soma.button('Soma'):
    calcular   =  n1  + n2 
    st.success(calcular)
elif sub.button('subtração'):    
    calcular   =  n1  - n2 
    st.success(calcular)    
elif div.button('Divisão'):    
    calcular   =  n1  / n2 
    st.success(calcular)       
elif mult.button('Multiplicação'):    
    calcular   =  n1  * n2 
    st.success(calcular)        

 #----------------------------------------------------------------------
import streamlit as st
st.title('Desafio 2: Formulário de Cadastro de Usuário (Entrada de Dados)')
nome = st.text_input('Insira seu nome completo:',)
idade = st.number_input('Insira sua idade', value = 0)
st.header("Você aceita os termos de uso?")
Aceito = st.checkbox("Eu Aceito")
Não_aceito = st.checkbox("Não aceito")
st.button ('Enviar formulario')

#-------------------------------------------------------------------------
import streamlit as st
st.title('Desafio 3: O Seletor de Cursos (Componentes de Escolha)')
opção = st.selectbox(
    "Qual o seu curso?",
    ("Pynton", "Web"),
)



Opções = st.multiselect(
    "Escolha qual a linguarem de programação que prefere?",
    ["GHTML", "CSS", "SQL", "Git"],
    
)



#-------------------------


