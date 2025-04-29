from django import forms

class NumberListForm(forms.Form):
    numbers = forms.CharField(
        label="Enter 9 numbers separated by commas",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 1,2,3,4,5,6,7,8,9'
        })
    )
