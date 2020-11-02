from django.db import models
from cabot.cabotapp.alert import AlertPlugin, AlertPluginUserData

from os import environ as env

from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import Context, Template

import logging
import requests

pushover_alert_url = "https://api.pushover.net/1/messages.json"
pushover_template = "Service {{ service.name }} {% if service.overall_status == service.PASSING_STATUS %}is back to normal{% else %}reporting {{ service.overall_status }} status{% endif %}: {{ scheme }}://{{ host }}{% url 'service' pk=service.id %}. {% if service.overall_status != service.PASSING_STATUS %}Checks failing: {% for check in service.all_failing_checks %}{% if check.check_category == 'Jenkins check' %}{% if check.last_result.error %} {{ check.name }} ({{ check.last_result.error|safe }}) {{jenkins_api}}job/{{ check.name }}/{{ check.last_result.job_number }}/console{% else %} {{ check.name }} {{jenkins_api}}/job/{{ check.name }}/{{check.last_result.job_number}}/console {% endif %}{% else %} {{ check.name }} {% if check.last_result.error %} ({{ check.last_result.error|safe }}){% endif %}{% endif %}{% endfor %}{% endif %}{% if alert %}{% for alias in users %} @{{ alias }}{% endfor %}{% endif %}"
pushover_update_template = '{{ service.unexpired_acknowledgement.user.email }} is working on service {{ service.name }} (status {{ service.overall_status }}) - acknowledged @ {{ service.unexpired_acknowledgement.time|date:"H:i" }}'


class PushoverAlert(AlertPlugin):
    name = "Pushover"
    author = "MattZK"

    def send_alert(self, service, users, duty_officers):
        alert = True
        pushover_userkeys = []
        users = list(users) + list(duty_officers)

        pushover_userkeys = [u.pushover_userkey for u in PushoverAlertUserData.objects.filter(user__user__in=users)]

        if service.overall_status == service.old_overall_status:
            return
        
        for key in pushover_userkeys:
            alert = True
            priority = 1

            if service.overall_status == service.WARNING_STATUS:
                priority = 0
            elif service.overall_status == service.ERROR_STATUS:
                priority = 1
            elif service.overall_status == service.CRITICAL_STATUS:
                priority = 2
            elif service.overall_status == service.PASSING_STATUS:
                priority = 0
                if service.old_overall_status == service.CRITICAL_STATUS:
                    # cancel the recurring crit
                    pass
            else:
                # something weird happened
                alert = False

            if not alert:
                return
            # now let's send
            c = Context({
                'service': service,
                'host': settings.WWW_HTTP_HOST,
                'scheme': settings.WWW_SCHEME,
                'jenkins_api': settings.JENKINS_API,
            })
            message = Template(pushover_template).render(c)
            self._send_pushover_alert(message, key=key, priority=priority)

    def _send_pushover_alert(self, message, key, priority=0):
        payload = {
            'token':env['PUSHOVER_TOKEN'],
            'user': key,
            'priority': priority,
            'title': 'Cabot ALERT',
            'message': message,
        }

        if priority == 2:
            payload['retry'] = 60
            payload['expire'] = 3600

        r = requests.post(pushover_alert_url, data=payload)

class PushoverAlertUserData(AlertPluginUserData):
    name = "Pushover Plugin"
    pushover_userkey = models.CharField(max_length=50, blank=True)

    def serialize(self):
        return {
            "pushover_userkey": self.pushover_userkey
        }
