from django.shortcuts import render
import numpy as np

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
