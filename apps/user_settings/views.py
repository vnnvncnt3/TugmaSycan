from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import UserSettings
from .forms import SettingsForm


@login_required
def settings_view(request):
    user_settings, _ = UserSettings.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = SettingsForm(request.POST, instance=user_settings)
        if form.is_valid():
            form.save()
            return redirect('user_settings:settings')
    else:
        form = SettingsForm(instance=user_settings)

    return render(request, 'user_settings/settings.html', {'form': form})