import streamlit as st
import pandas as pd
import requests
import time
import urllib3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURAÇÃO ---
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
st.set_page_config(page_title="Team Rabamos // Intelligence", layout="wide", initial_sidebar_state="expanded")

# --- ESTILO CSS PROFISSIONAL ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #0f1923; color: #ece8e1; }
    .role-badge { padding: 5px 12px; border-radius: 4px; font-size: 11px; font-weight: bold; color: white; display: inline-block; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px;}
    .duelista { background-color: #ff4655; box-shadow: 0 0 8px rgba(255, 70, 85, 0.3); }
    .controlador { background-color: #45b3e3; box-shadow: 0 0 8px rgba(69, 179, 227, 0.3); }
    .iniciador { background-color: #f9d533; color: black; }
    .sentinela { background-color: #b388ff; box-shadow: 0 0 8px rgba(179, 136, 255, 0.3); }
    .coach-box { padding: 12px; border-radius: 6px; font-size: 12px; margin-top: 8px; line-height: 1.4; border: 1px solid rgba(255,255,255,0.05); min-height: 55px; }
    .acerto { background: rgba(54, 211, 153, 0.1); color: #36d399; border-left: 4px solid #36d399; }
    .ajuste { background: rgba(248, 114, 114, 0.1); color: #f87272; border-left: 4px solid #f87272; }
    .foco { background: rgba(69, 179, 227, 0.1); color: #45b3e3; border-left: 4px solid #45b3e3; }
    .highlight-card { background: #1b252f; padding: 20px; border-radius: 12px; border: 1px solid #313e4b; text-align: center; }
    .hl-title { color: #ff4655; font-size: 12px; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; }
    .hl-value { font-size: 24px; font-weight: 800; color: #fff; }
    .hl-desc { font-size: 11px; color: #8894a0; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAÇÃO DO SQUAD ---
API_KEY = "HDEV-3650a7f3-c881-4cbe-942b-336551fc2696"
BASE_URL = "https://api.henrikdev.xyz/valorant/v3/matches/br/"

players = [
    {"name": "Japinhaa", "tag": "3031"}, {"name": "LDS Gabriela용", "tag": "5034"},
    {"name": "Carrasco", "tag": "rolao"}, {"name": "VoidinN", "tag": "4head"},
    {"name": "Bovis", "tag": "calvo"}, {"name": "LCK", "tag": "tlck"},
    {"name": "PankaOficial", "tag": "brr"},
]

AGENT_ROLES = {
    'Jett': 'Duelista', 'Raze': 'Duelista', 'Phoenix': 'Duelista', 'Reyna': 'Duelista', 'Yoru': 'Duelista', 'Neon': 'Duelista', 'Iso': 'Duelista', 'Waylay': 'Duelista',
    'Omen': 'Controlador', 'Viper': 'Controlador', 'Brimstone': 'Controlador', 'Astra': 'Controlador', 'Harbor': 'Controlador', 'Clove': 'Controlador',
    'Sova': 'Iniciador', 'Breach': 'Iniciador', 'Skye': 'Iniciador', 'KAY/O': 'Iniciador', 'Fade': 'Iniciador', 'Gekko': 'Iniciador', 'Tejo': 'Iniciador',
    'Killjoy': 'Sentinela', 'Cypher': 'Sentinela', 'Sage': 'Sentinela', 'Chamber': 'Sentinela', 'Deadlock': 'Sentinela', 'Vyse': 'Sentinela', 'Veto': 'Sentinela'
}

def analise_inteligente(row):
    obs = {"acerto": "", "ajuste": "", "foco": ""}
    kdr = row['K'] / max(row['D'], 1)
    adr = row['ADR']
    hs = row['HS%']
    role = row['Role']
    impacto = row.get('Impacto', 1)

    if hs > 28: 
        obs["acerto"] = "Mecânica de Contato: Índice de conversão em headshots acima da média, reduzindo o TTK nos duelos."
    elif adr > 165: 
        obs["acerto"] = "Volume de Fogo: Constância na aplicação de dano, gerando pressão territorial e drenando recursos adversários."
    elif kdr > 1.3: 
        obs["acerto"] = "Letalidade e Sobrevivência: Alta eficiência em trocas diretas com manutenção de integridade tática."
    elif impacto > 1.2:
        obs["acerto"] = "Participação Ativa: Presença constante em eventos críticos do round, resultando em impacto numérico direto."
    else: 
        obs["acerto"] = "Consistência de Base: Cumprimento dos protocolos padrão da role e manutenção de posicionamento tático."

    if kdr < 0.85: 
        obs["ajuste"] = "Déficit de Troca: Necessário priorizar o 're-frag' e evitar exposição sem cobertura de um segundo jogador."
    elif adr < 125 and role == 'Duelista': 
        obs["ajuste"] = "Passividade Ofensiva: Baixa criação de espaço. Necessário maior proatividade na abertura de bomb sites."
    elif hs < 17: 
        obs["ajuste"] = "Nível de Mira: Ajustar o 'crosshair placement' para a linha da cabeça em zonas de pre-fire."
    else: 
        obs["ajuste"] = "Leitura de Mapa: Refinar o timing de rotação para evitar ser isolado em zonas de transição."

    treinos = {
        'Duelista': "Rotas de entrada (pathing), gestão de escape e coordenação de dive.",
        'Controlador': "Padrões de one-way, timing de smokes e posicionamento de 'post-plant'.",
        'Iniciador': "Combos de info + flash, estudo de lineups e timing de entrada pós-utilitário.",
        'Sentinela': "Otimização de setups de ancoragem, controle de flanco e recursos para retake."
    }
    obs["foco"] = treinos.get(role, "Fundamentos de movimentação e disciplina de mira.")
    return obs

if 'all_stats' not in st.session_state: st.session_state.all_stats = None

st.sidebar.title("🎮 Team Rabamos")
aba = st.sidebar.radio("Navegação:", ["📊 Performance do time", "📈 Estratégia e Tendências", "⚔️ HISTÓRICO"])

if st.sidebar.button("🔄 Sincronizar Dados", use_container_width=True):
    all_data = []
    pb = st.progress(0); st_txt = st.empty()
    for i, p in enumerate(players):
        st_txt.markdown(f"⏳ **Buscando:** {p['name']}...")
        retry = 0
        while retry < 2:
            try:
                res = requests.get(f"{BASE_URL}{p['name']}/{p['tag']}?size=20", headers={"Authorization": API_KEY}, timeout=30, verify=False)
                if res.status_code == 200:
                    for m in res.json().get('data', []):
                        meta = m.get('metadata', {})
                        if meta.get('mode') == "Competitive":
                            teams = m.get('teams', {})
                            for ps in m.get('players', {}).get('all_players', []):
                                if ps.get('name', '').lower() == p['name'].lower():
                                    p_team = ps.get('team', '').lower()
                                    win = (teams['blue']['rounds_won'] > teams['red']['rounds_won']) if p_team == 'blue' else (teams['red']['rounds_won'] > teams['blue']['rounds_won'])
                                    rds = max(meta.get('rounds_played', 1), 1)
                                    s = ps.get('stats', {})
                                    all_data.append({
                                        "MatchID": meta.get('matchid'), "Data": meta.get('game_start_patched'),
                                        "Mapa": meta.get('map'), "Nome": p['name'], "Agente": ps.get('character'),
                                        "Role": AGENT_ROLES.get(ps.get('character'), 'Flex'),
                                        "K": s.get('kills', 0), "D": max(s.get('deaths', 1), 1), "A": s.get('assists', 0),
                                        "ADR": ps.get('damage_made', 0)/rds, "Win": win,
                                        "HS%": (s.get('headshots', 0) / max(s.get('headshots', 0) + s.get('bodyshots', 0) + s.get('legshots', 0), 1)) * 100,
                                        "Econ": ps.get('damage_made', 0) / (rds * 10),
                                        "Placar": f"{teams['blue']['rounds_won']}x{teams['red']['rounds_won']}"
                                    })
                    break
                else: retry += 1; time.sleep(1)
            except: retry += 1; time.sleep(1)
        pb.progress((i + 1) / len(players))
    st.session_state.all_stats = pd.DataFrame(all_data)
    st_txt.success("✅ Dados sincronizados!")
    time.sleep(1); st_txt.empty(); pb.empty()

if st.session_state.all_stats is not None:
    df = st.session_state.all_stats
    df['Data'] = pd.to_datetime(df['Data'])
    player_agg = df.groupby("Nome").agg({"ADR": "mean", "K": "sum", "D": "sum", "A": "sum", "HS%": "mean", "Econ": "mean", "Role": lambda x: x.mode()[0]}).reset_index()
    player_agg['Impacto'] = (player_agg['K'] + player_agg['A']) / ((player_agg['K'] + player_agg['A']).mean() if not player_agg.empty else 1)

    if aba == "📊 Performance do time":
        st.write("### 🎖️ RECONHECIMENTO DE ELITE")
        h1, h2, h3, h4 = st.columns(4)
        with h1:
            mvp_d = player_agg.loc[player_agg['ADR'].idxmax()]
            st.markdown(f"<div class='highlight-card'><div class='hl-title'>VOLUME DE DANO</div><div class='hl-value'>{mvp_d['Nome']}</div><div class='hl-desc'>Média: {mvp_d['ADR']:.1f} ADR</div></div>", unsafe_allow_html=True)
        with h2:
            mvp_h = player_agg.loc[player_agg['HS%'].idxmax()]
            st.markdown(f"<div class='highlight-card'><div class='hl-title'>PRECISÃO (HS%)</div><div class='hl-value'>{mvp_h['HS%']:.1f}%</div><div class='hl-desc'>{mvp_h['Nome']}</div></div>", unsafe_allow_html=True)
        with h3:
            st.markdown(f"<div class='highlight-card'><div class='hl-title'>WIN RATE SQUAD</div><div class='hl-value'>{(df['Win'].mean()*100):.1f}%</div><div class='hl-desc'>Aproveitamento Geral</div></div>", unsafe_allow_html=True)
        with h4:
            mapa_f = df.groupby('Mapa')['Win'].mean().idxmax()
            st.markdown(f"<div class='highlight-card'><div class='hl-title'>MELHOR MAPA</div><div class='hl-value'>{mapa_f}</div><div class='hl-desc'>Domínio Estratégico</div></div>", unsafe_allow_html=True)

        st.write("---")
        player_list = player_agg.sort_values("ADR", ascending=False).to_dict('records')
        for i in range(0, len(player_list), 4):
            cols = st.columns(4)
            for j, p_data in enumerate(player_list[i:i+4]):
                with cols[j]:
                    with st.container(border=True):
                        st.markdown(f"#### {p_data['Nome']}")
                        st.markdown(f'<span class="role-badge {p_data["Role"].lower()}">{p_data["Role"]}</span>', unsafe_allow_html=True)
                        fig = go.Figure(go.Scatterpolar(r=[p_data['ADR']/200, p_data['K']/p_data['D'], p_data['HS%']/35, p_data['Impacto']], theta=['ADR', 'K/D', 'HS%', 'Impacto'], fill='toself', line_color='#ff4655'))
                        fig.update_layout(polar=dict(radialaxis=dict(visible=False), bgcolor="#1f2933"), showlegend=False, height=140, margin=dict(l=20,r=20,t=20,b=20), paper_bgcolor="rgba(0,0,0,0)")
                        st.plotly_chart(fig, use_container_width=True)
                        notas = analise_inteligente(p_data)
                        st.markdown(f"<div class='coach-box acerto'><b>✅ ACERTO:</b> {notas['acerto']}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='coach-box ajuste'><b>⚠️ AJUSTE:</b> {notas['ajuste']}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='coach-box foco'><b>📘 FOCO:</b> {notas['foco']}</div>", unsafe_allow_html=True)

    elif aba == "📈 Estratégia e Tendências":
        st.write("### 🧠 INTELIGÊNCIA ESTRATÉGICA")
        t1, t2, t3 = st.tabs(["🎮 Agent Pool", "📈 Tendências", "⚔️ Lados"])
        with t1:
            agent_data = df.groupby(['Nome', 'Agente'])['Win'].mean().reset_index()
            agent_data['Win %'] = agent_data['Win'] * 100
            st.plotly_chart(px.bar(agent_data, x="Agente", y="Win %", color="Nome", barmode="group", template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Prism), use_container_width=True)
        with t2:
            st.plotly_chart(px.line(df.sort_values("Data"), x="Data", y="HS%", color="Nome", markers=True, template="plotly_dark", title="Evolução de Mira"), use_container_width=True)
        with t3:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("<h4 style='color: #ff4655;'>🔴 PERFIL OFENSIVO (ATAQUE)</h4>", unsafe_allow_html=True)
                st.dataframe(player_agg[['Nome', 'ADR', 'Impacto']].sort_values('Impacto', ascending=False).style.background_gradient(cmap="Reds"), use_container_width=True, hide_index=True)
            with c2:
                st.markdown("<h4 style='color: #45b3e3;'>🔵 PERFIL DEFENSIVO (DEFESA)</h4>", unsafe_allow_html=True)
                st.dataframe(player_agg[['Nome', 'Econ', 'HS%']].sort_values('HS%', ascending=False).style.background_gradient(cmap="Blues"), use_container_width=True, hide_index=True)

    elif aba == "⚔️ HISTÓRICO":
        st.write("### 📜 HISTÓRICO (Horário de Brasília)")
        matches = df.groupby(['MatchID', 'Data', 'Mapa', 'Placar', 'Win']).apply(lambda x: x.to_dict('records')).reset_index().sort_values('Data', ascending=False)
        for _, m in matches.iterrows():
            # AJUSTE DE FUSO HORÁRIO (-3h)
            data_br = m['Data'] - pd.Timedelta(hours=3)
            cor = "🟢 VITÓRIA" if m['Win'] else "🔴 DERROTA"
            with st.expander(f"{cor} | {m['Mapa']} | {m['Placar']} | {data_br.strftime('%d/%m %H:%M')}"):
                st.table(pd.DataFrame(m[0])[['Nome', 'Agente', 'K', 'D', 'A', 'ADR', 'HS%']].sort_values('ADR', ascending=False))