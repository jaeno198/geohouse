"""
Cria usuarios ficticios no banco, um para cada papel (role) do sistema:
admin, corretor, proprietario e cliente.

As senhas sao gravadas com hash bcrypt na coluna senha_hash.
O script e idempotente: rodar de novo apenas atualiza os mesmos usuarios
(identificados pelo e-mail, que e unico).

Uso:
    python backend/seed_usuarios.py
"""
import sys
from pathlib import Path

import bcrypt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from database import get_connection  # noqa: E402

# (nome, email, senha, tipo, telefone, creci)
USUARIOS = [
    ("Administrador GeoHouse", "admin@geohouse.com",        "Admin@123",    "admin",        "(44) 99999-0001", None),
    ("Carla Corretora",        "corretor@geohouse.com",     "Corretor@123", "corretor",     "(44) 99999-0002", "CRECI-PR 12345"),
    ("Paulo Proprietario",     "proprietario@geohouse.com", "Prop@123",     "proprietario", "(44) 99999-0003", None),
    ("Cliente Teste",          "cliente@geohouse.com",      "Cliente@123",  "cliente",      "(44) 99999-0004", None),
]

UPSERT = """
INSERT INTO usuarios (nome, email, senha_hash, tipo, telefone, creci, ativo, criado_em, atualizado_em)
VALUES (%s, %s, %s, %s, %s, %s, 1, NOW(), NOW())
ON DUPLICATE KEY UPDATE
    nome = VALUES(nome),
    senha_hash = VALUES(senha_hash),
    tipo = VALUES(tipo),
    telefone = VALUES(telefone),
    creci = VALUES(creci),
    ativo = 1,
    atualizado_em = NOW()
"""


def hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def main():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for nome, email, senha, tipo, telefone, creci in USUARIOS:
                cur.execute(UPSERT, (nome, email, hash_senha(senha), tipo, telefone, creci))
        conn.commit()
    finally:
        conn.close()

    print("Usuarios criados/atualizados:\n")
    print(f"{'PAPEL (role)':<14} {'LOGIN (e-mail)':<28} SENHA")
    print("-" * 60)
    for nome, email, senha, tipo, _tel, _creci in USUARIOS:
        print(f"{tipo:<14} {email:<28} {senha}")


if __name__ == "__main__":
    main()
