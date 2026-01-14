import streamlit as st
import pandas as pd
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão Leilões", page_icon="🏢", layout="centered")

# --- CONEXÃO COM PLANILHA ---
sheet_id = "1ke17ffjYUXwOf2gFLJorbWH46uY-EbEWCw0099iYaPI"
sheet_name = "Dados"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

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
    """Calcula % baseado no tipo de compra"""
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
    """Gera a barra de blocos (█ e ░) verde"""
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

# --- FUNÇÃO CARREGAR LOGO BLINDADA ---
def mostrar_logo(width_val):
    try:
        if os.path.exists("logo.png"): st.image("logo.png", width=width_val)
        elif os.path.exists("logo.jpg"): st.image("logo.jpg", width=width_val)
        elif os.path.exists("logo.jpeg"): st.image("logo.jpeg", width=width_val)
        elif os.path.exists("logo.png.jpg"): st.image("logo.png.jpg", width=width_val)
    except Exception:
        pass

# --- CARREGAMENTO DE DADOS (COM LIMPEZA) ---
try:
    # 1. Carrega tudo como texto
    df = pd.read_csv(url, dtype=str).fillna("")
    
    # 2. LIMPEZA DOS CABEÇALHOS (Remove espaços extras nos nomes das colunas)
    df.columns = df.columns.str.strip()
    
    # 3. LIMPEZA DOS CPFS (Remove espaços extras dentro dos dados)
    if 'CPFs_Acesso' in df.columns:
        df['CPFs_Acesso'] = df['CPFs_Acesso'].str.strip()
        
except Exception as e:
    st.error(f"Erro ao conectar na planilha: {e}")
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
                # Limpa o que o usuário digitou (tira pontos, traços e espaços)
                cpf_limpo = cpf_input.replace(".", "").replace("-", "").strip()
                
                try:
                    # Busca exata (agora funciona sem espaço extra)
                    filtro = df['CPFs_Acesso'] == cpf_limpo
                    cliente_df = df[filtro]
                    
                    if not cliente_df.empty:
                        st.session_state['logado'] = True
                        st.session_state['dados_cliente'] = cliente_df
                        st.session_state['nome_investidor'] = cliente_df.iloc[0]['Investidor']
                        st.rerun()
                    else:
                        st.error("CPF não encontrado.")
                except Exception as e:
                    st.error(f"Erro técnico ao buscar CPF: {e}")
            else:
                st.warning("Digite o CPF.")

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

            c_top1, c_top2 = st.columns(2)
            c_top1.caption(f"🆔 ID: {row['ID_Caixa']}")
            c_top1.caption(f"📍 Tipo: {row.get('Tipo_Imovel', '-')}")
            c_top2.markdown(f"💰 Valor: **:green[{row['Valor_Imovel']}]**")
            
            st.divider()

            st.markdown("##### 🚦 Status de Regularização")
            col_reg1, col_reg2, col_reg3 = st.columns(3)
            
            ocup = row.get('Status_Ocupacao', '-')
            cor_ocup = obter_cor_texto(ocup)
            col_reg1.markdown(f"**Ocupação:** :{cor_ocup}[{ocup}]")
            
            iptu = row.get('Debito_IPTU', '-')
            cor_iptu = obter_cor_texto(iptu)
            col_reg2.markdown(f"**IPTU:** :{cor_iptu}[{iptu}]")
            
            tipo_imovel = str(row.get('Tipo_Imovel', '')).lower()
            if 'casa' not in tipo_imovel:
                cond = row.get('Debito_Condominio', '-')
                cor_cond = obter_cor_texto(cond)
                col_reg3.markdown(f"**Condomínio:** :{cor_cond}[{cond}]")
            
            st.divider()

            st.markdown("##### 📝 Etapas Documentais")
            tipo_compra = str(row.get('Tipo_Compra', '')).lower()
            
            fluxo = [
                ("Contrato", "Status_Contrato", "Link_Contrato", "Nota_Contrato"),
                ("ITBI", "Status_ITBI", "Link_ITBI", "Nota_ITBI")
            ]
            if 'financiado' not in tipo_compra:
                fluxo.append(("Escritura", "Status_Escritura", "Link_Escritura", "Nota_Escritura"))
            fluxo.append(("Registro", "Status_Registro", "Link_Registro", "Nota_Registro"))
            fluxo.append(("Cad. Imobiliário", "Status_Cadastro", "Link_Cadastro", "Nota_Cadastro"))
            
            for i in range(0, len(fluxo), 2):
                cols = st.columns(2)
                itens_da_vez = fluxo[i : i+2]
                for j, item in enumerate(itens_da_vez):
                    label, col_st, col_lnk, col_nt = item
                    with cols[j]:
                        st_txt = row.get(col_st, '')
                        icone = obter_icone(st_txt)
                        
                        st.markdown(f"**{label}**")
                        st.write(f"{icone} {st_txt}")
                        
                        b1, b2 = st.columns([1, 4])
                        link = str(row.get(col_lnk, '')).strip()
                        if link and "http" in link:
                            b1.link_button("📂", link, help="Ver Documento")
                        nota = str(row.get(col_nt, '')).strip()
                        if nota and nota.lower() != "nan":
                            with b2.popover("Obs"):
                                st.write(nota)
                        st.write("")
            
            st.divider()
            
            st.caption("Fase Final")
            ce1, ce2 = st.columns(2)
            ce1.info(f"Engenharia: {row.get('Status_Engenharia', '-')}")
            revenda = row.get('Status_Revenda', '-')
            if "vendido" in str(revenda).lower():
                ce2.success(f"Revenda: {revenda}")
            else:
                ce2.warning(f"Revenda: {revenda}")
