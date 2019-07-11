from django.shortcuts import redirect , reverse


# Create your views here.


def index(request):
    if request.user.is_authenticated():
        return redirect(reverse('userena_profile_detail', kwargs={'username': request.user.username}))

    else:
        return redirect('/static/index.html')



