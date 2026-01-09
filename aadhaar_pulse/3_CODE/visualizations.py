"""
AADHAAR PULSE - Visualization Module
=====================================
Beautiful, hackathon-winning visualizations for all 11 analysis modules.

Author: Aadhaar Pulse Team
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style for all plots
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Custom color palettes
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'accent': '#F18F01',
    'success': '#C73E1D',
    'warning': '#F4D35E',
    'danger': '#E63946',
    'info': '#457B9D',
    'light': '#F1FAEE',
    'dark': '#1D3557'
}

GRADIENT_COLORS = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#457B9D']


def set_plot_style():
    """Set consistent plot styling."""
    plt.rcParams['figure.figsize'] = (12, 6)
    plt.rcParams['font.size'] = 11
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.titleweight'] = 'bold'
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.facecolor'] = 'white'
    plt.rcParams['axes.edgecolor'] = '#333333'
    plt.rcParams['grid.alpha'] = 0.3


def create_title(title, subtitle=None):
    """Create a styled title with optional subtitle."""
    if subtitle:
        return f"{title}\n{subtitle}"
    return title


# =============================================================================
# UNIVARIATE VISUALIZATIONS
# =============================================================================

def plot_time_series(df, date_col, value_col, title, color=None, figsize=(14, 6)):
    """
    Plot a time series with trend line.
    """
    set_plot_style()
    fig, ax = plt.subplots(figsize=figsize)
    
    color = color or COLORS['primary']
    
    ax.plot(df[date_col], df[value_col], color=color, linewidth=2, alpha=0.8)
    ax.fill_between(df[date_col], df[value_col], alpha=0.3, color=color)
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    
    # Add trend line
    z = np.polyfit(range(len(df)), df[value_col], 1)
    p = np.poly1d(z)
    ax.plot(df[date_col], p(range(len(df))), "--", color=COLORS['danger'], 
            alpha=0.8, label=f'Trend (slope: {z[0]:.2f})')
    ax.legend()
    
    plt.tight_layout()
    return fig, ax


def plot_distribution(data, title, xlabel, color=None, figsize=(10, 6)):
    """
    Plot distribution with histogram and KDE.
    """
    set_plot_style()
    fig, ax = plt.subplots(figsize=figsize)
    
    color = color or COLORS['primary']
    
    sns.histplot(data, kde=True, color=color, ax=ax, alpha=0.7)
    
    # Add statistics
    mean_val = np.mean(data)
    median_val = np.median(data)
    ax.axvline(mean_val, color=COLORS['danger'], linestyle='--', 
               label=f'Mean: {mean_val:,.0f}')
    ax.axvline(median_val, color=COLORS['success'], linestyle=':', 
               label=f'Median: {median_val:,.0f}')
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.legend()
    
    plt.tight_layout()
    return fig, ax


def plot_top_n_bar(df, category_col, value_col, title, n=10, horizontal=True, 
                   color=None, figsize=(12, 8)):
    """
    Plot top N categories as bar chart.
    """
    set_plot_style()
    
    top_n = df.nlargest(n, value_col)
    
    fig, ax = plt.subplots(figsize=figsize)
    
    colors = plt.cm.viridis(np.linspace(0.2, 0.8, n))
    
    if horizontal:
        bars = ax.barh(range(n), top_n[value_col], color=colors)
        ax.set_yticks(range(n))
        ax.set_yticklabels(top_n[category_col])
        ax.invert_yaxis()
        ax.set_xlabel(value_col, fontsize=12)
        
        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, top_n[value_col])):
            ax.text(val + max(top_n[value_col]) * 0.01, i, f'{val:,.0f}', 
                   va='center', fontsize=10)
    else:
        bars = ax.bar(range(n), top_n[value_col], color=colors)
        ax.set_xticks(range(n))
        ax.set_xticklabels(top_n[category_col], rotation=45, ha='right')
        ax.set_ylabel(value_col, fontsize=12)
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    return fig, ax


def plot_pie_chart(df, category_col, value_col, title, top_n=8, figsize=(10, 10)):
    """
    Plot pie chart with top N categories.
    """
    set_plot_style()
    
    top_n_df = df.nlargest(top_n, value_col)
    other_sum = df[~df[category_col].isin(top_n_df[category_col])][value_col].sum()
    
    if other_sum > 0:
        other_row = pd.DataFrame({category_col: ['Others'], value_col: [other_sum]})
        plot_df = pd.concat([top_n_df[[category_col, value_col]], other_row])
    else:
        plot_df = top_n_df[[category_col, value_col]]
    
    fig, ax = plt.subplots(figsize=figsize)
    
    colors = plt.cm.Set3(np.linspace(0, 1, len(plot_df)))
    
    wedges, texts, autotexts = ax.pie(
        plot_df[value_col], 
        labels=plot_df[category_col],
        autopct='%1.1f%%',
        colors=colors,
        explode=[0.02] * len(plot_df),
        shadow=True
    )
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    return fig, ax


# =============================================================================
# BIVARIATE VISUALIZATIONS
# =============================================================================

def plot_scatter(df, x_col, y_col, title, hue_col=None, size_col=None, 
                 figsize=(12, 8)):
    """
    Plot scatter plot with optional hue and size encoding.
    """
    set_plot_style()
    fig, ax = plt.subplots(figsize=figsize)
    
    if hue_col:
        scatter = ax.scatter(df[x_col], df[y_col], c=df[hue_col], 
                            cmap='viridis', alpha=0.6, s=50 if size_col is None 
                            else df[size_col]/df[size_col].max()*200)
        plt.colorbar(scatter, ax=ax, label=hue_col)
    else:
        ax.scatter(df[x_col], df[y_col], color=COLORS['primary'], alpha=0.6, s=50)
    
    # Add trend line
    z = np.polyfit(df[x_col], df[y_col], 1)
    p = np.poly1d(z)
    x_line = np.linspace(df[x_col].min(), df[x_col].max(), 100)
    ax.plot(x_line, p(x_line), "--", color=COLORS['danger'], alpha=0.8, 
            label=f'Trend (r={np.corrcoef(df[x_col], df[y_col])[0,1]:.3f})')
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel(x_col, fontsize=12)
    ax.set_ylabel(y_col, fontsize=12)
    ax.legend()
    
    plt.tight_layout()
    return fig, ax


def plot_heatmap(df, title, figsize=(14, 10), cmap='YlOrRd', annot=True):
    """
    Plot correlation heatmap.
    """
    set_plot_style()
    fig, ax = plt.subplots(figsize=figsize)
    
    # Calculate correlation matrix
    corr = df.select_dtypes(include=[np.number]).corr()
    
    # Create mask for upper triangle
    mask = np.triu(np.ones_like(corr, dtype=bool))
    
    sns.heatmap(corr, mask=mask, annot=annot, cmap=cmap, center=0,
                square=True, linewidths=0.5, ax=ax, fmt='.2f',
                cbar_kws={"shrink": 0.8})
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    return fig, ax


def plot_grouped_bar(df, x_col, y_cols, title, figsize=(14, 8)):
    """
    Plot grouped bar chart comparing multiple metrics.
    """
    set_plot_style()
    fig, ax = plt.subplots(figsize=figsize)
    
    x = np.arange(len(df))
    width = 0.8 / len(y_cols)
    
    for i, col in enumerate(y_cols):
        offset = (i - len(y_cols)/2 + 0.5) * width
        bars = ax.bar(x + offset, df[col], width, label=col, alpha=0.8)
    
    ax.set_xticks(x)
    ax.set_xticklabels(df[x_col], rotation=45, ha='right')
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.legend()
    
    plt.tight_layout()
    return fig, ax


def plot_line_comparison(df, date_col, value_cols, title, figsize=(14, 6)):
    """
    Plot multiple lines for comparison.
    """
    set_plot_style()
    fig, ax = plt.subplots(figsize=figsize)
    
    colors = plt.cm.Set1(np.linspace(0, 1, len(value_cols)))
    
    for col, color in zip(value_cols, colors):
        ax.plot(df[date_col], df[col], label=col, linewidth=2, color=color)
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.legend()
    
    plt.tight_layout()
    return fig, ax


# =============================================================================
# TRIVARIATE & ADVANCED VISUALIZATIONS
# =============================================================================

def plot_bubble_chart(df, x_col, y_col, size_col, color_col, title, 
                      figsize=(14, 10)):
    """
    Plot bubble chart with 4 dimensions.
    """
    set_plot_style()
    fig, ax = plt.subplots(figsize=figsize)
    
    # Normalize size
    sizes = (df[size_col] / df[size_col].max()) * 1000 + 50
    
    scatter = ax.scatter(df[x_col], df[y_col], s=sizes, c=df[color_col],
                        cmap='viridis', alpha=0.6, edgecolors='white', linewidth=0.5)
    
    plt.colorbar(scatter, ax=ax, label=color_col)
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel(x_col, fontsize=12)
    ax.set_ylabel(y_col, fontsize=12)
    
    # Add size legend
    for size_val in [df[size_col].min(), df[size_col].median(), df[size_col].max()]:
        ax.scatter([], [], s=(size_val/df[size_col].max())*1000+50, c='gray', 
                  alpha=0.6, label=f'{size_col}: {size_val:,.0f}')
    ax.legend(loc='upper right', title='Size Legend')
    
    plt.tight_layout()
    return fig, ax


def plot_3d_scatter(df, x_col, y_col, z_col, color_col, title, figsize=(14, 10)):
    """
    Plot 3D scatter plot.
    """
    from mpl_toolkits.mplot3d import Axes3D
    
    set_plot_style()
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection='3d')
    
    scatter = ax.scatter(df[x_col], df[y_col], df[z_col], c=df[color_col],
                        cmap='viridis', s=50, alpha=0.6)
    
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    ax.set_zlabel(z_col)
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    
    plt.colorbar(scatter, ax=ax, label=color_col, shrink=0.5)
    
    plt.tight_layout()
    return fig, ax


# =============================================================================
# SPECIAL VISUALIZATIONS FOR AADHAAR PULSE
# =============================================================================

def plot_migration_flow(source_data, title="Migration Flow Between States", 
                        figsize=(16, 12)):
    """
    Plot Sankey-style migration flow diagram.
    Uses a simplified chord-like visualization.
    """
    set_plot_style()
    fig, ax = plt.subplots(figsize=figsize)
    
    # This is a placeholder - in real implementation, use plotly for Sankey
    ax.text(0.5, 0.5, "Use Plotly for interactive Sankey diagram\n(See Streamlit dashboard)", 
           ha='center', va='center', fontsize=14, transform=ax.transAxes)
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.axis('off')
    
    return fig, ax


def plot_anomaly_heatmap(df, district_col, metric_col, title, figsize=(16, 10)):
    """
    Plot anomaly heatmap by district.
    """
    set_plot_style()
    
    # Pivot for heatmap
    pivot_df = df.pivot_table(values=metric_col, index='state', 
                               columns='month' if 'month' in df.columns else district_col,
                               aggfunc='sum')
    
    fig, ax = plt.subplots(figsize=figsize)
    
    sns.heatmap(pivot_df, cmap='RdYlGn_r', ax=ax, linewidths=0.5,
                cbar_kws={'label': metric_col})
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    return fig, ax


def plot_crisis_timeline(df, date_col, value_col, anomaly_col, title, 
                         figsize=(16, 6)):
    """
    Plot crisis timeline with highlighted anomaly periods.
    """
    set_plot_style()
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot main line
    ax.plot(df[date_col], df[value_col], color=COLORS['primary'], linewidth=2)
    ax.fill_between(df[date_col], df[value_col], alpha=0.2, color=COLORS['primary'])
    
    # Highlight anomalies
    anomaly_mask = df[anomaly_col] == 1
    ax.scatter(df.loc[anomaly_mask, date_col], df.loc[anomaly_mask, value_col],
              color=COLORS['danger'], s=100, zorder=5, label='Anomaly Detected')
    
    # Add alert bands
    mean_val = df[value_col].mean()
    std_val = df[value_col].std()
    ax.axhline(mean_val + 2*std_val, color=COLORS['warning'], linestyle='--', 
               alpha=0.7, label='Warning Threshold')
    ax.axhline(mean_val + 3*std_val, color=COLORS['danger'], linestyle='--',
               alpha=0.7, label='Critical Threshold')
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel(value_col, fontsize=12)
    ax.legend()
    
    plt.tight_layout()
    return fig, ax


def plot_cohort_funnel(cohort_data, title="Cohort Progression Funnel", 
                       figsize=(12, 8)):
    """
    Plot cohort progression funnel.
    """
    set_plot_style()
    fig, ax = plt.subplots(figsize=figsize)
    
    stages = list(cohort_data.keys())
    values = list(cohort_data.values())
    
    colors = plt.cm.Blues(np.linspace(0.3, 0.9, len(stages)))
    
    for i, (stage, value, color) in enumerate(zip(stages, values, colors)):
        width = value / max(values)
        left = (1 - width) / 2
        ax.barh(i, width, left=left, height=0.6, color=color, 
               edgecolor='white', linewidth=2)
        ax.text(0.5, i, f'{stage}\n{value:,} ({value/values[0]*100:.1f}%)', 
               ha='center', va='center', fontsize=11, fontweight='bold')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.5, len(stages) - 0.5)
    ax.invert_yaxis()
    ax.axis('off')
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    return fig, ax


def plot_sentiment_gauge(score, title="Aadhaar Sentiment Index", figsize=(8, 6)):
    """
    Plot gauge chart for sentiment index.
    """
    set_plot_style()
    fig, ax = plt.subplots(figsize=figsize, subplot_kw={'projection': 'polar'})
    
    # Gauge settings
    theta = np.linspace(0, np.pi, 100)
    
    # Background gradient
    for i, color in enumerate(['#E63946', '#F4D35E', '#2A9D8F']):
        start = i * np.pi / 3
        end = (i + 1) * np.pi / 3
        ax.fill_between(np.linspace(start, end, 30), 0.6, 1, 
                       color=color, alpha=0.3)
    
    # Needle
    needle_angle = score * np.pi  # score is 0-1
    ax.plot([needle_angle, needle_angle], [0, 0.9], color=COLORS['dark'], 
           linewidth=3)
    ax.scatter([needle_angle], [0.9], color=COLORS['dark'], s=100, zorder=5)
    
    # Score text
    ax.text(np.pi/2, 0.3, f'{score*100:.1f}', ha='center', va='center',
           fontsize=24, fontweight='bold')
    ax.text(np.pi/2, 0.1, 'Score', ha='center', va='center', fontsize=12)
    
    ax.set_ylim(0, 1)
    ax.set_theta_zero_location('W')
    ax.set_theta_direction(-1)
    ax.set_thetamin(0)
    ax.set_thetamax(180)
    ax.axis('off')
    ax.set_title(title, fontsize=16, fontweight='bold', y=1.1)
    
    plt.tight_layout()
    return fig, ax


def plot_radar_chart(categories, values, title, figsize=(10, 10)):
    """
    Plot radar/spider chart.
    """
    set_plot_style()
    
    # Number of variables
    N = len(categories)
    
    # Compute angle for each category
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Complete the loop
    
    values = list(values) + [values[0]]  # Complete the loop
    
    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))
    
    # Plot
    ax.plot(angles, values, 'o-', linewidth=2, color=COLORS['primary'])
    ax.fill(angles, values, alpha=0.25, color=COLORS['primary'])
    
    # Set category labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=11)
    
    ax.set_title(title, fontsize=16, fontweight='bold', y=1.1)
    
    plt.tight_layout()
    return fig, ax


def plot_calendar_heatmap(df, date_col, value_col, title, figsize=(16, 4)):
    """
    Plot calendar heatmap showing activity by day.
    """
    set_plot_style()
    
    # Prepare data
    df = df.copy()
    df['weekday'] = df[date_col].dt.dayofweek
    df['week'] = df[date_col].dt.isocalendar().week
    
    pivot = df.pivot_table(values=value_col, index='weekday', columns='week', 
                           aggfunc='sum')
    
    fig, ax = plt.subplots(figsize=figsize)
    
    sns.heatmap(pivot, cmap='YlGn', ax=ax, cbar_kws={'label': value_col})
    
    ax.set_yticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Week of Year')
    ax.set_ylabel('Day of Week')
    
    plt.tight_layout()
    return fig, ax


def save_figure(fig, filename, dpi=150, format='png'):
    """
    Save figure to file.
    """
    fig.savefig(filename, dpi=dpi, format=format, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    print(f"✓ Saved: {filename}")


# =============================================================================
# DASHBOARD HELPER FUNCTIONS
# =============================================================================

def create_summary_card(title, value, subtitle=None, delta=None):
    """
    Create data for summary card (for Streamlit).
    """
    return {
        'title': title,
        'value': value,
        'subtitle': subtitle,
        'delta': delta
    }


def format_large_number(num):
    """
    Format large numbers for display (e.g., 1.2M, 3.4K).
    """
    if num >= 1e9:
        return f'{num/1e9:.2f}B'
    elif num >= 1e6:
        return f'{num/1e6:.2f}M'
    elif num >= 1e3:
        return f'{num/1e3:.2f}K'
    else:
        return f'{num:.0f}'
