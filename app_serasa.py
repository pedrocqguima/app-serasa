""" App Serasa"""

import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import io

st.set_page_config(page_title="App Serasa", layout="centered")
st.title("🔍 Analisador de Alterações - Serasa Experian")

uploaded_file = st.file_uploader("📁 Envie o arquivo HTML", type="html")

# Função para encontrar a tabela correta com base nas colunas
def extract_table_from_html(html_string):
    soup = BeautifulSoup(html_string, "html.parser")
    try:
        tables = pd.read_html(str(soup))
        for table in tables:
            cols = [str(c).strip().upper() for c in table.columns]
            if "CNPJ" in cols and "RAZÃO SOCIAL" in cols and "ALTERAÇÃO" in cols:
                return table
        return None
    except Exception as e:
        return None

# Função para limpar e filtrar a tabela
def clean_and_filter_table(df):
    if not isinstance(df, pd.DataFrame) or df.empty:
        return None

    try:
        df.columns = [col.strip() for col in df.columns]
        df = df.applymap(lambda x: str(x).replace('\xa0', ' ').strip())
        df['Alteração'] = df['Alteração'].str.upper()
        filtro = df['Alteração'].isin([
            "INCLUSAO ANOT.INADIMPLENCIA",
            "INCL/EXCL ANOT.INADIMPLENCIA"
        ])
        return df[filtro].reset_index(drop=True)
    except Exception:
        return None

# Fluxo principal do app
if uploaded_file is not None:
    html_string = uploaded_file.read().decode("utf-8")
    extracted = extract_table_from_html(html_string)

    if extracted is None:
        st.error("❌ Nenhuma tabela com colunas 'CNPJ', 'Razão Social' e 'Alteração' foi encontrada.")
    else:
        df = clean_and_filter_table(extracted)

        if df is None or df.empty:
            st.warning("⚠️ Tabela encontrada, mas nenhuma linha corresponde ao filtro aplicado.")
        else:
            st.success("✅ Tabela extraída e filtrada com sucesso.")
            st.subheader("📄 Tabela Filtrada")
            st.dataframe(df, use_container_width=True)

            # Geração do arquivo Excel
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
