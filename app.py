"""
GeoHouse - inicializador unico.

Sobe o BACKEND (FastAPI/uvicorn) e o FRONTEND (Vite/Vue) juntos, em um
unico comando. As credenciais do banco de dados sao lidas do arquivo .env.

Uso:
    python app.py

Encerrar:
    Ctrl + C  (derruba backend e frontend juntos)

Enderecos:
    Frontend : http://127.0.0.1:5173
    Backend  : http://127.0.0.1:8000
    Health   : http://127.0.0.1 :8000/api/health
"""
import os
import sys
import time
import signal
import threading
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"

# Permite importar os modulos do backend (main, database) por nome.
sys.path.insert(0, str(BACKEND_DIR))

API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = int(os.getenv("API_PORT", "8000"))


def banner():
    from database import db_config, db_status  # importado aqui ja com .env carregado

    cfg = db_config()
    senha = "*" * len(cfg["password"]) if cfg["password"] else "(vazia)"
    print("=" * 60)
    print("  GEOHOUSE - iniciando backend + frontend")
    print("=" * 60)
    print(f"  Banco   : {cfg['user']}@{cfg['host']}:{cfg['port']}/{cfg['database']}")
    print(f"  Senha   : {senha}")
    ok, erro = db_status()
    if ok:
        print("  Conexao : OK (banco conectado)")
    else:
        print(f"  Conexao : FALHOU -> {erro}")
        print("            A API vai responder com os dados locais de demonstracao.")
    print("-" * 60)
    print(f"  Frontend: http://{API_HOST}:5173")
    print(f"  Backend : http://{API_HOST}:{API_PORT}")
    print(f"  Health  : http://{API_HOST}:{API_PORT}/api/health")
    print("=" * 60)
    print("  (Ctrl + C para encerrar tudo)")
    print()


def iniciar_backend():
    """Roda o uvicorn em uma thread separada e devolve o servidor."""
    import uvicorn

    config = uvicorn.Config(
        "main:app",
        host=API_HOST,
        port=API_PORT,
        log_level="info",
        reload=False,
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, name="backend", daemon=True)
    thread.start()
    return server, thread


def iniciar_frontend():
    """Roda 'npm run dev' (Vite) como processo filho."""
    npm = "npm.cmd" if os.name == "nt" else "npm"
    return subprocess.Popen([npm, "run", "dev"], cwd=str(ROOT))


def encerrar_frontend(proc: subprocess.Popen):
    if proc.poll() is not None:
        return
    try:
        if os.name == "nt":
            # Mata a arvore de processos do npm/node no Windows.
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            proc.terminate()
    except Exception:  # noqa: BLE001
        proc.kill()


def main():
    banner()

    server, back_thread = iniciar_backend()
    # Pequena espera para o backend subir antes do frontend.
    time.sleep(1.5)
    front = iniciar_frontend()

    try:
        # Mantem vivo enquanto os dois lados estiverem rodando.
        while True:
            if front.poll() is not None:
                print("\n[app] Frontend encerrou. Derrubando backend...")
                break
            if not back_thread.is_alive():
                print("\n[app] Backend encerrou. Derrubando frontend...")
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[app] Encerrando (Ctrl+C)...")
    finally:
        server.should_exit = True
        encerrar_frontend(front)
        back_thread.join(timeout=5)
        print("[app] Tudo encerrado.")


if __name__ == "__main__":
    main()
