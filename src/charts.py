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
                reference=None, reference_label=None, value_label="Median salary",
                highlight_above_reference=False, reference_color=COLOR_COMPARE):
    """
    Horizontal bars sorted from the highest to the lowest value.
    The highlighted category (France) is blue, the others grey.
    reference: optional value drawn as a dashed line (for example the EU median).
    highlight_above_reference: if True, the bars above the reference are blue
    (for example the technologies paid more than the median).
    """
    table = table.sort_values(value)
    if highlight_above_reference and reference is not None:
        colors = [COLOR_FOCUS if v > reference else COLOR_CONTEXT for v in table[value]]
    else:
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
        fig.add_vline(x=reference, line_dash="dash", line_color=reference_color, line_width=2,
                      annotation_text=reference_label, annotation_position="top",
                      annotation_font_color=reference_color)
    fig.update_xaxes(title=f"{value_label} (€ per year)", rangemode="tozero")
    fig.update_yaxes(title=None)
    return apply_style(fig, height=max(320, 26 * len(table) + 80))


def bars_compare(table, category, value, group_colors, value_label, unit="€", order=None):
    """
    Horizontal bars side by side: one bar per group (for example France and the EU)
    for each category. table comes from analysis.compare_groups (or has the
    columns group, category, value and n).
    unit: "€" for salaries, "%" for shares.
    order: list of the categories from top to bottom (default: by value of the first group).
    Bars of groups with fewer than 30 respondents are lighter.
    """
    number = "%{x:,.0f} €" if unit == "€" else "%{x:.1f}%"
    if order is None:
        first_group = table[table["group"] == table["group"].iloc[0]]
        order = list(first_group.sort_values(value, ascending=False)[category].astype(str))

    fig = go.Figure()
    for group, data in table.groupby("group", sort=False):
        reliable = data["reliable"] if "reliable" in data else [True] * len(data)
        fig.add_trace(go.Bar(
            x=data[value],
            y=data[category].astype(str),
            name=group,
            orientation="h",
            marker=dict(color=group_colors.get(group, COLOR_CONTEXT), cornerradius=4,
                        opacity=[1 if ok else 0.4 for ok in reliable]),
            customdata=data[["n"]],
            hovertemplate=(f"<b>{group}</b> · %{{y}}<br>{value_label}: {number}"
                           "<br>n = %{customdata[0]:,}<extra></extra>"),
        ))
    unit_text = "€ per year" if unit == "€" else "% of respondents"
    fig.update_layout(barmode="group", bargap=0.25, bargroupgap=0.05)
    fig.update_xaxes(title=f"{value_label} ({unit_text})", rangemode="tozero")
    # Plotly draws the first category at the bottom: reverse to have it on top
    fig.update_yaxes(title=None, categoryorder="array", categoryarray=list(reversed(order)))
    return apply_style(fig, height=max(320, 22 * len(order) * len(group_colors) + 100))


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


def dumbbell_years(table, group_column, old_year, new_year, value_label="Median salary",
                   prefix="median", unit="€", change_column="change_percent", change_unit="%"):
    """
    One row per group, with a light dot for the old year and a dark dot for the new year.
    table comes from analysis.evolution (columns <prefix>_<year>, n_<year> and the change).
    For shares of respondents: prefix="percent", unit="%", change_unit=" pts".
    """
    fig = go.Figure()
    groups = table[group_column].astype(str)
    number = "%{x:,.0f} €" if unit == "€" else "%{x:.1f}%"
    old_column, new_column = f"{prefix}_{old_year}", f"{prefix}_{new_year}"

    # Grey segment between the two years
    for _, row in table.iterrows():
        fig.add_trace(go.Scatter(
            x=[row[old_column], row[new_column]],
            y=[str(row[group_column])] * 2,
            mode="lines", line=dict(color=COLOR_CONTEXT, width=2),
            showlegend=False, hoverinfo="skip",
        ))
    for year in [old_year, new_year]:
        is_new = year == new_year
        fig.add_trace(go.Scatter(
            x=table[f"{prefix}_{year}"], y=groups, name=str(year),
            # The new year also shows the change, so it is readable even when
            # the two dots are at the same place
            mode="markers+text" if is_new else "markers",
            text=[f"  {change:+.1f}{change_unit}" for change in table[change_column]] if is_new else None,
            textposition="middle right",
            marker=dict(size=12, color=COLOR_YEAR[year], line=dict(width=2, color="white")),
            customdata=table[[f"n_{year}"]],
            hovertemplate=(f"<b>%{{y}}</b> · {year}<br>{value_label}: {number}"
                           "<br>n = %{customdata[0]:,}<extra></extra>"),
        ))
    # Some space on the right for the labels of the change
    low = table[[old_column, new_column]].min().min()
    high = table[[old_column, new_column]].max().max()
    margin = (high - low) * 0.15 + (1000 if unit == "€" else 1)
    unit_text = "€ per year" if unit == "€" else "% of respondents"
    fig.update_xaxes(title=f"{value_label} ({unit_text})", range=[low - margin, high + 2 * margin])
    fig.update_yaxes(title=None)
    return apply_style(fig, height=max(260, 40 * len(table) + 120))


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
