from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from tabs.chart_helpers import show_no_data_message, style_figure
from tabs.styles import inject_chart_card_styles, inject_shared_tab_styles


SHARED_CHART_COLORS = [
    "#74B892",
    "#DE5156",
    "#F2CB67",
    "#5EACD8",
    "#A48BC7",
    "#6553D9",
    "#F46B3A",
    "#F25A2B",
    "#B7E2F6",
    "#7AAFD4",
]
OTHER_COLOR = "#8A97A5"
CHART_WRAPPER_CLASS = "product-category-chart"


def _format_percent(value: float) -> str:
    return f"{value * 100:,.1f}%"


def _build_display_data(df: pd.DataFrame, selected_categories: list[str], top_n: int = 10) -> tuple[pd.DataFrame, float]:
    # Giữ lại các danh mục đang được chọn, phần còn lại gộp vào "Khác" để tỷ trọng luôn đúng trên toàn bộ dữ liệu.
    work_df = df.copy()
    work_df["category"] = work_df["category"].fillna("Chưa phân loại")

    grouped = (
        work_df.groupby("category", as_index=False)["historical_sold"]
        .sum()
        .sort_values("historical_sold", ascending=False)
        .reset_index(drop=True)
    )

    total = float(grouped["historical_sold"].sum())
    if total <= 0:
        return pd.DataFrame(columns=["category", "historical_sold", "share", "share_label"]), 0.0

    if not selected_categories:
        return pd.DataFrame(columns=["category", "historical_sold", "share", "share_label"]), total

    selected_set = set(selected_categories)
    selected_grouped = grouped[grouped["category"].isin(selected_set)].copy()
    selected_grouped = selected_grouped.head(top_n).reset_index(drop=True)

    shown_total = float(selected_grouped["historical_sold"].sum())
    other_total = max(0.0, total - shown_total)

    selected_grouped["share"] = selected_grouped["historical_sold"] / total
    selected_grouped["share_label"] = selected_grouped["share"].apply(_format_percent)

    if other_total > 0:
        other_row = pd.DataFrame(
            [{
                "category": "Khác",
                "historical_sold": other_total,
                "share": other_total / total,
                "share_label": _format_percent(other_total / total),
            }]
        )
        selected_grouped = pd.concat([selected_grouped, other_row], ignore_index=True)

    return selected_grouped, total


def render_tab(df: pd.DataFrame, filters: dict) -> None:
    # Tab 1 tập trung trả lời câu hỏi: danh mục nào đang chiếm tỷ trọng mua lớn nhất.
    inject_shared_tab_styles()
    inject_chart_card_styles(CHART_WRAPPER_CLASS)

    if df.empty:
        show_no_data_message("Doanh mục sản phẩm")
        return

    selected_categories = filters.get("category", [])
    chart_data, total = _build_display_data(df, selected_categories)

    if chart_data.empty or total <= 0:
        st.warning("Không có dữ liệu để vẽ biểu đồ.")
        return

    base_categories = [category for category in chart_data["category"].tolist() if category != "Khác"]
    base_color_map = {
        category: SHARED_CHART_COLORS[index % len(SHARED_CHART_COLORS)]
        for index, category in enumerate(base_categories)
    }
    color_map = {**base_color_map, "_other_": OTHER_COLOR}

    pie_data = chart_data.copy()
    pie_data["color_key"] = pie_data["category"].where(pie_data["category"] != "Khác", "_other_")

    bar_data = chart_data.copy()
    bar_data["color_key"] = bar_data["category"].where(bar_data["category"] != "Khác", "_other_")

    pie_fig = px.pie(
        pie_data,
        names="category",
        values="share",
        color="color_key",
        color_discrete_map=color_map,
        hole=0.38,
    )
    pie_fig.update_traces(
        text=pie_data["share_label"],
        textinfo="text",
        textposition="inside",
        customdata=pie_data[["share_label"]],
        hovertemplate="%{label}: %{customdata[0]} tổng lượt mua<extra></extra>",
        marker=dict(line=dict(color="rgba(255,255,255,0)", width=0)),
    )
    pie_fig.update_layout(
        title=dict(text="Tỷ trọng lượt mua theo danh mục", x=0.5, xanchor="center"),
        showlegend=True,
        legend=dict(
            orientation="v",
            y=0.5,
            yanchor="middle",
            x=1.02,
            xanchor="left",
            font=dict(size=10),
        ),
        margin=dict(t=28, l=4, r=4, b=4),
    )
    style_figure(pie_fig, height=370)
    pie_fig.update_layout(title_font=dict(size=15))

    bar_fig = px.bar(
        bar_data,
        x="category",
        y="share",
        color="color_key",
        color_discrete_map=color_map,
        text=bar_data["share_label"],
    )
    bar_fig.update_layout(
        title=dict(text="Tỷ trọng lượt mua theo cột", x=0.5, xanchor="center"),
        yaxis=dict(tickformat=".0%", title="Tỷ lệ"),
        xaxis=dict(title=None, tickangle=-28),
        showlegend=False,
        margin=dict(t=28, l=34, r=4, b=38),
    )
    bar_fig.update_traces(
        showlegend=False,
        textposition="outside",
        cliponaxis=False,
        hovertemplate="%{x}: %{y:.1%} tổng lượt mua<extra></extra>",
        marker=dict(line=dict(color="rgba(255,255,255,0)", width=0)),
    )
    style_figure(bar_fig, height=370)
    bar_fig.update_layout(title_font=dict(size=15))

    col_left, col_right = st.columns(2, gap="small")

    with col_left:
        st.markdown(f"<div class='{CHART_WRAPPER_CLASS}'>", unsafe_allow_html=True)
        st.plotly_chart(pie_fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown(f"<div class='{CHART_WRAPPER_CLASS}'>", unsafe_allow_html=True)
        st.plotly_chart(bar_fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})
        st.markdown("</div>", unsafe_allow_html=True)
