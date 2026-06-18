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

# ============ ESTILOS CUSTOMIZADOS ============
st.markdown("""
<style>
    /* Tema escuro personalizado */
    :root {
        --primary-color: #7C3AED;
        --secondary-color: #EC4899;
        --success-color: #10B981;
        --warning-color: #F59E0B;
        --danger-color: #EF4444;
        --background: #0F172A;
        --surface: #1E293B;
        --text: #F1F5F9;
    }

    .stApp {
        background-color: var(--background);
        color: var(--text);
    }

    /* IRA Gauge colors */
    .ira-baixo { color: #10B981; font-weight: bold; font-size: 2rem; }
    .ira-moderado { color: #F59E0B; font-weight: bold; font-size: 2rem; }
    .ira-critico { color: #EF4444; font-weight: bold; font-size: 2rem; }

    /* Alert cards */
    .alert-critical {
        border-left: 4px solid #EF4444;
        background: rgba(239, 68, 68, 0.1);
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .alert-moderate {
        border-left: 4px solid #F59E0B;
        background: rgba(245, 158, 11, 0.1);
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============ VERIFICAÇÃO DE AUTENTICAÇÃO ============
if "access_token" not in st.session_state:
    st.session_state.access_token = None

if not st.session_state.access_token:
    # Tela de Login
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("---")
        st.markdown("# 🛡️ GuardIA Parto Seguro")
        st.markdown("*Plataforma de IA para Vigilância Obstétrica*")
        st.markdown("---")

        with st.form("login_form"):
            email = st.text_input("📧 Email", placeholder="seu@email.com")
            password = st.text_input("🔒 Senha", type="password")
            submitted = st.form_submit_button("Entrar", use_container_width=True, type="primary")

            if submitted:
                if email and password:
                    with st.spinner("Autenticando..."):
                        client = APIClient()
                        result = client.login(email, password)
                        if result:
                            st.session_state.access_token = result["access_token"]
                            st.session_state.user = result["user"]
                            st.rerun()
                        else:
                            st.error("❌ Credenciais inválidas")
                else:
                    st.warning("Preencha email e senha")
    st.stop()

# ============ DASHBOARD PRINCIPAL ============
# Sidebar
with st.sidebar:
    st.markdown("# 🛡️ GuardIA")
    st.markdown(f"👤 **{st.session_state.get('user', {}).get('full_name', 'Usuário')}**")
    st.markdown(f"🎭 {st.session_state.get('user', {}).get('role', '').title()}")
    st.markdown("---")

    if st.button("🚪 Sair", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# Conteúdo principal
st.markdown("# 🛡️ GuardIA Parto Seguro")
st.markdown("**Dashboard de Vigilância Obstétrica**")
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🏥 Sessões Hoje", "12", "+3")
with col2:
    st.metric("🚨 Alertas Críticos", "2", "+1", delta_color="inverse")
with col3:
    st.metric("⚠️ Alertas Moderados", "5", "+2", delta_color="inverse")
with col4:
    st.metric("✅ IRA Médio Hoje", "38.2", "-5.1")

st.markdown("---")
st.info("👈 Use o menu à esquerda para navegar entre as páginas")
st.markdown("**Navegação:**")
st.markdown("- 📊 **Dashboard** — Visão geral e métricas")
st.markdown("- 🏥 **Sessões** — Criar e monitorar sessões clínicas")
st.markdown("- 🚨 **Alertas** — Central de alertas")
st.markdown("- 📄 **Relatórios** — Gerar e baixar relatórios")
