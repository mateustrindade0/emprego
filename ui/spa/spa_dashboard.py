"""
Dashboard — Painel embutido de gráficos.
"""

from tkinter import ttk, messagebox

from graphics.dashboard_graphs import DashboardGraphs
from ui.widgets import InfoLabel


class SPADashboard(ttk.Frame):
    """Painel SPA do Dashboard (gráficos)."""

    def __init__(self, parent, datastore):
        super().__init__(parent, padding=12)

        self.datastore = datastore
        self._dashboard = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build()

    # =====================================================================
    # LAYOUT
    # =====================================================================
    def _build(self):
        # cabeçalho interno
        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        header.columnconfigure(0, weight=1)
        header.columnconfigure(1, weight=0)

        InfoLabel(
            header,
            text="Visão Geral das Candidaturas",
            font=("TkDefaultFont", 18, "bold"),
        ).grid(row=0, column=0, sticky="w")

        # label de resumo (Candidaturas) no lado oposto do título
        self.summary_label = InfoLabel(header, text="Candidaturas: 0")
        self.summary_label.grid(row=0, column=1, sticky="e")

        # Painel de gráficos
        body = ttk.Frame(self)
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)

        try:
            self._dashboard = DashboardGraphs(
                parent=body, datastore=self.datastore
            )
            self._dashboard.build()
            self._dashboard.refresh()
        except Exception as e:
            InfoLabel(body, text=f"Erro ao carregar gráficos:\n{e}").grid(
                row=0, column=0, sticky="nsew", padx=12, pady=12
            )

    # =====================================================================
    # (chamada pelo ícone ↻ externo)
    # =====================================================================
    def refresh_dashboard(self):
        """Atualiza gráficos sem recarregar a página."""
        if self._dashboard:
            try:
                self._dashboard.refresh()
            except Exception as e:
                messagebox.showerror(
                    "Erro", f"Não foi possível atualizar:\n{e}"
                )
