# tracker/views.py

from django.shortcuts import render, redirect
from .models import Transaction, Category, Budget
from django.db import models
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from datetime import date

def dashboard(request):
    # Get all transactions
    transactions = Transaction.objects.all().order_by('-date')
    
    # Get the current month's budget (if exists)
    today = date.today()
    current_month = date(today.year, today.month, 1)
    budget = Budget.objects.filter(month=current_month).first()
    
    # Calculate total expenses and income
    expenses = transactions.filter(type='expense').aggregate(total=models.Sum('amount'))['total'] or 0
    income = transactions.filter(type='income').aggregate(total=models.Sum('amount'))['total'] or 0
    
    # Budget usage
    budget_used = (expenses / budget.amount) * 100 if budget else 0

    context = {
        'transactions': transactions,
        'budget': budget,
        'expenses': expenses,
        'income': income,
        'budget_used': round(budget_used, 2),
    }
    
    return render(request, 'tracker/dashboard.html', context)


def add_transaction(request):
    categories = Category.objects.all()

    if request.method == 'POST':
        category_id = request.POST.get('category')
        category = Category.objects.get(id=category_id) if category_id else None
        amount = request.POST['amount']
        date_value = request.POST['date']
        description = request.POST['description']
        transaction_type = request.POST['type']

        Transaction.objects.create(
            category=category,
            amount=amount,
            date=date_value,
            description=description,
            type=transaction_type
        )
        return redirect('dashboard')

    context = {
        'categories': categories,
    }
    return render(request, 'tracker/add_transaction.html', context)


def set_budget(request):
    today = date.today()
    current_month = date(today.year, today.month, 1)

    if request.method == 'POST':
        amount = request.POST['amount']
        # Update or create budget
        Budget.objects.update_or_create(
            month=current_month,
            defaults={'amount': amount}
        )
        return redirect('dashboard')

    return render(request, 'tracker/set_budget.html')


def analytics(request):
    transactions = Transaction.objects.all()

    if not transactions:
        return render(request, 'tracker/analytics.html', {'no_data': True})

    # DataFrame
    df = pd.DataFrame(list(transactions.values('date', 'amount', 'type', 'category__name')))
    df['date'] = pd.to_datetime(df['date'])

    # Expenses vs Income Plot
    df_expenses = df[df['type'] == 'expense'].groupby('date').sum()
    df_income = df[df['type'] == 'income'].groupby('date').sum()

    plt.figure(figsize=(10, 5))
    plt.plot(df_expenses.index, df_expenses['amount'], label='Expenses', color='red')
    plt.plot(df_income.index, df_income['amount'], label='Income', color='green')
    plt.legend()
    plt.title('Income vs Expenses Over Time')

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')

    return render(request, 'tracker/analytics.html', {'graph': graph})
