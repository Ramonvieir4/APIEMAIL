import smtplib
from email.message import EmailMessage
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

app = FastAPI(title="API de Cobrança de Documentos - LGOIS")

# Configurações do Servidor SMTP do Gmail
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465  # Porta com SSL para o Gmail
SENDER_EMAIL = "ramonvieira2711@gmail.com"
SENDER_PASSWORD = "fxuhayndhukagcsq"  # Sua senha de app de 16 dígitos do Google


class CobrancaRequest(BaseModel):
    cliente_nome: str
    cliente_emails: List[EmailStr]  # Aceita um ou vários e-mails
    documentos_faltantes: str


@app.post("/enviar-cobranca/")
def enviar_email_cobranca(dados: CobrancaRequest):
    msg = EmailMessage()
    msg["Subject"] = "Pendente: Falta de documentos para liberação - LGOIS"
    msg["From"] = SENDER_EMAIL
    
    # Junta múltiplos e-mails separados por vírgula para o envio
    msg["To"] = ", ".join(dados.cliente_emails)
    
    # E-mail de resposta configurado para a LGOIS
    msg["Reply-To"] = "imp.exp@lgois.com.br"

    corpo_mensagem = f"""Prezado(a) {dados.cliente_nome}, tudo bem?

Identificamos pendências de documentação em seu processo junto à LGOIS. Para darmos continuidade aos trâmites operacionais e liberação, solicitamos o envio urgente dos seguintes documentos faltantes:

• {dados.documentos_faltantes}

Por favor, responda diretamente a este e-mail anexando os arquivos solicitados o mais breve possível.

Atenciosamente,
Setor Operacional | LGOIS
"""
    msg.set_content(corpo_mensagem)

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        
        return {
            "status": "sucesso", 
            "mensagem": f"E-mail de cobrança enviado com sucesso para os destinatários!"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao enviar e-mail via Gmail: {str(e)}"
        )