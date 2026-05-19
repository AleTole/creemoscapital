from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('sesiones/', views.sesiones_view, name='sesiones'),
    path('videos/', views.videos_view, name='videos'),
    path('noticias/', views.noticias_view, name='noticias'),
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('musica/', views.musica_view, name='musica'),
    path('redes/', views.redes_view, name='redes'),
    path('api/calendario/', views.proxy_calendario, name='proxy_calendario'),
    
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/analisis/', views.analytics_view, name='analytics'),
    path('dashboard/trade/nuevo/', views.trade_create_view, name='trade_create'),
    path('dashboard/trade/<int:trade_id>/editar/', views.trade_edit_view, name='trade_edit'),
    path('dashboard/trade/<int:trade_id>/eliminar/', views.trade_delete_view, name='trade_delete'),
    
    path('dashboard/importar/', views.import_view, name='import'),
    path('dashboard/importar/okx-api/', views.okx_api_config_view, name='okx_api_config'),
    path('dashboard/importar/okx-sync/', views.okx_sync_view, name='okx_sync'),
    path('dashboard/importar/okx-csv/', views.okx_csv_upload_view, name='okx_csv_upload'),
    path('dashboard/importar/okx-refresh/', views.okx_refresh_account_view, name='okx_refresh_account'),
    path('dashboard/importar/okx-debug/', views.okx_debug_view, name='okx_debug'),
]
