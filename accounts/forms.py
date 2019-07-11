from accounts.models import Bot, Advert, AdvertBotSet,Payout,BotTheme
from django import forms

from django.utils.translation import ugettext_lazy as _
from phonenumber_field.formfields import PhoneNumberField
from userena.utils import get_profile_model
from userena.forms import SignupForm, EditProfileForm


class BotUsersAddForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea, required=False,label='(в одной строке один токен пользователя)' )
    import_bot_users_file = forms.FileField(required=False, label='или загрузите пользователей из файла')


class BotAddForm(forms.ModelForm):
    class Meta:
        model = Bot
        exclude = ['user']


class AdvertAddForm(forms.ModelForm):
    class Meta:
        model = Advert
        exclude = ['user']

class PayoutAddForm(forms.ModelForm):
    class Meta:
        model = Payout
        exclude = ['user','pub_date']

class AdvertBotSetAddForm(forms.ModelForm):
    class Meta:
        model = AdvertBotSet
        exclude = ['advert']
        widgets = {
            'prefered_datetime': forms.DateTimeInput(attrs={'class': 'bot_calendar'})
        }


class SignupFormExtra(SignupForm):
    first_name = forms.CharField(label=_(u'First name'),
                                 max_length=30,
                                 required=False)

    last_name = forms.CharField(label=_(u'Last name'),
                                max_length=30,
                                required=False)

    ADVERTISER = 'ADV'
    BOTHOST = 'HST'
    USER_TYPE_CHOICES = (
        (ADVERTISER, 'Advertiser'),
        (BOTHOST, 'Bot host'),
    )
    phone_number = PhoneNumberField()
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES)

    field_order = ['first_name', 'last_name']

    def save(self, commit=True):
        """
        Override the save method to save the first and last name to the user
        field.

        """
        # First save the parent form and get the user.
        new_user = super(SignupFormExtra, self).save()

        # Get the profile, the `save` method above creates a profile for each
        # user because it calls the manager method `create_user`.
        # See: https://github.com/bread-and-pepper/django-userena/blob/master/userena/managers.py#L65
        user_profile = new_user.my_profile
        user_profile.user.first_name = self.cleaned_data['first_name']
        user_profile.user.last_name = self.cleaned_data['last_name']
        user_profile.user_type = self.cleaned_data['user_type']
        user_profile.phone_number = self.cleaned_data['phone_number']
        user_profile.privacy = 'closed'
        user_profile.user.save()
        user_profile.save()

        # Userena expects to get the new user from this form, so return the new
        # user.
        return new_user


class EditProfileFormExtra(EditProfileForm):
    class Meta:
        model = get_profile_model()
        exclude = ['user', 'privacy','wallet']

    def save(self, force_insert=False, force_update=False, commit=True):
        profile = super(EditProfileFormExtra, self).save(commit=commit)
        # Save first and last name
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

        return profile

def get_bot_theme_choices():
    fin_list=[(0,'All')]
    for item in BotTheme.objects.all():
        fin_list.append((item.id,item.name))
    return fin_list

class ThemeChoiceForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ThemeChoiceForm, self).__init__(*args, **kwargs)
        self.fields['theme_choice_field'] = forms.ChoiceField(
            choices=get_bot_theme_choices())
