import streamlit as st
import requests
from datetime import datetime
import re

API_KEY = "06899b3d545c3d892ea50f9bca82a71e"

def geocode(cidade):
    url = f"https://api.openweathermap.org/geo/1.0/direct?q={cidade}&appid={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]['lat'], data[0]['lon']
    return None, None

def get_forecast(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&lang=pt_br&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def get_time():
    agora = datetime.now().strftime("%H:%M:%S")
    return f"🕒 Agora são {agora}"

def get_cep(cep):
    url = f"https://viacep.com.br/ws/{cep}/json/"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "erro" not in data:
            return f"📍 {data['logradouro']}, {data['bairro']}, {data['localidade']}-{data['uf']}"
        else:
            return "❌ CEP não encontrado."
    return "Erro ao consultar o CEP."

st.set_page_config(page_title="ChatBot", page_icon="🤖", layout="centered")
st.title("🤖 ChatBot")

st.markdown("""
    <style>
    .mensagem-user {
        text-align: right;
        background-color: #7a7a7a;
        padding: 8px 12px;
        border-radius: 12px;
        margin: 8px 0 8px 40px;
        font-size: 16px;
    }
    .mensagem-bot {
        text-align: left;
        background-color: #7a7a7a ;
        padding: 8px 12px;
        border-radius: 12px;
        margin: 8px 40px 8px 0;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

pergunta = st.chat_input("Digite sua pergunta...")

if pergunta:
    st.session_state.messages.append(("user", pergunta))
    resposta = None

    # Extrair o CEP
    match_cep = re.search(r"(\d{5}-?\d{3})", pergunta)
    if match_cep:
        cep = match_cep.group(1).replace("-", "")
        resposta = get_cep(cep)

    elif "hora" in pergunta.lower():
        resposta = get_time()

    elif "clima" in pergunta.lower() or "tempo" in pergunta.lower():
        # Extrai cidade e estado, se informado 
        match = re.search(r"(?:clima|tempo) em ([\w\s]+?)(?:,\s*([a-z]{2}))?$", pergunta.lower())
        if match:
            cidade = match.group(1).strip()
            estado = match.group(2).strip() if match.group(2) else ""
        else:
            cidade = None
            estado = ""

        if cidade:
            # Monta o local para a API (cidade,estado,br ou cidade,br)
            local = f"{cidade},{estado},br" if estado else f"{cidade},br"
            lat, lon = geocode(local)
            if lat and lon:
                data = get_forecast(lat, lon)
                if data:
                    temp = data["main"]["temp"]
                    desc = data["weather"][0]["description"]
                    resposta = f"🌤️ O clima em {cidade.title()} {estado.upper()} está {desc} com {temp:.1f}°C"
                else:
                    resposta = "❌ Não consegui obter os dados do clima."
            else:
                resposta = "❌ Cidade não encontrada."
        else:
            resposta = "Por favor, informe a cidade. Exemplo: clima em Recife, PE"

    if resposta is None:
        resposta = "❓ Não entendi. Pergunte sobre clima, hora ou CEP."

    st.session_state.messages.append(("bot", resposta))

for role, msg in st.session_state.messages:
    if role == "user":
        st.markdown(f"<div class='mensagem-user'><b>Você:</b> {msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='mensagem-bot'><b>Bot:</b> {msg}</div>", unsafe_allow_html=True)