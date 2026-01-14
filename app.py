import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão Leilões", page_icon="🏢", layout="centered")

# --- CONEXÃO DIRETA (SEM SENHA) ---
sheet_id = "1ke17ffjYUXwOf2gFLJorbWH46uY-EbEWCw0099iYaPI"
sheet_name = "Dados"
# Adicionei 'gid' para garantir a aba certa e cache busting simples
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

# --- FUNÇÕES AUXILIARES (A MÁGICA) ---

def obter_icone(status):
    """Define o ícone baseado no texto do status"""
    status = str(status).lower()
    if any(x in status for in ['assinado', 'concluido', 'concluída', 'emitido', 'ok', 'pago', 'registrado', 'pronto']):
        return "✅"
    elif any(x in status for in ['pendente', 'andamento', 'aguardando', 'fazer', 'processamento', 'analise']):
        return "📝"
    elif any(x in status for in ['travado', 'problema', 'atenção', 'erro']):
        return "⚠️"
    elif status == "nan" or status == "":
        return "⚪"
    else:
        return "ℹ️"

def calcular_progresso_auto(row):
    """Calcula % baseado nas 5 etapas principais (20% cada)"""
    etapas = ['Status_Contrato', 'Status_ITBI', 'Status_Escritura', 'Status_Registro', 'Status_Ficha']
    pontos = 0
    
    for etapa in etapas:
        status = str(row.get(etapa, '')).lower()
        # Se tiver palavras chave positivas, ganha 20 pontos
        if any(x in status for in ['assinado', 'concluido', 'concluída', 'emitido', 'ok', 'pago', 'registrado', 'pronto']):
            pontos += 20
            
    return min(pontos, 100) # Garante que não passa de 100

def barra_progresso_colorida(percent):
    """Cria uma barra HTML com cor dinâmica"""
    if percent < 40:
        cor = "#ff4b4b" # Vermelho
    elif percent < 80:
        cor = "#ffa421" # Amarelo/Laranja
    else:
        cor = "#09ab3b" # Verde
        
    st.markdown(f"""
    <div style="width: 100%; background-color: #f0f2f6; border-radius: 10px; height: 20px;">
        <div style="width: {percent}%; background-color: {cor}; height: 20px; border-radius: 10px; text-align: center; color: white; font-size: 12px; line-height: 20px; font-weight: bold;">
            {percent}%
        </div>
    </div>
    <br>
    """, unsafe_allow_html=True)

# --- CARREGAMENTO DE DADOS ---
try:
    # Lê todas as colunas como string para evitar erros
    df = pd.read_csv(url, dtype=str).fillna("")
except Exception as e:
    st.error(f"Erro ao conectar na planilha: {e}")
    st.stop()

# --- TELA DE LOGIN ---
if 'logado' not in st.session_state:
    st.session_state['logado'] = False

if not st.session_state['logado']:
    
    # Tenta mostrar a logo se existir no GitHub
    try:
        st.image("logo.png", width=200) 
    except:
        pass 

    st.markdown("<h1>🔐 Portal do Investidor</h1>", unsafe_allow_html=True)
    st.write("Digite seu CPF para acompanhar a evolução dos seus ativos.")
    
    with st.container(border=True):
        cpf_input = st.text_input("CPF (somente números):", type="password")
        entrar_btn = st.button("Acessar Painel", use_container_width=True)
    
    if entrar_btn:
        if cpf_input:
            cpf_limpo = cpf_input.replace(".", "").replace("-", "").strip()
            
            try:
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
                st.error("Erro: Coluna 'CPFs_Acesso' não encontrada. Verifique os cabeçalhos da planilha.")
        else:
            st.warning("Digite o CPF.")

# --- ÁREA LOGADA (PAINEL) ---
else:
    nome = st.session_state['nome_investidor']
    meus_dados = st.session_state['dados_cliente']
    
    with st.sidebar:
        try:
            st.image("logo.png", width=150)
        except:
            st.write("📸 (Logo)")
        st.header(f"Olá, {nome}")
        if st.button("Sair"):
            st.session_state['logado'] = False
            st.rerun()

    st.title("🏡 Meus Ativos")
    st.markdown("---")
    
    for index, row in meus_dados.iterrows():
        
        # 1. Calcula Progresso Automático
        progresso = calcular_progresso_auto(row)
        
        titulo_botao = f"{row['Imovel_Nome']} ({progresso}%)"
        
        with st.expander(titulo_botao, expanded=False):
            
            # --- Cabeçalho do Card ---
            c_head1, c_head2 = st.columns([2, 2])
            c_head1.caption(f"🆔 ID Caixa: {row['ID_Caixa']}")
            c_head2.markdown(f"💰 Valor: **:green[{row['Valor_Imovel']}]**")
            
            # --- Barra de Progresso Colorida ---
            st.write("Evolução do Processo:")
            barra_progresso_colorida(progresso)

            # --- Dicionário das 5 Etapas para Loop ---
            # Estrutura: Nome na Tela | Coluna Status | Coluna Link | Coluna Nota
            etapas_fluxo = [
                ("📝 Ficha do Imóvel", "Status_Ficha", "Link_Ficha", "Nota_Ficha"),
                ("📄 Contrato", "Status_Contrato", "Link_Contrato", "Nota_Contrato"),
                ("💸 ITBI", "Status_ITBI", "Link_ITBI", "Nota_ITBI"),
                ("✍️ Escritura", "Status_Escritura", "Link_Escritura", "Nota_Escritura"),
                ("®️ Registro", "Status_Registro", "Link_Registro", "Nota_Registro")
            ]

            st.caption("1️⃣ Etapa de Regularização")
            
            # Cria as linhas das etapas dinamicamente
            for label, col_status, col_link, col_nota in etapas_fluxo:
                st_txt = row.get(col_status, '')
                icone = obter_icone(st_txt)
                
                # Layout: 3 Colunas (Status | Doc | Nota)
                c1, c2, c3 = st.columns([5, 1, 1])
                
                # Coluna 1: Ícone + Texto Status
                c1.markdown(f"**{label}:** {icone} {st_txt}")
                
                # Coluna 2: Botão Link (Só aparece se tiver link)
                link = row.get(col_link, '').strip()
                if link and "http" in link:
                    c2.link_button("📂", link, help="Abrir Documento")
                
                # Coluna 3: Botão Nota (Só aparece se tiver nota)
                nota = row.get(col_nota, '').strip()
                if nota:
                    c3.popover("ℹ️", help="Ver observações").write(nota)
                
                st.divider() # Linha fina separadora

            # --- FASE 2: PÓS-VENDA ---
            st.caption("2️⃣ Etapa de Pós-Venda")
            col_venda1, col_venda2 = st.columns(2)
            
            # Ocupação e Engenharia
            col_venda1.info(f"**Ocupação:** {row.get('Status_Ocupacao', '-')}")
            col_venda1.write(f"**Engenharia:** {row.get('Status_Engenharia', '-')}")
            
            # Status Revenda (Com festa se vendido)
            status_venda = row.get('Status_Revenda', '-')
            if "vendido" in str(status_venda).lower():
                col_venda2.success(f"**Revenda:** 🎉 {status_venda}")
                st.balloons()
            else:
                col_venda2.warning(f"**Revenda:** {status_venda}")
