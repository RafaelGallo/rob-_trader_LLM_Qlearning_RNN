#!pip install google-generativeai
#!pip install python-dotenv

import os
import re
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
from google.api_core.exceptions import ResourceExhausted
from google.generativeai.types import GenerationConfig

# Carregar dados já tratados
df = pd.read_csv(r'G:\Meu Drive\AI_data_lab\Cursos_ml_AI\Fiap\Reinforcement Learning\Projeto_2_final\Agente_1_LLM\input\dados_acoes_tratado_mineradoras2.csv')

# ===============================
# 🔐 Carregar chave da API Gemini
# ===============================
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

# Lista todos os modelos disponíveis
models = genai.list_models()

#print("Modelos disponíveis:")
#for m in models:
    #if "generateContent" in m.supported_generation_methods:
        #print(f"✅ {m.name}")

# Use o modelo correto
model = genai.GenerativeModel("models/gemini-2.0-flash-exp")        

# Teste de prompt
prompt_test = "Explique em uma frase simples o que é a bolsa de valores."
response1 = model.generate_content(prompt_test)

#print("📈 Resposta do Gemini:")
#print(response1.text)

# -------------------------------
# ⚙️ Modelo Gemini
# -------------------------------
model = genai.GenerativeModel("models/gemini-1.5-flash")

# -------------------------------
# 📄 Função para criar prompt
# -------------------------------
def criar_prompt_para_venda(df):
    prompt = """
Você é um agente financeiro especialista em ações.

Com base nos dados históricos abaixo (Open, Close, Volume), diga apenas quais ações devem ser VENDIDAS e justifique em 1 linha. Ignore as que devem ser mantidas ou compradas.

Formato:
Ticker: <ticker>
Decisão: VENDER
Justificativa: <motivo>

"""
    for ticker, grupo in df.groupby("Ticker"):
        prompt += f"\nTicker: {ticker}\n"
        for _, row in grupo.iterrows():
            prompt += (f"- {row['Date'].date()} | Open: {row['Open']:.2f} | "
                       f"Close: {row['Close']:.2f} | Volume: {int(row['Volume'])}\n")
    return prompt.strip()

# ========================
# 3. Enviar prompt para o Gemini
# ========================
def consultar_gemini(prompt):
    try:
        resposta = modelo.generate_content(prompt)
        return resposta.text
    except Exception as e:
        return f"Erro ao consultar Gemini: {e}"

# -------------------------------
# 📊 Exemplo de dados (últimos 5 dias simulados)
# -------------------------------
df = pd.read_csv(r"G:\Meu Drive\AI_data_lab\Cursos_ml_AI\Fiap\Reinforcement Learning\Projeto_2_final\Agente_1_LLM\input\dados_acoes_tratado.csv", parse_dates=["Date"])

# Filtrar os últimos 5 dias de cada ação
df_ultimos = df.sort_values("Date").groupby("Ticker").tail(500)

# -------------------------------
# 📤 Enviar prompt para Gemini
# -------------------------------
prompt = criar_prompt_para_venda(df_ultimos)
print("📨 Prompt enviado ao Gemini:\n")
print(prompt)

resposta = model.generate_content(prompt)
print("\n📈 Resposta Agente:\n")
print(resposta.text)

# Salvando relatorio 

# -------------------------------
# 🧾 Resposta do LLM (exibida e salva)
# -------------------------------
resposta_texto = resposta.text

# Exibir no console
print("\n📈 Resposta do Gemini:\n")
print(resposta_texto)

# Salvar em TXT para documentação
with open("G:\Meu Drive\AI_data_lab\Cursos_ml_AI\Fiap\Reinforcement Learning\Projeto_2_final\Agente_1_LLM\output\decisoes_venda_llm2.txt", "w", encoding="utf-8") as f:
    f.write(resposta_texto)

# Agente 2 salvando csv

# Exemplo: resposta.text vindo do Gemini
resposta_llm = resposta.text

# Função para extrair VENDER do prompt
def extrair_decisoes_venda(texto):
    padrao = r"Ticker:\s*(\w+\.\w+)\s*Decisão:\s*VENDER\s*Justificativa:\s*(.*)"
    correspondencias = re.findall(padrao, texto, re.IGNORECASE)

    df = pd.DataFrame(correspondencias, columns=["Ticker", "Justificativa"])
    df["Decisao"] = "VENDER"
    return df

# Criar DataFrame das vendas
df_vendas = extrair_decisoes_venda(resposta_llm)

# Exibir
print("\n📋 Decisões de VENDA encontradas pelo LLM:\n")
print(df_vendas)

# Salvar CSV
caminho_saida = "G:\Meu Drive\AI_data_lab\Cursos_ml_AI\Fiap\Reinforcement Learning\Projeto_2_final\Agente_1_LLM\output\decisoes_venda_llm.csv"
df_vendas.to_csv(caminho_saida, index=False)
print(f"\n✅ CSV salvo em: {caminho_saida}")

# Simulação de venda (extra opcional)

def extrair_tickers_para_venda(resposta_texto):
    linhas = resposta_texto.splitlines()
    acoes_para_vender = []

    for i in range(len(linhas)):
        if linhas[i].startswith("Ticker:") and "VENDER" in linhas[i + 1]:
            ticker = linhas[i].split(":")[1].strip()
            acoes_para_vender.append(ticker)
    
    return acoes_para_vender

# Simular portfólio
tickers_a_vender = extrair_tickers_para_venda(resposta_texto)
print(f"\n📉 Ações que o agente decidiu VENDER: {tickers_a_vender}")

# Substituir pelo seu DataFrame real
df_final = df.copy()  # Certifique-se que df existe com as colunas ['Ticker', 'Date', 'Close']

# Tickers recomendados para VENDER pelo agente LLM
tickers_vender = ['VALE3.SA', 'PETR4.SA', 'BRFS3.SA']

# Conversão da coluna de datas
#df_final['Date'] = pd.to_datetime(df_final['Date'])

# Criação do gráfico
fig = go.Figure()

for ticker in tickers_vender:
    df_ticker = df_final[df_final['Ticker'] == ticker]

    fig.add_trace(go.Scatter(
        x=df_ticker['Date'],
        y=df_ticker['Close'],
        mode='lines',
        name=f"{ticker} - Fechamento"
    ))

    ultimos_pontos = df_ticker.tail(5)

    fig.add_trace(go.Scatter(
        x=ultimos_pontos['Date'],
        y=ultimos_pontos['Close'],
        mode='markers+text',
        name=f"{ticker} - VENDER",
        marker=dict(color='red', size=10, symbol='x'),
        text=['VENDER'] * len(ultimos_pontos),
        textposition='top center',
        showlegend=False
    ))

fig.update_layout(
    title='📉 Decisões de VENDA do Agente LLM para Ações',
    xaxis_title='Data',
    yaxis_title='Preço de Fechamento (R$)',
    template='plotly_white',
    hovermode='x unified',
    height=600
)

fig.show()

# Simulação de um DataFrame com dados históricos de ações para até 100 tickers
# Neste exemplo, usaremos apenas 3 para simplificação
data = {
    'Ticker': ['VALE3.SA'] * 5 + ['PETR4.SA'] * 5 + ['BRFS3.SA'] * 5,
    'Date': pd.date_range(start='2025-06-01', periods=5).tolist() * 3,
    'Open': [50.0, 49.5, 49.2, 49.8, 49.0, 30.0, 29.8, 30.1, 30.3, 29.9, 20.5, 20.7, 20.8, 20.6, 20.4],
    'Close': [49.0, 48.7, 48.5, 48.8, 48.3, 29.5, 29.2, 29.0, 28.9, 28.7, 20.3, 20.2, 20.0, 19.8, 19.7],
    'Volume': [20000000]*5 + [15000000]*5 + [10000000]*5
}
df_final = pd.DataFrame(data)

# Tickers que o agente decidiu vender
tickers_vender = ['VALE3.SA', 'PETR4.SA', 'BRFS3.SA']

# Processar datas
df_final['Date'] = pd.to_datetime(df_final['Date'])

# Criar figura
fig = go.Figure()

# Paleta de cores personalizada
cores = {
    'VALE3.SA': 'royalblue',
    'PETR4.SA': 'mediumseagreen',
    'BRFS3.SA': 'darkorange'
}

# Iterar pelos tickers
for ticker in tickers_vender:
    df_ticker = df[df['Ticker'] == ticker]

    # Plotar linha do fechamento
    fig.add_trace(go.Scatter(
        x=df_ticker['Date'],
        y=df_ticker['Close'],
        mode='lines',
        name=f"{ticker} - Fechamento",
        line=dict(color=cores[ticker], width=2)
    ))

    # Último ponto como recomendação de venda
    ponto_venda = df_ticker.tail(1)

    fig.add_trace(go.Scatter(
        x=ponto_venda['Date'],
        y=ponto_venda['Close'],
        mode='markers+text',
        name=f"{ticker} - VENDER",
        marker=dict(color='red', size=12, symbol='x'),
        text=["💸 VENDER"],
        textfont=dict(size=14, color='red'),
        textposition='bottom center',
        showlegend=False
    ))

# Layout refinado
fig.update_layout(
    title='📉 Recomendação de VENDA do Agente LLM',
    title_font_size=22,
    xaxis_title='Data',
    yaxis_title='Preço de Fechamento (R$)',
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor='lightgrey'),
    template='plotly_white',
    hovermode='x unified',
    legend=dict(orientation='h', y=-0.2),
    height=600
)

fig.show()

