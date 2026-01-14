import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão Leilões", page_icon="🏢", layout="centered")

# --- CONEXÃO COM A PLANILHA ---
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Lê a planilha e garante que CPFs e IDs sejam lidos como texto
    df = conn.read(worksheet="Página1", ttl=5)
    df['CPFs_Acesso'] = df['CPFs_Acesso'].astype(str)
    df['ID_Caixa'] = df['ID_Caixa'].astype(str)
except Exception as e:
    st.error("Erro ao conectar. Verifique se a planilha está compartilhada com o robô e se os nomes das colunas estão exatos.")
    st.stop()

# --- TELA DE LOGIN ---
if 'logado' not in st.session_state:
    st.session_state['logado'] = False

if not st.session_state['logado']:
    
    # Tenta mostrar a logo
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
            # Verifica se o CPF digitado existe dentro da célula (para grupos)
            filtro = df['CPFs_Acesso'].str.contains(cpf_input, na=False)
            cliente_df = df[filtro]
            
            if not cliente_df.empty:
                st.session_state['logado'] = True
                st.session_state['dados_cliente'] = cliente_df
                # Pega o nome do investidor da primeira linha encontrada
                st.session_state['nome_investidor'] = cliente_df.iloc[0]['Investidor']
                st.rerun()
            else:
                st.error("CPF não encontrado ou sem permissão.")
        else:
            st.warning("Digite o CPF.")

# --- ÁREA LOGADA (O PAINEL) ---
else:
    nome = st.session_state['nome_investidor']
    meus_dados = st.session_state['dados_cliente']
    
    # Barra Lateral
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
    
    # Loop para gerar a lista de imóveis
    for index, row in meus_dados.iterrows():
        
        # Define o título do botão (Nome + Progresso)
        progresso = int(row['Progresso']) if pd.notnull(row['Progresso']) else 0
        titulo_botao = f"{row['Imovel_Nome']} ({progresso}%)"
        
        # --- LISTA SANFONA (EXPANDER) ---
        with st.expander(titulo_botao, expanded=False):
            
            # Cabeçalho Interno: ID e Valor
            c_head1, c_head2 = st.columns([2, 2])
            c_head1.caption(f"🆔 ID Caixa: {row['ID_Caixa']}")
            
            valor = row.get('Valor_Imovel', 'R$ -')
            c_head2.markdown(f"💰 Valor: **:green[{valor}]**")
            
            # Barra de Progresso
            cor_barra = "green" if progresso == 100 else "blue"
            st.progress(progresso, text="Status Geral")
            
            st.markdown("---")

            # --- FASE 1: AQUISIÇÃO ---
            st.caption("1️⃣ Etapa de Aquisição e Legalização")
            c1, c2 = st.columns(2)
            
            # Contrato
            icon_contrato = "✅" if "Assinado" in str(row['Status_Contrato']) else "⏳"
            c1.markdown(f"**Contrato:** {icon_contrato} {row['Status_Contrato']}")

            # Escritura (Esconde se for Financiado)
            if str(row['Tipo_Compra']).lower().strip() == "vista":
                icon_esc = "✅" if "Concluída" in str(row['Status_Escritura']) else "📝"
                c1.markdown(f"**Escritura:** {icon_esc} {row['Status_Escritura']}")
            else:
                c1.markdown(f"**Escritura:** 🚫 *Financiado*")
            
            # ITBI (Alerta se tiver problema)
            status_itbi = row['Status_ITBI']
            icon_itbi = "✅"
            if "Travado" in str(status_itbi) or "IPTU" in str(status_itbi):
                icon_itbi = "⚠️"
                st.warning(f"Pendência: {status_itbi}")
            elif "Pendente" in str(status_itbi):
                icon_itbi = "⏳"
            c2.markdown(f"**ITBI:** {icon_itbi} {status_itbi}")
            
            # Registro
            c2.markdown(f"**Registro:** {row['Status_Registro']}")
            
            # Ocupação
            st.info(f"**Situação Ocupação:** {row['Status_Ocupacao']}")

            st.markdown("---")

            # --- FASE 2: REVENDA ---
            st.caption("2️⃣ Etapa de Revenda (Pós-Venda)")
            col_venda1, col_venda2 = st.columns(2)
            col_venda1.markdown(f"**Engenharia:** {row['Status_Engenharia']}")
            
            status_venda = row['Status_Revenda']
            if status_venda == "Vendido":
                col_venda2.markdown(f"**Status:** 🎉 :green[{status_venda}]")
                st.balloons()
            else:
                col_venda2.markdown(f"**Status:** {status_venda}")