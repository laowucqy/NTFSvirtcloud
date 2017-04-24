# coding: utf-8
from django import forms
from models import Flavor

class FlavorForm(forms.ModelForm):
    class Meta:
        model = Flavor
        fields = [
            "label", "memory","vcpu","disk"
        ]
