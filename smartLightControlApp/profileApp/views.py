import io
import os
import sys

from django.contrib.auth.decorators import login_required
from django.core.management import call_command
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from listenerApp.models import LightingEvent, ModelsStorage

from .forms import UserProfileForm, ConsentForm
from .models import UserProfile

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from controllers.controller import Controller
from .train_models import train_and_save_models
from listenerApp.predict import ai_control


@login_required
def train_models(request):
    try:
        train_and_save_models(user=request.user)
        success = True
        message = "Модель було створено успішно!"
    except Exception as e:
        success = False
        message = f"Сталась помилка при створенні моделі: {str(e)}"

    return JsonResponse({'status': 'success' if success else 'error', 'message': message})

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import UserProfile

@login_required
def ai_control_enabled(request):
    if request.method == 'POST':
        user_profile = get_object_or_404(UserProfile, user=request.user)
        ai_control_enabled = request.POST.get('ai_control_enabled') == 'true'
        user_profile.ai_control_enabled = ai_control_enabled
        user_profile.save()
        if ai_control_enabled:
            # Start the ai_control function in the background
            from threading import Thread
            thread = Thread(target=ai_control, args=(request.user,))
            thread.start()
        return JsonResponse({'status': 'success', 'ai_control_enabled': ai_control_enabled})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
@login_required
def user_profile(request):
    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        profile = None

    models_storage_exists = ModelsStorage.objects.filter(user=user).exists()

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            form = UserProfileForm(request.POST, instance=profile)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = user
                profile.save()
                return redirect('profile')
        elif 'update_ai_control' in request.POST:
            ai_control_enabled = request.POST.get('give_control_to_model') == 'on'
            if profile:
                profile.ai_control_enabled = ai_control_enabled
                profile.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)

    lighting_event_count = LightingEvent.objects.filter(user=user).count()
    can_create_model = lighting_event_count >= 1000
    consent_form = ConsentForm(instance=profile)

    return render(request, 'profile.html', {
        'form': form,
        'consent_form': consent_form,
        'profile': profile,
        'can_create_model': can_create_model,
        'lighting_event_count': lighting_event_count,
        'models_storage_exists': models_storage_exists,
    })



@login_required
def try_connect(request):
    status = None
    access_token = ''
    company_domain = ''

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


@require_POST
@csrf_exempt
@login_required
def update_consent(request):
    user = request.user
    consent = request.POST.get('consent') == 'true'

    try:
        profile = UserProfile.objects.get(user=user)
        profile.consent_for_data_collection = consent
        profile.save()
        return JsonResponse({'status': 'success'})
    except UserProfile.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Profile not found'}, status=404)
