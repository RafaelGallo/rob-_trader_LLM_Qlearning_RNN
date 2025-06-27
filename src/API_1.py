import yfinance as yf
import pandas as pd
from datetime import datetime
import os

# Lista completa de empresas
tickers = ['VALE3.SA', 'PETR4.SA', 'BRFS3.SA',
           'CMIN3.SA', 'PRIO3.SA', 'RRRP3.SA', 
           'ELET3.SA', 'EGIE3.SA', 'CSAN3.SA', 
           'GGBR4.SA', 'SLCE3.SA', 'XOM', 
           'CVX', 'SHEL', 'BHP', 
           'RIO']

#
inicio = '2005-01-01'
fim = datetime.today().strftime('%Y-%m-%d')

#
output_dirs = [r"G:\Meu Drive\AI_data_lab\Cursos_ml_AI\Fiap\Reinforcement Learning\Projeto_2_final\Agente_1_LLM\input"]

# Criar pastas se não existirem
for path in output_dirs:
    os.makedirs(path, exist_ok=True)

#
lista_dfs = []

#
for ticker in tickers:
    print(f"--> Baixando dados de: {ticker}")
    df = yf.Ticker(ticker).history(start=inicio, end=fim)
    if df.empty:
        print(f"! Nenhum dado encontrado para {ticker}. Pulando.")
        continue
    df.reset_index(inplace=True)
    df['Ticker'] = ticker
    df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Ticker']]
    lista_dfs.append(df)

# Salvar o resultado final
if lista_dfs:
    df_final = pd.concat(lista_dfs, ignore_index=True)
    for path in output_dirs:
        filename = os.path.join(path, "dados_acoes_tratado_mineradoras2.csv")
        df_final.to_csv(filename, index=False)
    print(f"\n-> Dados salvos com sucesso! Total de linhas: {len(df_final)}")
    print(df_final.head())
else:
    print("! Nenhum dado foi baixado. Verifique os tickers ou a conexão.")