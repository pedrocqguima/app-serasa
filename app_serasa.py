""" App Serasa"""

import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import io

## Colando / fazendo upload do arquivo

st.title("Gerencie Carteira - Serasa")

st.subheader("Cole aqui o conteúdo HTML coma a tabela:")
html_text = st.text_area("HTML Copiado", height=300)

st.subheader("... ou faça o upload do arquivo HTML:")
uploaded_file = st.file_uploader("Escolha um arquivo HTML", type="html")


## Limpar o HTML e extrair a tabela

def extract_table_from_html(html_string):
    soup = BeautifulSoup(html_string, "html.parser")
    tables = pd.read_html(str(soup))
    if tables:
        return tables[0]
    else:
        return None

def clean_and_filter_table(df):
    # Remove espaços e caracteres especiais das colunas
    df.columns = [col.strip() for col in df.columns]

    # Remove espaços dentro das células
    df = df.applymap(lambda x: str(x).replace('\xa0', ' ').strip())

    # Padroniza para maiúsculas
    df['Alteração'] = df['Alteração'].str.upper()

    # Mantém apenas linhas com as palavras-chave desejadas
    filtro = df['Alteração'].isin([
        "INCLUSAO  ANOT.INADIMPLENCIA",
        "INCL/EXCL ANOT.INADIMPLENCIA"
    ])
    df_filtrado = df[filtro].reset_index(drop=True)

    return df_filtrado


## Inicializa o DataFrame vazio
df = None


## Verificar se o HTML foi colado manualmente

if html_text:
    df = extract_table_from_html(html_text)
    if df is not None:
        df = clean_and_filter_table(df)
        st.subheader("Tabela filtrada:")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Nenhuma tabela foi encontrada no conteúdo colado.")
        
## Caso o usuário tenha feito o upload do arquivo

elif uploaded_file is not None:
    html_string = uploaded_file.read().decode("utf-8")
    df = extract_table_from_html(html_string)
    if df is not None:
        df = clean_and_filter_table(df)
        st.subheader("Tabela filtrada:")
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Nenhuma tabela foi encontrada no arquivo enviado.")
        

# Se o DataFrame existe, mostrar botão de download
if df is not None and not df.empty:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Filtrado')
    output.seek(0)

    st.download_button(
        label="📥 Baixar tabela filtrada em Excel",
        data=output,
        file_name="tabela_filtrada.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    )
