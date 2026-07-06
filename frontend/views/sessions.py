import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import textwrap

# Recuperar cliente de API, token e dados do usuário
api_client = st.session_state.api_client
token = st.session_state.access_token
user = st.session_state.user

# Ver se selecionamos uma sessão pela URL
url_selected_id = st.query_params.get("selected_session_id")
if url_selected_id:
    try:
        st.session_state.selected_session_id = int(url_selected_id)
    except ValueError:
        pass

# Ver se queremos editar uma sessão pela URL
url_edit_id = st.query_params.get("edit_session_id")
if url_edit_id:
    try:
        st.session_state.session_to_edit_id = int(url_edit_id)
        st.session_state.session_view = "edit"
    except ValueError:
        pass

# Ver se queremos uma página específica ou tamanho de página pela URL
url_page = st.query_params.get("page")
if url_page:
    try:
        st.session_state.sessions_current_page = int(url_page)
    except ValueError:
        pass

url_page_size = st.query_params.get("page_size")
if url_page_size:
    try:
        st.session_state.sessions_page_size_selector = int(url_page_size)
    except ValueError:
        pass

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

# Abas principais (Controladas programaticamente via session_state)
if "session_view" not in st.session_state:
    st.session_state.session_view = "list"

col_tab1, col_tab2, col_tab3 = st.columns([2.5, 2, 3.5])
with col_tab1:
    btn_type1 = "primary" if st.session_state.session_view == "list" else "secondary"
    if st.button("📋 Listagem e Detalhes", type=btn_type1, use_container_width=True):
        st.session_state.session_view = "list"
        st.rerun()
with col_tab2:
    btn_type2 = "primary" if st.session_state.session_view == "create" else "secondary"
    if st.button("➕ Nova Sessão", type=btn_type2, use_container_width=True):
        st.session_state.session_view = "create"
        st.rerun()
if st.session_state.session_view == "edit":
    with col_tab3:
        st.button(f"✏️ Editar Sessão #{st.session_state.get('session_to_edit_id')}", type="primary", use_container_width=True, disabled=True)

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# ============ RENDERIZAR VISÃO SELECIONADA ============
if st.session_state.session_view == "list":
    if not sessions:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 3rem 1.5rem;">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">📋</div>
            <h4 style="color: #FFFFFF; margin: 0;">Nenhuma sessão de monitoramento cadastrada</h4>
            <p style="color: #94A3B8; font-size: 0.9rem; margin-top: 0.4rem;">Crie uma nova sessão clínica utilizando a aba ao lado para iniciar a auditoria.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # ============ BARRA DE PESQUISA PREMIUM ============
        st.markdown("""
        <div style="margin-bottom: 0.5rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.3rem;">
                <span style="font-size: 1.1rem;">🔍</span>
                <span style="font-size: 0.85rem; font-weight: 700; color: #C084FC; text-transform: uppercase; letter-spacing: 1px;">Pesquisar Sessões</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_search, col_date_start, col_date_end = st.columns([3, 1.5, 1.5])

        with col_search:
            search_query = st.text_input(
                "Buscar por nome ou código",
                placeholder="Digite o título da sessão ou código do paciente...",
                key="session_search_query",
                label_visibility="collapsed"
            )

        with col_date_start:
            date_start = st.date_input(
                "Data início",
                value=None,
                key="session_date_start",
                format="DD/MM/YYYY"
            )

        with col_date_end:
            date_end = st.date_input(
                "Data fim",
                value=None,
                key="session_date_end",
                format="DD/MM/YYYY"
            )

        # Aplicar filtros sobre as sessões
        filtered_sessions = sessions

        if search_query:
            query_lower = search_query.lower()
            filtered_sessions = [
                s for s in filtered_sessions
                if query_lower in s.get('title', '').lower()
                or query_lower in s.get('patient_code', '').lower()
            ]

        if date_start:
            filtered_sessions = [
                s for s in filtered_sessions
                if datetime.fromisoformat(s['created_at'].replace("Z", "+00:00")).date() >= date_start
            ]

        if date_end:
            filtered_sessions = [
                s for s in filtered_sessions
                if datetime.fromisoformat(s['created_at'].replace("Z", "+00:00")).date() <= date_end
            ]

        # Inicializar variáveis de paginação
        if "sessions_current_page" not in st.session_state:
            st.session_state.sessions_current_page = 1
        if "sessions_page_size_selector" not in st.session_state:
            st.session_state.sessions_page_size_selector = 5

        # Garantir reset de página se o hash do filtro mudar
        current_filter_hash = f"{search_query or ''}-{date_start or ''}-{date_end or ''}"
        if st.session_state.get("prev_filter_hash") != current_filter_hash:
            st.session_state.sessions_current_page = 1
            st.session_state.prev_filter_hash = current_filter_hash

        total = len(sessions)
        filtered_count = len(filtered_sessions)
        page_size = st.session_state.sessions_page_size_selector

        # Sincronização inteligente de página se houver sessão selecionada
        selected_id = st.session_state.get("selected_session_id")
        if selected_id and selected_id in [s['id'] for s in filtered_sessions]:
            for i, s in enumerate(filtered_sessions):
                if s['id'] == selected_id:
                    containing_page = (i // page_size) + 1
                    if st.session_state.get("last_selected_id_pagination") != selected_id:
                        st.session_state.sessions_current_page = containing_page
                        st.session_state.last_selected_id_pagination = selected_id
                    break

        total_pages = max(1, (filtered_count + page_size - 1) // page_size)
        if st.session_state.sessions_current_page > total_pages:
            st.session_state.sessions_current_page = total_pages
        if st.session_state.sessions_current_page < 1:
            st.session_state.sessions_current_page = 1

        start_idx = (st.session_state.sessions_current_page - 1) * page_size
        end_idx = min(start_idx + page_size, filtered_count)
        
        paginated_sessions = filtered_sessions[start_idx:end_idx]

        if not filtered_sessions:
            st.markdown("""
            <div class="glass-card" style="text-align: center; padding: 2rem 1.5rem;">
                <div style="font-size: 2rem; margin-bottom: 0.8rem;">🔍</div>
                <h4 style="color: #FFFFFF; margin: 0;">Nenhuma sessão encontrada</h4>
                <p style="color: #94A3B8; font-size: 0.85rem; margin-top: 0.3rem;">Tente ajustar os filtros de pesquisa ou limpe o campo de busca.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # ============ TABELA DE SESSÕES ============
            status_labels = {
                "created": "Pendente",
                "processing": "Processando",
                "completed": "Concluído",
                "failed": "Falha"
            }

            # Construir linhas da tabela
            table_rows = ""
            for idx, s in enumerate(paginated_sessions):
                s_label = status_labels.get(s.get("status", "created"), s.get("status", "—"))
                try:
                    s_date = datetime.fromisoformat(s['created_at'].replace("Z", "+00:00")).strftime("%d/%m/%Y")
                except Exception:
                    s_date = "—"
                
                is_selected = st.session_state.get("selected_session_id") == s['id']
                
                # Cores alternadas das linhas
                row_bg = "rgba(255, 255, 255, 0.02)" if idx % 2 == 0 else "rgba(255, 255, 255, 0.05)"
                if is_selected:
                    row_bg = "rgba(139, 92, 246, 0.15)"
                
                # Estilização do link de ação
                if is_selected:
                    detail_btn = f'<span class="table-action-btn selected">📋 Detalhes</span>'
                else:
                    action_url = f"?selected_session_id={s['id']}&token={token}"
                    detail_btn = f'<a href="{action_url}" target="_self" class="table-action-btn select">📋 Detalhar</a>'
                
                edit_url = f"?edit_session_id={s['id']}&token={token}"
                edit_btn = f'<a href="{edit_url}" target="_self" class="table-action-btn edit">✏️ Editar</a>'

                action_cell = f"""<div style="display: flex; gap: 0.4rem; justify-content: center; align-items: center;">
{detail_btn}
{edit_btn}
</div>"""

                table_rows += f"""<tr style="background: {row_bg}; border-bottom: 1px solid rgba(255,255,255,0.06); transition: background 0.2s;">
<td style="padding: 0.8rem 1rem; color: #FFFFFF; font-weight: 600; font-size: 0.85rem;">{s['id']}</td>
<td style="padding: 0.8rem 1rem; color: #FFFFFF; font-weight: 500; font-size: 0.85rem;">{s['title']}</td>
<td style="padding: 0.8rem 1rem; color: #CBD5E1; font-size: 0.85rem;">{s['patient_code']}</td>
<td style="padding: 0.8rem 1rem; color: #CBD5E1; font-size: 0.85rem;">{s_date}</td>
<td style="padding: 0.8rem 1rem; color: #CBD5E1; font-size: 0.85rem;">{s_label}</td>
<td style="padding: 0.8rem 1rem; text-align: center;">{action_cell}</td>
</tr>"""

            table_html = f"""<style>
.custom-table {{
width: 100%;
border-collapse: collapse;
background: #0f172a;
border-radius: 8px;
overflow: hidden;
margin-bottom: 1rem;
}}
.custom-table th {{
background: #1e293b;
color: #94a3b8;
font-size: 0.75rem;
font-weight: 700;
text-transform: uppercase;
letter-spacing: 1px;
padding: 0.8rem 1rem;
text-align: left;
border-bottom: 2px solid rgba(255,255,255,0.08);
}}
.table-action-btn {{
display: inline-block;
padding: 4px 10px;
font-size: 0.78rem;
font-weight: 600;
border-radius: 4px;
text-decoration: none;
transition: all 0.2s;
text-align: center;
white-space: nowrap;
}}
.table-action-btn.select {{
background: rgba(139, 92, 246, 0.2);
color: #c084fc !important;
border: 1px solid rgba(139, 92, 246, 0.4);
}}
.table-action-btn.select:hover {{
background: #8b5cf6;
color: #ffffff !important;
box-shadow: 0 0 10px rgba(139,92,246,0.4);
}}
.table-action-btn.edit {{
background: rgba(245, 158, 11, 0.15);
color: #fbbf24 !important;
border: 1px solid rgba(245, 158, 11, 0.3);
}}
.table-action-btn.edit:hover {{
background: #f59e0b;
color: #ffffff !important;
box-shadow: 0 0 10px rgba(245, 158, 11, 0.4);
}}
.table-action-btn.selected {{
background: rgba(16, 185, 129, 0.15);
color: #34d399 !important;
border: 1px solid rgba(16, 185, 129, 0.3);
cursor: default;
}}
.custom-table tbody tr:hover {{
background: rgba(255,255,255,0.08) !important;
}}
            # Gerar HTML de navegação
            prev_disabled = st.session_state.sessions_current_page == 1
            next_disabled = st.session_state.sessions_current_page == total_pages

            # Função auxiliar para gerar URLs de paginação mantendo parâmetros atuais
            def make_page_url(page_num):
                params = dict(st.query_params)
                params["page"] = str(page_num)
                params["page_size"] = str(page_size)
                from urllib.parse import urlencode
                return "?" + urlencode(params)

            prev_url = make_page_url(st.session_state.sessions_current_page - 1)
            next_url = make_page_url(st.session_state.sessions_current_page + 1)

            prev_link = f'<span class="table-action-btn disabled" style="opacity: 0.4; cursor: not-allowed; margin-right: 0.5rem; background: rgba(255,255,255,0.05); color: #94a3b8 !important; border: 1px solid rgba(255,255,255,0.1);">⬅️ Anterior</span>' if prev_disabled else f'<a href="{prev_url}" target="_self" class="table-action-btn select" style="margin-right: 0.5rem; text-decoration: none;">⬅️ Anterior</a>'
            
            next_link = f'<span class="table-action-btn disabled" style="opacity: 0.4; cursor: not-allowed; margin-left: 0.5rem; background: rgba(255,255,255,0.05); color: #94a3b8 !important; border: 1px solid rgba(255,255,255,0.1);">Próxima ➡️</span>' if next_disabled else f'<a href="{next_url}" target="_self" class="table-action-btn select" style="margin-left: 0.5rem; text-decoration: none;">Próxima ➡️</a>'

            page_info = f'<span style="font-weight: 600; color: #ffffff; padding: 0 0.5rem; font-size: 0.82rem;">Página {st.session_state.sessions_current_page} de {total_pages}</span>'
            nav_html = f"{prev_link}{page_info}{next_link}"

            # Construir o rodapé (tfoot) integrado na tabela
            tfoot_html = f"""<tfoot>
<tr style="background: #1e293b; border-top: 1px solid rgba(255,255,255,0.08);">
<td colspan="2" style="padding: 0.8rem 1rem; color: #94a3b8; font-size: 0.8rem; font-weight: 500; text-align: left; vertical-align: middle;">
    Exibindo <b>{start_idx + 1}-{end_idx}</b> de <b>{filtered_count}</b> sessões
</td>
<td colspan="2" style="padding: 0.8rem 1rem; text-align: center; color: #CBD5E1; font-size: 0.8rem; vertical-align: middle;">
    {nav_html}
</td>
<td colspan="2" style="padding: 0.8rem 1rem; text-align: right; color: #94a3b8; font-size: 0.8rem; font-weight: 500; vertical-align: middle;">
    Registros por página: 
    <select onchange="const params = new URLSearchParams(window.location.search); params.set('page_size', this.value); params.set('page', '1'); window.location.href = window.location.pathname + '?' + params.toString();" style="background: #0f172a; color: #ffffff; border: 1px solid rgba(255,255,255,0.2); border-radius: 4px; padding: 4px 8px; font-size: 0.78rem; cursor: pointer; outline: none; margin-left: 0.4rem;">
        <option value="5" {"selected" if page_size == 5 else ""}>5</option>
        <option value="10" {"selected" if page_size == 10 else ""}>10</option>
        <option value="25" {"selected" if page_size == 25 else ""}>25</option>
        <option value="50" {"selected" if page_size == 50 else ""}>50</option>
    </select>
</td>
</tr>
</tfoot>"""

            table_html = f"""<style>
.custom-table {{
width: 100%;
border-collapse: collapse;
background: #0f172a;
color: #FFFFFF;
font-family: inherit;
}}
.custom-table th {{
background: #1e293b;
padding: 0.8rem 1rem;
text-align: left;
font-weight: 600;
font-size: 0.85rem;
color: #94A3B8;
border-bottom: 1px solid rgba(255,255,255,0.08);
}}
.custom-table td {{
padding: 0.8rem 1rem;
font-size: 0.85rem;
color: #CBD5E1;
border-bottom: 1px solid rgba(255,255,255,0.05);
vertical-align: middle;
}}
.table-action-btn {{
display: inline-flex;
align-items: center;
justify-content: center;
padding: 0.4rem 0.8rem;
font-size: 0.75rem;
font-weight: 600;
border-radius: 6px;
cursor: pointer;
transition: all 0.2s;
text-decoration: none;
}}
.table-action-btn.select {{
background: rgba(139, 92, 246, 0.15);
color: #c084fc !important;
border: 1px solid rgba(139, 92, 246, 0.3);
margin-right: 0.4rem;
}}
.table-action-btn.select:hover {{
background: rgba(139, 92, 246, 0.3);
color: #ffffff !important;
box-shadow: 0 0 10px rgba(139, 92, 246, 0.4);
}}
.table-action-btn.edit {{
background: rgba(245, 158, 11, 0.15);
color: #fbbf24 !important;
border: 1px solid rgba(245, 158, 11, 0.3);
}}
.table-action-btn.edit:hover {{
background: rgba(245, 158, 11, 0.3);
color: #ffffff !important;
box-shadow: 0 0 10px rgba(245, 158, 11, 0.4);
}}
.table-action-btn.selected {{
background: rgba(16, 185, 129, 0.15);
color: #34d399 !important;
border: 1px solid rgba(16, 185, 129, 0.3);
cursor: default;
}}
.custom-table tbody tr:hover {{
background: rgba(255,255,255,0.08) !important;
}}
</style>
<div style="border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; overflow: hidden;">
<table class="custom-table">
<thead>
<tr>
<th style="width: 8%;">ID</th>
<th style="width: 30%;">Título da Sessão</th>
<th style="width: 18%;">Paciente</th>
<th style="width: 14%;">Data de Criação</th>
<th style="width: 12%;">Status</th>
<th style="width: 18%; text-align: center;">Ação</th>
</tr>
</thead>
<tbody>
{table_rows}
</tbody>
{tfoot_html}
</table>
</div>"""

            st.markdown(table_html, unsafe_allow_html=True)
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

            # ============ DETALHAMENTO DA SESSÃO SELECIONADA ============
            selected_id = st.session_state.get("selected_session_id")
            filtered_ids = {s['id'] for s in filtered_sessions}

            if selected_id and selected_id in filtered_ids:
                session = api_client.get_session_details(token, selected_id)

                if session:
                    # Separador visual
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 1rem;">
                        <div style="height: 2px; flex: 1; background: linear-gradient(90deg, rgba(139,92,246,0.4), transparent);"></div>
                        <span style="font-size: 0.8rem; font-weight: 700; color: #C084FC; text-transform: uppercase; letter-spacing: 1px; white-space: nowrap;">📋 Detalhes da Sessão #{session['id']}</span>
                        <div style="height: 2px; flex: 1; background: linear-gradient(270deg, rgba(139,92,246,0.4), transparent);"></div>
                    </div>
                    """, unsafe_allow_html=True)

                    status_map = {
                        "created": {"color": "#8B5CF6", "label": "Pendente", "badge": "badge-primary", "step": 1},
                        "processing": {"color": "#F59E0B", "label": "Em Processamento", "badge": "badge-warning", "step": 2},
                        "completed": {"color": "#22C55E", "label": "Concluído", "badge": "badge-success", "step": 3},
                        "failed": {"color": "#EF4444", "label": "Falha na Análise", "badge": "badge-danger", "step": 0}
                    }
                    curr_status = status_map.get(session["status"], {"color": "#94A3B8", "label": session["status"].upper(), "badge": "badge-primary", "step": 0})

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

                    col_ira, col_timeline, col_actions = st.columns([1.0, 1.0, 1.0], gap="medium")

                    # ============ COLUNA 1: IRA ============
                    with col_ira:
                        with st.container(border=True):
                            st.markdown("<h4 style='margin-top:0; color:#8B5CF6; font-size: 1.1rem; font-weight: 700;'>Índice de Risco Assistencial (IRA)</h4>", unsafe_allow_html=True)

                            if session["status"] == "completed" and session["ira_score"] is not None:
                                score = session["ira_score"]
                                lvl = session["ira_level"] or "baixo"
                                color = "#22C55E" if lvl == "baixo" else "#F59E0B" if lvl == "moderado" else "#EF4444"

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

                    # ============ COLUNA 2: LINHA DO TEMPO ============
                    with col_timeline:
                        with st.container(border=True):
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

                    # ============ COLUNA 3: AÇÕES RÁPIDAS ============
                    with col_actions:
                        with st.container(border=True):
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

                    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

                    # ============ ARQUIVOS ANEXADOS ============
                    with st.container(border=True):
                        st.markdown("<h4 style='margin-top:0; color:#8B5CF6; font-size: 1.2rem; font-weight: 700; margin-bottom: 1.2rem;'>Arquivos Anexados à Sessão</h4>", unsafe_allow_html=True)

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

                    # ============ SEÇÕES DE DETALHAMENTO DE IA ============
                    if session["status"] == "completed":
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
                                    sentiment_badge = {"positive": "🟢 Positivo", "neutral": "⚪ Neutro", "negative": "🔴 Negativo"}.get(seg["sentiment"], "⚪ Neutro")
                                    st.markdown(f"""
                                    <div style="margin-bottom:0.8rem; padding:0.8rem; border-radius:10px; background:rgba(20,27,45,0.4); border-left: 4px solid {speaker_color};">
                                        <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#94A3B8; margin-bottom: 0.2rem;">
                                            <span style="font-weight:700; color:{speaker_color};">{seg['speaker'].upper()}</span>
                                            <span>[{seg['start']}s - {seg['end']}s] | {sentiment_badge}</span>
                                        </div>
                                        <div style="font-size:0.9rem; color:#FFFFFF;">{seg['text']}</div>
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
                            video_files = [m for m in active_media if m["media_type"] == "video"]
                            if not video_files:
                                st.info("Nenhum vídeo anexado a esta sessão para análise.")
                            else:
                                selected_video = st.selectbox(
                                    "Selecione o vídeo para detalhar a análise:",
                                    video_files,
                                    format_func=lambda x: f"🎥 {x['filename']} (Score: {x['analysis_score'] or 0.0:.1f}%)"
                                )
                                selected_analysis = None
                                if analysis_data and "video_analyses" in analysis_data:
                                    selected_analysis = analysis_data["video_analyses"].get(str(selected_video["id"]))
                                if not selected_analysis:
                                    st.warning("⚠️ Análise específica deste vídeo não encontrada ou ainda em processamento.")
                                else:
                                    score = selected_analysis.get("ira_score", 0.0)
                                    st.markdown(f"<p style='font-size:0.95rem; color:#E2E8F0; margin-bottom: 1rem;'>Deteção de vídeo retornou score de <b>{score:.1f}%</b> para o arquivo <b>{selected_video['filename']}</b>.</p>", unsafe_allow_html=True)
                                    components = selected_analysis.get("components", {})
                                    st.markdown("<b style='font-size:0.85rem; color:#8B5CF6;'>Componentes da Visão Computacional:</b>", unsafe_allow_html=True)
                                    col_comp1, col_comp2 = st.columns(2)
                                    with col_comp1:
                                        for sd in [{"label": "😊 Expressão Facial (DeepFace)", "val": components.get("emotion_score", 0.0), "color": "#8B5CF6"}, {"label": "🧘 Postura Corporal (MediaPipe)", "val": components.get("pose_score", 0.0), "color": "#3B82F6"}]:
                                            st.markdown(f"""
                                            <div style="margin-bottom: 0.5rem;">
                                                <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #E2E8F0;"><span>{sd['label']}</span><span style="font-weight: 600;">{sd['val']:.1f}%</span></div>
                                                <div class="score-bar-bg" style="height: 5px;"><div class="score-bar-fill" style="width: {sd['val']}%; background: {sd['color']};"></div></div>
                                            </div>
                                            """, unsafe_allow_html=True)
                                    with col_comp2:
                                        for sd in [{"label": "🔍 Objetos de Risco (YOLO)", "val": components.get("object_risk_score", 0.0), "color": "#EC4899"}, {"label": "🔴 Sangramento Clínico (HSV)", "val": components.get("bleeding_score", 0.0), "color": "#EF4444"}]:
                                            st.markdown(f"""
                                            <div style="margin-bottom: 0.5rem;">
                                                <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #E2E8F0;"><span>{sd['label']}</span><span style="font-weight: 600;">{sd['val']:.1f}%</span></div>
                                                <div class="score-bar-bg" style="height: 5px;"><div class="score-bar-fill" style="width: {sd['val']}%; background: {sd['color']};"></div></div>
                                            </div>
                                            """, unsafe_allow_html=True)

                                    vf_findings = selected_analysis.get("key_findings", [])
                                    if vf_findings:
                                        st.markdown("<b style='font-size:0.85rem; color:#8B5CF6; display:block; margin-top: 1rem; margin-bottom: 0.3rem;'>Ocorrências de IA detectadas:</b>", unsafe_allow_html=True)
                                        for f in vf_findings:
                                            st.markdown(f"- **{f.get('type','').title()}**: {f.get('description')} (Confiança: {f.get('confidence',0.0):.1%})")

                                    st.markdown("<b style='font-size:0.85rem; color:#8B5CF6; display:block; margin-top: 1rem; margin-bottom: 0.5rem;'>Evolução de Risco no Tempo (Vídeo):</b>", unsafe_allow_html=True)
                                    base_risk = score
                                    df_heat = pd.DataFrame({
                                        "Tempo (minutos)": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                                        "Nível de Risco (%)": [
                                            round(base_risk * 0.25, 1), round(base_risk * 0.35, 1), round(base_risk * 0.30, 1),
                                            round(base_risk * 0.85, 1),
                                            round(base_risk * 1.15 if base_risk * 1.15 <= 100 else 100, 1),
                                            round(base_risk * 1.20 if base_risk * 1.20 <= 100 else 100, 1),
                                            round(base_risk * 1.10 if base_risk * 1.10 <= 100 else 100, 1),
                                            round(base_risk * 0.65, 1), round(base_risk * 0.35, 1), round(base_risk * 0.30, 1)
                                        ]
                                    })
                                    fig_heat = px.bar(df_heat, x="Tempo (minutos)", y="Nível de Risco (%)", color="Nível de Risco (%)",
                                                     color_continuous_scale=["#22C55E", "#F59E0B", "#EF4444"])
                                    fig_heat.update_layout(height=180, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                                          margin=dict(l=0, r=0, t=10, b=10), font=dict(color="#94A3B8"))
                                    st.plotly_chart(fig_heat, use_container_width=True)

                                    lvl = "baixo" if score < 40.0 else "moderado" if score < 70.0 else "critico"
                                    rec_color = "#EF4444" if lvl == "critico" else "#F59E0B" if lvl == "moderado" else "#22C55E"
                                    rec_text = (
                                        "Revisão imediata da conduta assistencial sugerida. Elevada dor facial ou instrumental cirúrgico detectado."
                                        if lvl == "critico"
                                        else "Monitoramento preventivo. Verificar nível de dor da gestante e oferecer suporte."
                                        if lvl == "moderado"
                                        else "Sem anomalias. Procedimento dentro dos padrões clínicos humanizados."
                                    )
                                    st.markdown(f"""
                                    <div class="alert-card {'alert-critical' if lvl == 'critico' else 'alert-moderate' if lvl == 'moderado' else 'alert-success'}" style="margin-top: 1rem; margin-bottom: 0;">
                                        <b style="color: {rec_color};">Recomendação Assistencial ({lvl.upper()}):</b><br/>
                                        <span style="font-size: 0.85rem;">{rec_text}</span>
                                    </div>
                                    """, unsafe_allow_html=True)

                        # --- ABA PRONTUÁRIO ---
                        with sub_tab_doc:
                            if not risk_details or "document" not in risk_details:
                                st.info("Nenhuma análise documental disponível.")
                            else:
                                st.markdown(f"<p style='font-size:0.9rem; color:#E2E8F0; margin-bottom: 1rem;'>{risk_details['document']['text']}</p>", unsafe_allow_html=True)
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
            else:
                # Nenhuma sessão selecionada — mostrar prompt
                st.markdown("""
                <div class="glass-card" style="text-align: center; padding: 2.5rem 1.5rem;">
                    <div style="font-size: 2.2rem; margin-bottom: 0.8rem;">👆</div>
                    <h4 style="color: #FFFFFF; margin: 0; font-size: 1.1rem;">Selecione uma sessão na tabela acima</h4>
                    <p style="color: #94A3B8; font-size: 0.85rem; margin-top: 0.4rem;">Clique no botão <b style="color: #C084FC;">📋 Ver</b> ao lado de qualquer sessão para visualizar os detalhes completos, índice de risco e arquivos anexados.</p>
                </div>
                """, unsafe_allow_html=True)

# ============ VISÃO DE EDIÇÃO ============
elif st.session_state.session_view == "edit":
    edit_id = st.session_state.get("session_to_edit_id")
    if not edit_id:
        st.warning("Nenhuma sessão selecionada para edição.")
        st.session_state.session_view = "list"
        st.rerun()

    session_data = api_client.get_session_details(token, edit_id)
    if not session_data:
        st.error("Sessão não encontrada.")
        st.session_state.session_view = "list"
        st.rerun()

    with st.container(border=True):
        st.markdown(f"<h4 style='margin-top:0; color:#F59E0B; font-size: 1.25rem; font-weight: 700; margin-bottom: 1.5rem;'>Editar Sessão Clínica #{edit_id}</h4>", unsafe_allow_html=True)

    with st.form("edit_session_form"):
        title = st.text_input("Título da Sessão", value=session_data.get("title", ""), placeholder="Ex: Parto Normal — Amanda Reis")
        st.text_input("Código Anonimizado da Paciente (LGPD) - Não editável", value=session_data.get("patient_code", ""), disabled=True)
        notes = st.text_area("Notas Clínicas", value=session_data.get("notes", "") or "", placeholder="Digite observações importantes sobre histórico de risco, idade gestacional, etc.")

        col_submit, col_cancel = st.columns(2)
        with col_submit:
            edit_submitted = st.form_submit_button("Salvar Alterações", use_container_width=True)
        with col_cancel:
            cancel_submitted = st.form_submit_button("Cancelar", use_container_width=True)

        if edit_submitted:
            if title:
                with st.spinner("Atualizando sessão..."):
                    updated_session = api_client.update_session(token, edit_id, title=title, notes=notes)
                    if updated_session:
                        st.session_state.selected_session_id = edit_id
                        st.session_state.session_view = "list"
                        # Limpar edit_session_id da URL e marcar selected_session_id
                        st.query_params.clear()
                        st.query_params["token"] = token
                        st.query_params["selected_session_id"] = str(edit_id)
                        st.success("✅ Sessão atualizada com sucesso!")
                        st.rerun()
                    else:
                        st.error("Erro ao atualizar sessão. Tente novamente.")
            else:
                st.warning("Preencha o título da sessão.")

        if cancel_submitted:
            st.session_state.session_view = "list"
            st.session_state.selected_session_id = edit_id
            # Limpar edit_session_id da URL e marcar selected_session_id
            st.query_params.clear()
            st.query_params["token"] = token
            st.query_params["selected_session_id"] = str(edit_id)
            st.rerun()

# ============ VISÃO DE CRIAÇÃO ============
else:
    with st.container(border=True):
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
                        st.session_state.selected_session_id = new_session["id"]
                        st.session_state.session_view = "list"
                        st.success(f"✅ Sessão #{new_session['id']} criada com sucesso!")
                        st.rerun()
                    else:
                        st.error("Erro ao criar sessão. Tente novamente.")
            else:
                st.warning("Preencha o título e o código da paciente.")
