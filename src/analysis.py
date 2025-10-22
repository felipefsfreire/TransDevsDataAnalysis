# -*- coding: utf-8 -*-

"""
Script Principal de Análise de Dados - TransDevs Data Analysis (VERSÃO FINAL)

Este script implementa um pipeline completo para processar e analisar dados
de inscrições, perfis e voluntariado da comunidade TransDevs.
Ele padroniza dados demográficos e profissionais, identifica usuários únicos,
cria personas de usuários usando clustering e gera relatórios sobre
crescimento da comunidade e distribuição geográfica.

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
import numpy as np

# Configuração do sistema de logging para registrar eventos e erros.
# As mensagens serão salvas em 'analysis.log' e também exibidas no console.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', handlers=[logging.FileHandler("analysis.log", mode='w'), logging.StreamHandler()])
logger = logging.getLogger(__name__)

# Define o caminho raiz do projeto para localizar os arquivos de dados e relatórios.
# Isso garante que o script funcione independentemente de onde é executado.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Caminhos para os arquivos de dados brutos (raw data).
RAW_INSCRICOES_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw', '20250916-div_inscricoes.csv')
RAW_PROFILE_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw', '20250916-div_profile.csv')
RAW_VOLUNTARIADO_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw', '20250916-div_voluntariado.csv')
RAW_CIDADES_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw', 'cities.csv') # Adicionado para clareza
STATES_COORDS_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw', 'brazil_states_coords.csv')

# Caminhos para os arquivos de dados processados e relatórios.
PROCESSED_FINAL_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed', 'dados_consolidados_comunidade.csv')
PERSONA_SUMMARY_PATH = os.path.join(PROJECT_ROOT, 'reports', 'persona_summary_refinado.csv')
PERSONA_DETAILS_PATH = os.path.join(PROJECT_ROOT, 'reports', 'persona_details_refinado.csv')
ATUACAO_COUNT_PATH = os.path.join(PROJECT_ROOT, 'reports', 'atuacao_voluntariado_counts.csv')
CRESCIMENTO_PATH = os.path.join(PROJECT_ROOT, 'reports', 'crescimento_mensal.csv')
CIDADES_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw', 'cities.csv') # Duplicado, manter um.
MAP_SUMMARY_PATH = os.path.join(PROJECT_ROOT, 'reports', 'mapa_resumo_estados.csv')


def carregar_dados(caminho_arquivo: str) -> pd.DataFrame:
    """Carrega dados de um arquivo CSV em um DataFrame do Pandas.

    Registra informações sobre o carregamento e manipula erros de arquivo não encontrado.

    Args:
        caminho_arquivo (str): O caminho completo para o arquivo CSV.

    Returns:
        pd.DataFrame: Um DataFrame contendo os dados do arquivo, ou um DataFrame vazio
                      em caso de erro ou arquivo não encontrado.
    """
    logger.info(f"Carregando arquivo: {os.path.basename(caminho_arquivo)}")
    try:
        if not os.path.exists(caminho_arquivo):
            logger.warning(f"Arquivo não encontrado: {caminho_arquivo}")
            return pd.DataFrame()  # Retorna DataFrame vazio se o arquivo não existir
        df = pd.read_csv(caminho_arquivo)
        logger.info(f"Dados carregados com sucesso. Shape: {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Erro ao carregar o arquivo {caminho_arquivo}: {e}")
        return pd.DataFrame()  # Retorna DataFrame vazio em caso de exceção


def padronizar_categorias(series: pd.Series, mapa_variacoes: dict, padrao: str) -> pd.Series:
    """Padroniza valores de uma série do Pandas usando um mapa de variações.

    Converte variações de texto para uma categoria padrão definida no mapa.
    Remove caracteres indesejados e ignora maiúsculas/minúsculas.

    Args:
        series (pd.Series): A série do Pandas a ser padronizada.
        mapa_variacoes (dict): Um dicionário onde as chaves são as categorias
                               padronizadas e os valores são listas de suas variações.
        padrao (str): O valor padrão a ser atribuído se nenhuma variação for encontrada
                      ou se o valor for nulo.

    Returns:
        pd.Series: A série com os valores padronizados.
    """
    # Cria um mapa direto de variações para categorias padronizadas.
    # Ex: {'sao paulo': 'SP', 'sp': 'SP'}
    mapa_direto = {v: k for k, l in mapa_variacoes.items() for v in l}

    def mapear_valor(valor):
        """Função interna para mapear um único valor."""
        if pd.isna(valor):
            return padrao  # Retorna o padrão para valores nulos
        
        # Limpa o texto do valor, removendo caracteres especiais e convertendo para minúsculas.
        texto_limpo = re.sub(r'\[|\]|"|etnia_|identidade_', '', str(valor).lower().strip())
        
        # Tenta encontrar uma correspondência exata no mapa direto.
        if texto_limpo in mapa_direto:
            return mapa_direto[texto_limpo]
        
        # Se não houver correspondência exata, verifica se a variação está contida no texto limpo.
        for v, p in mapa_direto.items():
            if v in texto_limpo:
                return p
        
        # Se nenhuma correspondência for encontrada, retorna o padrão.
        return padrao
    
    # Aplica a função de mapeamento a cada elemento da série.
    return series.apply(mapear_valor)


def processar_dados_inscricoes(df: pd.DataFrame) -> pd.DataFrame:
    """Processa e padroniza os dados de inscrições.

    Realiza anonimização de e-mails, cria um ID de pessoa, padroniza
    campos como acesso a computador, estado, cidade, região, etnia, gênero,
    calcula idade e faixa etária. Remove colunas sensíveis e redundantes.

    Args:
        df (pd.DataFrame): DataFrame contendo os dados brutos de inscrições.

    Returns:
        pd.DataFrame: DataFrame processado com colunas padronizadas e enriquecidas.
    """
    logger.info("--- Processando Dados de Inscrições ---")
    df_anon = df.copy()

    # Anonimiza o e-mail e gera um 'person_id' único para cada e-mail.
    df_anon['email'] = df['email'].str.lower().str.strip()
    df_anon['person_id'] = pd.factorize(df_anon['email'])[0] + 1

    # Mapeia valores numéricos de 'computador' para strings descritivas.
    computador_map = {1.0: 'Sim', 0.0: 'Não'}
    df_anon['computador_acesso'] = df_anon['computador'].map(computador_map).fillna('Não Respondeu')
    
    # Coluna temporária para processamento da data de nascimento.
    df_anon['nascdt_temp'] = df['nascdt']

    # Define as variações de nomes de estados para padronização.
    estado_variacoes = {'SP': ['são paulo', 'sp'], 'RJ': ['rio de janeiro', 'rj'], 'MG': ['minas gerais', 'mg', 'bh'], 'BA': ['bahia', 'ba'], 'CE': ['ceará', 'ce', 'ceara'], 'PE': ['pernambuco', 'pe'], 'PR': ['paraná', 'pr', 'parana'], 'RS': ['rio grande do sul', 'rs'], 'SC': ['santa catarina', 'sc'], 'GO': ['goiás', 'go', 'goias'], 'DF': ['distrito federal', 'df'], 'AM': ['amazonas'], 'RO': ['rondônia'], 'RN': ['rio grande do norte', 'rn'], 'AL': ['alagoas'], 'ES': ['espirito santo', 'es'], 'PA': ['pará', 'para'], 'MA': ['maranhão', 'ma'], 'SE': ['sergipe'], 'PI': ['piauí', 'piaui'], 'MS': ['mato grosso do sul', 'ms'], 'MT': ['mato grosso', 'mt'], 'PB': ['paraíba', 'paraiba'], 'AC': ['acre'], 'TO': ['tocantins'], 'RR': ['roraima'], 'Internacional': ['portugal', 'lisboa', 'espanha', 'oizumi', 'gunma', 'murcia', 'amadora', 'matosinhos']}
    df_anon['estado_padronizado'] = padronizar_categorias(df_anon['estado'], estado_variacoes, 'Inválido')

    # Define um mapa reverso de cidades para estados para ajudar na padronização da cidade.
    # Este mapa é usado para validar se uma cidade pertence a um estado específico.
    cidade_map_reverso = {v.lower(): k for k, v_list in {'SP': ['são paulo', 'sp', 'sao paulo', 'sãopaulo', 'osasco', 'jaú', 'jau', 'itapecerica da serra', 'sumaré', 'suzano', 'campinas', 'guarulhos', 'ribeirão preto', 'ribeirao preto', 'ribeirão preto/sp', 'mauá', 'maua', 'itaquaquetuba', 'presidente prudente', 'sertãozinho', 'vila sônia', 'são bernardo do campo', 'sao bernardo do campo', 'rio claro', 'taubaté', 'atibaia', 'embu das artes', 'embú das artes', 'santo andré', 'santo andre', 'piracicaba', 'votorantim', 'são vicente', 'são caetano do sul', 'ribeirão pires', 'barueri', 'sorocaba', 'bauru', 'mongaguá', 'jundiaí', 'jundiai', 'itupeva', 'santos', 'jales', 'cosmópolis', 'carapicuíba', 'carapicuiba', 'agudos', 'paulínia', 'santo amaro', 'mogi mirim', 'aruja', 'diadema', 'praia grande', 'mairiporã', 'lorena', 'limeira', 'matão', 'guarujá', 'são joão da boa vista', 'araraquara', 'campo limpo paulista', 'várzea paulista', 'francisco morato', 'são josé do rio preto', 'americana', 'marilia', 'ibiporã', 'catanduva', 'piratininga', 'franco da rocha', 'são carlos', 'assis', 'mogi das cruzes', 'santana de parnaíba', 'vargem grande paulista', 'mirassol', 'tuiuti', 'araçatuba', 'itápolis', 'ibiúna', 'itararé', 'campos novos paulista', 'piedade', 'são jose dos campos', 'ituverava', 'indaiatuba', 'pindamonhangaba', 'franca', 'itatiba', 'santa bárbara d’oeste', "santa bárbara d'oeste"], 'RJ': ['rio de janeiro', 'rj', 'eio de janeiro', 'rio de janeieo', 'angra dos reis', 'nova iguaçu', 'cachoeirinhas', 'duque de caxias', 'são joão de meriti', 'resende', 'campos dos goytacazes', 'caompos dos goytacazes', 'nilópolis', 'araruama', 'teresópolis', 'teresopolis', 'barra mansa', 'niterói', 'niteroi', 'rio de janeiro niteroi', 'paracambi', 'rio das pedras', 'belford roxo', 'magé', 'magé - rj', 'três rios', 'maricá', 'marica', 'itaboraí', 'queimados', 'ramos', 'seropédica', 'são gonçalo', 'sao goncalo'], 'MG': ['minas gerais', 'mg', 'minaa gerais', 'bh', 'belo horizonte', 'malacacheta', 'sabará', 'vitória da conquista', 'juiz de fora', 'betim', 'são joão del rei', 'alfenas', 'diamantina', 'nova lima', 'três corações', 'ituiutaba', 'joão monlevade', 'uberlândia', 'uberlandia', 'uberaba', 'vespasiano', 'ponte nova', 'contagem', 'montes claros', 'curvelo', 'divinópolis', 'ipatinga', 'patrocínio', 'brasília de minas', 'lavras', 'itajubá'], 'BA': ['bahia', 'ba', 'salvador', 'senhor do bonfim', 'trancoso', 'porto seguro', 'ilhéus', 'camaçari', 'são francisco do conde', 'barreiro', 'santo antônio de jesus', 'bom jesus da lapa', 'lauro de freitas', 'alagoinhas', 'simões filho', 'juazeiro', 'guanambi', 'feira de santana'], 'CE': ['ceará', 'ce', 'ceara', 'fortaleza', 'maracanaú', 'jaguaruana', 'canindé', 'sobral', 'crateús', 'ipu', 'camocim', 'itapipoca', 'russas', 'caucaia', 'campos sales'], 'PE': ['pernambuco', 'pe', 'recife', 'paulista', 'olinda', 'abreu e lima', 'carpina', 'jaboatão dos guararapes', 'jaboatao dos guararapes', 'camaragibe', 'são lourenço da mata', 'igarassu', 'caruaru', 'petrolina'], 'PR': ['paraná', 'pr', 'parana', 'curitiba', 'guarapuava', 'araucária', 'maringá', 'prudentópolis', 'mandirituba', 'paranaguá', 'piraquara', 'ponta grossa', 'ponta grossa - pr', 'goioerê', 'londrina', 'bandeirantes', 'pinhais', 'sarandi', 'imbituva', 'campo mourão', 'campo mourão / pr', 'cornélio procópio', 'toledo', 'pitanga', 'nova prata do iguaçu', 'laranjeiras do sul'], 'RS': ['rio grande do sul', 'rs', 'porto alegre', 'três passos', 'triunfo', 'sapiranga', 'são leopoldo', 'sao leopoldo', 'canoas', 'santa maria', 'pelotas', 'viamão', 'ijuí', 'guaíba', 'caxias do sul', 'rio grande', 'bage', 'alvorada', 'novo hamburgo', 'esteio', 'sapucaia do sul', 'campo bom', 'passo fundo', 'cacequi', 'coração de maría'], 'SC': ['santa catarina', 'sc', 'florianopolis', 'florianópolis', 'joinville', 'santa luzia', 'brusque', 'capivari de baixo', 'garopaba', 'balneário camburiú', 'são josé', 'tubarão', 'itajai', 'palhoça', 'lages', 'são francisco do sul', 'biguaçu', 'canoinhas', 'navegantes'], 'GO': ['goiás', 'go', 'goias', 'goiânia', 'valparaiso', 'anápolis', 'planaltina', 'águas lindas', 'águas lindas de goiás', 'valparaíso de goiás', 'senador canedo', 'aparecida de goiânia'], 'DF': ['distrito federal', 'df', 'brasília', 'brasilia', 'brasília - df', 'paranoá', 'taguatinga norte', 'cidade ocidental', 'recanto das emas', 'gama'], 'AM': ['amazonas', 'manaus', 'manaus - am'], 'RO': ['rondônia', 'porto velho', 'cacoal'], 'RN': ['rio grande do norte', 'rn', 'natal', 'são gonçalo do amarante', 'mossoró', 'são josé de mipibu', 'parnamirim', 'jucurutu'], 'AL': ['alagoas', 'maceió', 'maceio', 'delmiro gouveia'], 'ES': ['espirito santo', 'esporo santo', 'es', 'vitoria', 'vitória', 'vila velha', 'cariacica', 'serra', 'guarapari', 'viana'], 'PA': ['pará', 'para', 'belém', 'belem', 'ananindeua', 'marabá', 'castanhal', 'augusto corrêa', 'parauapebas'], 'MA': ['maranhão', 'ma', 'são luís', 'sao luis'], 'SE': ['sergipe', 'aracaju'], 'PI': ['piauí', 'piaui', 'teresina', 'parnaíba', 'miguel alves'], 'MS': ['mato grosso do sul', 'ms', 'campo grande', 'dourados'], 'MT': ['mato grosso', 'mt', 'cuiabá', 'várzea grande', 'nova mutum', 'rondonópolis'], 'PB': ['paraíba', 'paraiba', 'joão pessoa', 'joao pessoa', 'campina grande', 'cabedelo', 'mamanguape', 'mamanaguape', 'remígio'], 'AC': ['acre', 'rio branco', 'sena madureira'], 'TO': ['tocantins', 'palmas', 'araguaína'], 'RR': ['roraima', 'boa vista'], 'Internacional': ['internacional', 'portugal', 'lisboa', 'porto', 'espanha', 'oizumi', 'gunma', 'murcia', 'amadora', 'matosinhos']}.items() for v in v_list}
    
    def padronizar_cidade_final(row):
        """Função interna para padronizar o nome da cidade."""
        cidade_str = row['cidade']
        estado_sigla = row['estado_padronizado']
        
        if pd.isna(cidade_str):
            return 'Não Informado'
        
        # Limpa o nome da cidade.
        cidade_limpa = re.split(r'/|,|-', str(cidade_str).lower().strip())[0].strip()
        
        # Verifica se a cidade limpa está no mapa reverso e se o estado corresponde.
        if cidade_limpa in cidade_map_reverso:
            estado_cidade_mapeada = cidade_map_reverso[cidade_limpa]
            if estado_cidade_mapeada == estado_sigla:
                return cidade_limpa.title() # Capitaliza a primeira letra
        
        # Lista de "lixo" para filtrar valores inválidos ou genéricos.
        lixo = ['Rj', 'Sp', 'Mg', 'Ba', 'Sc', 'Rs', 'Paraná', 'Df', 'Es', 'Ma', 'Mt', 'Rn', 'fasdfasd', 'asfa', 'sdfasd', 'afsdfasdfdsa', 'Prefiro Não Informar', 'Solteiro(A)', 'Solteiro (A)', 'Casado', 'Solteiro', 'Solteira']
        
        # Se a cidade está na lista de lixo ou é apenas dígitos, considera inválida.
        if cidade_limpa in [l.lower() for l in lixo] or cidade_limpa.isdigit():
            return 'Inválido'
        
        return cidade_limpa.title()

    df_anon['cidade_padronizada'] = df_anon.apply(padronizar_cidade_final, axis=1)

    # Mapeia estados padronizados para regiões geográficas do Brasil.
    regiao_map = {'AC': 'Norte', 'AP': 'Norte', 'AM': 'Norte', 'PA': 'Norte', 'RO': 'Norte', 'RR': 'Norte', 'TO': 'Norte','AL': 'Nordeste', 'BA': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Nordeste', 'PB': 'Nordeste', 'PE': 'Nordeste', 'PI': 'Nordeste', 'RN': 'Nordeste', 'SE': 'Nordeste','DF': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste','ES': 'Sudeste', 'MG': 'Sudeste', 'RJ': 'Sudeste', 'SP': 'Sudeste','PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul'}
    df_anon['regiao'] = df_anon['estado_padronizado'].map(regiao_map)

    # Padroniza a coluna de etnia.
    etnia_variacoes = {'Branca': ['branca'], 'Parda': ['parda'], 'Preta': ['preta'], 'Amarela': ['amarela'], 'Indígena': ['indigena'], 'Múltiplas': ['preta,parda'], 'Preferiu não informar': ['nao_quero_responder', 'outro', '[]']}
    df_anon['etnia_padronizada'] = padronizar_categorias(df_anon['etnia'], etnia_variacoes, 'Preferiu não informar')

    # Padroniza a coluna de gênero.
    genero_variacoes = {'Pessoa Trans': ['trans', 'transgenero', 'transsexual', 'transmasculino'], 'Mulher Trans': ['mulher trans'], 'Homem Trans': ['homem trans'], 'Não-Binárie': ['nao binarie', 'nao-binario', 'nao-binarie', 'agênero'], 'Travesti': ['travesti'], 'Cisgênero': ['cis', 'cisgenere', 'homem', 'mulher'], 'Queer': ['queer'], 'Outra identidade': ['outro', 'intersexo'], 'Preferiu não informar': ['nao_sei', 'nao_quero_responder', '[]']}
    df_anon['genero_padronizado'] = padronizar_categorias(df_anon['genero'], genero_variacoes, 'Preferiu não informar')
    
    # Converte a data de nascimento para datetime, calcula a idade e cria faixas etárias.
    df_anon['nascdt_dt'] = pd.to_datetime(df_anon['nascdt_temp'], errors='coerce', dayfirst=True)
    df_anon['idade'] = (datetime.now() - df_anon['nascdt_dt']).dt.days / 365.25
    bins = [0, 17, 24, 34, 44, 54, 64, 150]
    labels = ['Menor de 18', '18-24 anos', '25-34 anos', '35-44 anos', '45-54 anos', '55-64 anos', '65+ anos']
    df_anon['faixa_etaria'] = pd.cut(df_anon['idade'], bins=bins, labels=labels, right=False)

    # Define as colunas a serem mantidas e removidas para o DataFrame final.
    # Garante que 'person_id' e as colunas padronizadas sejam mantidas.
    colunas_a_manter = list(dict.fromkeys([col for col in df.columns] + ['person_id', 'computador_acesso', 'estado_padronizado', 'cidade_padronizada', 'regiao', 'etnia_padronizada', 'genero_padronizado', 'idade', 'faixa_etaria']))
    colunas_a_remover = ['nascdt_temp', 'nascdt_dt', 'estado', 'etnia', 'genero', 'email', 'id', 'nome_completo', 'nascdt', 'telefone', 'nome_primeiro', 'nome_ultimo', 's_link', 'computador', 'cidade']
    colunas_a_manter = [col for col in colunas_a_manter if col not in colunas_a_remover]
    
    return df_anon[colunas_a_manter]


def processar_dados_perfil(df_profile: pd.DataFrame) -> pd.DataFrame:
    """Processa e padroniza os dados de perfil profissional.

    Anonimiza e-mails, gera 'person_id', padroniza o nível profissional
    e seleciona colunas relevantes para o perfil.

    Args:
        df_profile (pd.DataFrame): DataFrame contendo os dados brutos de perfil.

    Returns:
        pd.DataFrame: DataFrame processado com nível profissional padronizado.
    """
    logger.info("--- Processando Dados de Perfil ---")
    if df_profile.empty:
        return pd.DataFrame() # Retorna DataFrame vazio se o input for vazio
    
    df_processado = df_profile.copy()
    # Anonimiza o e-mail e gera um 'person_id' único.
    df_processado['email'] = df_processado['email'].str.lower().str.strip()
    df_processado['person_id'] = pd.factorize(df_processado['email'])[0] + 1
    
    # Define as variações de níveis profissionais para padronização.
    level_variacoes = {'Iniciante': ['iniciante'], 'Estagiário': ['estagiário', 'estagiario'], 'Júnior': ['júnior', 'junior'], 'Pleno': ['pleno'], 'Sênior': ['sênior', 'senior'], 'Especialista': ['especialista'], 'Liderança': ['liderança', 'lideranca', 'c-level'], 'Outro': ['outro']}
    df_processado['professional_level_padronizado'] = padronizar_categorias(df_processado['professional_level'], level_variacoes, 'Não informado')
    
    # Define a ordem categórica para o nível profissional padronizado.
    ordem_nivel = ['Iniciante', 'Estagiário', 'Júnior', 'Pleno', 'Sênior', 'Especialista', 'Liderança', 'Outro', 'Não informado']
    df_processado['professional_level_padronizado'] = pd.Categorical(df_processado['professional_level_padronizado'], categories=ordem_nivel, ordered=True)
    
    # Seleciona as colunas profissionais a serem mantidas.
    colunas_profissionais = ['person_id', 'professional_level_padronizado', 'professional_area', 'professional_technologies', 'professional_tools', 'working', 'schooling']
    colunas_a_manter = [col for col in colunas_profissionais if col in df_processado.columns]
    
    return df_processado[colunas_a_manter]


def processar_dados_voluntariado(df_voluntariado: pd.DataFrame) -> pd.DataFrame:
    """Processa e padroniza os dados de voluntariado.

    Anonimiza e-mails, gera 'person_id', adiciona uma flag de voluntário,
    extrai tags de atuação e identifica a atuação principal.

    Args:
        df_voluntariado (pd.DataFrame): DataFrame contendo os dados brutos de voluntariado.

    Returns:
        pd.DataFrame: DataFrame processado com informações de voluntariado.
    """
    logger.info("--- Processando Dados de Voluntariado ---")
    if df_voluntariado.empty:
        return pd.DataFrame() # Retorna DataFrame vazio se o input for vazio
    
    df_processado = df_voluntariado.copy()
    # Anonimiza o e-mail e gera um 'person_id' único.
    df_processado['email'] = df_processado['email'].str.lower().str.strip()
    df_processado['person_id'] = pd.factorize(df_processado['email'])[0] + 1
    
    # Adiciona uma coluna indicando se a pessoa é voluntária.
    df_processado['is_volunteer'] = 'Sim'
    
    # Limpa e divide a coluna 'atuacao' em tags individuais.
    df_processado['atuacao_tags'] = df_processado['atuacao'].str.lower().str.replace(r'\[|\]|"', '', regex=True).str.split(',').apply(lambda x: [tag.strip() for tag in x] if isinstance(x, list) else [])
    
    # Extrai a primeira tag como atuação principal.
    df_processado['atuacao_principal'] = df_processado['atuacao_tags'].apply(lambda x: x[0] if x else 'Não informado')
    
    # Seleciona as colunas relevantes de voluntariado.
    colunas_relevantes = ['person_id', 'is_volunteer', 'atuacao_principal', 'atuacao_tags']
    colunas_a_manter = [col for col in colunas_relevantes if col in df_processado.columns]
    
    return df_processado[colunas_a_manter]


def descobrir_personas_com_clustering(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica o algoritmo K-Means para descobrir personas de usuários.

    Utiliza as features 'faixa_etaria', 'professional_level_padronizado',
    'working' e 'idade' para agrupar os usuários em 'K_IDEAL' clusters.
    Gera relatórios de resumo e detalhes das personas.

    Args:
        df (pd.DataFrame): DataFrame consolidado com dados processados.

    Returns:
        pd.DataFrame: O DataFrame original com uma nova coluna 'persona'
                      atribuindo cada usuário a um cluster.
    """
    logger.info("="*50 + "\n== INICIANDO FASE DE MACHINE LEARNING (FINAL) ==" + "\n" + "="*50)
    
    # Define as features a serem usadas para o clustering.
    features = ['faixa_etaria', 'professional_level_padronizado', 'working', 'idade']
    
    # Cria uma cópia do DataFrame apenas com as linhas que possuem todas as features.
    df_model = df.dropna(subset=features)
    
    # Verifica se há dados suficientes para realizar o clustering.
    if df_model.shape[0] < 10:
        logger.error("Não há dados suficientes para clustering (mínimo de 10 amostras).")
        return df # Retorna o DataFrame original se não houver dados suficientes.
    
    # Define as features categóricas e numéricas para pré-processamento.
    categorical_features = ['faixa_etaria', 'professional_level_padronizado', 'working']
    numerical_features = ['idade']
    
    # Cria um pré-processador usando ColumnTransformer.
    # Numéricas: padronizadas com StandardScaler.
    # Categóricas: transformadas com OneHotEncoder (ignora categorias desconhecidas).
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])
    
    # Define o número ideal de clusters e inicializa o modelo KMeans.
    K_IDEAL = 4
    kmeans_final = KMeans(n_clusters=K_IDEAL, random_state=42, n_init=10) # n_init para maior robustez
    
    # Cria um pipeline para pré-processamento e clustering.
    pipeline_final = Pipeline(steps=[('preprocessor', preprocessor), ('cluster', kmeans_final)])
    
    # Aplica o pipeline aos dados e atribui o cluster (persona) a cada usuário.
    # Os IDs de persona são incrementados em 1 para começar de 1, não de 0.
    df.loc[df_model.index, 'persona'] = pipeline_final.fit_predict(df_model) + 1
    
    logger.info("--- Gerando Resumo das Personas ---")
    
    # Agrupa o DataFrame pelas personas para gerar um resumo estatístico.
    summary = df.groupby('persona').agg(
        regiao_moda=('regiao', lambda x: x.mode().get(0, 'N/A')),
        faixa_etaria_moda=('faixa_etaria', lambda x: x.mode().get(0, 'N/A')),
        nivel_profissional_moda=('professional_level_padronizado', lambda x: x.mode().get(0, 'N/A')),
        acesso_computador_moda=('computador_acesso', lambda x: x.mode().get(0, 'N/A')),
        idade_media=('idade', 'mean'),
        n_de_pessoas=('persona', 'size')
    ).reset_index()
    
    # Formata as colunas 'persona' e 'idade_media'.
    summary['persona'] = summary['persona'].astype(int)
    summary['idade_media'] = summary['idade_media'].round(1)
    
    # Salva o resumo das personas em um arquivo CSV.
    summary.to_csv(PERSONA_SUMMARY_PATH, index=False)
    logger.info(f"Resumo principal das personas salvo em {PERSONA_SUMMARY_PATH}")
    
    # Gera detalhes mais aprofundados para cada persona.
    details_list = []
    for persona_id in sorted(df['persona'].dropna().unique()):
        df_persona = df[df['persona'] == persona_id]
        
        # Processa e conta as tecnologias mais citadas por cada persona.
        tech_tags = df_persona['professional_technologies'].dropna().str.lower().str.replace(r'\[|\]|"', '', regex=True).str.split(',').explode()
        top_3_tech = tech_tags.str.strip().value_counts(normalize=True).nlargest(3) * 100
        
        # Constrói o dicionário de detalhes para a persona atual.
        details = {
            'persona': int(persona_id),
            'top_schooling': [f"{idx}: {val:.1f}%" for idx, val in (df_persona['schooling'].value_counts(normalize=True).nlargest(3) * 100).items()],
            'top_technologies': [f"{idx}: {val:.1f}%" for idx, val in top_3_tech.items()],
            'level_distribution': [f"{idx}: {val:.1f}%" for idx, val in (df_persona['professional_level_padronizado'].value_counts(normalize=True) * 100).items()]
        }
        details_list.append(details)
    
    # Converte a lista de detalhes em um DataFrame e salva em CSV.
    df_details = pd.DataFrame(details_list)
    df_details.to_csv(PERSONA_DETAILS_PATH, index=False)
    logger.info(f"Detalhes das personas salvos em {PERSONA_DETAILS_PATH}")
    
    return df


def gerar_analise_de_crescimento(df_inscricoes: pd.DataFrame):
    """Gera uma análise mensal do crescimento da comunidade.

    Calcula o número de novas pessoas que se inscreveram a cada mês
    e o total acumulado de pessoas na comunidade.

    Args:
        df_inscricoes (pd.DataFrame): DataFrame contendo os dados brutos de inscrições.
    """
    logger.info("--- Gerando Análise de Crescimento da Comunidade ---")
    
    # Verifica se o DataFrame de inscrições não está vazio e se possui a coluna 'data'.
    if df_inscricoes.empty or 'data' not in df_inscricoes.columns:
        logger.warning("DataFrame de inscrições vazio ou sem coluna 'data'. Análise de crescimento pulada.")
        return
    
    df_growth = df_inscricoes[['email', 'data']].copy()
    
    # Anonimiza o e-mail e gera um 'person_id' único.
    df_growth['email'] = df_growth['email'].str.lower().str.strip()
    df_growth['person_id'] = pd.factorize(df_growth['email'])[0] + 1
    
    # Converte a coluna 'data' para formato datetime e remove linhas com datas inválidas.
    df_growth['data_inscricao'] = pd.to_datetime(df_growth['data'], errors='coerce')
    df_growth = df_growth.dropna(subset=['data_inscricao'])
    
    # Identifica a primeira inscrição para cada 'person_id' (para contar novas pessoas).
    primeira_inscricao = df_growth.loc[df_growth.groupby('person_id')['data_inscricao'].idxmin()]
    primeira_inscricao['periodo'] = primeira_inscricao['data_inscricao'].dt.to_period('M')
    
    # Conta o número de novas pessoas por mês.
    novas_pessoas_por_mes = primeira_inscricao.groupby('periodo').size().reset_index(name='novas_pessoas')
    novas_pessoas_por_mes['periodo'] = novas_pessoas_por_mes['periodo'].astype(str)
    
    # Calcula o total acumulado de pessoas ao longo do tempo.
    novas_pessoas_por_mes['total_acumulado'] = novas_pessoas_por_mes['novas_pessoas'].cumsum()
    
    # Salva o relatório de crescimento em um arquivo CSV.
    novas_pessoas_por_mes.to_csv(CRESCIMENTO_PATH, index=False)
    logger.info(f"Análise de crescimento salva em: {CRESCIMENTO_PATH}")


def main():
    """Função principal que orquestra todo o pipeline de análise de dados.

    Carrega os dados brutos, os processa e padroniza, mescla os DataFrames,
    aplica clustering para descobrir personas, gera relatórios de crescimento
    e de distribuição geográfica, e salva o DataFrame final processado.
    """
    logger.info("="*50 + "\n==  INICIANDO PIPELINE DE DADOS COMPLETO (FINAL)  ==" + "\n" + "="*50)
    
    # Carrega os dados brutos de inscrições, perfil, voluntariado, cidades e coordenadas de estados.
    df_inscricoes_raw = carregar_dados(RAW_INSCRICOES_PATH)
    df_profile_raw = carregar_dados(RAW_PROFILE_PATH)
    df_voluntariado_raw = carregar_dados(RAW_VOLUNTARIADO_PATH)
    df_cidades = carregar_dados(CIDADES_PATH) # Embora carregado, df_cidades não é usado neste script. Pode ser removido se não for necessário.
    df_states_coords = carregar_dados(STATES_COORDS_PATH)
    
    # Interrompe o pipeline se o arquivo de inscrições principal não for encontrado.
    if df_inscricoes_raw.empty:
        logger.error("Arquivo de inscrições não encontrado. Pipeline interrompido.")
        return
    
    # Gera a análise de crescimento da comunidade antes de outros processamentos.
    gerar_analise_de_crescimento(df_inscricoes_raw)
    
    # Processa individualmente cada conjunto de dados.
    df_demografico = processar_dados_inscricoes(df_inscricoes_raw)
    df_profissional = processar_dados_perfil(df_profile_raw)
    df_voluntario = processar_dados_voluntariado(df_voluntariado_raw)
    
    logger.info("Iniciando merges...")
    
    # Realiza os merges dos DataFrames processados utilizando 'person_id'.
    # O merge com df_profissional e df_voluntario é um 'left merge' para manter
    # todos os inscritos e adicionar informações de perfil/voluntariado onde disponíveis.
    df_consolidado = pd.merge(df_demografico, df_profissional, on='person_id', how='left')
    df_final = pd.merge(df_consolidado, df_voluntario, on='person_id', how='left')
    
    # Preenche valores NaN na coluna 'is_volunteer' com 'Não'.
    df_final['is_volunteer'] = df_final['is_volunteer'].fillna('Não')
    
    # Adiciona a identificação de alunos.
    # Se a coluna 'turma_slug' existe, identifica quem está matriculado.
    # Caso contrário, categoriza todos como 'Em espera'.
    if 'turma_slug' in df_final.columns:
        alunos_ids = df_final[df_final['turma_slug'].notna()]['person_id'].unique()
        df_final['perfil_aluno'] = np.where(df_final['person_id'].isin(alunos_ids), 'Matriculado', 'Em espera')
    else:
        df_final['perfil_aluno'] = 'Em espera'
        
    logger.info(f"Merges concluídos. Shape final: {df_final.shape}")
    
    # Se a coluna 'atuacao_tags' existe (vindo do voluntariado),
    # calcula a contagem de tags de atuação para voluntários.
    if 'atuacao_tags' in df_final.columns:
        atuacao_counts = df_final[df_final['is_volunteer'] == 'Sim']['atuacao_tags'].explode().value_counts().reset_index()
        atuacao_counts.columns = ['atuacao', 'count']
        atuacao_counts.to_csv(ATUACAO_COUNT_PATH, index=False)
        logger.info(f"Contagem de tags de atuação salva em {ATUACAO_COUNT_PATH}")
    
    # Descobre e atribui personas aos usuários.
    df_final = descobrir_personas_com_clustering(df_final)

    # Se a coluna 'estado_padronizado' existe e os dados de coordenadas de estados foram carregados,
    # gera um resumo para visualização em mapa.
    if 'estado_padronizado' in df_final.columns and df_states_coords is not None:
        logger.info("Gerando resumo para o mapa de estados...")
        # Agrupa por estado padronizado e conta o número de pessoas.
        map_summary = df_final[df_final['estado_padronizado'] != 'Inválido'].groupby('estado_padronizado').agg(n_de_pessoas=('person_id', 'count')).reset_index()
        # Mescla com as coordenadas dos estados.
        map_summary_final = pd.merge(map_summary, df_states_coords, left_on='estado_padronizado', right_on='uf', how='left')
        # Calcula uma métrica de tamanho (raiz quadrada do número de pessoas) para o mapa.
        map_summary_final['size_sqrt'] = np.sqrt(map_summary_final['n_de_pessoas'])
        map_summary_final.to_csv(MAP_SUMMARY_PATH, index=False)
        logger.info(f"Resumo do mapa (com coordenadas) salvo em: {MAP_SUMMARY_PATH}")
    
    # Salva o DataFrame final, consolidado e enriquecido, em um arquivo CSV.
    df_final.to_csv(PROCESSED_FINAL_PATH, index=False)
    logger.info(f"Dados consolidados e enriquecidos (com personas) salvos em: {PROCESSED_FINAL_PATH}")
    logger.info("Pipeline completo finalizado com sucesso.")


if __name__ == "__main__":
    # Garante que a função main() seja executada apenas quando o script é rodado diretamente.
    main()