"""
Tema e estilos Tkinter/ttk para o Meu Emprego.
"""

from tkinter import ttk

try:
    import tkinter as tk
    from tkinter import font as tkfont
except Exception:
    tk = None
    tkfont = None

PRIMARY = "#2b7cff"
PRIMARY_DARK = "#1a60d6"
BG = "#f7f9fc"
SURFACE = "#ffffff"
TEXT = "#222222"
MUTED = "#6b7280"


def apply_theme(root):
    if tk is None or tkfont is None:
        return {}

    style = ttk.Style(root)

    # Tenta melhorar o visual
    for theme_name in ("clam", "alt", "default"):
        try:
            style.theme_use(theme_name)
            break
        except Exception:
            continue

    # Fontes globais
    default_font = tkfont.nametofont("TkDefaultFont")
    default_font.configure(size=16)

    title_font = tkfont.Font(
        root=root,
        family=default_font.cget("family"),
        size=22,
        weight="bold",
    )

    # Fonte para cabeçalho da Treeview
    heading_font = tkfont.Font(
        root=root,
        family=default_font.cget("family"),
        size=14,
        weight="bold",
    )

    try:
        style.configure(".", background=BG, foreground=TEXT)
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=TEXT)
        style.configure("TEntry", padding=8)

        style.configure(
            "TButton",
            padding=10,
            relief="flat",
            background=PRIMARY,
            foreground="white",
            borderwidth=0,
        )
        style.map(
            "TButton",
            foreground=[("disabled", MUTED)],
            background=[("active", PRIMARY_DARK)],
        )

        style.configure(
            "Rounded.TButton",
            padding=10,
            background=PRIMARY,
            foreground="white",
            borderwidth=0,
        )

        style.configure(
            "Icon.TButton",
            padding=4,
            relief="flat",
            background=BG,
            foreground=TEXT,
            borderwidth=0,
        )

        # Treeview cabeçalho mais legível
        style.configure("Treeview.Heading", font=heading_font)

    except Exception:
        pass

    return {
        "style": style,
        "default_font": default_font,
        "title_font": title_font,
    }
