from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from tabs.chart_helpers import show_no_data_message, style_figure
from tabs.styles import inject_chart_card_styles, inject_shared_tab_styles


PRICE_SEGMENT_ORDER = [
    "Dưới 100K",
    "100K - 300K",
    "300K - 700K",
    "700K - 2 triệu",
    "2 - 5 triệu",
    "5 - 20 triệu",
    "Trên 20 triệu",
]

DISCOUNT_BAND_ORDER = [
    "0%",
    "1% - 10%",
    "11% - 20%",
    "21% - 30%",
    "31% - 40%",
    "Trên 40%",
]

CHART_WRAPPER_CLASS = "price-segment-chart"
BLUE_SCALE = ["#DCEFFC", "#A9D6F5", "#6FAFEA", "#2F7FD1", "#174A8B"]


def _build_price_segment(price: pd.Series) -> pd.Series:
    # Chia giá thành các ngưỡng dễ đọc để phân tích hành vi mua theo phân khúc.
    bins = [-1, 100_000, 300_000, 700_000, 2_000_000, 5_000_000, 20_000_000, np.inf]
    return pd.cut(price, bins=bins, labels=PRICE_SEGMENT_ORDER)


def _build_discount_band(discount_rate: pd.Series) -> pd.Series:
    bins = [-0.1, 0, 10, 20, 30, 40, np.inf]
    return pd.cut(discount_rate.fillna(0), bins=bins, labels=DISCOUNT_BAND_ORDER)


def _prepare_segment_summary(df: pd.DataFrame) -> pd.DataFrame:
    # Tóm tắt quy mô từng phân khúc giá: số sản phẩm, tổng lượt mua và sức mua trung bình.
    work_df = df.copy()
    work_df["price_segment"] = _build_price_segment(work_df["price"])

    summary = (
        work_df.groupby("price_segment", observed=False)
        .agg(
            product_count=("product_id", "count"),
            total_sold=("historical_sold", "sum"),
            avg_sold=("historical_sold", "mean"),
            median_price=("price", "median"),
        )
        .reset_index()
    )
    summary = summary.dropna(subset=["price_segment"])
    summary["price_segment"] = pd.Categorical(summary["price_segment"], categories=PRICE_SEGMENT_ORDER, ordered=True)
    summary = summary.sort_values("price_segment")
    summary["avg_sold_label"] = summary["avg_sold"].map(lambda value: f"{value:,.0f}")
    summary["total_sold_label"] = summary["total_sold"].map(lambda value: f"{value:,.0f}")
    summary["gold_score"] = summary["product_count"].rank(pct=True) * summary["total_sold"].rank(pct=True)
    return summary


def _prepare_discount_heatmap(df: pd.DataFrame) -> pd.DataFrame:
    # Tạo ma trận để xem cùng một mức giảm giá tác động khác nhau ra sao ở từng phân khúc giá.
    work_df = df.copy()
    work_df["price_segment"] = _build_price_segment(work_df["price"])
    work_df["discount_band"] = _build_discount_band(work_df["discount_rate"])

    heatmap_df = (
        work_df.groupby(["discount_band", "price_segment"], observed=False)
        .agg(
            avg_sold=("historical_sold", "mean"),
            median_sold=("historical_sold", "median"),
            product_count=("product_id", "count"),
        )
        .reset_index()
    )
    heatmap_df = heatmap_df.dropna(subset=["discount_band", "price_segment"])
    heatmap_df["discount_band"] = pd.Categorical(
        heatmap_df["discount_band"], categories=DISCOUNT_BAND_ORDER, ordered=True
    )
    heatmap_df["price_segment"] = pd.Categorical(
        heatmap_df["price_segment"], categories=PRICE_SEGMENT_ORDER, ordered=True
    )
    heatmap_df = heatmap_df.sort_values(["discount_band", "price_segment"])
    heatmap_df["avg_sold_label"] = heatmap_df["avg_sold"].map(lambda value: f"{value:,.1f}")
    return heatmap_df


def render_tab(df: pd.DataFrame, filters: dict) -> None:
    # Tab 2 trả lời 2 ý chính: phân khúc giá "vàng" và độ nhạy khuyến mãi theo từng mức giá.
    inject_shared_tab_styles()
    inject_chart_card_styles(CHART_WRAPPER_CLASS)

    if df.empty:
        show_no_data_message("Phân khúc giá bán")
        return

    segment_summary = _prepare_segment_summary(df)
    heatmap_df = _prepare_discount_heatmap(df)

    if segment_summary.empty or heatmap_df.empty:
        st.warning("Không có đủ dữ liệu giá hoặc giảm giá để phân tích.")
        return

    best_segment = segment_summary.sort_values(["gold_score", "total_sold"], ascending=False).iloc[0]
    segment_summary["is_best_segment"] = segment_summary["price_segment"] == best_segment["price_segment"]
    segment_summary["bar_color"] = np.where(
        segment_summary["is_best_segment"], "Phân khúc vàng", "Phân khúc còn lại"
    )
    price_segment_ticktext = [
        "Dưới 100K",
        "100K - 300K",
        "300K - 700K",
        "700K - 2 triệu",
        "2 - 5 triệu",
        "5 - 20 triệu",
        "Trên 20<br>triệu",
    ]

    sales_fig = px.bar(
        segment_summary,
        x="price_segment",
        y="total_sold",
        color="bar_color",
        color_discrete_map={
            "Phân khúc vàng": BLUE_SCALE[4],
            "Phân khúc còn lại": BLUE_SCALE[2],
        },
        text="total_sold_label",
        custom_data=["product_count", "avg_sold_label"],
        title="Lượt mua theo phân khúc giá",
    )
    sales_fig.update_traces(
        textposition="outside",
        cliponaxis=False,
        marker_line_width=0,
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Tổng lượt mua: %{y:,.0f}<br>"
            "Số sản phẩm: %{customdata[0]:,.0f}<br>"
            "Lượt mua trung bình/SP: %{customdata[1]}<extra></extra>"
        ),
    )
    sales_fig.update_layout(
        title=dict(text="Lượt mua theo phân khúc giá", x=0.5, xanchor="center"),
        xaxis=dict(
            title=None,
            automargin=True,
            tickangle=-14,
            tickfont=dict(size=11),
            tickmode="array",
            tickvals=segment_summary["price_segment"].tolist(),
            ticktext=price_segment_ticktext,
        ),
        yaxis=dict(title="Tổng lượt mua", automargin=True),
        margin=dict(t=48, l=26, r=44, b=56),
        showlegend=False,
    )
    style_figure(sales_fig, height=370)
    sales_fig.update_layout(title_font=dict(size=15))

    discount_fig = px.density_heatmap(
        heatmap_df,
        x="price_segment",
        y="discount_band",
        z="avg_sold",
        histfunc="avg",
        text_auto=".0f",
        color_continuous_scale=BLUE_SCALE,
        title="Giảm giá theo phân khúc",
    )
    discount_fig.update_traces(customdata=heatmap_df[["product_count", "median_sold", "avg_sold_label"]].to_numpy())
    discount_fig.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Mức giảm giá: %{y}<br>"
            "Lượt mua trung bình/SP: %{customdata[2]}<br>"
            "Lượt mua trung vị/SP: %{customdata[1]:,.1f}<br>"
            "Số sản phẩm: %{customdata[0]:,.0f}<extra></extra>"
        )
    )
    discount_fig.update_layout(
        title=dict(text="Giảm giá theo phân khúc", x=0.5, xanchor="center"),
        xaxis=dict(title=None),
        yaxis=dict(title="Biên độ giảm giá"),
        margin=dict(t=48, l=28, r=18, b=72),
        coloraxis_colorbar=dict(title="Lượt mua TB/SP"),
    )
    style_figure(discount_fig, height=370)
    discount_fig.update_layout(title_font=dict(size=15))
    discount_fig.update_xaxes(tickangle=-28, automargin=True)
    discount_fig.update_yaxes(automargin=True)

    left_col, right_col = st.columns(2, gap="small")

    with left_col:
        st.markdown(f"<div class='{CHART_WRAPPER_CLASS}'>", unsafe_allow_html=True)
        st.plotly_chart(sales_fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})
        st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        st.markdown(f"<div class='{CHART_WRAPPER_CLASS}'>", unsafe_allow_html=True)
        st.plotly_chart(discount_fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})
        st.markdown("</div>", unsafe_allow_html=True)
