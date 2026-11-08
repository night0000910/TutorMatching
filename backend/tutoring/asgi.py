import os
from django.core.asgi import get_asgi_application

# 1. 環境変数のセットとDjango初期化を最優先で実行
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tutoring.settings')
django_asgi_app = get_asgi_application()

# 2. Django初期化の後に Channels や自作アプリをインポート
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import signalingapp.routing


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            signalingapp.routing.websocket_urlpatterns
        )
    )
})