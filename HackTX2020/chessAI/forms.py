from django import forms
    
class UpdateBoardForm(forms.Form):
    RESET=[('resetBoard','resetBoard'),
            ('dontResetBoard','dontResetBoard')]
    move = forms.CharField(help_text="Enter a PGN move.")
    reset = forms.ChoiceField(required=False,
        widget=forms.RadioSelect,
        choices=RESET)
    def clean(self):
        cleaned_data = super(UpdateBoardForm, self).clean()
        name = cleaned_data.get('move')
        if not name:
            raise forms.ValidationError('You have to write something!')
        if len(name) > 10:
            raise forms.ValidationError('INput is too long!!')
        return cleaned_data