import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Gestão Leilões", page_icon="🏢", layout="centered")

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Tenta conectar na aba "Página1"
    df = conn.read(worksheet="Página1", ttl=5)
    df['CPFs_Acesso'] = df['CPFs_Acesso'].astype(str)
    df['ID_Caixa'] = df['ID_Caixa'].astype(str)
except Exception as e:
    # AQUI É O PULO DO GATO: Mostra o erro real na tela
    st.error(f"⚠️ O ERRO REAL É: {e}")
    st.info("Copie esse erro acima e mande no chat.")
    st.stop()

# --- SE CHEGOU AQUI, CONECTOU! ---
if 'logado' not in st.session_state:
    st.session_state['logado'] = False

if not st.session_state['logado']:
    st.title("🔐 Login")
    with st.container(border=True):
        cpf_input = st.text_input("CPF:", type="password")
        if st.button("Entrar"):
            # Busca o CPF na planilha
            try:
                filtro = df['CPFs_Acesso'].str.contains(cpf_input, na=False)
                cliente_df = df[filtro]
                if not cliente_df.empty:
                    st.session_state['logado'] = True
                    st.session_state['dados_cliente'] = cliente_df
                    st.rerun()
                else:
                    st.error("CPF não encontrado.")
            except KeyError:
                st.error("Erro: Coluna 'CPFs_Acesso' não encontrada na planilha.")

else:
    # Painel Principal
    meus_dados = st.session_state['dados_cliente']
    if st.button("Sair"):
        st.session_state['logado'] = False
        st.rerun()
    
    st.title("🏡 Meus Imóveis")
    for index, row in meus_dados.iterrows():
        with st.expander(f"{row['Imovel_Nome']}", expanded=False):
            st.write(f"**ID:** {row['ID_Caixa']}")
            st.write(f"**Status:** {row.get('Status_Contrato', 'N/A')}")
