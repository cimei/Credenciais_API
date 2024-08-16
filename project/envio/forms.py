"""

.. topic:: **Consultas (formulários)**

   Formulários:

   * PeriodoForm: para que o usuário informe o intervalo de datas para resgatar registros

"""

from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField, StringField, BooleanField, IntegerField,\
                    FieldList, FormField, Form, SelectField

from wtforms.validators import DataRequired, Email

   
class RegistroForm(FlaskForm):

    email        = StringField('E-mail: ', validators=[DataRequired(message="Informe seu e-mail registrado!"),Email()])
    admin        = BooleanField('Admin?')
    disabled     = BooleanField('Desabilitado?')
    ref          = SelectField('Ref.: ', choices=[('',''),('SIAPE', 'SIAPE'), ('SIORG', 'SIORG')])
    autorizadora = IntegerField('Autorizadora')
    password     = PasswordField('Senha: ', validators=[DataRequired(message="Informe sua senha!")])
    
    submit   = SubmitField('Registrar') 
    
class CredenciaisForm(Form):
    sel          = BooleanField(default=False)
    linha        = StringField()
    nome         = StringField()
    email        = StringField()
    sistema      = StringField()
    ref          = StringField()
    autorizadora = StringField()
    orgao        = StringField()

class TriagemForm(FlaskForm):
    
    credenciais = FieldList(FormField(CredenciaisForm))

    submit     = SubmitField('Registrar')