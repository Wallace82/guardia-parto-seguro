"""
GuardIA Parto Seguro — Dashboard Principal
Streamlit Application Entry Point
"""
import streamlit as st
from services.api_client import APIClient

# ============ CONFIGURAÇÃO DA PÁGINA ============
st.set_page_config(
    page_title="GuardIA Parto Seguro",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/seu-org/guardia-parto-seguro",
        "Report a Bug": "https://github.com/seu-org/guardia-parto-seguro/issues",
        "About": "GuardIA Parto Seguro v1.0 — Plataforma de IA para Vigilância Obstétrica",
    },
)

# Initialize API Client in session state
if "api_client" not in st.session_state:
    st.session_state.api_client = APIClient()

# ============ ESTILOS CUSTOMIZADOS (Estética Premium) ============
st.markdown("""
<style>
    /* Estilos globais e customização de fontes */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    /* Cores principais do tema */
    :root {
        --primary-color: #8B5CF6;      /* Roxo violeta vibrante */
        --secondary-color: #EC4899;    /* Rosa escuro */
        --success-color: #10B981;      /* Verde esmeralda */
        --warning-color: #F59E0B;      /* Âmbar */
        --danger-color: #EF4444;       /* Vermelho */
        --background: #0B0F19;         /* Azul escuro profundo */
        --surface: #1E293B;            /* Azul ardósia médio */
        --surface-hover: #334155;
        --text: #FFFFFF;               /* Branco puro para melhor contraste */
        --text-muted: #E2E8F0;         /* Cinza muito claro */
    }

    /* Fundo da aplicação com gradiente radial e profundo */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #090d16 60%, #020617 100%) !important;
        color: var(--text) !important;
    }

    /* Alto contraste global de textos */
    body, p, span, label, li, td, th, div, small, [data-testid="stMarkdown"] p {
        color: #FFFFFF !important;
    }

    /* Ajuste específico para subtítulos e descrições secundárias */
    .subtitle {
        font-size: 1.15rem;
        font-weight: 400;
        color: #E2E8F0 !important;
        margin-bottom: 2rem;
    }

    /* Streamlit widgets labels (Labels de Inputs) */
    div[data-testid="stWidgetLabel"] p, label, .stSelectbox label, .stTextInput label, .stTextArea label {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.5);
    }

    /* Tabelas em alto contraste */
    div[data-testid="stTable"] table, table {
        color: #FFFFFF !important;
        background-color: rgba(15, 23, 42, 0.6) !important;
        border-collapse: collapse;
        border-radius: 8px;
        overflow: hidden;
    }
    th {
        background-color: rgba(124, 58, 237, 0.2) !important;
        color: #C084FC !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        border-bottom: 2px solid rgba(124, 58, 237, 0.4) !important;
    }
    td {
        border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
        font-size: 0.9rem !important;
    }

    /* Tabs (Abas) estilo premium com alto contraste */
    button[data-baseweb="tab"] {
        color: #E2E8F0 !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease;
    }
    button[data-baseweb="tab"]:hover {
        color: #FFFFFF !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #C084FC !important;
        font-weight: 700 !important;
        border-bottom-color: #8B5CF6 !important;
    }

    /* Scrollbar customizado */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(11, 15, 25, 0.5);
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(124, 58, 237, 0.4);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(124, 58, 237, 0.7);
    }

    /* Efeito de surgimento (Fade In) */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(12px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* Cards e Containers com efeito Glassmorphism */
    .glass-card, div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(15, 23, 42, 0.55) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        margin-bottom: 1.2rem !important;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.75) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        animation: fadeInUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) both !important;
    }
    
    .glass-card:hover, div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-4px) !important;
        border-color: rgba(139, 92, 246, 0.5) !important;
        box-shadow: 0 15px 35px -5px rgba(139, 92, 246, 0.2), 0 5px 15px -5px rgba(0, 0, 0, 0.6) !important;
    }

    /* Glows customizados para cartões */
    .glow-red {
        border-left: 4px solid var(--danger-color) !important;
    }
    .glow-red:hover {
        border-color: var(--danger-color) !important;
        box-shadow: 0 15px 35px -5px rgba(239, 68, 68, 0.25), 0 5px 15px -5px rgba(0, 0, 0, 0.6) !important;
    }

    .glow-yellow {
        border-left: 4px solid var(--warning-color) !important;
    }
    .glow-yellow:hover {
        border-color: var(--warning-color) !important;
        box-shadow: 0 15px 35px -5px rgba(245, 158, 11, 0.25), 0 5px 15px -5px rgba(0, 0, 0, 0.6) !important;
    }

    .glow-green {
        border-left: 4px solid var(--success-color) !important;
    }
    .glow-green:hover {
        border-color: var(--success-color) !important;
        box-shadow: 0 15px 35px -5px rgba(16, 185, 129, 0.25), 0 5px 15px -5px rgba(0, 0, 0, 0.6) !important;
    }

    .glow-purple {
        border-left: 4px solid var(--primary-color) !important;
    }
    .glow-purple:hover {
        border-color: var(--primary-color) !important;
        box-shadow: 0 15px 35px -5px rgba(139, 92, 246, 0.3), 0 5px 15px -5px rgba(0, 0, 0, 0.6) !important;
    }

    /* Customização do Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(8, 10, 18, 0.85) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(24px) !important;
        -webkit-backdrop-filter: blur(24px) !important;
    }

    /* Botões personalizados */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.6rem !important;
        font-weight: 600 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        box-shadow: 0 4px 14px 0 rgba(139, 92, 246, 0.4) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #A78BFA 0%, #7C3AED 100%) !important;
        box-shadow: 0 6px 20px 0 rgba(139, 92, 246, 0.6) !important;
        transform: translateY(-2px) !important;
    }

    /* Estilo dos inputs e seletores da Streamlit */
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="textarea"] {
        background-color: rgba(15, 23, 42, 0.65) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 10px !important;
        transition: all 0.25s ease !important;
        color: #FFFFFF !important;
    }
    div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within {
        border-color: rgba(139, 92, 246, 0.6) !important;
        box-shadow: 0 0 12px rgba(139, 92, 246, 0.3) !important;
    }

    /* Garante que o interior do selectbox e os textos fiquem escuros e legíveis */
    div[data-baseweb="select"] > div {
        background-color: rgba(15, 23, 42, 0.9) !important;
        color: #FFFFFF !important;
    }
    div[data-baseweb="select"] input {
        color: #FFFFFF !important;
    }

    /* Estilização de Menus Dropdown, Popovers e Listbox (Itens de Seleção) */
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
        background-color: #1E293B !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 8px !important;
    }
    li[role="option"], [data-baseweb="menu"] li, [data-baseweb="popover"] li {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        transition: background-color 0.15s ease !important;
    }
    li[role="option"]:hover, [data-baseweb="menu"] li:hover, [data-baseweb="popover"] li:hover {
        background-color: #8B5CF6 !important;
        color: #FFFFFF !important;
    }

    /* Customização dos Títulos e Divisores */
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -0.05rem;
        background: linear-gradient(135deg, #C084FC 0%, #F472B6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }

    /* Indicadores de Risco (IRA) */
    .ira-gauge-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 1rem;
    }
    
    .ira-score-display {
        font-size: 3.5rem;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 0.5rem;
    }

    .ira-baixo { color: #10B981; text-shadow: 0 0 15px rgba(16, 185, 129, 0.5); font-weight: 800; }
    .ira-moderado { color: #F59E0B; text-shadow: 0 0 15px rgba(245, 158, 11, 0.5); font-weight: 800; }
    .ira-critico { color: #EF4444; text-shadow: 0 0 15px rgba(239, 68, 68, 0.5); font-weight: 800; }

    /* Estilos dos Alertas */
    .alert-card {
        border-left: 5px solid;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        background: rgba(15, 23, 42, 0.55);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.55);
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) both;
    }
    .alert-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.65);
    }
    .alert-critical {
        border-left-color: #EF4444;
        background: rgba(239, 68, 68, 0.08);
        border: 1px solid rgba(239, 68, 68, 0.15);
    }
    .alert-critical:hover {
        border-color: rgba(239, 68, 68, 0.45);
    }
    .alert-moderate {
        border-left-color: #F59E0B;
        background: rgba(245, 158, 11, 0.08);
        border: 1px solid rgba(245, 158, 11, 0.15);
    }
    .alert-moderate:hover {
        border-color: rgba(245, 158, 11, 0.45);
    }
    .alert-low {
        border-left-color: #10B981;
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.15);
    }
    .alert-low:hover {
        border-color: rgba(16, 185, 129, 0.45);
    }

    /* CSS Timeline */
    .timeline-container {
        position: relative;
        margin-top: 1.2rem;
        padding-left: 24px;
        border-left: 2px solid rgba(255, 255, 255, 0.08);
    }
    .timeline-item {
        position: relative;
        margin-bottom: 1.5rem;
    }
    .timeline-dot {
        position: absolute;
        left: -31px;
        top: 4px;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #1e293b;
        border: 2px solid rgba(255,255,255,0.15);
        transition: all 0.3s ease;
    }
    .timeline-item.active .timeline-dot {
        background: #7C4DFF !important;
        border-color: #0b1020 !important;
        box-shadow: 0 0 10px #7C4DFF;
    }
    .timeline-item.success .timeline-dot {
        background: #22C55E !important;
        border-color: #0b1020 !important;
        box-shadow: 0 0 10px #22C55E;
    }
    .timeline-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: #FFFFFF !important;
    }
    .timeline-desc {
        font-size: 0.8rem;
        color: #94A3B8 !important;
    }

    /* Cards dos Arquivos */
    .media-card {
        background: rgba(20, 27, 45, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        margin-bottom: 0.8rem !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        animation: fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) both;
    }
    .media-card:hover {
        background: rgba(28, 37, 64, 0.7) !important;
        border-color: rgba(124, 77, 255, 0.4) !important;
        transform: translateY(-2px);
    }
    .media-card-info {
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }
    .media-card-icon {
        width: 40px;
        height: 40px;
        border-radius: 8px;
        background: rgba(124, 77, 255, 0.15);
        border: 1px solid rgba(124, 77, 255, 0.25);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
    }
    .media-card-name {
        font-size: 0.9rem;
        font-weight: 600;
        color: #FFFFFF !important;
    }
    .media-card-meta {
        font-size: 0.75rem;
        color: #94A3B8 !important;
    }

    /* Barras de Score / Sub-scores */
    .score-bar-bg {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 6px;
        height: 8px;
        width: 100%;
        margin-top: 0.3rem;
        overflow: hidden;
    }
    .score-bar-fill {
        height: 100%;
        border-radius: 6px;
        transition: width 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    }

    /* Perfil do Usuário na Sidebar */
    .sidebar-profile {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem;
        background: rgba(20, 27, 45, 0.5);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-top: 1rem;
        margin-bottom: 1.5rem;
    }
    .sidebar-avatar {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: linear-gradient(135deg, #7C4DFF 0%, #EC4899 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: white;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
    }
    .sidebar-profile-name {
        font-size: 0.85rem;
        font-weight: 600;
        color: #FFFFFF !important;
        line-height: 1.2;
    }
    .sidebar-profile-role {
        font-size: 0.75rem;
        color: #94A3B8 !important;
    }
</style>
""", unsafe_allow_html=True)

# ============ VERIFICAÇÃO DE AUTENTICAÇÃO ============
if "access_token" not in st.session_state or not st.session_state.access_token:
    if "token" in st.query_params:
        token_val = st.query_params["token"]
        user_info = st.session_state.api_client.get_me(token_val)
        if user_info:
            st.session_state.access_token = token_val
            st.session_state.user = user_info
        else:
            st.session_state.access_token = None
            st.session_state.user = None
            st.query_params.clear()
    else:
        st.session_state.access_token = None
        st.session_state.user = None
else:
    if "user" not in st.session_state:
        st.session_state.user = None

if not st.session_state.access_token:
    # Tela de Login Centrada e Elegante
    _, col2, _ = st.columns([1, 1.8, 1])
    with col2:
        st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card' style='padding: 2.5rem;'>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; margin-bottom: 0.5rem;'>🛡️ GuardIA</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: #94A3B8; font-weight: 400; margin-bottom: 2rem;'>Vigilância Obstétrica Multimodal</h4>", unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("📧 Email Institucional", placeholder="medico@hospital.com")
            password = st.text_input("🔒 Senha de Acesso", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Entrar no Painel", use_container_width=True)

            if submitted:
                if email and password:
                    with st.spinner("Autenticando na plataforma..."):
                        result = st.session_state.api_client.login(email, password)
                        if result:
                            st.session_state.access_token = result["access_token"]
                            st.session_state.user = result["user"]
                            st.query_params["token"] = result["access_token"]
                            st.success("✅ Autenticado com sucesso!")
                            st.rerun()
                        else:
                            st.error("❌ Credenciais inválidas ou serviço indisponível")
                else:
                    st.warning("⚠️ Preencha o email e a senha para acessar")
        
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; color: #64748B; font-size: 0.85rem; margin-top: 1.5rem;'>Mantenha suas credenciais confidenciais. Em conformidade com a LGPD.</div>", unsafe_allow_html=True)
    st.stop()

# ============ NAVEGAÇÃO MULTIPÁGINA (Com st.Page ou Fallback) ============

# Customização da barra lateral superior (Perfil do Usuário)
with st.sidebar:
    st.markdown("### 🛡️ GuardIA")
    st.markdown("---")
    user = st.session_state.user
    if user:
        role_label = {
            "admin": "Administrador",
            "gestor": "Gestor Hospitalar",
            "profissional": "Profissional de Saúde",
            "auditor": "Auditor Clínico"
        }.get(user.get("role"), user.get("role"))
        initials = "".join([n[0] for n in user.get('full_name', 'U').split()[:2]]).upper()
        st.markdown(f"""
        <div class="sidebar-profile">
            <div class="sidebar-avatar">{initials}</div>
            <div>
                <div class="sidebar-profile-name">{user.get('full_name')}</div>
                <div class="sidebar-profile-role">{role_label}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")

if hasattr(st, "Page") and hasattr(st, "navigation"):
    # Definindo as páginas para a barra lateral usando a API moderna do Streamlit
    is_session_detail = "selected_session_id" in st.query_params or "edit_session_id" in st.query_params
    dashboard_page = st.Page("views/dashboard.py", title="Dashboard Geral", icon="📊", default=not is_session_detail)
    sessions_page = st.Page("views/sessions.py", title="Sessões Clínicas", icon="🏥", default=is_session_detail)
    alerts_page = st.Page("views/alerts.py", title="Central de Alertas", icon="🚨")
    reports_page = st.Page("views/reports.py", title="Relatórios e Auditoria", icon="📄")
    
    # Configura as páginas disponíveis
    pages = [dashboard_page, sessions_page, alerts_page, reports_page]
    pg = st.navigation(pages)
    pg.run()
else:
    # Fallback para versões mais antigas do Streamlit (< 1.35.0)
    page_options = {
        "📊 Dashboard Geral": "views/dashboard.py",
        "🏥 Sessões Clínicas": "views/sessions.py",
        "🚨 Central de Alertas": "views/alerts.py",
        "📄 Relatórios e Auditoria": "views/reports.py"
    }
    
    default_index = 1 if ("selected_session_id" in st.query_params or "edit_session_id" in st.query_params) else 0
    with st.sidebar:
        selected_page_name = st.radio("Menu de Navegação", list(page_options.keys()), index=default_index)
        
    page_file = page_options[selected_page_name]
    
    # Executa o arquivo da view selecionada no contexto global
    with open(page_file, "r", encoding="utf-8") as f:
        code = compile(f.read(), page_file, "exec")
        exec(code, globals())

# Rodapé da barra lateral com botão Sair
with st.sidebar:
    st.markdown("---")
    if st.button("🚪 Encerrar Sessão", use_container_width=True, type="secondary"):
        st.session_state.access_token = None
        st.session_state.user = None
        st.query_params.clear()
        st.rerun()
