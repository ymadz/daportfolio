# tracker/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from .forms import TransactionForm, BudgetForm, CategoryForm
from .models import Transaction, Budget, Category
from django.db.models import Sum
from decimal import Decimal, InvalidOperation
from django.core.paginator import Paginator
from django.db.models import Sum
from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO
from django.shortcuts import render
from .models import Transaction, Category
from django.contrib.auth.decorators import login_required


# Home Page View
def home(request):
    return render(request, 'tracker/home.html')

# Signup View
def signup(request):
    signup_form = UserCreationForm()
    login_form = AuthenticationForm()

    if request.method == 'POST':
        if 'signup' in request.POST:
            signup_form = UserCreationForm(request.POST)
            if signup_form.is_valid():
                user = signup_form.save()
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "There was an error with the signup form. Please try again.")
        
        elif 'login' in request.POST:
            login_form = AuthenticationForm(request, data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")

    return render(request, 'registration/signup.html', {
        'form': signup_form,
        'form_login': login_form,
    })

# Dashboard View (Protected view)
# Dashboard View (Protected view)
# Dashboard View (Protected view)
@login_required
def dashboard(request):
    # Get the user's transactions
    transactions = Transaction.objects.filter(user=request.user)
    total_income = transactions.filter(transaction_type=Transaction.INCOME).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expenses = transactions.filter(transaction_type=Transaction.EXPENSE).aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expenses

    # Get user’s budget info
    try:
        budget = Budget.objects.get(user=request.user)
        monthly_income = budget.monthly_income
        monthly_expense_limit = budget.monthly_expense_limit
        
        # Calculate the total spent (total_expenses is already calculated)
        spent = total_expenses
        remaining_budget = monthly_expense_limit - spent

        # Calculate progress for the budget (percentage of expense limit used)
        progress = (spent / monthly_expense_limit) * 100 if monthly_expense_limit else 0
    except Budget.DoesNotExist:
        budget = None
        spent = 0
        remaining_budget = 0
        progress = 0

    # Get the most recent transactions (for displaying in the table)
    recent_transactions = transactions.order_by('-date')[:5]  # Get last 5 transactions

    return render(request, 'tracker/dashboard.html', {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,
        'budget': budget,
        'spent': spent,
        'remaining_budget': remaining_budget,
        'progress': progress,  # Pass the progress data to the template
        'recent_transactions': recent_transactions,
    })


# Logout View (Logs out the user and redirects to home page)
def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def add_transaction(request):
    # Get all categories for the current user
    categories = Category.objects.filter(user=request.user)
    
    print(f"User: {request.user.username}, Categories: {categories.count()}")
    for cat in categories:
        print(f"- {cat.id}: {cat.name}")
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('dashboard')
    else:
        form = TransactionForm(user=request.user)
    
    context = {
        'form': form,
        'categories': list(categories),  # Convert QuerySet to list for debugging
    }
    
    return render(request, 'tracker/add_transaction.html', context)
    
def ensure_categories_for_user(user):
    """Ensure the user has the default categories"""
    default_categories = [
        'Food', 'Entertainment', 'Utilities', 'Rent', 'Transport', 'Healthcare', 'Other'
    ]
    
    for category_name in default_categories:
        Category.objects.get_or_create(user=user, name=category_name)
    
    return Category.objects.filter(user=user)

# @login_required
# def add_transaction(request):
#     if request.method == 'POST':
#         form = TransactionForm(request.POST)
#         if form.is_valid():
#             transaction = form.save(commit=False)
#             transaction.user = request.user  # Attach the logged-in user
#             transaction.save()
#             return redirect('dashboard')
#     else:
#         form = TransactionForm()

#     return render(request, 'tracker/create_transaction.html', {'form': form})

@login_required
def transaction_history(request):
    transactions = Transaction.objects.filter(user=request.user)
    return render(request, 'tracker/transaction_list.html', {'transactions': transactions})

@login_required
def create_or_edit_budget(request):
    # Try to fetch the user's existing budget
    budget = Budget.objects.filter(user=request.user).first()

    if request.method == "POST":
        # Get the form values
        try:
            # Get the 'monthly_income' and 'monthly_expense_limit' fields from the form
            monthly_income = request.POST.get('monthly_income')
            monthly_expense_limit = request.POST.get('monthly_expense_limit')

            # Ensure that the fields are not empty
            if not monthly_income or not monthly_expense_limit:
                return render(request, 'tracker/manage_budget.html', {'error': 'Both Monthly Income and Expense Limit are required.'})
            
            # Convert to Decimal
            monthly_income = Decimal(monthly_income)
            monthly_expense_limit = Decimal(monthly_expense_limit)

            # If a budget exists, update it; otherwise, create a new budget
            if budget:
                budget.monthly_income = monthly_income
                budget.monthly_expense_limit = monthly_expense_limit
                budget.save()
            else:
                Budget.objects.create(
                    user=request.user,
                    monthly_income=monthly_income,
                    monthly_expense_limit=monthly_expense_limit
                )

            return redirect('dashboard')  # Redirect to dashboard after saving the budget

        except (ValueError, InvalidOperation) as e:
            # Handle invalid value error (e.g., if it's not a valid decimal)
            return render(request, 'tracker/manage_budget.html', {'error': 'Invalid data. Please ensure you are entering valid numbers for both fields.'})

    # If GET request, render the form (with the existing budget data if available)
    return render(request, 'tracker/manage_budget.html', {'budget': budget})

@login_required
def manage_budget(request):
    budget, created = Budget.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = BudgetForm(instance=budget)

    return render(request, 'tracker/manage_budget.html', {'form': form})

@login_required
def transaction_list(request):
    # Get all transactions for the logged-in user
    transactions = Transaction.objects.filter(user=request.user)  # Correct filtering by user

    # Get all categories for filtering
    categories = Category.objects.filter(user=request.user)

    # Filter transactions by category if selected
    category_filter = request.GET.get('category')
    if category_filter:
        transactions = transactions.filter(category__id=category_filter)

    # Paginate transactions (10 per page)
    paginator = Paginator(transactions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'tracker/transaction_list.html', {
        'page_obj': page_obj,
        'categories': categories,
    })

@login_required
def create_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('transaction_list')
    else:
        form = TransactionForm()

    return render(request, 'tracker/add_transaction.html', {'form': form})

@login_required
def delete_transaction(request, pk):
    transaction = Transaction.objects.get(pk=pk, user=request.user)
    if transaction:
        transaction.delete()
    return redirect('transaction_list')

@login_required
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            return redirect('transaction_list')
    else:
        form = CategoryForm()

    return render(request, 'tracker/create_category.html', {'form': form})

@login_required
def summary_view(request):
    transactions = Transaction.objects.filter(user=request.user)

    # Summarize total income, expenses, balance
    total_income = transactions.filter(transaction_type=Transaction.INCOME).aggregate(Sum('amount'))['amount__sum'] or 0
    total_expenses = transactions.filter(transaction_type=Transaction.EXPENSE).aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expenses

    # Summarize by category
    income_by_category = transactions.filter(transaction_type=Transaction.INCOME).values('category__name').annotate(total=Sum('amount'))
    expenses_by_category = transactions.filter(transaction_type=Transaction.EXPENSE).values('category__name').annotate(total=Sum('amount'))

    return render(request, 'tracker/summary.html', {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,
        'income_by_category': income_by_category,
        'expenses_by_category': expenses_by_category,
    })
    
    
@login_required
def transaction_summary(request):
    transactions = Transaction.objects.filter(user=request.user)
    
    # If categories are missing, set them to "Unknown"
    transactions_data = transactions.values('category__name', 'amount', 'transaction_type')
    
    # Handle missing categories
    for transaction in transactions_data:
        if not transaction['category__name']:
            transaction['category__name'] = 'Unknown'
    
    # Convert the data to a Pandas DataFrame
    df = pd.DataFrame(transactions_data)
    
    # Summarize the data by category and transaction type
    summary = df.groupby(['category__name', 'transaction_type']).agg({'amount': 'sum'}).reset_index()

    # Use Matplotlib to generate a plot
    import matplotlib.pyplot as plt
    import numpy as np
    
    # Generate a bar plot showing income vs expense by category
    income_data = summary[summary['transaction_type'] == 'income']
    expense_data = summary[summary['transaction_type'] == 'expense']
    
    categories = income_data['category__name'].tolist()  # List of categories
    income_amounts = income_data['amount'].tolist()      # Income amounts
    expense_amounts = expense_data['amount'].tolist()    # Expense amounts
    
    # Handle cases where a category might not have an income or expense
    all_categories = set(categories) | set(expense_data['category__name'].tolist())
    all_categories = list(all_categories)

    income_amounts_full = [income_amounts[categories.index(c)] if c in categories else 0 for c in all_categories]
    expense_amounts_full = [expense_amounts[expense_data['category__name'].tolist().index(c)] if c in expense_data['category__name'].tolist() else 0 for c in all_categories]

    # Plotting
    x = np.arange(len(all_categories))
    width = 0.35  # Width of the bars
    
    fig, ax = plt.subplots()
    ax.bar(x - width/2, income_amounts_full, width, label='Income')
    ax.bar(x + width/2, expense_amounts_full, width, label='Expense')
    
    ax.set_ylabel('Amount')
    ax.set_title('Income vs Expense by Category')
    ax.set_xticks(x)
    ax.set_xticklabels(all_categories, rotation=45, ha="right")
    ax.legend()

    # Save the plot to a static directory or render it in the response
    plt.tight_layout()
    plt.savefig('transaction_summary_plot.png')  # Save to a file or render as image

    return render(request, 'tracker/transaction_summary.html', {
        'summary': summary,
        'plot_url': 'transaction_summary_plot.png',  # Send the plot path to the template
    })