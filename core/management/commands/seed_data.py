from django.core.management.base import BaseCommand
from core.models import SiteConfig, SocialLink, Sesion, SesionHorario, Video, NoticiaFuente, MusicaLink


class Command(BaseCommand):
    help = 'Carga datos iniciales desde el sitio original'

    def handle(self, *args, **options):
        self.stdout.write('Cargando datos iniciales...')

        config, _ = SiteConfig.objects.get_or_create(pk=1, defaults={
            'site_title': 'Creemos Capital',
            'site_description': 'Trading en vivo con estrategia C4',
            'whatsapp_number': '+57 315 326 3852',
            'whatsapp_url': 'https://wa.me/573153263852',
            'telegram_url': 'https://t.me/creemoscapitaloficial',
            'email': 'info@creemoscapital.com',
            'kick_channel': 'creemoscapital',
            'youtube_channel': '@creemoscapital',
            'youtube_channel_url': 'https://www.youtube.com/@creemoscapital',
            'google_form_url': 'https://forms.gle/gpwxCJwcXvEX2bU26',
            'okx_affiliate_url': 'https://www.okx.com/join/CREEMOS',
            'spotify_url': 'https://open.spotify.com/intl-es/artist/7JJXOml59BOQLztO0W1nL3',
            'youtube_music_url': 'https://music.youtube.com/channel/UCv4ma-yTMOqYYF_Ii5kv0zQ',
            'youtube_music_playlist_id': 'UUv4ma-yTMOqYYF_Ii5kv0zQ',
        })
        self.stdout.write(self.style.SUCCESS(f'  SiteConfig: {config.site_title}'))

        social_data = [
            ('YouTube', 'https://www.youtube.com/@CreemosCapital', '', 0),
            ('TikTok', 'https://www.tiktok.com/@creemoscapital', '', 1),
            ('Instagram', 'https://www.instagram.com/creemoscapital', '', 2),
            ('Facebook', 'https://www.facebook.com/people/Creemos-Capital/61564167813649/', '', 3),
            ('X / Twitter', 'https://x.com/creemoscapital', '', 4),
            ('Kick', 'https://kick.com/creemoscapital', '', 5),
        ]
        for name, url, icon, order in social_data:
            obj, created = SocialLink.objects.get_or_create(name=name, defaults={
                'url': url, 'icon_class': icon, 'order': order
            })
            if created:
                self.stdout.write(self.style.SUCCESS(f'  SocialLink: {name}'))

        sesiones_data = [
            ('New York', '🗽', 0, [
                ('Colombia / Perú / Ecuador', 'co pe ec', '8:00 PM - 5:00 AM'),
                ('Venezuela / Chile / USA', 've cl us', '9:00 PM - 6:00 AM'),
                ('México', 'mx', '7:00 PM - 4:00 AM'),
                ('Argentina', 'ar', '10:00 PM - 7:00 AM'),
                ('Reino Unido', 'gb', '2:00 AM - 11:00 AM'),
                ('España', 'es', '3:00 AM - 12:00 PM'),
            ]),
            ('Asia', '🌏', 1, [
                ('Colombia / Perú / Ecuador', 'co pe ec', '7:00 PM - 2:00 AM'),
                ('Venezuela / Chile / USA', 've cl us', '8:00 PM - 3:00 AM'),
                ('México', 'mx', '6:00 PM - 1:00 AM'),
                ('Argentina', 'ar', '9:00 PM - 4:00 AM'),
                ('Reino Unido', 'gb', '12:00 AM - 7:00 AM'),
                ('España', 'es', '1:00 AM - 8:00 AM'),
            ]),
            ('Europa', '🇪🇺', 2, [
                ('Colombia / Perú / Ecuador', 'co pe ec', '2:00 AM - 11:00 AM'),
                ('Venezuela / Chile / USA', 've cl us', '3:00 AM - 12:00 PM'),
                ('México', 'mx', '1:00 AM - 10:00 AM'),
                ('Argentina', 'ar', '4:00 AM - 1:00 PM'),
                ('Reino Unido', 'gb', '8:00 AM - 3:00 PM'),
                ('España', 'es', '9:00 AM - 4:00 PM'),
            ]),
        ]
        for nombre, emoji, order, horarios in sesiones_data:
            sesion, created = Sesion.objects.get_or_create(nombre=nombre, defaults={
                'emoji': emoji, 'order': order
            })
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Sesion: {nombre}'))
            for paises, bandera, hora in horarios:
                SesionHorario.objects.get_or_create(
                    sesion=sesion, paises=paises, hora=hora,
                    defaults={'bandera_codigo': bandera}
                )

        videos_data = [
            ('Trading para Novatos Sesión 1', 'VcX1bL4lyk0', 'novatos', 0),
            ('Trading para Novatos Sesión 2', 'k2MSeeZbEaQ', 'novatos', 1),
            ('Trading para Novatos Sesión 3', '6ZimHCukVzI', 'novatos', 2),
            ('La Estrategia C4 - Ep 1', 'O-s8F1EYgZo', 'estrategia', 0),
            ('La Estrategia C4 - Ep 2', 'SyskCkiNby8', 'estrategia', 1),
            ('La Estrategia C4 - Ep 3', 'ezvbivW95X4', 'estrategia', 2),
            ('La Estrategia C4 - Ep 4', 'mCSDxA4bjMA', 'estrategia', 3),
            ('La Estrategia C4 - Ep 5', 'l2HCP4BVG3s', 'estrategia', 4),
            ('La Estrategia C4 - Ep 6', '7xrAUPnKfFc', 'estrategia', 5),
            ('La Estrategia C4 - Ep 7', 'OvhAA3B6oYo', 'estrategia', 6),
            ('La Estrategia C4 - Ep 8', 'ySxbg7pZ0b8', 'estrategia', 7),
        ]
        for titulo, yt_id, cat, order in videos_data:
            obj, created = Video.objects.get_or_create(
                titulo=titulo, youtube_id=yt_id, categoria=cat,
                defaults={'order': order}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'  Video: {titulo}'))

        noticias_data = [
            ('Forex', 'https://es.investing.com/news/forex-news', 'Últimas noticias del mercado de divisas.', '', 0),
            ('Acciones', 'https://es.investing.com/news/stock-market-news', 'Noticias del mercado de acciones global.', '', 1),
            ('Criptomonedas', 'https://es.investing.com/news/cryptocurrency-news', 'Noticias del mundo crypto y blockchain.', '', 2),
            ('Análisis Técnico', 'https://es.investing.com/technical-analysis', 'Análisis y señales técnicas del mercado.', '', 3),
            ('Forex Factory News', 'https://www.forexfactory.com/news', 'Noticias y análisis de Forex Factory.', '', 4),
            ('Forex Factory Calendar', 'https://www.forexfactory.com/calendar', 'Calendario económico completo.', '', 5),
        ]
        for nombre, url, desc, icon, order in noticias_data:
            obj, created = NoticiaFuente.objects.get_or_create(nombre=nombre, defaults={
                'url': url, 'descripcion': desc, 'icono': icon, 'order': order
            })
            if created:
                self.stdout.write(self.style.SUCCESS(f'  NoticiaFuente: {nombre}'))

        musica_data = [
            ('spotify', config.spotify_url, 'Spotify', 0),
            ('youtube_music', config.youtube_music_url, 'YouTube Music', 1),
        ]
        for tipo, url, titulo, order in musica_data:
            obj, created = MusicaLink.objects.get_or_create(tipo=tipo, defaults={
                'url': url, 'titulo': titulo, 'order': order
            })
            if created:
                self.stdout.write(self.style.SUCCESS(f'  MusicaLink: {titulo}'))

        self.stdout.write(self.style.SUCCESS('\nDatos iniciales cargados correctamente.'))
