# graphics/helpers.py
"""
Helpers e estilos de visualização para gráficos matplotlib.
"""

import matplotlib as mpl


PALETTE = {
    "primary": "#2C7BB6",
    "accent": "#F4A261",
    "success": "#2ECC71",
    "danger": "#E63946",
}


def apply_rc_style():
    """Aplica configurações globais de estilo ao matplotlib."""
    mpl.rcParams.update({
        "figure.facecolor": "white",
        "axes.titlesize": 12,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Liberation Sans"],
    })


def style_axes(ax):
    """Aplica estilo consistente a um axe matplotlib."""
    try:
        ax.set_facecolor("#ffffff")
        ax.grid(axis="y", linestyle="--", alpha=0.25)
    except Exception:
        pass


def safe_labels(labels):
    """Converte rótulos para strings seguras."""
    return [str(x) if x is not None else "" for x in labels]
