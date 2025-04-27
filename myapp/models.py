# tracker/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_migrate
from django.dispatch import receiver

# Model to represent transaction categories
# tracker/models.py
class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Add this field
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name


# Model to represent a financial transaction
class Transaction(models.Model):
    INCOME = 'income'
    EXPENSE = 'expense'
    
    TRANSACTION_TYPES = [
        (INCOME, 'Income'),
        (EXPENSE, 'Expense'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(
        max_length=7, choices=TRANSACTION_TYPES, default=EXPENSE
    )
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type.capitalize()} of {self.amount} on {self.date}"

# Model to store a user's budget
class Budget(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_expense_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"Budget for {self.user.username}"

@receiver(post_migrate)
def create_default_categories(sender, **kwargs):
    # Default categories we want to add
    default_categories = [
        'Food', 'Entertainment', 'Utilities', 'Rent', 'Transport', 'Healthcare', 'Other'
    ]

    for user in User.objects.all():
        for category_name in default_categories:
            # Only create categories for the user if they don't already exist
            if not Category.objects.filter(user=user, name=category_name).exists():
                Category.objects.create(user=user, name=category_name)

print("Default categories created for all users.")