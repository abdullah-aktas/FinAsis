# Bu uygulamada şu anda admin paneline kayıtlı model yok. Eğer yeni model eklerseniz buradan kaydedebilirsiniz. 

from django.contrib import admin
from .models import Game

admin.site.register(Game) 