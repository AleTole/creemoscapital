from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import SiteConfig, SocialLink, Sesion, SesionHorario, Video, NoticiaFuente, MusicaLink, Miembro


@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    list_display = ['site_title', 'whatsapp_number', 'email']


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'order', 'is_active']
    list_editable = ['order', 'is_active']


class SesionHorarioInline(admin.TabularInline):
    model = SesionHorario
    extra = 1


@admin.register(Sesion)
class SesionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'order']
    inlines = [SesionHorarioInline]


@admin.register(SesionHorario)
class SesionHorarioAdmin(admin.ModelAdmin):
    list_display = ['sesion', 'paises', 'hora']


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'order', 'is_active']
    list_filter = ['categoria', 'is_active']
    list_editable = ['order', 'is_active']


@admin.register(NoticiaFuente)
class NoticiaFuenteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'url', 'order', 'is_active']
    list_editable = ['order', 'is_active']


@admin.register(MusicaLink)
class MusicaLinkAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'url', 'is_active']


class MiembroInline(admin.StackedInline):
    model = Miembro
    can_delete = False
    verbose_name_plural = 'Miembro'
    fk_name = 'user'
    fields = ['rol', 'whatsapp', 'telegram', 'pais', 'ciudad', 'experiencia', 'capital', 'created_at']
    readonly_fields = ['created_at']


class CustomUserAdmin(BaseUserAdmin):
    inlines = [MiembroInline]
    list_display = ['email', 'first_name', 'last_name', 'get_rol', 'is_staff', 'date_joined']

    def get_rol(self, obj):
        try:
            return obj.miembro.get_rol_display()
        except Miembro.DoesNotExist:
            return 'Sin rol'
    get_rol.short_description = 'Rol'


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Miembro)
class MiembroAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'email', 'rol', 'experiencia', 'capital', 'pais', 'opera_broker', 'broker_actual', 'created_at']
    list_filter = ['rol', 'experiencia', 'capital', 'pais', 'opera_broker', 'broker_actual', 'interesado_eventos', 'interesado_sesiones_vivo', 'interesado_ofertas', 'referral_source']
    search_fields = ['nombre', 'apellidos', 'email', 'whatsapp', 'telegram']
    readonly_fields = ['created_at', 'updated_at', 'user']
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellidos', 'fecha_nacimiento', 'pais', 'ciudad')
        }),
        ('Contacto', {
            'fields': ('email', 'whatsapp', 'telegram')
        }),
        ('Trading', {
            'fields': ('tiempo_interes', 'experiencia', 'mercados', 'objetivo_principal', 'objetivo_otro', 'capital', 'mayor_dificultad', 'dificultad_otro')
        }),
        ('Plataformas y Contenido', {
            'fields': ('plataformas', 'plataforma_otro', 'contenido_interes')
        }),
        ('Broker y Exchange', {
            'fields': ('opera_broker', 'broker_actual', 'broker_otro', 'interesado_herramientas')
        }),
        ('Intereses y Participación', {
            'fields': ('interesado_eventos', 'interesado_sesiones_vivo', 'interesado_ofertas')
        }),
        ('Referencia', {
            'fields': ('referral_source', 'referral_otro')
        }),
        ('Documento', {
            'fields': ('documento',)
        }),
        ('Sistema', {
            'fields': ('user', 'rol', 'acepta_terminos', 'created_at', 'updated_at')
        }),
    )
    actions = ['promover_a_master', 'degradar_a_miembro']

    def promover_a_master(self, request, queryset):
        queryset.update(rol='master')
        self.message_user(request, f'{queryset.count()} miembro(s) promovidos a Master.')
    promover_a_master.short_description = 'Promover seleccionados a Master'

    def degradar_a_miembro(self, request, queryset):
        queryset.update(rol='member')
        self.message_user(request, f'{queryset.count()} miembro(s) degradados a Miembro de Comunidad.')
    degradar_a_miembro.short_description = 'Degradar seleccionados a Miembro'
