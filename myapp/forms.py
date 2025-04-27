# tracker/forms.py
from django import forms
from .models import Transaction, Category, Budget

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_type', 'category', 'description']
    
    def __init__(self, *args, **kwargs):
        # Extract user from kwargs before calling parent __init__
        user = kwargs.pop('user', None)
        super(TransactionForm, self).__init__(*args, **kwargs)
        
        # Filter category queryset based on the user
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)

# class TransactionForm(forms.ModelForm):
#     class Meta:
#         model = Transaction
#         fields = ['amount', 'transaction_type', 'description', 'category']

#     transaction_type = forms.ChoiceField(
#         choices=Transaction.TRANSACTION_TYPES,
#         widget=forms.Select(attrs={'class': 'form-control'})
#     )
#     amount = forms.DecimalField(
#         max_digits=10, decimal_places=2,
#         widget=forms.NumberInput(attrs={'class': 'form-control'})
#     )
#     description = forms.CharField(
#         widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
#         required=False
#     )
#     category = forms.ModelChoiceField(
#         queryset=Category.objects.all(),
#         widget=forms.Select(attrs={'class': 'form-control'}),
#         required=False
#     )
    
# Category Form
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['monthly_income', 'monthly_expense_limit']
