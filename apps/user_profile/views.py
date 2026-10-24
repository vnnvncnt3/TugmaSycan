from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from .models import Profile
from .forms import AccountForm, ProfileForm


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    account_form = AccountForm(instance=request.user)
    profile_form = ProfileForm(instance=profile)
    password_form = PasswordChangeForm(user=request.user)

    if request.method == 'POST':
        if 'save_account' in request.POST:
            account_form = AccountForm(request.POST, instance=request.user)
            profile_form = ProfileForm(request.POST, instance=profile)
            if account_form.is_valid() and profile_form.is_valid():
                account_form.save()
                profile_form.save()
                if request.FILES.get('avatar'):
                    request.user.avatar = request.FILES['avatar']
                    request.user.save()
                return redirect('user_profile:profile')

        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                return redirect('user_profile:profile')

    return render(request, 'profile/profile.html', {
        'account_form': account_form,
        'profile_form': profile_form,
        'password_form': password_form,
    })