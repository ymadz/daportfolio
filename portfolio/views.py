from django.shortcuts import render
import numpy as np
import pandas as pd
import os
from django.conf import settings

def portfolio_home(request):
    mini_projects = [
        {"name": "Mean-Variance-Standard Deviation Calculator", "description": "Performs statistical analysis on datasets.", "url": "/mean_variance_calculator/"},
        {"name": "Demographic Data Analyzer", "description": "Analyzes and visualizes demographic data.", "url": "/demographic-analyzer/"},
        {"name": "Medical Data Visualizer", "description": "Creates insightful charts from patient medical data.", "url": "/medical-visualizer/"},
        {"name": "Page View Time Series Visualizer", "description": "Visualizes website traffic over time.", "url": "/pageview-visualizer/"},
        {"name": "Sea Level Predictor", "description": "Predicts future sea levels using historical data.", "url": "/sea-level-predictor/"},
    ]
    return render(request, 'portfolio.html', {"mini_projects": mini_projects})


def mean_variance_calculator(request):
    result = None
    error = None

    if request.method == "POST":
        input_data = request.POST.get("numbers")
        try:
            numbers = [int(num) for num in input_data.split(",") if num.strip()]
            if len(numbers) != 9:
                raise ValueError("Exactly 9 numbers are required.")
            
            matrix = np.array(numbers).reshape(3, 3)

            result = {
                'mean': [matrix.mean(axis=0).tolist(), matrix.mean(axis=1).tolist(), matrix.mean().item()],
                'variance': [matrix.var(axis=0).tolist(), matrix.var(axis=1).tolist(), matrix.var().item()],
                'standard deviation': [matrix.std(axis=0).tolist(), matrix.std(axis=1).tolist(), matrix.std().item()],
                'max': [matrix.max(axis=0).tolist(), matrix.max(axis=1).tolist(), matrix.max().item()],
                'min': [matrix.min(axis=0).tolist(), matrix.min(axis=1).tolist(), matrix.min().item()],
                'sum': [matrix.sum(axis=0).tolist(), matrix.sum(axis=1).tolist(), matrix.sum().item()],
            }

        except Exception as e:
            error = str(e)

    return render(request, 'mini_projects/mean_variance_calculator.html', {
        'result': result,
        'error': error
    })

def demographic_analyzer(request):
    preview = None
    result = None
    error = None

    try:
        file_path = os.path.join(settings.STATICFILES_DIRS[0], 'data', 'adult.data.csv')
        df = pd.read_csv(file_path)
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        preview = df.head(5).to_html(classes="table table-striped table-bordered", index=False)
        
        # Only run analysis on button click
        if request.method == "POST":
            # [Insert your existing calculate_demographic_data logic here]
            result = {
                'race_count': df["race"].value_counts().to_dict(),
                'average_age_men': round(df[df["sex"] == "Male"]["age"].mean(), 1),
                'percentage_bachelors': round((df["education"] == "Bachelors").sum() / len(df) * 100, 1),
                'higher_education_rich': round((df[df["education"].isin(["Bachelors", "Masters", "Doctorate"])]["salary"] == ">50K").sum() /
                                               len(df[df["education"].isin(["Bachelors", "Masters", "Doctorate"])] ) * 100, 1),
                'lower_education_rich': round((df[~df["education"].isin(["Bachelors", "Masters", "Doctorate"])]["salary"] == ">50K").sum() /
                                               len(df[~df["education"].isin(["Bachelors", "Masters", "Doctorate"])]) * 100, 1),
                'min_work_hours': df["hours-per-week"].min(),
                'rich_percentage': round((df[df["hours-per-week"] == df["hours-per-week"].min()]["salary"] == ">50K").sum() /
                                         len(df[df["hours-per-week"] == df["hours-per-week"].min()]) * 100, 1),
                'highest_earning_country': (df[df["salary"] == ">50K"]["native-country"].value_counts() /
                                            df["native-country"].value_counts()).idxmax(),
                'highest_earning_country_percentage': round(
                    (df[df["salary"] == ">50K"]["native-country"].value_counts() /
                     df["native-country"].value_counts()).max() * 100, 1),
                'top_IN_occupation': df[(df["native-country"] == "India") & (df["salary"] == ">50K")]["occupation"].mode()[0]
            }

    except Exception as e:
        error = str(e)

    return render(request, 'mini_projects/demographic_analyzer.html', {
        'preview': preview,
        'result': result,
        'error': error
    })
