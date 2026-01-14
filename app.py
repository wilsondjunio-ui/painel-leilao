import streamlit as st
import pandas as pd
import os
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão Leilões", page_icon="🏢", layout="centered")

# --- CSS VISUAL (BRANCO + AZUL MARINHO + MENU CORRIGIDO) ---
hide_st_style = """
            <style>
            /* --- 1. ESCONDER ÍCONES DO CANTO SUPERIOR DIREITO --- */
            /* Esconde a barra de ferramentas (Deploy, Manage App, etc.) */
            [data-testid="stToolbar"] {
                visibility: hidden;
            }
            /* Esconde a linha colorida de decoração no topo */
            [data-testid="stDecoration"] {
                display: none;
            }
            /* Esconde rodapé */
            footer {
                visibility: hidden;
            }

            /* --- 2. MENU HAMBÚRGUER (☰) BRANCO --- */
            /* Deixa o cabeçalho transparente */
            header[data-testid="stHeader"] {
                background: transparent !important;
            }
            /* Pinta o ícone SVG do menu de BRANCO */
            [data-testid="stHeader"] button > div > svg {
                fill: #FFFFFF !important;
                stroke: #FFFFFF !important;
            }
            /* Garante que o texto do botão (se houver) seja branco */
            [data-testid="baseButton-header"] {
                color: #FFFFFF !important;
            }

            /* --- 3. FUNDO GERAL (AZUL MARINHO -> BRANCO) --- */
            .stApp {
                background: linear-gradient(180deg, #0A2342 0%, #FFFFFF 85%);
                background-attachment: fixed;
            }

            /* --- 4. CARTÕES DOS IMÓVEIS (AGORA BRANCOS) --- */
            [data-testid="stExpander"] {
                background-color: #FFFFFF !important; /* Branco Puro */
                border: 1px solid #E0E0E0 !important; /* Borda cinza suave */
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05); /* Sombra bem leve */
            }
            
            /* Título do cartão em Azul Escuro para combinar com o tema */
            .streamlit-expanderHeader {
                color: #0A2342 !important; 
                font-weight: bold;
            }
            
            /* Texto interno do cartão em cinza escuro */
            [data-testid="stExpander"] .stMarkdown {
                color: #333333;
            }

            /* --- 5. BARRA LATERAL --- */
            [data-testid="stSidebar"] {
                background-color: #F8F9FA;
                border-right: 1px solid #eee;
            }
            
            /* Títulos principais em branco (na área azul) */
            h1, h3.stSubheader {
                color: #FFFFFF !important;
                text-shadow: 0 1px 2px rgba(0,0,0,0.3);
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- CONEXÃO COM PLANILHA (COM ANTI-CACHE) ---
sheet_id = "1ke17ffjYUXwOf2gFLJorbWH46uY-EbEWCw0099iYaPI"
sheet_name = "Dados"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}&t={int(time.time())}"

# --- FUNÇÕES VISUAIS E LÓGICAS ---

def obter_icone(status):
    status = str(status).lower()
    if any(x in status for x in ['assinado', 'concluido', 'concluída', 'emitido', 'ok', 'pago', 'registrado', 'pronto', 'desocupado', 'livre']):
        return "✅"
    elif any(x in status for x in ['pendente', 'andamento', 'aguardando', 'fazer', 'processamento', 'analise', 'a pagar', 'ocupado']):
        return "📝"
    elif any(x in status for x in ['travado', 'problema', 'atenção', 'erro']):
        return "⚠️"
    elif status in ["nan", ""]:
        return "⚪"
    else:
        return "ℹ️"

def obter_cor_texto(texto):
    texto = str(texto).lower()
    if any(x in texto for x in ['ocupado', 'a pagar', 'pendente', 'atrasado']):
        return "red"
    if any(x in texto for x in ['desocupado', 'pago', 'em dia', 'ok']):
        return "green"
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
        if any(x in status for x in sucesso):
            pontos += peso
    return min(pontos, 100)

def gerar_barra_titulo(percent):
    tamanho_total = 10
    cheios = int(percent / 10) 
    vazios = tamanho_total - cheios
    bloco_cheio = "█" 
    bloco_vazio = "░"
    barra_texto = (bloco_cheio * cheios) + (bloco_vazio * vazios)
    return f":green[{barra_texto}]"

def barra_progresso_interna(percent):
    cor = "#09ab3b" 
    st.markdown(f"""
    <div style="width: 100%; background-color: #e0e0e0; border-radius: 5px; height: 10px; margin-bottom: 10px;">
        <div style="width: {percent}%; background-color: {cor}; height: 10px; border-radius: 5px;"></div>
    </div>
    """, unsafe_allow_html=True)

def mostrar_logo(width_val):
    try:
        if os.path.exists("logo.png"): st.image("logo.png", width=width_val)
    except: pass

# --- CARREGAMENTO DE DADOS ---
try:
    df = pd.read_csv(url, dtype=str).fillna("")
    df.columns = df.columns.str.strip()
except Exception as e:
    st.error(f"Erro ao conectar: {e}")
    st.stop()

# --- LOGIN ---
if 'logado' not in st.session_state:
    st.session_state['logado'] = False

if not st.session_state['logado']:
    mostrar_logo(200)
    st.markdown("<h3>🔐 Acesso ao Sistema</h3>", unsafe_allow_html=True)
    
    with st.container(border=True):
        cpf_input = st.text_input("CPF:", type="password")
        if st.button("Entrar", use_container_width=True):
            if cpf_input:
                cpf_limpo = ''.join(filter(str.isdigit, cpf_input))
                try:
                    df['Acesso_Autorizado'] = False
                    if 'CPFs_Acesso' in df.columns:
                        for index, row in df.iterrows():
                            celula_crua = str(row['CPFs_Acesso'])
                            celula_limpa = ''.join([c if c.isdigit() else ' ' for c in celula_crua])
                            lista_cpfs = celula_limpa.split()
                            if cpf_limpo in lista_cpfs:
                                df.at[index, 'Acesso_Autorizado'] = True
                        
                        cliente_df = df[df['Acesso_Autorizado'] == True]
                        
                        if not cliente_df.empty:
                            st.session_state['logado'] = True
                            st.session_state['dados_cliente'] = cliente_df
                            st.session_state['nome_investidor'] = cliente_df.iloc[0]['Investidor']
                            st.rerun()
                        else:
                            st.error("CPF não encontrado.")
                    else:
                        st.error("Erro na planilha: Coluna 'CPFs_Acesso' não encontrada.")
                except Exception as e:
                    st.error(f"Erro: {e}")
            else:
                st.warning("Digite o CPF.")

# --- PAINEL PRINCIPAL ---
else:
    nome = st.session_state['nome_investidor']
    meus_dados = st.session_state['dados_cliente']
    
    # --- BARRA LATERAL ---
    with st.sidebar:
        mostrar_logo(150)
        st.write("")
        if st.button("Sair", use_container_width=True):
            st.session_state['logado'] = False
            st.rerun()

    # --- ÁREA PRINCIPAL ---
    st.title("🏡 Meus Ativos")
    st.subheader(f"Olá, {nome} 👋")
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
