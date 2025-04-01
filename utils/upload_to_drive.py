import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_to_drive(arquivo, pasta_id):
    print("⏫ Iniciando upload para o Drive...")

    try:
        credentials_info = json.loads(os.environ["GOOGLE_CREDENTIALS"])
        creds = Credentials.from_service_account_info(
            credentials_info, scopes=["https://www.googleapis.com/auth/drive"]
        )
        drive_service = build("drive", "v3", credentials=creds)

        # Verifica se já existe o arquivo na pasta
        query = f"name='{arquivo}' and '{pasta_id}' in parents and mimeType='text/csv'"
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
                "parents": [pasta_id],
                "mimeType": "text/csv"
            }
            drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
            print("✅ Arquivo criado no Google Drive.")
    except Exception as e:
        print("❌ Erro ao enviar para o Drive:", e)
