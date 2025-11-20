"""
Janela principal do sistema Meu Emprego.

Funções principais:
- Montar a janela principal
- Criar navegação lateral
- Controlar o painel dinâmico
- Atualizar a tela ativa com o botão ↻
- Testar conexão com o MongoDB via botão 🌐
- Exportar CSV
"""

import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont

from core.datastore import DataStore
from ui.widgets import BaseFrame, InfoLabel, ActionButton

# Importa as telas SPA
from ui.spa.spa_dashboard import SPADashboard
from ui.spa.spa_cadastro import SPACadastro
from ui.spa.spa_visualizacao import SPAVisualizacao


class MainWindow:
    """
    Controlador principal da SPA.

    coordenador que recebe a janela Tk,
    monta a estrutura e controla qual painel SPA fica visível.
    """

    def __init__(self, root: tk.Tk, datastore: DataStore):
        self.root = root
        self.datastore = datastore

        self.root.title("Meu Emprego – Visão Geral")

        # Fontes do título (com suporte a responsividade)
        try:
            self.default_font = tkfont.nametofont("TkDefaultFont")
            self.title_font = tkfont.Font(
                root=self.root,
                family=self.default_font.cget("family"),
                size=22,
                weight="bold",
            )
        except Exception:
            self.default_font = None
            self.title_font = None

        self._resize_after = None
        self._last_title_sz = None

        # referências da UI
        self.summary_label: ttk.Label | None = None
        self.content_frame: ttk.Frame | None = None
        self.current_view: ttk.Frame | None = None

        # constrói layout
        self._build_layout()

        # abre o Dashboard
        self.show_dashboard()

        # responsividade do título
        self.root.bind("<Configure>", self._on_root_resize)

    # =====================================================================
    # LAYOUT BASE
    # =====================================================================
    def _build_layout(self):
        """Cria o layout base da janela (não cria as telas SPA aqui)."""

        frame_root = BaseFrame(self.root, padding=16)
        frame_root.grid(sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        frame_root.columnconfigure(0, weight=0) 
        frame_root.columnconfigure(1, weight=1)  
        frame_root.rowconfigure(2, weight=1)

        # -------------------------------------------------------------
        # Cabeçalho
        # -------------------------------------------------------------
        ttk.Label(frame_root, text="Meu Emprego", font=self.title_font).grid(
            row=0, column=0, pady=(0, 4), sticky="w", columnspan=2
        )

        backend = "MongoDB" if self.datastore.use_mongo else "CSV (fallback)"

        # Linha de metadados (apenas ícones aqui). Backend mostrado no rodapé.
        # Mantemos espaço para os ícones no topo direito.
        # (O label de 'Candidaturas' será criado pela view do Dashboard)

        # Ícones do cabeçalho
        icons_frame = ttk.Frame(frame_root)
        icons_frame.grid(row=1, column=1, sticky="e")

        ttk.Button(
            icons_frame,
            text="🌐",
            width=3,
            command=self._on_test_connection,
            style="Icon.TButton",
        ).pack(side="left", padx=4)

        ttk.Button(
            icons_frame,
            text="↻",
            width=3,
            command=self._on_refresh_current_view,
            style="Icon.TButton",
        ).pack(side="left", padx=4)

        # -------------------------------------------------------------
        # Navegação lateral (SPA)
        # -------------------------------------------------------------
        nav = ttk.Frame(frame_root)
        nav.grid(row=2, column=0, sticky="nsw", padx=(0, 10))
        nav.columnconfigure(0, weight=1)

        # Botões SPA (sem contador aqui)
        ActionButton(nav, text="Visão Geral", command=self.show_dashboard).grid(
            row=0, column=0, sticky="ew", pady=4
        )
        ActionButton(nav, text="Nova Candidatura", command=self.show_cadastro).grid(
            row=1, column=0, sticky="ew", pady=4
        )
        ActionButton(
            nav, text="Visualizar Candidaturas", command=self.show_visualizacao
        ).grid(row=2, column=0, sticky="ew", pady=4)

        ActionButton(nav, text="Exportar CSV", command=self.export_csv).grid(
            row=3, column=0, sticky="ew", pady=4
        )

        # -------------------------------------------------------------
        # Painel dinâmico (SPA)
        # -------------------------------------------------------------
        self.content_frame = ttk.Frame(frame_root, borderwidth=1, relief="solid")
        self.content_frame.grid(row=2, column=1, sticky="nsew")
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)

        # Rodapé: mostra o backend/pendência atual
        footer = ttk.Frame(frame_root)
        footer.grid(row=3, column=0, sticky="w", columnspan=2, pady=(8, 0))
        InfoLabel(footer, text=f"Conectado ao {backend}", font=("TkDefaultFont", 9)).pack(side="left")

    # =====================================================================
    # TROCA DE TELAS (SPA)
    # =====================================================================
    def _set_view(self, view_cls):
        """Substitui o painel direito por outro painel SPA."""

        # Remove tela anterior
        if self.current_view:
            try:
                self.current_view.destroy()
            except Exception:
                pass

        # Cria nova tela
        self.current_view = view_cls(self.content_frame, self.datastore)
        self.current_view.grid(row=0, column=0, sticky="nsew")

        self.summary_label = getattr(self.current_view, "summary_label", self.summary_label)

        # Atualiza o contador no cabeçalho
        self._update_summary()

    def show_dashboard(self):
        self._set_view(SPADashboard)

    def show_cadastro(self):
        self._set_view(SPACadastro)

    def show_visualizacao(self):
        self._set_view(SPAVisualizacao)

    # =====================================================================
    # RESUMO (CANDIDATURAS)
    # =====================================================================
    def _update_summary(self):
        try:
            total = len(self.datastore.list_candidaturas() or [])
        except Exception:
            total = 0

        if self.summary_label is not None:
            self.summary_label.config(text=f"Candidaturas: {total}")

    # =====================================================================
    # AÇÕES GERAIS
    # =====================================================================
    def _on_test_connection(self):
        """Ícone 🌐 — testa conexão com MongoDB."""
        res = self.datastore.test_connection()
        if res.get("ok"):
            messagebox.showinfo(
                "Conexão", f"Conectado ao MongoDB {res.get('server')}"
            )
        else:
            messagebox.showerror(
                "Conexão", f"Erro: {res.get('msg', 'sem detalhes')}"
            )

    def _on_refresh_current_view(self):
        """Ícone ↻ — Atualiza a tela atual."""

        try:
            if hasattr(self.current_view, "refresh_dashboard"):
                self.current_view.refresh_dashboard()
            elif hasattr(self.current_view, "_load_data"):
                self.current_view._load_data()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao atualizar:\n{e}")

        self._update_summary()

    # =====================================================================
    # EXPORTAR CSV
    # =====================================================================
    def export_csv(self):
        """Exporta todos os registros para um arquivo CSV."""

        try:
            rows = self.datastore.list_candidaturas()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao obter dados:\n{e}")
            return

        if not rows:
            messagebox.showinfo("Exportação", "Não há dados para exportar.")
            return

        try:
            import pandas as pd
            from tkinter.filedialog import asksaveasfilename

            path = asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                title="Salvar como...",
            )

            if not path:
                return

            pd.DataFrame(rows).to_csv(path, index=False, encoding="utf-8-sig")
            messagebox.showinfo("Exportação", f"Arquivo salvo em:\n{path}")

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao exportar:\n{e}")

    # =====================================================================
    # RESPONSIVIDADE DO TÍTULO
    # =====================================================================
    def _on_root_resize(self, event=None):
        if self._resize_after:
            try:
                self.root.after_cancel(self._resize_after)
            except Exception:
                pass

        self._resize_after = self.root.after(120, self._apply_responsive)

    def _apply_responsive(self):
        if not self.title_font:
            return

        width = self.root.winfo_width()
        if not width:
            return

        new_size = max(14, int(22 * max(0.7, min(1.4, width / 800))))

        if new_size != self._last_title_sz:
            try:
                self.title_font.configure(size=new_size)
                self._last_title_sz = new_size
            except Exception:
                pass
