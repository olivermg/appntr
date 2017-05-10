from django.contrib import admin
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from .helpers import update_application
from . import loomio
from .models import *

LOOMIO_URL = "https://www.loomio.org/d/{key}/asdf"


class ApplicationeAdmin(admin.ModelAdmin):
    list_display = ['name', 'priority', 'vielfalt', 'state', 'changed_at']
    ordering = ['changed_at', 'anon_name', 'state']
    actions = ['move_on', 'send_invite', 'decline']
    search_fields = ['actual_name', 'personal_content']


    def decline(self, request, queryset):
        for app in queryset:
            if app.state not in (Application.STATES.REJECTED,
                                 Application.STATES.INVITED,
                                 Application.STATES.BACKBURNER):
                self.message_user(request, "{} can not be rejected".format(app))
                continue

            EmailMessage(
                    'Ihre Bewerbung bei Demokratie in Bewegung',
                    render_to_string('email_decline.txt', context=dict(app=app)),
                    'robot@demokratie-in-bewegung.org',
                    [app.email],
                    reply_to=("bewerbungs-hilfe@demokratie-in-bewegung.org",)
                ).send()

            app.state = Application.STATES.DECLINED
            app.save()

            self.message_user(request, "{} abgelehnt".format(app))


    decline.short_description = "Decline this application"


    def send_invite(self, request, queryset):
        for app in queryset:
            if app.state != Application.STATES.TO_INVITE:
                self.message_user(request, "{} not invitable".format(app))
                continue


            name = app.real_name
            email = app.email

            inv_info = dict(name=name, email=email, application=app)

            if app.loomio_discussion_id:
                dc = loomio.get_discussion(app.loomio_discussion_id)
                inv_info['external_url'] = LOOMIO_URL.format(**dc)

            else:
                inv_info['extra_info'] = app.personal_content


            invite = Invite(**inv_info)
            invite.save()

            EmailMessage(
                    'Einladung zum Gespräch mit Demokratie in Bewegung',
                    render_to_string('email_invite.txt', context=dict(invite=invite)),
                    'robot@demokratie-in-bewegung.org',
                    [invite.email],
                    reply_to=("bewerbungs-hilfe@demokratie-in-bewegung.org",)
                ).send()

            app.state = Application.STATES.INVITED
            app.save()

            self.message_user(request, "{} eingeladen".format(app))


    send_invite.short_description = "Invite this application"

    def move_on(self, request, queryset):
        for app in queryset:
            self.message_user(request, update_application(app))

    move_on.short_description = "Move to next Step"



class InviteAdmin(admin.ModelAdmin):
    list_display = ['state', 'name', 'email', 'added_at', 'reminded_at', 'appointment']

    actions = ['send_reminder', 'resend']

    def resend(self, request, queryset):
        for invite in queryset:
            if invite.state != "open":
                self.message_user(request, "{} already accepted".format(invite))
                continue

            EmailMessage(
                    'Einladung zum Gespräch mit Demokratie in Bewegung - Korrektur des Links',
                    render_to_string('email_invite.txt', context=dict(invite=invite)),
                    'robot@demokratie-in-bewegung.org',
                    [invite.email],
                    reply_to=("bewerbungs-hilfe@demokratie-in-bewegung.org",)
                ).send()

            # invite.reminded_at = datetime.utcnow()
            # invite.save()

            self.message_user(request, "{} Korrektur versand".format(invite))

    resend.short_description = "Link Korrektur"


    def send_reminder(self, request, queryset):
        for invite in queryset:
            if invite.state != "open":
                self.message_user(request, "{} already accepted".format(invite))
                continue

            if invite.reminded_at:
                self.message_user(request, "{} already reminded".format(invite))
                continue

            EmailMessage(
                    'Einladung zum Gespräch mit Demokratie in Bewegung',
                    render_to_string('email_reminder.txt', context=dict(invite=invite)),
                    'robot@demokratie-in-bewegung.org',
                    [invite.email],
                    reply_to=("bewerbungs-hilfe@demokratie-in-bewegung.org",)
                ).send()

            invite.reminded_at = datetime.utcnow()
            invite.save()

            self.message_user(request, "{} Erinnerung versand".format(invite))

    send_reminder.short_description = "Send Reminder"



admin.site.register(Interviewer)
admin.site.register(Application, ApplicationeAdmin)
admin.site.register(Invite, InviteAdmin)
admin.site.register(Timeslot)
admin.site.register(Appointment)
admin.site.register(CfgOption)