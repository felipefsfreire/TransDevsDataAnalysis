# -*- coding: utf-8 -*-

"""
Dashboard Interativo de Análise de Dados - TransDevs Data Analysis (VERSÃO FINAL COMPLETA E POLIDA)
Autor: [Seu Nome] & Smith (Mentor)
Data: 02/10/2025
"""

import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mtick
import ast
import json
import plotly.express as px

# --- Proteção por Senha ---
def check_password():
    def password_entered():
        if "password" in st.session_state and st.session_state["password"] == st.secrets.get("APP_PASSWORD", ""):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if not st.session_state["password_correct"]:
        st.text_input("Senha de Acesso", type="password", on_change=password_entered, key="password")
        if "password" in st.session_state and not st.session_state["password_correct"]:
            st.error("Senha incorreta.")
        return False
    else:
        return True

if not check_password():
    st.stop()

# --- Definição de Caminhos ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_PATH = os.path.join(PROJECT_ROOT, "logo-difersificadev-light.png")
DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed', 'dados_consolidados_comunidade.csv')
PERSONA_SUMMARY_PATH = os.path.join(PROJECT_ROOT, 'reports', 'persona_summary_refinado.csv')
PERSONA_DETAILS_PATH = os.path.join(PROJECT_ROOT, 'reports', 'persona_details_refinado.csv')
ATUACAO_COUNT_PATH = os.path.join(PROJECT_ROOT, 'reports', 'atuacao_voluntariado_counts.csv')
CRESCIMENTO_PATH = os.path.join(PROJECT_ROOT, 'reports', 'crescimento_mensal.csv')
MAP_SUMMARY_PATH = os.path.join(PROJECT_ROOT, 'reports', 'mapa_resumo_estados.csv')
BRAZIL_GEOJSON_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw', 'brazil_states.geojson')

# --- Configurações da Página ---
st.set_page_config(page_title="TransDevs Data Analysis", page_icon=LOGO_PATH, layout="wide", initial_sidebar_state="expanded")

# --- Paleta de Cores e Estilo ---
PRIMARY_COLOR = "#C738D8"; BACKGROUND_COLOR = "#121212"; TEXT_COLOR = "#FFFFFF"; SECONDARY_PALETTE = "plasma"
plt.rcParams.update({'text.color': TEXT_COLOR, 'axes.labelcolor': TEXT_COLOR, 'xtick.color': TEXT_COLOR, 'ytick.color': TEXT_COLOR, 'axes.edgecolor': TEXT_COLOR, 'figure.facecolor': BACKGROUND_COLOR, 'axes.facecolor': BACKGROUND_COLOR, 'savefig.facecolor': BACKGROUND_COLOR,})

# --- Funções Auxiliares ---
@st.cache_data
def carregar_csv(caminho_arquivo: str):
    if os.path.exists(caminho_arquivo):
        return pd.read_csv(caminho_arquivo)
    return None

def exibir_imagem_logo(caminho_logo: str, width: int = 100):
    if os.path.exists(caminho_logo): st.sidebar.image(caminho_logo, width=width)
    else: st.sidebar.warning("Arquivo de logo não encontrado na pasta raiz.")

def exibir_detalhes_persona(coluna_detalhes: str):
    try:
        items = ast.literal_eval(coluna_detalhes)
        for item in items:
            label, percent_str = item.split(': ')
            value = float(percent_str.replace('%', ''))
            st.markdown(f"**{label}**")
            st.progress(int(value))
    except (ValueError, SyntaxError):
        st.text("Dados indisponíveis.")

def clean_spines(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(TEXT_COLOR)
    ax.spines['left'].set_color(TEXT_COLOR)
    ax.tick_params(axis='both', which='both', length=0)

# --- Barra Lateral de Navegação ---
exibir_imagem_logo(LOGO_PATH, width=100)
st.sidebar.title("Navegação")
PAGINAS = ["Visão Geral", "Crescimento & Cursos", "Perfil Demográfico", "Perfil Profissional", "Análises Cruzadas", "Personas da Comunidade", "Análise de Voluntariado", "Planejamento Estratégico"]
pagina_selecionada = st.sidebar.radio("Selecione uma página:", PAGINAS)
st.sidebar.markdown("---")
st.sidebar.info("Dashboard analítico da comunidade TransDevs. Todos os dados foram anonimizados.")

# --- CONTEÚDO DAS PÁGINAS ---

if pagina_selecionada == "Visão Geral":
    st.title("Visão Geral do Impacto da TransDevs")
    df = carregar_csv(DATA_PATH)
    if df is not None:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("### Indicadores Chave")
            kpi1, kpi2, kpi3 = st.columns(3)
            total_pessoas = df['person_id'].nunique(); kpi1.metric("Pessoas Únicas Analisadas", f"{total_pessoas}")
            estados_brasileiros = df[~df['estado_padronizado'].isin(['Internacional', 'Inválido'])]; estados_alcancados = estados_brasileiros['estado_padronizado'].nunique(); kpi2.metric("Estados Brasileiros Alcançados", f"{estados_alcancados}")
            trabalhando_count = df[df['working'].str.lower().str.contains('sim|empregade', na=False)].shape[0]; taxa_empregabilidade = (trabalhando_count / total_pessoas) * 100 if total_pessoas > 0 else 0; kpi3.metric("Taxa de Empregabilidade na Área", f"{taxa_empregabilidade:.1f}%")
        with col2:
            st.markdown("### Perfil da Comunidade")
            if 'perfil_aluno' in df.columns:
                fig_pie, ax_pie = plt.subplots(figsize=(5, 3))
                counts_pie = df['perfil_aluno'].value_counts()
                ax_pie.pie(counts_pie, labels=counts_pie.index, autopct='%.1f%%', startangle=90, colors=[PRIMARY_COLOR, 'grey'])
                st.pyplot(fig_pie)
        
        st.markdown("---")
        st.subheader("Distribuição da Comunidade por Região (%)")
        fig, ax = plt.subplots(figsize=(12, 7))
        counts = df['regiao'].value_counts(normalize=True).mul(100)
        sns.barplot(x=counts.index, y=counts.values, ax=ax, color=PRIMARY_COLOR, edgecolor=BACKGROUND_COLOR)
        ax.set_title("Proporção de Pessoas por Região do Brasil", fontsize=18)
        ax.set_xlabel("Região")
        ax.set_ylabel("Percentual (%)")
        ax.yaxis.set_major_formatter(mtick.PercentFormatter())
        clean_spines(ax)
        for container in ax.containers:
            ax.bar_label(container, fmt='%.1f%%', color=TEXT_COLOR, fontsize=10)
        st.pyplot(fig)
        
        st.markdown("---")
        st.subheader("Mapa de Concentração da Comunidade por Estado")
        st.info("O mapa abaixo exibe a distribuição da comunidade pelos estados brasileiros. O **tamanho da bolha** é proporcional ao **número de pessoas** em cada estado. Passe o mouse sobre uma bolha para ver os detalhes.")
        df_mapa = carregar_csv(MAP_SUMMARY_PATH)
        if df_mapa is not None:
            fig_map = px.scatter_mapbox(df_mapa, lat="latitude", lon="longitude", size="size_sqrt", color_discrete_sequence=[PRIMARY_COLOR], hover_name="estado_padronizado", hover_data={"n_de_pessoas": True, "latitude": False, "longitude": False, "size_sqrt": False}, mapbox_style="carto-darkmatter", center={"lat": -14.2350, "lon": -51.9253}, zoom=3.5, labels={'n_de_pessoas':'Nº de Pessoas'})
            fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning("Arquivo de resumo do mapa não encontrado. Execute 'analysis.py' atualizado.")

        st.markdown("---")
        st.subheader("Distribuição da Comunidade por Região (%)")
        fig_reg, ax_reg = plt.subplots(figsize=(12, 7))
        counts = df['regiao'].value_counts(normalize=True).mul(100)
        sns.barplot(x=counts.index, y=counts.values, ax=ax_reg, color=PRIMARY_COLOR, edgecolor=BACKGROUND_COLOR)
        ax_reg.set_title("Proporção de Pessoas por Região do Brasil", fontsize=18)
        ax_reg.set_xlabel("Região")
        ax_reg.set_ylabel("Percentual (%)")
        ax_reg.yaxis.set_major_formatter(mtick.PercentFormatter())
        clean_spines(ax_reg)
        for container in ax_reg.containers:
            ax_reg.bar_label(container, fmt='%.1f%%', color=TEXT_COLOR, fontsize=10)
        st.pyplot(fig_reg)
    else:
        st.error("Arquivo de dados principal não encontrado. Execute o script 'analysis.py' e atualize o repositório.")

elif pagina_selecionada == "Crescimento & Cursos":
    st.title("Análise de Crescimento e Cursos")
    st.markdown("Acompanhe a evolução da comunidade e entenda a performance de cada iniciativa educacional.")
    st.markdown("---")
    st.subheader("Crescimento da Comunidade ao Longo do Tempo")
    df_growth = carregar_csv(CRESCIMENTO_PATH)
    if df_growth is not None:
        df_growth = df_growth.set_index('periodo')
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Novas Pessoas por Mês**")
            st.bar_chart(df_growth['novas_pessoas'], color=PRIMARY_COLOR)
        with col2:
            st.write("**Total Acumulado de Pessoas**")
            st.line_chart(df_growth['total_acumulado'], color=PRIMARY_COLOR)
    else:
        st.warning("Dados de crescimento não encontrados. Execute 'analysis.py' para gerá-los e atualize o repositório.")
    df = carregar_csv(DATA_PATH)
    if df is not None and 'curso_titulo' in df.columns:
        st.markdown("---")
        st.subheader("Análise de Performance dos Cursos")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Popularidade (Total de Inscrições)**")
            popularidade = df['curso_titulo'].value_counts()
            st.dataframe(popularidade)
        with col2:
            st.markdown("**Alcance (Pessoas Únicas)**")
            alcance = df.groupby('curso_titulo')['person_id'].nunique().sort_values(ascending=False)
            st.dataframe(alcance)
        st.markdown("---")
        st.subheader("Engajamento: Inscrições por Pessoa")
        inscricoes_por_pessoa = df.groupby('person_id')['curso_titulo'].count().value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=inscricoes_por_pessoa.index, y=inscricoes_por_pessoa.values, ax=ax, color=PRIMARY_COLOR, edgecolor=BACKGROUND_COLOR)
        ax.set_title("Quantas Pessoas se Inscrevem em Múltiplos Cursos?")
        ax.set_xlabel("Número de Cursos Inscritos")
        ax.set_ylabel("Número de Pessoas")
        clean_spines(ax)
        for c in ax.containers:
            ax.bar_label(c)
        st.pyplot(fig)

elif pagina_selecionada == "Perfil Demográfico":
    st.title("Análise do Perfil Demográfico (%)")
    df = carregar_csv(DATA_PATH)
    if df is not None:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Por Faixa Etária")
            fig1, ax1 = plt.subplots(figsize=(10, 6))
            counts = df['faixa_etaria'].value_counts(normalize=True).mul(100)
            sns.barplot(y=counts.index, x=counts.values, ax=ax1, color=PRIMARY_COLOR, orient='h', edgecolor=BACKGROUND_COLOR)
            ax1.set_xlabel("Percentual (%)")
            ax1.set_ylabel("Faixa Etária")
            ax1.xaxis.set_major_formatter(mtick.PercentFormatter())
            clean_spines(ax1)
            for c in ax1.containers:
                ax1.bar_label(c, fmt=' %.1f%%')
            st.pyplot(fig1)
            
            st.subheader("Por Etnia")
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            counts = df['etnia_padronizada'].value_counts(normalize=True).mul(100)
            sns.barplot(y=counts.index, x=counts.values, ax=ax2, color=PRIMARY_COLOR, orient='h', edgecolor=BACKGROUND_COLOR)
            ax2.set_xlabel("Percentual (%)")
            ax2.set_ylabel("Etnia")
            ax2.xaxis.set_major_formatter(mtick.PercentFormatter())
            clean_spines(ax2)
            for c in ax2.containers:
                ax2.bar_label(c, fmt=' %.1f%%')
            st.pyplot(fig2)
        with col2:
            st.subheader("Acesso a Computador")
            fig_comp, ax_comp = plt.subplots()
            counts_comp = df['computador_acesso'].value_counts()
            ax_comp.pie(counts_comp, labels=counts_comp.index, autopct='%.1f%%', startangle=90, colors=[PRIMARY_COLOR, 'grey', '#8A2BE2'])
            st.pyplot(fig_comp)
        
        st.subheader("Por Gênero")
        fig3, ax3 = plt.subplots(figsize=(12, 6))
        counts = df['genero_padronizado'].value_counts(normalize=True).mul(100)
        sns.barplot(x=counts.index, y=counts.values, ax=ax3, palette=SECONDARY_PALETTE, edgecolor=BACKGROUND_COLOR)
        ax3.set_xlabel("Gênero")
        ax3.set_ylabel("Percentual (%)")
        ax3.yaxis.set_major_formatter(mtick.PercentFormatter())
        clean_spines(ax3)
        for c in ax3.containers:
            ax3.bar_label(c, fmt='%.1f%%')
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig3)

elif pagina_selecionada == "Perfil Profissional":
    st.title("Análise do Perfil Profissional (%)")
    df = carregar_csv(DATA_PATH)
    if df is not None:
        st.subheader("Distribuição por Nível de Experiência")
        fig, ax = plt.subplots(figsize=(12, 8))
        counts = df['professional_level_padronizado'].value_counts(normalize=True).mul(100).sort_index()
        sns.barplot(y=counts.index, x=counts.values, ax=ax, palette=SECONDARY_PALETTE, orient='h', edgecolor=BACKGROUND_COLOR)
        ax.set_xlabel("Percentual (%)")
        ax.set_ylabel("Nível Profissional")
        ax.xaxis.set_major_formatter(mtick.PercentFormatter())
        clean_spines(ax)
        for c in ax.containers:
            ax.bar_label(c, fmt=' %.1f%%')
        st.pyplot(fig)

elif pagina_selecionada == "Análises Cruzadas":
    st.title("Análises Cruzadas e Insights Aprofundados")
    df = carregar_csv(DATA_PATH)
    if df is not None:
        st.subheader("Composição do Nível Profissional por Região")
        fig1, ax1 = plt.subplots(figsize=(14, 8))
        crosstab_reg_level = pd.crosstab(df['regiao'], df['professional_level_padronizado'], normalize='index')
        crosstab_reg_level.plot(kind='barh', stacked=True, ax=ax1, colormap='viridis')
        for n, c in enumerate(crosstab_reg_level.index):
            for i, (name, val) in enumerate(crosstab_reg_level.iloc[n].items()):
                if val * 100 > 5: ax1.text(crosstab_reg_level.iloc[n, :i].sum() + val / 2, n, f'{val*100:.0f}%', ha='center', va='center', color='white', fontsize=9, weight='bold')
        ax1.set_xlabel('Proporção (%)'); ax1.set_ylabel(''); ax1.xaxis.set_major_formatter(mtick.PercentFormatter(1.0)); clean_spines(ax1); legend = ax1.legend(title='Nível Profissional', bbox_to_anchor=(1.05, 1), loc='upper left', frameon=False); plt.setp(legend.get_title(), color=TEXT_COLOR); st.pyplot(fig1)
        
        st.subheader("Composição do Nível Profissional por Gênero")
        fig_gen, ax_gen = plt.subplots(figsize=(14, 8))
        crosstab_gen_level = pd.crosstab(df['genero_padronizado'], df['professional_level_padronizado'], normalize='index')
        crosstab_gen_level.plot(kind='barh', stacked=True, ax=ax_gen, colormap='plasma')
        for n, c in enumerate(crosstab_gen_level.index):
            for i, (name, val) in enumerate(crosstab_gen_level.iloc[n].items()):
                if val * 100 > 5: ax_gen.text(crosstab_gen_level.iloc[n, :i].sum() + val / 2, n, f'{val*100:.0f}%', ha='center', va='center', color='white', fontsize=9, weight='bold')
        ax_gen.set_xlabel('Proporção (%)'); ax_gen.set_ylabel(''); ax_gen.xaxis.set_major_formatter(mtick.PercentFormatter(1.0)); clean_spines(ax_gen); legend = ax_gen.legend(title='Nível Profissional', bbox_to_anchor=(1.05, 1), loc='upper left', frameon=False); plt.setp(legend.get_title(), color=TEXT_COLOR); st.pyplot(fig_gen)
        
        st.subheader("Proporção de Pessoas Trabalhando na Área por Faixa Etária")
        fig2, ax2 = plt.subplots(figsize=(12, 8))
        crosstab_idade_work = pd.crosstab(df['faixa_etaria'].dropna(), df['working'].dropna(), normalize='index')
        crosstab_idade_work.plot(kind='bar', stacked=True, ax=ax2, colormap='viridis')
        for i, (name, row) in enumerate(crosstab_idade_work.iterrows()):
            cumulative_val = 0
            for col_name, val in row.items():
                if val * 100 > 5: ax2.text(i, cumulative_val + val / 2, f'{val*100:.0f}%', ha='center', va='center', color='white', fontsize=9, weight='bold')
                cumulative_val += val
        ax2.set_xlabel(''); ax2.set_ylabel('Proporção (%)'); ax2.yaxis.set_major_formatter(mtick.PercentFormatter(1.0)); plt.xticks(rotation=45, ha='right'); clean_spines(ax2); legend = ax2.legend(title='Trabalhando na área?', bbox_to_anchor=(1.05, 1), loc='upper left', frameon=False); plt.setp(legend.get_title(), color=TEXT_COLOR); st.pyplot(fig2)
        
        st.subheader("Proporção de Pessoas Trabalhando na Área por Etnia")
        fig3, ax3 = plt.subplots(figsize=(12, 8))
        crosstab_etnia_work = pd.crosstab(df['etnia_padronizada'].dropna(), df['working'].dropna(), normalize='index')
        crosstab_etnia_work.plot(kind='bar', stacked=True, ax=ax3, colormap='plasma')
        for i, (name, row) in enumerate(crosstab_etnia_work.iterrows()):
            cumulative_val = 0
            for col_name, val in row.items():
                if val * 100 > 5: ax3.text(i, cumulative_val + val / 2, f'{val*100:.0f}%', ha='center', va='center', color='white', fontsize=9, weight='bold')
                cumulative_val += val
        ax3.set_xlabel(''); ax3.set_ylabel('Proporção (%)'); ax3.yaxis.set_major_formatter(mtick.PercentFormatter(1.0)); plt.xticks(rotation=45, ha='right'); clean_spines(ax3); legend = ax3.legend(title='Trabalhando na área?', bbox_to_anchor=(1.05, 1), loc='upper left', frameon=False); plt.setp(legend.get_title(), color=TEXT_COLOR); st.pyplot(fig3)

elif pagina_selecionada == "Personas da Comunidade":
    st.title("Personas da Comunidade (Análise de Cluster)")
    df_summary = carregar_csv(PERSONA_SUMMARY_PATH)
    df_details = carregar_csv(PERSONA_DETAILS_PATH)
    if df_summary is not None and df_details is not None:
        st.markdown("### Resumo das Personas"); st.dataframe(df_summary, hide_index=True)
        st.markdown("---"); st.markdown("### Quem são Elas? Uma Análise Detalhada")
        st.subheader("Persona 1: Talentos em Transição (25-34 anos, Iniciante)"); st.write("Nosso maior grupo, composto por profissionais maduros (25-34 anos) que estão fazendo uma transição de carreira para a tecnologia. Embora classificados como 'Iniciantes', sua formação (muitos com ensino superior) e interesse em tecnologias como Python e Node.js sugerem uma busca por posições de desenvolvimento web back-end ou full-stack. Eles são a principal força de novos talentos qualificados no mercado.")
        st.subheader("Persona 2: Novos Horizontes (35+ anos, Iniciante)"); st.write("Representando a coragem da reinvenção, esta persona inclui profissionais mais experientes (35+ anos) que estão entrando na área de tecnologia. Concentrados fora do eixo Sudeste (predominantemente no Norte), seu foco em tecnologias fundamentais como HTML, SQL e CSS indica a construção de uma nova base de carreira, possivelmente voltada para desenvolvimento web ou análise de dados.")
        st.subheader("Persona 3: Jovens Promessas (18-24 anos, Iniciante)"); st.write("A nova geração de talentos da comunidade. Este grupo, mais jovem, tem um foco claro em desenvolvimento front-end (HTML, CSS, Javascript). Vindo do ensino médio ou do início da faculdade, sua principal necessidade é transformar o conhecimento teórico em experiência prática através de projetos, estágios e mentoria.")
        st.subheader("Persona 4: Profissionais Qualificados (25-34 anos, Pleno)"); st.write("Este grupo representa a espinha dorsal de experiência técnica da comunidade. Embora a maioria seja de nível Pleno, há uma diversidade de senioridade, incluindo juniores e iniciantes em ascensão. Com foco em tecnologias como Python, eles provavelmente buscam consolidar suas carreiras, especializar-se ou assumir posições de maior responsabilidade, sendo um ativo valioso para empresas que buscam talentos com experiência comprovada.")
        
        st.markdown("---"); st.markdown("### Detalhes Técnicos por Persona")
        for index, row in df_details.iterrows():
            persona_id = row['persona']; summary_row = df_summary[df_summary['persona'] == persona_id].iloc[0]
            with st.expander(f"**Persona {summary_row['persona']}: {summary_row['faixa_etaria_moda']} - {summary_row['nivel_profissional_moda']}**"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("**Senioridade**"); exibir_detalhes_persona(row['level_distribution'])
                with col2:
                    st.markdown("**Escolaridade (Top 3)**"); exibir_detalhes_persona(row['top_schooling'])
                with col3:
                    st.markdown("**Tecnologias (Top 3)**"); exibir_detalhes_persona(row['top_technologies'])

        st.markdown("---"); st.subheader("Insights Acionáveis")
        st.info("""- **Trilhas de Carreira Direcionadas:** Os focos tecnológicos claros de cada persona permitem a criação de programas específicos. **Persona 3** se beneficiaria de um 'Bootcamp de Front-End', enquanto a **Persona 1** teria mais proveito de uma 'Trilha de Desenvolvimento Back-End com Python/Node.js'.\n- **Aceleração para Profissionais Qualificados:** A **Persona 4**, com sua diversidade de senioridade, necessita de mais do que apenas networking. Oferecer 'Workshops de Arquitetura de Software' ou 'Mentorias de Liderança Técnica' pode ajudá-los a alcançar o nível Sênior e além.\n- **Inclusão Geográfica e de Habilidades Fundamentais:** A **Persona 2** (Novos Horizontes) reforça a necessidade de vagas remotas. Além disso, seu foco em SQL e web básico sugere que cursos de 'Análise de Dados com SQL e Python' poderiam ser uma porta de entrada de alto impacto para este grupo.""")
    else:
        st.warning("Arquivos de resumo das personas não encontrados. Execute 'analysis.py' novamente.")

elif pagina_selecionada == "Análise de Voluntariado":
    st.title("Análise do Perfil de Voluntariado"); df = carregar_csv(DATA_PATH)
    if df is not None and 'is_volunteer' in df.columns:
        voluntario_count = df[df['is_volunteer'] == 'Sim'].shape[0]; total_pessoas = df['person_id'].nunique(); taxa_voluntariado = (voluntario_count / total_pessoas) * 100; st.metric("Taxa de Voluntariado na Comunidade", f"{taxa_voluntariado:.1f}%"); st.markdown("---")
        
        st.subheader("Quem são as Pessoas Interessadas no Voluntariado?"); st.write("A análise das pessoas que se inscreveram para o voluntariado revela um perfil de **protagonismo e engajamento da base**. Longe de ser um grupo dominado pela senioridade, o interesse em voluntariar é majoritariamente expressado por profissionais em **nível Iniciante**. Isso demonstra uma incrível cultura de 'construir a comunidade que queremos', onde as pessoas que estão começando a carreira são as mais motivadas a doar seu tempo. A diversidade de personas interessadas, com destaque para **'Talentos em Transição' (Persona 1)** e **'Profissionais Qualificados' (Persona 4)**, mostra que o desejo de contribuir permeia todos os níveis de experiência.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Frequência de Áreas de Atuação"); df_atuacao = carregar_csv(ATUACAO_COUNT_PATH)
            if df_atuacao is not None:
                fig, ax = plt.subplots(figsize=(10, 6)); sns.barplot(y='atuacao', x='count', data=df_atuacao.nlargest(10, 'count'), ax=ax, color=PRIMARY_COLOR, orient='h', edgecolor=BACKGROUND_COLOR); ax.set_xlabel("Nº de Menções"); ax.set_ylabel("Área de Atuação (Tags)"); clean_spines(ax); st.pyplot(fig)
        with col2:
            st.subheader("Nível Profissional: Comparativo"); fig2, ax2 = plt.subplots(figsize=(10, 6)); crosstab_vol_level = pd.crosstab(df['professional_level_padronizado'], df['is_volunteer'], normalize='columns').mul(100); crosstab_vol_level.plot(kind='barh', ax=ax2, color=['grey', PRIMARY_COLOR]); ax2.set_xlabel("Percentual (%)"); ax2.set_ylabel(""); ax2.xaxis.set_major_formatter(mtick.PercentFormatter()); clean_spines(ax2); legend = ax2.legend(title='Grupo', frameon=False); plt.setp(legend.get_title(), color=TEXT_COLOR); st.pyplot(fig2)
        
        st.markdown("---"); st.subheader("Perfil Detalhado das Personas Voluntárias");
        if 'persona' in df.columns:
            df_vol = df[df['is_volunteer'] == 'Sim'].dropna(subset=['persona'])
            if not df_vol.empty:
                vol_persona_summary = df_vol.groupby('persona').agg(n_de_pessoas=('persona', 'size'), regiao_moda=('regiao', lambda x: x.mode().get(0, 'N/A')), nivel_profissional_moda=('professional_level_padronizado', lambda x: x.mode().get(0, 'N/A')), atuacao_principal_moda=('atuacao_principal', lambda x: x.mode().get(0, 'N/A'))).reset_index()
                st.dataframe(vol_persona_summary, hide_index=True)

                st.markdown("---"); st.markdown("### Quem são Elas? Uma Análise das Personas Voluntárias")
                st.subheader("Persona 1 (Talentos em Transição): O Desejo de Crescer Junto"); st.write("Sendo o maior grupo entre os interessados, estas pessoas veem o voluntariado não apenas como uma forma de ajudar, mas também como uma oportunidade de ganhar experiência prática e construir portfólio. Sua principal área de interesse é **Tecnologia**, indicando um forte desejo de aplicar seus novos conhecimentos em projetos reais da comunidade.")
                st.subheader("Persona 2 (Novos Horizontes): Compartilhando a Experiência de Vida"); st.write("Representando a maturidade e a coragem da reinvenção, o interesse deste grupo no voluntariado é particularmente inspirador. Vindos majoritariamente da região Norte e focados na área de **Tecnologia**, eles buscam aplicar suas novas habilidades e, ao mesmo tempo, compartilhar a vasta experiência profissional e de vida que acumularam em outras carreiras. Sua participação enriquece a comunidade com diversidade de pensamento e resiliência.")
                st.subheader("Persona 3 (Jovens Promessas): Energia e Novas Ideias"); st.write("Este grupo traz a energia da nova geração. Seu interesse se concentra em **Engajamento**, sugerindo um desejo de atuar na linha de frente da comunidade, organizando eventos, gerenciando redes sociais e garantindo que o ambiente seja acolhedor e vibrante. Eles são a voz e o coração da comunidade.")
                st.subheader("Persona 4 (Profissionais Qualificados): A Vontade de Retribuir"); st.write("Este grupo, composto por profissionais mais experientes, demonstra o clássico desejo de 'retribuir'. Eles são a espinha dorsal técnica do voluntariado, também focando na área de **Tecnologia**. Sua presença é vital para a mentoria de pessoas mais novas e para a viabilidade de projetos mais complexos.")
            else:
                st.info("Ainda não há dados suficientes para cruzar personas e voluntariado.")

elif pagina_selecionada == "Planejamento Estratégico":
    st.title("Planejamento Estratégico Baseado em Dados"); st.markdown("Use os dados da comunidade para tomar decisões sobre novas iniciativas, identificar talentos e entender a capacidade de nossos programas."); df = carregar_csv(DATA_PATH)
    if df is not None:
        st.markdown("---"); st.subheader("Análise de Recorte de Diversidade"); genero_selecionado = st.selectbox("Selecione um Gênero para analisar o recorte racial:", df['genero_padronizado'].unique())
        if genero_selecionado:
            df_filtrado = df[df['genero_padronizado'] == genero_selecionado]; total_no_grupo = len(df_filtrado); st.metric(f"Total de Pessoas no Grupo '{genero_selecionado}'", total_no_grupo)
            if total_no_grupo > 0:
                fig, ax = plt.subplots(figsize=(10, 6)); counts = df_filtrado['etnia_padronizada'].value_counts(normalize=True).mul(100); sns.barplot(y=counts.index, x=counts.values, ax=ax, color=PRIMARY_COLOR, orient='h'); ax.set_xlabel("Percentual (%)"); ax.set_ylabel("Etnia"); clean_spines(ax)
                for c in ax.containers: ax.bar_label(c, fmt=' %.1f%%')
                st.pyplot(fig)
        st.info("**Nota sobre 'Pessoas Ativas':** Os dados atuais refletem o total de *inscrições*. Para medir a 'atividade', seria necessário integrar dados de engajamento da plataforma de cursos.")
        st.markdown("---"); st.subheader("Identificação de Talentos para Mentorias")
        available_genders = df['genero_padronizado'].unique().tolist(); desired_defaults = ['Mulher Trans', 'Homem Trans', 'Não-Binárie', 'Travesti']; actual_defaults = [g for g in desired_defaults if g in available_genders]; generos_mentoria = st.multiselect("Filtre por Gênero para encontrar potenciais mentores/as/es:", options=available_genders, default=actual_defaults)
        if generos_mentoria:
            niveis_experientes = ['Pleno', 'Sênior', 'Especialista', 'Liderança']; mentores_potenciais = df[(df['genero_padronizado'].isin(generos_mentoria)) & (df['professional_level_padronizado'].isin(niveis_experientes)) & (df['is_volunteer'] == 'Sim')]; st.metric("Total de Potenciais Mentores/as/es Encontrados:", len(mentores_potenciais))
            if len(mentores_potenciais) > 0:
                fig, ax = plt.subplots(figsize=(10, 6)); counts = mentores_potenciais['genero_padronizado'].value_counts(); sns.barplot(x=counts.index, y=counts.values, ax=ax, palette=SECONDARY_PALETTE, edgecolor=BACKGROUND_COLOR); ax.set_ylabel("Número de Pessoas"); clean_spines(ax)
                for c in ax.containers: ax.bar_label(c)
                st.pyplot(fig)