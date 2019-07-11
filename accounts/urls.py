from django.conf.urls import url, include
from django.views.generic import TemplateView

from accounts.views import profile_detail_extra,moderator_workplace,profile_edit_extra,bot_add,advert_add,payout_add,signup_signin_extra,money_add
from accounts.forms import EditProfileFormExtra





urlpatterns = [
   url(r'^signup/$', signup_signin_extra, name='signup_signin'),
   url(r'^signin/$', signup_signin_extra, name='signup_signin'),
   url(r'^(?P<username>[\@\.\w-]+)/money_add/$', money_add,name='money_add'),
   url(r'^(?P<username>[\@\.\w-]+)/edit/$',
        profile_edit_extra,{'edit_profile_form': EditProfileFormExtra},
        name='profile_edit'),
   url(r'^(?P<username>[\@\.\w-]+)/addbot/$',bot_add,
       name='bot_add'),
   url(r'^(?P<username>[\@\.\w-]+)/editbot/(?P<id>\d+)/$',bot_add,
       name='bot_edit'),
   url(r'^(?P<username>[\@\.\w-]+)/addadvert/$',advert_add,
       name='advert_add'),
   url(r'^(?P<username>[\@\.\w-]+)/editadvert/(?P<id>\d+)/$',advert_add,
       name='advert_edit'),
   url(r'^(?P<username>[\@\.\w-]+)/addpayout/$',payout_add,
       name='payout_add'),
   url(r'^(?P<username>[\@\.\w-]+)/editpayout/(?P<id>\d+)/$',payout_add,
       name='payout_edit'),
   url(r'^(?P<username>[\@\.\w-]+)/moderator/$',moderator_workplace,
       name='moderator'),
   url(r'^(?P<username>(?!(signout|signup|signin)/)[\@\.\w-]+)/$',
       profile_detail_extra,
       name='userena_profile_detail'),
   url(r'^', include('userena.urls')),
 ]


