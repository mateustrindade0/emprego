"""
DataStore — Camada de persistência do Meu Emprego.

Responsabilidades:
- Centralizar acesso aos dados das candidaturas.
- Tentar usar MongoDB Atlas como backend principal.
- Fazer fallback automático para CSV (`assets/candidaturas.csv`) se o Mongo falhar.
- Garantir consistência entre campos (empresa, cargo, data, tipo, status, observacoes, link).
"""

import csv
import os
import datetime
from pathlib import Path
from typing import List, Dict, Optional

from dotenv import load_dotenv

# Tenta importar MongoDB caso de erro vai para CSV
try:
    from pymongo import MongoClient
    PYMONGO_AVAILABLE = True
except Exception:
    PYMONGO_AVAILABLE = False


# Campos base da aplicação
CSV_FIELDS = [
    "empresa",
    "cargo",
    "data",
    "tipo",
    "status",
    "observacoes",
    "link",
]


class DataStore:
    """
    Persistência unificada: MongoDB (primário) ou CSV (fallback).
    A aplicação usa sempre os mesmos métodos independentemente do backend.
    """

    def __init__(self, mongo_uri: str = None, db_name: str = "meu_emprego"):
        # Carrega variáveis do .env
        load_dotenv()

        # URI definida pelo .env 
        self.mongo_uri = mongo_uri or os.getenv("MEU_EMPREGO_MONGO_URI")
        self.db_name = db_name

        # Caminho do CSV para fallback caso a conexão com Mongo falhe
        self.csv_path = Path(
            os.getenv("CANDIDATURAS_CSV_PATH", "assets/candidaturas.csv")
        )

        self.client = None
        self.db = None
        self.use_mongo: bool = False

        self._connect_mongo()
        self._ensure_csv()

    # ----------------------------------------------------------------------
    # MONGO
    # ----------------------------------------------------------------------
    def _connect_mongo(self):
        """
        Tenta conectar no MongoDB.
        Se falhar, ativa fallback para CSV sem quebrar o app.
        """

        if not (PYMONGO_AVAILABLE and self.mongo_uri):
            self.use_mongo = False
            return

        try:
            self.client = MongoClient(
                self.mongo_uri,
                serverSelectionTimeoutMS=6000,
            )
            self.client.server_info()

            self.db = self.client[self.db_name]
            self.use_mongo = True

        except Exception as e:
            print("\n[ERRO MONGO] Falha ao conectar:", e, "\n")
            self.client = None
            self.db = None
            self.use_mongo = False

    def test_connection(self) -> Dict[str, str]:
        """Usado pelo botão 🌐 na UI."""
        if not self.mongo_uri:
            return {"ok": False, "msg": "Nenhuma URI configurada"}

        if not PYMONGO_AVAILABLE:
            return {"ok": False, "msg": "pymongo não instalado"}

        try:
            info = self.client.server_info()
            return {"ok": True, "server": info.get("version", "?")}
        except Exception as e:
            return {"ok": False, "msg": str(e)}

    # ----------------------------------------------------------------------
    # CSV fallback
    # ----------------------------------------------------------------------
    def _ensure_csv(self):
        """Cria o CSV caso não exista ou arruma cabeçalho incorreto."""
        if not self.csv_path.exists():
            self.csv_path.parent.mkdir(parents=True, exist_ok=True)
            with self.csv_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(CSV_FIELDS)
            return

        # garantir cabeçalho correto
        with self.csv_path.open("r", encoding="utf-8") as f:
            lines = f.readlines()

        if not lines or "empresa" not in lines[0].lower():
            with self.csv_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(CSV_FIELDS)

    # ----------------------------------------------------------------------
    # INSERT
    # ----------------------------------------------------------------------
    def insert_candidatura(self, doc: Dict) -> Dict:
        """
        Insere uma candidatura no Mongo (se disponível) E sempre no CSV para backup.
        """

        # converter datas para datetime no Mongo
        doc_mongo = doc.copy()
        if isinstance(doc_mongo.get("data"), str):
            try:
                doc_mongo["data"] = datetime.datetime.fromisoformat(doc_mongo["data"])
            except Exception:
                pass

        # Sempre salva no CSV (backup)
        self._ensure_csv()
        data_str = doc.get("data", "")
        if data_str:
            try:
                y, m, d = data_str.split('-')
                data_str = f"{d}-{m}-{y}"
            except:
                pass
        with self.csv_path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                doc.get("empresa", ""),
                doc.get("cargo", ""),
                data_str,
                doc.get("tipo", ""),
                doc.get("status", ""),
                doc.get("observacoes", ""),
                doc.get("link", ""),
            ])

        # MongoDB (se disponível)
        if self.use_mongo:
            try:
                res = self.db["candidaturas"].insert_one(doc_mongo)
                return {"ok": True, "id": str(res.inserted_id), "backend": "mongo+csv"}
            except Exception:
                self.use_mongo = False  # desativa mongo, mas CSV já foi salvo

        return {"ok": True, "backend": "csv"}

    # ----------------------------------------------------------------------
    # READ
    # ----------------------------------------------------------------------
    def list_candidaturas(
        self,
        limit: Optional[int] = None,
        order_by_date_desc: bool = True,
    ) -> List[Dict]:
        """
        Lista registros do Mongo ou CSV.
        """

        # ------------------ MONGO ------------------
        if self.use_mongo:
            try:
                cursor = self.db["candidaturas"].find()

                if order_by_date_desc:
                    cursor = cursor.sort("data", -1)
                if limit:
                    cursor = cursor.limit(limit)

                items = []
                for d in cursor:
                    dt = d.get("data")
                    if hasattr(dt, "isoformat"):
                        dt = dt.isoformat()
                        # DD-MM-YYYY
                        if dt:
                            try:
                                y, m, d = dt.split('-')
                                dt = f"{d}-{m}-{y}"
                            except:
                                pass

                    items.append({
                        "empresa": d.get("empresa", ""),
                        "cargo": d.get("cargo", ""),
                        "data": dt or "",
                        "tipo": d.get("tipo", ""),
                        "status": d.get("status", ""),
                        "observacoes": d.get("observacoes", ""),
                        "link": d.get("link", ""),
                    })

                return items

            except Exception:
                self.use_mongo = False  # falhou → CSV

        # ------------------ CSV ------------------
        self._ensure_csv()

        items = []
        with self.csv_path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if any(row.values()):
                    items.append(row)

        # normalização
        for r in items:
            for field in CSV_FIELDS:
                r[field] = r.get(field, "")

        # ordenação por data
        try:
            def date_key(x):
                d_str = x.get("data", "")
                try:
                    d, m, y = d_str.split('-')
                    return datetime.date(int(y), int(m), int(d))
                except:
                    return datetime.date.min
            items.sort(key=date_key, reverse=order_by_date_desc)
        except Exception:
            pass

        if limit:
            return items[:limit]

        return items
