from typing import Union, List

from django.utils import timezone
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as __

from .models import HelpArticle
from .widgets import MarkdownEditor
from .logs_processing import log_action_ids, staff_logs, Log


def get_action_choices():
    choices = [(
        val,
        val.translate(str.maketrans('_', ' ')).capitalize()
    ) for val in log_action_ids.__dict__.values()]
    choices.insert(0, ('', '-Select action-'))
    return tuple(choices)


class HelpArticleForm(forms.ModelForm):

    class Meta:
        model = HelpArticle
        exclude = ('slug',)
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'help_text': MarkdownEditor()
        }


class HelpArticleEditForm(forms.ModelForm):

    class Meta:
        model = HelpArticle
        fields = ('description', 'help_text')
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'help_text': MarkdownEditor()
        }


class LogSearchForm(forms.Form):
    to = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Action happened to?'}),
        help_text='The user the action happened to',
        required=False
    )
    by = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Action was done by?'}),
        help_text='The user that did the action',
        required=False
    )
    user = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Action happened to or was by whom?'}),
        help_text='Logs that involve the user, This ignores by and to/includes both',
        required=False
    )
    action = forms.ChoiceField(
        choices=get_action_choices(),
        help_text='Action performed; Choose one',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    start_time = forms.SplitDateTimeField(widget=forms.SplitDateTimeWidget(
        attrs={'class': 'form-control'},
        date_format='dd/mm/yyyy',
        time_format='hh:mm',
        date_attrs={
            'type': 'date',
        },
        time_attrs={
            'type': 'time',
        }
    ), required=False, help_text='Filter logs from when')
    end_time = forms.SplitDateTimeField(widget=forms.SplitDateTimeWidget(
        date_format='dd/mm/yyyy',
        time_format='hh:mm',
        date_attrs={
            'type': 'date',
        },
        time_attrs={
            'type': 'time',
        }
    ), required=False, help_text='Filter logs up to')

    def clean_end_time(self):
        start_time = self.cleaned_data.get('start_time')
        end_time = self.cleaned_data.get('end_time')

        if type(start_time) == timezone.datetime and type(end_time) == timezone.datetime:
            if start_time > end_time:
                raise ValidationError(__('Start time cannot be more recent compared to end time.'))

        return end_time

    def get_logs(self) -> Union[List[Log], List]:
        logs = []
        if self.cleaned_data and type(self.cleaned_data) == dict:
            s_data = {
                key: value for key, value in zip(self.cleaned_data.keys(), self.cleaned_data.values()) if value
            }
            logs = staff_logs.search(**s_data)
        return logs
