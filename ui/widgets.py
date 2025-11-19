"""
Componentes reutilizáveis de UI para o Meu Emprego.
"""

import tkinter as tk
from tkinter import ttk


class BaseFrame(ttk.Frame):
    """Frame base com padding e configuração padrão."""

    def __init__(self, master=None, padding=12, **kwargs):
        super().__init__(master, padding=padding, **kwargs)
        self.columnconfigure(0, weight=1)


def InfoLabel(master, text, **kwargs):
    """Label simples para informações contextuais."""
    return ttk.Label(master, text=text, **kwargs)


def ActionButton(
    master,
    text,
    command,
    width: int | None = None,
    style: str = "Rounded.TButton",
    **kwargs,
):
    """
    Botão de ação estilizado.

    - width: largura em caracteres (None => automático)
    - style: estilo ttk (por padrão Rounded.TButton)
    """
    params = dict(text=text, command=command, style=style, **kwargs)
    if width is not None:
        params["width"] = width
    return ttk.Button(master, **params)
