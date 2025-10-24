import subprocess
import threading
import os
from datetime import datetime
from tkinter import Tk, Label, Button, filedialog, messagebox, ttk
import platform

# === Caminhos base ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TABULADOR_PATH = os.path.join(BASE_DIR, "tabulador_evol.py")
LEITOR_PATH = os.path.join(BASE_DIR, "leitor_json.py")

PASTA_SAIDA_CSV = os.path.join(BASE_DIR, "deposito_csv")
PASTA_SAIDA_JSON = os.path.join(BASE_DIR, "deposito_json")

# Garante que as pastas de saída existam
os.makedirs(PASTA_SAIDA_CSV, exist_ok=True)
os.makedirs(PASTA_SAIDA_JSON, exist_ok=True)


# === Funções ===
def executar_script(script_path, entrada, saida):
    """Executa o script Python em subprocesso separado, multiplataforma"""
    python_cmd = "python3" if platform.system() != "Windows" else "python"
    comando = [python_cmd, script_path, entrada, saida]
    subprocess.run(comando)


def rodar_tabulador(progress_bar):
    """Seleciona CSV de qualquer pasta e executa tabulador — gera apenas JSON"""
    arquivo_entrada = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
    if not arquivo_entrada:
        messagebox.showwarning("⚠️", "Nenhum CSV selecionado.")
        return

    nome_saida = f"evolucoes_tabuladas_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    arquivo_saida_json = os.path.join(PASTA_SAIDA_JSON, f"{nome_saida}.json")

    progress_bar["value"] = 0
    progress_bar.update()

    threading.Thread(target=executar_script, args=(TABULADOR_PATH, arquivo_entrada, arquivo_saida_json)).start()

    progress_bar["value"] = 100
    progress_bar.update()
    messagebox.showinfo("✅", f"Processamento iniciado.\nSaída esperada:\n\n{arquivo_saida_json}")


def rodar_leitor_json(progress_bar):
    """Seleciona JSON de qualquer pasta e executa leitor"""
    arquivo_entrada = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
    if not arquivo_entrada:
        messagebox.showwarning("⚠️", "Nenhum JSON selecionado.")
        return

    nome_saida = f"json_convertido_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    arquivo_saida_csv = os.path.join(PASTA_SAIDA_CSV, nome_saida)

    progress_bar["value"] = 0
    progress_bar.update()

    threading.Thread(target=executar_script, args=(LEITOR_PATH, arquivo_entrada, arquivo_saida_csv)).start()

    progress_bar["value"] = 100
    progress_bar.update()
    messagebox.showinfo("✅", f"Conversão iniciada.\nSaída esperada em:\n\n{arquivo_saida_csv}")


# === Interface ===
def criar_interface():
    root = Tk()
    root.title("tabulador automatico")
    root.geometry("600x400")
    root.resizable(False, False)

    Label(root, text="tabulador automatico", font=("Arial", 16, "bold")).pack(pady=25)

    progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
    progress_bar.pack(pady=10)

    Button(
        root,
        text="1️⃣ Selecionar CSV e Extrair Texto",
        font=("Arial", 12, "bold"),
        command=lambda: rodar_tabulador(progress_bar)
    ).pack(pady=20)

    Button(
        root,
        text="2️⃣ Selecionar JSON e Gerar CSV Final",
        font=("Arial", 12, "bold"),
        command=lambda: rodar_leitor_json(progress_bar)
    ).pack(pady=20)

    Label(root, text="Saídas automáticas em /deposito_csv e /deposito_json", font=("Arial", 10)).pack(pady=5)
    Label(root, text="🐯🐯🐯").pack(side="bottom", pady=15)

    root.mainloop()


# === Execução ===
if __name__ == "__main__":
    criar_interface()