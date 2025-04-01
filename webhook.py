from flask import Flask, request
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)
ARQUIVO_CSV = "gastos.csv"

# Carrega ou cria o arquivo
if os.path.exists(ARQUIVO_CSV):
    df = pd.read_csv(ARQUIVO_CSV)
else:
    df = pd.DataFrame(columns=["data", "valor", "item"])

@app.route("/webhook", methods=["POST"])
def webhook():
    mensagem = request.form.get("Body")
    try:
        valor_str, item = mensagem.split(" - ")
        valor = float(valor_str.replace(",", "."))
        data_envio = datetime.now().strftime("%Y-%m-%d %H:%M")

        global df
        df.loc[len(df)] = [data_envio, valor, item.strip()]
        df.to_csv(ARQUIVO_CSV, index=False)

        return "Registrado com sucesso", 200
    except:
        return "Formato inválido. Use: 32,90 - Estacionamento", 200

@app.route("/", methods=["GET"])
def hello():
    return "Webhook ativo!", 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
