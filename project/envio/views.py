"""
.. topic:: Envio (views)

    Procedimentos relacionados ao envio de dados (planos e atividades) ao orgão superior.


.. topic:: Funções


.. topic:: Ações relacionadas ao envio

    * envio_i: Auxiliar para montagem do menu em cascata


"""

# views.py na pasta envio

from flask import render_template,url_for,flash, redirect, request, Blueprint, abort

from project.envio.forms import RegistroForm, TriagemForm

import requests
import json
import os, sys
import re
import ast
import string, random

import os.path

import google.auth

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import base64
from email.message import EmailMessage



envio = Blueprint('envio',__name__, template_folder='templates')

# Se for modificar estes scopes, remova o arquivo /static/token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/gmail.send"]

# O ID da planilha google, alimentada pelo formulário
SAMPLE_SPREADSHEET_ID = os.getenv('SAMPLE_SPREADSHEET_ID')
# SAMPLE_SPREADSHEET_ID = "1VW09Mam8vAOl5XkgJGhTkOl2Yg3XgSkWUnpfZ3yLstk"
# Intervalo da planilha a ser resgatado
SAMPLE_RANGE_NAME = os.getenv('SAMPLE_RANGE_NAME')
# SAMPLE_RANGE_NAME     = "Respostas!A2:K500"

if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    # application_path = os.path.dirname(os.path.abspath(__file__))
    application_path = sys.path[0]
    

# funções

# gera uma senha aleatória

def gera_senha(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
    

# pega token de acesso à API 
def pega_token(): 

    user_api   = os.getenv('APIPGD_AUTH_USER')
    senha_api  = os.getenv('APIPGD_AUTH_PASSWORD')

    if user_api == None:
        user_api  = ''
        print ('** Não há admin configurado para acesso à API. ***')
    if senha_api == None:    
        senha_api = ''
        print ('** Não há senha do admin configurada para acesso à API. ***')
    
    string = 'grant_type=&username='+user_api+'&password='+senha_api+'&scope=&client_id=&client_secret='

    headers = {'Content-Type': "application/x-www-form-urlencoded", 'Accept': "application/json"}
    
    if os.getenv('APIPGD_URL')[-1] == '/': 
        api_url_login = os.getenv('APIPGD_URL') + 'token'
    else:
        api_url_login = os.getenv('APIPGD_URL') + '/token'

    try:
        response = requests.post(api_url_login, headers=headers ,data=json.dumps(string))
    except:
        print('** ERRO AO TENTAR CONECTAR COM A API **')
        flash('Não consegui conexão com a API, verifique se '+os.getenv('APIPGD_URL')+' está on line.','erro')
        abort(404) 

    rlogin_json = response.json()
        
    try:
        token = rlogin_json['access_token']
        # tipo =  rlogin_json['token_type'] 
    except:
         retorno_API = rlogin_json['detail']  
         print ('** RETORNO DA API: ',retorno_API)
         print ('** Valores informados:')
         print ('** API URL login: ', api_url_login)
         print ('** User API: ', user_api)
         print ('** Senha API: ', senha_api)
         
         flash('Não consegui pegar um token junto à API. '+retorno_API+'.','erro')
         abort(403)  
        
    return(token)
  

# função que gera lista de credenciais existentes na API
def lista_credenciais_API():
    
    if os.getenv('APIPGD_URL') != None and os.getenv('APIPGD_URL') != "" and \
       os.getenv('APIPGD_AUTH_USER') != None and os.getenv('APIPGD_AUTH_USER') != "" and \
       os.getenv('APIPGD_AUTH_PASSWORD') != None and os.getenv('APIPGD_AUTH_PASSWORD') != "":  

        # pega token de acesso à API de envio de dados
        
        token = pega_token()      

        head = {'Authorization': 'Bearer {}'.format(token)}

        r = requests.get(os.getenv('APIPGD_URL') + '/users', headers= head)

        # if r.ok:
        #     print('request ok')
            
        return r.text        
                
    else:
        return ('erro_credenciais')
    
      
# função que cria, ou altera, uma credencial na API
def put_credencial_API(dic_credencial,tipo):
    
    if os.getenv('APIPGD_URL') != None and os.getenv('APIPGD_URL') != "" and \
       os.getenv('APIPGD_AUTH_USER') != None and os.getenv('APIPGD_AUTH_USER') != "" and \
       os.getenv('APIPGD_AUTH_PASSWORD') != None and os.getenv('APIPGD_AUTH_PASSWORD') != "":  

        # pega token de acesso à API de envio de dados
        
        token = pega_token()
    
        headers = {'Content-Type': "application/json", 'Accept': "application/json", 'Authorization': 'Bearer {}'.format(token)}
                    
        # faz o put na API via dumps json do dicionário    
        r_put = requests.put(os.getenv('APIPGD_URL') + '/user/'+dic_credencial['email'], headers= headers, data=json.dumps(dic_credencial))

        if r_put.ok:
            if tipo == 'um':
                flash('Credencial registrada!','sucesso')
        else:
            retorno_API = re.search(r'\bmsg[\W|w]+[\w+\s]+',r_put.text) 

            if retorno_API:
                retorno_API_msg = retorno_API.group()[6:]
                flash (str(retorno_API_msg),'erro')
            else:
                flash ('*** Texto API: '+str(r_put.text),'erro')
                if str(r_put.text) == '{"detail":"Unauthorized"}':
                    abort(401)
                    
        return r_put.ok        
                
    else:
        return ('erro_credenciais')                

# Pega creds API google

def pega_creds():
    
    """Pega credenciais da API Google
    """
    
    credencial_google = os.path.join(application_path, 'credentials.json')
    token_google = os.path.join(application_path, 'token.json')
    
    creds = None

    if os.path.exists(token_google):
        creds = Credentials.from_authorized_user_file(token_google, SCOPES)
    # Se não tiver credencial google válida, abre browser para log in do usuário.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credencial_google, SCOPES)
            creds = flow.run_local_server(port=0)
            
            # Salva credenciais google no /static/token.json para próxio uso
            with open(token_google, "w") as token:
                token.write(creds.to_json())

    return creds

#
def gmail_send_message(conteudo, para, de, assunto):
    
    """Cria e envia um e-mail
    Faz o print do id da mensagem retornado
    Retorna: Objeto message, incluindo o message id

    """
    # creds = None

    # if os.path.exists('/static/token.json'):
    #     creds = Credentials.from_authorized_user_file('/static/token.json', SCOPES)
    # # If there are no (valid) credentials available, let the user log in.
    # if not creds or not creds.valid:
    #     if creds and creds.expired and creds.refresh_token:
    #         creds.refresh(Request())
    #     else:

    #         flow = InstalledAppFlow.from_client_secrets_file(
    #             "/static/credentials.json", SCOPES)
    #         creds = flow.run_local_server(port=0)
            
    #         # Save the credentials for the next run
    #         with open("/static/token.json", "w") as token:
    #             token.write(creds.to_json())

    creds = pega_creds()
    
    try:
        # Chama a API Gmail
        service = build("gmail", "v1", credentials=creds)
        message = EmailMessage()

        message.set_content(conteudo)

        message["To"] = para
        message["From"] = de
        message["Subject"] = assunto

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"raw": encoded_message}
        
        send_message = (
            service.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )
        print(f'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(f"An error occurred: {error}")
        send_message = None
    return send_message





## VIEWS

## registra credencial na API 

@envio.route('/registrar', methods=['GET','POST'])

def registrar():
    """
    +---------------------------------------------------------------------------------------+
    |Cria nova credencial na API.                                                           |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """
    
    # token = pega_token()
    
    form = RegistroForm()
    
    if form.validate_on_submit():
                
        dic_credencial = {}
        
        dic_credencial['email'] = form.email.data
        dic_credencial['is_admin'] = form.admin.data
        dic_credencial['disabled'] = form.disabled.data
        dic_credencial['origem_unidade'] = form.ref.data
        dic_credencial['cod_unidade_autorizadora'] = form.autorizadora.data
        dic_credencial['password'] = form.password.data 
        
        put_credencial_API(dic_credencial,'um')
    
    return render_template('registro.html', form = form, tipo = 'registrar')


## edita credencial na API 

@envio.route('/editar/<email>', methods=['GET','POST'])

def editar(email):
    """
    +---------------------------------------------------------------------------------------+
    |Edita nova credencial na API.                                                          |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """
    
    form = RegistroForm()
    
    if form.validate_on_submit():
        
        dic_credencial = {}
        
        dic_credencial['email'] = form.email.data
        dic_credencial['is_admin'] = form.admin.data
        dic_credencial['disabled'] = form.disabled.data
        dic_credencial['origem_unidade'] = form.ref.data
        dic_credencial['cod_unidade_autorizadora'] = form.autorizadora.data
        dic_credencial['password'] = form.password.data 
        
        put_credencial_API(dic_credencial,'um')
        
        return redirect(url_for('envio.listar'))
    
    token = pega_token()
    
    head = {'Authorization': 'Bearer {}'.format(token)}

    r = requests.get(os.getenv('APIPGD_URL') + '/user/' + email, headers= head)

    # if r.ok:
    #     print('request ok')
            
    credencial = ast.literal_eval(r.text.replace('[','').replace(']','').replace('false','"false"').replace('true','"true"'))
    
    form.email.data = email
    if credencial['is_admin'] == 'true':
        form.admin.data = True
    else:
        form.admin.data = False    
    if credencial['disabled'] == 'true':
        form.disabled.data = True
    else:
        form.disabled.data = False    
    form.ref.data = credencial['origem_unidade']
    form.autorizadora.data = credencial['cod_unidade_autorizadora']
    form.password.data = None
    
    return render_template('registro.html', form = form, tipo = 'editar')


## lista credenciais da API 

@envio.route('/listar')

def listar():
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta uma lista das credenciais cadastradas na API.                                |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """
    
    resultado = lista_credenciais_API()
    
    resultado_dict = ast.literal_eval(resultado.replace('[','').replace(']','').replace('false','"false"').replace('true','"true"'))

    return render_template('lista_credenciais.html', lista = resultado_dict)


## triagem para registro de credenciais em lote

@envio.route('/triagem_lote', methods=['GET','POST'])

def triagem_lote():
    """
    +---------------------------------------------------------------------------------------+
    |Prepara lista de credencias não processadas da planilha google.                        |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """
    
    creds = pega_creds()

    try:
        service = build("sheets", "v4", credentials=creds)

        # Chama a API google de planilhas
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
            .execute()
        )
        values = result.get("values", [])

        if not values:
            print("Nada encontrado na planilha google de origem.")
            return
        
    except HttpError as err:
        print(err)
        
    ### Varre a planilha para pegar não processados
    lista = []
    i = 1
    for row in values:
        i += 1
        if len(row) < 9:
            row.append(i)
            lista.append(row)
        elif len(row) >= 9 and row[8] == 'NÃO':
            row.append(i)
            lista.append(row)
            
    ## monta opções para credenciais no formulário
    credenciais = [{'linha':l[8],'sel':False,'nome':l[1],'email':l[2], 'sistema':l[3],'ref':l[5],'autorizadora':l[4],'orgao':l[7]} for l in lista]  
    dados = {'credenciais':credenciais}
    
    qtd_credenciais = len(credenciais)
    
    form = TriagemForm(data=dados)
    
    if form.validate_on_submit(): 
        
        qtd_processar = 0
        
        for field in form.credenciais:
            
            if field.sel.data == True:
                qtd_processar += 1
                                
                # Gera uma senha de 10 posições
                senha = gera_senha()
                                
                # Registra senha na planilha. 
                # Coluna I recebe NÃO, para indicar que a credencial ainda não foi criada na API
                # Coluna J recebe a senha da credencial 
                result = (service.spreadsheets().values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                                                 range='I'+str(field.linha.data)+':'+'J'+str(field.linha.data),
                                                                 valueInputOption='RAW',
                                                                 body={"values": [['NÃO',senha]]})
                                 .execute())
                
                # Inclui credencial na API
                
                dic_credencial = {}
        
                dic_credencial['email'] = field.email.data
                dic_credencial['is_admin'] = 'false'
                dic_credencial['disabled'] = 'false'
                dic_credencial['origem_unidade'] = field.ref.data
                dic_credencial['cod_unidade_autorizadora'] = field.autorizadora.data
                dic_credencial['password'] = senha 
                
                retorno = put_credencial_API(dic_credencial,'lote')
                
                if retorno:
                    # coloca status processado = SIM na planilha. Coluna I.
                    result = (service.spreadsheets().values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                                                 range='I'+str(field.linha.data),
                                                                 valueInputOption='RAW',
                                                                 body={"values": [['SIM']]})
                                 .execute())
                
                    # envia um e-mail para o solicitante da credencial
                    mensagem = 'Credenciais para a API: '+os.getenv('APIPGD_URL')+'\n'+'Credencial: ' + field.email.data + '. Senha: ' + senha + '.'
                    e_mail = gmail_send_message(mensagem, field.email.data, 'seges.cginf@gmail.com', 'Credencial para API do PGD IN 24 ('+field.orgao.data+')')
                    
                    # coloca o id do e-mail enviado na planilha. Coluna K.
                    result = (service.spreadsheets().values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                                                 range='K'+str(field.linha.data),
                                                                 valueInputOption='RAW',
                                                                 body={"values": [[e_mail["id"]]]})
                                 .execute())
                
                else:
                    print ('** Houve problema no processamento das solicitações da credencial para ',field.email.data, '!')    
                    flash('Houve problema no processamento das solicitações da credencial para '+field.email.data,'erro')
                    
            else:
                
                # coloca status processado = IGNORADA na planilha. Coluna I.
                result = (service.spreadsheets().values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                                                range='I'+str(field.linha.data),
                                                                valueInputOption='RAW',
                                                                body={"values": [['IGNORADA']]})
                                 .execute())   
                # envia um e-mail de recusa para o solicitante da credencial
                mensagem = 'A solicitação de credencial para a API: '+os.getenv('APIPGD_URL')+'\n'+'foi negada. Se desejar, solicite informações via pgd@gestao.gov.br.'
                e_mail = gmail_send_message(mensagem, field.email.data, 'seges.cginf@gmail.com', 'Credencial para API do PGD IN 24 ('+field.orgao.data+')')  
                
                # coloca o id do e-mail enviado na planilha. Coluna K.
                result = (service.spreadsheets().values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                                                range='K'+str(field.linha.data),
                                                                valueInputOption='RAW',
                                                                body={"values": [[e_mail["id"]]]})
                                 .execute()) 

        flash('Processamento das solicitações de credencial realizado.','sucesso')
                    
        return redirect (url_for('envio.triagem_lote'))
    
    return render_template ('triagem.html', lista = lista, form = form, qtd_credenciais = qtd_credenciais)    
    
    

## lista de solicitaçõe de credencial ignoradas

@envio.route('/lista_ignoradas')

def lista_ignoradas():
    """
    +---------------------------------------------------------------------------------------+
    |Lista as solicitações que foram ignoradas na planilha google.                          |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """
    
    creds = pega_creds()

    try:
        service = build("sheets", "v4", credentials=creds)

        # Chama a API google de planilhas
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME)
            .execute()
        )
        values = result.get("values", [])

        if not values:
            print("Nada encontrado na planilha google de origem.")
            return
        
        ### Varre a planilha para pegar ignorados
        lista = []
        i = 0
        for row in values:
            if len(row) >= 9 and row[8] == 'IGNORADA':
                i += 1
                lista.append(row)
                                 
    except HttpError as err:
        print(err)
    
    return render_template ('lista_ignoradas.html', lista = lista, qtd = i)


## renderiza tela do tratamento de solicitações em lote 

@envio.route('/lote')

def lote():
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta tela do tratamento de solicitações.                                          |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """
    
    return render_template('lote.html', admin = 'ok')          
