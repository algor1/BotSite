from accounts.models import Bot, BotUser,AdvertBotSet,Adv
from django.shortcuts import get_object_or_404
from django.utils import timezone
from userena.utils import get_user_profile
import datetime


def import_bot_users(text, id):
    bot = get_object_or_404(Bot, pk=id)
    for line in text:
        q = BotUser(token=line, bot=bot)
        q.save()

def make_adv(advert):
    bots = AdvertBotSet.objects.filter(advert=advert)
    for bot in bots:
        bot_users = BotUser.objects.filter(bot=bot.bot)
        for bot_user in bot_users:
            adv=Adv(advert =advert, text=advert.text, image=advert.image, login=advert.user.username, user=advert.user, pub_date=timezone.now(),bot_token=bot.bot.token,user_token=bot_user.token)
            adv.save()

def make_payout(payout):
    profile = get_user_profile(user=payout.user)
    profile.wallet-= float(payout.amount)
    profile.save()

def build_calendar(bot):
    today=timezone.now()
    cal_days_l=[]
    cal_months={}
    cal_months_l=[]
    delta = datetime.timedelta(days=1)

    for i in range(0,24):
        d=today+delta*i
        if d.month in cal_months:
            cal_months[d.month]+=1
        else:
            cal_months[d.month]=1
        busy=date_is_busy(d,bot)
        cal_days_l.append([d,busy[0],busy[1]])

    for k in sorted(cal_months.keys()):
        cal_months_l.append( [datetime.datetime(2017, k, 1,),cal_months[k]])

    return cal_days_l, cal_months_l

def date_is_busy(check_date,bot):
    bots=AdvertBotSet.objects.filter(bot=bot,prefered_datetime__year=check_date.year, prefered_datetime__month=check_date.month, prefered_datetime__day=check_date.day )
    print(bots)
    evening=False
    morning=False
    for b in bots:
        if b.prefered_datetime.hour>=15 or b.prefered_datetime.hour<3:
            evening=True
        else:
            morning= True
    return [morning,evening]

def build_calendar_new(bot,day_from,month,year):

    today=datetime.datetime(int(year),1,1)
    busy_days=[]
    delta = datetime.timedelta(days=1)
    d=today
    i=0
    while d.year==year:
        i+=1
        d=today+delta*i
        busy=date_is_busy(d,bot)
        if busy[0] or busy[1]:
            busy_days.append([d,busy[0],busy[1]])
    return busy_days




