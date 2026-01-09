"""
AADHAAR PULSE - Interactive Streamlit Dashboard
================================================
India's Societal Seismograph - Real-time insights from Aadhaar data.

Run with: streamlit run app.py

Author: Aadhaar Pulse Team
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
sys.path.append('../3_CODE')

from data_loader import load_all_datasets
from preprocessing import clean_all_datasets
from module_01_migration import calculate_migration_indicators, generate_migration_summary
from module_02_anomaly import calculate_anomaly_scores, detect_ghost_districts
from module_03_service_demand import forecast_school_demand, forecast_healthcare_demand
from module_04_inequality import calculate_digital_inclusion_index
from module_05_to_11 import (detect_crisis_signals, calculate_sentiment_index, 
                              track_cohort_progression, calculate_future_demand)

# Page config
st.set_page_config(
    page_title="AADHAAR PULSE",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #2E86AB, #A23B72);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🚀 AADHAAR PULSE</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem;">India\'s Societal Seismograph - Transform passive identity records into real-time societal insights</p>', unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🎛️ Control Panel")

# Data loading
@st.cache_data
def load_data():
    """Load and cache data."""
    try:
        enrol_path = '../../api_data_aadhar_enrolment'
        demo_path = '../../api_data_aadhar_demographic'
        bio_path = '../../api_data_aadhar_biometric'
        
        enrol_raw, demo_raw, bio_raw = load_all_datasets(enrol_path, demo_path, bio_path)
        enrol_df, demo_df, bio_df = clean_all_datasets(enrol_raw, demo_raw, bio_raw)
        return enrol_df, demo_df, bio_df, True
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, False

# Load data
with st.spinner("📂 Loading Aadhaar datasets..."):
    enrol_df, demo_df, bio_df, data_loaded = load_data()

if not data_loaded:
    st.error("⚠️ Could not load data. Please ensure CSV files are in the correct location.")
    st.stop()

# Data summary
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Data Summary")
st.sidebar.metric("Total Records", f"{len(enrol_df) + len(demo_df) + len(bio_df):,}")
st.sidebar.metric("States", f"{enrol_df['state'].nunique()}")
st.sidebar.metric("Districts", f"{enrol_df['district'].nunique()}")

# Module selection
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔬 Select Analysis Module")
module = st.sidebar.selectbox(
    "Choose Module",
    [
        "📊 Overview Dashboard",
        "🚶 Migration Corridors",
        "👻 Ghost Districts (Anomalies)",
        "📈 Service Demand Forecast",
        "⚖️ Digital Inequality Index",
        "🚨 Crisis Early Warning",
        "📈 Sentiment Index",
        "👶 Cohort Tracking",
        "🔮 Future Demand (10-Year)"
    ]
)

# Main content based on module
if module == "📊 Overview Dashboard":
    st.header("📊 Overview Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Enrolments", f"{enrol_df['total_enrolments'].sum():,.0f}")
    with col2:
        st.metric("Demographic Updates", f"{demo_df['total_demo_updates'].sum():,.0f}")
    with col3:
        st.metric("Biometric Updates", f"{bio_df['total_bio_updates'].sum():,.0f}")
    with col4:
        total = enrol_df['total_enrolments'].sum() + demo_df['total_demo_updates'].sum() + bio_df['total_bio_updates'].sum()
        st.metric("Total Activity", f"{total:,.0f}")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Enrolments by State")
        state_enrol = enrol_df.groupby('state')['total_enrolments'].sum().nlargest(15).reset_index()
        fig = px.bar(state_enrol, x='total_enrolments', y='state', orientation='h',
                     color='total_enrolments', color_continuous_scale='Blues')
        fig.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Activity Over Time")
        daily = enrol_df.groupby('date')['total_enrolments'].sum().reset_index()
        fig = px.line(daily, x='date', y='total_enrolments', 
                      title="Daily Enrolment Trend")
        fig.update_traces(fill='tozeroy')
        st.plotly_chart(fig, use_container_width=True)
    
    # Age distribution
    st.subheader("Age Distribution of Enrolments")
    age_data = pd.DataFrame({
        'Age Group': ['0-5 Years', '5-17 Years', '18+ Years'],
        'Count': [enrol_df['age_0_5'].sum(), enrol_df['age_5_17'].sum(), enrol_df['age_18_greater'].sum()]
    })
    fig = px.pie(age_data, values='Count', names='Age Group', 
                 color_discrete_sequence=['#2E86AB', '#A23B72', '#F18F01'])
    st.plotly_chart(fig, use_container_width=True)

elif module == "🚶 Migration Corridors":
    st.header("🚶 Migration Corridor Detection")
    st.markdown("**Insight**: High demographic updates + Low enrolments = People MOVING IN")
    
    migration_df = calculate_migration_indicators(enrol_df, demo_df, level='state')
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Migration Score by State")
        fig = px.bar(migration_df.nlargest(15, 'migration_score'), 
                     x='migration_score', y='state', orientation='h',
                     color='migration_type', 
                     color_discrete_map={'INFLOW': '#2E86AB', 'OUTFLOW': '#E63946', 
                                        'HIGH_CHURN': '#F18F01', 'NEW_SETTLEMENT': '#2A9D8F',
                                        'STABLE': '#457B9D'})
        fig.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Migration Type Distribution")
        type_counts = migration_df['migration_type'].value_counts().reset_index()
        type_counts.columns = ['Migration Type', 'Count']
        fig = px.pie(type_counts, values='Count', names='Migration Type')
        st.plotly_chart(fig, use_container_width=True)
    
    # Summary
    summary = generate_migration_summary(enrol_df, demo_df)
    st.markdown("### Key Findings")
    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Update-Enrol Ratio", f"{summary['avg_update_enrol_ratio']:.2f}")
    col2.metric("Total States", f"{summary['total_states']}")
    col3.metric("Total Districts", f"{summary['total_districts']}")

elif module == "👻 Ghost Districts (Anomalies)":
    st.header("👻 Ghost Districts - Anomaly Detection")
    st.markdown("**Insight**: Districts with high enrolments but zero updates = potential fraud")
    
    anomaly_df = calculate_anomaly_scores(enrol_df, demo_df, bio_df, level='district')
    ghost = detect_ghost_districts(enrol_df, demo_df, bio_df, top_n=20)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ghost Districts", f"{anomaly_df['ghost_district'].sum()}")
    col2.metric("Critical Anomalies", f"{len(anomaly_df[anomaly_df['anomaly_level']=='CRITICAL'])}")
    col3.metric("High Anomalies", f"{len(anomaly_df[anomaly_df['anomaly_level']=='HIGH'])}")
    col4.metric("Avg Anomaly Score", f"{anomaly_df['anomaly_score'].mean():.1f}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Anomaly Score Distribution")
        fig = px.histogram(anomaly_df, x='anomaly_score', nbins=50,
                          color_discrete_sequence=['#E63946'])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Anomaly Level Breakdown")
        level_counts = anomaly_df['anomaly_level'].value_counts().reset_index()
        level_counts.columns = ['Level', 'Count']
        fig = px.bar(level_counts, x='Level', y='Count',
                     color='Level',
                     color_discrete_map={'CRITICAL': '#E63946', 'HIGH': '#F18F01',
                                        'MEDIUM': '#F4D35E', 'LOW': '#2A9D8F', 'NORMAL': '#457B9D'})
        st.plotly_chart(fig, use_container_width=True)
    
    if len(ghost) > 0:
        st.subheader("🚨 Top Ghost Districts")
        st.dataframe(ghost[['state', 'district', 'risk_score', 'total_enrolments', 
                           'update_enrol_ratio']].head(10))

elif module == "📈 Service Demand Forecast":
    st.header("📈 Predictive Service Demand Forecaster")
    st.markdown("**Insight**: 0-5 enrolments today = School seats needed in 5-13 years")
    
    years = st.slider("Forecast Years Ahead", 1, 10, 5)
    
    school = forecast_school_demand(enrol_df, years_ahead=years)
    healthcare = forecast_healthcare_demand(enrol_df, bio_df)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📚 School Seat Demand Forecast")
        school_yearly = school.groupby('forecast_year')['primary_school_seats_needed'].sum().reset_index()
        fig = px.bar(school_yearly, x='forecast_year', y='primary_school_seats_needed',
                     color='primary_school_seats_needed', color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏥 Healthcare Demand by State")
        fig = px.bar(healthcare.nlargest(15, 'total_healthcare_demand'),
                     x='total_healthcare_demand', y='state', orientation='h',
                     color='total_healthcare_demand', color_continuous_scale='Reds')
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

elif module == "⚖️ Digital Inequality Index":
    st.header("⚖️ Digital Inclusion Inequality Index")
    st.markdown("**Insight**: Low activity across ALL datasets = systematically underserved")
    
    inclusion = calculate_digital_inclusion_index(enrol_df, demo_df, bio_df, level='state')
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Digital Divide Score by State")
        fig = px.bar(inclusion.nlargest(15, 'digital_divide_score'),
                     x='digital_divide_score', y='state', orientation='h',
                     color='digital_divide_score', color_continuous_scale='Reds')
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Inclusion Category Distribution")
        cat_counts = inclusion['inclusion_category'].value_counts().reset_index()
        cat_counts.columns = ['Category', 'Count']
        fig = px.pie(cat_counts, values='Count', names='Category',
                     color='Category',
                     color_discrete_map={'WELL_CONNECTED': '#2A9D8F', 'MODERATE': '#F4D35E',
                                        'UNDERSERVED': '#F18F01', 'SEVERELY_EXCLUDED': '#E63946'})
        st.plotly_chart(fig, use_container_width=True)

elif module == "🚨 Crisis Early Warning":
    st.header("🚨 Crisis Early Warning System")
    st.markdown("**Insight**: Detect disasters 24-48 hours before official reports")
    
    crisis = detect_crisis_signals(enrol_df, demo_df, bio_df)
    
    # Alert counts
    alert_counts = crisis['alert_level'].value_counts()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🔴 RED Alerts", alert_counts.get('RED', 0))
    col2.metric("🟠 ORANGE Alerts", alert_counts.get('ORANGE', 0))
    col3.metric("🟡 YELLOW Alerts", alert_counts.get('YELLOW', 0))
    col4.metric("⚫ Dead Zones", alert_counts.get('DEAD_ZONE', 0))
    
    st.subheader("Crisis Timeline")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=crisis['date'], y=crisis['total_activity'],
                             mode='lines', name='Activity', fill='tozeroy'))
    
    # Highlight crisis days
    crisis_days = crisis[crisis['is_crisis'] == 1]
    fig.add_trace(go.Scatter(x=crisis_days['date'], y=crisis_days['total_activity'],
                             mode='markers', name='Crisis Alert', 
                             marker=dict(color='red', size=10)))
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

elif module == "📈 Sentiment Index":
    st.header("📈 Aadhaar Sentiment Index")
    st.markdown("**Insight**: Measure national well-being without costly surveys")
    
    sentiment = calculate_sentiment_index(enrol_df, demo_df, bio_df, level='state')
    national_avg = sentiment['sentiment_index'].mean()
    
    # Gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=national_avg,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "National Sentiment Index"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#2E86AB"},
            'steps': [
                {'range': [0, 30], 'color': "#E63946"},
                {'range': [30, 50], 'color': "#F18F01"},
                {'range': [50, 70], 'color': "#F4D35E"},
                {'range': [70, 100], 'color': "#2A9D8F"}
            ]
        }
    ))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    # State breakdown
    st.subheader("Sentiment by State")
    fig = px.bar(sentiment.nlargest(15, 'sentiment_index'),
                 x='sentiment_index', y='state', orientation='h',
                 color='sentiment_category',
                 color_discrete_map={'THRIVING': '#2A9D8F', 'STABLE': '#F4D35E',
                                    'STRUGGLING': '#F18F01', 'AT_RISK': '#E63946'})
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

elif module == "👶 Cohort Tracking":
    st.header("👶 Cohort Tracking Analysis")
    st.markdown("**Insight**: Track children enrolled at 0-5 who never appear in subsequent updates")
    
    cohort = track_cohort_progression(enrol_df, demo_df, bio_df)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("0-5 → 5-17 Survival", f"{cohort['survival_rate_0_5_to_5_17']*100:.1f}%")
    col2.metric("5-17 → Adult Survival", f"{cohort['survival_rate_5_17_to_adult']*100:.1f}%")
    col3.metric("⚠️ At-Risk Children", f"{cohort['at_risk_children']:,.0f}")
    
    # Funnel chart
    fig = go.Figure(go.Funnel(
        y=['Enrolled (0-5)', 'Demo Updated (5-17)', 'Bio Updated (5-17)'],
        x=[cohort['enrolled']['age_0_5_enrolled'],
           cohort['demo_updated']['age_5_17_demo_updated'],
           cohort['bio_updated']['age_5_17_bio_updated']],
        textinfo="value+percent initial"
    ))
    fig.update_layout(title="Cohort Progression Funnel", height=400)
    st.plotly_chart(fig, use_container_width=True)

elif module == "🔮 Future Demand (10-Year)":
    st.header("🔮 Future Demand Equation - 10-Year Forecast")
    st.markdown("**Insight**: Predict schools, hospitals, pensions 10 years ahead")
    
    future = calculate_future_demand(enrol_df, demo_df, bio_df, years_ahead=10)
    
    # Multi-line forecast
    fig = make_subplots(rows=1, cols=3, subplot_titles=['📚 School Seats', '🏥 Healthcare Visits', '👴 Pension Beneficiaries'])
    
    fig.add_trace(go.Bar(x=future['year_ahead'], y=future['school_seats_needed']/1e6, 
                         marker_color='#2E86AB'), row=1, col=1)
    fig.add_trace(go.Bar(x=future['year_ahead'], y=future['healthcare_visits_needed']/1e6,
                         marker_color='#A23B72'), row=1, col=2)
    fig.add_trace(go.Bar(x=future['year_ahead'], y=future['pension_beneficiaries']/1e6,
                         marker_color='#F18F01'), row=1, col=3)
    
    fig.update_layout(height=400, showlegend=False)
    fig.update_yaxes(title_text="Millions", row=1, col=1)
    fig.update_xaxes(title_text="Years Ahead")
    st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(future)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🚀 <strong>AADHAAR PULSE</strong> - India's Societal Seismograph</p>
    <p>Built for Aadhaar Hackathon | Transform passive identity records into real-time societal insights</p>
</div>
""", unsafe_allow_html=True)
