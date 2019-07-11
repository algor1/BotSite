from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from userena.models import UserenaBaseProfile
from phonenumber_field.modelfields import PhoneNumberField
from tinymce import models as tinymce_models

import os


def get_image_path(instance, filename):
    return os.path.join(str(instance.user.username), filename)


class MyProfile(UserenaBaseProfile):
    user = models.OneToOneField(User,
                                unique=True,
                                verbose_name=_('user'),
                                related_name='my_profile')

    ADVERTISER = 'ADV'
    BOTHOST = 'HST'

    USER_TYPE_CHOICES = (
        (ADVERTISER, 'Advertiser'),
        (BOTHOST, 'Bot host'),
    )
    phone_number = PhoneNumberField(null=True)
    user_type = models.CharField(max_length=3,
                                 choices=USER_TYPE_CHOICES,
                                 default=ADVERTISER)
    passport = models.ImageField(upload_to=get_image_path, null=True, blank=True)
    NEW = 'NEW'
    WAIT = 'WAIT'
    OK = 'OK'
    PROFILE_STATUS_CHOICES = (
        (NEW, 'New'),
        (WAIT, 'On moderation'),
        (OK, 'OK'),
    )
    status = models.CharField(max_length=4,
                              choices=PROFILE_STATUS_CHOICES,
                              default=NEW, null=True, blank=True)
    wallet = models.FloatField (blank=True,default=0)


class Bot(models.Model):
    name = models.CharField(max_length=200, blank=True)
    theme = models.ForeignKey('BotTheme', on_delete=models.CASCADE)
    token = models.CharField(max_length=200)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='bots', null=True, blank=True)
    text = models.TextField( null=True, blank=True)

    def __str__(self):
        return self.theme.name + ' / ' +self.name


class BotTheme(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class BotUser(models.Model):
    token = models.CharField(max_length=200)
    bot = models.ForeignKey('Bot', on_delete=models.CASCADE)

    def __str__(self):
        return  self.bot.name + ' / ' + self.token


class Advert(models.Model):
    text = tinymce_models.HTMLField()
    image = models.ImageField(upload_to=get_image_path, null=True, blank=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    NEW = 'NEW'
    WAIT = 'WAIT'
    OK = 'OK'
    AD_STATUS_CHOICES = (
        (NEW, 'New'),
        (WAIT, 'On moderation'),
        (OK, 'OK'),
    )
    status = models.CharField(max_length=4, choices=AD_STATUS_CHOICES,
                              default=NEW, null=True, blank=True)


class AdvertBotSet(models.Model):
    bot = models.ForeignKey('Bot', on_delete=models.CASCADE)
    advert = models.ForeignKey('Advert',on_delete=models.CASCADE)
    prefered_datetime=models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.advert.id) + ' / ' + self.bot.name

class Adv(models.Model):
    advert = models.ForeignKey('Advert')
    text = tinymce_models.HTMLField(blank=True)
    image = models.ImageField(upload_to=get_image_path, null=True, blank=True)
    bot_token = models.CharField(max_length=200,null = True)
    user_token = models.CharField(max_length=200,null = True)
    login = models.CharField(max_length=200)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    pub_date = models.DateTimeField()
    prod_datetime = models.DateTimeField(null = True)

class Payout(models.Model):
    amount = models.FloatField (blank=True,default=0)
    walletout = models.CharField(max_length=200,null = True ,blank=True)
    walletoutname = models.CharField(max_length=200,null = True ,blank=True)
    cardout = models.CharField(max_length=200,null = True ,blank=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    pub_date = models.DateTimeField()

    NEW = 'NEW'
    WAIT = 'WAIT'
    OK = 'OK'
    AD_STATUS_CHOICES = (
        (NEW, 'New'),
        (WAIT, 'On moderation'),
        (OK, 'OK'),
    )
    status = models.CharField(max_length=4, choices=AD_STATUS_CHOICES,
                              default=NEW, null=True, blank=True)


    def __str__(self):
        return self.user.username + ' / ' +str(self.pub_date)

class BotImage(models.Model):
    bot = models.ForeignKey('Bot', on_delete=models.CASCADE)
    name = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='bots', null=True, blank=True)

    def __str__(self):
        return self.name
