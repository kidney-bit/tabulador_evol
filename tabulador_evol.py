import os
import sys
import json
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from tqdm import tqdm
from tkinter import filedialog, Tk, messagebox

# === CONFIGURAÇÃO ===
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === PROMPT PADRONIZADO ===
PROMPT = """
Você é um assistente médico que recebe um texto de evolução clínica.
Sua tarefa é retornar um JSON puro, estruturado e padronizado, sem linguagem natural descritiva.
Use apenas as opções predefinidas abaixo. Se nada se aplica, use "outros".

Retorne um JSON exatamente neste formato:

{
  "comorbidades": ["HAS", "DM", "DRC", "ICC", "coronariopatia", "transplante de rim", "outros"],
  "motivo_internacao": ["IRA", "DRC", "Sepse", "Choque", "Descompensação cardiológica", "Acidose metabólica", "outros"],
  "medicamentos_continuos": ["IECA", "BRA", "Diurético", "Insulina", "Antibiótico", "Corticoide", "outros"],
  "sintomas": ["Dispneia", "Tosse", "Disúria", "Edema", "Oligúria", "Febre", "Dor", "Náusea", "outros"],
  "achados_exame_fisico": ["Hipotenso", "Edemaciado", "Taquipneico", "Anúrico", "outros"]
}

Regras:
- Liste apenas as categorias reconhecíveis (sem frases descritivas).
- Use sempre listas, mesmo que haja um único item.
- Nunca use texto corrido, diagnósticos compostos ou frases.
- Responda com JSON puro e válido (sem ``` ou comentários).

Texto:
"""

# === FUNÇÃO DE EXTRAÇÃO ===
def analisar_evolucao(texto):
    prompt = PROMPT + texto
    try:
        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você extrai categorias médicas em JSON puro, sem frases completas."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
        )
        conteudo = resposta.choices[0].message.content.strip()
        conteudo = conteudo.replace("```json", "").replace("```", "").strip()
        resultado = json.loads(conteudo)

        # Garante que todos os campos estejam presentes
        campos = ["comorbidades", "motivo_internacao", "medicamentos_continuos", "sintomas", "achados_exame_fisico"]
        for c in campos:
            if c not in resultado:
                resultado[c] = [] if c != "motivo_internacao" else ["outros"]
        return resultado

    except Exception as e:
        return {"erro": str(e), "obs": texto}


# === FUNÇÃO PRINCIPAL ===
def rodar_extracao(arquivo_csv, arquivo_json_saida):
    """Executa a análise do CSV e salva JSON/CSV de saída."""
    print(f"📂 Lendo arquivo: {arquivo_csv}")
    df = pd.read_csv(arquivo_csv)

    if "obs" not in df.columns:
        raise ValueError("A coluna 'obs' não foi encontrada no CSV.")

    resultados = []
    for _, linha in tqdm(df.iterrows(), total=len(df), desc="Analisando evoluções"):
        texto = str(linha["obs"]) if pd.notnull(linha["obs"]) else ""
        if len(texto.strip()) < 10:
            continue

        extracao = analisar_evolucao(texto)
        registro = linha.to_dict()
        registro.update(extracao)
        resultados.append(registro)

    # === Caminho CSV correspondente ===
    arquivo_csv_saida = os.path.splitext(arquivo_json_saida)[0] + ".csv"

    df_final = pd.DataFrame(resultados)
    # df_final.to_csv(arquivo_csv_saida, index=False, encoding="utf-8-sig")

    with open(arquivo_json_saida, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

    print(f"✅ Concluído: {len(resultados)} evoluções processadas.")
    print(f"🧾 CSV salvo em: {arquivo_csv_saida}")
    print(f"🧠 JSON salvo em: {arquivo_json_saida}")


# === EXECUÇÃO ===
if __name__ == "__main__":
    # Se o app.py chamar com argumentos, usa-os diretamente
    if len(sys.argv) >= 3:
        entrada = sys.argv[1]
        saida_json = sys.argv[2]
        rodar_extracao(entrada, saida_json)
    else:
        # Execução direta (modo manual)
        root = Tk()
        root.withdraw()
        arquivo = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if not arquivo:
            messagebox.showwarning("⚠️", "Nenhum CSV selecionado.")
            sys.exit()

        rodar_extracao(arquivo, "evolucoes_tabuladas.json")
        messagebox.showinfo("✅ Concluído", "Processamento finalizado e arquivos salvos.")
