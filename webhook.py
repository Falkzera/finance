from flask import Flask, request
import pandas as pd
from datetime import datetime
import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

app = Flask(__name__)
ARQUIVO_CSV = "gastos.csv"
PASTA_ID = "1JOdQyFd3fgDZst1GeaTP6HFRHi3L5BDB"  # <-- ID da pasta no Google Drive

# Tenta carregar o CSV existente
if os.path.exists(ARQUIVO_CSV):
    df = pd.read_csv(ARQUIVO_CSV)
else:
    df = pd.DataFrame(columns=["data", "valor", "item"])

# Função para fazer upload/atualização do arquivo no Google Drive
def upload_to_drive(arquivo):
    try:
        credentials_info = json.loads(os.environ["GOOGLE_CREDENTIALS"])
        creds = Credentials.from_service_account_info(
            credentials_info, scopes=["https://www.googleapis.com/auth/drive"]
        )
        drive_service = build("drive", "v3", credentials=creds)

        # Verifica se já existe o arquivo na pasta
        query = f"name='{arquivo}' and '{PASTA_ID}' in parents and mimeType='text/csv'"
        response = drive_service.files().list(q=query, fields="files(id, name)").execute()
        arquivos = response.get("files", [])

        media = MediaFileUpload(arquivo, mimetype="text/csv", resumable=True)

        if arquivos:
            file_id = arquivos[0]["id"]
            drive_service.files().update(fileId=file_id, media_body=media).execute()
            print("✅ Arquivo atualizado no Google Drive.")
        else:
            file_metadata = {
                "name": arquivo,
                "parents": [PASTA_ID],
                "mimeType": "text/csv"
            }
            drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
            print("✅ Arquivo criado no Google Drive.")

    except Exception as e:
        print(f"❌ Erro ao enviar para o Drive: {e}")

# Rota principal do webhook (Twilio envia POST aqui)
@app.route("/webhook", methods=["POST"])
def webhook():
    mensagem = request.form.get("Body")
    print("📩 Mensagem recebida:", mensagem)

    try:
        valor_str, item = mensagem.split(" - ")
        valor = float(valor_str.replace(",", "."))
        data_envio = datetime.now().strftime("%Y-%m-%d %H:%M")

        global df
        df.loc[len(df)] = [data_envio, valor, item.strip()]
        df.to_csv(ARQUIVO_CSV, index=False)

        upload_to_drive(ARQUIVO_CSV)

        return "✅ Gasto registrado com sucesso!", 200
    except Exception as e:
        print("❌ Erro ao processar mensagem:", e)
        return "⚠️ Formato inválido. Use: 32,90 - Estacionamento", 200

# Rota de teste (GET na raiz)
@app.route("/", methods=["GET"])
def hello():
    return "🚀 Webhook ativo e esperando mensagens do Twilio!", 200

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
