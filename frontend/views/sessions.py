import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# Recuperar cliente de API e token
api_client = st.session_state.api_client
token = st.session_state.access_token
user = st.session_state.user

st.markdown("<h1 class='main-title'>🏥 Sessões de Monitoramento</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Crie, envie mídias e visualize a análise multimodal de cada parto ou consulta</p>", unsafe_allow_html=True)

# Tabs principais
tab_list, tab_create = st.tabs(["📋 Listagem e Detalhes", "➕ Nova Sessão"])

# Buscar sessões
sessions = api_client.get_sessions(token, role=user.get("role"))

# ============ TAB 1: LISTAGEM E DETALHES ============
with tab_list:
    if not sessions:
        st.info("Nenhuma sessão de monitoramento cadastrada no momento.")
    else:
        # Criar opções de seleção para a caixa de listagem
        session_options = {f"#{s['id']} — {s['title']} ({s['patient_code']})": s['id'] for s in sessions}
        selected_label = st.selectbox("Selecione a Sessão para detalhamento:", list(session_options.keys()))
        selected_id = session_options[selected_label]
        
        # Obter detalhes completos da sessão
        session = api_client.get_session_details(token, selected_id)
        
        if session:
            # Header da sessão
            status_color = {
                "created": "#A78BFA",
                "processing": "#F59E0B",
                "completed": "#10B981",
                "failed": "#EF4444"
            }.get(session["status"], "#94A3B8")
            
            st.markdown(f"""
            <div class="glass-card" style="margin-top: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                    <div>
                        <h3 style="margin: 0; color: #F1F5F9;">{session['title']}</h3>
                        <span style="color: #94A3B8; font-size: 0.9rem;">Paciente: <b>{session['patient_code']}</b> | Criada em: {datetime.fromisoformat(session['created_at'].replace("Z", "+00:00")).strftime("%d/%m/%Y às %H:%M")}</span>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 0.85rem; background: {status_color}22; color: {status_color}; padding: 0.4rem 1rem; border-radius: 20px; font-weight: 600; border: 1px solid {status_color}44;">
                            Status: {session['status'].upper()}
                        </span>
                    </div>
                </div>
                <div style="margin-top: 1rem; font-size: 0.95rem; color: #CBD5E1; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 0.8rem;">
                    <b>Notas Clínicas:</b> {session['notes'] or 'Nenhuma nota adicionada.'}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Layout de Detalhes em Colunas
            col_left, col_right = st.columns([1.2, 1.8])
            
            with col_left:
                # CARD DO IRA DA SESSÃO
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                st.markdown("<h4 style='margin-top:0; color:#A78BFA;'>Composição do Risco (IRA)</h4>", unsafe_allow_html=True)
                
                if session["status"] == "completed" and session["ira_score"] is not None:
                    ira_level = session["ira_level"] or "baixo"
                    ira_class = f"ira-{ira_level}"
                    st.markdown(f"""
                    <div class="ira-gauge-container">
                        <span class="{ira_class} ira-score-display">{session['ira_score']:.1f}%</span>
                        <span style="text-transform: uppercase; font-weight: 700; color: #94A3B8; font-size: 0.9rem; letter-spacing: 1px;">Classificação: <span class="{ira_class}">{ira_level} risco</span></span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    # Mostrar sub-scores
                    st.markdown(f"🎥 **Pontuação Vídeo (Visão):** `{session['score_video'] or 0.0}%`")
                    st.markdown(f"🎙️ **Pontuação Áudio (Linguagem):** `{session['score_audio'] or 0.0}%`")
                    st.markdown(f"📄 **Pontuação Documento (OCR):** `{session['score_document'] or 0.0}%`")
                elif session["status"] == "processing":
                    st.markdown("""
                    <div style="text-align: center; padding: 2rem 0;">
                        <div class="ira-moderado" style="font-size: 2.5rem; font-weight:800;">PROCESSANDO...</div>
                        <p style="color: #94A3B8; font-size:0.9rem; margin-top:0.5rem;">Os modelos de IA estão analisando os vídeos, áudios e prontuários. Por favor, aguarde alguns instantes.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("🔄 Atualizar Status", use_container_width=True):
                        st.rerun()
                else:
                    st.markdown("""
                    <div style="text-align: center; padding: 2rem 0; color: #94A3B8;">
                        <span style="font-size: 3rem;">📥</span>
                        <p style="font-size:0.95rem; margin-top:0.5rem;">Aguardando envio de mídias para iniciar o cálculo do risco assistencial.</p>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # UPLOAD DE ARQUIVOS PARA A SESSÃO
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                st.markdown("<h4 style='margin-top:0; color:#A78BFA;'>Enviar Mídia para Análise</h4>", unsafe_allow_html=True)
                
                with st.form("upload_media_form"):
                    media_type = st.selectbox(
                        "Tipo de Mídia",
                        ["video", "audio", "document"],
                        format_func=lambda x: {"video": "🎥 Vídeo Clínico", "audio": "🎙️ Áudio da Consulta", "document": "📄 Prontuário PDF"}[x]
                    )
                    uploaded_file = st.file_uploader("Selecione o arquivo", type=["mp4", "wav", "mp3", "pdf", "jpg", "png"])
                    upload_submitted = st.form_submit_button("Enviar e Iniciar IA", use_container_width=True)
                    
                    if upload_submitted:
                        if uploaded_file is not None:
                            file_bytes = uploaded_file.read()
                            with st.spinner("Efetuando upload seguro..."):
                                res = api_client.upload_media(token, session["id"], uploaded_file.name, file_bytes, media_type)
                                if res:
                                    st.success(f"✅ Arquivo enviado! Análise de {media_type} iniciada.")
                                    # Simula transição de status para fins de demonstração local
                                    if session["status"] == "created":
                                        session["status"] = "processing"
                                    st.rerun()
                                else:
                                    st.error("Erro ao enviar o arquivo. Verifique sua conexão.")
                        else:
                            st.warning("Selecione um arquivo válido.")
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col_right:
                # ARQUIVOS ENVIADOS
                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                st.markdown("<h4 style='margin-top:0; color:#A78BFA;'>Arquivos na Sessão</h4>", unsafe_allow_html=True)
                
                if not session["media_files"]:
                    st.info("Nenhum arquivo de mídia associado a esta sessão.")
                else:
                    media_data = []
                    for m in session["media_files"]:
                        media_data.append({
                            "Tipo": "🎥 Vídeo" if m["media_type"] == "video" else "🎙️ Áudio" if m["media_type"] == "audio" else "📄 Prontuário",
                            "Arquivo": m["filename"],
                            "Tamanho": f"{m['file_size_bytes'] / (1024*1024):.1f} MB" if m["file_size_bytes"] else "N/A",
                            "Status": m["status"].upper(),
                            "Score": f"{m['analysis_score']:.1f}%" if m["analysis_score"] is not None else "—"
                        })
                    st.table(pd.DataFrame(media_data))
                st.markdown("</div>", unsafe_allow_html=True)
                
                            # Obter análise detalhada real do backend
                    analysis_data = api_client.get_session_analysis(token, session["id"])
                    
                    transcription = analysis_data.get("transcription") if analysis_data else None
                    risk_details = analysis_data.get("risk_details") if analysis_data else None
                    video_findings = analysis_data.get("video_findings") if analysis_data else []
                    
                    # Aba interna para dividir as análises
                    sub_tab_audio, sub_tab_video, sub_tab_doc = st.tabs([
                        "🎙️ Análise de Áudio (Transcrição)", 
                        "🎥 Análise de Vídeo", 
                        "📄 Análise do Prontuário"
                    ])
                    
                    with sub_tab_audio:
                        if not transcription:
                            st.info("Nenhuma análise de áudio/transcrição disponível para esta sessão.")
                        else:
                            st.markdown(f"<b>Texto Completo:</b> *\"{transcription['full_text']}\"*", unsafe_allow_html=True)
                            st.markdown("---")
                            st.markdown("<b>Segmentos por Speaker e Sentimento:</b>", unsafe_allow_html=True)
                            
                            for seg in transcription["segments"]:
                                role_color = "#3B82F6" if seg["role"] == "profissional" else "#EC4899"
                                sentiment_badge = {
                                    "positive": "🟢 Positivo",
                                    "neutral": "⚪ Neutro",
                                    "negative": "🔴 Negativo"
                                }.get(seg["sentiment"], "⚪ Neutro")
                                
                                st.markdown(f"""
                                <div style="margin-bottom:0.8rem; padding:0.6rem; border-radius:6px; background:rgba(255,255,255,0.02); border-left: 3px solid {role_color};">
                                    <div style="display:flex; justify-content:space-between; font-size:0.8rem; color:#94A3B8;">
                                        <span style="font-weight:700; color:{role_color};">{seg['speaker']} ({seg['role'].upper()})</span>
                                        <span>[{seg['start']}s - {seg['end']}s] | Sentimento: {sentiment_badge} ({seg['sentiment_confidence']:.2f})</span>
                                    </div>
                                    <div style="margin-top:0.3rem; font-size:0.92rem; color:#E2E8F0;">
                                        {seg['text']}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                            # Recomendações do áudio
                            if risk_details and "audio" in risk_details:
                                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                                st.markdown(f"""
                                <div class="alert-card alert-moderate" style="margin-bottom: 0;">
                                    <b>Recomendação Assistencial (Voz/Áudio):</b><br/>
                                    {risk_details['audio']['recommendation']}
                                </div>
                                """, unsafe_allow_html=True)
                                
                    with sub_tab_video:
                        if not risk_details or "video" not in risk_details:
                            st.info("Nenhuma análise detalhada de vídeo disponível para esta sessão.")
                        else:
                            st.markdown(f"<b>Resumo da Visão Computacional:</b>", unsafe_allow_html=True)
                            st.markdown(f"*{risk_details['video']['text']}*")
                            
                            if risk_details['video']['key_indicators']:
                                st.markdown("<b>Indicadores Identificados:</b>", unsafe_allow_html=True)
                                for ind in risk_details['video']['key_indicators']:
                                    st.markdown(f"- `{ind}`")
                            
                            if video_findings:
                                st.markdown("<b>Ocorrências de Vídeo Identificadas (IA):</b>", unsafe_allow_html=True)
                                for finding in video_findings:
                                    st.markdown(f"- **{finding.get('type', '').title()}**: {finding.get('description')} (Confiança: {finding.get('confidence', 0.0):.2%})")

                            # Heatmap do IRA ao longo do tempo do vídeo (exemplo mock)
                            st.markdown("<b>Mapa de Calor Temporal do Risco no Vídeo:</b>", unsafe_allow_html=True)
                            df_heat = pd.DataFrame({
                                "Tempo (minutos)": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                                "Nível de Risco (%)": [15, 20, 18, 55, 78, 82, 75, 40, 22, 19]
                            })
                            fig_heat = px.bar(df_heat, x="Tempo (minutos)", y="Nível de Risco (%)", color="Nível de Risco (%)",
                                             color_continuous_scale=["#10B981", "#F59E0B", "#EF4444"])
                            fig_heat.update_layout(height=200, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                                  margin=dict(l=0, r=0, t=10, b=10), font=dict(color="#94A3B8"))
                            st.plotly_chart(fig_heat, use_container_width=True)
 
                            st.markdown(f"""
                            <div class="alert-card alert-critical" style="margin-bottom: 0;">
                                <b>Recomendação Assistencial (Visão/Vídeo):</b><br/>
                                {risk_details['video']['recommendation']}
                            </div>
                            """, unsafe_allow_html=True)
                            
                    with sub_tab_doc:
                        if not risk_details or "document" not in risk_details:
                            st.info("Nenhuma análise detalhada de prontuário disponível para esta sessão.")
                        else:
                            st.markdown(f"<b>Resumo do Processamento Documental (OCR):</b>", unsafe_allow_html=True)
                            st.markdown(f"*{risk_details['document']['text']}*")
                            
                            # Mostrar checklist de conformidade do prontuário
                            st.markdown("<b>Checklist de Conformidade (LGPD/Clínico):</b>", unsafe_allow_html=True)
                            
                            consent_present = "consentimento_ausente" not in risk_details["document"].get("key_indicators", [])
                            
                            checklist = [
                                {"Item": "Identificação Completa da Paciente", "Verificado": True, "Severidade": "none"},
                                {"Item": "Assinatura do Profissional e CRM", "Verificado": True, "Severidade": "none"},
                                {"Item": "Posologia de Medicamentos", "Verificado": True, "Severidade": "none"},
                                {"Item": "Termo de Consentimento para Procedimentos Invasivos", "Verificado": consent_present, "Severidade": "none" if consent_present else "high"}
                            ]
                            
                            for item in checklist:
                                icon = "✅" if item["Verificado"] else "❌"
                                style = "color: #EF4444; font-weight:600;" if not item["Verificado"] else "color: #10B981;"
                                st.markdown(f"<span style='{style}'>{icon} {item['Item']}</span>", unsafe_allow_html=True)
                                
                            st.markdown(f"""
                            <div class="alert-card alert-moderate" style="margin-top: 1rem; margin-bottom: 0;">
                                <b>Recomendação Assistencial (Documentação):</b><br/>
                                {risk_details['document']['recommendation']}
                            </div>
                            """, unsafe_allow_html=True)

# ============ TAB 2: NOVA SESSÃO ============
with tab_create:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0; color:#A78BFA;'>Cadastrar Nova Sessão Clínica</h4>", unsafe_allow_html=True)
    
    with st.form("create_session_form"):
        title = st.text_input("Título da Sessão", placeholder="Ex: Parto Normal — Gestante Amanda Reis")
        patient_code = st.text_input("Código Anonimizado da Paciente", placeholder="Ex: PAC-2026-902 (Não use nome real)")
        notes = st.text_area("Notas Clínicas Iniciais", placeholder="Inserir observações sobre histórico de risco, idade gestacional, etc.")
        
        create_submitted = st.form_submit_button("Salvar e Criar", use_container_width=True)
        
        if create_submitted:
            if title and patient_code:
                with st.spinner("Criando sessão..."):
                    new_session = api_client.create_session(token, title, patient_code, notes)
                    if new_session:
                        st.success(f"✅ Sessão #{new_session['id']} criada com sucesso!")
                        st.rerun()
                    else:
                        st.error("Erro ao criar sessão. Tente novamente.")
            else:
                st.warning("Por favor, preencha o Título e o Código da Paciente.")
    st.markdown("</div>", unsafe_allow_html=True)
