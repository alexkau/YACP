from django import forms

class CappReportField(forms.Form):
    cappReportField = forms.FileField(
        label='Select a file'
    )
