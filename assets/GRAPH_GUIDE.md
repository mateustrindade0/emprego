# Guia para implementação dos gráficos (Dashboard)

Este documento destina-se ao desenvolvedor encarregado de implementar a área de
análise/gráficos no dashboard da aplicação `Meu Emprego`.

## Objetivo

- Fornecer instruções claras e um snippet de exemplo para embutir gráficos
  Matplotlib dentro do `MainWindow` usando `FigureCanvasTkAgg`.
- Orientar sobre pré-requisitos, manipulação de dados e boas práticas de
  responsividade.

## Estrutura atual

- Persistência de dados: `core/datastore.py` (classe `DataStore`).
- UI principal: `ui/main_window.py` (classe `MainWindow`).
- Gráficos: pasta `graphics/`:
  - `dashboard_graphs.py` — classe `DashboardGraphs` embutida no Tkinter.
  - `helpers.py` — paleta de cores e estilo.
  - `generate_dashboard.py` — função para gerar gráficos direto do CSV (modo teste).

## Dependências

Adicione (ou confirme) no `requirements.txt`:

```text
matplotlib>=3.0
pandas>=2.0
