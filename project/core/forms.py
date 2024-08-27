"""

.. topic:: Core (formulários)

   * ArquivoForm: permite escolher o arquivo para carga de dados.

**Campos definidos no formulário (todos são obrigatórios):**

"""

# forms.py dentro de core

from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField, StringField

from wtforms.validators import DataRequired, Email, URL

from wtforms.fields import URLField

class InformaAdminForm(FlaskForm):

    url_hom   = URLField('API Homologação: ', validators=[DataRequired(message="URL da API de homologação!"),URL()])
    url_prod  = URLField('API Produção: ', validators=[DataRequired(message="URL da API de produção!"),URL()])
    email     = StringField('E-mail: ', validators=[DataRequired(message="E-mail credencial admin!"),Email()])
    password  = PasswordField('Senha: ', validators=[DataRequired(message="Informe senha do admin!")])
    
    submit    = SubmitField('Enviar')   


