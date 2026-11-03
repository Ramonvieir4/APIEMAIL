from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr
from typing import List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = FastAPI(title="LGOIS API de Cobrança")

# Configurações fixas do seu e-mail de envio
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_REMETENTE = "ramonvieira2711@gmail.com"
EMAIL_SENHA = "fxuhayndhukagcsq"

class CobrancaRequest(BaseModel):
    cliente_nome: str
    cliente_emails: List[EmailStr]
    documentos_faltantes: str

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cobrança de Documentos - LGOIS</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f7f6; margin: 0; padding: 50px; display: flex; justify-content: center; }
            .container { background: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); width: 100%; max-width: 500px; }
            h2 { color: #333; margin-bottom: 20px; text-align: center; }
            label { font-weight: bold; color: #555; display: block; margin-top: 15px; }
            input, textarea { width: 100%; padding: 10px; margin-top: 5px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
            textarea { resize: vertical; height: 80px; }
            small { color: #666; display: block; margin-top: 3px; }
            button { background-color: #28a745; color: white; border: none; padding: 12px; width: 100%; border-radius: 4px; font-size: 16px; cursor: pointer; margin-top: 20px; }
            button:hover { background-color: #218838; }
            #mensagem { margin-top: 15px; padding: 10px; border-radius: 4px; text-align: center; display: none; }
            .sucesso { background-color: #d4edda; color: #155724; }
            .erro { background-color: #f8d7da; color: #721c24; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Cobrança LGOIS</h2>
            <label for="cliente_nome">Nome do Cliente / Empresa:</label>
            <input type="text" id="cliente_nome" placeholder="Ex: Importadora Exemplo Ltda">
            <label for="cliente_email">E-mail(s) do Cliente:</label>
            <input type="text" id="cliente_email" placeholder="email1@empresa.com, email2@empresa.com">
            <small>Separe múltiplos e-mails com vírgula.</small>
            <label for="documentos_faltantes">Documentos Faltantes:</label>
            <textarea id="documentos_faltantes">BL, Notas Fiscais de Entrada e Saída, e Parecer</textarea>
            <button onclick="enviarCobranca()">Enviar Cobrança</button>
            <div id="mensagem"></div>
        </div>
        <script>
            async function enviarCobranca() {
                const nome = document.getElementById('cliente_nome').value;
                const emailsTexto = document.getElementById('cliente_email').value;
                const documentos = document.getElementById('documentos_faltantes').value;
                const divMensagem = document.getElementById('mensagem');

                if (!nome || !emailsTexto || !documentos) {
                    divMensagem.style.display = 'block';
                    divMensagem.className = 'erro';
                    divMensagem.innerText = 'Por favor, preencha todos os campos!';
                    return;
                }

                const listaEmails = emailsTexto.split(',').map(e => e.trim());
                divMensagem.style.display = 'block';
                divMensagem.className = 'sucesso';
                divMensagem.innerText = 'A enviar e-mail...';

                try {
                    const resposta = await fetch('/enviar-cobranca/', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ cliente_nome: nome, cliente_emails: listaEmails, documentos_faltantes: documentos })
                    });
                    const resultado = await resposta.json();
                    if (resposta.ok) {
                        divMensagem.className = 'sucesso';
                        divMensagem.innerText = 'E-mail de cobrança enviado com sucesso!';
                    } else {
                        divMensagem.className = 'erro';
                        divMensagem.innerText = 'Erro: ' + (resultado.detail || 'Não foi possível enviar.');
                    }
                } catch (error) {
                    divMensagem.style.display = 'block';
                    divMensagem.className = 'erro';
                    divMensagem.innerText = 'Erro de conexão com o servidor na nuvem.';
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/enviar-cobranca/")
def enviar_cobranca(dados: CobrancaRequest):
    try:
        assunto = f"PENDÊNCIA DE DOCUMENTOS - {dados.cliente_nome}"
        corpo = f"""Prezados,

Informamos que constam pendências de documentos referentes à empresa {dados.cliente_nome}.

Documentos solicitados:
{dados.documentos_faltantes}

Solicitamos a regularização com brevidade.

Atenciosamente,
Equipe LGOIS
"""
        msg = MIMEMultipart()
        msg['From'] = EMAIL_REMETENTE
        msg['To'] = ", ".join(dados.cliente_emails)
        msg['Subject'] = assunto
        msg.attach(MIMEText(corpo, 'plain'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as servidor:
            servidor.starttls()
            servidor.login(EMAIL_REMETENTE, EMAIL_SENHA)
            servidor.sendmail(EMAIL_REMETENTE, dados.cliente_emails, msg.as_string())

        return {"status": "sucesso", "mensagem": "E-mails enviados com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    