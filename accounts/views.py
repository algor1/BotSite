from accounts.utils import import_bot_users,make_adv,make_payout,build_calendar_new
from accounts.models import Bot,Advert, MyProfile,BotUser, AdvertBotSet,Payout,BotTheme
from accounts.forms import EditProfileFormExtra,BotAddForm,BotUsersAddForm, AdvertAddForm, AdvertBotSetAddForm, PayoutAddForm,ThemeChoiceForm,SignupFormExtra

from userena.forms import EditProfileForm, SignupForm, SignupFormOnlyEmail, AuthenticationForm
from userena.views import profile_detail,ExtraContextTemplateView
from userena.utils import get_profile_model, get_user_profile
from userena import settings as userena_settings
from userena import signals as userena_signals
from userena.decorators import secure_required

from django.utils.translation import ugettext as _
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth import get_user_model,authenticate, login, logout
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.views.generic import DetailView

from guardian.decorators import permission_required_or_403

import datetime


# Create your views here.

def profile_detail_extra(request,username):

     user = get_object_or_404(get_user_model(), username__iexact=username)
     bots = Bot.objects.filter(user=user)
     adverts = Advert.objects.filter(user=user)
     payouts = Payout.objects.filter(user=user)
     return_userna_profile_detail = profile_detail(request,username,extra_context={'Bot':bots,'Advert':adverts,'Payout':payouts})

     return return_userna_profile_detail

@secure_required
@permission_required_or_403('change_profile', (get_profile_model(), 'user__username', 'username'))
def moderator_workplace(request,username):


     user = get_object_or_404(get_user_model(), username__iexact=username)
     adverts_for_moderation = Advert.objects.exclude(status='OK')
     payouts_for_moderation = Payout.objects.exclude(status='OK')
     users_for_moderation = MyProfile.objects.exclude(status='OK')

     return_userna_profile_detail = profile_detail(
          request,username,template_name='accounts/moderator.html',
          extra_context={'Users':users_for_moderation,
                         'Advert':adverts_for_moderation,
                         'Payout':payouts_for_moderation}
          )

     return return_userna_profile_detail

@secure_required
@permission_required_or_403('change_profile', (get_profile_model(), 'user__username', 'username'))
def bot_add (request, username,id=None, edit_profile_form=EditProfileForm,
                 template_name='accounts/bot_add.html', success_url=None,
                 extra_context=None, **kwargs):

    user = get_object_or_404(get_user_model(), username__iexact=username)
    if id:
        bot_instance = get_object_or_404(Bot,user=user, pk=id)
        form = BotAddForm(request.POST or None, request.FILES or None, instance=bot_instance)
        bot_user = BotUser.objects.filter(bot=bot_instance)
    else:
        form = BotAddForm(request.POST or None, request.FILES or None)
        bot_user = None

    buform = BotUsersAddForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            bot = form.save(commit=False)
            bot.user=user
            bot.save()
            if userena_settings.USERENA_USE_MESSAGES:
                messages.success(request, _('Bot sucsefully added'),
                                 fail_silently=True)

            redirect_to = reverse('userena_profile_detail', kwargs={'username': username})
            return redirect(redirect_to)

        if buform.is_valid():
            if id:

                text = buform.cleaned_data['text']
                if text:
                    import_bot_users(text.splitlines(),id)

                import_file = request.FILES.get('import_bot_users_file', False)

                if import_file:
                    import_bot_users(import_file.readlines(),id)

                if userena_settings.USERENA_USE_MESSAGES:
                    messages.success(request, _('User(s) sucsefully added'),
                                 fail_silently=True)
            else:
                if userena_settings.USERENA_USE_MESSAGES:
                    messages.error(request, _('Сначала добавьте бота'),
                                 fail_silently=True)

            redirect_to = reverse('userena_profile_detail', kwargs={'username': username})
            return redirect(redirect_to)

    if not extra_context: extra_context = dict()
    extra_context['BotUsers'] = bot_user
    extra_context['form'] = form
    extra_context['profile'] = get_user_profile(user=user)
    extra_context['buform'] = buform

    return ExtraContextTemplateView.as_view(template_name=template_name,
                                            extra_context=extra_context)(request)


@secure_required
@permission_required_or_403('change_profile', (get_profile_model(), 'user__username', 'username'))
def profile_edit_extra(request, username, edit_profile_form=EditProfileFormExtra,
                 template_name='userena/profile_form.html', success_url=None,
                 extra_context=None, **kwargs):
    """
    Edit profile.

    Edits a profile selected by the supplied username. First checks
    permissions if the user is allowed to edit this profile, if denied will
    show a 404. When the profile is successfully edited will redirect to
    ``success_url``.

    :param username:
        Username of the user which profile should be edited.

    :param edit_profile_form:

        Form that is used to edit the profile. The :func:`EditProfileForm.save`
        method of this form will be called when the form
        :func:`EditProfileForm.is_valid`.  Defaults to :class:`EditProfileForm`
        from userena.

    :param template_name:
        String of the template that is used to render this view. Defaults to
        ``userena/edit_profile_form.html``.

    :param success_url:
        Named URL which will be passed on to a django ``reverse`` function after
        the form is successfully saved. Defaults to the ``userena_detail`` url.

    :param extra_context:
        Dictionary containing variables that are passed on to the
        ``template_name`` template.  ``form`` key will always be the form used
        to edit the profile, and the ``profile`` key is always the edited
        profile.

    **Context**

    ``form``
        Form that is used to alter the profile.

    ``profile``
        Instance of the ``Profile`` that is edited.

    """
    user = get_object_or_404(get_user_model(), username__iexact=username)

    profile = get_user_profile(user=user)
    success_url = request.GET.get('next')
    user_initial = {'first_name': user.first_name,
                    'last_name': user.last_name}

    form = edit_profile_form(instance=profile, initial=user_initial)

    if request.method == 'POST':

        form = edit_profile_form(request.POST, request.FILES, instance=profile,
                                 initial=user_initial)

        if form.is_valid():

            profile = form.save()

            if userena_settings.USERENA_USE_MESSAGES:
                messages.success(request, _('Your profile has been updated.'),
                                 fail_silently=True)

            if success_url:
                # Send a signal that the profile has changed
                userena_signals.profile_change.send(sender=None,
                                                    user=user)
                redirect_to = success_url
            else: redirect_to = reverse('userena_profile_detail', kwargs={'username': username})
            return redirect(redirect_to)

    if not extra_context: extra_context = dict()
    extra_context['form'] = form
    extra_context['profile'] = profile
    return ExtraContextTemplateView.as_view(template_name=template_name,
                                            extra_context=extra_context)(request)


@secure_required
@permission_required_or_403('change_profile', (get_profile_model(), 'user__username', 'username'))
def advert_add(request, username, id=None, template_name='accounts/advert_add.html', success_url=None,
               extra_context=None, **kwargs):
    user = get_object_or_404(get_user_model(), username__iexact=username)
    if user.my_profile.status == 'OK':
        if id:
            advert_instance = get_object_or_404(Advert, user=user, pk=id)
            form = AdvertAddForm(request.POST or None, request.FILES or None, instance=advert_instance)
            advert_bot = AdvertBotSet.objects.filter(advert=advert_instance)
        else:
            form = AdvertAddForm(request.POST or None, request.FILES or None)
            advert_bot = None

        abform=AdvertBotSetAddForm(request.POST or None)
        if request.method == 'POST':
            if form.is_valid():
                advert = form.save(commit=False)
                advert.user = user
                if not advert.status:
                    advert.status = 'NEW'
                elif advert.user == request.user:
                    advert.status = 'WAIT'
                elif advert.status == 'OK'and request.user.is_superuser :
                    make_adv(advert)
                advert.save()
                if form.instance:
                    if userena_settings.USERENA_USE_MESSAGES:
                        messages.success(request, _('Adverts sucsefully moderated.'),
                                         fail_silently=True)
                    if request.GET.get('next'):
                        redirect_to = request.GET['next']
                    else:
                        redirect_to = reverse('userena_profile_detail', kwargs={'username': username})
                else:
                    redirect_to = reverse('userena_profile_detail', kwargs={'username': username})
                    if userena_settings.USERENA_USE_MESSAGES:
                        messages.success(request, _('Advert sucsefully added. Wait for moderation.'),
                                         fail_silently=True)


            if abform.is_valid():
                if id:
                    advert_bot=abform.save(commit=False)
                    advert_bot.advert=advert_instance
                    if request.POST.get("morning")=='on':
                        advert_bot.prefered_datetime=advert_bot.prefered_datetime.replace(hour=9)
                    advert_bot.save()

                    if userena_settings.USERENA_USE_MESSAGES:
                        messages.success(request, _('Bot sucsefully added'),
                                 fail_silently=True)
                else:
                    if userena_settings.USERENA_USE_MESSAGES:
                        messages.error(request, _('Сначала добавьте объявление'),
                                        fail_silently=True)
                redirect_to = reverse('userena_profile_detail', kwargs={'username': username})
                return redirect(redirect_to)





        if not extra_context: extra_context = dict()
        extra_context['form'] = form
        extra_context['profile'] = get_user_profile(user=user)
        extra_context['advert_bot'] = advert_bot
        extra_context['abform'] = abform
        for boundfield in form: print(boundfield)
        return ExtraContextTemplateView.as_view(template_name=template_name,
                                                extra_context=extra_context)(request)
    else:
        if userena_settings.USERENA_USE_MESSAGES:
            messages.error(request, _("You can't add advert!"),
                           fail_silently=True)

            messages.error(request, _("Your accound hasn't been moderated yet. Please scan or photo your passport to identify yourself. Then our moderator accept you to add advertisings"),
                           fail_silently=True)
        if request.GET.get('next'):
            redirect_to = request.GET['next']
        else:
            redirect_to = reverse('userena_profile_detail', kwargs={'username': username})
        return redirect(redirect_to)

@secure_required
@permission_required_or_403('change_profile', (get_profile_model(), 'user__username', 'username'))
def payout_add(request, username, id=None, template_name='accounts/payout_add.html', success_url=None,
               extra_context=None, **kwargs):
    user = get_object_or_404(get_user_model(), username__iexact=username)
    cards_num=Payout.objects.filter(user=user).exclude(cardout__isnull=True).exclude(cardout__exact='').count()
    if cards_num>2:
        cards=Payout.objects.filter(user=user).exclude(cardout__isnull=True).exclude(cardout__exact='')[cards_num-2:cards_num]
    else:
        cards=Payout.objects.filter(user=user).exclude(cardout__isnull=True).exclude(cardout__exact='')
    wallets_num=Payout.objects.filter(user=user).exclude(walletout__isnull=True).exclude(walletout__exact='').count()
    if wallets_num>2:
        wallets=Payout.objects.filter(user=user).exclude(walletout__isnull=True).exclude(walletout__exact='')[wallets_num-2:wallets_num]
    else:
        wallets=Payout.objects.filter(user=user).exclude(walletout__isnull=True).exclude(walletout__exact='')

    if user.my_profile.status == 'OK' or True:

        if id:
            payout_instance = get_object_or_404(Payout, user=user, pk=id)
            form = PayoutAddForm(request.POST or None, instance=payout_instance)

        else:
            form = PayoutAddForm(request.POST or None)

        if request.method == 'POST':
            if form.is_valid():
                payout = form.save(commit=False)
                payout.user = user
                if not payout.status:
                    payout.status = 'NEW'
                    payout.pub_date=timezone.now()
                elif payout.user == request.user:
                    payout.status = 'WAIT'
                elif payout.status == 'OK'and request.user.is_superuser :
                    make_payout(payout)
                if not payout.pub_date:
                    payout.pub_date=timezone.now()
                payout.save()
                if form.instance:
                    if userena_settings.USERENA_USE_MESSAGES:
                        messages.success(request, _('Payout sucsefully done.'),
                                         fail_silently=True)
                    if request.GET.get('next'):
                        redirect_to = request.GET['next']
                    else:
                        redirect_to = reverse('userena_profile_detail', kwargs={'username': username})
                else:
                    redirect_to = reverse('userena_profile_detail', kwargs={'username': username})
                    if userena_settings.USERENA_USE_MESSAGES:
                        messages.success(request, _('Payout sucsefully added. Wait for moderation.'),
                                         fail_silently=True)
                return redirect(redirect_to)
        if not extra_context: extra_context = dict()
        extra_context['form'] = form
        extra_context['profile'] = get_user_profile(user=user)
        extra_context['cards']=cards
        extra_context['wallets']=wallets
        return ExtraContextTemplateView.as_view(template_name=template_name,
                                                extra_context=extra_context)(request)

def bot_collection( request, extra_context=None):

    if not extra_context: extra_context = dict()
    template_name = 'accounts/bot_collection.html'
    form = ThemeChoiceForm(request.GET or None)
    bot_theme=BotTheme.objects.all()
    bot_theme_menu=BotTheme.objects.all()

    if request.method == 'GET':
        if form.is_valid():
            if form.cleaned_data["theme_choice_field"]=='0':
                bot_theme=BotTheme.objects.all()
            else:
                bot_theme=BotTheme.objects.filter(id=form.cleaned_data["theme_choice_field"])

    extra_context['bot_theme']=bot_theme
    extra_context['bot_theme_menu']=bot_theme_menu
    extra_context['form'] = form
    return ExtraContextTemplateView.as_view(template_name=template_name,
                                                extra_context=extra_context)(request)



class BotDetail(DetailView):
    model=Bot

def bot_detail( request,pk, extra_context=None):
    template_name = 'accounts/bot_detail.html'
    bot=get_object_or_404(Bot, pk=pk)
    today=timezone.now()
    botusers=BotUser.objects.filter(bot=bot).count()
    calendar=build_calendar_new(bot,today.day,today.month,today.year)

    if not extra_context: extra_context = dict()
    extra_context['bot']=bot
    extra_context['calendar']=calendar
    extra_context['today']=today
    extra_context['botusers']=botusers
    return ExtraContextTemplateView.as_view(template_name=template_name,
                                                extra_context=extra_context)(request)


@secure_required
def signup_signin_extra(request, signup_form=SignupFormExtra ,auth_form=AuthenticationForm,
           template_name='accounts/signup_signin_form.html', success_url=None,
           extra_context=None):
    # If signup is disabled, return 403
    if userena_settings.USERENA_DISABLE_SIGNUP:
        raise PermissionDenied

    # If no usernames are wanted and the default form is used, fallback to the
    # default form that doesn't display to enter the username.
    if userena_settings.USERENA_WITHOUT_USERNAMES and (signup_form == SignupForm):
        signup_form = SignupFormOnlyEmail

    formup = signup_form(request.POST or None)
    formin = auth_form(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if formup.is_valid():
            user = formup.save()
            # Send the signup complete signal
            userena_signals.signup_complete.send(sender=None,
                                                 user=user)
            if success_url: redirect_to = success_url
            else: redirect_to = reverse('userena_signup_complete',
                                        kwargs={'username': user.username})
            # A new signed user should logout the old one.
            if request.user.is_authenticated():
                logout(request)
            if (userena_settings.USERENA_SIGNIN_AFTER_SIGNUP and
                not userena_settings.USERENA_ACTIVATION_REQUIRED):
                user = authenticate(identification=user.email, check_password=False)
                login(request, user)
            return redirect(redirect_to)

        if formin.is_valid():
            identification, password, remember_me = (formin.cleaned_data['identification'],
                                                     formin.cleaned_data['password'],
                                                     formin.cleaned_data['remember_me'])
            user = authenticate(identification=identification,
                                password=password)
            if user.is_active:
                login(request, user)
                if remember_me:
                    request.session.set_expiry(userena_settings.USERENA_REMEMBER_ME_DAYS[1] * 86400)
                else: request.session.set_expiry(0)

                if userena_settings.USERENA_USE_MESSAGES:
                    messages.success(request, _('You have been signed in.'),
                                     fail_silently=True)

                #send a signal that a user has signed in
                userena_signals.account_signin.send(sender=None, user=user)
                # Whereto now?
                redirect_to  = reverse('userena_profile_detail',
                                        kwargs={'username': user.username})
                return redirect(redirect_to)
            else:
                return redirect(reverse('userena_disabled',
                                        kwargs={'username': user.username}))



    if not extra_context: extra_context = dict()
    extra_context['formup'] = formup
    extra_context['formin'] = formin

    return ExtraContextTemplateView.as_view(template_name=template_name,
                                            extra_context=extra_context)(request)




def bot_calendar_js( request,pk, extra_context=None):
    template_name = 'accounts/bot_calendar.js'
    bot=get_object_or_404(Bot, pk=pk)
    today=timezone.now()
    calendar=build_calendar_new(bot,today.day,today.month,today.year)

    if not extra_context: extra_context = dict()
    extra_context['bot']=bot
    extra_context['calendar']=calendar
    extra_context['today']=today
    return render(request, template_name, extra_context)


@secure_required
@permission_required_or_403('change_profile', (get_profile_model(), 'user__username', 'username'))
def money_add (request, username,template_name='accounts/money_add.html',
                 extra_context=None, **kwargs):

    user = get_object_or_404(get_user_model(), username__iexact=username)
    if not extra_context: extra_context = dict()
    extra_context['profile'] = get_user_profile(user=user)

    return ExtraContextTemplateView.as_view(template_name=template_name,
                                            extra_context=extra_context)(request)
