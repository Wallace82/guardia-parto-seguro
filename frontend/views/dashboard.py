import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# Recuperar cliente de API e token
api_client = st.session_state.api_client
token = st.session_state.access_token
user = st.session_state.user

st.markdown("<h1 class='main-title'>📊 Dashboard de Vigilância Obstétrica</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Métricas de Risco Assistencial (IRA) e Alertas de Parto Seguro</p>", unsafe_allow_html=True)

# Buscar dados da API (com fallbacks mockados automáticos)
sessions = api_client.get_sessions(token, role=user.get("role"))
alerts = api_client.get_alerts(token)

# Calcular métricas chave
total_sessions = len(sessions)
active_critical = len([a for a in alerts if a["severity"] == "critical" and not a["is_acknowledged"]])
active_moderate = len([a for a in alerts if a["severity"] == "moderate" and not a["is_acknowledged"]])

completed_sessions = [s for s in sessions if s["ira_score"] is not None]
if completed_sessions:
    avg_ira = sum([s["ira_score"] for s in completed_sessions]) / len(completed_sessions)
else:
    avg_ira = 0.0

# ============ RENDERIZAR MÉTRICAS GERAIS ============
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="glass-card glow-purple" style="text-align: center;">
        <span style="font-size: 0.9rem; color: #94A3B8; font-weight: 600;">🏥 Sessões Monitoradas</span>
        <h2 style="font-size: 2.3rem; margin: 0.4rem 0; color: #F1F5F9;">{total_sessions}</h2>
        <span style="font-size: 0.8rem; color: #10B981;">+12% vs. semana anterior</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="glass-card glow-red" style="text-align: center;">
        <span style="font-size: 0.9rem; color: #94A3B8; font-weight: 600;">🚨 Alertas Críticos Ativos</span>
        <h2 style="font-size: 2.3rem; margin: 0.4rem 0; color: #EF4444;">{active_critical}</h2>
        <span style="font-size: 0.8rem; color: #EF4444;">Ação imediata necessária</span>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="glass-card glow-yellow" style="text-align: center;">
        <span style="font-size: 0.9rem; color: #94A3B8; font-weight: 600;">⚠️ Alertas Moderados</span>
        <h2 style="font-size: 2.3rem; margin: 0.4rem 0; color: #F59E0B;">{active_moderate}</h2>
        <span style="font-size: 0.8rem; color: #F59E0B;">Acompanhamento preventivo</span>
    </div>
    """, unsafe_allow_html=True)

with col4:
    ira_class = "ira-baixo" if avg_ira < 40 else "ira-moderado" if avg_ira < 70 else "ira-critico"
    glow_class = "glow-green" if avg_ira < 40 else "glow-yellow" if avg_ira < 70 else "glow-red"
    st.markdown(f"""
    <div class="glass-card {glow_class}" style="text-align: center;">
        <span style="font-size: 0.9rem; color: #94A3B8; font-weight: 600;">✅ IRA Médio</span>
        <h2 class="{ira_class}" style="font-size: 2.3rem; margin: 0.4rem 0;">{avg_ira:.1f}</h2>
        <span style="font-size: 0.8rem; color: #94A3B8;">Meta assistencial &lt; 40.0</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# ============ SEÇÃO DE ANÁLISE GRÁFICA ============
g_col1, g_col2 = st.columns([1, 1.8])

with g_col1:
    st.markdown("<div class='glass-card' style='height: 480px;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0; margin-bottom:1.5rem; color:#A78BFA;'>Indicador de Risco (IRA Médio)</h4>", unsafe_allow_html=True)
    
    # Criar Gauge Chart usando Plotly
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_ira,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Índice de Risco Assistencial", 'font': {'size': 14, 'color': '#94A3B8'}},
        number={'font': {'size': 36, 'color': '#F1F5F9'}, 'suffix': "%"},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#94A3B8"},
            'bar': {'color': "#7C3AED", 'thickness': 0.3},
            'bgcolor': "rgba(30, 41, 59, 0.5)",
            'borderwidth': 1,
            'bordercolor': "rgba(255,255,255,0.05)",
            'steps': [
                {'range': [0, 40], 'color': 'rgba(16, 185, 129, 0.15)'},
                {'range': [40, 70], 'color': 'rgba(245, 158, 11, 0.15)'},
                {'range': [70, 100], 'color': 'rgba(239, 68, 68, 0.15)'}
            ],
            'threshold': {
                'line': {'color': "#EF4444", 'width': 3},
                'thickness': 0.75,
                'value': avg_ira
            }
        }
    ))
    fig_gauge.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=30, b=10),
        height=320
    )
    st.plotly_chart(fig_gauge, use_container_width=True)
    
    # Descritivo curto do estado do IRA
    if avg_ira < 40:
        st.markdown("<p style='text-align: center; color: #10B981;'>🟢 Risco médio sob controle. Protocolos assistenciais adequados.</p>", unsafe_allow_html=True)
    elif avg_ira < 70:
        st.markdown("<p style='text-align: center; color: #F59E0B;'>🟡 Risco moderado. Necessário reforçar verificação de conforto obstétrico.</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='text-align: center; color: #EF4444;'>🔴 Risco assistencial alto! Auditoria urgente das sessões ativas recomendada.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with g_col2:
    st.markdown("<div class='glass-card' style='height: 480px;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0; margin-bottom:1rem; color:#A78BFA;'>Evolução Histórica do IRA</h4>", unsafe_allow_html=True)
    
    # Criar dados de tendência histórica fictícios para plotar de acordo com as sessões existentes
    dates = []
    scores = []
    titles = []
    
    # Ordenar sessões completadas por data
    completed_sorted = sorted(completed_sessions, key=lambda s: s["created_at"])
    for s in completed_sorted:
        dates.append(datetime.fromisoformat(s["created_at"].replace("Z", "+00:00")).strftime("%d/%m — %H:%M"))
        scores.append(s["ira_score"])
        titles.append(s["title"])
        
    if len(dates) < 2:
        # Adicionar alguns pontos extras de exemplo caso haja poucas sessões
        base_date = datetime.now() - timedelta(days=5)
        dates = [ (base_date + timedelta(days=i)).strftime("%d/%m") for i in range(5) ] + dates
        scores = [25.0, 38.0, 54.0, 31.0, 42.0] + scores
        titles = ["Cesárea Demo 1", "Consulta Demo 2", "Parto Normal Demo 3", "Parto Demo 4", "Cesárea Demo 5"] + titles
    
    df_trend = pd.DataFrame({
        "Sessão": titles,
        "Data": dates,
        "IRA (%)": scores
    })
    
    fig_trend = px.line(
        df_trend, 
        x="Data", 
        y="IRA (%)", 
        hover_data=["Sessão"],
        markers=True,
        color_discrete_sequence=["#8B5CF6"]
    )
    fig_trend.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(30, 41, 59, 0.2)',
        font=dict(color="#94A3B8"),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", range=[0, 100]),
        height=350
    )
    st.plotly_chart(fig_trend, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ============ ALERTAS EM DESTAQUE ============
st.markdown("<h4 style='color: #F1F5F9; margin-bottom: 1rem;'>🚨 Alertas Críticos Recentes</h4>", unsafe_allow_html=True)

critical_alerts = [a for a in alerts if a["severity"] == "critical" and not a["is_acknowledged"]][:3]

if not critical_alerts:
    st.info("Nenhum alerta crítico ativo pendente de reconhecimento.")
else:
    for a in critical_alerts:
        created_time = datetime.fromisoformat(a["created_at"].replace("Z", "+00:00")).strftime("%d/%m/%Y às %H:%M")
        st.markdown(f"""
        <div class="alert-card alert-critical">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h5 style="margin: 0; color: #EF4444; font-size: 1.1rem; font-weight: 600;">{a['title']}</h5>
                <span style="font-size: 0.8rem; background: rgba(239, 68, 68, 0.15); color: #EF4444; padding: 0.2rem 0.6rem; border-radius: 4px; font-weight: 600;">IRA: {a['ira_score']}%</span>
            </div>
            <p style="margin: 0.5rem 0 0.2rem 0; font-size: 0.95rem; color: #E2E8F0;">{a['description']}</p>
            <div style="font-size: 0.8rem; color: #94A3B8; display: flex; justify-content: space-between; margin-top: 0.5rem;">
                <span>Sessão Ref: #{a['session_id']}</span>
                <span>Gerado em: {created_time}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
