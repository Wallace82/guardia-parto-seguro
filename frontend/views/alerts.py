import streamlit as st
from datetime import datetime

# Recuperar cliente de API e token
api_client = st.session_state.api_client
token = st.session_state.access_token
user = st.session_state.user

st.markdown("<h1 class='main-title'>🚨 Central de Alertas</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Acompanhe desvios assistenciais e tome medidas preventivas em tempo real</p>", unsafe_allow_html=True)

# Filtros no topo
col1, col2 = st.columns(2)

with col1:
    severity_filter = st.selectbox(
        "Filtrar por Severidade",
        ["Todos", "Críticos", "Moderados"],
        index=0
    )

with col2:
    status_filter = st.selectbox(
        "Filtrar por Status",
        ["Pendente de Reconhecimento", "Todos"],
        index=0
    )

# Mapeamento de filtros para parâmetros da API
severity_param = {
    "Todos": None,
    "Críticos": "critical",
    "Moderados": "moderate"
}.get(severity_filter)

unacknowledged_only = (status_filter == "Pendente de Reconhecimento")

# Buscar alertas da API
alerts = api_client.get_alerts(token, severity=severity_param, unacknowledged_only=unacknowledged_only)

# Exibição dos alertas
if not alerts:
    st.info("Nenhum alerta encontrado com os filtros selecionados.")
else:
    for a in alerts:
        created_time = datetime.fromisoformat(a["created_at"].replace("Z", "+00:00")).strftime("%d/%m/%Y às %H:%M")
        
        card_class = "alert-critical" if a["severity"] == "critical" else "alert-moderate"
        severity_label = "CRÍTICO" if a["severity"] == "critical" else "MODERADO"
        badge_style = "background: rgba(239, 68, 68, 0.15); color: #EF4444;" if a["severity"] == "critical" else "background: rgba(245, 158, 11, 0.15); color: #F59E0B;"
        
        # Início do card de alerta
        st.markdown(f"""
        <div class="alert-card {card_class}">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <span style="font-size: 0.75rem; font-weight: 700; border-radius: 4px; padding: 0.15rem 0.5rem; margin-right: 0.5rem; {badge_style}">{severity_label}</span>
                    <h5 style="margin: 0.4rem 0 0 0; display: inline-block; color: #F1F5F9; font-size: 1.1rem; font-weight: 600;">{a['title']}</h5>
                </div>
                <div style="font-size: 0.85rem; color: #94A3B8;">
                    Gerado em: {created_time}
                </div>
            </div>
            <p style="margin: 0.6rem 0 0.8rem 0; font-size: 0.95rem; color: #E2E8F0; line-height: 1.4;">{a['description']}</p>
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; border-top: 1px solid rgba(255,255,255,0.03); padding-top: 0.6rem; font-size: 0.8rem; color: #94A3B8;">
                <div>
                    <span>Sessão Clínicas Ref: <b>#{a['session_id']}</b></span>
                    {f" | IRA no momento: <b>{a['ira_score']}%</b>" if a['ira_score'] is not None else ""}
                </div>
                <div id="action-area-{a['id']}">
        """, unsafe_allow_html=True)
        
        # Lógica para o botão de reconhecimento
        if a["is_acknowledged"]:
            ack_time = datetime.fromisoformat(a["acknowledged_at"].replace("Z", "+00:00")).strftime("%d/%m às %H:%M") if a["acknowledged_at"] else "N/A"
            st.markdown(f"""
                <span style="color: #10B981; font-weight: 600;">✓ Reconhecido em {ack_time}</span>
            """, unsafe_allow_html=True)
        else:
            # Para renderizar botões Streamlit para interatividade individual de cada card de alerta
            # Usamos chaves únicas baseadas no ID do alerta
            if st.button(f"Reconhecer Alerta #{a['id']}", key=f"ack_btn_{a['id']}", use_container_width=False, type="primary"):
                with st.spinner("Marcando como verificado..."):
                    res = api_client.acknowledge_alert(token, a["id"])
                    if res:
                        st.success("Alerta reconhecido com sucesso!")
                        st.rerun()
                    else:
                        st.error("Erro ao reconhecer o alerta.")
                        
        st.markdown("""
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
