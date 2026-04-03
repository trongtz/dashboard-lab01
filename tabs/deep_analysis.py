from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from tabs.common import inject_tab_styles, show_no_data_message, style_figure


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


def _build_price_segment(price: pd.Series) -> pd.Series:
    bins = [-1, 100_000, 300_000, 700_000, 2_000_000, 5_000_000, 20_000_000, np.inf]
    return pd.cut(price, bins=bins, labels=PRICE_SEGMENT_ORDER)


def _build_discount_band(discount_rate: pd.Series) -> pd.Series:
    bins = [-0.1, 0, 10, 20, 30, 40, np.inf]
    return pd.cut(discount_rate.fillna(0), bins=bins, labels=DISCOUNT_BAND_ORDER)


def _prepare_segment_summary(df: pd.DataFrame) -> pd.DataFrame:
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
    inject_tab_styles()

    if df.empty:
        show_no_data_message("Phân khúc giá bán")
        return

    segment_summary = _prepare_segment_summary(df)
    heatmap_df = _prepare_discount_heatmap(df)

    if segment_summary.empty or heatmap_df.empty:
        st.warning("Không có đủ dữ liệu giá hoặc giảm giá để phân tích.")
        return

    best_segment = segment_summary.sort_values(["gold_score", "total_sold"], ascending=False).iloc[0]

    st.markdown(
        """
        <style>
            .deep-chart {
                position: relative;
                overflow: hidden;
                border-radius: 22px;
            }
            .deep-chart .stPlotlyChart {
                border: 1px solid rgba(255, 140, 0, 0.14) !important;
                box-shadow: 0 12px 22px rgba(0, 0, 0, 0.12);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    segment_summary["is_best_segment"] = segment_summary["price_segment"] == best_segment["price_segment"]
    segment_summary["bar_color"] = np.where(
        segment_summary["is_best_segment"], "Phân khúc vàng", "Phân khúc còn lại"
    )

    bubble_fig = px.bar(
        segment_summary,
        x="price_segment",
        y="total_sold",
        color="bar_color",
        color_discrete_map={
            "Phân khúc vàng": "#D96B0B",
            "Phân khúc còn lại": "#F7B267",
        },
        text="total_sold_label",
        custom_data=["product_count", "avg_sold_label"],
        title="Phân khúc giá vàng: nơi sản phẩm tập trung và sức mua bùng nổ",
    )
    bubble_fig.update_traces(
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
    bubble_fig.update_layout(
        title=dict(text="Lượt mua theo phân khúc giá", x=0.5, xanchor="center"),
        xaxis=dict(title=None, automargin=True),
        yaxis=dict(title="Tổng lượt mua", automargin=True),
        margin=dict(t=48, l=26, r=18, b=34),
        showlegend=False,
    )
    style_figure(bubble_fig, height=330)
    bubble_fig.update_layout(title_font=dict(size=15))
    bubble_fig.update_xaxes(tickangle=-24)

    heatmap_fig = px.density_heatmap(
        heatmap_df,
        x="price_segment",
        y="discount_band",
        z="avg_sold",
        histfunc="avg",
        text_auto=".0f",
        color_continuous_scale=["#FFF2E0", "#F7C27B", "#FF8A1D", "#CC5A00"],
        title="Độ nhạy khuyến mãi theo từng phân khúc giá",
    )
    heatmap_fig.update_traces(
        customdata=heatmap_df[["product_count", "median_sold", "avg_sold_label"]].to_numpy()
    )
    heatmap_fig.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Mức giảm giá: %{y}<br>"
            "Lượt mua trung bình/SP: %{customdata[2]}<br>"
            "Lượt mua trung vị/SP: %{customdata[1]:,.1f}<br>"
            "Số sản phẩm: %{customdata[0]:,.0f}<extra></extra>"
        )
    )
    heatmap_fig.update_layout(
        title=dict(text="Giảm giá theo phân khúc", x=0.5, xanchor="center"),
        xaxis=dict(title=None),
        yaxis=dict(title="Biên độ giảm giá"),
        margin=dict(t=48, l=28, r=18, b=72),
        coloraxis_colorbar=dict(title="Lượt mua TB/SP"),
    )
    style_figure(heatmap_fig, height=330)
    heatmap_fig.update_layout(title_font=dict(size=15))
    heatmap_fig.update_xaxes(tickangle=-28, automargin=True)
    heatmap_fig.update_yaxes(automargin=True)

    left_col, right_col = st.columns(2, gap="small")

    with left_col:
        st.markdown("<div class='deep-chart'>", unsafe_allow_html=True)
        st.plotly_chart(bubble_fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})
        st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        st.markdown("<div class='deep-chart'>", unsafe_allow_html=True)
        st.plotly_chart(heatmap_fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})
        st.markdown("</div>", unsafe_allow_html=True)
