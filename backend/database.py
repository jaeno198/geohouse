"""
Conexao com o banco de dados MariaDB/MySQL.

Todas as credenciais sao lidas do arquivo .env na raiz do projeto
(nunca ficam fixas no codigo). Veja o .env:

    DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
"""
import os
from pathlib import Path

import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

# .env fica na raiz deste repositorio (mesma pasta deste arquivo).
# No deploy (Render) as variaveis vem do ambiente; load_dotenv nao sobrescreve.
ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(ROOT_DIR / ".env")


def db_config() -> dict:
    """Monta a configuracao de conexao a partir do .env."""
    return {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", ""),
        "charset": "utf8mb4",
        "connect_timeout": 8,
        "cursorclass": DictCursor,
    }


def get_connection():
    """Abre uma nova conexao com o banco. Lanca excecao se falhar."""
    return pymysql.connect(**db_config())


def db_status() -> tuple[bool, str | None]:
    """Testa a conexao. Retorna (ok, mensagem_de_erro)."""
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
            return True, None
        finally:
            conn.close()
    except Exception as exc:  # noqa: BLE001
        return False, f"{type(exc).__name__}: {exc}"


def query(sql: str, params: tuple | None = None) -> list[dict]:
    """Executa um SELECT e devolve a lista de linhas como dicionarios."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return list(cur.fetchall())
    finally:
        conn.close()