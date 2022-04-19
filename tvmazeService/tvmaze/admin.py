from django.contrib import admin

# Register your models here.

# 别忘了导入ArticlerPost
from .models import Actor,Character,Show

# 注册模型类到admin中
admin.site.register(Actor)
admin.site.register(Character)
admin.site.register(Show)