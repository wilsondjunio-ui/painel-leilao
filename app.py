import streamlit as st
import pandas as pd
import os
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão Leilões", page_icon="🏢", layout="centered")

# --- ESCONDER MENU, CABEÇALHO E RODAPÉ (VISUAL LIMPO) ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
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
                # Limpa o input (deixa só numeros)
                cpf_limpo = ''.join(filter(str.isdigit, cpf_input))
                
                try:
                    df['Acesso_Autorizado'] = False
                    
                    if 'CPFs_Acesso' in df.columns:
                        for index, row in df.iterrows():
                            # Pega o conteúdo da célula
                            celula_crua = str(row['CPFs_Acesso'])
                            # Troca tudo que não for número por espaço
                            celula_limpa = ''.join([c if c.isdigit() else ' ' for c in celula_crua])
                            # Cria lista de CPFs daquela célula
                            lista_cpfs = celula_limpa.split()
                            
                            # Verifica se o CPF digitado está na lista
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
    
    # --- BARRA LATERAL (Apenas Logo e Sair) ---
    with st.sidebar:
        mostrar_logo(150)
        st.write("") 
        if st.button("Sair"):
            st.session_state['logado'] = False
            st.rerun()

    # --- ÁREA PRINCIPAL ---
    
    # 1. NOME NO TOPO ESQUERDO
    st.subheader(f"Olá, {nome}")
    
    # 2. TÍTULO ABAIXO
    st.title("🏡 Meus Imoveis")
    
    st.markdown("---")
    
    for index, row in meus_dados.iterrows():
        progresso = calcular_progresso_inteligente(row)
        barra_visual = gerar_barra_titulo(progresso)
        titulo_card = f"{row['Imovel_Nome']}⠀{barra_visual}⠀{progresso}%"
        
        with st.expander(titulo_card, expanded=False):
            barra_progresso_interna(progresso)
            c1, c2 = st.columns(2)
            c1.caption
