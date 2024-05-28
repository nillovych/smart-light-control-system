import os
import sys

from django.contrib.auth.decorators import login_required

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from controllers.lamp import Lamp

from django.shortcuts import render

from listenerApp.models import LightingEvent


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

        if request.user.userprofile.consent_for_data_collection:
            updated_lamp = Lamp(entity_id=entity_id, domain=company_domain, token=access_token)
            rgb_color = updated_lamp.entity['attributes']['rgb_color']
            brightness = updated_lamp.entity['attributes']['brightness']

            if brightness:
                new_record = LightingEvent(user=request.user, lamp_id=entity_id, brightness=int(brightness),
                                           state=True, color_r=rgb_color[0], color_g=rgb_color[1],
                                           color_b=rgb_color[2])
            else:
                new_record = LightingEvent(user=request.user, lamp_id=entity_id, state=False)

            new_record.save()

        lamp = Lamp(entity_id=entity_id, domain=company_domain, token=access_token)
    brightness = lamp.entity['attributes']['brightness']
    if brightness is None:
        brightness = 0

    rgb = lamp.entity['attributes']['rgb_color']
    if rgb is not None:
        hex_color = '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
    else:
        hex_color = '#000000'
    return render(request, 'light_control.html',
                  {'name': lamp.entity['attributes']['friendly_name'], 'features': lamp.entity['attributes'],
                   'entity_id': entity_id, 'brightness': brightness,
                   'hex_color': hex_color})
