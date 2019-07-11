from django.contrib import admin

# Register your models here.
from .models import Bot, BotTheme, Advert, BotUser, Adv,AdvertBotSet,Payout,BotImage

admin.site.register(Bot)
admin.site.register(BotTheme)
admin.site.register(BotImage)
admin.site.register(Advert)
admin.site.register(Adv)
admin.site.register(BotUser)
admin.site.register(AdvertBotSet)
admin.site.register(Payout)