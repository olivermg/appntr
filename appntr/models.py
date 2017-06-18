from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.db.models import Q
from django.conf import settings
from django.db import models, IntegrityError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from uuid import uuid4

import re


class Timeslot(models.Model):
    class Meta:
        app_label = 'appntr'
    once = models.BooleanField(default=True)
    datetime = models.DateTimeField()
    interviewer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="slots")



class Application(models.Model):
    class Meta:
        app_label = 'appntr'

    class STATES:
        NEW = "new"
        TO_INVITE = "to_invite"
        INVITED = "invited"
        INTERVIEWING = "interview"
        ACCEPTED = "accepted"
        REJECTED = "rejected"


    added_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)
    state = models.CharField(max_length=25, choices= [
        (STATES.NEW, "new"),
        (STATES.TO_INVITE, "To invite"),
        (STATES.INVITED, "Invited"),
        (STATES.INTERVIEWING, "Being interviewed"),
        (STATES.ACCEPTED, "Accepted"),
        (STATES.REJECTED, "Rejected")
    ], default=STATES.NEW)
    # actual application 

    # personal data
    first_name = models.CharField(max_length=255, verbose_name="Vorname")
    last_name = models.CharField(max_length=255, verbose_name="Nachname")
    gender = models.CharField(max_length=30, verbose_name="Geschlecht")
    email = models.CharField(max_length=255, verbose_name="E-Mail Adresse", help_text="Unter welcher E-Mail Adresse können wir Dich persönlich erreichen?")
    phone = models.CharField(max_length=255, verbose_name="Telefonnummer", help_text="Unter welcher Telefonnummer können wir Dich persönlich erreichen?")
    country = models.CharField(max_length=25, verbose_name="Bundesland", help_text="In welchem Bundesland hast du deinen Erstwohnsitz?")
    internet_profiles = models.TextField(null=True, blank=True, verbose_name="Falls gegeben: Persönliche Webseite(n), Profile auf Sozialen Netzwerken (Xing, Facebook, Twitter und so weiter)")

    # application
    motivation = models.TextField()
    skills = models.TextField()
    ethical_dilemma = models.TextField()

    @property
    def winner(self):
        votes = dict(y=0, n=0, a=0)
        for v in self.votes.all():
            votes[v.vote] += 1

        tally = sum(dict.values())
        if tally < 5:
            # None yet
            return None

        if votes['y'] > votes['n']:
            if votes['y'] <= votes['a']:
                return 'abstain'
            
            return "yay"
        return "nay" 


class UserVote(models.Model):
    class Meta:
        app_label = 'appntr'
    added_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="votes")
    application = models.ForeignKey(Application, related_name="votes")
    vote = models.CharField(max_length=1, choices=[('y', 'yay'), ('n', 'nay'), ('a', 'abstain')])

    class Meta:
        unique_together = (("user", "application"),)


class Comment(models.Model):
    class Meta:
        app_label = 'appntr'
    added_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="comments")
    application = models.ForeignKey(Application, related_name="comments")
    comment = models.TextField(blank=True, null=True)


class Invite(models.Model):
    class Meta:
        app_label = 'appntr'

    id = models.CharField(max_length=10, primary_key=True)
    application = models.OneToOneField(Application, null=True, default=None, related_name="invite")
    added_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)
    reminded_at = models.DateTimeField(blank=True, null=True, default=None)


class Appointment(models.Model):
    class Meta:
        app_label = 'appntr'

    datetime = models.DateTimeField()
    application = models.OneToOneField(Application, related_name="appointment")
    interview_lead = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="leading")
    interview_snd = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="second")  

