import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- CONFIGURAÇÃO DA PÁGINA E TEMA ---
st.set_page_config(
    page_title="OncoFlux",
    page_icon="🧭",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Simulando um Banco de Dados Local (CSV)
FILE_DB = "oncoflux_db.csv"

# Função para carregar dados
def load_data():
    if os.path.exists(FILE_DB):
        return pd.read_csv(FILE_DB)
    else:
        # Cria um DataFrame vazio se não existir arquivo
        columns = ["Data_Registro", "Tipo_Usuario", "Origem", "Tipo_Solicitacao", 
                   "Satisfacao", "Resolvida", "Perda_Volume", "Motivo_Perda"]
        return pd.DataFrame(columns=columns)

# Função para salvar dados
def save_data(data):
    df = load_data()
    new_df = pd.DataFrame([data])
    df_final = pd.concat([df, new_df], ignore_index=True)
    df_final.to_csv(FILE_DB, index=False)
    return df_final

# --- INTERFACE PRINCIPAL ---
def main():
    # Carrega dados existentes para o Dashboard
    df = load_data()

    # Cabeçalho com a Identidade Visual
    st.markdown("""
        <style>
        .title {color: #00d4ff; text-align: center; font-family: sans-serif;}
        .subtitle {color: #ffffff; text-align: center; font-size: 14px; opacity: 0.8;}
        .stApp {background-color: #0b1d35; color: white} 
        </style>
        """, unsafe_allow_html=True)

    st.markdown("<h1 class='title'>🧭 OncoFlux</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Transformando o trabalho invisível em dados para Tomada de Decisão.</p>", unsafe_allow_html=True)
    st.write("---")

    # Navegação por Abas (Fica perfeito no celular)
    tab1, tab2 = st.tabs(["📝 Novo Registro", "📊 Dashboard Diretoria"])

    # --- ABA 1: REGISTRO DIÁRIO ---
    with tab1:
        st.header("Registro Diário de Fluxo")

        with st.form(key='daily_flow_form', clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                tipo_usuario = st.selectbox("Solicitante", ["Paciente", "Familiar", "Médico Externo", "Staff Interno"])
            with col2:
                origem = st.selectbox("Canal", ["Pessoal", "WhatsApp", "Telefone", "E-mail"])

            tipo_solicitacao = st.selectbox("Tipo de Demanda", 
                                            ["Agendamento/Reagendamento", 
                                             "Confirmação de Tratamento", 
                                             "Crise/Conflito", 
                                             "Documentação/Convênio", 
                                             "Dúvida de Fluxo/Logística",
                                             "Outro"])

            st.markdown("### Resolução & Qualidade")
            col3, col4 = st.columns(2)
            with col3:
                resolvida = st.selectbox("Resolvido?", ["Sim", "Não (Pendência)"])
            with col4:
                satisfacao = st.select_slider("Nível de Satisfação", 
                                              options=["1-Crítico", "2-Ruim", "3-Neutro", "4-Bom", "5-Excelente"],
                                              value="3-Neutro")

            st.markdown("### Gestão de Perdas (Churn)")
            perda_volume = st.selectbox("Houve Perda para Concorrente?", ["Não", "Sim (Perda de Volume)"])

            motivo_perda = "N/A"
            if perda_volume == "Sim (Perda de Volume)":
                st.warning("📉 Atenção: Informe o motivo para relatório executivo.")
                motivo_perda = st.selectbox("Motivo Principal", 
                                            ["Cobertura/Convênio", "Agenda Indisponível", "Preço", "Preferência Médica", "Distância"])

            submit = st.form_submit_button("💾 Salvar Registro")

            if submit:
                novo_dado = {
                    "Data_Registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Tipo_Usuario": tipo_usuario,
                    "Origem": origem,
                    "Tipo_Solicitacao": tipo_solicitacao,
                    "Satisfacao": satisfacao,
                    "Resolvida": resolvida,
                    "Perda_Volume": perda_volume,
                    "Motivo_Perda": motivo_perda
                }
                save_data(novo_dado)
                st.success("Registro adicionado à base de dados!")
                st.rerun() # Atualiza a página para o dado aparecer no dashboard

    # --- ABA 2: DASHBOARD EXECUTIVO (BI) ---
    with tab2:
        st.header("Visão Executiva")

        if df.empty:
            st.info("Comece a registrar dados para gerar o Dashboard.")
        else:
            # KPIS PRINCIPAIS (Resumo no topo)
            total_atendimentos = len(df)
            satisfacao_critica = len(df[df['Satisfacao'] == '1-Crítico'])
            perdas = len(df[df['Perda_Volume'] == 'Sim (Perda de Volume)'])

            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("Total Atendimentos", total_atendimentos)
            kpi2.metric("Casos Críticos", satisfacao_critica, delta_color="inverse")
            kpi3.metric("Perda de Pacientes", perdas, delta="-{}".format(perdas), delta_color="inverse")

            st.write("---")

            # GRÁFICO 1: Onde está indo o tempo? (Tipo de Solicitação)
            st.subheader("Distribuição de Demandas")
            fig_demanda = px.pie(df, names='Tipo_Solicitacao', hole=0.4, 
                                 color_discrete_sequence=px.colors.sequential.Teal)
            st.plotly_chart(fig_demanda, use_container_width=True)

            # GRÁFICO 2: Análise de Qualidade (Satisfação)
            st.subheader("NPS / Satisfação")
            fig_bar = px.bar(df['Satisfacao'].value_counts().reset_index(), 
                             x='Satisfacao', y='count', 
                             labels={'count':'Qtd', 'Satisfacao':'Nível'},
                             color_discrete_sequence=['#00d4ff'])
            st.plotly_chart(fig_bar, use_container_width=True)

            # ALERTAS DE GESTÃO
            if perdas > 0:
                st.error("🚨 **Atenção Diretoria:** Motivos de Perda de Receita Detectados:")
                df_perdas = df[df['Perda_Volume'] == 'Sim (Perda de Volume)']
                st.dataframe(df_perdas[['Data_Registro', 'Motivo_Perda', 'Tipo_Solicitacao']], use_container_width=True)

if __name__ == "__main__":
    main()
