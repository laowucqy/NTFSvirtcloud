import re
from django import forms
from django.utils.translation import ugettext_lazy as _


class NewVMForm(forms.Form):
    name = forms.CharField(error_messages={'required': _('No Virtual Machine name has been entered')},
                           max_length=20)
    vcpu = forms.IntegerField(error_messages={'required': _('No VCPU has been entered')})
    host_model = forms.BooleanField(required=False)
    disk = forms.IntegerField(required=False)
    memory = forms.IntegerField(error_messages={'required': _('No RAM size has been entered')})
    networks = forms.CharField(error_messages={'required': _('No Network pool has been choice')})
    storage = forms.CharField(max_length=20, required=False)
    template = forms.CharField(required=False)
    images = forms.CharField(required=False)
    cache_mode = forms.CharField(error_messages={'required': _('Please select HDD cache mode')})
    hdd_size = forms.IntegerField(required=False)
    meta_prealloc = forms.BooleanField(required=False)
    virtio = forms.BooleanField(required=False)
    mac = forms.CharField(required=False)

    def clean_name(self):
        name = self.cleaned_data['name']
        have_symbol = re.match('^[a-zA-Z0-9._-]+$', name)
        if not have_symbol:
            raise forms.ValidationError(_('The name of the virtual machine must not contain any special characters'))
        elif len(name) > 20:
            raise forms.ValidationError(_('The name of the virtual machine must not exceed 20 characters'))
        return name
