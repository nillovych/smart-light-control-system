import os
import sys

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import SignupForm, LoginForm

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from controllers.controller import Controller
from controllers.lamp import Lamp


# Create your views here.
# Home page
@login_required
def index(request):
    user = request.user

    if hasattr(user, 'userprofile'):
        profile = user.userprofile

        access_token = profile.access_token
        company_domain = profile.company_domain

        controller = Controller(token=access_token, domain=company_domain)
        if controller.verify_connection() == "Підключення успішне!":
            lights = controller.get_light_entities()
            if len(lights) > 0:

                return render(request, 'index.html', {'lights': lights})
            else:
                message = 'У вашому розпорядженні немає активних освітлювальних приладів'
        else:
            message = 'Ваше підключення некоректне або не відповідає. Перевірте його у профілі.'
    else:
        message = 'Ваш профіль не підключено. Перейдіть в профіль для підключення.'

    return render(request, 'index.html', {'message': message})


@login_required
def light_control(request, entity_id):
    user = request.user
    profile = user.userprofile

    access_token = profile.access_token
    company_domain = profile.company_domain

    lamp = Lamp(entity_id=entity_id, domain=company_domain, token=access_token)

    if request.method == 'POST':
        brightness = request.POST.get('brightness')
        if brightness:
            lamp.change_brightness(int(brightness))

        rgb_color_hex = request.POST.get('rgb_color')
        if rgb_color_hex:
            rgb_color = [int(rgb_color_hex[i:i + 2], 16) for i in (1, 3, 5)]
            lamp.change_color(rgb_color)

        lamp = Lamp(entity_id=entity_id, domain=company_domain, token=access_token)
    print(lamp.entity)
    brightness = lamp.entity['attributes']['brightness']
    if brightness is None:
        brightness = 0

    rgb = lamp.entity['attributes']['rgb_color']
    if rgb is not None:
        hex_color = '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
    else:
        hex_color = '#000000'
    return render(request, 'light_control.html',
                  {'name': lamp.entity['attributes']['friendly_name'], 'features': lamp.entity['attributes'], 'entity_id': entity_id, 'brightness': brightness,
                   'hex_color': hex_color})

    # signup page


def user_signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


# login page
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


# logout page
def user_logout(request):
    logout(request)
    return redirect('login')
