# Sistema Meu Emprego
Python + Tkinter + MongoDB/CSV + Matplotlib
## 📌 Visão Geral

Meu Emprego é um sistema desktop para controle de candidaturas, desenvolvido para fins acadêmicos utilizando Python, Tkinter, MongoDB Atlas e gráficos em Matplotlib.
O objetivo é registrar candidaturas, visualizar todas as vagas aplicadas, gerar gráficos analíticos e fornecer um dashboard completo para acompanhamento da jornada de busca por emprego.

O projeto cumpre todos os requisitos acadêmicos, incluindo:

✔ Interface gráfica com múltiplas janelas
✔ Formulário com mais de 5 campos
✔ Uso de diversos widgets Tkinter
✔ Persistência com CSV ou MongoDB
✔ Tela de análise com gráficos (Matplotlib)
✔ Três telas integradas (Dashboard, Cadastro, Visualização)
✔ Código modular e organizado por camadas

## Arquitetura do Sistema

A aplicação é dividida em módulos bem definidos, garantindo organização e facilidade de manutenção:

```
├── 📁 assets
│   ├── 📝 GRAPH_GUIDE.md
│   ├── 📕 Relatorio_MeuEmprego_ABNT.pdf
│   ├── 🐍 __init__.py
│   └── 📄 candidaturas.csv
├── 📁 core
│   ├── 🐍 __init__.py
│   └── 🐍 datastore.py
├── 📁 graphics
│   ├── 🐍 __init__.py
│   ├── 🐍 dashboard_graphs.py
│   └── 🐍 helpers.py
├── 📁 ui
│   ├── 📁 spa
│   │   ├── 🐍 spa_cadastro.py
│   │   ├── 🐍 spa_dashboard.py
│   │   └── 🐍 spa_visualizacao.py
│   ├── 🐍 __init__.py
│   ├── 🐍 main_window.py
│   ├── 🐍 theme.py
│   └── 🐍 widgets.py
├── ⚙️ .env.example
├── ⚙️ .gitignore
├── 📝 Readme.md
├── 📄 RequisitosCheck.txt
├── 🐍 app.py
└── 📄 requirements.txt
```

## 🔍 Fluxo de Funcionamento
### 1️⃣ app.py

Carrega o .env (MongoDB)

Inicializa o DataStore

Carrega o tema

Abre a interface principal (Dashboard)

### 2️⃣ DataStore (core/datastore.py)

Responsável por toda a persistência, incluindo:

Conexão com MongoDB Atlas

Criação automática do CSV

Save e read dinâmicos (MongoDB → primário / CSV → fallback)

Chamado por:
→ Dashboard
→ Cadastro
→ Visualização
→ Gráficos

### 3️⃣ UI (ui/)

Dividida em camadas profissionais:

🖥 MainWindow (Dashboard)

Resumo geral

Botão “Cadastrar Vaga”

Botão “Visualizar Candidaturas”

Área de gráficos animados

📝 Cadastro

Widgets usados:

Entry (empresa, cargo, data)

Combobox (tipo)

Radiobutton (status)

Text (observações)

Button estilizado

Ao enviar → grava via insert_candidatura()

📊 Visualização (TreeView)

Lista todas as candidaturas

Atualização automática

Mostra todos os campos

### 4️⃣ Gráficos (graphics/)

Inclui:

Gráfico de barras por status

Gráfico de linha (evolução por data)

Estilização avançada usando helpers.py

## 🧩 Tecnologias Utilizadas
Camada	Tecnologia
Interface	Tkinter
Dados	MongoDB Atlas + CSV
Gráficos	Matplotlib
Manipulação	Python 3.12+
Configuração	python-dotenv
Estrutura	SPA modular Tkinter


## ⚙️ Instalação e Execução

### 🪟 Windows

1) Ativar ambiente virtual (recomendado)
python -m venv .venv
.venv\Scripts\Activate

2) Instalar dependências
pip install -r requirements.txt

3) Rodar
python app.py

### 🐧 Linux (Ubuntu/Debian)
1) Criar ambiente virtual (recomendado)
python3 -m venv .venv

2) Ativar ambiente virtual
source .venv/bin/activate

3) Instalar Tkinter
sudo apt install python3-tk

4) Instalar dependências
pip3 install -r requirements.txt

5) Executar
python3 app.py

## 🌐 Variáveis de Ambiente (.env)

Exemplo de .env:

```bash
MEU_EMPREGO_MONGO_URI="Insira a Chave do seu banco de dados Aqui"
MEU_EMPREGO_DB_NAME="meu_emprego"
CANDIDATURAS_CSV_PATH="assets/candidaturas.csv"
APP_ENV="development"
DEBUG=1
```

## 🧪 Estrutura de Dados Gravados
```json
{
  "empresa": "Google",
  "cargo": "Desenvolvedor",
  "data": "2025-11-20",
  "tipo": "CLT",
  "status": "Enviado",
  "observacoes": "Processo iniciado",
  "link": "https://..."
}
```

## 📊 Telas do Sistema

(Serão adicionadas no relatório ABNT com imagens)

Dashboard

Cadastro

Visualização

Gráficos

## 🏁 Conclusão

O sistema “Meu Emprego” é robusto, organizado, escalável e cumpre rigorosamente todas as exigências do trabalho.
