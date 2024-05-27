import os
import sys

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import UserProfileForm
from .models import UserProfile

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from controllers.controller import Controller


@login_required
def user_profile(request):
    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = user  # Link the profile to the currently logged-in user
            profile.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'profile.html', {'form': form})


@login_required
def try_connect(request):
    status = None
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            access_token = form.cleaned_data['access_token']
            company_domain = form.cleaned_data['company_domain']

            # Create an instance of the Controller class
            controller = Controller(token=access_token, domain=company_domain)
            status = controller.verify_connection()

    form = UserProfileForm(initial={'access_token': access_token, 'company_domain': company_domain})

    return render(request, 'profile.html', {'message': status, 'form': form})


