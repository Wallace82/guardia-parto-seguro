import streamlit as st
import time
import io
from datetime import datetime

# Recuperar cliente de API e token
api_client = st.session_state.api_client
token = st.session_state.access_token
user = st.session_state.user

st.markdown("<h1 class='main-title'>📄 Relatórios e Auditoria</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Exporte relatórios de sessão em PDF ou relatórios executivos em Excel com autenticação por hash de integridade</p>", unsafe_allow_html=True)

# Buscar sessões
sessions = api_client.get_sessions(token, role=user.get("role"))
completed_sessions = [s for s in sessions if s["status"] == "completed"]

if not completed_sessions:
    st.info("⚠️ É necessário ter ao menos uma sessão com análise COMPLETA para gerar relatórios.")
else:
    with st.container(border=True):
        st.markdown("<h4 style='margin-top:0; color:#A78BFA;'>Parâmetros de Geração</h4>", unsafe_allow_html=True)
    
    with st.form("generate_report_form"):
        # Seletor de sessão
        session_options = {f"#{s['id']} — {s['title']} ({s['patient_code']})": s['id'] for s in completed_sessions}
        selected_session_label = st.selectbox("Selecione a Sessão:", list(session_options.keys()))
        selected_session_id = session_options[selected_session_label]
        
        # Formato e Opções
        report_format = st.radio(
            "Formato do Relatório",
            ["pdf", "excel"],
            format_func=lambda x: "📄 PDF — Relatório Clínico Detalhado (Sessão)" if x == "pdf" else "📊 Excel — Relatório Executivo Analítico (Múltiplas Sessões)",
            horizontal=True
        )
        
        col1, col2 = st.columns(2)
        with col1:
            inc_trans = st.checkbox("Incluir Transcrição da Voz", value=True)
        with col2:
            inc_frames = st.checkbox("Incluir Frames de Sofrimento Facial", value=True)
            
        generate_submitted = st.form_submit_button("Gerar Relatório Autenticado", use_container_width=True)
        
        if generate_submitted:
            st.session_state.generating_report = {
                "session_id": selected_session_id,
                "format": report_format,
                "inc_trans": inc_trans,
                "inc_frames": inc_frames,
                "step": "request"
            }
            st.rerun()

    # Processamento de geração (Simulador visual e chamada à API)
    if "generating_report" in st.session_state:
        rep_config = st.session_state.generating_report
        
        with st.container(border=True):
            st.markdown(f"#### ⚙️ Processando geração para a Sessão #{rep_config['session_id']}...", unsafe_allow_html=True)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Chamada da API
        with st.spinner("Solicitando ao Report Service..."):
            req_res = api_client.generate_report(
                token, 
                rep_config["session_id"], 
                format=rep_config["format"],
                include_transcription=rep_config["inc_trans"],
                include_key_frames=rep_config["inc_frames"]
            )
            report_id = req_res.get("report_id")
            
        if report_id:
            # Simulação visual de progresso (para dar feedback estético ao usuário)
            for percent_complete in range(0, 101, 20):
                time.sleep(0.3)
                progress_bar.progress(percent_complete)
                if percent_complete < 40:
                    status_text.text("🔍 Carregando dados da sessão e mídias analisadas...")
                elif percent_complete < 80:
                    status_text.text("✍️ Estruturando layout e renderizando gráficos de IRA...")
                elif percent_complete < 100:
                    status_text.text("🔒 Calculando assinatura criptográfica SHA-256...")
                else:
                    status_text.text("✅ Pronto!")
            
            # Buscar detalhes finais
            report_details = api_client.get_report_details(token, report_id)
            
            st.success("🎉 Relatório gerado com sucesso!")
            
            # Exibir metadados de auditoria e segurança
            st.markdown(f"""
            <div style="background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2); padding: 1.2rem; border-radius: 8px; margin-top: 1rem;">
                <h5 style="color: #10B981; margin: 0 0 0.5rem 0; font-weight:600;">🔐 Selo de Integridade e Auditoria</h5>
                <p style="margin: 0.2rem 0; font-size: 0.9rem; color: #E2E8F0;">
                    <b>Nome do Arquivo:</b> {report_details['title']}.{report_details['report_format']}
                </p>
                <p style="margin: 0.2rem 0; font-size: 0.9rem; color: #E2E8F0;">
                    <b>Hash SHA-256:</b> <code style="background:rgba(0,0,0,0.3); padding:0.15rem 0.4rem; border-radius:4px; font-family:monospace; color:#E2E8F0;">{report_details['file_hash_sha256']}</code>
                </p>
                <p style="margin: 0.2rem 0; font-size: 0.85rem; color: #94A3B8;">
                    Gerado em: {datetime.fromisoformat(report_details['generated_at'].replace("Z", "+00:00")).strftime("%d/%m/%Y às %H:%M")} | Expira em: 24 horas.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
            
            # Download Real de arquivos gerados pelo report-service
            with st.spinner("Baixando arquivo gerado..."):
                file_bytes = api_client.download_report_file(token, report_details["download_url"])
            
            if file_bytes:
                if rep_config["format"] == "pdf":
                    mime_type = "application/pdf"
                    file_name = f"Relatorio_Clinico_Sessao_{rep_config['session_id']}.pdf"
                else:
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    file_name = f"Relatorio_Executivo_Sessao_{rep_config['session_id']}.xlsx"
                
                st.download_button(
                    label=f"💾 Baixar Arquivo ({rep_config['format'].upper()})",
                    data=file_bytes,
                    file_name=file_name,
                    mime=mime_type,
                    use_container_width=True
                )
            else:
                st.error("Erro ao baixar o arquivo gerado do servidor. Baixando versão de demonstração (fallback)...")
                # Fallback em caso de falha de download
                if rep_config["format"] == "pdf":
                    fallback_data = b"%PDF-1.4 ... (Demo Fallback) ..."
                    mime_type = "application/pdf"
                    file_name = f"Relatorio_Clinico_Sessao_{rep_config['session_id']}.pdf"
                else:
                    fallback_data = b"ID,Title,IRA_Score,Risk_Level\n101,Parto Clara,78.5,critico"
                    mime_type = "text/csv"
                    file_name = f"Relatorio_Executivo_Sessao_{rep_config['session_id']}.csv"
                st.download_button(
                    label=f"💾 Baixar Arquivo Demonstrativo ({rep_config['format'].upper()})",
                    data=fallback_data,
                    file_name=file_name,
                    mime=mime_type,
                    use_container_width=True
                )
            
            # Limpar estado de geração
            del st.session_state.generating_report
        else:
            st.error("Erro ao gerar relatório. O Report Service retornou uma falha.")
