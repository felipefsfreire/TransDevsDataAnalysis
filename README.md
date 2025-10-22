# TransDevs Data Analysis & Dashboard

## 1. Sobre o Projeto

Este projeto consiste em um pipeline completo de análise de dados e um dashboard interativo desenvolvido para a comunidade **TransDevs**. O objetivo principal é transformar dados brutos de inscrições, perfis e voluntariado em insights estratégicos e visualmente impactantes.

A solução foi construída do zero, seguindo as melhores práticas de ciência de dados e engenharia de software, incluindo:

- **ETL Robusto:** Um pipeline para extração, transformação e limpeza de múltiplos arquivos de dados.
- **Análise de Dados:** Geração de insights através de análises descritivas, cruzadas e de crescimento.
- **Machine Learning:** Aplicação de algoritmos de clustering (K-Means) para descobrir "personas" de usuários de forma automática.
- **Data Storytelling & UX:** Um dashboard interativo e seguro, projetado com foco na experiência do usuário e na clareza da comunicação, utilizando a identidade visual da organização.

Este `README.md` serve como um guia central para a configuração, execução e entendimento do projeto.

## 2. Funcionalidades do Dashboard

O dashboard interativo, construído com Streamlit, é o principal produto deste projeto e está organizado nas seguintes seções:

- **Visão Geral:** Apresenta os KPIs mais importantes (Pessoas Únicas, Estados Alcançados, Taxa de Empregabilidade) e um mapa de bolhas interativo mostrando a concentração da comunidade no Brasil.
- **Crescimento & Cursos:** Exibe a evolução do número de membros ao longo do tempo e analisa a popularidade e o alcance dos cursos oferecidos.
- **Perfil Demográfico:** Detalha as características da comunidade, como faixa etária, etnia, gênero e acesso a computador.
- **Perfil Profissional:** Mostra a distribuição de senioridade e experiência profissional dos membros.
- **Análises Cruzadas:** Aprofunda os insights ao cruzar variáveis, como nível profissional por região/gênero e situação de trabalho por etnia/faixa etária.
- **Personas da Comunidade:** Apresenta os 4 principais perfis de usuários identificados pelo modelo de Machine Learning, com descrições narrativas e detalhes técnicos interativos.
- **Análise de Voluntariado:** Foca no perfil das pessoas interessadas em voluntariar, analisando suas áreas de atuação, senioridade e distribuição entre as personas.
- **Planejamento Estratégico:** Uma ferramenta interativa para a diretoria, permitindo filtrar recortes de diversidade e identificar talentos para iniciativas de mentoria.
- **Segurança:** Acesso ao dashboard protegido por senha para garantir a privacidade dos dados.

## 3. Estrutura do Projeto

```text
/TransDevsDataAnalysis/
├── .streamlit/
│   └── secrets.toml        # Arquivo para armazenar a senha do dashboard (NÃO ENVIAR PARA O GITHUB)
├── data/
│   ├── raw/                # Onde os arquivos de dados brutos (.csv, .geojson) devem ser colocados
│   └── processed/          # Onde os dados limpos e consolidados são salvos pelo pipeline
├── notebooks/
│   └── data_discovery.ipynb # Notebook para exploração e análise preliminar dos dados
├── reports/
│   └── (arquivos .csv e .png gerados pelo pipeline)
├── src/
│   ├── analysis.py         # O motor do projeto: pipeline de ETL e Machine Learning
│   └── dashboard.py        # A interface do usuário: o código do dashboard Streamlit
├── .gitignore              # Arquivo para ignorar arquivos sensíveis (como secrets.toml)
├── requirements.txt        # Lista de todas as bibliotecas Python necessárias
└── README.md               # Este arquivo
```

## 4. Tecnologias Utilizadas

- **Linguagem:** Python 3.11+
- **Análise e Manipulação de Dados:** Pandas, NumPy
- **Machine Learning:** Scikit-learn
- **Visualização de Dados:** Matplotlib, Seaborn, Plotly Express
- **Dashboard Interativo:** Streamlit
- **Geoprocessamento:** Pydeck, GeoJSON

## 5. Configuração do Ambiente (Setup)

Siga estes passos para configurar e executar o projeto em uma nova máquina.

**Passo 1: Clonar o Repositório**

```bash
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
cd TransDevsDataAnalysis
```

**Passo 2: Criar e Ativar um Ambiente Virtual**
É uma forte recomendação usar um ambiente virtual para isolar as dependências do projeto.

```bash
# Criar o ambiente
python -m venv venv

# Ativar no Windows
.\venv\Scripts\activate

# Ativar no macOS/Linux
source venv/bin/activate
```

**Passo 3: Instalar as Dependências**
Com o ambiente virtual ativado, instale todas as bibliotecas necessárias.

```bash
pip install -r requirements.txt
```

**Passo 4: Adicionar os Arquivos de Dados**
Certifique-se de que os arquivos de dados brutos estejam na pasta `data/raw/`.

**Passo 5: Configurar a Senha de Acesso**

1. Crie uma pasta chamada `.streamlit` na raiz do projeto.
2. Dentro de `.streamlit`, crie um arquivo chamado `secrets.toml`.
3. Adicione o seguinte conteúdo ao arquivo, substituindo pela senha desejada:

   ```toml
   APP_PASSWORD = "SUA_SENHA_FORTE_AQUI"
   ```

4. **IMPORTANTE:** Certifique-se de que o arquivo `.gitignore` na raiz do projeto contém a linha `.streamlit/secrets.toml` para evitar que sua senha seja enviada para o GitHub.

## 6. Como Executar o Projeto

A execução do projeto é feita em duas etapas.

**Etapa 1: Executar o Pipeline de Análise**
Este script processará todos os dados brutos, executará o modelo de Machine Learning e gerará os arquivos limpos que o dashboard utiliza. Execute este comando no terminal a partir da pasta raiz do projeto.

```bash
python src/analysis.py
```

Você deve executar este script sempre que os dados brutos forem atualizados.

**Etapa 2: Iniciar o Dashboard**
Após o pipeline de análise ser concluído com sucesso, inicie a aplicação web interativa.

```bash
streamlit run src/dashboard.py
```

Seu navegador abrirá automaticamente o dashboard. A primeira tela pedirá a senha que você configurou no `secrets.toml`.

## 7. Próximos Passos (Melhorias Futuras)

Este projeto estabelece uma base sólida. As próximas evoluções podem incluir:

- **Conexão com Banco de Dados:** Substituir a leitura de arquivos CSV por uma conexão direta a um banco de dados (ex: PostgreSQL com SQLAlchemy) para automatizar a atualização dos dados.
- **Orquestração de Pipeline:** Utilizar uma ferramenta como Apache Airflow ou Prefect para agendar e monitorar a execução do `analysis.py` de forma automática (ex: diariamente).
- **Dados de Engajamento:** Integrar novas fontes de dados, como a atividade de alunos em plataformas de curso, para responder a perguntas sobre "usuários ativos".

## 8. Autores e Agradecimentos

- **Desenvolvedor:** Felipe Freire

Um agradecimento especial à comunidade **TransDevs** por fornecer os dados e a inspiração para este projeto.
