""" App Serasa"""

import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import io

st.set_page_config(page_title="App Serasa", layout="centered")
st.title("🔍 Analisador de Alterações - Serasa Experian")

# Upload do arquivo HTML
uploaded_file = st.file_uploader("📁 Envie o arquivo HTML", type="html")

# Função para extrair a tabela
def extract_table_from_html(html_string):
    soup = BeautifulSoup(html_string, "html.parser")
    try:
        tables = pd.read_html(str(soup))  # Usa lxml ou html5lib
        return tables[0] if tables else None
    except Exception as e:
        st.error(f"Erro ao processar o HTML: {e}")
        return None

# Função para limpar e filtrar
def clean_and_filter_table(df):
    df.columns = [col.strip() for col in df.columns]
    df = df.applymap(lambda x: str(x).replace('\xa0', ' ').strip())
    df['Alteração'] = df['Alteração'].str.upper()
    filtro = df['Alteração'].isin([
        "INCLUSAO  ANOT.INADIMPLENCIA",
        "INCL/EXCL ANOT.INADIMPLENCIA"
    ])
    return df[filtro].reset_index(drop=True)

# Fluxo principal
if uploaded_file is not None:
    html_string = uploaded_file.read().decode("utf-8")
    extracted = extract_table_from_html(html_string)
    
    if extracted is not None:
        df = clean_and_filter_table(extracted)
        if not df.empty:
            st.success("✅ Tabela extraída e filtrada com sucesso.")
            st.subheader("📄 Tabela Filtrada")
            st.dataframe(df, use_container_width=True)

            # Geração do Excel para download
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Filtrado")
            output.seek(0)

            st.download_button(
                label="📥 Baixar tabela filtrada (Excel)",
                data=output,
                file_name="tabela_filtrada.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("⚠️ Nenhuma linha válida encontrada após o filtro.")
    else:
        st.warning("⚠️ Nenhuma tabela válida foi encontrada no HTML enviado.")
