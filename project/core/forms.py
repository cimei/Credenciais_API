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

    url      = URLField('URL da API: ', validators=[DataRequired(message="URL da API!"),URL()])
    email    = StringField('E-mail: ', validators=[DataRequired(message="E-mail credencial admin!"),Email()])
    password = PasswordField('Senha: ', validators=[DataRequired(message="Informe senha do admin!")])
    
    submit   = SubmitField('Enviar')   


