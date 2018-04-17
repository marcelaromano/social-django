from django import forms

class ResearcherForm(forms.Form):
    url = forms.CharField(label='URL', max_length=2048)
