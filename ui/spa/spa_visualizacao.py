"""
SPA Visualização — Tabela de candidaturas.
"""

from tkinter import ttk, messagebox
import tkinter.font as tkfont
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

        # Debounce handle for resize
        self._resize_after = None

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

        # Cabeçalhos (alinhados à esquerda para melhor leitura)
        self.tree.heading("empresa", text="Empresa", anchor="w")
        self.tree.heading("cargo", text="Cargo", anchor="w")
        self.tree.heading("link", text="Link da Vaga", anchor="w")
        self.tree.heading("data", text="Data", anchor="w")
        self.tree.heading("tipo", text="Modelo", anchor="w")
        self.tree.heading("status", text="Status", anchor="w")
        self.tree.heading("observacoes", text="Observações", anchor="w")

        # Larguras, alinhamento e stretch para melhor redimensionamento
        self.tree.column("empresa", width=180, minwidth=80, anchor="w", stretch=True)
        self.tree.column("cargo", width=170, minwidth=80, anchor="w", stretch=True)
        self.tree.column("link", width=300, minwidth=120, anchor="w", stretch=True)
        self.tree.column("data", width=100, minwidth=60, anchor="w", stretch=False)
        self.tree.column("tipo", width=100, minwidth=60, anchor="w", stretch=False)
        self.tree.column("status", width=110, minwidth=70, anchor="w", stretch=False)
        self.tree.column("observacoes", width=300, minwidth=120, anchor="w", stretch=True)

        # Grade principal da Treeview
        self.tree.grid(row=1, column=0, sticky="nsew")

        # Scrollbars: vertical à direita e horizontal abaixo
        vscroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vscroll.set)
        vscroll.grid(row=1, column=1, sticky="ns")

        hscroll = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscroll=hscroll.set)
        # horizontal abaixo da tabela; isso empurra a paginação para baixo
        hscroll.grid(row=2, column=0, sticky="ew")

        # Bind para redimensionar colunas dinamicamente
        try:
            self.bind("<Configure>", self._on_configure)
            # redimensionamento inicial
            self.after(50, self._resize_columns)
        except Exception:
            pass

        # Paginação simples (prev / página / next)
        pag_frame = ttk.Frame(self)
        pag_frame.grid(row=3, column=0, sticky="w", pady=(8, 0))

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
        btn_frame.grid(row=4, column=0, sticky="e", pady=(8, 0))

        ttk.Button(btn_frame, text="Abrir Link", command=self._open_link).pack(
            side="left", padx=4
        )

        ttk.Button(
            btn_frame, text="Copiar Link", command=self._copy_link
        ).pack(side="left", padx=4)

        # Carrega dados inicialmente
        self._load_data()

        # Melhor visual: aumenta um pouco a altura das linhas
        try:
            style = ttk.Style(self)
            style.configure("Treeview", rowheight=26)
        except Exception:
            pass

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

        # Ajusta colunas automaticamente com base no conteúdo visível
        try:
            self._autosize_columns(page_rows)
        except Exception:
            pass

        # Atualiza estado dos botões e label
        self.page_label.config(text=f"Página {self.page+1}/{self.total_pages}")
        self.prev_btn.config(state=("disabled" if self.page <= 0 else "normal"))
        self.next_btn.config(state=("disabled" if self.page >= self.total_pages-1 else "normal"))

    # =====================================================================
    # REDIMENSIONAMENTO AUTOMÁTICO
    # =====================================================================
    def _on_configure(self, event=None):
        if self._resize_after:
            try:
                self.after_cancel(self._resize_after)
            except Exception:
                pass

        self._resize_after = self.after(120, self._resize_columns)

    def _resize_columns(self):
        """Calcula larguras das colunas com base na largura disponível do widget."""
        try:
            self._resize_after = None
            total_w = self.winfo_width()
            if not total_w or total_w < 200:
                return

            # espaço para scrollbar vertical e margens
            vbar = 20
            padding = 24
            avail = max(200, total_w - vbar - padding)

            # alocações percentuais (soma = 1.0)
            ratios = {
                "empresa": 0.18,
                "cargo": 0.18,
                "link": 0.30,
                "data": 0.08,
                "tipo": 0.08,
                "status": 0.10,
                "observacoes": 0.08,
            }

            for col, r in ratios.items():
                w = max(int(avail * r), 60)
                try:
                    self.tree.column(col, width=w)
                except Exception:
                    pass
        except Exception:
            pass

    # =====================================================================
    # UTILITÁRIOS
    # =====================================================================
    def _get_selected_link(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma candidatura.")
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

    # =====================================================================
    # AUTO SIZE COLUMNS
    # =====================================================================
    def _autosize_columns(self, rows):
        """Calcula a largura ideal de cada coluna com base no cabeçalho e no conteúdo da
        página atual, usando medidas de fonte para evitar cortes de texto."""
        try:
            font = tkfont.nametofont("TkDefaultFont")
        except Exception:
            font = None

        cols = [
            "empresa",
            "cargo",
            "link",
            "data",
            "tipo",
            "status",
            "observacoes",
        ]

        padding = 18
        max_widths = {}

        # Começa pelo tamanho do cabeçalho
        for c in cols:
            header = self.tree.heading(c).get("text", c)
            w = (font.measure(header) if font else len(header) * 8) + padding
            max_widths[c] = w

        # Verifica conteúdo da página atual
        for r in rows:
            for c in cols:
                txt = str(r.get(c, ""))
                m = (font.measure(txt) if font else len(txt) * 8) + padding
                if m > max_widths.get(c, 0):
                    max_widths[c] = m

        # Se houver espaço restante, distribui preferencialmente para 'link' e 'observacoes'
        total_needed = sum(max_widths.values())
        avail = self.winfo_width() or self.winfo_reqwidth() or 800
        # reserva para scrollbar e margens
        reserve = 60
        extra = avail - total_needed - reserve
        if extra > 40:
            add_link = int(extra * 0.65)
            add_obs = extra - add_link
            max_widths["link"] = max_widths.get("link", 100) + add_link
            max_widths["observacoes"] = max_widths.get("observacoes", 100) + add_obs

        # Aplica larguras calculadas
        for c, w in max_widths.items():
            try:
                self.tree.column(c, width=int(w), minwidth=60)
            except Exception:
                pass
