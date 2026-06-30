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
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    /* Cores principais do tema */
    :root {
        --primary-color: #7C3AED;      /* Roxo violeta */
        --secondary-color: #EC4899;    /* Rosa escuro */
        --success-color: #10B981;      /* Verde esmeralda */
        --warning-color: #F59E0B;      /* Âmbar */
        --danger-color: #EF4444;       /* Vermelho */
        --background: #0B0F19;         /* Azul escuro profundo */
        --surface: #1E293B;            /* Azul ardósia médio */
        --surface-hover: #334155;
        --text: #F1F5F9;
        --text-muted: #94A3B8;
    }

    /* Fundo da aplicação */
    .stApp {
        background: linear-gradient(135deg, #090D16 0%, #111827 100%);
        color: var(--text);
    }

    /* Cards e Containers com efeito Glassmorphism */
    .glass-card {
        background: rgba(30, 41, 59, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-2px);
        border-color: rgba(124, 58, 237, 0.3);
    }

    /* Botões personalizados */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        box-shadow: 0 4px 14px 0 rgba(124, 58, 237, 0.4);
        transition: all 0.2s ease;
    }
    
    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
        box-shadow: 0 6px 20px 0 rgba(124, 58, 237, 0.6);
        transform: translateY(-1px);
    }

    /* Customização dos Títulos e Divisores */
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(to right, #A78BFA, #EC4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    
    .subtitle {
        font-size: 1.1rem;
        color: var(--text-muted);
        margin-bottom: 2rem;
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

    .ira-baixo { color: #10B981; text-shadow: 0 0 10px rgba(16, 185, 129, 0.3); }
    .ira-moderado { color: #F59E0B; text-shadow: 0 0 10px rgba(245, 158, 11, 0.3); }
    .ira-critico { color: #EF4444; text-shadow: 0 0 10px rgba(239, 68, 68, 0.3); }

    /* Estilos dos Alertas */
    .alert-card {
        border-left: 5px solid;
        border-radius: 0px 10px 10px 0px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        background: rgba(30, 41, 59, 0.3);
    }
    .alert-critical {
        border-left-color: #EF4444;
        background: rgba(239, 68, 68, 0.05);
    }
    .alert-moderate {
        border-left-color: #F59E0B;
        background: rgba(245, 158, 11, 0.05);
    }
    .alert-low {
        border-left-color: #10B981;
        background: rgba(16, 185, 129, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# ============ VERIFICAÇÃO DE AUTENTICAÇÃO ============
if "access_token" not in st.session_state:
    st.session_state.access_token = None
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
        st.markdown(f"👤 **{user.get('full_name')}**")
        role_label = {
            "admin": "⚙️ Administrador",
            "gestor": "📈 Gestor Hospitalar",
            "profissional": "🩺 Profissional de Saúde",
            "auditor": "🔍 Auditor Clínico"
        }.get(user.get("role"), user.get("role"))
        st.markdown(f"**Papel:** `{role_label}`")
        st.markdown(f"📧 `{user.get('email')}`")
    st.markdown("---")

if hasattr(st, "Page") and hasattr(st, "navigation"):
    # Definindo as páginas para a barra lateral usando a API moderna do Streamlit
    dashboard_page = st.Page("views/dashboard.py", title="Dashboard Geral", icon="📊", default=True)
    sessions_page = st.Page("views/sessions.py", title="Sessões Clínicas", icon="🏥")
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
    
    with st.sidebar:
        selected_page_name = st.radio("Menu de Navegação", list(page_options.keys()))
        
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
        st.rerun()
