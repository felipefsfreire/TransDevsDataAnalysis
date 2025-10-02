# Documentação de Dados - TransDevs

**Autor:** Felipe Freire
**Data de Criação:** 02/10/2025
**Última Atualização:** 02/10/2025

## 1. Introdução

Este documento serve como um Dicionário de Dados centralizado para as principais tabelas do projeto de análise da TransDevs. O objetivo é descrever cada coluna, seu tipo de dado esperado e sua finalidade de negócio, garantindo a consistência e o entendimento para futuras análises e integrações de dados.

---

## 2. Tabela de Inscrições (`20250916-div_inscricoes.csv`)

Esta tabela contém o registro de cada inscrição realizada para os diversos cursos e eventos oferecidos pela TransDevs. É a principal fonte de dados demográficos e de interesse da comunidade.

| Coluna | Tipo de Dado | Descrição |
| :--- | :--- | :--- |
| `id` | Integer (Chave Primária) | Identificador numérico único para cada registro de inscrição nesta tabela. |
| `nome_completo` | String (PII) | Nome completo da pessoa. **Dado sensível, removido após anonimização.** |
| `nascdt` | String (Data) | Data de nascimento da pessoa. O formato é inconsistente (ex: `DD/MM/AAAA` ou `AAAA-MM-DD`). |
| `email` | String (PII / Chave de Junção) | Endereço de e-mail da pessoa. **Dado sensível usado como chave para criar o `person_id` anônimo.** |
| `telefone` | String (PII) | Número de telefone da pessoa. **Dado sensível, removido após anonimização.** |
| `cidade` | String | Cidade de residência declarada pela pessoa. |
| `estado` | String | Estado de residência declarado pela pessoa. Pode conter siglas e nomes completos. |
| `sabendo` | String (Categórico) | Como a pessoa ficou sabendo sobre o curso/evento (ex: "Instagram", "Amigos"). |
| `conhecimento` | String (Texto Livre) | Descrição do conhecimento prévio da pessoa sobre o tema do curso. |
| `computador` | Integer (Binário) | Indica se a pessoa possui computador (`1` para Sim, `0` para Não). |
| `pcd` | String (Texto Livre) | Campo para a pessoa indicar se é uma Pessoa com Deficiência e descrever necessidades. |
| `data` | Datetime (Formato String) | Data e hora em que o registro de inscrição foi criado no sistema. **Usado para análise de crescimento.** |
| `turma` | String (Categórico) | Nome da turma para a qual a pessoa foi alocada (ex: "Turma 5", "T1 Div - Manu e Sophia"). |
| `turma_slug` | String | Identificador único (slug) para a turma, usado internamente. |
| `notas` | String (Texto Livre) | Campo para anotações internas sobre a pessoa inscrita. |
| `data_form_selecao` | Datetime (Formato String) | Data e hora do preenchimento de um formulário secundário de seleção. |
| `s_conhecimento`| String (Categórico) | **(Legado/Survey)** Nível de conhecimento prévio declarado em um formulário (ex: "nao_sei_nada"). |
| `s_escolaridade`| String (Categórico) | **(Legado/Survey)** Nível de escolaridade declarado (ex: "ensino_superior_completo"). |
| `s_trabalhando` | String (Categórico) | **(Legado/Survey)** Situação de trabalho declarada (ex: "desempregade", "tenho_emprego"). |
| `nome_primeiro` | String (PII) | Primeiro nome da pessoa. **Dado sensível, removido após anonimização.** |
| `nome_ultimo` | String (PII) | Último nome/sobrenome da pessoa. **Dado sensível, removido após anonimização.** |
| `curso_titulo` | String (Categórico) | Título do curso ou evento para o qual a inscrição foi feita (ex: "Curso TransDevs", "Curso Python"). |
| `curso_slug` | String | Identificador único (slug) para o curso, usado internamente. |
| `genero` | String (Categórico/JSON) | Identidade de gênero declarada. Pode conter múltiplos valores. |
| `etnia` | String (Categórico/JSON) | Etnia declarada pela pessoa. Pode conter múltiplos valores. |
| `pronome` | String (Categórico/JSON) | Pronomes de tratamento. Pode conter múltiplos valores. |
| `logica_simples` | String (Categórico) | Resultado de um possível teste de lógica simples (ex: "logica_s_joao"). |
| `s_link` | String (URL) | **(Legado/Survey)** Link para um perfil profissional (LinkedIn, GitHub) fornecido em um formulário. |
| `s_atuacao` | String (Categórico) | **(Legado/Survey)** Área de atuação profissional desejada ou atual. |
| `s_nivel_exp` | String (Categórico) | **(Legado/Survey)** Nível de experiência profissional declarado. |
| `s_tecnologias` | String (Tags) | **(Legado/Survey)** Lista de tecnologias de interesse ou conhecimento, separadas por vírgula. |
| `s_ferramentas` | String (Tags) | **(Legado/Survey)** Lista de ferramentas de interesse ou conhecimento, separadas por vírgula. |

---

## 3. Tabela de Voluntariado (`20250916-div_voluntariado.csv`)

A tabela de voluntariado contém informações sobre as pessoas que se inscreveram ou estão atuando como voluntárias na comunidade.

| Coluna | Tipo de Dado | Descrição |
| :--- | :--- | :--- |
| `id` | Integer (Chave Primária) | Identificador numérico único para cada registro de inscrição de voluntariado nesta tabela específica. |
| `nome_completo` | String (PII) | Nome completo da pessoa. **Dado sensível, removido após anonimização.** |
| `nome_display` | String | Nome preferido pela pessoa para exibição pública ou interna na comunidade. Pode estar nulo. |
| `cargo_titulo` | String (Categórico) | Título ou cargo que a pessoa ocupa dentro da estrutura de voluntariado (ex: "Coordenação", "Designer"). |
| `link` | String (URL) | Link para um perfil profissional ou de contato da pessoa (ex: LinkedIn, Instagram, WhatsApp). |
| `crp` | String | Número do registro no Conselho Regional de Psicologia. Específico para voluntariado na área de psicologia. |
| `status` | String (Categórico) | Status atual da pessoa no voluntariado (ex: "atuando", "inscricao", "inativo", "contactado"). |
| `pronomes`| String (Pode conter JSON) | Pronomes de tratamento da pessoa. Pode ser um valor único ou uma lista de valores em formato de string. |
| `email` | String (PII / Chave de Junção) | Endereço de e-mail da pessoa. **Dado sensível usado como chave para criar o `person_id` anônimo.** |
| `telefone` | String (PII) | Número de telefone da pessoa. **Dado sensível, removido após anonimização.** |
| `cidade` | String | Cidade de residência declarada pela pessoa. |
| `estado` | String | Estado de residência declarado pela pessoa. |
| `necessidades` | String | Campo para descrever necessidades especiais ou de acessibilidade. |
| `disponibilidade` | String (Pode conter JSON) | Descreve os horários em que a pessoa está disponível. Pode ser texto livre ou uma estrutura JSON. |
| `crm` | String | Número do registro no Conselho Regional de Medicina. Específico para voluntariado na área de medicina. |
| `genero` | String (Pode conter JSON) | Identidade de gênero declarada pela pessoa. Pode ser um valor único ou uma lista de valores. |
| `atuacao` | String (Pode conter JSON) | Lista das áreas de atuação de interesse da pessoa no voluntariado (ex: "tecnologia", "comunicacao"). |
| `atuacao_sobre`| String (Texto Livre) | Um campo de texto aberto onde a pessoa pode descrever com mais detalhes suas atividades ou interesses. |
| `foto_url` | String (URL) | Link para a foto de perfil da pessoa, geralmente usada no site da comunidade. |
| `created_at` | Datetime (Formato String) | Data e hora em que o registro de inscrição foi criado no sistema. |
| `updated_at` | Datetime (Formato String) | Data e hora da última atualização do registro no sistema. |

## 4. Considerações Gerais

*   **PII (Informações de Identificação Pessoal):** Colunas como `nome_completo`, `email` e `telefone` são dados sensíveis. O pipeline de análise deve garantir a remoção dessas colunas após a criação de um identificador anônimo (`person_id`).
*   **Campos de Múltiplos Valores:** Colunas como `pronomes`, `genero` e `atuacao` frequentemente contêm listas de valores armazenadas como uma string (ex: `["tecnologia", "comunicacao"]`). Elas exigem um tratamento especial (parsing) para serem analisadas corretamente, como a contagem individual de cada "tag".
*   **Colunas Legado (prefixo `s_`):** As colunas na tabela de inscrições com prefixo `s_` (ex: `s_conhecimento`, `s_tecnologias`) parecem originar-se de formulários de pesquisa ou sistemas mais antigos. Elas são fontes ricas de dados de perfil profissional e devem ser usadas em conjunto com os dados da tabela de perfis.