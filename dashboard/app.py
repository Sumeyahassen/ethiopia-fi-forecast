"""
dashboard/app.py
Ethiopia Financial Inclusion Forecast — Interactive Dashboard
Run with: streamlit run dashboard/app.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pickle

st.set_page_config(page_title="Ethiopia Financial Inclusion Forecast", layout="wide")

# ============================================================
# Data loading
# ============================================================
@st.cache_data
def load_data():
    df = pd.read_csv('data/processed/ethiopia_fi_enriched.csv', parse_dates=['observation_date'])
    obs = df[df['record_type'] == 'observation'].copy()
    events = df[df['record_type'] == 'event'].copy()
    targets = df[df['record_type'] == 'target'].copy()
    obs['year'] = obs['observation_date'].dt.year
    return df, obs, events, targets

@st.cache_data
def load_forecasts():
    with open('models/forecast_models.pkl', 'rb') as f:
        return pickle.load(f)

try:
    df, obs, events, targets = load_data()
    forecasts = load_forecasts()
    data_loaded = True
except FileNotFoundError as e:
    data_loaded = False
    st.error(f"Could not load data files: {e}. Make sure you run the app "
             f"from the project root: `streamlit run dashboard/app.py`")

if data_loaded:

    # ============================================================
    # Sidebar navigation
    # ============================================================
    st.sidebar.title("🇪🇹 Ethiopia FI Forecast")
    page = st.sidebar.radio("Navigate", ["Overview", "Trends", "Forecasts", "Inclusion Projections"])

    # ============================================================
    # PAGE 1: OVERVIEW
    # ============================================================
    if page == "Overview":
        st.title("Ethiopia Financial Inclusion — Overview")
        st.markdown("Key metrics tracking Ethiopia's digital financial transformation.")

        access_latest = obs[obs['indicator_code'] == 'ACC_OWNERSHIP'].dropna(subset=['value_numeric'])
        access_latest = access_latest[~access_latest['original_text'].astype(str).str.contains(
            'disaggregated', case=False, na=False)].sort_values('observation_date')

        mm_latest = obs[obs['indicator_code'] == 'ACC_MM_ACCOUNT'].sort_values('observation_date')
        crossover = obs[obs['indicator_code'] == 'USG_CROSSOVER'].sort_values('observation_date')

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if len(access_latest) >= 2:
                current = access_latest['value_numeric'].iloc[-1]
                prev = access_latest['value_numeric'].iloc[-2]
                st.metric("Account Ownership (Access)", f"{current:.0f}%", f"{current-prev:+.0f}pp")
        with col2:
            if len(mm_latest) >= 2:
                current = mm_latest['value_numeric'].iloc[-1]
                prev = mm_latest['value_numeric'].iloc[-2]
                st.metric("Mobile Money Accounts", f"{current:.1f}%", f"{current-prev:+.1f}pp")
        with col3:
            n_events = len(events)
            st.metric("Cataloged Events", n_events)
        with col4:
            if len(crossover) > 0:
                val = crossover['value_numeric'].iloc[-1]
                st.metric("P2P/ATM Crossover Ratio", f"{val:.2f}")
            else:
                st.metric("P2P/ATM Crossover Ratio", "N/A")

        st.markdown("---")
        st.subheader("Access Growth Rate by Period")
        if len(access_latest) >= 2:
            access_latest = access_latest.copy()
            access_latest['pp_change'] = access_latest['value_numeric'].diff()
            fig = px.bar(access_latest.iloc[1:], x='observation_date', y='pp_change',
                         title="Percentage Point Change Between Survey Rounds",
                         labels={'pp_change': 'pp change', 'observation_date': 'Survey Round'})
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Record Composition")
        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(df, names='record_type', title='Records by Type')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            conf_counts = df['confidence'].value_counts(dropna=False).reset_index()
            conf_counts.columns = ['confidence', 'count']
            fig = px.bar(conf_counts, x='confidence', y='count', title='Data Confidence Levels')
            st.plotly_chart(fig, use_container_width=True)

    # ============================================================
    # PAGE 2: TRENDS
    # ============================================================
    elif page == "Trends":
        st.title("Historical Trends")

        indicator_options = sorted(obs['indicator_code'].dropna().unique())
        selected_indicators = st.multiselect(
            "Select indicators to compare", indicator_options,
            default=['ACC_OWNERSHIP', 'ACC_MM_ACCOUNT'] if 'ACC_OWNERSHIP' in indicator_options else indicator_options[:2]
        )

        date_range = st.date_input(
            "Date range",
            value=(obs['observation_date'].min(), obs['observation_date'].max())
        )

        if selected_indicators:
            filtered = obs[obs['indicator_code'].isin(selected_indicators)]
            if len(date_range) == 2:
                filtered = filtered[
                    (filtered['observation_date'] >= pd.Timestamp(date_range[0])) &
                    (filtered['observation_date'] <= pd.Timestamp(date_range[1]))
                ]
            # drop known duplicate-tagged disaggregated rows for ACC_OWNERSHIP
            filtered = filtered[~filtered['original_text'].astype(str).str.contains(
                'disaggregated', case=False, na=False)]

            fig = px.line(filtered.sort_values('observation_date'), x='observation_date',
                          y='value_numeric', color='indicator_code', markers=True,
                          title="Indicator Trends Over Time",
                          labels={'value_numeric': '%', 'observation_date': 'Date'})
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Event Timeline")
            fig2 = go.Figure()
            for code in selected_indicators:
                sub = filtered[filtered['indicator_code'] == code].sort_values('observation_date')
                fig2.add_trace(go.Scatter(x=sub['observation_date'], y=sub['value_numeric'],
                                          mode='lines+markers', name=code))
            for _, ev in events.iterrows():
                fig2.add_vline(x=ev['observation_date'].timestamp() * 1000,
                               line_dash="dash", line_color="gray", opacity=0.4)
            fig2.update_layout(title="Trends with Event Overlay", yaxis_title="%")
            st.plotly_chart(fig2, use_container_width=True)

            st.subheader("Data Table")
            st.dataframe(filtered[['observation_date', 'indicator_code', 'indicator',
                                     'value_numeric', 'source_name', 'confidence']])

            csv = filtered.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download this data as CSV", csv, "trends_data.csv", "text/csv")
        else:
            st.info("Select at least one indicator to view trends.")

    # ============================================================
    # PAGE 3: FORECASTS
    # ============================================================
    elif page == "Forecasts":
        st.title("Forecasts: Access & Usage 2025-2027")

        access_data = forecasts['access_data']
        access_baseline = forecasts['access_baseline']
        access_scenarios = forecasts['access_scenarios']
        usage_projection = forecasts['usage_projection']
        usage_scenarios = forecasts['usage_scenarios']

        model_choice = st.selectbox("Forecast basis", ["Recent growth-rate trend (used)", "Full-history OLS (reference only)"])

        st.subheader("Access (Account Ownership) Forecast")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=access_data['observation_date'], y=access_data['value_numeric'],
                                 mode='lines+markers', name='Historical', line=dict(color='navy', width=3)))
        fig.add_trace(go.Scatter(x=pd.to_datetime(access_scenarios['year'].astype(int).astype(str) + '-01-01'),
                                 y=access_scenarios['base'], mode='lines+markers', name='Base forecast',
                                 line=dict(color='darkorange', width=3)))
        fig.add_trace(go.Scatter(x=pd.to_datetime(access_scenarios['year'].astype(int).astype(str) + '-01-01'),
                                 y=access_scenarios['optimistic'], mode='lines', name='Optimistic',
                                 line=dict(color='green', dash='dot')))
        fig.add_trace(go.Scatter(x=pd.to_datetime(access_scenarios['year'].astype(int).astype(str) + '-01-01'),
                                 y=access_scenarios['pessimistic'], mode='lines', name='Pessimistic',
                                 line=dict(color='red', dash='dot')))
        fig.update_layout(yaxis_title="% of adults", title="Access Forecast with Scenarios")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Usage (Digital Payment Adoption) Forecast")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=pd.to_datetime(usage_scenarios['year'].astype(int).astype(str) + '-01-01'),
                                  y=usage_scenarios['base'], mode='lines+markers', name='Base forecast',
                                  line=dict(color='purple', width=3)))
        fig2.add_trace(go.Scatter(x=pd.to_datetime(usage_scenarios['year'].astype(int).astype(str) + '-01-01'),
                                  y=usage_scenarios['optimistic'], mode='lines', name='Optimistic',
                                  line=dict(color='green', dash='dot')))
        fig2.add_trace(go.Scatter(x=pd.to_datetime(usage_scenarios['year'].astype(int).astype(str) + '-01-01'),
                                  y=usage_scenarios['pessimistic'], mode='lines', name='Pessimistic',
                                  line=dict(color='red', dash='dot')))
        fig2.update_layout(yaxis_title="% of adults", title="Usage Forecast with Scenarios")
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Forecast Table")
        final_table = forecasts['final_table']
        st.dataframe(final_table)
        csv = final_table.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download forecast table as CSV", csv, "forecast_table.csv", "text/csv")

        st.subheader("Key Projected Milestones")
        st.markdown(f"""
        - **Access** projected to reach **{access_scenarios['base'].iloc[-1]:.1f}%** by 2027 (base case)
        - **Usage** projected to reach **{usage_scenarios['base'].iloc[-1]:.1f}%** by 2027 (base case)
        - Wide uncertainty bands reflect limited historical data (only 3-5 usable survey points)
        """)

    # ============================================================
    # PAGE 4: INCLUSION PROJECTIONS
    # ============================================================
    elif page == "Inclusion Projections":
        st.title("Inclusion Projections & Policy Targets")

        scenario = st.radio("Select scenario", ["Pessimistic", "Base", "Optimistic"], horizontal=True)
        scenario_key = scenario.lower()

        access_scenarios = forecasts['access_scenarios']
        usage_scenarios = forecasts['usage_scenarios']

        col1, col2 = st.columns(2)
        with col1:
            val_2027 = access_scenarios[scenario_key].iloc[-1]
            st.metric(f"Access by 2027 ({scenario})", f"{val_2027:.1f}%")
        with col2:
            val_2027_usg = usage_scenarios[scenario_key].iloc[-1]
            st.metric(f"Usage by 2027 ({scenario})", f"{val_2027_usg:.1f}%")

        st.subheader("Progress Toward Policy Target")
        target_row = targets[targets['indicator_code'] == 'ACC_OWNERSHIP']
        if not target_row.empty:
            target_val = target_row.iloc[0]['value_numeric']
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=val_2027,
                title={'text': f"Access vs Target ({target_val}%)"},
                gauge={'axis': {'range': [0, max(target_val, val_2027) * 1.2]},
                       'threshold': {'line': {'color': "red", 'width': 4}, 'value': target_val},
                       'bar': {'color': "darkorange"}}
            ))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No policy target found for ACC_OWNERSHIP in the dataset.")

        st.subheader("Answers to Consortium Questions")
        st.markdown(f"""
        **What drives financial inclusion in Ethiopia?**
        Infrastructure and product launches show measurable but modest effects;
        much of historical growth reflects broader survey-period trends rather
        than single events (see Task 3 impact modeling).

        **How do events affect inclusion outcomes?**
        Our event-indicator model estimates individual event effects of
        1-5 percentage points, ramping up gradually over 3-24 months
        depending on the event type (see Forecasts page).

        **How will Access and Usage look in 2026-2027?**
        Under the {scenario.lower()} scenario: Access ≈ {val_2027:.1f}%,
        Usage ≈ {val_2027_usg:.1f}% by 2027.
        """)

else:
    st.warning("Dashboard cannot load — please run notebooks 01-04 first to generate "
               "`data/processed/ethiopia_fi_enriched.csv` and `models/forecast_models.pkl`.")