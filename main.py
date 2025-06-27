import yfinance as yf
import pandas as pd
from datetime import datetime

# Ações para coletar
tickers = ['VALE3.SA', 'PETR4.SA', 'BRFS3.SA']
inicio = '2010-01-01'

# Data atual
fim = datetime.today().strftime('%Y-%m-%d')  

# Lista para guardar os dados individuais
lista_dfs = []

# Baixar os dados de cada ação SEPARADAMENTE
for ticker in tickers:
    print(f"Baixando dados de {ticker} até {fim}...")
    df = yf.Ticker(ticker).history(start=inicio, end=fim)
    
    # Verifica se tem dados
    if df.empty:
        continue

    df = df.reset_index()  # Coluna 'Date'
    df['Ticker'] = ticker  # Adiciona nome da ação
    df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Ticker']]  # Reorganiza colunas
    lista_dfs.append(df)

# Junta todos os dados
df_final = pd.concat(lista_dfs, ignore_index=True)

# Salvando em CSV
df_final.to_csv(r"G:\Meu Drive\AI_data_lab\Cursos_ml_AI\Fiap\Reinforcement Learning\Projeto_2_final\Agente_1_LLM\data\dados_acoes_tratado.csv", index=False)

# Mostra as colunas e primeiras linhas
print(df_final.columns)
print(df_final.head(10).to_string(index=False))
