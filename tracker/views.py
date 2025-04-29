from django.shortcuts import render, redirect, get_object_or_404
from .models import Transaction, Category, Budget
from django.db import models
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from datetime import date
import csv
from django.http import HttpResponse
from django.contrib import messages
from decimal import Decimal

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
    
    # Budget usage and progress bar logic
    if income > 0:
        expenses_percentage = (expenses / income) * 100
        income_left = income - expenses
        income_left_percentage = (income_left / income) * 100
    else:
        expenses_percentage = 0
        income_left = 0
        income_left_percentage = 0

    # Budget usage calculation
    if budget:
        budget_total = budget.amount
        budget_remaining = budget.amount - expenses
        budget_remaining_percentage = (budget_remaining / budget.amount) * 100
        budget_used = (expenses / budget.amount) * 100 if budget_total else 0
    else:
        budget_total = 0
        budget_remaining = 0
        budget_remaining_percentage = 0
        budget_used = 0

    # Pass the data to the template
    context = {
        'transactions': transactions,
        'budget': budget,
        'expenses': expenses,
        'income': income,
        'income_left': income_left,
        'expenses_percentage': round(expenses_percentage, 2),
        'income_left_percentage': round(income_left_percentage, 2),
        'budget_total': budget_total,
        'budget_remaining': budget_remaining,
        'budget_remaining_percentage': round(budget_remaining_percentage, 2),
        'budget_used': round(budget_used, 2),
    }
    
    return render(request, 'tracker/dashboard.html', context)

    # Get all transactions
    transactions = Transaction.objects.all().order_by('-date')
    
    # Get the current month's budget (if exists)
    today = date.today()
    current_month = date(today.year, today.month, 1)
    budget = Budget.objects.filter(month=current_month).first()
    
    # Calculate total expenses and income
    expenses = transactions.filter(type='expense').aggregate(total=models.Sum('amount'))['total'] or 0
    income = transactions.filter(type='income').aggregate(total=models.Sum('amount'))['total'] or 0
    
    # Budget usage and progress bar logic
    if income > 0:
        expenses_percentage = (expenses / income) * 100
        income_left_percentage = 100 - expenses_percentage
    else:
        expenses_percentage = 0
        income_left_percentage = 0

    if budget:
        budget_total = budget.amount
        budget_remaining = budget.amount - expenses
        budget_remaining_percentage = (budget_remaining / budget.amount) * 100
        budget_used = (expenses / budget.amount) * 100 if budget_total else 0
    else:
        budget_total = 0
        budget_remaining = 0
        budget_remaining_percentage = 0
        budget_used = 0

    # Pass the data to the template
    context = {
        'transactions': transactions,
        'budget': budget,
        'expenses': expenses,
        'income': income,
        'expenses_percentage': round(expenses_percentage, 2),
        'income_left_percentage': round(income_left_percentage, 2),
        'budget_total': budget_total,
        'budget_remaining': budget_remaining,
        'budget_remaining_percentage': round(budget_remaining_percentage, 2),
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

    # Ensure the 'amount' column is numeric
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

    # 1. Income vs Expense Over Time
    df_expenses = df[df['type'] == 'expense'].groupby('date').agg({'amount': 'sum'})
    df_income = df[df['type'] == 'income'].groupby('date').agg({'amount': 'sum'})

    if df_expenses.empty or df_income.empty:
        return render(request, 'tracker/analytics.html', {'no_data': True})

    # Plot Income vs Expenses
    plt.figure(figsize=(10, 5))
    plt.plot(df_expenses.index, df_expenses['amount'], label='Expenses', color='red')
    plt.plot(df_income.index, df_income['amount'], label='Income', color='green')
    plt.legend()
    plt.title('Income vs Expenses Over Time')
    plt.xlabel('Date')
    plt.ylabel('Amount')
    plt.xticks(rotation=45)
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    income_expenses_graph = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    # 2. Monthly Income and Expense Breakdown (Bar Chart)
    monthly_expenses = df[df['type'] == 'expense'].groupby(df['date'].dt.to_period('M')).agg({'amount': 'sum'})
    monthly_income = df[df['type'] == 'income'].groupby(df['date'].dt.to_period('M')).agg({'amount': 'sum'})

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(monthly_expenses.index.astype(str), monthly_expenses['amount'], label='Expenses', color='red')
    ax.bar(monthly_income.index.astype(str), monthly_income['amount'], label='Income', color='green', alpha=0.5)
    ax.set_title('Monthly Income vs Expenses')
    ax.set_xlabel('Month')
    ax.set_ylabel('Amount')
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    monthly_graph = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    # 3. Category-wise Expense Breakdown (Pie Chart)
    category_expenses = df[df['type'] == 'expense'].groupby('category__name').agg({'amount': 'sum'})

    if category_expenses.empty:
        return render(request, 'tracker/analytics.html', {'no_data': True})

    plt.figure(figsize=(8, 8))
    category_expenses['amount'].plot(kind='pie', autopct='%1.1f%%', colors=['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0'])
    plt.title('Expense Breakdown by Category')
    plt.ylabel('')  # Hide the y-axis label
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    category_graph = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    # 4. Budget vs. Actual Spending (Progress Bar)
    today = date.today()
    current_month = date(today.year, today.month, 1)
    budget = Budget.objects.filter(month=current_month).first()

    if budget:
        # Convert to float to avoid Decimal vs Float error
        budget_total = float(budget.amount)
        expenses = df[df['type'] == 'expense'].agg({'amount': 'sum'})['amount']
        expenses = float(expenses)  # Ensure it's a float
        budget_used = (expenses / budget_total) * 100 if budget_total else 0
        budget_remaining = budget_total - expenses
        budget_remaining_percentage = (budget_remaining / budget_total) * 100
    else:
        budget_used = 0
        budget_remaining = 0
        budget_remaining_percentage = 0

    # Pass the data to the template
    context = {
        'income_expenses_graph': income_expenses_graph,
        'monthly_graph': monthly_graph,
        'category_graph': category_graph,
        'budget_total': budget_total if budget else 0,
        'budget_used': round(budget_used, 2),
        'budget_remaining': round(budget_remaining, 2),
        'budget_remaining_percentage': round(budget_remaining_percentage, 2),
    }

    return render(request, 'tracker/analytics.html', context)

def transaction_list(request):
    transactions = Transaction.objects.all().order_by('-date')
    return render(request, 'tracker/transaction_list.html', {'transactions': transactions})

def edit_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    categories = Category.objects.all()

    if request.method == 'POST':
        category_id = request.POST.get('category')
        category = Category.objects.get(id=category_id) if category_id else None
        transaction.category = category
        transaction.amount = request.POST['amount']
        transaction.date = request.POST['date']
        transaction.description = request.POST['description']
        transaction.type = request.POST['type']
        transaction.save()
        return redirect('transaction_list')

    return render(request, 'tracker/edit_transaction.html', {'transaction': transaction, 'categories': categories})

def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    transaction.delete()
    return redirect('transaction_list')

def export_transactions(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Category', 'Description', 'Amount', 'Type'])

    for transaction in Transaction.objects.all():
        writer.writerow([
            transaction.date,
            transaction.category.name if transaction.category else '',
            transaction.description,
            transaction.amount,
            transaction.type,
        ])

    return response

def import_transactions(request):
    if request.method == 'POST' and request.FILES.get('file'):
        csv_file = request.FILES['file']
        print("✅ CSV file received")

        try:
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)

            for raw_row in reader:
                print(f"🛠 Raw row: {raw_row}")

                # Normalize the keys
                row = {k.lower().strip(): v.strip() for k, v in raw_row.items()}
                print(f"🔍 Normalized row: {row}")

                # Skip incomplete rows
                if not all(row.get(field) for field in ['date', 'amount', 'type']):
                    print("⚠️ Incomplete row, skipping")
                    continue

                # Handle optional fields
                category = None
                if row.get('category'):
                    category, _ = Category.objects.get_or_create(name=row['category'])

                description = row.get('description', '')

                # Convert date to a proper datetime object
                from datetime import datetime
                try:
                    row['date'] = datetime.strptime(row['date'], "%Y-%m-%d").date()
                except ValueError as e:
                    print(f"⚠️ Error parsing date {row['date']}: {e}")
                    continue

                # Handle amount as a Decimal
                try:
                    amount = Decimal(row['amount'])
                except Exception as e:
                    print(f"⚠️ Invalid amount value: {row['amount']} - {e}")
                    continue

                print(f"📦 Creating transaction: {row['date']} - {amount} - {row['type']}")

                # Create the transaction
                Transaction.objects.create(
                    date=row['date'],
                    category=category,
                    description=description,
                    amount=amount,
                    type=row['type'].lower()
                )

            messages.success(request, "✅ Transactions imported successfully!")
        except Exception as e:
            print(f"❌ Error during import: {e}")
            messages.error(request, f"Error importing CSV: {e}")

    return redirect('transaction_list')

