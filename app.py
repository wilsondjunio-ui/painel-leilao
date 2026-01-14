import streamlit as st
import pandas as pd
import os
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão Leilões", page_icon="🏢", layout="centered")

# --- CONEXÃO COM PLANILHA (COM ANTI-CACHE) ---
sheet_id = "1ke17ffjYUXwOf2gFLJorbWH46uY-EbEWCw0099iYaPI"
sheet_name = "Dados"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}&t={int(time.time())}"

# --- FUNÇÕES VISUAIS ---
def obter_icone(status):
    status = str(status).lower()
    if any(x in status for x in ['assinado', 'concluido', 'concluída', 'emitido', 'ok', 'pago', 'registrado', 'pronto', 'desocupado', 'livre']): return "✅"
    elif any(x in status for x in ['pendente', 'andamento', 'aguardando', 'fazer', 'processamento', 'analise', 'a pagar', 'ocupado']): return "📝"
    elif any(x in status for x in ['travado', 'problema', 'atenção', 'erro']): return "⚠️"
    elif status in ["nan", ""]: return "⚪"
    else: return "ℹ️"

def obter_cor_texto(texto):
    texto = str(texto).lower()
    if any(x in texto for x in ['ocupado', 'a pagar', 'pendente', 'atrasado']): return "red"
    if any(x in texto for x in ['desocupado', 'pago', 'em dia', 'ok']): return "green"
    return "black"

def calcular_progresso_inteligente(row):
    tipo_compra = str(row.get('Tipo_Compra', '')).lower()
    if 'financiado' in tipo_compra:
        etapas = ['Status_Contrato', 'Status_ITBI', 'Status_Registro', 'Status_Cadastro']
        peso = 25
    else:
        etapas = ['Status_Contrato', 'Status_ITBI', 'Status_Escritura', 'Status_Registro', 'Status_Cadastro']
        peso = 20
    pontos = 0
    sucesso = ['assinado', 'concluido', 'concluída', 'emitido', 'ok', 'pago', 'registrado', 'pronto']
    for etapa in etapas:
        status = str(row.get(etapa, '')).lower()
        if any(x in status for x in sucesso): pontos += peso
    return min(pontos, 100)

def gerar_barra_titulo(percent):
    tamanho = 10
    cheios = int(percent / 10) 
    barra = ("█" * cheios) + ("░" * (tamanho - cheios))
    return f":green[{barra}]"

def barra_progresso_interna(percent):
    st.markdown(f"""<div style="width:100%;background-color:#e0e0e0;border-radius:5px;height:10px;margin-bottom:10px;"><div style="width:{percent}%;background-color:#09ab3b;height:10px;border-radius:5px;"></div></div>""", unsafe_allow_html=True)

def mostrar_logo(w):
    try:
        if os.path.exists("logo.png"): st.image("logo.png", width=w)
    except: pass

# --- CARREGAMENTO DE DADOS ---
try:
    # Lê a planilha crua
    df = pd.read_csv(url, dtype=str).fillna("")
    # Limpa nomes das colunas (remove espaços nas bordas)
    df.columns = df.columns.str.strip()
    
except Exception as e:
    st.error(f"Erro fatal na conexão: {e}")
    st.stop()

# --- LOGIN ---
if 'logado' not in st.session_state:
    st.session_state['logado'] = False

if not st.session_state['logado']:
    mostrar_logo(200)
    st.markdown("<h3>🔐 Acesso ao Sistema</h3>", unsafe_allow_html=True)
    
    with st.container(border=True):
        cpf_input = st.text_input("CPF:", type="password")
        entrar = st.button("Entrar", use_container_width=True)

        if entrar:
            if cpf_input:
                # 1. Limpa o que foi digitado (Deixa só números)
                cpf_limpo = ''.join(filter(str.isdigit, cpf_input))
                
                try:
                    # 2. LÓGICA DE BUSCA MANUAL (Mais segura)
                    # Vamos olhar linha por linha para ver se o CPF está lá dentro
                    df['Acesso_Liberado'] = False
                    
                    if 'CPFs_Acesso' in df.columns:
                        for index, row in df.iterrows():
                            # Pega o conteúdo da célula na planilha e limpa (tira pontos, traços, espaços)
                            celula_crua = str(row['CPFs_Acesso'])
                            celula_limpa = ''.join(filter(str.isdigit, celula_crua))
                            
                            # Verifica: O CPF digitado está dentro dessa tripa de números?
                            if cpf_limpo in celula_limpa and cpf_limpo != "":
                                df.at[index, 'Acesso_Liberado'] = True
                        
                        # Filtra apenas quem teve acesso liberado
                        cliente_df = df[df['Acesso_Liberado'] == True]
                        
                        if not cliente_df.empty:
                            st.session_state['logado'] = True
                            st.session_state['dados_cliente'] = cliente_df
                            st.session_state['nome_investidor'] = cliente_df.iloc[0]['Investidor']
                            st.rerun()
                        else:
                            st.error(f"CPF {cpf_limpo} não encontrado na lista.")
                    else:
                        st.error("ERRO: Coluna 'CPFs_Acesso' não encontrada na planilha.")
                        
                except Exception as e:
                    st.error(f"Erro técnico: {e}")
            else:
                st.warning("Digite o CPF.")

    # --- ÁREA DE DIAGNÓSTICO (O ESPIÃO) ---
    st.markdown("---")
    with st.expander("🕵️‍♂️ ÁREA TÉCNICA (Se der erro, abra aqui)"):
        st.write("Verifique abaixo se a coluna 'CPFs_Acesso' existe e como os dados estão chegando:")
        st.dataframe(df.head())
        st.write(f"**Colunas detectadas:** {list(df.columns)}")

# --- PAINEL PRINCIPAL ---
else:
    nome = st.session_state['nome_investidor']
    meus_dados = st.session_state['dados_cliente']
    
    with st.sidebar:
        mostrar_logo(150)
        st.write(f"Olá, **{nome}**")
        if st.button("Sair"):
            st.session_state['logado'] = False
            st.rerun()

    st.title("🏡 Meus Ativos")
    st.markdown("---")
    
    for index, row in meus_dados.iterrows():
        progresso = calcular_progresso_inteligente(row)
        barra_visual = gerar_barra_titulo(progresso)
        titulo_card = f"{row['Imovel_Nome']}⠀{barra_visual}⠀{progresso}%"
        
        with st.expander(titulo_card, expanded=False):
            barra_progresso_interna(progresso)
            c1, c2 = st.columns(2)
            c1.caption(f"🆔 ID: {row['ID_Caixa']}")
            c1.caption(f"📍 Tipo: {row.get('Tipo_Imovel', '-')}")
            c2.markdown(f"💰 Valor: **:green[{row['Valor_Imovel']}]**")
            st.divider()

            st.markdown("##### 🚦 Status de Regularização")
            r1, r2, r3 = st.columns(3)
            ocup = row.get('Status_Ocupacao', '-')
            r1.markdown(f"**Ocupação:** :{obter_cor_texto(ocup)}[{ocup}]")
            iptu = row.get('Debito_IPTU', '-')
            r2.markdown(f"**IPTU:** :{obter_cor_texto(iptu)}[{iptu}]")
            if 'casa' not in str(row.get('Tipo_Imovel', '')).lower():
                cond = row.get('Debito_Condominio', '-')
                r3.markdown(f"**Condomínio:** :{obter_cor_texto(cond)}[{cond}]")
            
            st.divider()
            st.markdown("##### 📝 Etapas Documentais")
            tipo_compra = str(row.get('Tipo_Compra', '')).lower()
            fluxo = [("Contrato", "Status_Contrato", "Link_Contrato", "Nota_Contrato"), ("ITBI", "Status_ITBI", "Link_ITBI", "Nota_ITBI")]
            if 'financiado' not in tipo_compra: fluxo.append(("Escritura", "Status_Escritura", "Link_Escritura", "Nota_Escritura"))
            fluxo.append(("Registro", "Status_Registro", "Link_Registro", "Nota_Registro"))
            fluxo.append(("Cad. Imobiliário", "Status_Cadastro", "Link_Cadastro", "Nota_Cadastro"))
            
            for i in range(0, len(fluxo), 2):
                cols = st.columns(2)
                for j, item in enumerate(fluxo[i:i+2]):
                    lbl, stt, lnk, nt = item
                    with cols[j]:
                        txt = row.get(stt, '')
                        st.markdown(f"**{lbl}**"); st.write(f"{obter_icone(txt)} {txt}")
                        l, n = st.columns([1,4])
                        lk = str(row.get(lnk, '')).strip()
                        if lk and "http" in lk: l.link_button("📂", lk)
                        nt_txt = str(row.get(nt, '')).strip()
                        if nt_txt: n.popover("Obs").write(nt_txt)
                        st.write("")
            st.divider()
            st.caption("Fase Final")
            f1, f2 = st.columns(2)
            f1.info(f"Engenharia: {row.get('Status_Engenharia', '-')}")
            rv = str(row.get('Status_Revenda', '-'))
            if "vendido" in rv.lower(): f2.success(f"Revenda: {rv}")
            else: f2.warning(f"Revenda: {rv}")
