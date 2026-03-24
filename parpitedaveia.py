import streamlit as st
import pandas as pd
import random
import time
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="CUCURUCO GOLD", page_icon="🎰", layout="wide")

# --- CSS PERSONALIZADO (Dark Mode Premium) ---
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    [data-testid="stMetricValue"] { color: #ffd700 !important; }
    .stAlert { border-radius: 15px; border: 1px solid #ffd700; }
    .ganhador-card {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #22c55e;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_stdio=True)

# --- INICIALIZAÇÃO DO BANCO (Session State) ---
if 'usuarios' not in st.session_state:
    st.session_state.usuarios = {
        "admin": {"senha": "123", "saldo": 1000, "pix": "admin@pix.com", "tipo": "admin"},
        "cliente01": {"senha": "123", "saldo": 50, "pix": "cliente@pix.com", "tipo": "user"}
    }
if 'apostas_ativas' not in st.session_state:
    st.session_state.apostas_ativas = []
if 'historico_sorteios' not in st.session_state:
    st.session_state.historico_sorteios = []
if 'logado' not in st.session_state:
    st.session_state.logado = False

# --- LÓGICA DE NAVEGAÇÃO ---
if not st.session_state.logado:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://img.icons8.com/color/144/slot-machine.png")
        st.title("🎰 PRIGUIÇA DO CUCURUCO")
        with st.form("login_form"):
            user = st.text_input("Usuário")
            pw = st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR PLATAFORMA"):
                if user in st.session_state.usuarios and st.session_state.usuarios[user]["senha"] == pw:
                    st.session_state.logado = True
                    st.session_state.user_atual = user
                    st.rerun()
                else:
                    st.error("Acesso Negado")

else:
    # --- SIDEBAR ---
    u_atual = st.session_state.user_atual
    st.sidebar.title("💎 CUCURUCO VIP")
    st.sidebar.write(f"Usuário: **{u_atual}**")
    menu = ["🎰 Apostar", "💰 Saldo/Pix", "🏆 Resultados"]
    if st.session_state.usuarios[u_atual]['tipo'] == "admin":
        menu.append("👑 CENTRAL DO DONO")

    escolha = st.sidebar.radio("Navegar", menu)

    if st.sidebar.button("LOGOUT"):
        st.session_state.logado = False
        st.rerun()

    # --- ABA: APOSTAR ---
    if escolha == "🎰 Apostar":
        st.title("🎰 Faça sua Fé!")
        saldo = st.session_state.usuarios[u_atual]['saldo']
        st.metric("Meu Saldo", f"🪙 {saldo} moedas")

        with st.container():
            col_a, col_b = st.columns(2)
            tipo = col_a.selectbox("Modalidade", ["Milhar", "Centena", "Dezena"])
            valor = col_b.number_input("Valor da Aposta", min_value=1)
            palpite = st.text_input("Seu Número da Sorte", max_chars=4)

            if st.button("CONFIRMAR BILHETE"):
                if saldo >= valor and len(palpite) > 0:
                    st.session_state.usuarios[u_atual]['saldo'] -= valor
                    st.session_state.apostas_ativas.append({
                        "user": u_atual, "numero": palpite, "valor": valor, "tipo": tipo
                    })
                    st.success("✅ Aposta registrada! O sistema sorteia em 2h.")
                else:
                    st.error("Verifique saldo ou número.")

    # --- ABA: CENTRAL DO DONO (A MAIS CHAMATIVA) ---
    elif escolha == "👑 CENTRAL DO DONO":
        st.title("👑 Gestão de Banca")

        # Dashboard de métricas
        m1, m2, m3 = st.columns(3)
        m1.metric("Apostas Ativas", len(st.session_state.apostas_ativas))
        m2.metric("Volume de Moedas", sum(a['valor'] for a in st.session_state.apostas_ativas))
        m3.metric("Usuários Base", len(st.session_state.usuarios))

        st.divider()

        col_sorteio, col_lista = st.columns([1, 2])

        with col_sorteio:
            st.subheader("🎲 Rodar Sorteio")
            num_sorteado = st.text_input("Resultado Oficial", placeholder="Ex: 1234")
            if st.button("FINALIZAR SORTEIO E PAGAR"):
                st.session_state.historico_sorteios.append(num_sorteado)
                ganhadores = [a for a in st.session_state.apostas_ativas if a['numero'] == num_sorteado]

                if ganhadores:
                    st.balloons()
                    for g in ganhadores:
                        st.markdown(f"""
                        <div class="ganhador-card">
                            <h3 style='margin:0; color:#22c55e;'>🏆 GANHADOR: {g['user']}</h3>
                            <p style='margin:0;'>Prêmio: <b>{g['valor'] * 10} moedas</b></p>
                            <p style='margin:0;'>Chave PIX: {st.session_state.usuarios[g['user']]['pix']}</p>
                        </div>
                        """, unsafe_allow_stdio=True)
                else:
                    st.info("Sorteio encerrado. Não houve ganhadores desta vez.")

                # Limpa apostas para o próximo ciclo de 2h
                st.session_state.apostas_ativas = []

        with col_lista:
            st.subheader("📊 Bilhetes no Globo")
            if st.session_state.apostas_ativas:
                st.table(pd.DataFrame(st.session_state.apostas_ativas))
            else:
                st.write("Aguardando novas apostas...")

    # --- ABA: RESULTADOS ---
    elif escolha == "🏆 Resultados":
        st.title("🏆 Últimos Sorteios")
        if st.session_state.historico_sorteios:
            for n in reversed(st.session_state.historico_sorteios):
                st.info(f"🎰 Resultado: **{n}**")
        else:
            st.write("Ainda não houve sorteios hoje.")