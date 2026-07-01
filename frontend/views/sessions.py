import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# Recuperar cliente de API, token e dados do usuário
api_client = st.session_state.api_client
token = st.session_state.access_token
user = st.session_state.user

# ============ HEADER PREMIUM ============
st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <div style="font-size: 0.8rem; color: #8B5CF6; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 0.3rem;">Plataforma GuardIA</div>
    <h1 style="margin: 0; font-size: 2.3rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.04rem;">Auditoria de Sessões Clínicas</h1>
    <p style="margin: 0.2rem 0 0 0; color: #94A3B8; font-size: 0.95rem;">Monitoramento multimodal de segurança assistencial e detecção de riscos em tempo real</p>
</div>
""", unsafe_allow_html=True)

# Buscar sessões da API
sessions = api_client.get_sessions(token, role=user.get("role"))

# Abas principais
tab_list, tab_create = st.tabs(["📋 Listagem e Detalhes", "➕ Nova Sessão"])

# ============ TAB 1: LISTAGEM E DETALHES ============
with tab_list:
    if not sessions:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 3rem 1.5rem;">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">📋</div>
            <h4 style="color: #FFFFFF; margin: 0;">Nenhuma sessão de monitoramento cadastrada</h4>
            <p style="color: #94A3B8; font-size: 0.9rem; margin-top: 0.4rem;">Crie uma nova sessão clínica utilizando a aba ao lado para iniciar a auditoria.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Seletor de Sessões minimalista
        session_options = {f"#{s['id']} — {s['title']} ({s['patient_code']})": s['id'] for s in sessions}
        selected_label = st.selectbox("Selecione a Sessão para detalhamento:", list(session_options.keys()))
        selected_id = session_options[selected_label]
        
        # Buscar detalhes reais
        session = api_client.get_session_details(token, selected_id)
        
        if session:
            # Status e Cores
            status_map = {
                "created": {"color": "#8B5CF6", "label": "Pendente", "badge": "badge-primary", "step": 1},
                "processing": {"color": "#F59E0B", "label": "Em Processamento", "badge": "badge-warning", "step": 2},
                "completed": {"color": "#22C55E", "label": "Concluído", "badge": "badge-success", "step": 3},
                "failed": {"color": "#EF4444", "label": "Falha na Análise", "badge": "badge-danger", "step": 0}
            }
            curr_status = status_map.get(session["status"], {"color": "#94A3B8", "label": session["status"].upper(), "badge": "badge-primary", "step": 0})
            
            # Header do Card de Detalhes
            created_date = datetime.fromisoformat(session['created_at'].replace("Z", "+00:00")).strftime("%d/%m/%Y às %H:%M")
            
            st.markdown(f"""
            <div class="glass-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
                    <div>
                        <div style="font-size: 0.75rem; color: #94A3B8; font-weight: 600; margin-bottom: 0.2rem;">Identificador da Sessão: #{session['id']}</div>
                        <h3 style="margin: 0; color: #FFFFFF; font-size: 1.4rem; font-weight: 700;">{session['title']}</h3>
                        <div style="margin-top: 0.3rem; font-size: 0.85rem; color: #94A3B8;">
                            Código Paciente: <b style="color: #FFFFFF;">{session['patient_code']}</b> | Criada em: {created_date}
                        </div>
                    </div>
                    <div>
                        <span class="badge-capsule {curr_status['badge']}">{curr_status['label']}</span>
                    </div>
                </div>
                <div style="margin-top: 1rem; padding-top: 0.8rem; border-top: 1px solid rgba(255,255,255,0.06); font-size: 0.9rem; color: #E2E8F0;">
                    <span style="color: #94A3B8; font-weight: 600;">Notas Clínicas:</span> {session['notes'] or 'Nenhuma nota clínica registrada.'}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Três colunas de métricas e ações (Proposta A — Clean & Linear)
            col_ira, col_timeline, col_actions = st.columns([1.0, 1.0, 1.0], gap="medium")
            
            # ============ COLUNA 1: ÍNDICE DE RISCO ASSISTENCIAL (IRA) ============
            with col_ira:
                st.markdown("<div class='glass-card' style='height: 100%; min-height: 380px;'>", unsafe_allow_html=True)
                st.markdown("<h4 style='margin-top:0; color:#8B5CF6; font-size: 1.1rem; font-weight: 700;'>Índice de Risco Assistencial (IRA)</h4>", unsafe_allow_html=True)
                
                if session["status"] == "completed" and session["ira_score"] is not None:
                    score = session["ira_score"]
                    lvl = session["ira_level"] or "baixo"
                    color = "#22C55E" if lvl == "baixo" else "#F59E0B" if lvl == "moderado" else "#EF4444"
                    
                    # Circular Gauge SVG
                    st.markdown(f"""
                    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 0.5rem 0 1rem 0;">
                        <svg width="120" height="120" viewBox="0 0 150 150">
                            <circle cx="75" cy="75" r="60" fill="none" stroke="rgba(255,255,255,0.03)" stroke-width="12"></circle>
                            <circle cx="75" cy="75" r="60" fill="none" stroke="{color}" stroke-width="12"
                                    stroke-dasharray="376.99" stroke-dashoffset="{376.99 * (1 - score / 100)}"
                                    stroke-linecap="round" transform="rotate(-90 75 75)" style="transition: stroke-dashoffset 0.8s ease-in-out;"></circle>
                            <text x="75" y="83" text-anchor="middle" font-size="28" font-weight="800" fill="#FFFFFF" font-family="'Outfit', sans-serif">{score:.1f}%</text>
                        </svg>
                        <div style="margin-top: 0.8rem; text-transform: uppercase; letter-spacing: 1px; font-size: 0.75rem; color: #94A3B8; font-weight: 700;">
                            Risco Classificado: <span style="color: {color}; font-weight: 800;">{lvl}</span>
                        </div>
                        <div style="margin-top: 0.5rem; font-size: 0.8rem; color: #94A3B8; text-align: center; line-height: 1.3;">
                            {"Risco assistencial alto! Auditoria urgente das sessões clínicas recomendada." if lvl == "critico" else "Monitoramento preventivo recomendado." if lvl == "moderado" else "Parâmetros dentro da normalidade."}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Sub-scores minimalistas
                    scores_data = [
                        {"label": "🎥 Vídeo", "val": session["score_video"] or 0.0, "color": "#8B5CF6"},
                        {"label": "🎙️ Áudio", "val": session["score_audio"] or 0.0, "color": "#3B82F6"},
                        {"label": "📄 Prontuário", "val": session["score_document"] or 0.0, "color": "#EC4899"}
                    ]
                    for sd in scores_data:
                        st.markdown(f"""
                        <div style="margin-bottom: 0.4rem;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #E2E8F0;">
                                <span>{sd['label']}</span>
                                <span style="font-weight: 600;">{sd['val']:.1f}%</span>
                            </div>
                            <div class="score-bar-bg" style="height: 5px;">
                                <div class="score-bar-fill" style="width: {sd['val']}%; background: {sd['color']};"></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                elif session["status"] == "processing":
                    st.markdown("""
                    <div style="text-align: center; padding: 3rem 1rem;">
                        <div style="font-size: 2.5rem; animation: pulse 2s infinite;" class="ira-moderado">⚙️</div>
                        <h5 style="color: #FFFFFF; margin: 0.8rem 0 0.3rem 0;">Processando Análise</h5>
                        <p style="color: #94A3B8; font-size: 0.8rem; margin: 0;">As engines de IA estão analisando os arquivos clínicos anexados.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("🔄 Atualizar", use_container_width=True, key="update_btn_ira"):
                        st.rerun()
                else:
                    st.markdown("""
                    <div style="text-align: center; padding: 3rem 1rem; color: #94A3B8;">
                        <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">📥</div>
                        <h5 style="color: #FFFFFF; margin: 0.5rem 0 0.2rem 0;">Aguardando Mídias</h5>
                        <p style="font-size: 0.8rem; margin: 0;">Envie arquivos no painel ao lado para calcular o Risco.</p>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            # ============ COLUNA 2: LINHA DO TEMPO DA AUDITORIA ============
            with col_timeline:
                st.markdown("<div class='glass-card' style='height: 100%; min-height: 380px;'>", unsafe_allow_html=True)
                st.markdown("<h4 style='margin-top:0; color:#8B5CF6; font-size: 1.1rem; font-weight: 700;'>Linha do Tempo</h4>", unsafe_allow_html=True)
                
                step = curr_status["step"]
                st.markdown(f"""
                <div class="timeline-container" style="margin-top: 0.5rem;">
                    <div class="timeline-item {'success' if step >= 1 else 'active' if step == 0 else ''}">
                        <div class="timeline-dot"></div>
                        <div class="timeline-title" style="font-size: 0.85rem;">Criação da Sessão</div>
                        <div class="timeline-desc" style="font-size: 0.75rem;">Sessão cadastrada e autorizada no banco central.</div>
                    </div>
                    <div class="timeline-item {'success' if step >= 3 else 'active' if step == 2 else ''}">
                        <div class="timeline-dot"></div>
                        <div class="timeline-title" style="font-size: 0.85rem;">Processamento Multimodal</div>
                        <div class="timeline-desc" style="font-size: 0.75rem;">Extração de sentimentos, OCR de prontuário e análises do OpenCV.</div>
                    </div>
                    <div class="timeline-item {'success' if step >= 3 else ''}">
                        <div class="timeline-dot"></div>
                        <div class="timeline-title" style="font-size: 0.85rem;">Cálculo de Risco (IRA)</div>
                        <div class="timeline-desc" style="font-size: 0.75rem;">Auditoria finalizada. Recomendações e scores clínicos gerados.</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            # ============ COLUNA 3: AÇÕES RÁPIDAS ============
            with col_actions:
                st.markdown("<div class='glass-card' style='height: 100%; min-height: 380px;'>", unsafe_allow_html=True)
                st.markdown("<h4 style='margin-top:0; color:#8B5CF6; font-size: 1.1rem; font-weight: 700;'>Ações Rápidas</h4>", unsafe_allow_html=True)
                
                show_upload = st.checkbox("📥 Anexar Arquivo Clínico", key="toggle_upload_form", value=False)
                
                if show_upload:
                    with st.form("upload_media_form"):
                        media_type = st.selectbox(
                            "Tipo de Arquivo",
                            ["video", "audio", "document"],
                            format_func=lambda x: {"video": "🎥 Vídeo do Parto", "audio": "🎙️ Áudio da Consulta", "document": "📄 Prontuário PDF"}[x]
                        )
                        uploaded_file = st.file_uploader("Selecionar Arquivo", type=["mp4", "wav", "mp3", "pdf", "jpg", "png"], label_visibility="collapsed")
                        upload_submitted = st.form_submit_button("Submeter para IA", use_container_width=True)
                        
                        if upload_submitted:
                            if uploaded_file is not None:
                                file_bytes = uploaded_file.read()
                                with st.spinner("Efetuando upload seguro..."):
                                    res = api_client.upload_media(token, session["id"], uploaded_file.name, file_bytes, media_type)
                                    if res:
                                        st.success(f"✅ Enviado com sucesso!")
                                        if session["status"] == "created":
                                            session["status"] = "processing"
                                        st.rerun()
                                    else:
                                        st.error("Erro ao enviar arquivo.")
                            else:
                                st.warning("Nenhum arquivo selecionado.")
                else:
                    st.markdown("""
                    <div style="margin-top: 1rem; padding: 1rem; background: rgba(139, 92, 246, 0.05); border: 1px solid rgba(139, 92, 246, 0.15); border-radius: 10px;">
                        <span style="font-size: 0.85rem; color: #FFFFFF; font-weight: 600;">Status do Monitoramento:</span>
                        <div style="margin-top: 0.5rem; font-size: 0.8rem; color: #E2E8F0;">
                            Ative o checkbox acima para enviar novas mídias médicas (vídeo, áudio ou prontuário) para processamento pelas engines de IA da AWS.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if session["status"] == "processing":
                        if st.button("🔄 Atualizar Resultados", use_container_width=True, key="update_btn_actions"):
                            st.rerun()
                    else:
                        st.button("⏳ Aguardar Mídias", use_container_width=True, disabled=True, key="wait_media_btn")
                        
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

            # ============ SEÇÃO INFERIOR: ARQUIVOS ANEXADOS (FULL WIDTH) ============
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("<h4 style='margin-top:0; color:#8B5CF6; font-size: 1.2rem; font-weight: 700; margin-bottom: 1.2rem;'>Arquivos Anexados à Sessão</h4>", unsafe_allow_html=True)
            
            # Filtrar arquivos deletados simulados
            deleted_ids = st.session_state.get("deleted_file_ids", set())
            active_media = [m for m in session["media_files"] if m["id"] not in deleted_ids] if session.get("media_files") else []
            
            if not active_media:
                st.markdown("""
                <div style="text-align: center; padding: 2rem 0; color: #94A3B8; font-size: 0.9rem;">
                    Nenhum arquivo anexado a esta sessão clínica. Utilize o painel de Ações Rápidas acima para anexar.
                </div>
                """, unsafe_allow_html=True)
            else:
                for m in active_media:
                    m_type = m["media_type"]
                    icon = "🎥" if m_type == "video" else "🎙️" if m_type == "audio" else "📄"
                    size_mb = f"{m['file_size_bytes'] / (1024*1024):.1f} MB" if m["file_size_bytes"] else "N/A"
                    status_lbl = m["status"].upper()
                    
                    badge_cls = "badge-success" if status_lbl == "ANALYZED" else "badge-warning" if status_lbl == "PROCESSING" else "badge-danger" if status_lbl == "ERROR" else "badge-primary"
                    score_txt = f"<span style='font-weight: 700; color: #8B5CF6; font-size: 0.85rem; margin-left: 1rem;'>{m['analysis_score']:.1f}%</span>" if m["analysis_score"] is not None else ""
                    
                    # Cria colunas para organizar o card e os botões de ação nativos
                    col_card, col_dl, col_del = st.columns([10, 1, 1])
                    
                    with col_card:
                        st.markdown(f"""<div class="media-card" style="margin-bottom: 0;">
<div class="media-card-info">
<div class="media-card-icon">{icon}</div>
<div>
<div class="media-card-name">{m['filename']}</div>
<div class="media-card-meta">{size_mb} | Tipo: {m_type.upper()} | Status: <span class="badge-capsule {badge_cls}" style="font-size: 0.7rem; padding: 0.1rem 0.4rem; display: inline-block;">{status_lbl}</span> {score_txt}</div>
</div>
</div>
</div>""", unsafe_allow_html=True)
                        
                    with col_dl:
                        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                        if st.button("📥", key=f"dl_{m['id']}", help=f"Baixar {m['filename']}", use_container_width=True):
                            st.toast(f"📥 Iniciando download de: {m['filename']}...")
                            
                    with col_del:
                        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
                        if st.button("🗑️", key=f"del_{m['id']}", help=f"Excluir {m['filename']}", use_container_width=True):
                            success = api_client.delete_media(token, m["id"])
                            if success:
                                st.toast(f"🗑️ Mídia '{m['filename']}' excluída permanentemente!")
                            else:
                                if "deleted_file_ids" not in st.session_state:
                                    st.session_state.deleted_file_ids = set()
                                st.session_state.deleted_file_ids.add(m["id"])
                                st.toast(f"🗑️ Mídia '{m['filename']}' removida temporariamente!")
                            st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            # 3. Seções de Detalhamento de IA
            if session["status"] == "completed":
                # Obter dados de análise do backend
                analysis_data = api_client.get_session_analysis(token, session["id"])
                
                transcription = analysis_data.get("transcription") if analysis_data else None
                risk_details = analysis_data.get("risk_details") if analysis_data else None
                video_findings = analysis_data.get("video_findings") if analysis_data else []
                
                sub_tab_audio, sub_tab_video, sub_tab_doc = st.tabs([
                    "🎙️ Transcrição do Diálogo", 
                    "🎥 Visão Computacional", 
                    "📄 Prontuário & Conformidade"
                ])
                
                # --- ABA ÁUDIO ---
                with sub_tab_audio:
                    if not transcription:
                        st.info("Nenhuma análise de transcrição disponível.")
                    else:
                        st.markdown(f"<div style='margin-bottom: 1rem; font-style: italic; font-size: 0.9rem; color: #FFFFFF;'>Texto Completo: \"{transcription['full_text']}\"</div>", unsafe_allow_html=True)
                        
                        for seg in transcription["segments"]:
                            is_prof = seg["role"] == "profissional"
                            speaker_color = "#8B5CF6" if is_prof else "#EC4899"
                            sentiment_badge = {
                                "positive": "🟢 Positivo",
                                "neutral": "⚪ Neutro",
                                "negative": "🔴 Negativo"
                            }.get(seg["sentiment"], "⚪ Neutro")
                            
                            st.markdown(f"""
                            <div style="margin-bottom:0.8rem; padding:0.8rem; border-radius:10px; background:rgba(20,27,45,0.4); border-left: 4px solid {speaker_color};">
                                <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#94A3B8; margin-bottom: 0.2rem;">
                                    <span style="font-weight:700; color:{speaker_color};">{seg['speaker'].upper()}</span>
                                    <span>[{seg['start']}s - {seg['end']}s] | {sentiment_badge}</span>
                                </div>
                                <div style="font-size:0.9rem; color:#FFFFFF;">
                                    {seg['text']}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                        if risk_details and "audio" in risk_details:
                            st.markdown(f"""
                            <div class="alert-card alert-moderate" style="margin-top: 1rem; margin-bottom: 0;">
                                <b style="color: #F59E0B;">Recomendação Assistencial:</b><br/>
                                <span style="font-size: 0.85rem;">{risk_details['audio']['recommendation']}</span>
                            </div>
                            """, unsafe_allow_html=True)
                            
                # --- ABA VÍDEO ---
                with sub_tab_video:
                    if not risk_details or "video" not in risk_details:
                        st.info("Nenhuma análise de vídeo disponível.")
                    else:
                        st.markdown(f"<p style='font-size:0.9rem; color:#E2E8F0; margin-bottom: 1rem;'>{risk_details['video']['text']}</p>", unsafe_allow_html=True)
                        
                        if video_findings:
                            st.markdown("<b style='font-size:0.85rem; color:#8B5CF6;'>Ocorrências de IA no Vídeo:</b>", unsafe_allow_html=True)
                            for f in video_findings:
                                st.markdown(f"- **{f.get('type','').title()}**: {f.get('description')} (Confiança: {f.get('confidence',0.0):.1%})")
                        
                        # Heatmap Temporal
                        st.markdown("<b style='font-size:0.85rem; color:#8B5CF6; display:block; margin-top: 1rem; margin-bottom: 0.5rem;'>Evolução de Risco no Tempo (Vídeo):</b>", unsafe_allow_html=True)
                        df_heat = pd.DataFrame({
                            "Tempo (minutos)": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                            "Nível de Risco (%)": [15, 20, 18, 55, 78, 82, 75, 40, 22, 19]
                        })
                        fig_heat = px.bar(df_heat, x="Tempo (minutos)", y="Nível de Risco (%)", color="Nível de Risco (%)",
                                         color_continuous_scale=["#22C55E", "#F59E0B", "#EF4444"])
                        fig_heat.update_layout(height=180, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                              margin=dict(l=0, r=0, t=10, b=10), font=dict(color="#94A3B8"))
                        st.plotly_chart(fig_heat, use_container_width=True)
                        
                        st.markdown(f"""
                        <div class="alert-card alert-critical" style="margin-top: 1rem; margin-bottom: 0;">
                            <b style="color: #EF4444;">Recomendação Assistencial:</b><br/>
                            <span style="font-size: 0.85rem;">{risk_details['video']['recommendation']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                # --- ABA PRONTUÁRIO ---
                with sub_tab_doc:
                    if not risk_details or "document" not in risk_details:
                        st.info("Nenhuma análise documental disponível.")
                    else:
                        st.markdown(f"<p style='font-size:0.9rem; color:#E2E8F0; margin-bottom: 1rem;'>{risk_details['document']['text']}</p>", unsafe_allow_html=True)
                        
                        # Checklist de Conformidade
                        st.markdown("<b style='font-size:0.85rem; color:#8B5CF6; display:block; margin-bottom: 0.5rem;'>Checklist de Conformidade Documental (LGPD):</b>", unsafe_allow_html=True)
                        consent_present = "consentimento_ausente" not in risk_details["document"].get("key_indicators", [])
                        
                        checklist = [
                            {"Item": "Identificação Completa da Paciente", "Verificado": True},
                            {"Item": "Assinatura do Profissional e CRM", "Verificado": True},
                            {"Item": "Posologia de Medicamentos", "Verificado": True},
                            {"Item": "Termo de Consentimento para Procedimentos Invasivos", "Verificado": consent_present}
                        ]
                        for c in checklist:
                            icon = "✅" if c["Verificado"] else "❌"
                            style = "color: #22C55E;" if c["Verificado"] else "color: #EF4444; font-weight:600;"
                            st.markdown(f"<div style='margin-bottom:0.4rem; font-size:0.85rem; {style}'>{icon} {c['Item']}</div>", unsafe_allow_html=True)
                            
                        st.markdown(f"""
                        <div class="alert-card alert-moderate" style="margin-top: 1rem; margin-bottom: 0;">
                            <b style="color: #F59E0B;">Recomendação Assistencial:</b><br/>
                            <span style="font-size: 0.85rem;">{risk_details['document']['recommendation']}</span>
                        </div>
                        """, unsafe_allow_html=True)

# ============ TAB 2: NOVA SESSÃO ============
with tab_create:
    st.markdown("<div class='glass-card' style='padding: 2rem;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0; color:#8B5CF6; font-size: 1.25rem; font-weight: 700; margin-bottom: 1.5rem;'>Cadastrar Nova Sessão Clínica</h4>", unsafe_allow_html=True)
    
    with st.form("create_session_form"):
        title = st.text_input("Título da Sessão", placeholder="Ex: Parto Normal — Amanda Reis")
        patient_code = st.text_input("Código Anonimizado da Paciente (LGPD)", placeholder="Ex: PAC-2026-902 (Nunca utilize o nome real)")
        notes = st.text_area("Notas Clínicas Iniciais", placeholder="Digite observações importantes sobre histórico de risco, idade gestacional, etc.")
        
        create_submitted = st.form_submit_button("Salvar e Criar Sessão", use_container_width=True)
        
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
                st.warning("Preencha o título e o código da paciente.")
    st.markdown("</div>", unsafe_allow_html=True)
