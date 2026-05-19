from django.db import models
from django.contrib.auth.models import User


class Miembro(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('master', 'Master'),
        ('member', 'Miembro de Comunidad'),
    ]

    EXPERIENCIA_CHOICES = [
        ('principiante', 'Principiante'),
        ('intermedio', 'Intermedio'),
        ('avanzado', 'Avanzado'),
    ]

    CAPITAL_CHOICES = [
        ('0-100', '$0 - $100 USD'),
        ('100-1000', '$100 - $1,000 USD'),
        ('1000-5000', '$1,000 - $5,000 USD'),
        ('5000+', 'Más de $5,000 USD'),
    ]

    DIFICULTAD_CHOICES = [
        ('no_se_por_donde', 'No sé por dónde empezar'),
        ('pierdo_dinero', 'Pierdo dinero constantemente'),
        ('falta_disciplina', 'Falta de disciplina'),
        ('no_entiendo', 'No entiendo el mercado'),
        ('mala_gestion', 'Mala gestión de riesgo'),
        ('otro', 'Otro'),
    ]

    TIEMPO_CHOICES = [
        ('menos_1mes', 'Menos de 1 mes'),
        ('1-6meses', '1 a 6 meses'),
        ('6-12meses', '6 a 12 meses'),
        ('1-2anos', '1 a 2 años'),
        ('mas_2anos', 'Más de 2 años'),
    ]

    OBJETIVO_CHOICES = [
        ('ingresos_extra', 'Generar Ingresos Extra'),
        ('vivir_trading', 'Vivir del Trading'),
        ('aprender_cero', 'Aprender desde Cero'),
        ('lograr_consistencia', 'Lograr Consistencia'),
        ('cuenta_fondeo', 'Para una Cuenta de Fondeo'),
        ('otro', 'Otro'),
    ]

    PLATAFORMA_CHOICES = [
        ('metatrader', 'MetaTrader (MT4/MT5)'),
        ('ctrader', 'cTrader'),
        ('tradingview', 'TradingView'),
        ('ninjatrader', 'NinjaTrader'),
        ('otro', 'Otro'),
    ]

    CONTENIDO_CHOICES = [
        ('trading_vivo', 'Trading en Vivo'),
        ('psicotrading', 'Psicotrading'),
        ('cuentas_pequenas', 'Manejo de Cuentas Pequeñas'),
        ('config_herramientas', 'Configuración de Herramientas'),
        ('criptomonedas', 'Criptomonedas'),
        ('todo', 'Todo lo Anterior'),
    ]

    MERCADO_CHOICES = [
        ('forex', 'Forex'),
        ('cripto', 'Criptomonedas'),
        ('indices', 'Índices'),
        ('materias_primas', 'Materias Primas'),
        ('acciones', 'Acciones'),
    ]

    BROKER_CHOICES = [
        ('okx', 'OKX'),
        ('fxpro', 'FXPRO'),
        ('tickmill', 'Tickmill'),
        ('pepperstone', 'Pepperstone'),
        ('exness', 'Exness'),
        ('bybit', 'Bybit'),
        ('otro', 'Otro'),
    ]

    REFERRAL_CHOICES = [
        ('youtube', 'YouTube'),
        ('tiktok', 'TikTok'),
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('amigo', 'Recomendación de un amigo'),
        ('telegram', 'Telegram'),
        ('discord', 'Discord'),
        ('otro', 'Otro'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='miembro', null=True, blank=True)
    rol = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member', verbose_name='Rol')

    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(verbose_name='Fecha de Nacimiento')
    pais = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100)
    email = models.EmailField(verbose_name='Correo Electrónico')
    whatsapp = models.CharField(max_length=20, verbose_name='Teléfono WhatsApp')
    telegram = models.CharField(max_length=50, verbose_name='Usuario Telegram', help_text='Incluir @ si aplica')

    tiempo_interes = models.CharField(max_length=20, choices=TIEMPO_CHOICES, verbose_name='¿Hace cuánto te interesa el trading?')
    experiencia = models.CharField(max_length=20, choices=EXPERIENCIA_CHOICES, verbose_name='Nivel de Experiencia')
    mercados = models.CharField(max_length=200, verbose_name='Mercados de Interés', help_text='Separados por coma')
    objetivo_principal = models.CharField(max_length=20, choices=OBJETIVO_CHOICES, verbose_name='Objetivo Principal')
    objetivo_otro = models.CharField(max_length=200, blank=True, verbose_name='Otro Objetivo')
    capital = models.CharField(max_length=20, choices=CAPITAL_CHOICES, verbose_name='Capital para Operar')
    mayor_dificultad = models.CharField(max_length=20, choices=DIFICULTAD_CHOICES, verbose_name='Mayor Dificultad')
    dificultad_otro = models.CharField(max_length=200, blank=True, verbose_name='Otra Dificultad')
    plataformas = models.CharField(max_length=200, verbose_name='Plataformas de Trading', help_text='Separados por coma')
    plataforma_otro = models.CharField(max_length=200, blank=True, verbose_name='Otra Plataforma')
    contenido_interes = models.CharField(max_length=200, verbose_name='Contenido de Interés', help_text='Separados por coma')

    opera_broker = models.BooleanField(default=False, verbose_name='¿Actualmente operas con algún broker o exchange?')
    broker_actual = models.CharField(max_length=20, choices=BROKER_CHOICES, blank=True, verbose_name='¿Cuál utilizas actualmente?')
    broker_otro = models.CharField(max_length=100, blank=True, verbose_name='Otro Broker')
    interesado_herramientas = models.BooleanField(default=False, verbose_name='¿Te gustaría operar con herramientas y brokers recomendados?')
    interesado_eventos = models.BooleanField(default=False, verbose_name='¿Te interesan eventos presenciales o virtuales?')
    interesado_sesiones_vivo = models.BooleanField(default=False, verbose_name='¿Te gustaría participar activamente en sesiones en vivo?')
    interesado_ofertas = models.BooleanField(default=False, verbose_name='¿Te gustaría recibir ofertas exclusivas, promociones o lanzamientos?')
    referral_source = models.CharField(max_length=20, choices=REFERRAL_CHOICES, default='', blank=True, verbose_name='¿Por dónde te enteraste de Creemos Capital?')
    referral_otro = models.CharField(max_length=100, blank=True, verbose_name='Otra Fuente')
    documento = models.FileField(upload_to='documentos/', blank=True, null=True, verbose_name='Documento o Selfie')
    acepta_terminos = models.BooleanField(default=False, verbose_name='Aceptación de Términos')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Miembro'
        verbose_name_plural = 'Miembros'

    def __str__(self):
        return f'{self.nombre} {self.apellidos} ({self.get_rol_display()})'

    def get_full_name(self):
        return f'{self.nombre} {self.apellidos}'


class SiteConfig(models.Model):
    site_title = models.CharField(max_length=200, default='Creemos Capital')
    site_description = models.TextField(default='Trading en vivo con estrategia C4')
    whatsapp_number = models.CharField(max_length=20, default='+57 315 326 3852')
    whatsapp_url = models.URLField(default='https://wa.me/573153263852')
    telegram_url = models.URLField(default='https://t.me/creemoscapitaloficial')
    email = models.EmailField(default='info@creemoscapital.com')
    kick_channel = models.CharField(max_length=100, default='creemoscapital')
    youtube_channel = models.CharField(max_length=100, default='@creemoscapital')
    youtube_channel_url = models.URLField(default='https://www.youtube.com/@creemoscapital')
    google_form_url = models.URLField(default='https://forms.gle/gpwxCJwcXvEX2bU26')
    okx_affiliate_url = models.URLField(default='https://www.okx.com/join/CREEMOS')
    spotify_url = models.URLField(blank=True, default='')
    youtube_music_url = models.URLField(blank=True, default='')
    youtube_music_playlist_id = models.CharField(max_length=100, default='UUv4ma-yTMOqYYF_Ii5kv0zQ')

    class Meta:
        verbose_name = 'Configuracion del Sitio'
        verbose_name_plural = 'Configuracion del Sitio'

    def __str__(self):
        return self.site_title

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class SocialLink(models.Model):
    name = models.CharField(max_length=50)
    url = models.URLField()
    icon_class = models.CharField(max_length=100, blank=True, help_text='SVG icon class or emoji')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Red Social'
        verbose_name_plural = 'Redes Sociales'

    def __str__(self):
        return self.name


class Sesion(models.Model):
    nombre = models.CharField(max_length=50)
    emoji = models.CharField(max_length=10, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Sesion de Trading'
        verbose_name_plural = 'Sesiones de Trading'

    def __str__(self):
        return self.nombre


class SesionHorario(models.Model):
    sesion = models.ForeignKey(Sesion, on_delete=models.CASCADE, related_name='horarios')
    paises = models.CharField(max_length=100, help_text='Paises separados por /')
    bandera_codigo = models.CharField(max_length=5, help_text='Codigo de bandera (flagcdn)')
    hora = models.CharField(max_length=50)

    class Meta:
        ordering = ['sesion__order', 'id']
        verbose_name = 'Horario de Sesion'
        verbose_name_plural = 'Horarios de Sesiones'

    def __str__(self):
        return f'{self.sesion.nombre} - {self.paises}'


class Video(models.Model):
    CATEGORIA_CHOICES = [
        ('novatos', 'Trading para Novatos'),
        ('estrategia', 'La Estrategia'),
    ]
    titulo = models.CharField(max_length=200)
    youtube_id = models.CharField(max_length=20)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['categoria', 'order']
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'

    def __str__(self):
        return self.titulo

    def thumbnail_url(self):
        return f'https://img.youtube.com/vi/{self.youtube_id}/hqdefault.jpg'


class NoticiaFuente(models.Model):
    nombre = models.CharField(max_length=100)
    url = models.URLField()
    descripcion = models.TextField(blank=True)
    icono = models.CharField(max_length=100, blank=True, help_text='SVG icon class')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Fuente de Noticias'
        verbose_name_plural = 'Fuentes de Noticias'

    def __str__(self):
        return self.nombre


class MusicaLink(models.Model):
    TIPO_CHOICES = [
        ('spotify', 'Spotify'),
        ('youtube_music', 'YouTube Music'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    url = models.URLField()
    titulo = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Enlace de Musica'
        verbose_name_plural = 'Enlaces de Musica'

    def __str__(self):
        return f'{self.get_tipo_display()} - {self.titulo}'


class TradeJournal(models.Model):
    TIPO_CHOICES = [
        ('long', 'Long (Compra)'),
        ('short', 'Short (Venta)'),
    ]
    RESULTADO_CHOICES = [
        ('ganancia', 'Ganancia'),
        ('perdida', 'Pérdida'),
        ('breakeven', 'Breakeven'),
        ('pendiente', 'Pendiente'),
    ]
    MERCADO_CHOICES = [
        ('forex', 'Forex'),
        ('cripto', 'Criptomonedas'),
        ('indices', 'Índices'),
        ('materias_primas', 'Materias Primas'),
        ('acciones', 'Acciones'),
    ]
    ESTRATEGIA_CHOICES = [
        ('c4', 'Estrategia C4'),
        ('soporte_resistencia', 'Soporte/Resistencia'),
        ('fibonacci', 'Fibonacci'),
        ('ict', 'ICT/SMC'),
        ('otro', 'Otro'),
    ]
    EMOCION_CHOICES = [
        ('confiado', 'Confiado'),
        ('neutral', 'Neutral'),
        ('ansioso', 'Ansioso'),
        ('miedo', 'Miedo'),
        ('codicia', 'Codicia'),
        ('impulsivo', 'Impulsivo'),
        ('disciplinado', 'Disciplinado'),
    ]
    FUENTE_CHOICES = [
        ('manual', 'Registro Manual'),
        ('okx_api', 'OKX API'),
        ('okx_csv', 'OKX CSV'),
    ]

    miembro = models.ForeignKey(Miembro, on_delete=models.CASCADE, related_name='trades')
    
    fecha = models.DateField(verbose_name='Fecha de Operación')
    hora_entrada = models.TimeField(verbose_name='Hora de Entrada', blank=True, null=True)
    hora_salida = models.TimeField(verbose_name='Hora de Salida', blank=True, null=True)
    
    par = models.CharField(max_length=20, verbose_name='Par/Activo', help_text='Ej: EURUSD, BTCUSDT, XAUUSD')
    mercado = models.CharField(max_length=20, choices=MERCADO_CHOICES, verbose_name='Mercado')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, verbose_name='Tipo de Operación')
    estrategia = models.CharField(max_length=30, choices=ESTRATEGIA_CHOICES, verbose_name='Estrategia')
    estrategia_otro = models.CharField(max_length=100, blank=True, verbose_name='Otra Estrategia')
    
    precio_entrada = models.DecimalField(max_digits=12, decimal_places=5, verbose_name='Precio de Entrada')
    precio_salida = models.DecimalField(max_digits=12, decimal_places=5, verbose_name='Precio de Salida', blank=True, null=True)
    stop_loss = models.DecimalField(max_digits=12, decimal_places=5, verbose_name='Stop Loss', blank=True, null=True)
    take_profit = models.DecimalField(max_digits=12, decimal_places=5, verbose_name='Take Profit', blank=True, null=True)
    
    lotes = models.DecimalField(max_digits=10, decimal_places=4, verbose_name='Lotes/Tamaño', blank=True, null=True)
    resultado = models.CharField(max_length=15, choices=RESULTADO_CHOICES, default='pendiente', verbose_name='Resultado')
    pnl = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='P&L ($)', blank=True, null=True, help_text='Ganancia o pérdida en dólares')
    pnl_porciento = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='P&L (%)', blank=True, null=True, help_text='Porcentaje de ganancia/pérdida')
    
    rr = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Risk:Reward', blank=True, null=True, help_text='Ratio Riesgo/Beneficio')
    duracion = models.CharField(max_length=20, blank=True, verbose_name='Duración', help_text='Ej: 2h 30min')
    
    emocion = models.CharField(max_length=15, choices=EMOCION_CHOICES, blank=True, verbose_name='Emoción durante el trade')
    notas = models.TextField(blank=True, verbose_name='Notas y Observaciones')
    lecciones = models.TextField(blank=True, verbose_name='Lecciones Aprendidas')
    
    screenshot = models.ImageField(upload_to='trades/screenshots/', blank=True, null=True, verbose_name='Captura de Pantalla')
    
    fuente = models.CharField(max_length=15, choices=FUENTE_CHOICES, default='manual', verbose_name='Fuente de Registro')
    okx_order_id = models.CharField(max_length=50, blank=True, verbose_name='OKX Order ID')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha', '-created_at']
        verbose_name = 'Registro de Trading'
        verbose_name_plural = 'Bitácora de Trading'
        indexes = [
            models.Index(fields=['miembro', 'fecha']),
            models.Index(fields=['miembro', 'resultado']),
        ]

    def __str__(self):
        return f'{self.par} - {self.fecha} ({self.get_resultado_display()})'

    def save(self, *args, **kwargs):
        if self.precio_entrada and self.precio_salida:
            if self.tipo == 'long':
                diff = self.precio_salida - self.precio_entrada
            else:
                diff = self.precio_entrada - self.precio_salida
            
            if self.stop_loss:
                if self.tipo == 'long':
                    risk = self.precio_entrada - self.stop_loss
                else:
                    risk = self.stop_loss - self.precio_entrada
                
                if risk and risk != 0:
                    self.rr = round(abs(diff / risk), 2)
        
        super().save(*args, **kwargs)


class OKXApiConfig(models.Model):
    miembro = models.OneToOneField(Miembro, on_delete=models.CASCADE, related_name='okx_config')
    api_key = models.CharField(max_length=200, verbose_name='API Key')
    api_secret = models.CharField(max_length=200, verbose_name='API Secret')
    passphrase = models.CharField(max_length=200, verbose_name='Passphrase')
    is_active = models.BooleanField(default=False, verbose_name='Conexión Activa')
    last_sync = models.DateTimeField(blank=True, null=True, verbose_name='Última Sincronización')
    
    okx_uid = models.CharField(max_length=50, blank=True, verbose_name='OKX UID')
    account_balance = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, verbose_name='Balance Total (USD)')
    total_volume = models.DecimalField(max_digits=15, decimal_places=4, blank=True, null=True, verbose_name='Volumen Total Tradeado')
    total_trades_api = models.PositiveIntegerField(default=0, verbose_name='Total Trades en OKX')
    account_details = models.JSONField(blank=True, null=True, verbose_name='Detalles de Cuenta')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuración OKX API'
        verbose_name_plural = 'Configuraciones OKX API'

    def __str__(self):
        return f'OKX API - {self.miembro.get_full_name()}'
