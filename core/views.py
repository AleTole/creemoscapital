import requests
import csv
import hmac
import hashlib
import base64
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.cache import cache_page
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, Q, Max, Min
from django.utils import timezone
from .models import SiteConfig, Video, Sesion, NoticiaFuente, MusicaLink, SocialLink, TradeJournal, OKXApiConfig
from .forms import MiembroRegistroForm, MiembroLoginForm, TradeJournalForm, OKXApiConfigForm, OKXCsvUploadForm


def get_context():
    config = SiteConfig.load()
    return {
        'config': config,
        'social_links': SocialLink.objects.filter(is_active=True),
    }


def home(request):
    context = get_context()
    context['videos_novatos'] = Video.objects.filter(categoria='novatos', is_active=True)[:3]
    context['videos_estrategia'] = Video.objects.filter(categoria='estrategia', is_active=True)[:4]
    context['sesiones'] = Sesion.objects.prefetch_related('horarios').all()
    return render(request, 'core/index.html', context)


def sesiones_view(request):
    context = get_context()
    context['sesiones'] = Sesion.objects.prefetch_related('horarios').all()
    return render(request, 'core/sesiones.html', context)


def videos_view(request):
    context = get_context()
    context['videos_novatos'] = Video.objects.filter(categoria='novatos', is_active=True)
    context['videos_estrategia'] = Video.objects.filter(categoria='estrategia', is_active=True)
    return render(request, 'core/videos.html', context)


def noticias_view(request):
    context = get_context()
    context['noticias_fuentes'] = NoticiaFuente.objects.filter(is_active=True)
    return render(request, 'core/noticias.html', context)


def registro_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = MiembroRegistroForm(request.POST, request.FILES)
        if form.is_valid():
            miembro = form.save()
            login(request, miembro.user)
            messages.success(request, '¡Registro exitoso! Bienvenido a Creemos Capital.')
            return redirect('core:home')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = MiembroRegistroForm()

    context = get_context()
    context['form'] = form
    return render(request, 'core/registro.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = MiembroLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'¡Bienvenido de vuelta, {user.first_name}!')
            next_url = request.GET.get('next', 'core:home')
            return redirect(next_url)
        else:
            messages.error(request, 'Correo o contraseña incorrectos.')
    else:
        form = MiembroLoginForm()

    context = get_context()
    context['form'] = form
    return render(request, 'core/login.html', context)


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('core:home')


def musica_view(request):
    context = get_context()
    context['musica_links'] = MusicaLink.objects.filter(is_active=True)
    return render(request, 'core/musica.html', context)


def redes_view(request):
    context = get_context()
    return render(request, 'core/redes.html', context)


@require_GET
@cache_page(60 * 5)
def proxy_calendario(request):
    url = 'https://nfs.faireconomy.media/ff_calendar_thisweek.json?timezone=America%2FBogota'
    try:
        resp = requests.get(url, timeout=10)
        return JsonResponse(resp.json(), safe=False)
    except Exception:
        return JsonResponse({'error': 'No se pudo cargar el calendario'}, status=502)


@login_required
def dashboard_view(request):
    try:
        miembro = request.user.miembro
    except Miembro.DoesNotExist:
        messages.error(request, 'No se encontró tu perfil. Contacta a soporte.')
        return redirect('core:home')

    trades = TradeJournal.objects.filter(miembro=miembro)
    
    hoy = timezone.now().date()
    trades_hoy = trades.filter(fecha=hoy)
    trades_semana = trades.filter(fecha__gte=hoy - timezone.timedelta(days=7))
    trades_mes = trades.filter(fecha__gte=hoy.replace(day=1))
    
    total_trades = trades.count()
    trades_ganados = trades.filter(resultado='ganancia').count()
    trades_perdidos = trades.filter(resultado='perdida').count()
    win_rate = round((trades_ganados / total_trades * 100), 1) if total_trades > 0 else 0
    
    pnl_total = trades.aggregate(total=Sum('pnl'))['total'] or 0
    pnl_mes = trades_mes.aggregate(total=Sum('pnl'))['total'] or 0
    
    okx_config = None
    try:
        okx_config = OKXApiConfig.objects.get(miembro=miembro, is_active=True)
    except OKXApiConfig.DoesNotExist:
        pass
    
    okx_trades_count = 0
    if okx_config:
        okx_trades_count = okx_config.total_trades_api
    
    context = get_context()
    context['miembro'] = miembro
    context['trades'] = trades[:50]
    context['total_trades'] = total_trades
    context['trades_ganados'] = trades_ganados
    context['trades_perdidos'] = trades_perdidos
    context['win_rate'] = win_rate
    context['pnl_total'] = pnl_total
    context['pnl_mes'] = pnl_mes
    context['trades_hoy_count'] = trades_hoy.count()
    context['trades_semana_count'] = trades_semana.count()
    context['trades_mes_count'] = trades_mes.count()
    context['okx_config'] = okx_config
    context['okx_trades_count'] = okx_trades_count
    
    return render(request, 'core/dashboard.html', context)


@login_required
def trade_create_view(request):
    try:
        miembro = request.user.miembro
    except Miembro.DoesNotExist:
        messages.error(request, 'No se encontró tu perfil.')
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = TradeJournalForm(request.POST, request.FILES)
        if form.is_valid():
            trade = form.save(commit=False)
            trade.miembro = miembro
            trade.save()
            messages.success(request, f'✅ Trade registrado: {trade.par}')
            return redirect('core:dashboard')
    else:
        form = TradeJournalForm(initial={'fecha': timezone.now().date()})

    context = get_context()
    context['form'] = form
    context['title'] = 'Nuevo Trade'
    return render(request, 'core/trade_form.html', context)


@login_required
def trade_edit_view(request, trade_id):
    trade = get_object_or_404(TradeJournal, id=trade_id, miembro=request.user.miembro)

    if request.method == 'POST':
        form = TradeJournalForm(request.POST, request.FILES, instance=trade)
        if form.is_valid():
            form.save()
            messages.success(request, f'✏️ Trade actualizado: {trade.par}')
            return redirect('core:dashboard')
    else:
        form = TradeJournalForm(instance=trade)

    context = get_context()
    context['form'] = form
    context['title'] = 'Editar Trade'
    return render(request, 'core/trade_form.html', context)


@login_required
def trade_delete_view(request, trade_id):
    trade = get_object_or_404(TradeJournal, id=trade_id, miembro=request.user.miembro)
    
    if request.method == 'POST':
        par = trade.par
        trade.delete()
        messages.success(request, f'🗑️ Trade eliminado: {par}')
        return redirect('core:dashboard')

    context = get_context()
    context['trade'] = trade
    return render(request, 'core/trade_confirm_delete.html', context)


@login_required
def import_view(request):
    try:
        miembro = request.user.miembro
    except Miembro.DoesNotExist:
        messages.error(request, 'No se encontró tu perfil.')
        return redirect('core:dashboard')

    trades_count = TradeJournal.objects.filter(miembro=miembro).count()
    has_okx_config = OKXApiConfig.objects.filter(miembro=miembro).exists()
    
    context = get_context()
    context['miembro'] = miembro
    context['trades_count'] = trades_count
    context['has_okx_config'] = has_okx_config
    context['api_form'] = OKXApiConfigForm()
    context['csv_form'] = OKXCsvUploadForm()
    
    return render(request, 'core/import_trades.html', context)


@login_required
@require_POST
def okx_api_config_view(request):
    try:
        miembro = request.user.miembro
    except Miembro.DoesNotExist:
        messages.error(request, 'No se encontró tu perfil.')
        return redirect('core:import')

    config, created = OKXApiConfig.objects.get_or_create(miembro=miembro)
    form = OKXApiConfigForm(request.POST, instance=config)
    
    if form.is_valid():
        config = form.save(commit=False)
        config.is_active = True
        config.save()
        
        try:
            fetch_okx_account_info(config)
            messages.success(request, '✅ Conexión con OKX configurada correctamente')
        except Exception as e:
            messages.warning(request, f'⚠️ API conectada pero no se pudo obtener info de cuenta: {str(e)}')
        
        return redirect('core:import')
    
    messages.error(request, 'Error al configurar la API. Verifica tus credenciales.')
    return redirect('core:import')


@login_required
def okx_sync_view(request):
    try:
        miembro = request.user.miembro
        config = OKXApiConfig.objects.get(miembro=miembro, is_active=True)
    except (Miembro.DoesNotExist, OKXApiConfig.DoesNotExist):
        messages.error(request, 'No hay configuración de OKX activa.')
        return redirect('core:import')

    try:
        trades_synced = sync_okx_trades(miembro, config)
        if trades_synced > 0:
            messages.success(request, f'✅ {trades_synced} trades sincronizados desde OKX')
        else:
            messages.warning(request, '⚠️ No se encontraron trades nuevos. Verifica que tu API tenga permisos de lectura.')
    except Exception as e:
        messages.error(request, f'Error al sincronizar: {str(e)}')
    
    return redirect('core:dashboard')


def fetch_okx_account_info(config):
    """Obtiene información básica de la cuenta OKX"""
    from datetime import datetime, timezone as dt_timezone
    import logging
    
    logger = logging.getLogger(__name__)
    
    api_key = config.api_key
    api_secret = config.api_secret
    passphrase = config.passphrase
    
    def make_request(request_path):
        timestamp = datetime.now(dt_timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.') + f'{datetime.now(dt_timezone.utc).microsecond // 1000:03d}Z'
        method = 'GET'
        
        sign_str = timestamp + method + request_path
        signature = hmac.new(
            api_secret.encode('utf-8'),
            sign_str.encode('utf-8'),
            hashlib.sha256
        ).digest()
        signature = base64.b64encode(signature).decode('utf-8')
        
        headers = {
            'OK-ACCESS-KEY': api_key,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': passphrase,
            'Content-Type': 'application/json',
        }
        
        logger.info(f'OKX Request: {request_path}')
        logger.info(f'OKX Timestamp: {timestamp}')
        logger.info(f'OKX Sign String: {sign_str}')
        
        response = requests.get(f'https://www.okx.com{request_path}', headers=headers, timeout=30)
        logger.info(f'OKX Response Status: {response.status_code}')
        logger.info(f'OKX Response: {response.text[:500]}')
        
        return response.json()
    
    account_details = {}
    
    try:
        config_data = make_request('/api/v5/account/config')
        logger.info(f'OKX Config Data: {config_data}')
        
        if config_data.get('code') == '0':
            data_list = config_data.get('data', [])
            if data_list:
                config.okx_uid = data_list[0].get('uid', '')
                logger.info(f'OKX UID found: {config.okx_uid}')
            else:
                logger.warning('OKX Config: No data returned')
        else:
            logger.warning(f'OKX Config Error: {config_data}')
    except Exception as e:
        logger.error(f'OKX Config Exception: {str(e)}')
    
    try:
        balance_data = make_request('/api/v5/account/balance')
        logger.info(f'OKX Balance Data: {balance_data}')
        
        if balance_data.get('code') == '0':
            data_list = balance_data.get('data', [])
            if data_list:
                total_balance = 0
                for account in data_list[0].get('details', []):
                    eq = float(account.get('eq', 0))
                    total_balance += eq
                
                config.account_balance = round(total_balance, 2)
                account_details['balance'] = data_list
                logger.info(f'OKX Balance: ${config.account_balance}')
            else:
                logger.warning('OKX Balance: No data returned')
        else:
            logger.warning(f'OKX Balance Error: {balance_data}')
    except Exception as e:
        logger.error(f'OKX Balance Exception: {str(e)}')
    
    inst_types = ['SPOT', 'SWAP', 'FUTURES', 'MARGIN']
    total_trades = 0
    total_volume = 0
    all_recent_trades = []
    
    for inst_type in inst_types:
        try:
            trades_data = make_request(f'/api/v5/trade/orders-history-archive?instType={inst_type}')
            if trades_data.get('code') == '0':
                orders = trades_data.get('data', [])
                total_trades += len(orders)
                
                for order in orders:
                    fill_sz = float(order.get('accFillSz', 0))
                    avg_px = float(order.get('avgPx', 0))
                    total_volume += fill_sz * avg_px
                
                all_recent_trades.extend(orders[:5])
        except Exception as e:
            logger.error(f'OKX {inst_type} Exception: {str(e)}')
            continue
    
    config.total_trades_api = total_trades
    config.total_volume = round(total_volume, 4)
    account_details['recent_trades'] = all_recent_trades[:20]
    account_details['inst_types'] = inst_types
    
    config.account_details = account_details
    config.save()
    
    logger.info(f'OKX Account Info Updated: UID={config.okx_uid}, Balance={config.account_balance}, Trades={config.total_trades_api}')


@login_required
def analytics_view(request):
    """Vista de análisis profesional de psicotrading y rendimiento"""
    try:
        miembro = request.user.miembro
    except Miembro.DoesNotExist:
        messages.error(request, 'No se encontró tu perfil.')
        return redirect('core:dashboard')

    trades = TradeJournal.objects.filter(miembro=miembro)
    total = trades.count()
    
    if total == 0:
        messages.info(request, 'Aún no tienes trades para analizar. Importa desde OKX o registra manualmente.')
        return redirect('core:dashboard')
    
    hoy = timezone.now().date()
    
    # Métricas básicas
    ganados = trades.filter(resultado='ganancia').count()
    perdidos = trades.filter(resultado='perdida').count()
    breakeven = trades.filter(resultado='breakeven').count()
    win_rate = round((ganados / total * 100), 1) if total > 0 else 0
    
    pnl_total = trades.aggregate(total=Sum('pnl'))['total'] or 0
    avg_pnl = trades.aggregate(avg=Avg('pnl'))['avg'] or 0
    best_trade = trades.aggregate(best=Max('pnl'))['best'] or 0
    worst_trade = trades.aggregate(worst=Min('pnl'))['worst'] or 0
    
    # Análisis por tipo
    longs = trades.filter(tipo='long')
    shorts = trades.filter(tipo='short')
    long_win_rate = round((longs.filter(resultado='ganancia').count() / longs.count() * 100), 1) if longs.count() > 0 else 0
    short_win_rate = round((shorts.filter(resultado='ganancia').count() / shorts.count() * 100), 1) if shorts.count() > 0 else 0
    
    # Análisis por emoción (psicotrading)
    trades_con_emocion = trades.exclude(emocion='').exclude(emocion__isnull=True)
    emocion_stats = {}
    if trades_con_emocion.exists():
        for emocion_code, emocion_label in TradeJournal.EMOCION_CHOICES:
            emocion_trades = trades.filter(emocion=emocion_code)
            count = emocion_trades.count()
            if count > 0:
                emocion_win = emocion_trades.filter(resultado='ganancia').count()
                emocion_pnl = emocion_trades.aggregate(total=Sum('pnl'))['total'] or 0
                emocion_stats[emocion_label] = {
                    'count': count,
                    'win_rate': round((emocion_win / count * 100), 1),
                    'pnl': emocion_pnl,
                }
    
    # Rachas
    trades_sorted = trades.order_by('fecha', 'created_at')
    current_streak = 0
    max_win_streak = 0
    max_loss_streak = 0
    current_streak_type = None
    
    for trade in trades_sorted:
        if trade.resultado == 'ganancia':
            if current_streak_type == 'win':
                current_streak += 1
            else:
                current_streak = 1
                current_streak_type = 'win'
            max_win_streak = max(max_win_streak, current_streak)
        elif trade.resultado == 'perdida':
            if current_streak_type == 'loss':
                current_streak += 1
            else:
                current_streak = 1
                current_streak_type = 'loss'
            max_loss_streak = max(max_loss_streak, current_streak)
        else:
            current_streak = 0
            current_streak_type = None
    
    # Análisis por día de semana
    day_order = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    day_stats = {}
    for trade in trades:
        day_name = trade.fecha.strftime('%A')
        day_spanish = {'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles', 'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'}
        day_es = day_spanish.get(day_name, day_name)
        
        if day_es not in day_stats:
            day_stats[day_es] = {'count': 0, 'wins': 0, 'pnl': 0}
        
        day_stats[day_es]['count'] += 1
        if trade.resultado == 'ganancia':
            day_stats[day_es]['wins'] += 1
        day_stats[day_es]['pnl'] += float(trade.pnl or 0)
    
    for day in day_stats:
        if day_stats[day]['count'] > 0:
            day_stats[day]['win_rate'] = round((day_stats[day]['wins'] / day_stats[day]['count'] * 100), 1)
        else:
            day_stats[day]['win_rate'] = 0
    
    # Ordenar días en orden lógico
    day_stats_sorted = {day: day_stats[day] for day in day_order if day in day_stats}
    
    # Profit factor
    gross_profit = trades.filter(resultado='ganancia').aggregate(total=Sum('pnl'))['total'] or 0
    gross_loss = abs(trades.filter(resultado='perdida').aggregate(total=Sum('pnl'))['total'] or 0)
    profit_factor = round(gross_profit / gross_loss, 2) if gross_loss > 0 else 0
    
    # Expectativa matemática
    avg_win = trades.filter(resultado='ganancia').aggregate(avg=Avg('pnl'))['avg'] or 0
    avg_loss = abs(trades.filter(resultado='perdida').aggregate(avg=Avg('pnl'))['avg'] or 0)
    win_prob = ganados / total if total > 0 else 0
    loss_prob = perdidos / total if total > 0 else 0
    expectancy = round((win_prob * avg_win) - (loss_prob * avg_loss), 2)
    
    context = get_context()
    context['miembro'] = miembro
    context['total'] = total
    context['ganados'] = ganados
    context['perdidos'] = perdidos
    context['breakeven'] = breakeven
    context['win_rate'] = win_rate
    context['pnl_total'] = pnl_total
    context['avg_pnl'] = avg_pnl
    context['best_trade'] = best_trade
    context['worst_trade'] = worst_trade
    context['longs_count'] = longs.count()
    context['shorts_count'] = shorts.count()
    context['long_win_rate'] = long_win_rate
    context['short_win_rate'] = short_win_rate
    context['emocion_stats'] = emocion_stats
    context['max_win_streak'] = max_win_streak
    context['max_loss_streak'] = max_loss_streak
    context['day_stats'] = day_stats_sorted
    context['profit_factor'] = profit_factor
    context['expectancy'] = expectancy
    context['gross_profit'] = gross_profit
    context['gross_loss'] = gross_loss
    
    return render(request, 'core/analytics.html', context)


@login_required
def okx_refresh_account_view(request):
    """Refresca la información de la cuenta OKX"""
    try:
        miembro = request.user.miembro
        config = OKXApiConfig.objects.get(miembro=miembro, is_active=True)
    except (Miembro.DoesNotExist, OKXApiConfig.DoesNotExist):
        messages.error(request, 'No hay configuración de OKX activa.')
        return redirect('core:dashboard')

    try:
        fetch_okx_account_info(config)
        
        if config.okx_uid:
            messages.success(request, f'✅ Cuenta OKX actualizada. UID: {config.okx_uid}')
        else:
            messages.warning(request, '⚠️ No se pudo obtener el UID. Verifica que tu API Key tenga permisos de "Read" para Account.')
    except Exception as e:
        messages.error(request, f'Error al refrescar: {str(e)}')
    
    return redirect('core:dashboard')


@login_required
def okx_debug_view(request):
    """Vista de debug para ver qué devuelve la API de OKX"""
    try:
        miembro = request.user.miembro
        config = OKXApiConfig.objects.get(miembro=miembro, is_active=True)
    except (Miembro.DoesNotExist, OKXApiConfig.DoesNotExist):
        return JsonResponse({'error': 'No hay configuración de OKX activa'}, status=400)

    from datetime import datetime, timezone as dt_timezone
    
    api_key = config.api_key
    api_secret = config.api_secret
    passphrase = config.passphrase
    
    timestamp = datetime.now(dt_timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
    method = 'GET'
    request_path = '/api/v5/account/balance'
    
    sign_str = timestamp + method + request_path
    signature = hmac.new(
        api_secret.encode('utf-8'),
        sign_str.encode('utf-8'),
        hashlib.sha256
    ).digest()
    signature = base64.b64encode(signature).decode('utf-8')
    
    headers = {
        'OK-ACCESS-KEY': api_key,
        'OK-ACCESS-SIGN': signature,
        'OK-ACCESS-TIMESTAMP': timestamp,
        'OK-ACCESS-PASSPHRASE': passphrase,
        'Content-Type': 'application/json',
    }
    
    try:
        response = requests.get(
            f'https://www.okx.com{request_path}',
            headers=headers,
            timeout=30
        )
        
        result = {
            'status_code': response.status_code,
            'response': response.json(),
            'timestamp': timestamp,
            'request_path': request_path,
        }
        
        return JsonResponse(result, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
def okx_csv_upload_view(request):
    try:
        miembro = request.user.miembro
    except Miembro.DoesNotExist:
        messages.error(request, 'No se encontró tu perfil.')
        return redirect('core:import')

    form = OKXCsvUploadForm(request.POST, request.FILES)
    if form.is_valid():
        csv_file = request.FILES['csv_file']
        try:
            trades_imported = import_okx_csv(miembro, csv_file)
            messages.success(request, f'✅ {trades_imported} trades importados desde CSV')
        except Exception as e:
            messages.error(request, f'Error al importar CSV: {str(e)}')
    else:
        messages.error(request, 'Error en el archivo CSV.')
    
    return redirect('core:dashboard')


def sync_okx_trades(miembro, config):
    """Sincroniza trades desde la API de OKX usando fills-history (3 meses de historial)"""
    from datetime import datetime, timezone as dt_timezone
    import logging
    
    logger = logging.getLogger(__name__)
    
    api_key = config.api_key
    api_secret = config.api_secret
    passphrase = config.passphrase
    
    inst_types = ['SPOT', 'SWAP', 'FUTURES', 'MARGIN']
    trades_synced = 0
    
    for inst_type in inst_types:
        after = None
        page = 0
        
        while page < 20:
            timestamp = datetime.now(dt_timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.') + f'{datetime.now(dt_timezone.utc).microsecond // 1000:03d}Z'
            method = 'GET'
            
            request_path = f'/api/v5/trade/fills-history?instType={inst_type}'
            if after:
                request_path += f'&after={after}'
            
            sign_str = timestamp + method + request_path
            signature = hmac.new(
                api_secret.encode('utf-8'),
                sign_str.encode('utf-8'),
                hashlib.sha256
            ).digest()
            signature = base64.b64encode(signature).decode('utf-8')
            
            headers = {
                'OK-ACCESS-KEY': api_key,
                'OK-ACCESS-SIGN': signature,
                'OK-ACCESS-TIMESTAMP': timestamp,
                'OK-ACCESS-PASSPHRASE': passphrase,
                'Content-Type': 'application/json',
            }
            
            try:
                response = requests.get(
                    f'https://www.okx.com{request_path}',
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code != 200:
                    logger.warning(f'OKX API error for {inst_type} fills-history: {response.status_code} - {response.text}')
                    break
                
                data = response.json()
                if data.get('code') != '0':
                    logger.warning(f'OKX error for {inst_type} fills-history: {data.get("msg")}')
                    break
                
                fills = data.get('data', [])
                if not fills:
                    logger.info(f'OKX {inst_type} fills-history: No more data')
                    break
                
                logger.info(f'OKX {inst_type} fills-history page {page}: {len(fills)} fills found')
                
                for fill in fills:
                    trade_id = fill.get('tradeId', '')
                    
                    if not trade_id:
                        continue
                    
                    if TradeJournal.objects.filter(miembro=miembro, okx_order_id=trade_id).exists():
                        continue
                    
                    inst_id = fill.get('instId', '')
                    side = fill.get('side', '')
                    fill_price = fill.get('fillPx', '0')
                    fill_size = fill.get('fillSz', '0')
                    fee = fill.get('fee', '0')
                    fee_currency = fill.get('feeCcy', '')
                    fill_time = fill.get('ts', '')
                    
                    trade_type = 'long' if side == 'buy' else 'short'
                    
                    trade_date = timezone.now().date()
                    trade_time = None
                    
                    if fill_time:
                        try:
                            ts = int(fill_time) / 1000
                            dt = datetime.fromtimestamp(ts)
                            trade_date = dt.date()
                            trade_time = dt.time()
                        except:
                            pass
                    
                    TradeJournal.objects.create(
                        miembro=miembro,
                        fecha=trade_date,
                        hora_entrada=trade_time,
                        par=inst_id.replace('-', '/') if inst_id else 'UNKNOWN',
                        mercado='cripto',
                        tipo=trade_type,
                        estrategia='okx_auto',
                        precio_entrada=float(fill_price) if fill_price else 0,
                        precio_salida=float(fill_price) if fill_price else 0,
                        lotes=float(fill_size) if fill_size else 0,
                        resultado='pendiente',
                        pnl=0,
                        fuente='okx_api',
                        okx_order_id=trade_id,
                        notas=f'OKX Fill - Fee: {fee} {fee_currency}' if fee else '',
                    )
                    trades_synced += 1
                
                after = fills[-1].get('tradeId')
                page += 1
                
                if not after:
                    break
            
            except Exception as e:
                logger.error(f'Error syncing {inst_type} fills-history: {str(e)}')
                break
    
    config.last_sync = timezone.now()
    config.save()
    
    logger.info(f'Total trades synced: {trades_synced}')
    return trades_synced


def import_okx_csv(miembro, csv_file):
    """Importa trades desde un archivo CSV de OKX"""
    decoded_file = csv_file.read().decode('utf-8').splitlines()
    reader = csv.DictReader(decoded_file)
    
    trades_imported = 0
    
    for row in reader:
        try:
            inst_id = row.get('Instrument', row.get('instId', ''))
            side = row.get('Side', row.get('side', '')).lower()
            fill_price = row.get('Fill Price', row.get('avgPx', '0'))
            fill_size = row.get('Fill Size', row.get('accFillSz', '0'))
            pnl = row.get('PnL', row.get('pnl', '0'))
            fee = row.get('Fee', row.get('fee', '0'))
            order_id = row.get('Order ID', row.get('ordId', ''))
            fill_time = row.get('Fill Time', row.get('fillTime', ''))
            
            if not inst_id or TradeJournal.objects.filter(miembro=miembro, okx_order_id=order_id).exists():
                continue
            
            trade_type = 'long' if side == 'buy' else 'short'
            pnl_val = float(pnl) if pnl else 0
            resultado = 'ganancia' if pnl_val > 0 else 'perdida' if pnl_val < 0 else 'breakeven'
            
            trade_date = timezone.now().date()
            trade_time = None
            
            if fill_time:
                try:
                    dt = datetime.strptime(fill_time, '%Y-%m-%d %H:%M:%S')
                    trade_date = dt.date()
                    trade_time = dt.time()
                except:
                    pass
            
            TradeJournal.objects.create(
                miembro=miembro,
                fecha=trade_date,
                hora_entrada=trade_time,
                par=inst_id.replace('-', '/'),
                mercado='cripto',
                tipo=trade_type,
                estrategia='okx_csv',
                precio_entrada=float(fill_price) if fill_price else 0,
                precio_salida=float(fill_price) if fill_price else 0,
                lotes=float(fill_size) if fill_size else 0,
                resultado=resultado,
                pnl=pnl_val,
                fuente='okx_csv',
                okx_order_id=order_id,
            )
            trades_imported += 1
        except Exception:
            continue
    
    return trades_imported
