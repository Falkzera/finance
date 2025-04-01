import json
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def authenticate_service_account():
    """
    Autentica no Google Drive usando credenciais do secrets.toml (Streamlit).
    """
    SCOPES = ['https://www.googleapis.com/auth/drive']
    credentials_info = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    credentials = Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
    return build('drive', 'v3', credentials=credentials)


import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_to_drive(arquivo):
    # ID da pasta no Google Drive
    pasta_id = "1JOdQyFd3fgDZst1GeaTP6HFRHi3L5BDB"

    # Autenticando com as credenciais do Render
    credentials_info = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    creds = Credentials.from_service_account_info(
        credentials_info, scopes=['https://www.googleapis.com/auth/drive']
    )
    drive_service = build('drive', 'v3', credentials=creds)

    # Verifica se já existe o arquivo com o mesmo nome na pasta
    query = f"name='{arquivo}' and '{pasta_id}' in parents and mimeType='text/csv'"
    response = drive_service.files().list(q=query, fields="files(id, name)").execute()
    arquivos = response.get("files", [])

    media = MediaFileUpload(arquivo, mimetype="text/csv", resumable=True)

    if arquivos:
        # Atualiza o arquivo existente
        file_id = arquivos[0]["id"]
        drive_service.files().update(fileId=file_id, media_body=media).execute()
        print("✅ Arquivo atualizado na pasta do Google Drive.")
    else:
        # Cria novo arquivo na pasta
        file_metadata = {
            "name": arquivo,
            "parents": [pasta_id],
            "mimeType": "text/csv"
        }
        drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        print("✅ Arquivo enviado para a pasta do Google Drive.")
