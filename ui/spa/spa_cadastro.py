"""
SPACadastro — Tela SPA responsável pelo cadastro de novas candidaturas.

- Fonte  (tema gerencia fonte global, campos herdam automaticamente).
- Layout alinhado, campos organizados e espaçados.
- refresh local (refresh é o ↻ global no header).
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime

from ui.widgets import InfoLabel


class SPACadastro(ttk.Frame):
    """Painel SPA de cadastro de candidatura."""

    def __init__(self, parent, datastore):
        super().__init__(parent, padding=16)

        self.datastore = datastore

        # Layout responsivo
        self.columnconfigure(1, weight=1)
        self.rowconfigure(7, weight=1)

        self._build()

    # =====================================================================
    # LAYOUT DO FORMULÁRIO
    # =====================================================================
    def _build(self):
        # Título da seção
        InfoLabel(
            self,
            text="Nova Candidatura",
            font=("TkDefaultFont", 18, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        # Empresa
        ttk.Label(self, text="Nome da Empresa:").grid(
            row=1, column=0, sticky="w", pady=4
        )
        self.empresa_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.empresa_var).grid(
            row=1, column=1, sticky="ew", padx=(0, 4)
        )

        # Cargo
        ttk.Label(self, text="Cargo:").grid(row=2, column=0, sticky="w", pady=4)
        self.cargo_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.cargo_var).grid(
            row=2, column=1, sticky="ew", padx=(0, 4)
        )

        # Link da Vaga
        ttk.Label(self, text="Link da Vaga:").grid(
            row=3, column=0, sticky="w", pady=4
        )
        self.link_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.link_var).grid(
            row=3, column=1, sticky="ew", padx=(0, 4)
        )

        # Data da Inscrição
        ttk.Label(self, text="Data da inscrição:").grid(
            row=4, column=0, sticky="w", pady=4
        )
        self.data_var = tk.StringVar(value=datetime.date.today().isoformat())
        ttk.Entry(self, textvariable=self.data_var, width=20).grid(
            row=4, column=1, sticky="w"
        )

        # Modelo de Trabalho (Combobox)
        ttk.Label(self, text="Modelo de Trabalho:").grid(
            row=5, column=0, sticky="w", pady=4
        )

        self.tipo_var = tk.StringVar()
        tipos = ["Presencial", "Remoto", "Híbrido"]

        ttk.Combobox(
            self,
            textvariable=self.tipo_var,
            values=tipos,
            state="readonly",
        ).grid(row=5, column=1, sticky="ew")

        # Status (Radio Buttons)
        ttk.Label(self, text="Status:").grid(
            row=6, column=0, sticky="nw", pady=4
        )

        self.status_var = tk.StringVar(value="Inscrito")
        status_frame = ttk.Frame(self)
        status_frame.grid(row=6, column=1, sticky="w")

        for s in ["Inscrito", "Entrevista", "Rejeitado", "Contratado"]:
            ttk.Radiobutton(
                status_frame,
                text=s,
                variable=self.status_var,
                value=s,
            ).pack(side="left", padx=4)

        # Observações (Text Area)
        ttk.Label(self, text="Descrição e Requisitos:").grid(
            row=7, column=0, sticky="nw", pady=4
        )

        self.obs_text = tk.Text(self, width=40, height=5)
        self.obs_text.grid(row=7, column=1, sticky="nsew")

        # Botões (Salvar / Limpar)
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=8, column=1, sticky="e", pady=(12, 0))

        ttk.Button(
            btn_frame,
            text="Salvar",
            command=self._on_submit,
        ).pack(side="left", padx=6)

        ttk.Button(
            btn_frame,
            text="Limpar",
            command=self._clear_form,
        ).pack(side="left", padx=6)

    # =====================================================================
    # FUNÇÕES DO FORMULÁRIO
    # =====================================================================
    def _clear_form(self):
        """Limpa todos os campos do formulário."""
        self.empresa_var.set("")
        self.cargo_var.set("")
        self.link_var.set("")
        self.data_var.set(datetime.date.today().isoformat())
        self.tipo_var.set("")
        self.status_var.set("Inscrito")
        self.obs_text.delete("1.0", "end")

    def _on_submit(self):
        """Valida e envia os dados ao DataStore."""
        doc = {
            "empresa": self.empresa_var.get().strip(),
            "cargo": self.cargo_var.get().strip(),
            "link": self.link_var.get().strip(),
            "data": self.data_var.get().strip(),
            "tipo": self.tipo_var.get().strip(),
            "status": self.status_var.get().strip(),
            "observacoes": self.obs_text.get("1.0", "end").strip(),
        }

        # Validações essenciais
        if not doc["empresa"] or not doc["cargo"]:
            messagebox.showwarning("Validação", "Preencha Empresa e Cargo.")
            return

        try:
            datetime.date.fromisoformat(doc["data"])
        except Exception:
            messagebox.showwarning(
                "Validação", "Data inválida (use YYYY-MM-DD)."
            )
            return

        # Insere no banco
        res = self.datastore.insert_candidatura(doc)

        if res.get("ok"):
            messagebox.showinfo("Sucesso", "Registro salvo!")
            self._clear_form()
        else:
            messagebox.showerror("Erro", "Falha ao salvar no banco.")
