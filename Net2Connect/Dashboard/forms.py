from django import forms
from .models import Task
from django.contrib.auth.models import User

class TaskForm(forms.ModelForm):
    assigned_to = forms.ModelChoiceField(queryset=User.objects.none(), required=False)
    
    def __init__(self, *args, assignable_users=None, **kwargs):
        super().__init__(*args, **kwargs)
        if assignable_users is not None:
            self.fields['assigned_to'].queryset = assignable_users

    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to']

