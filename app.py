import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão Leilões", page_icon="🏢", layout="centered")

# --- CONEXÃO COM PLANILHA ---
sheet_id = "1ke17ffjYUXwOf2gFLJorbWH46uY-EbEWCw0099iYaPI"
sheet_name = "Dados"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

# --- FUNÇÕES DE LÓGICA E VISUAL ---

def obter_icone(status):
    status = str(status).lower()
    if any(x in status for x in ['assinado', 'concluido', 'concluída', 'emitido', 'ok', 'pago', 'registrado', 'pronto', 'desocupado', 'livre']):
        return "✅"
    elif any(x in status for x in ['pendente', 'andamento', 'aguardando', 'fazer', 'processamento', 'analise', 'a pagar', 'ocupado']):
        return "📝" # Ou ⏳
    elif any(x in status for x in ['travado', 'problema', 'atenção', 'erro']):
        return "⚠️"
    elif status in ["nan", ""]:
        return "⚪"
    else:
        return "ℹ️"

def obter_cor_texto(texto):
    """Retorna a cor para usar no st.markdown baseado no texto"""
    texto = str(texto).lower()
    if any(x in texto for x in ['ocupado', 'a pagar', 'pendente', 'atrasado']):
        return "red"
    if any(x in texto for x in ['desocupado', 'pago', 'em dia', 'ok']):
        return "green"
    return "black" # ou gray

def calcular_progresso_inteligente(row):
    """
    Calcula % considerando se é Financiado (4 etapas) ou Vista (5 etapas).
    """
    tipo_compra = str(row.get('Tipo_Compra', '')).lower()
    
    # Define as etapas baseadas no tipo de compra
    if 'financiado' in tipo_compra:
        # 4 Etapas (25% cada): Contrato -> ITBI -> Registro -> Cadastro
        etapas = ['Status_Contrato', 'Status_ITBI', 'Status_Registro', 'Status_Cadastro']
        peso = 25
    else:
        # 5 Etapas (20% cada): Contrato -> ITBI -> Escritura -> Registro -> Cadastro
        etapas = ['Status_Contrato', 'Status_ITBI', 'Status_Escritura', 'Status_Registro', 'Status_Cadastro']
        peso = 20
        
    pontos = 0
    sucesso = ['assinado', 'concluido', 'concluída', 'emitido', 'ok', 'pago', 'registrado', 'pronto']
    
    for etapa in etapas:
        status = str(row.get(etapa, '')).lower()
        if any(x in status for x in sucesso):
            pontos += peso
            
    return min(pontos, 100)

def barra_progresso_colorida(percent):
    if percent < 40:
        cor = "#ff4b4b" # Vermelho
    elif percent < 80:
        cor = "#ffa421" # Amarelo
    else:
        cor = "#09ab3b" # Verde
    
    # Barra HTML fina e elegante
    st.markdown(f"""
    <div style="width: 100%; background-color: #e0e0e0; border-radius: 5px; height: 10px; margin-bottom: 10px;">
        <div style="width: {percent}%; background-color: {cor}; height: 10px; border-radius: 5px;"></div>
    </div>
    """, unsafe_allow_html=True)

def obter_bola_status(percent):
    if percent < 40: return "🔴"
    if percent < 80: return "🟡"
    return "🟢"

# --- CARREGAMENTO ---
try:
    df = pd.read_csv(url, dtype=str).fillna("")
except Exception as e:
    st.error(f"Erro ao conectar: {e}")
    st.stop()

# --- LOGIN ---
if 'logado' not in st.session_state:
    st.session_state['logado'] = False

if not st.session_state['logado']:
    try:
        st.image("logo.png", width=180) 
    except:
        pass # Se não tiver logo, segue vida

    st.markdown("<h3>🔐 Acesso ao Sistema</h3>", unsafe_allow_html=True)
    
    with st.container(border=True):
        cpf_input = st.text_input("CPF:", type="password")
        if st.button("Entrar", use_container_width=True):
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
                except:
                    st.error("Erro na leitura da coluna CPF.")
            else:
                st.warning("Digite o CPF.")

# --- PAINEL PRINCIPAL ---
else:
    nome = st.session_state['nome_investidor']
    meus_dados = st.session_state['dados_cliente']
    
    with st.sidebar:
        try:
            st.image("logo.png", width=150)
        except:
            st.write("📷 (Logo não encontrada)")
        st.write(f"Olá, **{nome}**")
        if st.button("Sair"):
            st.session_state['logado'] = False
            st.rerun()

    st.title("🏡 Meus Imóveis")
    st.markdown("---")
    
    for index, row in meus_dados.iterrows():
        
        # Cálculos Iniciais
        progresso = calcular_progresso_inteligente(row)
        bola = obter_bola_status(progresso)
        
        # Título com Status Visual (Sem clicar o cliente já vê a cor)
        titulo_card = f"{bola} {row['Imovel_Nome']}  —  {progresso}%"
        
        with st.expander(titulo_card, expanded=False):
            
            # 1. Barra de Progresso Interna
            barra_progresso_colorida(progresso)
            
            # 2. Cabeçalho (ID e Valor)
            c_top1, c_top2 = st.columns(2)
            c_top1.caption(f"🆔 ID: {row['ID_Caixa']}")
            c_top1.caption(f"📍 Tipo: {row.get('Tipo_Imovel', '-')}")
            c_top2.markdown(f"💰 Valor: **:green[{row['Valor_Imovel']}]**")
            
            st.divider()

            # 3. Informações de Regularização (Ocupação e Débitos)
            st.markdown("##### 🚦 Status de Regularização")
            
            col_reg1, col_reg2, col_reg3 = st.columns(3)
            
            # Ocupação
            ocup = row.get('Status_Ocupacao', '-')
            cor_ocup = obter_cor_texto(ocup)
            col_reg1.markdown(f"**Ocupação:**")
            col_reg1.markdown(f":{cor_ocup}[{ocup}]")
            
            # IPTU
            iptu = row.get('Debito_IPTU', '-')
            cor_iptu = obter_cor_texto(iptu)
            col_reg2.markdown(f"**IPTU:**")
            col_reg2.markdown(f":{cor_iptu}[{iptu}]")
            
            # Condomínio (Lógica: Só mostra se NÃO for Casa)
            tipo_imovel = str(row.get('Tipo_Imovel', '')).lower()
            if 'casa' not in tipo_imovel:
                cond = row.get('Debito_Condominio', '-')
                cor_cond = obter_cor_texto(cond)
                col_reg3.markdown(f"**Condomínio:**")
                col_reg3.markdown(f":{cor_cond}[{cond}]")
            
            st.divider()

            # 4. Fluxo do Processo (Grid 2x2)
            st.markdown("##### 📝 Etapas Documentais")
            
            # Define o fluxo baseado no financiamento
            tipo_compra = str(row.get('Tipo_Compra', '')).lower()
            
            # Lista Base
            fluxo = [
                ("Contrato", "Status_Contrato", "Link_Contrato", "Nota_Contrato"),
                ("ITBI", "Status_ITBI", "Link_ITBI", "Nota_ITBI")
            ]
            
            # Adiciona Escritura SOMENTE se NÃO for financiado
            if 'financiado' not in tipo_compra:
                fluxo.append(("Escritura", "Status_Escritura", "Link_Escritura", "Nota_Escritura"))
            
            # Adiciona o resto
            fluxo.append(("Registro", "Status_Registro", "Link_Registro", "Nota_Registro"))
            fluxo.append(("Cad. Imobiliário", "Status_Cadastro", "Link_Cadastro", "Nota_Cadastro"))
            
            # Loop para criar o Grid (2 colunas)
            for i in range(0, len(fluxo), 2):
                cols = st.columns(2) # Cria 2 colunas
                
                # Pega até 2 itens da lista por vez
                itens_da_vez = fluxo[i : i+2]
                
                for j, item in enumerate(itens_da_vez):
                    label, col_st, col_lnk, col_nt = item
                    
                    with cols[j]: # Preenche a coluna da esquerda (0) ou direita (1)
                        st_txt = row.get(col_st, '')
                        icone = obter_icone(st_txt)
                        
                        # Linha 1: Título e Ícone
                        st.markdown(f"**{label}**")
                        st.write(f"{icone} {st_txt}")
                        
                        # Linha 2: Botões (Pequenos lado a lado)
                        b1, b2 = st.columns([1, 4])
                        
                        link = str(row.get(col_lnk, '')).strip()
                        if link and "http" in link:
                            b1.link_button("📂", link, help="Ver Documento")
                            
                        nota = str(row.get(col_nt, '')).strip()
                        if nota and nota.lower() != "nan":
                            with b2.popover("Obs"):
                                st.write(nota)
                        
                        st.write("") # Espaço vazio para alinhar
            
            st.divider()
            
            # 5. Engenharia e Revenda
            st.caption("Fase Final (Engenharia e Venda)")
            ce1, ce2 = st.columns(2)
            ce1.info(f"Engenharia: {row.get('Status_Engenharia', '-')}")
            
            revenda = row.get('Status_Revenda', '-')
            if "vendido" in str(revenda).lower():
                ce2.success(f"Revenda: {revenda}")
            else:
                ce2.warning(f"Revenda: {revenda}")
