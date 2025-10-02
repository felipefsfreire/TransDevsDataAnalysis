# -*- coding: utf-8 -*-

"""
Script Principal de Análise de Dados - TransDevs Data Analysis (VERSÃO FINAL COMPLETA)
Autor: [Seu Nome] & Smith (Mentor)
Data: 02/10/2025
"""

import logging
import pandas as pd
import os
from datetime import datetime
import re
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import numpy as np # <-- NOVA IMPORTAÇÃO

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', handlers=[logging.FileHandler("analysis.log", mode='w'), logging.StreamHandler()])
logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_INSCRICOES_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw', '20250916-div_inscricoes.csv')
RAW_PROFILE_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw', '20250916-div_profile.csv')
RAW_VOLUNTARIADO_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw', '20250916-div_voluntariado.csv')
PROCESSED_FINAL_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed', 'dados_consolidados_comunidade.csv')
PERSONA_SUMMARY_PATH = os.path.join(PROJECT_ROOT, 'reports', 'persona_summary_refinado.csv')
PERSONA_DETAILS_PATH = os.path.join(PROJECT_ROOT, 'reports', 'persona_details_refinado.csv')
ATUACAO_COUNT_PATH = os.path.join(PROJECT_ROOT, 'reports', 'atuacao_voluntariado_counts.csv')
CRESCIMENTO_PATH = os.path.join(PROJECT_ROOT, 'reports', 'crescimento_mensal.csv')
CIDADES_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw', 'cities.csv')
MAP_SUMMARY_PATH = os.path.join(PROJECT_ROOT, 'reports', 'mapa_resumo_estados.csv')
STATES_COORDS_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw', 'brazil_states_coords.csv')

def carregar_dados(caminho_arquivo: str) -> pd.DataFrame:
    logger.info(f"Carregando arquivo: {os.path.basename(caminho_arquivo)}")
    try:
        if not os.path.exists(caminho_arquivo):
            logger.warning(f"Arquivo não encontrado: {caminho_arquivo}")
            return pd.DataFrame()
        df = pd.read_csv(caminho_arquivo)
        logger.info(f"Dados carregados com sucesso. Shape: {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Erro ao carregar o arquivo: {e}")
        return pd.DataFrame()

def padronizar_categorias(series: pd.Series, mapa_variacoes: dict, padrao: str) -> pd.Series:
    mapa_direto = {v: k for k, l in mapa_variacoes.items() for v in l}
    def mapear_valor(valor):
        if pd.isna(valor): return padrao
        texto_limpo = re.sub(r'\[|\]|"|etnia_|identidade_', '', str(valor).lower().strip())
        if texto_limpo in mapa_direto: return mapa_direto[texto_limpo]
        for v, p in mapa_direto.items():
            if v in texto_limpo: return p
        return padrao
    return series.apply(mapear_valor)

def processar_dados_inscricoes(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("--- Processando Dados de Inscrições ---")
    df_anon = df.copy()
    df_anon['email'] = df['email'].str.lower().str.strip()
    df_anon['person_id'] = pd.factorize(df_anon['email'])[0] + 1
    computador_map = {1.0: 'Sim', 0.0: 'Não'}
    df_anon['computador_acesso'] = df_anon['computador'].map(computador_map).fillna('Não Respondeu')
    df_anon['nascdt_temp'] = df['nascdt']
    estado_variacoes = {'SP': ['são paulo', 'sp'], 'RJ': ['rio de janeiro', 'rj'], 'MG': ['minas gerais', 'mg', 'bh'], 'BA': ['bahia', 'ba'], 'CE': ['ceará', 'ce', 'ceara'], 'PE': ['pernambuco', 'pe'], 'PR': ['paraná', 'pr', 'parana'], 'RS': ['rio grande do sul', 'rs'], 'SC': ['santa catarina', 'sc'], 'GO': ['goiás', 'go', 'goias'], 'DF': ['distrito federal', 'df'], 'AM': ['amazonas'], 'RO': ['rondônia'], 'RN': ['rio grande do norte', 'rn'], 'AL': ['alagoas'], 'ES': ['espirito santo', 'es'], 'PA': ['pará', 'para'], 'MA': ['maranhão', 'ma'], 'SE': ['sergipe'], 'PI': ['piauí', 'piaui'], 'MS': ['mato grosso do sul', 'ms'], 'MT': ['mato grosso', 'mt'], 'PB': ['paraíba', 'paraiba'], 'AC': ['acre'], 'TO': ['tocantins'], 'RR': ['roraima'], 'Internacional': ['portugal', 'lisboa', 'espanha', 'oizumi', 'gunma', 'murcia', 'amadora', 'matosinhos']}
    df_anon['estado_padronizado'] = padronizar_categorias(df_anon['estado'], estado_variacoes, 'Inválido')
    regiao_map = {'AC': 'Norte', 'AP': 'Norte', 'AM': 'Norte', 'PA': 'Norte', 'RO': 'Norte', 'RR': 'Norte', 'TO': 'Norte','AL': 'Nordeste', 'BA': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Nordeste', 'PB': 'Nordeste', 'PE': 'Nordeste', 'PI': 'Nordeste', 'RN': 'Nordeste', 'SE': 'Nordeste','DF': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste','ES': 'Sudeste', 'MG': 'Sudeste', 'RJ': 'Sudeste', 'SP': 'Sudeste','PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul'}
    df_anon['regiao'] = df_anon['estado_padronizado'].map(regiao_map)
    etnia_variacoes = {'Branca': ['branca'], 'Parda': ['parda'], 'Preta': ['preta'], 'Amarela': ['amarela'], 'Indígena': ['indigena'], 'Múltiplas': ['preta,parda'], 'Preferiu não informar': ['nao_quero_responder', 'outro', '[]']}
    df_anon['etnia_padronizada'] = padronizar_categorias(df_anon['etnia'], etnia_variacoes, 'Preferiu não informar')
    genero_variacoes = {'Pessoa Trans': ['trans', 'transgenero', 'transsexual', 'transmasculino'], 'Mulher Trans': ['mulher trans'], 'Homem Trans': ['homem trans'], 'Não-Binárie': ['nao binarie', 'nao-binario', 'nao-binarie', 'agênero'], 'Travesti': ['travesti'], 'Cisgênero': ['cis', 'cisgenere', 'homem', 'mulher'], 'Queer': ['queer'], 'Outra identidade': ['outro', 'intersexo'], 'Preferiu não informar': ['nao_sei', 'nao_quero_responder', '[]']}
    df_anon['genero_padronizado'] = padronizar_categorias(df_anon['genero'], genero_variacoes, 'Preferiu não informar')
    df_anon['nascdt_dt'] = pd.to_datetime(df_anon['nascdt_temp'], errors='coerce', dayfirst=True); df_anon['idade'] = (datetime.now() - df_anon['nascdt_dt']).dt.days / 365.25; bins = [0, 17, 24, 34, 44, 54, 64, 150]; labels = ['Menor de 18', '18-24 anos', '25-34 anos', '35-44 anos', '45-54 anos', '55-64 anos', '65+ anos']; df_anon['faixa_etaria'] = pd.cut(df_anon['idade'], bins=bins, labels=labels, right=False)
    colunas_a_manter = list(dict.fromkeys([col for col in df.columns] + ['person_id', 'computador_acesso', 'estado_padronizado', 'cidade', 'regiao', 'etnia_padronizada', 'genero_padronizado', 'idade', 'faixa_etaria'])); colunas_a_remover = ['nascdt_temp', 'nascdt_dt', 'estado', 'etnia', 'genero', 'email', 'id', 'nome_completo', 'nascdt', 'telefone', 'nome_primeiro', 'nome_ultimo', 's_link', 'computador']; colunas_a_manter = [col for col in colunas_a_manter if col not in colunas_a_remover]; return df_anon[colunas_a_manter]

def processar_dados_perfil(df_profile: pd.DataFrame) -> pd.DataFrame:
    logger.info("--- Processando Dados de Perfil ---")
    if df_profile.empty: return pd.DataFrame()
    df_processado = df_profile.copy(); df_processado['email'] = df_processado['email'].str.lower().str.strip(); df_processado['person_id'] = pd.factorize(df_processado['email'])[0] + 1; level_variacoes = {'Iniciante': ['iniciante'], 'Estagiário': ['estagiário', 'estagiario'], 'Júnior': ['júnior', 'junior'], 'Pleno': ['pleno'], 'Sênior': ['sênior', 'senior'], 'Especialista': ['especialista'], 'Liderança': ['liderança', 'lideranca', 'c-level'], 'Outro': ['outro']}; df_processado['professional_level_padronizado'] = padronizar_categorias(df_processado['professional_level'], level_variacoes, 'Não informado'); ordem_nivel = ['Iniciante', 'Estagiário', 'Júnior', 'Pleno', 'Sênior', 'Especialista', 'Liderança', 'Outro', 'Não informado']; df_processado['professional_level_padronizado'] = pd.Categorical(df_processado['professional_level_padronizado'], categories=ordem_nivel, ordered=True); colunas_profissionais = ['person_id', 'professional_level_padronizado', 'professional_area', 'professional_technologies', 'professional_tools', 'working', 'schooling']; colunas_a_manter = [col for col in colunas_profissionais if col in df_processado.columns]; return df_processado[colunas_a_manter]

def processar_dados_voluntariado(df_voluntariado: pd.DataFrame) -> pd.DataFrame:
    logger.info("--- Processando Dados de Voluntariado ---")
    if df_voluntariado.empty: return pd.DataFrame()
    df_processado = df_voluntariado.copy(); df_processado['email'] = df_processado['email'].str.lower().str.strip(); df_processado['person_id'] = pd.factorize(df_processado['email'])[0] + 1; df_processado['is_volunteer'] = 'Sim'; df_processado['atuacao_tags'] = df_processado['atuacao'].str.lower().str.replace(r'\[|\]|"', '', regex=True).str.split(',').apply(lambda x: [tag.strip() for tag in x] if isinstance(x, list) else []); df_processado['atuacao_principal'] = df_processado['atuacao_tags'].apply(lambda x: x[0] if x else 'Não informado'); colunas_relevantes = ['person_id', 'is_volunteer', 'atuacao_principal', 'atuacao_tags']; colunas_a_manter = [col for col in colunas_relevantes if col in df_processado.columns]; return df_processado[colunas_a_manter]

def descobrir_personas_com_clustering(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("="*50 + "\n== INICIANDO FASE DE MACHINE LEARNING (FINAL) ==" + "\n" + "="*50)
    features = ['faixa_etaria', 'professional_level_padronizado', 'working', 'idade']
    df_model = df.dropna(subset=features)
    if df_model.shape[0] < 10: logger.error("Não há dados suficientes para clustering."); return df
    categorical_features = ['faixa_etaria', 'professional_level_padronizado', 'working']; numerical_features = ['idade']; preprocessor = ColumnTransformer(transformers=[('num', StandardScaler(), numerical_features), ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)])
    K_IDEAL = 4; kmeans_final = KMeans(n_clusters=K_IDEAL, random_state=42, n_init=10); pipeline_final = Pipeline(steps=[('preprocessor', preprocessor), ('cluster', kmeans_final)])
    df['persona'] = pd.Series(pipeline_final.fit_predict(df_model) + 1, index=df_model.index)
    logger.info("--- Gerando Resumo das Personas ---")
    summary = df.groupby('persona').agg(regiao_moda=('regiao', lambda x: x.mode().get(0, 'N/A')), faixa_etaria_moda=('faixa_etaria', lambda x: x.mode().get(0, 'N/A')), nivel_profissional_moda=('professional_level_padronizado', lambda x: x.mode().get(0, 'N/A')), acesso_computador_moda=('computador_acesso', lambda x: x.mode().get(0, 'N/A')), idade_media=('idade', 'mean'), n_de_pessoas=('persona', 'size')).reset_index()
    summary['persona'] = summary['persona'].astype(int); summary['idade_media'] = summary['idade_media'].round(1)
    summary.to_csv(PERSONA_SUMMARY_PATH, index=False); logger.info(f"Resumo principal das personas salvo em {PERSONA_SUMMARY_PATH}")
    details_list = []
    for persona_id in sorted(df['persona'].dropna().unique()):
        df_persona = df[df['persona'] == persona_id]
        tech_tags = df_persona['professional_technologies'].dropna().str.lower().str.replace(r'\[|\]|"', '', regex=True).str.split(',').explode()
        top_3_tech = tech_tags.str.strip().value_counts(normalize=True).nlargest(3) * 100
        details = {'persona': int(persona_id), 'top_schooling': [f"{idx}: {val:.1f}%" for idx, val in (df_persona['schooling'].value_counts(normalize=True).nlargest(3) * 100).items()], 'top_technologies': [f"{idx}: {val:.1f}%" for idx, val in top_3_tech.items()], 'level_distribution': [f"{idx}: {val:.1f}%" for idx, val in (df_persona['professional_level_padronizado'].value_counts(normalize=True) * 100).items()]}; details_list.append(details)
    df_details = pd.DataFrame(details_list); df_details.to_csv(PERSONA_DETAILS_PATH, index=False); logger.info(f"Detalhes das personas salvos em {PERSONA_DETAILS_PATH}")
    return df

def gerar_analise_de_crescimento(df_inscricoes: pd.DataFrame):
    logger.info("--- Gerando Análise de Crescimento da Comunidade ---")
    if df_inscricoes.empty or 'data' not in df_inscricoes.columns:
        logger.warning("DataFrame de inscrições vazio ou sem coluna 'data'. Análise de crescimento pulada."); return
    df_growth = df_inscricoes[['email', 'data']].copy(); df_growth['email'] = df_growth['email'].str.lower().str.strip(); df_growth['person_id'] = pd.factorize(df_growth['email'])[0] + 1
    df_growth['data_inscricao'] = pd.to_datetime(df_growth['data'], errors='coerce'); df_growth = df_growth.dropna(subset=['data_inscricao'])
    primeira_inscricao = df_growth.loc[df_growth.groupby('person_id')['data_inscricao'].idxmin()]; primeira_inscricao['periodo'] = primeira_inscricao['data_inscricao'].dt.to_period('M')
    novas_pessoas_por_mes = primeira_inscricao.groupby('periodo').size().reset_index(name='novas_pessoas'); novas_pessoas_por_mes['periodo'] = novas_pessoas_por_mes['periodo'].astype(str)
    novas_pessoas_por_mes['total_acumulado'] = novas_pessoas_por_mes['novas_pessoas'].cumsum()
    novas_pessoas_por_mes.to_csv(CRESCIMENTO_PATH, index=False); logger.info(f"Análise de crescimento salva em: {CRESCIMENTO_PATH}")

def main():
    logger.info("="*50 + "\n==  INICIANDO PIPELINE DE DADOS COMPLETO (FINAL)  ==" + "\n" + "="*50)
    df_inscricoes_raw = carregar_dados(RAW_INSCRICOES_PATH); df_profile_raw = carregar_dados(RAW_PROFILE_PATH); df_voluntariado_raw = carregar_dados(RAW_VOLUNTARIADO_PATH); df_states_coords = carregar_dados(STATES_COORDS_PATH)
    if df_inscricoes_raw.empty: logger.error("Arquivo de inscrições não encontrado. Pipeline interrompido."); return
    gerar_analise_de_crescimento(df_inscricoes_raw)
    df_demografico = processar_dados_inscricoes(df_inscricoes_raw); df_profissional = processar_dados_perfil(df_profile_raw); df_voluntario = processar_dados_voluntariado(df_voluntariado_raw)
    logger.info("Iniciando merges..."); df_consolidado = pd.merge(df_demografico, df_profissional, on='person_id', how='left'); df_final = pd.merge(df_consolidado, df_voluntario, on='person_id', how='left')
    df_final['is_volunteer'] = df_final['is_volunteer'].fillna('Não'); logger.info(f"Merges concluídos. Shape final: {df_final.shape}")
    if 'atuacao_tags' in df_final.columns:
        atuacao_counts = df_final[df_final['is_volunteer'] == 'Sim']['atuacao_tags'].explode().value_counts().reset_index(); atuacao_counts.columns = ['atuacao', 'count']; atuacao_counts.to_csv(ATUACAO_COUNT_PATH, index=False); logger.info(f"Contagem de tags de atuação salva em {ATUACAO_COUNT_PATH}")
    
    df_final = descobrir_personas_com_clustering(df_final)

    if 'estado_padronizado' in df_final.columns and df_states_coords is not None:
        logger.info("Gerando resumo para o mapa de estados...")
        map_summary = df_final[df_final['estado_padronizado'] != 'Inválido'].groupby('estado_padronizado').agg(n_de_pessoas=('person_id', 'count')).reset_index()
        map_summary_final = pd.merge(map_summary, df_states_coords, left_on='estado_padronizado', right_on='uf', how='left')
        map_summary_final['size_sqrt'] = np.sqrt(map_summary_final['n_de_pessoas']) # <-- NOVO: Coluna para tamanho da bolha
        map_summary_final.to_csv(MAP_SUMMARY_PATH, index=False)
        logger.info(f"Resumo do mapa (com coordenadas) salvo em: {MAP_SUMMARY_PATH}")
    
    df_final.to_csv(PROCESSED_FINAL_PATH, index=False); logger.info(f"Dados consolidados e enriquecidos (com personas) salvos em: {PROCESSED_FINAL_PATH}")
    logger.info("Pipeline completo finalizado com sucesso.")

if __name__ == "__main__":
    main()