import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# -----------------------------
# PAGE CONFIGURATION
# -----------------------------

st.set_page_config(
    page_title="Nassau Candy | Shipping Analytics",
    page_icon="🚚",
    layout="wide"
)

# =========================
# CUSTOM DARK THEME
# =========================

st.markdown("""
<style>

    /* Main App Background */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }

    /* Main content */
    .main {
        background-color: #0e1117;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #262833;
    }

    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    /* Main headings */
    h1, h2, h3 {
        color: #ffffff !important;
    }

    /* Normal text */
    p, span, label {
        color: #ffffff;
    }

    /* Horizontal lines */
    hr {
        border-color: #333740;
    }

    /* KPI metric containers */
    div[data-testid="stMetric"] {
        background-color: #151820;
        border: 1px solid #2d313a;
        border-radius: 12px;
        padding: 15px;
    }

    div[data-testid="stMetricLabel"] {
        color: #b8bdc9 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
    }

    /* Select boxes / multiselect */
    div[data-baseweb="select"] > div {
        background-color: #151820;
        border-color: #333740;
    }

    /* Multiselect text */
    div[data-baseweb="select"] span {
        color: #ffffff !important;
    }

    /* Date input */
    div[data-baseweb="input"] {
        background-color: #151820;
    }

    div[data-baseweb="input"] input {
        color: #ffffff !important;
    }

    /* Sidebar widgets */
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #0e1117;
    }

    /* Dataframes / tables */
    div[data-testid="stDataFrame"] {
        border-radius: 10px;
    }

    /* Buttons */
    .stButton > button {
        background-color: #1f2937;
        color: #ffffff;
        border: 1px solid #374151;
        border-radius: 8px;
    }

    .stButton > button:hover {
        border-color: #ffffff;
    }

</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOAD DATA
# -----------------------------

@st.cache_data
def load_data():

    df = pd.read_csv("cleaned_nassau_candy.csv")

    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], errors="coerce")

    numeric_columns = ["Shipping Lead Time", "Sales", "Units", "Gross Profit"]
    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    text_columns = ["Factory", "State/Province", "Ship Mode", "Delayed"]
    for column in text_columns:
        if column in df.columns:
            df[column] = df[column].astype("string").str.strip()

    return df


df = load_data()


# -----------------------------
# SIDEBAR FILTERS
# -----------------------------

st.sidebar.title("🎛️ Dashboard Filters")

# ------------------------------------------------------------
# DATE FILTER - BULLETPROOF VERSION
# ------------------------------------------------------------

valid_dates = df["Order Date"].dropna()

if not valid_dates.empty:

    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()

    date_range = st.sidebar.date_input(
        "Order Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="date_filter"
    )

else:

    date_range = ()

    st.sidebar.warning(
        "⚠️ No valid Order Dates available."
    )

# Ship Mode Filter
ship_modes = sorted(df["Ship Mode"].dropna().unique())

selected_ship_modes = st.sidebar.multiselect(
    "Ship Mode",
    options=ship_modes,
    default=ship_modes,
    key="ship_filter"
)

# State Filter
states = sorted(df["State/Province"].dropna().unique())

selected_states = st.sidebar.multiselect(
    "State / Province",
    options=states,
    default=states,
    key="state_filter"
)

# Delay Filter
delay_status = st.sidebar.multiselect(
    "Shipment Status",
    options=["Yes", "No"],
    default=["Yes", "No"],
    key="delay_filter"
)

# ============================================================
# LIVE FILTER SUMMARY
# ============================================================

st.sidebar.markdown("---")
st.sidebar.subheader("📌 Current Filters")

# Date summary
if len(date_range) == 2:
    st.sidebar.write(
        f"📅 **Date:** {date_range[0]} → {date_range[1]}"
    )

# Ship Mode summary
st.sidebar.write(f"🚚 **Ship Modes:** {len(selected_ship_modes)} Selected")

# State summary
st.sidebar.write(f"🌍 **States:** {len(selected_states)} Selected")

# Shipment status
st.sidebar.write(
    f"⚠️ **Status:** {', '.join(delay_status) if delay_status else 'None selected'}"
)

# -----------------------------
# APPLY FILTERS
# -----------------------------

filtered_df = df.copy()

# Date filtering
if len(date_range) == 2:

    start_date, end_date = date_range

    filtered_df = filtered_df[
        filtered_df["Order Date"].notna() &
        (filtered_df["Order Date"].dt.date >= start_date) &
        (filtered_df["Order Date"].dt.date <= end_date)
    ]

# Ship mode filtering
filtered_df = filtered_df[
    filtered_df["Ship Mode"].isin(selected_ship_modes)
]

# State filtering
filtered_df = filtered_df[
    filtered_df["State/Province"].isin(selected_states)
]

# Delay filtering
filtered_df = filtered_df[
    filtered_df["Delayed"].isin(delay_status)
]
st.sidebar.write(f"📦 **Records:** {len(filtered_df):,}")
st.sidebar.markdown("---")

if st.sidebar.button("🔄 Reset Filters"):

    for key in ["date_filter", "ship_filter", "state_filter", "delay_filter"]:
        if key in st.session_state:
            del st.session_state[key]

    st.rerun()

# -----------------------------
# DASHBOARD HEADER
# -----------------------------

col1, col2 = st.columns([1,5])

with col1:
    st.image("logo.png", width=1000)

with col2:
    st.title("📦 Nassau Candy Distributor")

st.subheader("Factory-to-Customer Shipping Route Efficiency Dashboard")

st.markdown(
    """
    **Factory-to-Customer Shipping Route Efficiency Analysis**

    Analyze shipping performance, route efficiency,
    geographic bottlenecks, delays, and shipping modes.
    """
)

st.divider()

# ============================================================
# DOWNLOAD FILTERED DATA
# ============================================================

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download Filtered Data (CSV)",
    data=csv,
    file_name="filtered_shipments.csv",
    mime="text/csv"
)

# -----------------------------
# KPI CALCULATIONS
# -----------------------------

total_shipments = len(filtered_df)

avg_lead_time = filtered_df["Shipping Lead Time"].mean()
if pd.isna(avg_lead_time):
    avg_lead_time = 0

delay_rate = (
    filtered_df["Delayed"].eq("Yes").mean() * 100
    if len(filtered_df) > 0 else 0
)

total_sales = filtered_df["Sales"].sum()

total_profit = filtered_df["Gross Profit"].sum()

total_units = filtered_df["Units"].sum()


# -----------------------------
# KPI CARDS
# -----------------------------

st.subheader("📊 Key Performance Indicators")

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric(
        label="Total Shipments",
        value=f"{total_shipments:,}"
    )

with col2:
    st.metric(
        label="Avg Lead Time",
        value=f"{avg_lead_time:.1f} d"
    )

with col3:
    st.metric(
        label="Delay Rate",
        value=f"{delay_rate:.1f}%"
    )

with col4:
    st.metric(
        label="Total Sales",
        value=f"${total_sales:,.0f}"
    )

with col5:
    st.metric(
        label="Gross Profit",
        value=f"${total_profit:,.0f}"
    )

with col6:
    st.metric(
        label="Total Units",
        value=f"{total_units:,}"
    )

st.divider()

# ------------------------------------------------------------
# EMPTY FILTER RESULT GUARD
# ------------------------------------------------------------
if filtered_df.empty:
    st.warning("⚠️ No shipments match the selected filters. Please broaden at least one filter.")
    st.info("Tip: select at least one Ship Mode, one State / Province, and one Shipment Status, and make sure the date range contains data.")
    st.stop()

# ============================================================
# SHIPPING PERFORMANCE OVERVIEW
# ============================================================

st.subheader("📦 Shipping Performance Overview")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Distribution of Shipping Lead Time")

    fig_lead = px.histogram(
        filtered_df,
        x="Shipping Lead Time",
        nbins=15,
        title="Distribution of Shipping Lead Time",
        labels={
            "Shipping Lead Time": "Shipping Lead Time (Days)",
            "count": "Number of Shipments"
        }
    )
    fig_lead.update_traces(
        marker_color="#00CC96"
    )
    fig_lead.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(
        fig_lead,
        use_container_width=True,
        key="chart_fig_lead"
    )


with col2:
    st.markdown("### Shipment Delay Distribution")

    delay_counts = (
        filtered_df["Delayed"]
        .value_counts()
        .reset_index()
    )

    delay_counts.columns = ["Shipment Status", "Number of Shipments"]

    fig_delay = px.bar(
        delay_counts,
        x="Shipment Status",
        y="Number of Shipments",
        title="Shipment Delay Distribution",
        labels={
            "Shipment Status": "Shipment Status",
            "Number of Shipments": "Number of Shipments"
        }
    )
    fig_delay.update_traces(
        marker_color="#EF553B"
    )
    fig_delay.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(
        fig_delay,
        use_container_width=True,
        key="chart_fig_delay"
    )

# ============================================================
# FACTORY PERFORMANCE
# ============================================================

st.divider()

st.subheader("🏭 Factory Performance")

# ------------------------------------------------------------
# Factory-level analysis
# ------------------------------------------------------------

factory_analysis = (
    filtered_df.groupby("Factory")
    .agg(
        Total_Shipments=("Shipping Lead Time", "count"),
        Average_Lead_Time=("Shipping Lead Time", "mean"),
        Delay_Rate=("Delayed", lambda x: (x == "Yes").mean() * 100),
        Total_Sales=("Sales", "sum"),
        Gross_Profit=("Gross Profit", "sum")
    )
    .reset_index()
)

factory_analysis["Average_Lead_Time"] = factory_analysis["Average_Lead_Time"].fillna(0)
factory_analysis["Delay_Rate"] = factory_analysis["Delay_Rate"].fillna(0).clip(0, 100)

# ------------------------------------------------------------
# Shipment Volume by Factory
# ------------------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    factory_volume = (
        factory_analysis
        .sort_values("Total_Shipments", ascending=True)
    )

    fig_factory_volume = px.bar(
        factory_volume,
        x="Total_Shipments",
        y="Factory",
        orientation="h",
        title="Shipment Volume by Factory",
        text="Total_Shipments",
        labels={
            "Total_Shipments": "Number of Shipments",
            "Factory": "Factory"
        }
    )

    fig_factory_volume.update_traces(
        marker_color="#636EFA",
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig_factory_volume.update_layout(
        height=420,
        margin=dict(l=20, r=70, t=60, b=20)
    )

    st.plotly_chart(
        fig_factory_volume,
        use_container_width=True,
        key="chart_fig_factory_volume"
    )


# ------------------------------------------------------------
# Average Lead Time by Factory
# ------------------------------------------------------------

with col2:

    factory_lead = (
        factory_analysis
        .sort_values("Average_Lead_Time", ascending=True)
    )

    fig_factory_lead = px.bar(
        factory_lead,
        x="Average_Lead_Time",
        y="Factory",
        orientation="h",
        title="Average Shipping Lead Time by Factory",
        text="Average_Lead_Time",
        labels={
            "Average_Lead_Time": "Average Lead Time (Days)",
            "Factory": "Factory"
        }
    )

    fig_factory_lead.update_traces(
        marker_color="#00CC96",
        texttemplate="%{text:.1f}",
        textposition="outside"
    )

    fig_factory_lead.update_layout(
        height=420,
        margin=dict(l=20, r=70, t=60, b=20)
    )

    st.plotly_chart(
        fig_factory_lead,
        use_container_width=True,
        key="chart_fig_factory_lead"
    )


# ------------------------------------------------------------
# Factory Delay Rate
# ------------------------------------------------------------

st.markdown("### 🚨 Factory Delay Performance")

fig_factory_delay = px.bar(
    factory_analysis.sort_values(
        "Delay_Rate",
        ascending=True
    ),
    x="Delay_Rate",
    y="Factory",
    orientation="h",
    title="Delay Rate by Factory",
    text="Delay_Rate",
    labels={
        "Delay_Rate": "Delay Rate (%)",
        "Factory": "Factory"
    }
)

fig_factory_delay.update_traces(
    marker_color="#EF553B",
    texttemplate="%{text:.1f}%",
    textposition="outside"
)

fig_factory_delay.update_layout(
    height=420,
    margin=dict(l=20, r=70, t=60, b=20)
)

st.plotly_chart(
    fig_factory_delay,
    use_container_width=True,
    key="chart_fig_factory_delay"
)


# ------------------------------------------------------------
# Factory Performance Table
# ------------------------------------------------------------

st.markdown("### 📋 Factory Performance Summary")

factory_summary = factory_analysis.copy()

factory_summary["Average_Lead_Time"] = (
    factory_summary["Average_Lead_Time"].round(2)
)

factory_summary["Delay_Rate"] = (
    factory_summary["Delay_Rate"].round(2)
)

factory_summary["Total_Sales"] = (
    factory_summary["Total_Sales"].round(2)
)

factory_summary["Gross_Profit"] = (
    factory_summary["Gross_Profit"].round(2)
)
st.caption("Factory-wise shipping performance summary")
st.dataframe(
    factory_summary,
    use_container_width=True,
    hide_index=True
)

# ============================================================
# ROUTE EFFICIENCY ANALYSIS
# ============================================================

st.divider()

st.subheader("🚚 Route Efficiency Analysis")

# ------------------------------------------------------------
# Route-level analysis
# ------------------------------------------------------------

route_dashboard = (
    filtered_df.groupby(["Factory", "State/Province"])
    .agg(
        Total_Shipments=("Shipping Lead Time", "count"),
        Average_Lead_Time=("Shipping Lead Time", "mean"),
        Lead_Time_Variability=("Shipping Lead Time", "std"),
        Minimum_Lead_Time=("Shipping Lead Time", "min"),
        Maximum_Lead_Time=("Shipping Lead Time", "max"),
        Delay_Rate=("Delayed", lambda x: (x == "Yes").mean() * 100),
        Total_Sales=("Sales", "sum"),
        Total_Units=("Units", "sum"),
        Total_Gross_Profit=("Gross Profit", "sum")
    )
    .reset_index()
)

# Create route name
route_dashboard["Route"] = (
    route_dashboard["Factory"].astype(str)
    + " → "
    + route_dashboard["State/Province"].astype(str)
)

route_dashboard["Average_Lead_Time"] = route_dashboard["Average_Lead_Time"].fillna(0)
route_dashboard["Lead_Time_Variability"] = route_dashboard["Lead_Time_Variability"].fillna(0)
route_dashboard["Delay_Rate"] = route_dashboard["Delay_Rate"].fillna(0).clip(0, 100)

# ------------------------------------------------------------
# Route Efficiency Score
# ------------------------------------------------------------

lead_range = (
    route_dashboard["Average_Lead_Time"].max()
    - route_dashboard["Average_Lead_Time"].min()
)

if pd.isna(lead_range) or lead_range == 0:

    route_dashboard["Lead_Time_Score"] = 100

else:

    route_dashboard["Lead_Time_Score"] = (
        100
        * (
            route_dashboard["Average_Lead_Time"].max()
            - route_dashboard["Average_Lead_Time"]
        )
        / lead_range
    )

route_dashboard["Delay_Score"] = (
    100 - route_dashboard["Delay_Rate"]
)

route_dashboard["Route_Efficiency_Score"] = (
    route_dashboard["Lead_Time_Score"] * 0.5
    + route_dashboard["Delay_Score"] * 0.5
)

route_dashboard["Route_Efficiency_Score"] = (
    route_dashboard["Route_Efficiency_Score"]
    .clip(0, 100)
    .fillna(0)
)

# ------------------------------------------------------------
# Route KPI Cards
# ------------------------------------------------------------

best_route = route_dashboard.loc[
    route_dashboard["Route_Efficiency_Score"].idxmax()
]

worst_route = route_dashboard.loc[
    route_dashboard["Route_Efficiency_Score"].idxmin()
]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Routes",
        f"{len(route_dashboard):,}"
    )

with col2:
    st.metric(
        "Best Route Score",
        f"{best_route['Route_Efficiency_Score']:.1f}/100"
    )

with col3:
    st.metric(
        "Worst Route Score",
        f"{worst_route['Route_Efficiency_Score']:.1f}/100"
    )

with col4:
    st.metric(
        "Avg Route Lead Time",
        f"{route_dashboard['Average_Lead_Time'].mean():.1f} days"
    )

# ------------------------------------------------------------
# Top 10 and Bottom 10 Routes
# ------------------------------------------------------------

col1, col2 = st.columns(2)

# TOP 10
with col1:

    st.markdown("### 🏆 Top 10 Most Efficient Routes")

    top_routes = (
        route_dashboard
        .sort_values(
            "Route_Efficiency_Score",
            ascending=False
        )
        .head(10)
        .sort_values(
            "Route_Efficiency_Score",
            ascending=True
        )
    )

    fig_top_routes = px.bar(
        top_routes,
        x="Route_Efficiency_Score",
        y="Route",
        orientation="h",
        title="Top 10 Efficient Routes",
        text="Route_Efficiency_Score",
        labels={
            "Route_Efficiency_Score": "Efficiency Score",
            "Route": "Shipping Route"
        }
    )

    fig_top_routes.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside"
    )

    fig_top_routes.update_layout(
        height=500,
        margin=dict(
            l=20,
            r=60,
            t=60,
            b=20
        )
    )

    st.plotly_chart(
        fig_top_routes,
        use_container_width=True,
        key="chart_fig_top_routes"
    )


# BOTTOM 10
with col2:

    st.markdown("### ⚠️ Bottom 10 Least Efficient Routes")

    bottom_routes = (
        route_dashboard
        .sort_values(
            "Route_Efficiency_Score",
            ascending=True
        )
        .head(10)
        .sort_values(
            "Route_Efficiency_Score",
            ascending=True
        )
    )

    fig_bottom_routes = px.bar(
        bottom_routes,
        x="Route_Efficiency_Score",
        y="Route",
        orientation="h",
        title="Bottom 10 Inefficient Routes",
        text="Route_Efficiency_Score",
        labels={
            "Route_Efficiency_Score": "Efficiency Score",
            "Route": "Shipping Route"
        }
    )

    fig_bottom_routes.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside"
    )

    fig_bottom_routes.update_layout(
        height=500,
        margin=dict(
            l=20,
            r=60,
            t=60,
            b=20
        )
    )

    st.plotly_chart(
        fig_bottom_routes,
        use_container_width=True,
        key="chart_fig_bottom_routes"
    )

# ------------------------------------------------------------
# Route Performance Table
# ------------------------------------------------------------

st.markdown("### 📋 Route Performance Leaderboard")

route_table = (
    route_dashboard[
        [
            "Route",
            "Total_Shipments",
            "Average_Lead_Time",
            "Lead_Time_Variability",
            "Delay_Rate",
            "Route_Efficiency_Score",
            "Total_Sales",
            "Total_Gross_Profit"
        ]
    ]
    .sort_values(
        "Route_Efficiency_Score",
        ascending=False
    )
    .copy()
)

route_table["Average_Lead_Time"] = (
    route_table["Average_Lead_Time"].round(2)
)

route_table["Lead_Time_Variability"] = (
    route_table["Lead_Time_Variability"]
    .fillna(0)
    .round(2)
)

route_table["Delay_Rate"] = (
    route_table["Delay_Rate"].round(2)
)

route_table["Route_Efficiency_Score"] = (
    route_table["Route_Efficiency_Score"].round(2)
)

route_table["Total_Sales"] = (
    route_table["Total_Sales"].round(2)
)

route_table["Total_Gross_Profit"] = (
    route_table["Total_Gross_Profit"].round(2)
)
st.caption("Route-wise shipping efficiency leaderboard")
st.dataframe(
    route_table,
    use_container_width=True,
    hide_index=True
)

# ============================================================
# ROUTE OPERATIONAL RISK ANALYSIS
# ============================================================

st.markdown("### ⚠️ Route Operational Risk")

# Calculate operational risk
route_risk = route_dashboard.copy()

route_risk["Operational_Risk"] = (
    route_risk["Total_Shipments"] *
    route_risk["Delay_Rate"] / 100
)

# Top 10 highest-risk routes
high_risk_routes = (
    route_risk
    .sort_values("Operational_Risk", ascending=False)
    .head(10)
    .sort_values("Operational_Risk", ascending=True)
)

fig_risk = px.bar(
    high_risk_routes,
    x="Operational_Risk",
    y="Route",
    orientation="h",
    title="Top 10 Routes by Operational Risk",
    text="Operational_Risk",
    labels={
        "Operational_Risk": "Operational Risk",
        "Route": "Shipping Route"
    }
)

fig_risk.update_traces(
    texttemplate="%{text:.1f}",
    textposition="outside"
)

fig_risk.update_layout(
    height=500,
    margin=dict(
        l=20,
        r=70,
        t=60,
        b=20
    )
)

st.plotly_chart(
    fig_risk,
    use_container_width=True,
    key="chart_fig_risk"
)

# Risk summary table
st.markdown("### 📋 Highest-Risk Route Summary")

risk_table = route_risk[
    [
        "Route",
        "Total_Shipments",
        "Average_Lead_Time",
        "Delay_Rate",
        "Operational_Risk"
    ]
].copy()

risk_table = (
    risk_table
    .sort_values("Operational_Risk", ascending=False)
    .head(10)
)

risk_table["Average_Lead_Time"] = (
    risk_table["Average_Lead_Time"].round(2)
)

risk_table["Delay_Rate"] = (
    risk_table["Delay_Rate"].round(2)
)

risk_table["Operational_Risk"] = (
    risk_table["Operational_Risk"].round(2)
)

st.dataframe(
    risk_table,
    use_container_width=True,
    hide_index=True
)

# ============================================================
# GEOGRAPHIC SHIPPING ANALYSIS
# ============================================================

st.divider()

st.subheader("🌎 Geographic Shipping Analysis")

st.markdown("### 🗺️ State-wise Shipment Distribution")

# State code mapping
us_state_abbrev = {
    "Alabama":"AL","Alaska":"AK","Arizona":"AZ","Arkansas":"AR",
    "California":"CA","Colorado":"CO","Connecticut":"CT","Delaware":"DE",
    "Florida":"FL","Georgia":"GA","Hawaii":"HI","Idaho":"ID",
    "Illinois":"IL","Indiana":"IN","Iowa":"IA","Kansas":"KS",
    "Kentucky":"KY","Louisiana":"LA","Maine":"ME","Maryland":"MD",
    "Massachusetts":"MA","Michigan":"MI","Minnesota":"MN","Mississippi":"MS",
    "Missouri":"MO","Montana":"MT","Nebraska":"NE","Nevada":"NV",
    "New Hampshire":"NH","New Jersey":"NJ","New Mexico":"NM","New York":"NY",
    "North Carolina":"NC","North Dakota":"ND","Ohio":"OH","Oklahoma":"OK",
    "Oregon":"OR","Pennsylvania":"PA","Rhode Island":"RI",
    "South Carolina":"SC","South Dakota":"SD","Tennessee":"TN","Texas":"TX",
    "Utah":"UT","Vermont":"VT","Virginia":"VA","Washington":"WA",
    "West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY"
}

map_df = (
    filtered_df.groupby("State/Province")
    .size()
    .reset_index(name="Shipments")
)

map_df["State_Code"] = map_df["State/Province"].map(us_state_abbrev)

fig_map = px.choropleth(
    map_df,
    locations="State_Code",
    locationmode="USA-states",
    color="Shipments",
    scope="usa",
    hover_name="State/Province",
    color_continuous_scale="Blues",
    title="State-wise Shipment Volume"
)

fig_map.update_layout(
    height=650,
    margin=dict(l=10, r=10, t=50, b=10)
)

st.plotly_chart(fig_map, use_container_width=True)

# ------------------------------------------------------------
# State-level analysis
# ------------------------------------------------------------

state_analysis = (
    filtered_df.groupby("State/Province")
    .agg(
        Total_Shipments=("Shipping Lead Time", "count"),
        Average_Lead_Time=("Shipping Lead Time", "mean"),
        Delay_Rate=("Delayed", lambda x: (x == "Yes").mean() * 100),
        Total_Sales=("Sales", "sum"),
        Total_Gross_Profit=("Gross Profit", "sum")
    )
    .reset_index()
)

state_analysis["Average_Lead_Time"] = state_analysis["Average_Lead_Time"].fillna(0)
state_analysis["Delay_Rate"] = state_analysis["Delay_Rate"].fillna(0).clip(0, 100)
# ------------------------------------------------------------
# Convert State Names to US State Codes
# ------------------------------------------------------------

state_map = {
    "Alabama":"AL","Alaska":"AK","Arizona":"AZ","Arkansas":"AR",
    "California":"CA","Colorado":"CO","Connecticut":"CT","Delaware":"DE",
    "Florida":"FL","Georgia":"GA","Hawaii":"HI","Idaho":"ID",
    "Illinois":"IL","Indiana":"IN","Iowa":"IA","Kansas":"KS",
    "Kentucky":"KY","Louisiana":"LA","Maine":"ME","Maryland":"MD",
    "Massachusetts":"MA","Michigan":"MI","Minnesota":"MN","Mississippi":"MS",
    "Missouri":"MO","Montana":"MT","Nebraska":"NE","Nevada":"NV",
    "New Hampshire":"NH","New Jersey":"NJ","New Mexico":"NM","New York":"NY",
    "North Carolina":"NC","North Dakota":"ND","Ohio":"OH","Oklahoma":"OK",
    "Oregon":"OR","Pennsylvania":"PA","Rhode Island":"RI",
    "South Carolina":"SC","South Dakota":"SD","Tennessee":"TN",
    "Texas":"TX","Utah":"UT","Vermont":"VT","Virginia":"VA",
    "Washington":"WA","West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY"
}

state_analysis["State_Code"] = state_analysis["State/Province"].map(state_map)

# ------------------------------------------------------------
# State Shipment Volume
# ------------------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    shipment_volume = (
        state_analysis
        .sort_values("Total_Shipments", ascending=False)
        .head(15)
        .sort_values("Total_Shipments", ascending=True)
    )

    fig_volume = px.bar(
        shipment_volume,
        x="Total_Shipments",
        y="State/Province",
        orientation="h",
        title="Top 15 States by Shipment Volume",
        text="Total_Shipments",
        labels={
            "Total_Shipments": "Shipments",
            "State/Province": "State"
        }
    )

    fig_volume.update_traces(
        texttemplate="%{text:,}",
        textposition="outside"
    )

    fig_volume.update_layout(
        height=550,
        margin=dict(l=20, r=70, t=60, b=20)
    )

    st.plotly_chart(
        fig_volume,
        use_container_width=True,
        key="chart_fig_volume"
    )
st.markdown("### 🗺️ State-wise Shipment Volume Map")

fig_map = px.choropleth(
    state_analysis,
    locations="State_Code",
    locationmode="USA-states",
    color="Total_Shipments",
    scope="usa",
    color_continuous_scale="Blues",
    hover_name="State/Province",
    hover_data={
        "Total_Shipments": True,
        "Average_Lead_Time":":.1f",
        "Delay_Rate":":.1f"
    },
    title="Shipment Volume Across United States"
)

fig_map.update_layout(
    height=650,
    margin=dict(l=10,r=10,t=60,b=10)
)

st.plotly_chart(
    fig_map,
    use_container_width=True
)

# ------------------------------------------------------------
# Average Lead Time by State
# ------------------------------------------------------------

with col2:

    lead_time_state = (
        state_analysis
        .sort_values("Average_Lead_Time", ascending=False)
        .head(15)
        .sort_values("Average_Lead_Time", ascending=True)
    )

    fig_state_lead = px.bar(
        lead_time_state,
        x="Average_Lead_Time",
        y="State/Province",
        orientation="h",
        title="Highest Average Lead Time by State",
        text="Average_Lead_Time",
        labels={
            "Average_Lead_Time": "Average Lead Time (Days)",
            "State/Province": "State"
        }
    )

    fig_state_lead.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside"
    )

    fig_state_lead.update_layout(
        height=550,
        margin=dict(l=20, r=70, t=60, b=20)
    )

    st.plotly_chart(
        fig_state_lead,
        use_container_width=True,
        key="chart_fig_state_lead"
    )


# ------------------------------------------------------------
# Delay Rate by State
# ------------------------------------------------------------

st.markdown("### 🚨 Geographic Delay Analysis")

delay_states = (
    state_analysis
    .sort_values("Delay_Rate", ascending=False)
    .head(15)
    .sort_values("Delay_Rate", ascending=True)
)

fig_delay_state = px.bar(
    delay_states,
    x="Delay_Rate",
    y="State/Province",
    orientation="h",
    title="States with Highest Delay Rates",
    text="Delay_Rate",
    labels={
        "Delay_Rate": "Delay Rate (%)",
        "State/Province": "State"
    }
)

fig_delay_state.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside"
)

fig_delay_state.update_layout(
    height=550,
    margin=dict(l=20, r=70, t=60, b=20)
)

st.plotly_chart(
    fig_delay_state,
    use_container_width=True,
    key="chart_fig_delay_state"
)
st.markdown("### 🗺️ State-wise Delay Rate Map")

fig_delay_map = px.choropleth(
    state_analysis,
    locations="State_Code",
    locationmode="USA-states",
    color="Delay_Rate",
    scope="usa",
    color_continuous_scale="Reds",
    hover_name="State/Province",
    hover_data={
        "Delay_Rate":":.1f",
        "Total_Shipments":True,
        "Average_Lead_Time":":.1f"
    },
    title="Shipment Delay Rate Across United States"
)

fig_delay_map.update_layout(
    height=650,
    margin=dict(l=10,r=10,t=60,b=10)
)

st.plotly_chart(
    fig_delay_map,
    use_container_width=True
)

# ============================================================
# US DELAY RATE MAP
# ============================================================

st.markdown("### 🗺️ US Delay Rate Heat Map")

fig_delay_map = px.choropleth(
    state_analysis,
    locations="State/Province",
    locationmode="USA-states",     # State codes like CA, TX, NY
    color="Delay_Rate",
    scope="usa",
    color_continuous_scale="Reds",
    hover_name="State/Province",
    hover_data={
        "Delay_Rate": ":.1f",
        "Total_Shipments": True,
        "Average_Lead_Time": ":.1f"
    },
    labels={
        "Delay_Rate": "Delay Rate (%)"
    },
    title="State-wise Shipment Delay Rate"
)

fig_delay_map.update_layout(
    height=650,
    margin=dict(l=10, r=10, t=60, b=10),
    geo=dict(bgcolor="rgba(0,0,0,0)")
)

st.plotly_chart(
    fig_delay_map,
    use_container_width=True,
    key="delay_rate_map"
)

# ------------------------------------------------------------
# Geographic Bottleneck Detection
# ------------------------------------------------------------

st.markdown("### ⚠️ Geographic Bottlenecks")

overall_state_lead = state_analysis["Average_Lead_Time"].mean()
overall_state_delay = state_analysis["Delay_Rate"].mean()

bottlenecks = state_analysis[
    (state_analysis["Average_Lead_Time"] >= overall_state_lead) &
    (state_analysis["Delay_Rate"] >= overall_state_delay)
].copy()

bottlenecks = bottlenecks.sort_values(
    ["Delay_Rate", "Total_Shipments"],
    ascending=[False, False]
)

if len(bottlenecks) > 0:

    st.info(
        f"Identified {len(bottlenecks)} states with "
        "above-average lead time and above-average delay rate."
    )

    bottleneck_table = bottlenecks[
        [
            "State/Province",
            "Total_Shipments",
            "Average_Lead_Time",
            "Delay_Rate",
            "Total_Sales",
            "Total_Gross_Profit"
        ]
    ].copy()

    bottleneck_table["Average_Lead_Time"] = (
        bottleneck_table["Average_Lead_Time"].round(2)
    )

    bottleneck_table["Delay_Rate"] = (
        bottleneck_table["Delay_Rate"].round(2)
    )

    bottleneck_table["Total_Sales"] = (
        bottleneck_table["Total_Sales"].round(2)
    )

    bottleneck_table["Total_Gross_Profit"] = (
        bottleneck_table["Total_Gross_Profit"].round(2)
    )

    st.dataframe(
        bottleneck_table,
        use_container_width=True,
        hide_index=True
    )

else:

    st.success(
        "No significant geographic bottlenecks detected "
        "under the current filters."
    )


# ------------------------------------------------------------
# State Performance Summary
# ------------------------------------------------------------

st.markdown("### 📋 State Performance Summary")

state_summary = state_analysis.copy()

state_summary["Average_Lead_Time"] = (
    state_summary["Average_Lead_Time"].round(2)
)

state_summary["Delay_Rate"] = (
    state_summary["Delay_Rate"].round(2)
)

state_summary["Total_Sales"] = (
    state_summary["Total_Sales"].round(2)
)

state_summary["Total_Gross_Profit"] = (
    state_summary["Total_Gross_Profit"].round(2)
)
st.caption("State-wise shipping performance summary")
st.dataframe(
    state_summary.sort_values(
        "Delay_Rate",
        ascending=False
    ),
    use_container_width=True,
    hide_index=True
)

# ============================================================
# SHIP MODE COMPARISON
# ============================================================

st.divider()

st.subheader("🚚 Ship Mode Performance")

# ------------------------------------------------------------
# Ship Mode Analysis
# ------------------------------------------------------------

ship_mode_analysis = (
    filtered_df.groupby("Ship Mode")
    .agg(
        Total_Shipments=("Shipping Lead Time", "count"),
        Average_Lead_Time=("Shipping Lead Time", "mean"),
        Lead_Time_Variability=("Shipping Lead Time", "std"),
        Delay_Rate=("Delayed", lambda x: (x == "Yes").mean() * 100),
        Total_Sales=("Sales", "sum"),
        Total_Gross_Profit=("Gross Profit", "sum")
    )
    .reset_index()
)

ship_mode_analysis["Average_Lead_Time"] = ship_mode_analysis["Average_Lead_Time"].fillna(0)
ship_mode_analysis["Lead_Time_Variability"] = ship_mode_analysis["Lead_Time_Variability"].fillna(0)
ship_mode_analysis["Delay_Rate"] = ship_mode_analysis["Delay_Rate"].fillna(0).clip(0, 100)

# ------------------------------------------------------------
# KPI Cards
# ------------------------------------------------------------

fastest_mode = ship_mode_analysis.loc[
    ship_mode_analysis["Average_Lead_Time"].idxmin()
]

lowest_delay_mode = ship_mode_analysis.loc[
    ship_mode_analysis["Delay_Rate"].idxmin()
]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Fastest Ship Mode",
        fastest_mode["Ship Mode"],
        f"{fastest_mode['Average_Lead_Time']:.1f} days"
    )

with col2:
    st.metric(
        "Lowest Delay Rate",
        lowest_delay_mode["Ship Mode"],
        f"{lowest_delay_mode['Delay_Rate']:.1f}%"
    )

with col3:
    st.metric(
        "Total Shipments",
        f"{ship_mode_analysis['Total_Shipments'].sum():,}"
    )

# ------------------------------------------------------------
# Lead Time vs Delay Rate
# ------------------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    fig_mode_lead = px.bar(
        ship_mode_analysis.sort_values(
            "Average_Lead_Time",
            ascending=True
        ),
        x="Average_Lead_Time",
        y="Ship Mode",
        orientation="h",
        title="Average Lead Time by Ship Mode",
        text="Average_Lead_Time",
        labels={
            "Average_Lead_Time": "Average Lead Time (Days)",
            "Ship Mode": "Shipping Method"
        }
    )

    fig_mode_lead.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside"
    )

    fig_mode_lead.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=70,
            t=60,
            b=20
        )
    )

    st.plotly_chart(
        fig_mode_lead,
        use_container_width=True,
        key="chart_fig_mode_lead"
    )


# ------------------------------------------------------------
# Delay Rate by Ship Mode
# ------------------------------------------------------------

with col2:

    fig_mode_delay = px.bar(
        ship_mode_analysis.sort_values(
            "Delay_Rate",
            ascending=True
        ),
        x="Delay_Rate",
        y="Ship Mode",
        orientation="h",
        title="Delay Rate by Ship Mode",
        text="Delay_Rate",
        labels={
            "Delay_Rate": "Delay Rate (%)",
            "Ship Mode": "Shipping Method"
        }
    )

    fig_mode_delay.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig_mode_delay.update_layout(
        height=430,
        margin=dict(
            l=20,
            r=70,
            t=60,
            b=20
        )
    )

    st.plotly_chart(
        fig_mode_delay,
        use_container_width=True,
        key="chart_fig_mode_delay"
    )


# ------------------------------------------------------------
# Shipment Volume by Ship Mode
# ------------------------------------------------------------

st.markdown("### 📦 Shipment Volume by Ship Mode")

fig_mode_volume = px.pie(
    ship_mode_analysis,
    names="Ship Mode",
    values="Total_Shipments",
    hole=0.45,
    title="Shipment Distribution by Shipping Method"
)

fig_mode_volume.update_traces(
    textposition="inside",
    textinfo="percent+label"
)

fig_mode_volume.update_layout(
    height=450,
    legend_orientation="h",
    legend_y=-0.15
)

st.plotly_chart(
    fig_mode_volume,
    use_container_width=True,
    key="chart_fig_mode_volume"
)


# ------------------------------------------------------------
# Ship Mode Trade-off Analysis
# ------------------------------------------------------------

st.markdown("### ⚖️ Lead Time vs Delay Trade-off")

fig_tradeoff = px.scatter(
    ship_mode_analysis,
    x="Average_Lead_Time",
    y="Delay_Rate",
    size="Total_Shipments",
    text="Ship Mode",
    hover_data=[
        "Total_Shipments",
        "Average_Lead_Time",
        "Delay_Rate",
        "Total_Sales",
        "Total_Gross_Profit"
    ],
    title="Shipping Speed vs Delay Risk",
    labels={
        "Average_Lead_Time": "Average Lead Time (Days)",
        "Delay_Rate": "Delay Rate (%)",
        "Total_Shipments": "Shipment Volume"
    }
)

fig_tradeoff.update_traces(
    textposition="top center",
    opacity=0.80
)

fig_tradeoff.update_layout(
    height=500
)

st.plotly_chart(
    fig_tradeoff,
    use_container_width=True,
    key="chart_fig_tradeoff"
)


# ------------------------------------------------------------
# Ship Mode Performance Table
# ------------------------------------------------------------

st.markdown("### 📋 Ship Mode Performance Summary")

ship_mode_table = ship_mode_analysis.copy()

ship_mode_table["Average_Lead_Time"] = (
    ship_mode_table["Average_Lead_Time"].round(2)
)

ship_mode_table["Lead_Time_Variability"] = (
    ship_mode_table["Lead_Time_Variability"]
    .fillna(0)
    .round(2)
)

ship_mode_table["Delay_Rate"] = (
    ship_mode_table["Delay_Rate"].round(2)
)

ship_mode_table["Total_Sales"] = (
    ship_mode_table["Total_Sales"].round(2)
)

ship_mode_table["Total_Gross_Profit"] = (
    ship_mode_table["Total_Gross_Profit"].round(2)
)
st.caption("Comparison of all shipping methods")
st.dataframe(
    ship_mode_table.sort_values(
        "Average_Lead_Time"
    ),
    use_container_width=True,
    hide_index=True
)

# ============================================================
# ROUTE DRILL-DOWN
# ============================================================

st.divider()

st.subheader("🔎 Route Drill-Down")

# Create route column for filtered data
filtered_df["Route"] = (
    filtered_df["Factory"] + " → " +
    filtered_df["State/Province"]
)

available_routes = sorted(
    filtered_df["Route"].dropna().unique()
)

# Pre-compute route ranking once, used by the drill-down below.
rank_table = (
    route_dashboard[["Route", "Route_Efficiency_Score"]]
    .sort_values("Route_Efficiency_Score", ascending=False)
    .reset_index(drop=True)
)
rank_table["Rank"] = rank_table.index + 1

if len(available_routes) > 0:

    selected_route = st.selectbox(
        "Select Route",
        available_routes
    )

    route_df = filtered_df[
        filtered_df["Route"] == selected_route
    ].copy()

    # ========================================================
    # ROUTE RANK & PERFORMANCE BADGE
    # ========================================================

    selected_rank = rank_table[
        rank_table["Route"] == selected_route
    ]

    if not selected_rank.empty:

        route_rank = int(selected_rank["Rank"].iloc[0])

        route_score = float(
            selected_rank["Route_Efficiency_Score"].iloc[0]
        )

        total_routes = len(rank_table)

        # Performance Badge
        if route_score >= 80:
            badge = "🟢 Excellent"
        elif route_score >= 65:
            badge = "🟡 Good"
        elif route_score >= 50:
            badge = "🟠 Average"
        else:
            badge = "🔴 Needs Improvement"

        c1, c2 = st.columns(2)

        with c1:
            st.metric(
                "🏆 Route Rank",
                f"#{route_rank} / {total_routes}"
            )

        with c2:
            st.metric(
                "⭐ Performance",
                badge
            )

    # ------------------------------------------------------------
    # ROUTE KPIs
    # ------------------------------------------------------------

    route_shipments = len(route_df)

    route_avg_lead = route_df["Shipping Lead Time"].mean()
    if pd.isna(route_avg_lead):
        route_avg_lead = 0

    route_delay_rate = (
        route_df["Delayed"].eq("Yes").mean() * 100
        if len(route_df) > 0 else 0
    )

    route_sales = route_df["Sales"].sum()

    route_profit = route_df["Gross Profit"].sum()

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Shipments",
            f"{route_shipments:,}"
        )

    with col2:
        st.metric(
            "Avg Lead Time",
            f"{route_avg_lead:.1f} days"
        )

    with col3:
        st.metric(
            "Delay Rate",
            f"{route_delay_rate:.1f}%"
        )

    with col4:
        st.metric(
            "Sales",
            f"${route_sales:,.2f}"
        )

    with col5:
        st.metric(
            "Gross Profit",
            f"${route_profit:,.2f}"
        )

    st.markdown("### 📋 Order-Level Shipment Details")

    # ------------------------------------------------------------
    # ORDER TABLE
    # ------------------------------------------------------------

    display_columns = [
        "Order ID",
        "Order Date",
        "Ship Date",
        "Ship Mode",
        "Customer ID",
        "City",
        "State/Province",
        "Shipping Lead Time",
        "Delayed",
        "Sales",
        "Units",
        "Gross Profit"
    ]

    available_columns = [
        col for col in display_columns
        if col in route_df.columns
    ]

    route_orders = route_df[
        available_columns
    ].sort_values(
        "Order Date"
    )

    st.dataframe(
        route_orders,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "No routes available for the selected filters."
    )

# ============================================================
# EXECUTIVE SUMMARY
# ============================================================

st.divider()

st.subheader("📌 Executive Summary")

# ------------------------------------------------------------
# OVERALL PERFORMANCE METRICS
# ------------------------------------------------------------

overall_avg_lead = (
    filtered_df["Shipping Lead Time"].mean()
    if len(filtered_df) > 0 else 0
)
if pd.isna(overall_avg_lead):
    overall_avg_lead = 0

overall_delay_rate = (
    filtered_df["Delayed"].eq("Yes").mean() * 100
    if len(filtered_df) > 0 else 0
)

overall_sales = filtered_df["Sales"].sum()
overall_profit = filtered_df["Gross Profit"].sum()

# ------------------------------------------------------------
# ROUTE PERFORMANCE
# ------------------------------------------------------------

if len(route_dashboard) > 0:

    best_route = route_dashboard.loc[
        route_dashboard["Route_Efficiency_Score"].idxmax()
    ]

    worst_route = route_dashboard.loc[
        route_dashboard["Route_Efficiency_Score"].idxmin()
    ]

    # --------------------------------------------------------
    # MANAGEMENT KPI CARDS
    # --------------------------------------------------------

    st.markdown("### 📊 Management Snapshot")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Avg Lead Time",
            f"{overall_avg_lead:.1f} days"
        )

    with col2:
        st.metric(
            "Overall Delay Rate",
            f"{overall_delay_rate:.1f}%"
        )

    with col3:
        st.metric(
            "Total Sales",
            f"${overall_sales:,.0f}"
        )

    with col4:
        st.metric(
            "Gross Profit",
            f"${overall_profit:,.0f}"
        )

    # --------------------------------------------------------
    # BEST & WORST ROUTES
    # --------------------------------------------------------

    st.markdown("### 🏆 Route Performance Highlights")

    col1, col2 = st.columns(2)

    with col1:
        st.success(
            f"""
            **🏆 Best Performing Route**

            **{best_route['Route']}**

            • Efficiency Score: **{best_route['Route_Efficiency_Score']:.1f}/100**  
            • Average Lead Time: **{best_route['Average_Lead_Time']:.1f} days**  
            • Delay Rate: **{best_route['Delay_Rate']:.1f}%**  
            • Shipments: **{best_route['Total_Shipments']:,}**
            """
        )

    with col2:
        st.error(
            f"""
            **⚠️ Highest-Risk Route**

            **{worst_route['Route']}**

            • Efficiency Score: **{worst_route['Route_Efficiency_Score']:.1f}/100**  
            • Average Lead Time: **{worst_route['Average_Lead_Time']:.1f} days**  
            • Delay Rate: **{worst_route['Delay_Rate']:.1f}%**  
            • Shipments: **{worst_route['Total_Shipments']:,}**
            """
        )

    # --------------------------------------------------------
    # OPERATIONAL PRIORITIES
    # --------------------------------------------------------

    st.markdown("### 🎯 Operational Priorities")

    # Highest delay state / highest volume state
    if len(state_analysis) > 0:
        highest_delay_state = state_analysis.loc[
            state_analysis["Delay_Rate"].idxmax()
        ]

        highest_volume_state = state_analysis.loc[
            state_analysis["Total_Shipments"].idxmax()
        ]
    else:
        highest_delay_state = None
        highest_volume_state = None

    # Highest-risk route
    highest_risk_route = route_dashboard.loc[
        (
            route_dashboard["Total_Shipments"]
            * route_dashboard["Delay_Rate"]
        ).idxmax()
    ]

    # Fastest / most reliable shipping mode
    if len(ship_mode_analysis) > 0:
        fastest_mode = ship_mode_analysis.loc[
            ship_mode_analysis["Average_Lead_Time"].idxmin()
        ]

        lowest_delay_mode = ship_mode_analysis.loc[
            ship_mode_analysis["Delay_Rate"].idxmin()
        ]
    else:
        fastest_mode = None
        lowest_delay_mode = None

    priority_col1, priority_col2 = st.columns(2)

    with priority_col1:

        st.markdown("#### 🚨 Immediate Attention")

        highest_delay_line = (
            f"{highest_delay_state['State/Province']} records the highest "
            f"delay rate at **{highest_delay_state['Delay_Rate']:.1f}%**."
            if highest_delay_state is not None
            else "No state-level delay data available."
        )

        highest_volume_line = (
            f"{highest_volume_state['State/Province']} has the highest "
            f"shipment volume with **{highest_volume_state['Total_Shipments']:,}** shipments."
            if highest_volume_state is not None
            else "No state-level volume data available."
        )

        st.markdown(
            f"""
            **1. Highest-Risk Route**  
            {highest_risk_route['Route']} has the highest operational
            exposure based on shipment volume and delay rate.

            **2. Highest Delay State**  
            {highest_delay_line}

            **3. Monitor High-Volume Markets**  
            {highest_volume_line}
            """
        )

    with priority_col2:

        st.markdown("#### 💡 Optimization Opportunities")

        fastest_mode_line = (
            f"**{fastest_mode['Ship Mode']}** has the lowest average lead time "
            f"at **{fastest_mode['Average_Lead_Time']:.1f} days**."
            if fastest_mode is not None
            else "No shipping mode data available."
        )

        lowest_delay_mode_line = (
            f"**{lowest_delay_mode['Ship Mode']}** has the lowest delay rate "
            f"at **{lowest_delay_mode['Delay_Rate']:.1f}%**."
            if lowest_delay_mode is not None
            else "No shipping mode data available."
        )

        st.markdown(
            f"""
            **1. Review Shipping Mode Strategy**  
            {fastest_mode_line}

            **2. Prioritize Reliable Shipping Modes**  
            {lowest_delay_mode_line}

            **3. Route-Level Optimization**  
            Focus operational improvements on high-volume routes where
            delay exposure can have the largest business impact.
            """
        )

    # --------------------------------------------------------
    # EXECUTIVE TAKEAWAYS
    # --------------------------------------------------------

    st.markdown("### 🧠 Executive Takeaways")

    st.markdown(
        f"""
        **Overall Performance:**  
        The current filtered dataset shows an average shipping lead time of
        **{overall_avg_lead:.1f} days** with an overall delay rate of
        **{overall_delay_rate:.1f}%**.

        **Route Efficiency:**  
        Route performance varies across factory-to-state combinations.
        The best-performing route achieves an efficiency score of
        **{best_route['Route_Efficiency_Score']:.1f}/100**, while the lowest
        performing route requires operational attention.

        **Operational Focus:**  
        Management should prioritize routes and geographic markets where
        **shipment volume and delay exposure are both high**, rather than
        focusing only on delay percentage.

        **Shipping Strategy:**  
        Shipping mode decisions should balance **lead time, reliability,
        shipment volume, and business impact** rather than optimizing for
        speed alone.
        """
    )

else:

    st.info(
        "No route-level performance data is available "
        "for the selected filters."
    )

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <center>
        <h4>🚚 Nassau Candy Shipping Analytics Dashboard</h4>
        <p>
        Built with ❤️ using Streamlit • Plotly • Pandas • Python
        </p>
        <p>
        Developed by <b>Shivansh Mathur</b>
        </p>
    </center>
    """,
    unsafe_allow_html=True
)