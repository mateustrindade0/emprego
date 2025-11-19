"""
DashboardGraphs — Classe responsável por desenhar e atualizar os gráficos
exibidos no painel direito da aplicação.

Ele funciona como um widget embutido no Tkinter, utilizando o backend TkAgg
para integrar Matplotlib com Tkinter.

Contém:
• Gráfico de barras (Candidaturas por Status)
• Gráfico de linha (Candidaturas nos últimos 30 dias)
"""

from pathlib import Path
from typing import Optional
import datetime

import pandas as pd
import matplotlib.pyplot as plt

from graphics.helpers import apply_rc_style, style_axes, PALETTE

# Integração Tkinter + Matplotlib
try:
    import tkinter as tk
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
except Exception:
    tk = None
    FigureCanvasTkAgg = None


# --------------------------------------------------------------------------
# Função utilitária para localizar a coluna correta ignorando maiúsculas/minúsculas
# --------------------------------------------------------------------------
def _find_col(df: pd.DataFrame, *names: str) -> Optional[str]:
    cols = {c.lower(): c for c in df.columns}
    for n in names:
        if n.lower() in cols:
            return cols[n.lower()]
    return None


# --------------------------------------------------------------------------
# Função correta para normalizar datas vindas do MongoDB e CSV
# --------------------------------------------------------------------------
def _normalize_date(v):
    """
    Aceita formatos:
    • {"$date": "..."} (MongoDB)
    • "2025-11-02" (string)
    • datetime / Timestamp
    """
    try:
        if isinstance(v, dict) and "$date" in v:
            return pd.to_datetime(v["$date"], utc=True).tz_convert(None)
        return pd.to_datetime(v, utc=True).tz_convert(None)
    except Exception:
        return pd.NaT


# --------------------------------------------------------------------------
# CLASSE PRINCIPAL DOS GRÁFICOS
# --------------------------------------------------------------------------
class DashboardGraphs:
    """
    Widget responsável por desenhar e atualizar gráficos da dashboard.

    Métodos:
    • build() -> monta a figura no Tkinter
    • refresh() -> redesenha os gráficos com os dados atuais
    """

    def __init__(self, parent, datastore):
        if tk is None or FigureCanvasTkAgg is None:
            raise RuntimeError("TkAgg/Tkinter não disponíveis no ambiente.")

        self.parent = parent
        self.datastore = datastore

        self.fig = None
        self.canvas = None
        self.axs = None

    # ----------------------------------------------------------------------
    def build(self):
        """Cria a figura Matplotlib dentro do Tkinter."""

        apply_rc_style()

        self.fig, self.axs = plt.subplots(1, 2, figsize=(10, 4))

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent)
        widget = self.canvas.get_tk_widget()
        widget.grid(row=0, column=0, sticky="nsew")

        try:
            self.parent.rowconfigure(0, weight=1)
            self.parent.columnconfigure(0, weight=1)
        except:
            pass

    # ----------------------------------------------------------------------
    def refresh(self):
        """Recalcula e redesenha os gráficos com base nos dados mais recentes."""

        # Obtém dados do banco
        try:
            rows = self.datastore.list_candidaturas(
                limit=None,
                order_by_date_desc=False
            )
        except Exception:
            rows = []

        df = pd.DataFrame(rows)

        # Detecção de colunas
        date_col = _find_col(df, "data", "Date")
        status_col = _find_col(df, "status", "Status")

        # Limpa e cria novos eixos
        self.fig.clear()
        axs = self.fig.subplots(1, 2)

        # ==================================================================
        # GRÁFICO 1 — Candidaturas por Status
        # ==================================================================
        ax_bar = axs[0]
        style_axes(ax_bar)

        if status_col and status_col in df.columns:
            counts = df[status_col].fillna("(sem status)").value_counts()
            labels = list(counts.index)
            values = list(counts.values)

            status_colors = {
                "Inscrito": PALETTE["primary"],
                "Entrevista": PALETTE["accent"],
                "Rejeitado": PALETTE["danger"],
                "Contratado": PALETTE["success"],
            }

            colors = [status_colors.get(lb, PALETTE["primary"]) for lb in labels]

            bars = ax_bar.bar(labels, values, color=colors)

            # Rótulos cima das barras
            for bar in bars:
                h = bar.get_height()
                ax_bar.text(
                    bar.get_x() + bar.get_width() / 2,
                    h,
                    str(int(h)),
                    ha="center",
                    va="bottom",
                    fontsize=8,
                )
        else:
            ax_bar.text(0.5, 0.5, "Sem coluna 'status'", ha="center")

        ax_bar.set_title("Candidaturas por Status")

        # ==================================================================
        # GRÁFICO 2 — Últimos 30 dias
        # ==================================================================
        ax_line = axs[1]
        style_axes(ax_line)

        if date_col and date_col in df.columns:

            # Normaliza datas (CORRIGIDO)
            df[date_col] = df[date_col].apply(_normalize_date)
            times = df.dropna(subset=[date_col]).copy()

            if not times.empty:
                times["_day"] = times[date_col].dt.date
                series = times.groupby("_day").size()

                N = 30
                last_date = series.index.max()
                start_date = last_date - datetime.timedelta(days=N - 1)

                rng = pd.date_range(start=start_date, end=last_date)
                rng_days = [d.date() for d in rng]

                series_full = pd.Series(index=rng_days, data=0)
                for d, v in series.items():
                    if d in series_full.index:
                        series_full.loc[d] = v

                ax_line.plot(
                    series_full.index,
                    series_full.values,
                    marker="o",
                    color=PALETTE["primary"],
                    linewidth=2.2,
                )

                for x, y in zip(series_full.index, series_full.values):
                    if y:
                        ax_line.text(
                            x,
                            y,
                            str(int(y)),
                            ha="center",
                            va="bottom",
                            fontsize=8,
                        )
        else:
            ax_line.text(0.5, 0.5, "Sem dados de data", ha="center")

        ax_line.set_title("Vagas Recentes (últimos 30 dias)")
        ax_line.set_xlabel("Data")

        self.fig.tight_layout()

        try:
            self.canvas.draw()
        except:
            pass
