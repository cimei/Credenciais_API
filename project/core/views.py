"""
.. topic:: Core (views)

    Este é o módulo inicial do sistema.

    Apresenta as telas de início, informação e procedimentos de carga de dados em lote.

.. topic:: Funções

    * PegaArquivo: Faz o upload do arquivo desejado

.. topic:: Ações relacionadas aos bolsistas

    * index: Primeiro template chamado na inicialização do sistema. Reprograma agendamentos.
    * inicio: Tela inicial do sistema
    * info: Tela de informações

"""

# core/views.py

from flask import render_template,url_for,flash, redirect, request, Blueprint, send_from_directory

import os
from datetime import datetime as dt, date
import tempfile
from werkzeug.utils import secure_filename


from datetime import datetime

from project.core.forms import InformaAdminForm

from project.envio.views import pega_token

core = Blueprint("core",__name__)



@core.route('/informa_adm', methods=['GET','POST'])
def informa_adm():
    """+--------------------------------------------------------------------------------------+
       |Pede que o usuário informe dados de um admin da API                                   |
       +--------------------------------------------------------------------------------------+
    """
        
    form = InformaAdminForm()

    if form.validate_on_submit():
                    
        os.environ["APIPGD_URL"]           = form.url.data
        os.environ["APIPGD_AUTH_USER"]     = form.email.data
        os.environ["APIPGD_AUTH_PASSWORD"] = form.password.data
        
        pega_token()
        
        return render_template ('index.html', admin = 'ok')   
    
    if os.getenv("APIPGD_URL") != '' and os.getenv("APIPGD_URL") != None:
        form.url.data = os.getenv("APIPGD_URL")
        
    if os.getenv("APIPGD_AUTH_USER") != '' and os.getenv("APIPGD_AUTH_USER") != None:
        form.email.data = os.getenv("APIPGD_AUTH_USER")    
    
    return render_template('login.html',form=form)


@core.route('/')
def index():
    """
    +---------------------------------------------------------------------------------------+
    |Ações quando o aplicativo é colocado no ar.                                            |
    |Inicia jobs de envio e de reenvio conforme ultimo registro de agendamento no log.      |
    +---------------------------------------------------------------------------------------+
    """
    
    if os.getenv("APIPGD_AUTH_USER") != '' and os.getenv("APIPGD_AUTH_USER") != None:
        return render_template ('index.html', admin = 'ok')
    else:
        return render_template ('index.html', admin = 'ko')


@core.route('/inicio')
def inicio():
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta a tela inicial do aplicativo.                                                |
    +---------------------------------------------------------------------------------------+
    """

    if os.getenv("APIPGD_AUTH_USER") != '' and os.getenv("APIPGD_AUTH_USER") != None:
        return render_template ('index.html', admin = 'ok')
    else:
        return render_template ('index.html', admin = 'ko')

@core.route('/info')
def info():
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta a tela de informações do aplicativo.                                         |
    +---------------------------------------------------------------------------------------+
    """

    return render_template('info.html')







