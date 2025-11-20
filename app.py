# app.py
"""
Aplicação Meu Emprego.

Responsabilidades deste arquivo:
- Inicializar variáveis de ambiente (.env).
- Criar o DataStore (MongoDB ou CSV).
- Criar a janela Tkinter principal.
- Aplicar o tema visual.
- Instanciar a MainWindow (SPA) e iniciar o loop da aplicação.
"""

import os
import tkinter as tk

from dotenv import load_dotenv

from core.datastore import DataStore
from ui.theme import apply_theme
from ui.main_window import MainWindow


def main():
    """Ponto de entrada da aplicação."""

    # ------------------------------------------------------------------
    # 1) Carrega variáveis de ambiente (.env)
    # ------------------------------------------------------------------
    load_dotenv(".env")

    mongo_uri = os.environ.get("MEU_EMPREGO_MONGO_URI", "")
    db_name = os.environ.get("MEU_EMPREGO_DB_NAME", "meu_emprego")

    # ------------------------------------------------------------------
    # 2) Inicializa a camada de dados (DataStore)
    # ------------------------------------------------------------------
    datastore = DataStore(mongo_uri=mongo_uri, db_name=db_name)

    # ------------------------------------------------------------------
    # 3) Cria janela raiz Tkinter
    # ------------------------------------------------------------------
    root = tk.Tk()
    root.title("Meu Emprego")

    # Aplica tema visual (cores, fontes, estilos de botão)
    apply_theme(root)

    # ------------------------------------------------------------------
    # 4) Instancia a MainWindow SPA
    # ------------------------------------------------------------------
    _app = MainWindow(root, datastore) 

    # Dimensões iniciais (simples, centralizado na tela)
    try:
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        w = max(900, int(sw * 0.7))
        h = max(600, int(sh * 0.7))
        x = (sw - w) // 2
        y = (sh - h) // 2
        root.geometry(f"{w}x{h}+{x}+{y}")
    except Exception:
        pass

    # ------------------------------------------------------------------
    # 5) Inicia o loop principal da interface
    # ------------------------------------------------------------------
    root.mainloop()


if __name__ == "__main__":
    main()
