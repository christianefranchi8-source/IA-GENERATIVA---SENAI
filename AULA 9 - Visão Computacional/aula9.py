import cv2
import numpy as np
import streamlit as st
from PIL import Image
from ultralytics import YOLO

# Configuração inicial da página web
st.set_page_config(page_title="Detector de Veículos", layout="centered")
st.title("🚗 Detector de Carros - Upload de Clientes")
st.write("Faça o upload de uma imagem para identificar e localizar os carros presentes.")

@st.cache_resource
def carregar_modelo():
    """Carrega o modelo YOLO apenas uma vez e guarda em cache na memória."""
    return YOLO("yolov8n.pt")

model = carregar_modelo()

# Componente de upload de arquivos do Streamlit
arquivo_enviado = st.file_uploader("Escolha uma imagem (JPG, JPEG, PNG)...", type=["jpg", "jpeg", "png"])

if arquivo_enviado is not None:
    # Converte o arquivo enviado para o formato PIL e depois para o array OpenCV (BGR)
    imagem_pil = Image.open(arquivo_enviado)
    imagem_bgr = cv2.cvtColor(np.array(imagem_pil), cv2.COLOR_RGB2BGR)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Imagem Original")
        st.image(imagem_pil, use_container_width=True)
        
    with st.spinner("Processando imagem e detectando veículos..."):
        # Executa a inferência do modelo
        resultados = model(imagem_bgr, verbose=False)[0]
        
        CLASSE_CARRO = 2
        total_carros = 0
        
        # Desenha as caixas na imagem para exibição visual
        for box in resultados.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            
            # Filtra apenas pela classe de carros com confiança mínima de 25%
            if cls == CLASSE_CARRO and conf >= 0.25:
                total_carros += 1
                x1, y1, x2, y2 = [int(coord) for coord in box.xyxy[0].tolist()]
                
                # Desenha o retângulo do carro
                cv2.rectangle(imagem_bgr, (x1, y1), (x2, y2), (0, 255, 0), 3)
                # Adiciona o texto de confiança acima da caixa
                texto = f"Carro: {conf:.2f}"
                cv2.putText(imagem_bgr, texto, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Converte de volta para RGB para exibir corretamente no Streamlit
        imagem_resultado_rgb = cv2.cvtColor(imagem_bgr, cv2.COLOR_BGR2RGB)
        
    with col2:
        st.subheader("Resultado da Detecção")
        st.image(imagem_resultado_rgb, use_container_width=True)
        
    # Exibe o resumo do processamento
    if total_carros > 0:
        st.success(f"Sucesso! Encontramos **{total_carros}** carro(s) na imagem.")
    else:
        st.warning("Nenhum carro foi detectado nesta imagem com o limite atual de confiança.")