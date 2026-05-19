from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Miembro, TradeJournal, OKXApiConfig


class MiembroRegistroForm(forms.ModelForm):
    fecha_nacimiento = forms.DateField(
        input_formats=['%d/%m/%Y'],
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'dd/mm/aaaa',
        }),
        label='Fecha de Nacimiento',
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Contraseña',
        }),
        label='Contraseña',
        help_text='Mínimo 8 caracteres',
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirmar Contraseña',
        }),
        label='Confirmar Contraseña',
    )

    mercados = forms.MultipleChoiceField(
        choices=Miembro.MERCADO_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    plataformas = forms.MultipleChoiceField(
        choices=Miembro.PLATAFORMA_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    contenido_interes = forms.MultipleChoiceField(
        choices=Miembro.CONTENIDO_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Miembro
        fields = [
            'nombre', 'apellidos', 'fecha_nacimiento', 'pais', 'ciudad',
            'email', 'whatsapp', 'telegram', 'tiempo_interes', 'experiencia',
            'mercados', 'objetivo_principal', 'objetivo_otro', 'capital',
            'mayor_dificultad', 'dificultad_otro', 'plataformas',
            'plataforma_otro', 'contenido_interes', 'opera_broker',
            'broker_actual', 'broker_otro', 'interesado_herramientas',
            'interesado_eventos', 'interesado_sesiones_vivo',
            'interesado_ofertas', 'referral_source', 'referral_otro',
            'documento', 'acepta_terminos',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nombre', 'autocomplete': 'given-name'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Apellidos', 'autocomplete': 'family-name'}),
            'pais': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'País', 'autocomplete': 'country-name', 'list': 'paises-list'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ciudad', 'autocomplete': 'address-level2', 'list': 'ciudades-list'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'correo@ejemplo.com', 'autocomplete': 'email'}),
            'whatsapp': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+57 300 123 4567', 'autocomplete': 'tel'}),
            'telegram': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '@usuario', 'autocomplete': 'off'}),
            'tiempo_interes': forms.Select(attrs={'class': 'form-select', 'autocomplete': 'off'}),
            'experiencia': forms.Select(attrs={'class': 'form-select', 'autocomplete': 'off'}),
            'objetivo_principal': forms.Select(attrs={'class': 'form-select', 'autocomplete': 'off'}),
            'objetivo_otro': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Especificar', 'autocomplete': 'off'}),
            'capital': forms.Select(attrs={'class': 'form-select', 'autocomplete': 'off'}),
            'mayor_dificultad': forms.Select(attrs={'class': 'form-select', 'autocomplete': 'off'}),
            'dificultad_otro': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Especificar', 'autocomplete': 'off'}),
            'plataforma_otro': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Especificar', 'autocomplete': 'off'}),
            'contenido_interes': forms.CheckboxSelectMultiple(),
            'opera_broker': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'broker_actual': forms.Select(attrs={'class': 'form-select', 'autocomplete': 'off'}),
            'broker_otro': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Especificar', 'autocomplete': 'off'}),
            'interesado_herramientas': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'interesado_eventos': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'interesado_sesiones_vivo': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'interesado_ofertas': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'referral_source': forms.Select(attrs={'class': 'form-select', 'autocomplete': 'off'}),
            'referral_otro': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Especificar', 'autocomplete': 'off'}),
            'documento': forms.FileInput(attrs={'class': 'form-file', 'accept': '.pdf,.png,.jpg,.jpeg'}),
            'acepta_terminos': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
        labels = {
            'nombre': 'Nombre',
            'apellidos': 'Apellidos',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'pais': 'País',
            'ciudad': 'Ciudad',
            'email': 'Correo Electrónico',
            'whatsapp': 'Teléfono WhatsApp',
            'telegram': 'Usuario Telegram',
            'tiempo_interes': '¿Hace cuánto tiempo te interesa el trading?',
            'experiencia': 'Nivel de experiencia en trading',
            'mercados': '¿En qué mercados estás interesado?',
            'objetivo_principal': '¿Cuál es tu objetivo principal en el trading?',
            'objetivo_otro': 'Especificar otro objetivo',
            'capital': '¿Con qué capital cuentas actualmente para operar?',
            'mayor_dificultad': '¿Cuál es tu mayor dificultad actualmente?',
            'dificultad_otro': 'Especificar otra dificultad',
            'plataformas': '¿Tienes cuenta en alguna plataforma de trading?',
            'plataforma_otro': 'Especificar otra plataforma',
            'contenido_interes': '¿Qué tipo de contenido te interesa más?',
            'opera_broker': '¿Actualmente operas con algún broker o exchange?',
            'broker_actual': '¿Cuál utilizas actualmente?',
            'broker_otro': 'Especificar otro broker',
            'interesado_herramientas': '¿Te gustaría operar con las herramientas y brokers recomendados por la comunidad?',
            'interesado_eventos': '¿Te interesan eventos presenciales o virtuales?',
            'interesado_sesiones_vivo': '¿Te gustaría participar activamente en sesiones en vivo?',
            'interesado_ofertas': '¿Te gustaría recibir ofertas exclusivas, promociones o lanzamientos?',
            'referral_source': '¿Por dónde te enteraste de Creemos Capital?',
            'referral_otro': 'Especificar otra fuente',
            'documento': 'Adjunta tu foto (Documento o selfie, formato png, jpg o pdf)',
            'acepta_terminos': 'Aceptación de términos',
        }

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get('fecha_nacimiento')
        if fecha and fecha > __import__('datetime').date.today():
            raise forms.ValidationError('La fecha no puede ser futura.')
        return fecha

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Las contraseñas no coinciden.')

        if password and len(password) < 8:
            raise forms.ValidationError('La contraseña debe tener al menos 8 caracteres.')

        objetivo = cleaned_data.get('objetivo_principal')
        if objetivo == 'otro' and not cleaned_data.get('objetivo_otro'):
            self.add_error('objetivo_otro', 'Debes especificar tu objetivo.')

        dificultad = cleaned_data.get('mayor_dificultad')
        if dificultad == 'otro' and not cleaned_data.get('dificultad_otro'):
            self.add_error('dificultad_otro', 'Debes especificar tu dificultad.')

        plataformas = cleaned_data.get('plataformas')
        if plataformas and 'otro' in plataformas and not cleaned_data.get('plataforma_otro'):
            self.add_error('plataforma_otro', 'Debes especificar la plataforma.')

        broker = cleaned_data.get('broker_actual')
        if broker == 'otro' and not cleaned_data.get('broker_otro'):
            self.add_error('broker_otro', 'Debes especificar el broker.')

        referral = cleaned_data.get('referral_source')
        if referral == 'otro' and not cleaned_data.get('referral_otro'):
            self.add_error('referral_otro', 'Debes especificar la fuente.')

        if not cleaned_data.get('acepta_terminos'):
            self.add_error('acepta_terminos', 'Debes aceptar los términos para registrarte.')

        return cleaned_data

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['nombre'],
            last_name=self.cleaned_data['apellidos'],
        )

        miembro = super().save(commit=False)
        miembro.user = user
        miembro.rol = 'member'

        mercados = self.cleaned_data.get('mercados', [])
        miembro.mercados = ','.join(mercados) if mercados else ''

        plataformas = self.cleaned_data.get('plataformas', [])
        miembro.plataformas = ','.join(plataformas) if plataformas else ''

        contenido = self.cleaned_data.get('contenido_interes', [])
        miembro.contenido_interes = ','.join(contenido) if contenido else ''

        if commit:
            miembro.save()
        return miembro


class MiembroLoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'correo@ejemplo.com',
            'autofocus': True,
        }),
        label='Correo Electrónico',
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Contraseña',
        }),
        label='Contraseña',
    )


class TradeJournalForm(forms.ModelForm):
    class Meta:
        model = TradeJournal
        fields = [
            'fecha', 'hora_entrada', 'hora_salida', 'par', 'mercado', 'tipo',
            'estrategia', 'estrategia_otro', 'precio_entrada', 'precio_salida',
            'stop_loss', 'take_profit', 'lotes', 'resultado', 'pnl', 'pnl_porciento',
            'duracion', 'emocion', 'notas', 'lecciones', 'screenshot',
        ]
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'hora_entrada': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'hora_salida': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'par': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'EURUSD, BTCUSDT, XAUUSD'}),
            'mercado': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'estrategia': forms.Select(attrs={'class': 'form-select'}),
            'estrategia_otro': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Especificar estrategia'}),
            'precio_entrada': forms.NumberInput(attrs={'class': 'form-input', 'step': 'any', 'placeholder': '1.08500'}),
            'precio_salida': forms.NumberInput(attrs={'class': 'form-input', 'step': 'any', 'placeholder': '1.09000'}),
            'stop_loss': forms.NumberInput(attrs={'class': 'form-input', 'step': 'any', 'placeholder': '1.08000'}),
            'take_profit': forms.NumberInput(attrs={'class': 'form-input', 'step': 'any', 'placeholder': '1.09500'}),
            'lotes': forms.NumberInput(attrs={'class': 'form-input', 'step': 'any', 'placeholder': '0.10'}),
            'resultado': forms.Select(attrs={'class': 'form-select'}),
            'pnl': forms.NumberInput(attrs={'class': 'form-input', 'step': 'any', 'placeholder': '50.00'}),
            'pnl_porciento': forms.NumberInput(attrs={'class': 'form-input', 'step': 'any', 'placeholder': '2.5'}),
            'duracion': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '2h 30min'}),
            'emocion': forms.Select(attrs={'class': 'form-select'}),
            'notas': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': '¿Qué viste en el mercado? ¿Por qué entraste?'}),
            'lecciones': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': '¿Qué aprendiste de este trade?'}),
            'screenshot': forms.FileInput(attrs={'class': 'form-input', 'accept': 'image/*'}),
        }
        labels = {
            'fecha': 'Fecha de Operación',
            'hora_entrada': 'Hora de Entrada',
            'hora_salida': 'Hora de Salida',
            'par': 'Par/Activo',
            'mercado': 'Mercado',
            'tipo': 'Tipo de Operación',
            'estrategia': 'Estrategia Utilizada',
            'estrategia_otro': 'Otra Estrategia',
            'precio_entrada': 'Precio de Entrada',
            'precio_salida': 'Precio de Salida',
            'stop_loss': 'Stop Loss',
            'take_profit': 'Take Profit',
            'lotes': 'Lotes/Tamaño',
            'resultado': 'Resultado',
            'pnl': 'P&L ($)',
            'pnl_porciento': 'P&L (%)',
            'duracion': 'Duración del Trade',
            'emocion': 'Emoción durante el Trade',
            'notas': 'Notas y Observaciones',
            'lecciones': 'Lecciones Aprendidas',
            'screenshot': 'Captura de Pantalla',
        }


class OKXApiConfigForm(forms.ModelForm):
    class Meta:
        model = OKXApiConfig
        fields = ['api_key', 'api_secret', 'passphrase']
        widgets = {
            'api_key': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ingresa tu API Key de OKX'}),
            'api_secret': forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Ingresa tu API Secret'}),
            'passphrase': forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Ingresa tu Passphrase'}),
        }
        labels = {
            'api_key': 'API Key',
            'api_secret': 'API Secret',
            'passphrase': 'Passphrase',
        }


class OKXCsvUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='Archivo CSV de OKX',
        widget=forms.FileInput(attrs={'class': 'form-input', 'accept': '.csv'}),
        help_text='Exporta tus trades desde OKX y sube el archivo CSV',
    )
