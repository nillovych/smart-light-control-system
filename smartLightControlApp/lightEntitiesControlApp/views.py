import os
import sys

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from controllers.lamp import Lamp


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
