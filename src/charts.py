"""
Chart functions (Plotly). They take a table made by src/analysis.py
and return a figure. No Streamlit here.

Rules used in every chart (see docs/ARCHITECTURE.md):
- France is always blue, the comparison group always orange, the rest grey;
- the number of respondents (n) is always in the tooltip;
- groups with fewer than 30 respondents are drawn with open (empty) markers
  or lighter bars, and the caption says it;
- one axis only, starting at 0 for bars.
"""

import plotly.graph_objects as go

from src.config import COLOR_COMPARE, COLOR_CONTEXT, COLOR_FOCUS, COLOR_YEAR, FOCUS_COUNTRY

FONT_COLOR = "#52514e"
GRID_COLOR = "rgba(128, 128, 128, 0.2)"


def format_euros(value):
    """55000 -> '55k €', 66521 -> '66.5k €'"""
    thousands = round(value / 1000, 1)
    return f"{thousands:g}k €"


def ordinal(number):
    """1 -> '1st', 2 -> '2nd', 14 -> '14th'"""
    if 10 <= number % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    return f"{number}{suffix}"


def apply_style(fig, height=420):
    """Common look of all the charts: light grid, legend on top, clean tooltips."""
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=40, b=10),
        font=dict(color=FONT_COLOR),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title=None),
        hoverlabel=dict(bgcolor="white", font_color="#0b0b0b"),
        # Transparent background: works with the light and the dark theme of Streamlit
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(gridcolor=GRID_COLOR, zeroline=False)
    fig.update_yaxes(gridcolor=GRID_COLOR, zeroline=False)
    return fig


def bar_ranking(table, category, value="median", highlight=FOCUS_COUNTRY,
                reference=None, reference_label=None, value_label="Median salary"):
    """
    Horizontal bars sorted from the highest to the lowest value.
    The highlighted category (France) is blue, the others grey.
    reference: optional value drawn as an orange dashed line (for example the EU median).
    """
    table = table.sort_values(value)
    colors = [COLOR_FOCUS if name == highlight else COLOR_CONTEXT for name in table[category]]

    fig = go.Figure(go.Bar(
        x=table[value],
        y=table[category].astype(str),
        orientation="h",
        marker=dict(color=colors, cornerradius=4),
        customdata=table[["n", "q1", "q3"]],
        hovertemplate=(f"<b>%{{y}}</b><br>{value_label}: %{{x:,.0f}} €"
                       "<br>Middle 50%: %{customdata[1]:,.0f} – %{customdata[2]:,.0f} €"
                       "<br>n = %{customdata[0]:,}<extra></extra>"),
    ))
    if reference is not None:
        fig.add_vline(x=reference, line_dash="dash", line_color=COLOR_COMPARE, line_width=2,
                      annotation_text=reference_label, annotation_position="top",
                      annotation_font_color=COLOR_COMPARE)
    fig.update_xaxes(title=f"{value_label} (€ per year)", rangemode="tozero")
    fig.update_yaxes(title=None)
    return apply_style(fig, height=max(320, 26 * len(table) + 80))


def lines_compare(table, x, value="median", group_colors=None, value_label="Median salary"):
    """
    One line per group (for example France and the EU) along an ordered category
    (for example the experience level). table comes from analysis.compare_groups.
    Points with fewer than 30 respondents have an open marker.
    """
    if group_colors is None:
        group_colors = {}
    fig = go.Figure()
    for group, data in table.groupby("group", sort=False):
        color = group_colors.get(group, COLOR_CONTEXT)
        symbols = ["circle" if ok else "circle-open" for ok in data["reliable"]]
        fig.add_trace(go.Scatter(
            x=data[x].astype(str),
            y=data[value],
            name=group,
            mode="lines+markers",
            line=dict(color=color, width=2),
            marker=dict(size=9, symbol=symbols, color=color, line=dict(width=2, color=color)),
            customdata=data[["n"]],
            hovertemplate=(f"<b>{group}</b> · %{{x}}<br>{value_label}: %{{y:,.0f}} €"
                           "<br>n = %{customdata[0]:,}<extra></extra>"),
        ))
    fig.update_xaxes(title=None, type="category")
    fig.update_yaxes(title=f"{value_label} (€ per year)", rangemode="tozero")
    fig.update_layout(hovermode="x unified")
    return apply_style(fig)


def dumbbell_years(table, group_column, old_year, new_year, value_label="Median salary"):
    """
    One row per group, with a light dot for the old year and a dark dot for the new year.
    table comes from analysis.evolution (columns median_<year> and n_<year>).
    """
    fig = go.Figure()
    groups = table[group_column].astype(str)

    # Grey segment between the two years
    for _, row in table.iterrows():
        fig.add_trace(go.Scatter(
            x=[row[f"median_{old_year}"], row[f"median_{new_year}"]],
            y=[str(row[group_column])] * 2,
            mode="lines", line=dict(color=COLOR_CONTEXT, width=2),
            showlegend=False, hoverinfo="skip",
        ))
    for year in [old_year, new_year]:
        is_new = year == new_year
        fig.add_trace(go.Scatter(
            x=table[f"median_{year}"], y=groups, name=str(year),
            # The new year also shows the change in %, so it is readable even when
            # the two dots are at the same place
            mode="markers+text" if is_new else "markers",
            text=[f"  {change:+.1f}%" for change in table["change_percent"]] if is_new else None,
            textposition="middle right",
            marker=dict(size=12, color=COLOR_YEAR[year], line=dict(width=2, color="white")),
            customdata=table[[f"n_{year}", "change_percent"]],
            hovertemplate=(f"<b>%{{y}}</b> · {year}<br>{value_label}: %{{x:,.0f}} €"
                           "<br>n = %{customdata[0]:,}<extra></extra>"),
        ))
    # Some space on the right for the % labels
    low = table[[f"median_{old_year}", f"median_{new_year}"]].min().min()
    high = table[[f"median_{old_year}", f"median_{new_year}"]].max().max()
    margin = (high - low) * 0.15 + 1000
    fig.update_xaxes(title=f"{value_label} (€ per year)", range=[low - margin, high + 2 * margin])
    fig.update_yaxes(title=None)
    return apply_style(fig, height=max(260, 60 * len(table) + 100))


def choropleth(table, value="median", value_label="Median salary"):
    """
    World map, one color per country (one blue, light = low, dark = high).
    table needs the columns ISO3, Country, n and the value.
    Countries without data are grey (not blue), so they are not read as "low".
    """
    fig = go.Figure(go.Choropleth(
        locations=table["ISO3"],
        z=table[value],
        text=table["Country"],
        customdata=table[["n"]],
        colorscale=[[0, "#cde2fb"], [0.5, "#3987e5"], [1, "#0d366b"]],
        marker_line_color="white",
        marker_line_width=0.5,
        colorbar=dict(title="€"),
        hovertemplate=(f"<b>%{{text}}</b><br>{value_label}: %{{z:,.0f}} €"
                       "<br>n = %{customdata[0]:,}<extra></extra>"),
    ))
    fig.update_geos(showframe=False, showcoastlines=False, projection_type="natural earth",
                    projection_rotation=dict(lon=10), showland=True, landcolor="#e4e3df",
                    lataxis_range=[-58, 85], bgcolor="rgba(0,0,0,0)")
    return apply_style(fig, height=450)
