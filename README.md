# Sistema de Apoio ao Plano de Desenvolvimento Individual (PDI) com Inteligência Artificial

Plataforma corporativa *full-stack* para gestão de desempenho por competências, apuração matemática calibrada de *gaps* e geração automatizada de **Planos de Desenvolvimento Individual (PDI)** estruturados na metodologia **70-20-10** com apoio de Inteligência Artificial Generativa (**Google Gemini**).

---

## Sumário

1. [Visão Geral e Motivação](#1-visão-geral-e-motivação)
2. [Metodologia e Regras de Negócio](#2-metodologia-e-regras-de-negócio)
3. [Perfis de Acesso e Isolamento Multiempresa](#3-perfis-de-acesso-e-isolamento-multiempresa)
4. [Arquitetura e Tecnologias](#4-arquitetura-e-tecnologias)
5. [Estrutura de Diretórios](#5-estrutura-de-diretórios)
6. [Como Executar o Projeto](#6-como-executar-o-projeto)
7. [Principais Rotas da API](#7-principais-rotas-da-api)

---

## 1. Visão Geral e Motivação

Processos tradicionais de avaliação de desempenho frequentemente sofrem com subjetividade, desalinhamento entre a percepção do colaborador e a do gestor, e dificuldade em transformar o resultado das avaliações em planos de ação práticos.

Este sistema resolve esse problema integrando todo o ciclo de desenvolvimento humano e organizacional:

1. **Mapeamento da Matriz de Cargos e Competências**: definição clara do nível de proficiência esperado (escala de `1` a `5`) em cada competência por cargo.
2. **Sistematização de Questionários Observáveis (IA)**: elaboração automática de critérios comportamentais e técnicos observáveis via Google Gemini para o ciclo de avaliação (`SELF` + `MANAGER`), com disparo de notificações por e-mail.
3. **Cálculo Calibrado de *Gaps* e Recomendação de Mentores**: ponderação matemática entre a avaliação do gestor e a autoavaliação, identificando déficits reais e localizando mentores internos qualificados na mesma empresa.
4. **Geração do PDI no Modelo 70-20-10 (IA)**: criação personalizada de ações práticas (*70%*), mentoria/troca (*20%*) e capacitação formal (*10%*) diretamente baseadas nas evidências registradas pelos avaliadores.

---

## 2. Metodologia e Regras de Negócio

### 2.1. Ciclo Completo de Avaliação (`SELF` + `MANAGER`)
Para garantir imparcialidade e consistência no cálculo de *gaps*, cada ciclo de avaliação (ex: `2026.2`) de um colaborador é composto obrigatoriamente por duas pontas que compartilham o mesmo questionário:
- **Autoavaliação (`SELF`)**: respondida pelo próprio colaborador avaliado.
- **Avaliação do Gestor (`MANAGER`)**: respondida exclusivamente pelo gestor direto vinculado ao cadastro do colaborador.

> **Trava de Integridade do Ciclo**: Uma vez que o ciclo recebe respostas ou tem seu PDI gerado, o questionário é automaticamente congelado, impedindo a inclusão de novas questões que distorceriam a apuração.

### 2.2. Cálculo Calibrado de *Gaps*
Para cada competência exigida pelo cargo alvo, o backend consolida as médias das respostas em escala de `1` a `5` aplicando peso de **70% para a visão do Gestor** e **30% para a Autoavaliação**:

$$\text{Nota Calibrada} = (0{,}7 \times \text{Média}_{\text{Gestor}}) + (0{,}3 \times \text{Média}_{\text{Autoavaliação}})$$

$$\text{Gap} = \text{Nota Calibrada} - \text{Nível Esperado do Cargo}$$

- Quando $\text{Gap} < 0$, caracteriza-se um **déficit de competência** que passa a integrar o Plano de Desenvolvimento Individual (PDI).

### 2.3. Identificação Automática de Mentores Internos
Para cada competência com *gap* negativo, o motor de calibragem consulta o banco de dados em busca de até **2 colaboradores da mesma empresa** que possuam **Nota Calibrada $\ge 4{,}0$** naquela competência, sugerindo-os nominalmente à IA para compor a etapa de **20% (Mentoria/Troca)** do PDI.

### 2.4. Estruturação do PDI 70-20-10 e Conclusão Automática
O plano de ação gerado para cada competência é decomposto em:
- **70% (Prática no Trabalho / *On-the-Job*)**: atividades práticas baseadas nas observações reais dos avaliadores.
- **20% (Mentoria e Troca de Experiências)**: pareamento com os mentores internos identificados na empresa ou comunidades técnicas.
- **10% (Educação Formal)**: cursos, leituras técnicas e documentações oficiais.

Conforme as ações (`development_plan`) são marcadas como concluídas (`COMPLETE`), o próprio backend verifica o conjunto de ações e atualiza automaticamente o status do PDI principal (`development`) de `IN_PROGRESS` para `COMPLETE`.

---

## 3. Perfis de Acesso e Isolamento Multiempresa

O sistema implementa autenticação via **JWT (Bearer Token)**, controle de acesso baseado em papéis (**RBAC**) e **isolamento multiempresa (*Multi-tenant*)** via `enterprise_id` em todas as rotas:

| Perfil | Permissões Principais |
| :--- | :--- |
| **Recursos Humanos** | Gestão do quadro de colaboradores, matriz de cargos/competências, abertura de ciclos, geração de perguntas via IA, vínculo manual de questões ao ciclo e processamento do PDI 70-20-10. |
| **Gestor** | Consulta da equipe direta (liderados), abertura de ciclos para seus liderados, preenchimento das avaliações `MANAGER` e acompanhamento/atualização de ações de PDI da equipe. |
| **Colaborador** | Consulta da própria ficha funcional e matriz do cargo atual, preenchimento da autoavaliação (`SELF`), visualização de respostas e atualização de status das ações do seu PDI. |

---

## 4. Arquitetura e Tecnologias

### Backend (`pdi-backend`)
- **Linguagem & Framework**: Python 3.11+ com **FastAPI**
- **ORM & Banco de Dados**: **SQLAlchemy 2.0** + **PostgreSQL** (`psycopg2`)
- **Validação & Serialização**: **Pydantic v2**
- **Segurança & Autenticação**: JWT (`python-jose`) e hash de senhas com `bcrypt`
- **Inteligência Artificial**: SDK oficial **Google GenAI** (`google-genai`) utilizando a família **Gemini Flash / Flash-Lite** com *Structured Outputs* (`application/json`)
- **Notificações Assíncronas**: Envio de e-mails transacionais em segundo plano com `BackgroundTasks` e `smtplib`

### Frontend (`pdi-frontend`)
- **Framework**: **Angular 19** (arquitetura modular com *Standalone Components*, templates HTML e estilos SCSS separados)
- **Gerenciamento de Estado**: **Angular Signals** (`signal`, `computed`)
- **Comunicação HTTP Padronizada**: `ApiClientService` baseado em Promises (`firstValueFrom` + `async/await`), `authInterceptor` (injeção automática do token JWT) e `errorInterceptor` (captura global de erros da API e exibição padronizada em *Toast* flutuante)

---

## 5. Estrutura de Diretórios

```text
system-idp/
├── pdi-backend/                  # API RESTful em FastAPI
│   ├── app/
│   │   ├── config/               # Conexão com banco (SQLAlchemy) e segurança JWT
│   │   ├── models/               # Entidades do banco (auth, competence, evaluation, development)
│   │   ├── schemas/              # Schemas Pydantic de entrada e saída
│   │   ├── routers/              # Rotas organizadas por domínio de negócio
│   │   ├── services/             # Motor de cálculo de gaps, integração Gemini AI e e-mail
│   │   ├── utils/                # Utilitários de paginação padronizada
│   │   └── main.py               # Ponto de entrada da aplicação FastAPI e CORS
│   └── tests/                    # Testes automatizados de schemas e isolamento de empresa
│
└── pdi-frontend/                 # Aplicação Web em Angular 19
    └── src/app/
        ├── core/
        │   ├── config/           # Configurações de URL base da API
        │   ├── guards/           # Guards de rota (authGuard, guestGuard, roleGuard)
        │   ├── interceptors/     # Interceptors de JWT e tratamento padronizado de erros
        │   ├── models/           # Interfaces TypeScript espelhando os domínios do backend
        │   └── services/         # Serviços de domínio e cliente HTTP centralizado
        ├── shared/components/    # Componentes globais (Toast / FeedbackBanner)
        ├── layout/shell/         # Estrutura principal com menu lateral e barra superior
        └── features/             # Telas do sistema (login, dashboard, profile, user, competence, evaluation, development)
```

---

## 6. Como Executar o Projeto

### Pré-requisitos
- **Python 3.11+**
- **Node.js 20+** e **npm**
- **PostgreSQL** em execução
- Chave de API do **Google AI Studio (Gemini)**

### 6.1. Configurando e Rodando o Backend (`pdi-backend`)

1. Acesse a pasta do backend e crie/ative o ambiente virtual:
   ```powershell
   cd pdi-backend
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. Instale as dependências:
   ```powershell
   pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic[email] python-dotenv python-jose[cryptography] bcrypt google-genai
   ```

3. Crie um arquivo `.env` na raiz de `pdi-backend/` com as seguintes variáveis:
   ```env
   DATABASE_URL=postgresql://usuario:senha@localhost:5432/nome_do_banco
   SECRET_KEY=sua_chave_secreta_jwt
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   GEMINI_API_KEY=sua_chave_do_google_gemini

   # Configurações opcionais de SMTP para disparo de e-mails do ciclo
   MAIL_HOST=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USERNAME=seu_email@dominio.com
   MAIL_PASSWORD=sua_senha_de_app
   MAIL_FROM=seu_email@dominio.com
   ```

4. Inicie o servidor FastAPI:
   ```powershell
   uvicorn app.main:app --reload
   ```
   - A API estará disponível em `http://127.0.0.1:8000`
   - Documentação interativa (Swagger UI): `http://127.0.0.1:8000/docs`

### 6.2. Configurando e Rodando o Frontend (`pdi-frontend`)

1. Em outro terminal, acesse a pasta do frontend e instale os pacotes:
   ```powershell
   cd pdi-frontend
   npm install
   ```

2. Inicie o servidor de desenvolvimento do Angular:
   ```powershell
   npm start
   ```
   - Acesse a aplicação no navegador em: `http://127.0.0.1:4200`

---

## 7. Principais Rotas da API

| Módulo | Método e Rota | Descrição |
| :--- | :--- | :--- |
| **Autenticação** | `POST /auth/login` | Autentica usuário por e-mail ou matrícula (NP) e retorna token JWT |
| **Autenticação** | `POST /auth/register` | Cadastra novo colaborador na empresa (exclusivo RH) |
| **Colaboradores** | `GET /users/list` | Lista colaboradores da empresa autenticada com paginação |
| **Colaboradores** | `GET /users/{user_id}` | Consulta ficha detalhada de um colaborador |
| **Matriz de Cargos** | `POST /position/create` / `GET /position/list` | Cadastro e listagem de cargos da empresa |
| **Competências** | `POST /competences/create` / `GET /competences/list` | Catálogo de competências técnicas e comportamentais |
| **Matriz Cargo × Comp.** | `POST /position_competence/create` | Define o nível esperado (`1` a `5`) de uma competência para um cargo |
| **Avaliações** | `POST /evaluation/create` | Abre ciclo de avaliação (`SELF` ou `MANAGER`) |
| **Avaliações (IA)** | `POST /evaluation/{id}/generate-questions` | Gera questões observáveis via IA e vincula ao par `SELF` + `MANAGER` |
| **Questões do Ciclo** | `POST /evaluation_question/create` | Vincula questão existente ao ciclo completo (`SELF` + `MANAGER`) |
| **Respostas** | `POST /evaluation_answer/create` | Registra notas (`1` a `5`) e justificativas técnicas da avaliação |
| **PDI 70-20-10 (IA)** | `POST /development/generate-from-evaluation/{id}` | Calcula *gaps* calibrados, busca mentores e gera o PDI via IA |
| **Ações do PDI** | `PATCH /development_plan/{plan_id}/status` | Atualiza status da ação (`PENDING`/`COMPLETE`) e recalcula status do PDI |
