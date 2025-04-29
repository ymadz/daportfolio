from django.shortcuts import render

def portfolio_home(request):
    mini_projects = [
        {"name": "Mean-Variance-Standard Deviation Calculator", "description": "Performs statistical analysis on datasets.", "url": "/mean-variance-calculator/"},
        {"name": "Demographic Data Analyzer", "description": "Analyzes and visualizes demographic data.", "url": "/demographic-analyzer/"},
        {"name": "Medical Data Visualizer", "description": "Creates insightful charts from patient medical data.", "url": "/medical-visualizer/"},
        {"name": "Page View Time Series Visualizer", "description": "Visualizes website traffic over time.", "url": "/pageview-visualizer/"},
        {"name": "Sea Level Predictor", "description": "Predicts future sea levels using historical data.", "url": "/sea-level-predictor/"},
    ]
    return render(request, 'portfolio.html', {"mini_projects": mini_projects})
