from django.shortcuts import render
import numpy as np
import pandas as pd
import os
from django.conf import settings
import seaborn as sns
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import linregress




def portfolio_home(request):
    mini_projects = [
        {"name": "Mean-Variance-Standard Deviation Calculator", "description": "Performs statistical analysis on datasets.", "url": "/mean_variance_calculator/"},
        {"name": "Demographic Data Analyzer", "description": "Analyzes and visualizes demographic data.", "url": "/demographic-analyzer/"},
        {"name": "Medical Data Visualizer", "description": "Creates insightful charts from patient medical data.", "url": "/medical-visualizer/"},
        {"name": "Page View Time Series Visualizer", "description": "Visualizes website traffic over time.", "url": "/time-series-visualizer/"},
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


def medical_visualizer(request):
    # Load data
    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'data', 'medical_examination.csv')
    df = pd.read_csv(file_path)

    # Create HTML table of first 10 rows
    csv_preview = df.head(10).to_html(classes="table table-striped", index=False)

    if request.method == 'POST':
        # Add overweight column
        df['overweight'] = (df['weight'] / ((df['height'] / 100) ** 2) > 25).astype(int)

        # Normalize cholesterol and gluc
        df['cholesterol'] = (df['cholesterol'] > 1).astype(int)
        df['gluc'] = (df['gluc'] > 1).astype(int)

        # Draw categorical plot
        df_cat = pd.melt(df,
                         id_vars=['cardio'],
                         value_vars=['cholesterol', 'gluc', 'smoke', 'alco', 'active', 'overweight'])
        df_cat = df_cat.groupby(['cardio', 'variable', 'value']).size().reset_index(name='total')

        cat_plot = sns.catplot(x='variable', y='total', hue='value',
                               col='cardio', data=df_cat, kind='bar')
        catplot_path = os.path.join(settings.STATICFILES_DIRS[0], 'data', 'catplot.png')
        cat_plot.savefig(catplot_path)

        # Draw heatmap
        df_heat = df[
            (df['ap_lo'] <= df['ap_hi']) &
            (df['height'] >= df['height'].quantile(0.025)) &
            (df['height'] <= df['height'].quantile(0.975)) &
            (df['weight'] >= df['weight'].quantile(0.025)) &
            (df['weight'] <= df['weight'].quantile(0.975))
        ]

        corr = df_heat.corr()
        mask = np.triu(np.ones_like(corr, dtype=bool))
        fig, ax = plt.subplots(figsize=(12, 10))
        sns.heatmap(corr, mask=mask, annot=True, fmt=".1f", center=0, square=True,
                    linewidths=.5, cbar_kws={"shrink": .45}, ax=ax)
        heatmap_path = os.path.join(settings.STATICFILES_DIRS[0], 'data', 'heatmap.png')
        fig.savefig(heatmap_path)
        return render(request, 'mini_projects/medical_visualizer.html', {
            'csv_data': csv_preview,
            'analyzed': True
        })

    return render(request, 'mini_projects/medical_visualizer.html', {
        'csv_data': csv_preview,
        'analyzed': False
    })
    

def time_series_visualizer(request):
    # Load and clean data
    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'data', 'fcc-forum-pageviews.csv')
    df = pd.read_csv(file_path, parse_dates=['date'], index_col='date')

    low = df['value'].quantile(0.025)
    high = df['value'].quantile(0.975)
    df = df[(df['value'] >= low) & (df['value'] <= high)]

    # Show preview
    csv_preview = df.head(10).to_html(classes='table table-striped', index=True)


    if request.method == 'POST':
        # Line Plot
        fig, ax = plt.subplots(figsize=(15, 5))
        ax.plot(df.index, df['value'], color='red', linewidth=1)
        ax.set_title('Daily freeCodeCamp Forum Page Views from: 5/2016-12/2019')
        ax.set_xlabel('Date')
        ax.set_ylabel('Page Views')
        fig.savefig(os.path.join(settings.STATICFILES_DIRS[0], 'data', 'line_plot.png'))
        plt.close(fig)

        # Bar Plot
        df_bar = df.copy()
        df_bar['year'] = df_bar.index.year
        df_bar['month'] = df_bar.index.month_name()
        df_grouped = df_bar.groupby(['year', 'month'])['value'].mean().unstack()
        month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
        df_grouped = df_grouped[month_order]
        fig = df_grouped.plot(kind='bar', figsize=(12, 8)).figure
        plt.xlabel('Years')
        plt.ylabel('Average Page Views')
        plt.legend(title='Months')
        fig.savefig(os.path.join(settings.STATICFILES_DIRS[0], 'data', 'bar_plot.png'))
        plt.close(fig)

        # Box Plot
        df_box = df.copy()
        df_box.reset_index(inplace=True)
        df_box['year'] = df_box['date'].dt.year
        df_box['month'] = df_box['date'].dt.strftime('%b')
        df_box['month_num'] = df_box['date'].dt.month
        df_box = df_box.sort_values('month_num')
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        sns.boxplot(x='year', y='value', data=df_box, ax=axes[0])
        axes[0].set_title('Year-wise Box Plot (Trend)')
        axes[0].set_xlabel('Year')
        axes[0].set_ylabel('Page Views')
        sns.boxplot(x='month', y='value', data=df_box, ax=axes[1])
        axes[1].set_title('Month-wise Box Plot (Seasonality)')
        axes[1].set_xlabel('Month')
        axes[1].set_ylabel('Page Views')
        fig.savefig(os.path.join(settings.STATICFILES_DIRS[0], 'data', 'box_plot.png'))
        plt.close(fig)

        return render(request, 'mini_projects/time_series_visualizer.html', {
            'csv_data': csv_preview,
            'analyzed': True
        })

    return render(request, 'mini_projects/time_series_visualizer.html', {
        'csv_data': csv_preview,
        'analyzed': False
    })

def sea_level_predictor(request):
    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'data', 'epa-sea-level.csv')
    df = pd.read_csv(file_path)

    # Preview table
    csv_preview = df.head(10).to_html(classes='table table-striped', index=False)

    if request.method == 'POST':
        # Plot setup
        plt.figure(figsize=(12, 6))
        plt.scatter(df['Year'], df['CSIRO Adjusted Sea Level'], label='Original Data', alpha=0.7)

        # Full data regression (1880–2050)
        res1 = linregress(df['Year'], df['CSIRO Adjusted Sea Level'])
        x_pred1 = pd.Series(range(1880, 2051))
        y_pred1 = res1.slope * x_pred1 + res1.intercept
        plt.plot(x_pred1, y_pred1, 'r', label='Best Fit Line (1880–2050)')

        # Recent data regression (2000–2050)
        df_recent = df[df['Year'] >= 2000]
        res2 = linregress(df_recent['Year'], df_recent['CSIRO Adjusted Sea Level'])
        x_pred2 = pd.Series(range(2000, 2051))
        y_pred2 = res2.slope * x_pred2 + res2.intercept
        plt.plot(x_pred2, y_pred2, 'g', label='Best Fit Line (2000–2050)')

        plt.xlabel('Year')
        plt.ylabel('Sea Level (inches)')
        plt.title('Rise in Sea Level')
        plt.legend()

        save_path = os.path.join(settings.STATICFILES_DIRS[0], 'data', 'sea_level_plot.png')
        plt.savefig(save_path)
        plt.close()

        return render(request, 'mini_projects/sea_level_predictor.html', {
            'csv_data': csv_preview,
            'analyzed': True
        })

    return render(request, 'mini_projects/sea_level_predictor.html', {
        'csv_data': csv_preview,
        'analyzed': False
    })