# streamlit_app.py
# ULTRA PREMIUM DARK THEME DASHBOARD
# Palo Alto Networks HR Analytics

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Palo Alto Networks HR Intelligence",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------
# CUSTOM CSS (Netflix Premium Theme)
# ---------------------------------------------------
st.markdown("""
<style>

/* Sidebar Background */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#16222A,#3A6073,#1c92d2);
}

/* Sidebar Title */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] label {
    color: #00E5FF !important;
    font-weight: 700;
}

/* Selectbox / Multiselect */
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background-color: #244c66 !important;
    color: white !important;
    border: 1px solid #00E5FF !important;
    border-radius: 10px;
}

/* Dropdown selected text */
section[data-testid="stSidebar"] span {
    color: white !important;
}

/* Slider */
section[data-testid="stSidebar"] .stSlider label {
    color: #B3F5FF !important;
}

/* Slider Track */
section[data-testid="stSidebar"] div[data-baseweb="slider"] > div > div {
    background: #00E5FF !important;
}

/* Numbers */
section[data-testid="stSidebar"] .st-bq {
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Palo Alto Networks.csv")
    return df

df = load_data()

# ---------------------------------------------------
# FEATURE ENGINEERING
# ---------------------------------------------------
df["Engagement_Index"] = (
    df["JobInvolvement"] +
    df["JobSatisfaction"] +
    df["EnvironmentSatisfaction"] +
    df["RelationshipSatisfaction"]
) / 4

conditions = [
    (df["OverTime"] == "Yes") & (df["WorkLifeBalance"] <= 2),
    (df["OverTime"] == "Yes")
]

choices = ["High", "Medium"]

df["Burnout_Risk"] = np.select(
    conditions,
    choices,
    default="Low"
)

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------
st.sidebar.title("⚙ Executive Filters")

dept = st.sidebar.multiselect(
    "Department",
    df["Department"].unique(),
    default=df["Department"].unique()
)

role = st.sidebar.multiselect(
    "Job Role",
    df["JobRole"].unique(),
    default=df["JobRole"].unique()
)

overtime = st.sidebar.selectbox(
    "Overtime",
    ["All", "Yes", "No"]
)

threshold = st.sidebar.slider(
    "Low Engagement Threshold",
    1.0, 4.0, 2.5
)

tenure = st.sidebar.slider(
    "Years At Company",
    int(df["YearsAtCompany"].min()),
    int(df["YearsAtCompany"].max()),
    (
        int(df["YearsAtCompany"].min()),
        int(df["YearsAtCompany"].max())
    )
)

# ---------------------------------------------------
# FILTER DATA
# ---------------------------------------------------
filtered_df = df[
    (df["Department"].isin(dept)) &
    (df["JobRole"].isin(role)) &
    (df["YearsAtCompany"].between(tenure[0], tenure[1]))
]

if overtime != "All":
    filtered_df = filtered_df[
        filtered_df["OverTime"] == overtime
    ]

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------
st.title("🔥 Palo Alto Networks HR Intelligence Center")
st.caption("Executive Dashboard | Burnout Detection | Retention Analytics")

# ---------------------------------------------------
# KPI CARDS
# ---------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Engagement Score",
    round(filtered_df["Engagement_Index"].mean(),2)
)

col2.metric(
    "Burnout Risk",
    len(filtered_df[filtered_df["Burnout_Risk"]=="High"])
)

col3.metric(
    "Attrition %",
    str(round(filtered_df["Attrition"].mean()*100,2))+"%"
)

col4.metric(
    "Work-Life Balance",
    round(filtered_df["WorkLifeBalance"].mean(),2)
)

# ---------------------------------------------------
# CHART THEME
# ---------------------------------------------------
chart_theme = dict(
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    font=dict(color="white")
)

# ---------------------------------------------------
# SECTION 1
# ---------------------------------------------------
st.header("📈 Engagement Intelligence")

fig1 = px.histogram(
    filtered_df,
    x="Engagement_Index",
    nbins=25,
    color_discrete_sequence=["#12E0CC"]
)
fig1.update_layout(**chart_theme)
st.plotly_chart(fig1, use_container_width=True)

fig2 = px.box(
    filtered_df,
    x="Department",
    y="Engagement_Index",
    color="Department"
)
fig2.update_layout(**chart_theme)
st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------
# SECTION 2
# ---------------------------------------------------
st.header("🔥 Burnout Risk Center")

fig3 = px.pie(
    filtered_df,
    names="Burnout_Risk",
    color="Burnout_Risk",
    color_discrete_map={
        "Low":"#33eba1",
        "Medium":"#2dbcec",
        "High":"#E92D92"
    },
    hole=0.55
)
fig3.update_layout(**chart_theme)
st.plotly_chart(fig3, use_container_width=True)

fig4 = px.scatter(
    filtered_df,
    x="WorkLifeBalance",
    y="Engagement_Index",
    color="Burnout_Risk",
    size="MonthlyIncome",
    color_discrete_map={
        "Low":"#b5ed29",
        "Medium":"#e24141",
        "High":"#B725E8"
    }
)
fig4.update_layout(**chart_theme)
st.plotly_chart(fig4, use_container_width=True)

# ---------------------------------------------------
# SECTION 3
# ---------------------------------------------------
st.header("💼 Career Stage Analytics")

fig5 = px.line(
    filtered_df.groupby("YearsAtCompany")["Engagement_Index"].mean().reset_index(),
    x="YearsAtCompany",
    y="Engagement_Index",
    markers=True
)
fig5.update_traces(line_color="#1EACE4")
fig5.update_layout(**chart_theme)
st.plotly_chart(fig5, use_container_width=True)

fig6 = px.bar(
    filtered_df.groupby("JobRole")["Engagement_Index"].mean().reset_index(),
    x="JobRole",
    y="Engagement_Index",
    color="Engagement_Index",
    color_continuous_scale="Blues"
)
fig6.update_layout(**chart_theme)
st.plotly_chart(fig6, use_container_width=True)

# ---------------------------------------------------
# MANAGER ACTION PANEL
# ---------------------------------------------------
st.header("🚨 Manager Action Panel")

alerts = filtered_df[
    filtered_df["Engagement_Index"] <= threshold
]

st.subheader("Low Engagement Employees")

st.dataframe(
    alerts[
        [
            "Age",
            "Department",
            "JobRole",
            "YearsAtCompany",
            "Engagement_Index",
            "Burnout_Risk",
            "OverTime"
        ]
    ],
    use_container_width=True
)

# ---------------------------------------------------
# DOWNLOAD BUTTON
# ---------------------------------------------------
csv = alerts.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇ Download Risk Report",
    csv,
    "risk_report.csv",
    "text/csv"
)

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------
st.markdown("---")
st.caption("Designed for Palo Alto Networks | Premium Executive Interface")
