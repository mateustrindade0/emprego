"""
SPA Visualização — Tabela de candidaturas.
"""

from tkinter import ttk, messagebox
import webbrowser

from ui.widgets import InfoLabel


class SPAVisualizacao(ttk.Frame):
    """Painel SPA que exibe as candidaturas cadastradas."""

    def __init__(self, parent, datastore):
        super().__init__(parent, padding=12)

        self.datastore = datastore
        # Paginação
        self.page = 0
        self.page_size = 20
        self.total_pages = 1

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build()

    # =====================================================================
    # BUILD
    # =====================================================================
    def _build(self):
        InfoLabel(
            self,
            text="Visualizar Candidaturas",
            font=("TkDefaultFont", 18, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        # -----------------------------------------------------------------
        # Tabela
        # -----------------------------------------------------------------
        cols = [
            "empresa",
            "cargo",
            "link",
            "data",
            "tipo",
            "status",
            "observacoes",
        ]

        self.tree = ttk.Treeview(
            self,
            columns=cols,
            show="headings",
            height=14,
        )

        # Cabeçalhos
        self.tree.heading("empresa", text="Empresa")
        self.tree.heading("cargo", text="Cargo")
        self.tree.heading("link", text="Link da Vaga")
        self.tree.heading("data", text="Data")
        self.tree.heading("tipo", text="Modelo")
        self.tree.heading("status", text="Status")
        self.tree.heading("observacoes", text="Observações")

        # Larguras
        self.tree.column("empresa", width=130)
        self.tree.column("cargo", width=130)
        self.tree.column("link", width=200)
        self.tree.column("data", width=80)
        self.tree.column("tipo", width=90)
        self.tree.column("status", width=100)
        self.tree.column("observacoes", width=200)

        self.tree.grid(row=1, column=0, sticky="nsew")

        scroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scroll.set)
        scroll.grid(row=1, column=1, sticky="ns")

        # Paginação simples (prev / página / next)
        pag_frame = ttk.Frame(self)
        pag_frame.grid(row=2, column=0, sticky="w", pady=(8, 0))

        self.prev_btn = ttk.Button(pag_frame, text="◀", command=self._on_prev, style="Icon.TButton", width=3)
        self.prev_btn.pack(side="left", padx=(0, 6))

        self.page_label = InfoLabel(pag_frame, text="Página 1/1")
        self.page_label.pack(side="left", padx=(0, 6))

        self.next_btn = ttk.Button(pag_frame, text="▶", command=self._on_next, style="Icon.TButton", width=3)
        self.next_btn.pack(side="left", padx=(0, 6))

        # -----------------------------------------------------------------
        # Botões inferiores (somente link)
        # -----------------------------------------------------------------
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=3, column=0, sticky="e", pady=(8, 0))

        ttk.Button(btn_frame, text="Abrir Link", command=self._open_link).pack(
            side="left", padx=4
        )

        ttk.Button(
            btn_frame, text="Copiar Link", command=self._copy_link
        ).pack(side="left", padx=4)

        # Carrega dados inicialmente
        self._load_data()

    # =====================================================================
    # CARREGAR DADOS (é chamado via ↻ no MainWindow)
    # =====================================================================
    def _load_data(self):
        """Carrega registros do banco e atualiza a tabela."""
        try:
            rows = self.datastore.list_candidaturas()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar dados:\n{e}")
            return

        # Atualiza paginação
        total = len(rows or [])
        import math
        self.total_pages = max(1, math.ceil(total / self.page_size))
        if self.page >= self.total_pages:
            self.page = self.total_pages - 1

        start = self.page * self.page_size
        end = start + self.page_size
        page_rows = (rows or [])[start:end]

        for i in self.tree.get_children():
            self.tree.delete(i)

        for row in page_rows:
            self.tree.insert(
                "",
                "end",
                values=(
                    row.get("empresa", ""),
                    row.get("cargo", ""),
                    row.get("link", ""),
                    row.get("data", ""),
                    row.get("tipo", ""),
                    row.get("status", ""),
                    row.get("observacoes", ""),
                ),
            )

        # Atualiza estado dos botões e label
        self.page_label.config(text=f"Página {self.page+1}/{self.total_pages}")
        self.prev_btn.config(state=("disabled" if self.page <= 0 else "normal"))
        self.next_btn.config(state=("disabled" if self.page >= self.total_pages-1 else "normal"))

    # =====================================================================
    # UTILITÁRIOS
    # =====================================================================
    def _get_selected_link(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma linha.")
            return None

        values = self.tree.item(selected[0], "values")
        return values[2]  # índice do link

    def _open_link(self):
        link = self._get_selected_link()
        if not link:
            return

        if not link.startswith("http"):
            messagebox.showwarning("Link inválido", "O link parece inválido.")
            return

        webbrowser.open(link)

    def _copy_link(self):
        link = self._get_selected_link()
        if not link:
            return

        self.clipboard_clear()
        self.clipboard_append(link)
        messagebox.showinfo(
            "Copiado", "Link copiado para área de transferência."
        )

    # =====================================================================
    # PAGINAÇÃO
    # =====================================================================
    def _on_prev(self):
        if self.page > 0:
            self.page -= 1
            self._load_data()

    def _on_next(self):
        if self.page < self.total_pages - 1:
            self.page += 1
            self._load_data()
