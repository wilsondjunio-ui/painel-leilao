import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão Leilões", page_icon="🏢", layout="centered")

# --- CONEXÃO DIRETA (SEM SENHA) ---
# Usamos o link de exportação CSV do Google Sheets
sheet_id = "1ke17ffjYUXwOf2gFLJorbWH46uY-EbEWCw0099iYaPI"
sheet_name = "Dados"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

try:
    # Lê direto do link, forçando CPF e ID a serem textos (para não perder zeros)
    df = pd.read_csv(url, dtype={'CPFs_Acesso': str, 'ID_Caixa': str})
    
except Exception as e:
    st.error(f"Erro ao conectar na planilha: {e}")
    st.stop()

# --- TELA DE LOGIN ---
if 'logado' not in st.session_state:
    st.session_state['logado'] = False

if not st.session_state['logado']:
    
    try:
        st.image("logo.png", width=200) 
    except:
        pass 

    st.markdown("<h1>🔐 Portal do Investidor</h1>", unsafe_allow_html=True)
    st.write("Digite seu CPF para acompanhar a regularização e venda.")
    
    with st.container(border=True):
        cpf_input = st.text_input("CPF (somente números):", type="password")
        entrar_btn = st.button("Acessar Painel", use_container_width=True)
    
    if entrar_btn:
        if cpf_input:
            # Limpa pontos e traços do CPF digitado, se houver
            cpf_limpo = cpf_input.replace(".", "").replace("-", "")
            
            try:
                # Verifica se o CPF existe na coluna (mesmo que esteja dentro de uma lista)
                filtro = df['CPFs_Acesso'].str.contains(cpf_limpo, na=False)
                cliente_df = df[filtro]
                
                if not cliente_df.empty:
                    st.session_state['logado'] = True
                    st.session_state['dados_cliente'] = cliente_df
                    st.session_state['nome_investidor'] = cliente_df.iloc[0]['Investidor']
                    st.rerun()
                else:
                    st.error("CPF não encontrado.")
            except KeyError:
                st.error("Erro: A coluna 'CPFs_Acesso' não foi encontrada na planilha. Verifique o nome na aba 'Dados'.")
        else:
            st.warning("Digite o CPF.")

# --- ÁREA LOGADA ---
else:
    nome = st.session_state['nome_investidor']
    meus_dados = st.session_state['dados_cliente']
    
    with st.sidebar:
        try:
            st.image("logo.png", width=150)
        except:
            pass
        st.header(f"Olá, {nome}")
        if st.button("Sair"):
            st.session_state['logado'] = False
            st.rerun()

    st.title("🏡 Meus Ativos")
    st.markdown("---")
    
    for index, row in meus_dados.iterrows():
        # Trata o progresso para garantir que seja número
        try:
            progresso = int(row['Progresso'])
        except:
            progresso = 0
            
        titulo_botao = f"{row['Imovel_Nome']} ({progresso}%)"
        
        with st.expander(titulo_botao, expanded=False):
            c_head1, c_head2 = st.columns([2, 2])
            c_head1.caption(f"🆔 ID Caixa: {row['ID_Caixa']}")
            
            valor = row.get('Valor_Imovel', 'R$ -')
            c_head2.markdown(f"💰 Valor: **:green[{valor}]**")
            
            st.progress(progresso, text="Status Geral")
            st.markdown("---")

            st.caption("1️⃣ Etapa de Aquisição e Legalização")
            c1, c2 = st.columns(2)
            
            icon_contrato = "✅" if "Assinado" in str(row['Status_Contrato']) else "⏳"
            c1.markdown(f"**Contrato:** {icon_contrato} {row['Status_Contrato']}")

            if str(row['Tipo_Compra']).lower().strip() == "vista":
                icon_esc = "✅" if "Concluída" in str(row['Status_Escritura']) else "📝"
                c1.markdown(f"**Escritura:** {icon_esc} {row['Status_Escritura']}")
            else:
                c1.markdown(f"**Escritura:** 🚫 *Financiado*")
            
            status_itbi = row['Status_ITBI']
            icon_itbi = "✅"
            if "Travado" in str(status_itbi) or "IPTU" in str(status_itbi):
                icon_itbi = "⚠️"
                st.warning(f"Pendência: {status_itbi}")
            elif "Pendente" in str(status_itbi):
                icon_itbi = "⏳"
            c2.markdown(f"**ITBI:** {icon_itbi} {status_itbi}")
            
            c2.markdown(f"**Registro:** {row['Status_Registro']}")
            st.info(f"**Situação Ocupação:** {row['Status_Ocupacao']}")

            st.markdown("---")

            st.caption("2️⃣ Etapa de Revenda (Pós-Venda)")
            col_venda1, col_venda2 = st.columns(2)
            col_venda1.markdown(f"**Engenharia:** {row['Status_Engenharia']}")
            
            status_venda = row['Status_Revenda']
            if status_venda == "Vendido":
                col_venda2.markdown(f"**Status:** 🎉 :green[{status_venda}]")
                st.balloons()
            else:
                col_venda2.markdown(f"**Status:** {status_venda}")
