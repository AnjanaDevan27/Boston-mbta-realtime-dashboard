import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from sqlalchemy import create_engine
import os
import json
import polyline as pl

load_dotenv()

# Use Streamlit secrets in production, .env locally
try:
    if hasattr(st, "secrets") and "DB_HOST" in st.secrets:
        os.environ["DB_HOST"] = st.secrets["DB_HOST"]
        os.environ["DB_PORT"] = str(st.secrets["DB_PORT"])
        os.environ["DB_NAME"] = st.secrets["DB_NAME"]
        os.environ["DB_USER"] = st.secrets["DB_USER"]
        os.environ["DB_PASSWORD"] = st.secrets["DB_PASSWORD"]
except Exception:
    pass

# Load config files
with open("config/stop_names.json") as f:
    stop_data = json.load(f)

with open("config/route_shapes.json") as f:
    route_shapes = json.load(f)

with open("config/stop_coords.json") as f:
    stop_coords = json.load(f)

ALL_STOP_NAMES = stop_data["all_stops"]
ROUTE_STOP_NAMES = stop_data["route_stops"]


def get_stop_name(stop_id):
    if stop_id is None:
        return None
    return ALL_STOP_NAMES.get(str(stop_id), str(stop_id))


def decode_shape(encoded):
    return pl.decode(encoded)


st.set_page_config(
    page_title="Boston MBTA Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Auto-refresh every 2 minutes
st.markdown('<meta http-equiv="refresh" content="120">', unsafe_allow_html=True)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif !important; }
    .stApp { background-color: #0F1923; color: #FFFFFF; }
    button[data-testid="collapsedControl"] { display: none; }
    div[data-testid="metric-container"] {
        background-color: #1A2940;
        border: 1px solid #2A4060;
        border-top: 2px solid #C8A951;
        border-radius: 6px;
        padding: 16px 20px;
    }
    div[data-testid="metric-container"] label {
        color: #7A9BBF !important;
        font-size: 10px !important;
        font-weight: 600 !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
    }
    div[data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 1.6rem !important; font-weight: 700 !important; }
    div[data-testid="stMetricDelta"] { color: #C8A951 !important; font-size: 0.72rem !important; }
    h1 { color: #FFFFFF !important; font-size: 1.3rem !important; font-weight: 700 !important; letter-spacing: -0.01em !important; margin: 0 !important; }
    h2, h3 { color: #7A9BBF !important; font-size: 0.65rem !important; font-weight: 600 !important; letter-spacing: 0.14em !important; text-transform: uppercase !important; margin-bottom: 10px !important; }
    p { color: #7A9BBF !important; font-size: 0.8rem !important; }
    hr { border-color: #2A4060 !important; margin: 16px 0 !important; }
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; max-width: 100% !important; }
    span[data-baseweb="tag"] { background-color: #C8A951 !important; color: #0F1923 !important; font-weight: 600 !important; font-size: 11px !important; }
    div[data-baseweb="select"] { background-color: #1A2940 !important; border-color: #2A4060 !important; }
    div[data-baseweb="select"] * { color: #FFFFFF !important; }
    div[data-testid="stRadio"] label { color: #FFFFFF !important; font-size: 0.8rem !important; }
    div[data-testid="stSelectbox"] label { color: #7A9BBF !important; font-size: 0.7rem !important; font-weight: 600 !important; letter-spacing: 0.1em !important; text-transform: uppercase !important; }
    div[data-testid="stSlider"] label { color: #7A9BBF !important; font-size: 0.7rem !important; font-weight: 600 !important; letter-spacing: 0.1em !important; text-transform: uppercase !important; }
    div[data-testid="stSlider"] p { color: #FFFFFF !important; }
    div[data-testid="stMultiSelect"] label { color: #7A9BBF !important; font-size: 0.7rem !important; font-weight: 600 !important; letter-spacing: 0.1em !important; text-transform: uppercase !important; }
    .stButton button { background-color: transparent !important; color: #C8A951 !important; border: 1px solid #C8A951 !important; border-radius: 4px !important; font-size: 0.75rem !important; font-weight: 600 !important; padding: 4px 12px !important; }
    .stButton button:hover { background-color: #C8A951 !important; color: #0F1923 !important; }
    .stDataFrame { border: 1px solid #2A4060 !important; border-radius: 6px !important; }
    @media (max-width: 768px) {
        h1 { font-size: 1rem !important; }
        h2, h3 { font-size: 0.6rem !important; }
        div[data-testid="stMetricValue"] { font-size: 1.2rem !important; }
        div[data-testid="metric-container"] { padding: 10px 12px !important; }
        .block-container { padding: 0.5rem !important; }
        div[data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
        div[data-testid="stHorizontalBlock"] > div { min-width: 100% !important; flex: 1 1 100% !important; }
        span[data-baseweb="tag"] { font-size: 10px !important; }
    }
    @media (max-width: 1024px) {
        h1 { font-size: 1.1rem !important; }
        div[data-testid="stMetricValue"] { font-size: 1.4rem !important; }
    }
</style>
""", unsafe_allow_html=True)

CHART_LAYOUT = dict(
    paper_bgcolor="#1A2940",
    plot_bgcolor="#1A2940",
    font=dict(family="Inter", color="#7A9BBF", size=10),
    margin=dict(l=12, r=12, t=12, b=12),
    legend=dict(bgcolor="#0F1923", bordercolor="#2A4060", borderwidth=1, font=dict(size=9, color="#FFFFFF")),
    xaxis=dict(gridcolor="#2A4060", linecolor="#2A4060", tickfont=dict(size=9, color="#7A9BBF")),
    yaxis=dict(gridcolor="#2A4060", linecolor="#2A4060", tickfont=dict(size=9, color="#7A9BBF")),
)

ROUTE_COLORS = {
    "Red": "#E8362A", "Orange": "#F5920A", "Blue": "#2A5FC4",
    "Green-B": "#12A050", "Green-C": "#12A050", "Green-D": "#12A050", "Green-E": "#12A050",
}

ALL_ROUTES = ["Red", "Orange", "Blue", "Green-B", "Green-C", "Green-D", "Green-E"]

HOUR_LABELS = {
    0: "12 AM", 1: "1 AM", 2: "2 AM", 3: "3 AM", 4: "4 AM",
    5: "5 AM", 6: "6 AM", 7: "7 AM", 8: "8 AM", 9: "9 AM",
    10: "10 AM", 11: "11 AM", 12: "12 PM", 13: "1 PM", 14: "2 PM",
    15: "3 PM", 16: "4 PM", 17: "5 PM", 18: "6 PM", 19: "7 PM",
    20: "8 PM", 21: "9 PM", 22: "10 PM", 23: "11 PM"
}


@st.cache_resource
def get_engine():
    db_url = (
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'postgres')}"
    )
    return create_engine(db_url)


@st.cache_data(ttl=120)
def load_predictions():
    return pd.read_sql("""
        SELECT route, stop_id, direction_id, arrival_time,
               departure_time, status, schedule_relationship, fetched_at
        FROM predictions
        WHERE fetched_at >= NOW() - INTERVAL '24 hours'
        ORDER BY fetched_at DESC
        LIMIT 50000
    """, get_engine())


@st.cache_data(ttl=120)
def load_vehicles():
    return pd.read_sql("""
        SELECT vehicle_id, route, latitude, longitude,
               bearing, speed, current_status, fetched_at
        FROM vehicles
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        ORDER BY fetched_at DESC LIMIT 1000
    """, get_engine())


@st.cache_data(ttl=120)
def load_alerts():
    return pd.read_sql("""
        SELECT alert_id, header, severity, effect, cause, fetched_at
        FROM alerts ORDER BY fetched_at DESC LIMIT 100
    """, get_engine())


# Load data
predictions = load_predictions()
vehicles = load_vehicles()
alerts = load_alerts()

# Parse timestamps
predictions["fetched_at"] = pd.to_datetime(predictions["fetched_at"], utc=True)
predictions["arrival_time"] = pd.to_datetime(predictions["arrival_time"], utc=True, errors="coerce")
predictions["departure_time"] = pd.to_datetime(predictions["departure_time"], utc=True, errors="coerce")
predictions["hour"] = predictions["arrival_time"].dt.hour
predictions["fetched_hour"] = predictions["fetched_at"].dt.hour
predictions["delay_seconds"] = (predictions["departure_time"] - predictions["arrival_time"]).dt.total_seconds()

# ── TOP FILTER BAR ──────────────────────────────────────────────────────────
h_col, f1, f2, f3, f4, f5 = st.columns([2, 3, 2, 2, 2, 1])

with h_col:
    st.title("Boston MBTA Dashboard")

with f1:
    selected_routes = st.multiselect("Routes", options=ALL_ROUTES, default=ALL_ROUTES)

with f2:
    direction = st.radio(
        "Direction",
        options=["Both", "Inbound (toward downtown)", "Outbound (away from downtown)"],
        index=0,
    )

with f3:
    if selected_routes:
        route_stop_options = {}
        for route in selected_routes:
            route_stop_options.update(ROUTE_STOP_NAMES.get(route, {}))
        stop_options = {"All stops": None}
        stop_options.update({v: k for k, v in sorted(route_stop_options.items(), key=lambda x: x[1])})
    else:
        stop_options = {"All stops": None}

    stop_search = st.selectbox("Stop", options=list(stop_options.keys()), index=0)
    selected_stop_id = stop_options.get(stop_search)

with f4:
    time_range = st.slider("Time of Day", 0, 23, (0, 23))
    st.caption(f"{HOUR_LABELS[time_range[0]]} — {HOUR_LABELS[time_range[1]]}")

with f5:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Refresh"):
        st.cache_data.clear()
        st.rerun()

st.divider()

# Last updated
last_updated = predictions["fetched_at"].max()
st.caption(f"Last updated: {last_updated.strftime('%I:%M %p')} UTC")

# ── APPLY FILTERS ───────────────────────────────────────────────────────────
filtered = predictions.copy()
if selected_routes:
    filtered = filtered[filtered["route"].isin(selected_routes)]
if direction == "Inbound (toward downtown)":
    filtered = filtered[filtered["direction_id"] == 1]
elif direction == "Outbound (away from downtown)":
    filtered = filtered[filtered["direction_id"] == 0]
if selected_stop_id:
    filtered = filtered[filtered["stop_id"] == selected_stop_id]
filtered = filtered[
    (filtered["hour"].isna()) |
    ((filtered["hour"] >= time_range[0]) & (filtered["hour"] <= time_range[1]))
]
vehicles_filtered = vehicles[vehicles["route"].isin(selected_routes)] if selected_routes else vehicles

# ── KPI ROW ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Predictions", f"{len(filtered):,}")
with k2:
    st.metric("Active Vehicles", f"{len(vehicles_filtered):,}")
with k3:
    st.metric("Active Alerts", f"{len(alerts):,}")
with k4:
    on_time_pct = (filtered["schedule_relationship"].isna().sum() / len(filtered) * 100) if len(filtered) > 0 else 0
    cancelled_pct = ((filtered["schedule_relationship"] == "CANCELLED").sum() / len(filtered) * 100) if len(filtered) > 0 else 0
    st.metric("On-Time Rate", f"{on_time_pct:.1f}%", delta=f"-{cancelled_pct:.1f}% cancelled")

st.divider()

# ── ROW 1: MAP + BAR + DONUT ────────────────────────────────────────────────
c1, c2, c3 = st.columns([2, 2, 1])

with c1:
    st.subheader("Live Vehicle Positions")
    map_data = vehicles_filtered.dropna(subset=["latitude", "longitude"])
    map_zoom = 14 if (selected_stop_id and stop_search != "All stops") else 11
    map_center = {"lat": 42.3601, "lon": -71.0589}

    fig = px.scatter_mapbox(
        map_data if len(map_data) > 0 else pd.DataFrame(columns=["latitude", "longitude", "route", "vehicle_id"]),
        lat="latitude", lon="longitude",
        color="route", hover_name="vehicle_id",
        hover_data={"current_status": True, "speed": True, "latitude": False, "longitude": False, "route": False},
        color_discrete_map=ROUTE_COLORS,
        zoom=map_zoom, center=map_center,
        mapbox_style="carto-positron", height=400
    )
    fig.update_traces(
        marker=dict(size=12, opacity=1.0),
        hovertemplate="<b>%{hovertext}</b><br>Status: %{customdata[0]}<extra></extra>"
    )

    # Route lines
    for route in (selected_routes if selected_routes else ALL_ROUTES):
        if route not in route_shapes:
            continue
        coords = decode_shape(route_shapes[route])
        lats = [c[0] for c in coords]
        lons = [c[1] for c in coords]
        fig.add_trace({
            "type": "scattermapbox",
            "lat": lats, "lon": lons,
            "mode": "lines",
            "line": {"width": 3, "color": ROUTE_COLORS.get(route, "#FFFFFF")},
            "name": f"{route} Line",
            "hoverinfo": "skip",
            "showlegend": False,
        })

    # Stop markers
    shown_stops = set()
    for route in (selected_routes if selected_routes else ALL_ROUTES):
        for stop_id in ROUTE_STOP_NAMES.get(route, {}).keys():
            if stop_id in shown_stops or stop_id not in stop_coords:
                continue
            shown_stops.add(stop_id)
            s = stop_coords[stop_id]
            fig.add_trace({
                "type": "scattermapbox",
                "lat": [s["lat"]], "lon": [s["lon"]],
                "mode": "markers",
                "marker": {"size": 7, "color": "#FFFFFF", "opacity": 0.9},
                "name": s["name"],
                "hovertext": s["name"],
                "hoverinfo": "text",
                "showlegend": False,
            })

    # Deduplicate Green Line in legend
    seen_legends = set()
    for trace in fig.data:
        if hasattr(trace, "name") and trace.name and str(trace.name).startswith("Green"):
            if "Green" in seen_legends:
                trace.showlegend = False
            else:
                seen_legends.add("Green")
                trace.name = "Green"

    fig.update_layout(
        paper_bgcolor="#1A2940",
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(
            bgcolor="#0F1923", bordercolor="#2A4060", borderwidth=1,
            font=dict(size=9, color="#FFFFFF"),
            x=0.01, y=0.99, xanchor="left", yanchor="top"
        ),
        mapbox=dict(style="carto-positron")
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Predictions by Route")
    route_counts = filtered.groupby("route").size().reset_index(name="count").sort_values("count", ascending=True)
    fig = px.bar(
        route_counts, x="count", y="route", orientation="h",
        color="route", labels={"count": "Predictions", "route": ""},
        color_discrete_map=ROUTE_COLORS
    )
    fig.update_layout(showlegend=False, height=400, **CHART_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

with c3:
    st.subheader("Schedule Relationship")
    if len(filtered) > 0:
        sched = filtered["schedule_relationship"].fillna("ON SCHEDULE").value_counts().reset_index()
        sched.columns = ["Relationship", "Count"]
        fig = px.pie(
            sched, values="Count", names="Relationship", hole=0.55,
            color_discrete_sequence=["#C8A951", "#2A5FC4", "#E8362A", "#12A050"]
        )
        fig.update_layout(height=400, **CHART_LAYOUT)
        fig.update_layout(legend=dict(
            orientation="v",
            bgcolor="#0F1923",
            bordercolor="#2A4060",
            borderwidth=1,
            font=dict(size=9, color="#FFFFFF"),
        ))
        fig.update_traces(textfont=dict(size=9), textinfo="percent", pull=[0.05] * 10)
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── STOP DRILL DOWN ──────────────────────────────────────────────────────────
if selected_stop_id and stop_search != "All stops":
    st.subheader(f"Next Arrivals — {stop_search}")
    stop_preds = predictions[predictions["stop_id"] == selected_stop_id].copy()
    stop_preds = stop_preds.dropna(subset=["arrival_time"])
    stop_preds = stop_preds[stop_preds["arrival_time"] > pd.Timestamp.now(tz="UTC")]
    stop_preds = stop_preds.sort_values("arrival_time").head(5)
    if len(stop_preds) > 0:
        display = stop_preds[["route", "direction_id", "arrival_time", "schedule_relationship"]].copy()
        display["direction"] = display["direction_id"].map({0: "Outbound", 1: "Inbound"})
        display["arrival"] = display["arrival_time"].dt.strftime("%I:%M %p")
        display["status"] = display["schedule_relationship"].fillna("On Schedule")
        display = display[["route", "direction", "arrival", "status"]]
        display.columns = ["Route", "Direction", "Arrival", "Status"]
        st.dataframe(display, use_container_width=True, hide_index=True)
    else:
        st.info("No upcoming arrivals found for this stop")
    st.divider()

# ── ROW 2: ANALYTICS ────────────────────────────────────────────────────────
a1, a2, a3 = st.columns(3)

with a1:
    st.subheader("Peak Hour Activity")
    hour_data = filtered.dropna(subset=["hour"])
    if len(hour_data) > 0:
        hour_counts = hour_data.groupby("hour").size().reset_index(name="count")
        hour_counts["hour_label"] = hour_counts["hour"].map(HOUR_LABELS)
        fig = px.bar(
            hour_counts, x="hour_label", y="count",
            color="count", color_continuous_scale=["#1A2940", "#C8A951"],
            labels={"hour_label": "Time", "count": "Predictions"}
        )
        fig.update_layout(showlegend=False, coloraxis_showscale=False, height=260, **CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No arrival time data available")

with a2:
    st.subheader("Delay Distribution by Route")
    delay_data = filtered.dropna(subset=["delay_seconds"])
    delay_data = delay_data[delay_data["delay_seconds"].between(-300, 1800)]
    if len(delay_data) > 0:
        fig = px.box(
            delay_data, x="route", y="delay_seconds", color="route",
            color_discrete_map=ROUTE_COLORS,
            labels={"delay_seconds": "Seconds", "route": ""}
        )
        fig.update_layout(showlegend=False, height=260, **CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No delay data available")

with a3:
    st.subheader("Predictions Over Time")
    if len(filtered) > 0:
        ts = filtered.groupby(filtered["fetched_at"].dt.floor("10min")).size().reset_index(name="count")
        ts.columns = ["time", "count"]
        fig = px.area(
            ts, x="time", y="count",
            color_discrete_sequence=["#C8A951"],
            labels={"time": "", "count": "Predictions"}
        )
        fig.update_traces(line=dict(width=2), fillcolor="rgba(200,169,81,0.15)")
        fig.update_layout(height=260, **CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── ON-TIME + DIRECTION SPLIT ────────────────────────────────────────────────
r1, r2 = st.columns(2)

with r1:
    st.subheader("On-Time Rate by Route")
    if len(filtered) > 0:
        ontime_by_route = filtered.groupby("route").apply(
            lambda x: round(x["schedule_relationship"].isna().sum() / len(x) * 100, 1)
        ).reset_index(name="on_time_pct")
        ontime_by_route = ontime_by_route.sort_values("on_time_pct", ascending=True)
        fig = px.bar(
            ontime_by_route, x="on_time_pct", y="route",
            orientation="h", color="route",
            color_discrete_map=ROUTE_COLORS,
            labels={"on_time_pct": "On-Time %", "route": ""},
            range_x=[0, 100]
        )
        fig.update_layout(showlegend=False, height=260, **CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

with r2:
    st.subheader("Direction Split by Route")
    if len(filtered) > 0:
        dir_split = filtered.groupby(["route", "direction_id"]).size().reset_index(name="count")
        dir_split["direction"] = dir_split["direction_id"].map({0: "Outbound", 1: "Inbound"})
        fig = px.bar(
            dir_split, x="count", y="route", color="direction",
            orientation="h",
            color_discrete_map={"Inbound": "#C8A951", "Outbound": "#2A5FC4"},
            labels={"count": "Predictions", "route": ""},
            barmode="stack"
        )
        fig.update_layout(height=260, **CHART_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── BUSIEST STOPS ────────────────────────────────────────────────────────────
st.subheader("Busiest Stops")
if len(filtered) > 0:
    stop_counts = filtered.groupby("stop_id").size().reset_index(name="predictions")
    stop_counts["stop_name"] = stop_counts["stop_id"].apply(get_stop_name)
    stop_counts = stop_counts.sort_values("predictions", ascending=False).head(15)
    stop_counts = stop_counts.sort_values("predictions", ascending=True)
    fig = px.bar(
        stop_counts, x="predictions", y="stop_name",
        orientation="h",
        color="predictions",
        color_continuous_scale=["#1A2940", "#C8A951"],
        labels={"predictions": "Predictions", "stop_name": ""}
    )
    fig.update_layout(showlegend=False, coloraxis_showscale=False, height=420, **CHART_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── ALERTS ───────────────────────────────────────────────────────────────────
st.subheader("Active Service Alerts")
if len(alerts) > 0:
    ad = alerts[["header", "effect", "cause", "severity"]].copy()
    ad.columns = ["Alert", "Effect", "Cause", "Severity"]
    ad = ad.drop_duplicates(subset=["Alert"]).sort_values("Severity", ascending=False)
    st.dataframe(ad, use_container_width=True, hide_index=True, height=220)
else:
    st.success("No active alerts")