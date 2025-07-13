import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
from scipy import stats
import warnings
import io
import base64
from pathlib import Path
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Banking Data EDA Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
        margin: 1rem 0;
    }
    .insight-box {
        background: #f8f9fa;
        border-left: 4px solid #17a2b8;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(file_path=None):
    """Load and preprocess data with enhanced error handling"""
    try:
        if file_path:
            df = pd.read_csv(file_path, delimiter=";")
        else:
            # Placeholder for alternative data loading
            st.warning("No file path provided. Using sample data.")
            # Create sample data if none provided
            data = {
                'age': np.random.randint(18, 70, 100),
                'job': np.random.choice(['admin.', 'technician', 'services', 'management'], 100),
                'marital': np.random.choice(['married', 'single', 'divorced'], 100),
                'education': np.random.choice(['secondary', 'tertiary', 'primary'], 100),
                'balance': np.random.randint(-1000, 5000, 100),
                'housing': np.random.choice(['yes', 'no'], 100),
                'contact': np.random.choice(['cellular', 'telephone'], 100),
                'duration': np.random.randint(0, 1000, 100),
                'campaign': np.random.randint(1, 10, 100),
                'previous': np.random.randint(0, 5, 100),
                'month': np.random.choice(['jan', 'feb', 'mar', 'apr'], 100),
                'y': np.random.choice(['yes', 'no'], 100)
            }
            df = pd.DataFrame(data)
            
        # Data preprocessing
        if 'y' in df.columns:
            df['y'] = df['y'].map({'yes': 1, 'no': 0}).astype('int8')
        else:
            df['y'] = np.random.randint(0, 2, len(df))
            
        # Optimize data types
        for col in df.select_dtypes(include=['int64']).columns:
            df[col] = df[col].astype('int32')
        for col in df.select_dtypes(include=['float64']).columns:
            df[col] = df[col].astype('float32')
            
        return df
    except Exception as e:
        st.error(f"⚠️ Error loading data: {str(e)}")
        return None

def apply_filters(df, filters):
    """Apply filters to the dataframe with optimized performance"""
    filtered_df = df.copy()
    
    # Apply range filters
    filtered_df = filtered_df[
        (filtered_df['age'].between(filters['age_range'][0], filters['age_range'][1])) &
        (filtered_df['balance'].between(filters['balance_range'][0], filters['balance_range'][1])) &
        (filtered_df['duration'].between(filters['duration_range'][0], filters['duration_range'][1]))
    ]
    
    # Apply categorical filters
    if filters['selected_job'] != 'All':
        filtered_df = filtered_df[filtered_df['job'] == filters['selected_job']]
    if filters['selected_education'] != 'All':
        filtered_df = filtered_df[filtered_df['education'] == filters['selected_education']]
    if filters['selected_marital'] != 'All':
        filtered_df = filtered_df[filtered_df['marital'] == filters['selected_marital']]
    
    return filtered_df

def get_download_link(df, filename, text):
    """Generate download link for DataFrame"""
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    b64 = base64.b64encode(buffer.getvalue().encode()).decode()
    return f'<a class="download-btn" href="data:text/csv;base64,{b64}" download="{filename}">{text}</a>'

def overview_dashboard(df):
    """Overview dashboard with enhanced visualizations and export option"""
    st.markdown("## 📊 Overview Dashboard")
    
    # Key metrics with improved layout
    cols = st.columns(5)
    metrics = [
        ("Total Customers", f"{len(df):,}", ""),
        ("Success Rate", f"{df['y'].mean():.1%}", ""),
        ("Average Age", f"{df['age'].mean():.1f}", ""),
        ("Average Balance", f"${df['balance'].mean():,.0f}", ""),
        ("Avg Call Duration", f"{df['duration'].mean():.0f}s", "")
    ]
    
    for col, (label, value, delta) in zip(cols, metrics):
        with col:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                label=label,
                value=value,
                delta=delta if delta else None
            )
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(
            values=df['y'].value_counts().values,
            names=['No', 'Yes'],
            title="Campaign Success Distribution",
            color_discrete_sequence=['#ff7f7f', '#7fbf7f'],
            hole=0.4
        )
        fig.update_layout(height=400, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.histogram(
            df, x='age', nbins=30,
            title="Age Distribution",
            color_discrete_sequence=['#1f77b4'],
            marginal="box"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Summary statistics with export option
    st.markdown("### 📋 Summary Statistics")
    numerical_cols = [col for col in ['age', 'balance', 'duration', 'campaign', 'previous'] if col in df.columns]
    if numerical_cols:
        summary_stats = df[numerical_cols].describe().round(2)
        st.dataframe(summary_stats, use_container_width=True)
        st.markdown(get_download_link(summary_stats, "summary_stats.csv", "Download Summary Statistics"), unsafe_allow_html=True)
    else:
        st.warning("No numerical columns found for summary statistics")

def demographics_dashboard(df):
    """Enhanced demographics dashboard with additional insights"""
    st.markdown("## 👥 Demographics Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'job' in df.columns:
            job_counts = df['job'].value_counts()
            fig = px.bar(
                x=job_counts.index, y=job_counts.values,
                title="Job Distribution",
                labels={'x': 'Job', 'y': 'Count'},
                color=job_counts.values,
                color_continuous_scale='Blues'
            )
            fig.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Job column not found in dataset")
    
    with col2:
        if 'job' in df.columns and 'y' in df.columns:
            job_success = df.groupby('job')['y'].mean().sort_values(ascending=False)
            fig = px.bar(
                x=job_success.index, y=job_success.values,
                title="Success Rate by Job",
                labels={'x': 'Job', 'y': 'Success Rate'},
                color=job_success.values,
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Required columns (job, y) not found")
    
    # Additional demographic analysis
    col1, col2 = st.columns(2)
    
    with col1:
        if 'education' in df.columns and 'age' in df.columns and 'y' in df.columns:
            fig = px.box(
                df, x='education', y='age',
                title="Age Distribution by Education",
                color='y',
                color_discrete_sequence=['#ff7f7f', '#7fbf7f']
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Required columns (education, age, y) not found")
    
    with col2:
        if 'marital' in df.columns and 'balance' in df.columns and 'y' in df.columns:
            fig = px.box(
                df, x='marital', y='balance',
                title="Balance Distribution by Marital Status",
                color='y',
                color_discrete_sequence=['#ff7f7f', '#7fbf7f']
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Required columns (marital, balance, y) not found")
    
    # Enhanced age group analysis
    if 'age' in df.columns:
        df_temp = df.copy()
        df_temp['age_group'] = pd.cut(df_temp['age'], bins=[0, 30, 40, 50, 60, 100], labels=['<30', '30-40', '40-50', '50-60', '60+'])
        
        if 'y' in df_temp.columns and 'balance' in df_temp.columns and 'duration' in df_temp.columns:
            age_group_stats = df_temp.groupby('age_group').agg({
                'y': ['count', 'mean'],
                'balance': ['mean', 'median'],
                'duration': ['mean', 'median']
            }).round(2)
            
            st.markdown("### 📊 Age Group Analysis")
            st.dataframe(age_group_stats, use_container_width=True)
            st.markdown(get_download_link(age_group_stats, "age_group_stats.csv", "Download Age Group Statistics"), unsafe_allow_html=True)
        else:
            st.warning("Required columns for age group analysis not found")
    else:
        st.warning("Age column not found in dataset")

def financial_dashboard(df):
    """Enhanced financial dashboard with additional visualizations"""
    st.markdown("## 💰 Financial Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'balance' in df.columns:
            fig = px.histogram(
                df, x='balance', nbins=50,
                title="Balance Distribution",
                color='y' if 'y' in df.columns else None,
                color_discrete_sequence=['#ff7f7f', '#7fbf7f'],
                marginal="violin"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Balance column not found")
    
    with col2:
        if 'balance' in df.columns and 'y' in df.columns:
            fig = px.box(
                df, x='y', y='balance',
                title="Balance Distribution by Target",
                labels={'y': 'Balance', 'x': 'Campaign Success'},
                color='y',
                color_discrete_sequence=['#ff7f7f', '#7fbf7f'],
                points="all"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Required columns (balance, y) not found")
    
    # Enhanced financial segments
    if 'balance' in df.columns and 'housing' in df.columns:
        df_temp = df.copy()
        df_temp['balance_category'] = pd.cut(df_temp['balance'], 
                                   bins=[-float('inf'), 0, 1000, 5000, float('inf')],
                                   labels=['Negative', '0-1K', '1K-5K', '5K+'])
        
        if 'y' in df_temp.columns and 'age' in df_temp.columns and 'duration' in df_temp.columns:
            balance_stats = df_temp.groupby(['balance_category', 'housing']).agg({
                'y': ['count', 'mean'],
                'age': 'mean',
                'duration': 'mean'
            }).round(2)
            
            st.markdown("### 💳 Financial Segments")
            st.dataframe(balance_stats, use_container_width=True)
            st.markdown(get_download_link(balance_stats, "balance_stats.csv", "Download Financial Segments"), unsafe_allow_html=True)
        else:
            st.warning("Required columns for financial segments not found")
    else:
        st.warning("Required columns (balance, housing) not found")

def campaign_dashboard(df):
    """Enhanced campaign dashboard with interactive elements"""
    st.markdown("## 📞 Campaign Dashboard")
    
    # Interactive campaign analysis
    col1, col2 = st.columns(2)
    
    with col1:
        if 'contact' in df.columns and 'y' in df.columns:
            contact_success = df.groupby('contact')['y'].mean().sort_values(ascending=False)
            fig = px.bar(
                x=contact_success.index, y=contact_success.values,
                title="Success Rate by Contact Method",
                labels={'x': 'Contact Method', 'y': 'Success Rate'},
                color=contact_success.values,
                color_continuous_scale='Greens'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Required columns (contact, y) not found")
    
    with col2:
        if 'campaign' in df.columns:
            fig = px.histogram(
                df, x='campaign', nbins=20,
                title="Campaign Contacts Distribution",
                color='y' if 'y' in df.columns else None,
                color_discrete_sequence=['#ff7f7f', '#7fbf7f'],
                marginal="box"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Campaign column not found")
    
    # Interactive duration analysis
    if 'duration' in df.columns and 'contact' in df.columns and 'y' in df.columns:
        duration_category = pd.cut(df['duration'], 
                                 bins=[0, 60, 180, 300, float('inf')],
                                 labels=['<1 min', '1-3 min', '3-5 min', '5+ min'])
        
        duration_analysis = df.groupby([duration_category, 'contact'])['y'].mean().reset_index()
        
        fig = px.bar(
            duration_analysis, x='duration', y='y', color='contact',
            title="Success Rate by Call Duration and Contact Method",
            labels={'duration': 'Call Duration', 'y': 'Success Rate'},
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Required columns (duration, contact, y) not found")

def temporal_dashboard(df):
    """Enhanced temporal dashboard with trend analysis"""
    st.markdown("## 📅 Temporal Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'month' in df.columns:
            month_counts = df['month'].value_counts()
            fig = px.line(
                x=month_counts.index, y=month_counts.values,
                title="Campaign Volume by Month",
                labels={'x': 'Month', 'y': 'Number of Calls'},
                markers=True
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Month column not found")
    
    with col2:
        if 'month' in df.columns and 'y' in df.columns:
            month_success = df.groupby('month')['y'].mean().sort_values(ascending=False)
            fig = px.line(
                x=month_success.index, y=month_success.values,
                title="Success Rate by Month",
                labels={'x': 'Month', 'y': 'Success Rate'},
                markers=True
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Required columns (month, y) not found")

def advanced_dashboard(df):
    """Enhanced advanced analysis with additional statistical tests"""
    st.markdown("## 🔍 Advanced Analysis")
    
    # Correlation matrix
    numerical_cols = [col for col in ['age', 'balance', 'duration', 'campaign', 'previous', 'y'] if col in df.columns]
    if len(numerical_cols) > 1:
        corr_matrix = df[numerical_cols].corr()
        
        fig = px.imshow(
            corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.index,
            title="Correlation Matrix",
            color_continuous_scale='RdBu',
            text_auto=True
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Not enough numerical columns for correlation matrix")
    
    # Enhanced statistical analysis
    st.markdown("### 📊 Statistical Analysis")
    numerical_vars = [col for col in ['age', 'balance', 'duration', 'campaign'] if col in df.columns and 'y' in df.columns]
    test_results = []
    
    for var in numerical_vars:
        group_0 = df[df['y'] == 0][var]
        group_1 = df[df['y'] == 1][var]
        t_stat, p_value = stats.ttest_ind(group_0, group_1)
        test_results.append({
            'Variable': var,
            'T-statistic': f"{t_stat:.3f}",
            'P-value': f"{p_value:.3e}" if p_value < 0.001 else f"{p_value:.3f}",
            'Significant': "✅" if p_value < 0.05 else "❌"
        })
    
    if test_results:
        test_df = pd.DataFrame(test_results)
        st.dataframe(test_df, use_container_width=True)
        st.markdown(get_download_link(test_df, "statistical_tests.csv", "Download Statistical Tests"), unsafe_allow_html=True)
    else:
        st.warning("No valid columns found for statistical tests")

def create_sidebar_filters(df):
    """Enhanced sidebar filters with better UX"""
    with st.sidebar:
        st.markdown('<div class="sidebar-header">🔧 Controls & Filters</div>', unsafe_allow_html=True)
        
        # Data info
        st.markdown("### 📊 Dataset Info")
        with st.expander("View Details"):
            st.write(f"**Records:** {len(df):,}")
            st.write(f"**Features:** {len(df.columns)}")
            if 'y' in df.columns:
                st.write(f"**Success Rate:** {df['y'].mean():.1%}")
            else:
                st.write("**Success Rate:** N/A")
        
        # Filters with better organization
        st.markdown("### 🎛️ Filters")
        
        with st.expander("Demographic Filters"):
            if 'age' in df.columns:
                age_range = st.slider(
                    "Age Range",
                    min_value=int(df['age'].min()),
                    max_value=int(df['age'].max()),
                    value=(int(df['age'].min()), int(df['age'].max())),
                    step=1
                )
            else:
                age_range = (18, 70)
            
            if 'job' in df.columns:
                job_options = ['All'] + sorted(list(df['job'].unique()))
                selected_job = st.selectbox("Job Category", job_options)
            else:
                selected_job = 'All'
            
            if 'education' in df.columns:
                education_options = ['All'] + sorted(list(df['education'].unique()))
                selected_education = st.selectbox("Education Level", education_options)
            else:
                selected_education = 'All'
            
            if 'marital' in df.columns:
                marital_options = ['All'] + sorted(list(df['marital'].unique()))
                selected_marital = st.selectbox("Marital Status", marital_options)
            else:
                selected_marital = 'All'
        
        with st.expander("Financial Filters"):
            if 'balance' in df.columns:
                balance_range = st.slider(
                    "Balance Range",
                    min_value=int(df['balance'].min()),
                    max_value=int(df['balance'].max()),
                    value=(int(df['balance'].min()), int(df['balance'].max())),
                    step=100
                )
            else:
                balance_range = (-1000, 5000)
            
            if 'duration' in df.columns:
                duration_range = st.slider(
                    "Call Duration (seconds)",
                    min_value=int(df['duration'].min()),
                    max_value=int(df['duration'].max()),
                    value=(int(df['duration'].min()), int(df['duration'].max())),
                    step=10
                )
            else:
                duration_range = (0, 1000)
        
        return {
            'age_range': age_range,
            'selected_job': selected_job,
            'selected_education': selected_education,
            'selected_marital': selected_marital,
            'balance_range': balance_range,
            'duration_range': duration_range
        }

def main():
    """Main application function"""
    st.markdown('<h1 class="main-header">🏦 Banking Data EDA Dashboard</h1>', unsafe_allow_html=True)
    
    # File uploader
    uploaded_file = st.file_uploader("Upload banking data CSV", type=['csv'])
    
    if uploaded_file:
        df = load_data(uploaded_file)
    else:
        df = load_data()
    
    if df is None:
        st.error("Failed to load data. Please check your file format or try again.")
        return
    
    # Create sidebar filters
    filters = create_sidebar_filters(df)
    
    # Apply filters
    filtered_df = apply_filters(df, filters)
    
    if filtered_df.empty:
        st.warning("⚠️ No data available after applying filters. Please adjust the filter settings.")
        return
    
    # Create tabs
    tabs = st.tabs(["Overview", "Demographics", "Financial", "Campaign", "Temporal", "Advanced"])
    
    # Render dashboards
    with tabs[0]:
        overview_dashboard(filtered_df)
    with tabs[1]:
        demographics_dashboard(filtered_df)
    with tabs[2]:
        financial_dashboard(filtered_df)
    with tabs[3]:
        campaign_dashboard(filtered_df)
    with tabs[4]:
        temporal_dashboard(filtered_df)
    with tabs[5]:
        advanced_dashboard(filtered_df)

if __name__ == "__main__":
    main()