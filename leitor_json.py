import json
import pandas as pd
import sys
from tkinter import Tk, Button, Label, filedialog, messagebox


def carregar_json_para_df(caminho_json):
    """Lê o arquivo JSON e retorna um DataFrame."""
    with open(caminho_json, "r", encoding="utf-8") as f:
        dados = json.load(f)

    if not isinstance(dados, list) or not all(isinstance(item, dict) for item in dados):
        raise ValueError("O JSON deve conter uma lista de objetos (evoluções).")

    return pd.DataFrame(dados)


def salvar_csv(df, caminho_saida):
    """Salva o DataFrame em CSV."""
    df.to_csv(caminho_saida, index=False, encoding="utf-8-sig")
    print(f"✅ CSV salvo em: {caminho_saida}")


# === MODO AUTOMÁTICO (chamado pelo app.py) ===
def rodar_leitura_automatica(caminho_json, caminho_csv):
    print(f"📂 Lendo JSON: {caminho_json}")
    df = carregar_json_para_df(caminho_json)
    salvar_csv(df, caminho_csv)
    print(f"✅ Conversão concluída. {len(df)} linhas processadas.")


# === MODO INTERATIVO (manual) ===
def selecionar_arquivo_json():
    root = Tk()
    root.withdraw()
    arquivo = filedialog.askopenfilename(
        title="Selecione o arquivo JSON com evoluções tabuladas",
        filetypes=[("Arquivos JSON", "*.json")]
    )
    return arquivo


def salvar_como_csv(df):
    caminho = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        title="Salvar como CSV"
    )
    if caminho:
        df.to_csv(caminho, index=False, encoding="utf-8-sig")
        messagebox.showinfo("✅ Sucesso", f"Arquivo salvo em:\n{caminho}")


def abrir_json_como_dataframe():
    arquivo = selecionar_arquivo_json()
    if not arquivo:
        messagebox.showwarning("⚠️", "Nenhum arquivo selecionado.")
        return

    try:
        df = carregar_json_para_df(arquivo)
        print("\n📊 Preview das 5 primeiras linhas:")
        print(df.head())

        if messagebox.askyesno("Exportar", "Deseja exportar para CSV?"):
            salvar_como_csv(df)
    except Exception as e:
        messagebox.showerror("Erro ao carregar", f"Erro ao processar JSON:\n{str(e)}")


def iniciar_interface():
    janela = Tk()
    janela.title("📂 Leitor de JSON de Evoluções Tabuladas")
    janela.geometry("460x180")

    Label(janela, text="🔍 Abrir e exportar JSON de evoluções médicas", font=("Arial", 11)).pack(pady=10)
    Button(janela, text="Selecionar e Carregar JSON", command=abrir_json_como_dataframe, width=30, height=2).pack(pady=20)
    Label(janela, text="Versão: Leitor JSON 2.0", font=("Arial", 8), fg="gray").pack(side="bottom", pady=10)

    janela.mainloop()


# === EXECUÇÃO PRINCIPAL ===
if __name__ == "__main__":
    # Se for chamado pelo app.py com argumentos
    if len(sys.argv) >= 3:
        caminho_json = sys.argv[1]
        caminho_csv = sys.argv[2]
        rodar_leitura_automatica(caminho_json, caminho_csv)
    else:
        # Modo manual (interface)
        iniciar_interface()
