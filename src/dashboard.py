# -*- coding: utf-8 -*-

"""
Dashboard Interativo de Análise de Dados - TransDevs Data Analysis (VERSÃO FINAL FASE 2)
Adiciona a página de análise de crescimento e popularidade de cursos.
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

# --- Definição de Caminhos ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_PATH = os.path.join(PROJECT_ROOT, "logo-difersificadev-light.png")
DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed', 'dados_consolidados_comunidade.csv')
PERSONA_SUMMARY_PATH = os.path.join(PROJECT_ROOT, 'reports', 'persona_summary_refinado.csv')
PERSONA_DETAILS_PATH = os.path.join(PROJECT_ROOT, 'reports', 'persona_details_refinado.csv')
ATUACAO_COUNT_PATH = os.path.join(PROJECT_ROOT, 'reports', 'atuacao_voluntariado_counts.csv')
CRESCIMENTO_PATH = os.path.join(PROJECT_ROOT, 'reports', 'crescimento_mensal.csv')

# --- Configurações da Página ---
st.set_page_config(page_title="TransDevs Data Analysis", page_icon=LOGO_PATH, layout="wide", initial_sidebar_state="expanded")

# --- Paleta de Cores e Estilo ---
PRIMARY_COLOR = "#C738D8"; BACKGROUND_COLOR = "#121212"; TEXT_COLOR = "#FFFFFF"; SECONDARY_PALETTE = "plasma"
plt.rcParams.update({'text.color': TEXT_COLOR, 'axes.labelcolor': TEXT_COLOR, 'xtick.color': TEXT_COLOR, 'ytick.color': TEXT_COLOR, 'axes.edgecolor': TEXT_COLOR, 'figure.facecolor': BACKGROUND_COLOR, 'axes.facecolor': BACKGROUND_COLOR, 'savefig.facecolor': BACKGROUND_COLOR,})

# --- Funções Auxiliares ---
@st.cache_data
def carregar_dados(caminho_dados: str):
    if os.path.exists(caminho_dados): return pd.read_csv(caminho_dados)
    st.error(f"Erro: Arquivo de dados não encontrado em '{caminho_dados}'. Execute o script 'analysis.py' primeiro.")
    return pd.DataFrame()

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

# --- Carregamento dos Dados ---
df = carregar_dados(DATA_PATH)

# --- Barra Lateral de Navegação ---
exibir_imagem_logo(LOGO_PATH, width=100)
st.sidebar.title("Navegação")
PAGINAS = ["Visão Geral", "Crescimento & Cursos", "Perfil Demográfico", "Perfil Profissional", "Análises Cruzadas", "Personas da Comunidade", "Análise de Voluntariado"]
pagina_selecionada = st.sidebar.radio("Selecione uma página:", PAGINAS)
st.sidebar.markdown("---")
st.sidebar.info("Dashboard analítico da comunidade TransDevs. Todos os dados foram anonimizados.")

# --- CONTEÚDO DAS PÁGINAS ---

if pagina_selecionada == "Visão Geral":
    st.title("Visão Geral do Impacto da TransDevs")
    if not df.empty:
        st.markdown("### Indicadores Chave")
        col1, col2, col3 = st.columns(3)
        total_pessoas = df['person_id'].nunique(); col1.metric("Pessoas Únicas Analisadas", f"{total_pessoas}")
        estados_brasileiros = df[~df['estado_padronizado'].isin(['Internacional', 'Inválido'])]; estados_alcancados = estados_brasileiros['estado_padronizado'].nunique(); col2.metric("Estados Brasileiros Alcançados", f"{estados_alcancados}")
        trabalhando_count = df[df['working'].str.lower().str.contains('sim|empregade', na=False)].shape[0]; taxa_empregabilidade = (trabalhando_count / total_pessoas) * 100 if total_pessoas > 0 else 0; col3.metric("Taxa de Empregabilidade na Área", f"{taxa_empregabilidade:.1f}%")
        st.markdown("---"); st.subheader("Distribuição Geográfica da Comunidade (%)")
        fig, ax = plt.subplots(figsize=(12, 8)); counts = df['regiao'].value_counts(normalize=True).mul(100); sns.barplot(x=counts.index, y=counts.values, ax=ax, color=PRIMARY_COLOR, edgecolor=TEXT_COLOR); ax.set_title("Proporção de Pessoas por Região do Brasil", fontsize=18); ax.set_xlabel("Região"); ax.set_ylabel("Percentual (%)"); ax.yaxis.set_major_formatter(mtick.PercentFormatter());
        for container in ax.containers: ax.bar_label(container, fmt='%.1f%%', color=TEXT_COLOR, fontsize=10)
        st.pyplot(fig)

elif pagina_selecionada == "Crescimento & Cursos":
    st.title("Análise de Crescimento e Cursos")
    st.markdown("Acompanhe a evolução da comunidade e entenda a performance de cada iniciativa educacional.")
    
    st.markdown("---")
    st.subheader("Crescimento da Comunidade ao Longo do Tempo")
    df_growth = carregar_dados(CRESCIMENTO_PATH)
    if not df_growth.empty:
        df_growth = df_growth.set_index('periodo')
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Novas Pessoas por Mês**")
            st.bar_chart(df_growth['novas_pessoas'], color=PRIMARY_COLOR)
        with col2:
            st.write("**Total Acumulado de Pessoas**")
            st.line_chart(df_growth['total_acumulado'], color=PRIMARY_COLOR)
    else:
        st.warning("Dados de crescimento não encontrados. Execute 'analysis.py' para gerá-los.")

    if not df.empty and 'curso_titulo' in df.columns:
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
        sns.barplot(x=inscricoes_por_pessoa.index, y=inscricoes_por_pessoa.values, ax=ax, color=PRIMARY_COLOR)
        ax.set_title("Quantas Pessoas se Inscrevem em Múltiplos Cursos?")
        ax.set_xlabel("Número de Cursos Inscritos")
        ax.set_ylabel("Número de Pessoas")
        for c in ax.containers: ax.bar_label(c)
        st.pyplot(fig)

elif pagina_selecionada == "Perfil Demográfico":
    st.title("Análise do Perfil Demográfico (%)")
    if not df.empty:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Por Faixa Etária"); fig1, ax1 = plt.subplots(figsize=(10, 6)); counts = df['faixa_etaria'].value_counts(normalize=True).mul(100); sns.barplot(y=counts.index, x=counts.values, ax=ax1, color=PRIMARY_COLOR, orient='h'); ax1.set_xlabel("Percentual (%)"); ax1.set_ylabel("Faixa Etária"); ax1.xaxis.set_major_formatter(mtick.PercentFormatter()); 
            for c in ax1.containers: ax1.bar_label(c, fmt=' %.1f%%')
            st.pyplot(fig1)
            st.subheader("Por Etnia"); fig2, ax2 = plt.subplots(figsize=(10, 6)); counts = df['etnia_padronizada'].value_counts(normalize=True).mul(100); sns.barplot(y=counts.index, x=counts.values, ax=ax2, color=PRIMARY_COLOR, orient='h'); ax2.set_xlabel("Percentual (%)"); ax2.set_ylabel("Etnia"); ax2.xaxis.set_major_formatter(mtick.PercentFormatter()); 
            for c in ax2.containers: ax2.bar_label(c, fmt=' %.1f%%')
            st.pyplot(fig2)
        with col2:
            st.subheader("Acesso a Computador"); fig_comp, ax_comp = plt.subplots(); counts_comp = df['computador_acesso'].value_counts(); ax_comp.pie(counts_comp, labels=counts_comp.index, autopct='%.1f%%', startangle=90, colors=[PRIMARY_COLOR, 'grey', '#8A2BE2']); st.pyplot(fig_comp)
        st.subheader("Por Gênero"); fig3, ax3 = plt.subplots(figsize=(12, 6)); counts = df['genero_padronizado'].value_counts(normalize=True).mul(100); sns.barplot(x=counts.index, y=counts.values, ax=ax3, palette=SECONDARY_PALETTE); ax3.set_xlabel("Gênero"); ax3.set_ylabel("Percentual (%)"); ax3.yaxis.set_major_formatter(mtick.PercentFormatter()); 
        for c in ax3.containers: ax3.bar_label(c, fmt='%.1f%%')
        plt.xticks(rotation=45, ha='right'); st.pyplot(fig3)

elif pagina_selecionada == "Perfil Profissional":
    st.title("Análise do Perfil Profissional (%)")
    if not df.empty:
        st.subheader("Distribuição por Nível de Experiência"); fig, ax = plt.subplots(figsize=(12, 8)); counts = df['professional_level_padronizado'].value_counts(normalize=True).mul(100).sort_index(); sns.barplot(y=counts.index, x=counts.values, ax=ax, palette=SECONDARY_PALETTE, orient='h'); ax.set_xlabel("Percentual (%)"); ax.set_ylabel("Nível Profissional"); ax.xaxis.set_major_formatter(mtick.PercentFormatter()); 
        for c in ax.containers: ax.bar_label(c, fmt=' %.1f%%')
        st.pyplot(fig)

elif pagina_selecionada == "Análises Cruzadas":
    st.title("Análises Cruzadas e Insights Aprofundados")
    if not df.empty:
        st.subheader("Composição do Nível Profissional por Região"); fig1, ax1 = plt.subplots(figsize=(14, 8)); crosstab_reg_level = pd.crosstab(df['regiao'], df['professional_level_padronizado'], normalize='index'); crosstab_reg_level.plot(kind='barh', stacked=True, ax=ax1, colormap='viridis');
        for n, c in enumerate(crosstab_reg_level.index):
            for i, (name, val) in enumerate(crosstab_reg_level.iloc[n].items()):
                if val * 100 > 5: ax1.text(crosstab_reg_level.iloc[n, :i].sum() + val / 2, n, f'{val*100:.0f}%', ha='center', va='center', color='white', fontsize=9, weight='bold')
        ax1.set_xlabel('Proporção (%)'); ax1.set_ylabel('Região'); ax1.xaxis.set_major_formatter(mtick.PercentFormatter(1.0)); ax1.legend(title='Nível Profissional', bbox_to_anchor=(1.05, 1), loc='upper left'); st.pyplot(fig1)

        st.subheader("Composição do Nível Profissional por Gênero"); fig_gen, ax_gen = plt.subplots(figsize=(14, 8)); crosstab_gen_level = pd.crosstab(df['genero_padronizado'], df['professional_level_padronizado'], normalize='index'); crosstab_gen_level.plot(kind='barh', stacked=True, ax=ax_gen, colormap='plasma');
        for n, c in enumerate(crosstab_gen_level.index):
            for i, (name, val) in enumerate(crosstab_gen_level.iloc[n].items()):
                if val * 100 > 5: ax_gen.text(crosstab_gen_level.iloc[n, :i].sum() + val / 2, n, f'{val*100:.0f}%', ha='center', va='center', color='white', fontsize=9, weight='bold')
        ax_gen.set_xlabel('Proporção (%)'); ax_gen.set_ylabel('Gênero'); ax_gen.xaxis.set_major_formatter(mtick.PercentFormatter(1.0)); ax_gen.legend(title='Nível Profissional', bbox_to_anchor=(1.05, 1), loc='upper left'); st.pyplot(fig_gen)
        
        st.subheader("Proporção de Pessoas Trabalhando na Área por Faixa Etária"); fig2, ax2 = plt.subplots(figsize=(12, 8)); crosstab_idade_work = pd.crosstab(df['faixa_etaria'].dropna(), df['working'].dropna(), normalize='index'); crosstab_idade_work.plot(kind='bar', stacked=True, ax=ax2, colormap='cividis');
        for i, (name, row) in enumerate(crosstab_idade_work.iterrows()):
            cumulative_val = 0
            for col_name, val in row.items():
                if val * 100 > 5: ax2.text(i, cumulative_val + val / 2, f'{val*100:.0f}%', ha='center', va='center', color='white', fontsize=9, weight='bold')
                cumulative_val += val
        ax2.set_xlabel('Faixa Etária'); ax2.set_ylabel('Proporção (%)'); ax2.yaxis.set_major_formatter(mtick.PercentFormatter(1.0)); plt.xticks(rotation=45, ha='right'); ax2.legend(title='Trabalhando na área?', bbox_to_anchor=(1.05, 1), loc='upper left'); st.pyplot(fig2)

        st.subheader("Proporção de Pessoas Trabalhando na Área por Etnia"); fig3, ax3 = plt.subplots(figsize=(12, 8)); crosstab_etnia_work = pd.crosstab(df['etnia_padronizada'].dropna(), df['working'].dropna(), normalize='index'); crosstab_etnia_work.plot(kind='bar', stacked=True, ax=ax3, colormap='inferno');
        for i, (name, row) in enumerate(crosstab_etnia_work.iterrows()):
            cumulative_val = 0
            for col_name, val in row.items():
                if val * 100 > 5: ax3.text(i, cumulative_val + val / 2, f'{val*100:.0f}%', ha='center', va='center', color='white', fontsize=9, weight='bold')
                cumulative_val += val
        ax3.set_xlabel('Etnia'); ax3.set_ylabel('Proporção (%)'); ax3.yaxis.set_major_formatter(mtick.PercentFormatter(1.0)); plt.xticks(rotation=45, ha='right'); ax3.legend(title='Trabalhando na área?', bbox_to_anchor=(1.05, 1), loc='upper left'); st.pyplot(fig3)

elif pagina_selecionada == "Personas da Comunidade":
    st.title("Personas da Comunidade (Análise de Cluster)")
    if os.path.exists(PERSONA_SUMMARY_PATH) and os.path.exists(PERSONA_DETAILS_PATH):
        df_summary = pd.read_csv(PERSONA_SUMMARY_PATH); df_details = pd.read_csv(PERSONA_DETAILS_PATH)
        st.markdown("### Resumo das Personas"); st.dataframe(df_summary, hide_index=True)
        st.markdown("---"); st.markdown("### Quem são Elas? Uma Análise Detalhada")
        st.subheader("Persona 1: Talentos em Transição (25-34 anos, Iniciante)"); st.write("Este é o nosso maior grupo, representando profissionais na faixa dos 25 a 34 anos que, apesar de estarem no início de sua jornada em tecnologia, já possuem maturidade e provavelmente experiências em outras áreas. Concentrados no Sudeste, eles são a força motriz da transição de carreira para o setor de tecnologia.")
        st.subheader("Persona 2: Novos Horizontes (35+ anos, Iniciante)"); st.write("Esta persona representa a coragem da reinvenção. São profissionais mais maduros que estão fazendo uma transição de carreira significativa para a tecnologia. Eles trazem consigo uma rica bagagem de 'soft skills' de suas carreiras anteriores e buscam um caminho estruturado para aplicar seu novo conhecimento técnico.")
        st.subheader("Persona 3: Jovens Promessas (18-24 anos, Iniciante)"); st.write("O grupo mais jovem, representando a nova geração de talentos. Geralmente estudantes ou recém-formados, estão buscando sua primeira oportunidade no mercado. Sua principal necessidade é a experiência prática e mentoria para dar o pontapé inicial na carreira.")
        st.subheader("Persona 4: Profissionais Qualificados (25-34 anos, Pleno/Sênior)"); st.write("Composto por profissionais que já possuem experiência sólida (Pleno ou Sênior), este grupo pode estar buscando recolocação devido a layoffs, ou procurando novas oportunidades que ofereçam maior crescimento e alinhamento de valores. São um ativo valioso para empresas que buscam talentos experientes.")
        
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
        st.info("""- **Oportunidade de Aceleração:** As Personas 1 e 4 (Talentos em Transição e Profissionais Qualificados) podem se beneficiar de programas de mentoria focados em 'soft skills' para entrevistas e networking, acelerando sua recolocação.\n- **Foco na Base:** A Persona 3 (Jovens Promessas) é a base do futuro. Parcerias com universidades e cursos introdutórios são essenciais para este grupo.\n- **Expansão e Inclusão Geográfica:** A Persona 2 (Novos Horizontes) prova a necessidade de fortalecer as redes de apoio e oportunidades para vagas remotas fora do eixo Sudeste.""")
    else:
        st.warning("Arquivos de resumo das personas não encontrados. Execute 'analysis.py' novamente.")

elif pagina_selecionada == "Análise de Voluntariado":
    st.title("Análise do Perfil de Voluntariado")
    if not df.empty and 'is_volunteer' in df.columns:
        voluntario_count = df[df['is_volunteer'] == 'Sim'].shape[0]; total_pessoas = df['person_id'].nunique(); taxa_voluntariado = (voluntario_count / total_pessoas) * 100; st.metric("Taxa de Voluntariado na Comunidade", f"{taxa_voluntariado:.1f}%"); st.markdown("---")
        
        st.subheader("Quem são as Pessoas Interessadas no Voluntariado?"); st.write("A análise das pessoas que se inscreveram para o voluntariado revela um perfil de **protagonismo e engajamento da base**. Longe de ser um grupo dominado pela senioridade, o interesse em voluntariar é majoritariamente expressado por profissionais em **nível Iniciante**. Isso demonstra uma incrível cultura de 'construir a comunidade que queremos', onde as pessoas que estão começando a carreira são as mais motivadas a doar seu tempo. A diversidade de personas interessadas, com destaque para **'Talentos em Transição' (Persona 1)** e **'Profissionais Qualificados' (Persona 4)**, mostra que o desejo de contribuir permeia todos os níveis de experiência.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Frequência de Áreas de Atuação");
            if os.path.exists(ATUACAO_COUNT_PATH):
                df_atuacao = pd.read_csv(ATUACAO_COUNT_PATH); fig, ax = plt.subplots(figsize=(10, 6)); sns.barplot(y='atuacao', x='count', data=df_atuacao.nlargest(10, 'count'), ax=ax, color=PRIMARY_COLOR, orient='h'); ax.set_xlabel("Nº de Menções"); ax.set_ylabel("Área de Atuação (Tags)"); st.pyplot(fig)
        with col2:
            st.subheader("Nível Profissional: Comparativo"); fig2, ax2 = plt.subplots(figsize=(10, 6)); crosstab_vol_level = pd.crosstab(df['professional_level_padronizado'], df['is_volunteer'], normalize='columns').mul(100); crosstab_vol_level.plot(kind='barh', ax=ax2, color=['grey', PRIMARY_COLOR]); ax2.set_xlabel("Percentual (%)"); ax2.set_ylabel("Nível Profissional"); ax2.xaxis.set_major_formatter(mtick.PercentFormatter()); st.pyplot(fig2)
        
        st.markdown("---"); st.subheader("Perfil Detalhado das Personas Voluntárias");
        if 'persona' in df.columns:
            df_vol = df[df['is_volunteer'] == 'Sim'].dropna(subset=['persona'])
            if not df_vol.empty:
                vol_persona_summary = df_vol.groupby('persona').agg(n_de_pessoas=('persona', 'size'), regiao_moda=('regiao', lambda x: x.mode().get(0, 'N/A')), nivel_profissional_moda=('professional_level_padronizado', lambda x: x.mode().get(0, 'N/A')), atuacao_principal_moda=('atuacao_principal', lambda x: x.mode().get(0, 'N/A'))).reset_index()
                st.dataframe(vol_persona_summary, hide_index=True)

                st.markdown("---")
                st.markdown("### Quem são Elas? Uma Análise das Personas Voluntárias")
                st.subheader("Persona 1 (Talentos em Transição): O Desejo de Crescer Junto"); st.write("Sendo o maior grupo entre os interessados, estas pessoas veem o voluntariado não apenas como uma forma de ajudar, mas também como uma oportunidade de ganhar experiência prática e construir portfólio. Sua principal área de interesse é **Tecnologia**, indicando um forte desejo de aplicar seus novos conhecimentos em projetos reais da comunidade.")
                st.subheader("Persona 2 (Novos Horizontes): Compartilhando a Experiência de Vida"); st.write("Representando a maturidade e a coragem da reinvenção, o interesse deste grupo no voluntariado é particularmente inspirador. Vindos majoritariamente da região Norte e focados na área de **Tecnologia**, eles buscam aplicar suas novas habilidades e, ao mesmo tempo, compartilhar a vasta experiência profissional e de vida que acumularam em outras carreiras. Sua participação enriquece a comunidade com diversidade de pensamento e resiliência.")
                st.subheader("Persona 3 (Jovens Promessas): Energia e Novas Ideias"); st.write("Este grupo traz a energia da nova geração. Seu interesse se concentra em **Engajamento**, sugerindo um desejo de atuar na linha de frente da comunidade, organizando eventos, gerenciando redes sociais e garantindo que o ambiente seja acolhedor e vibrante. Eles são a voz e o coração da comunidade.")
                st.subheader("Persona 4 (Profissionais Qualificados): A Vontade de Retribuir"); st.write("Este grupo, composto por profissionais mais experientes, demonstra o clássico desejo de 'retribuir'. Eles são a espinha dorsal técnica do voluntariado, também focando na área de **Tecnologia**. Sua presença é vital para a mentoria de pessoas mais novas e para a viabilidade de projetos mais complexos.")
            else:
                st.info("Ainda não há dados suficientes para cruzar personas e voluntariado.")