from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from tabs.chart_helpers import show_no_data_message, style_figure
from tabs.styles import inject_chart_card_styles, inject_shared_tab_styles


DISCOUNT_BAND_ORDER = [
    "0%",
    "1% - 10%",
    "11% - 20%",
    "21% - 30%",
    "31% - 40%",
    "Trên 40%",
]

DISCOUNT_COLORS = [
    "#F6D7B0",
    "#F7BE77",
    "#F49A41",
    "#EA7D1C",
    "#D7680B",
    "#B85400",
]

CHART_WRAPPER_CLASS = "discount-rate-chart"


def _build_discount_band(discount_rate: pd.Series) -> pd.Series:
    # Gom tỷ lệ giảm giá thành các band để so sánh dễ hơn thay vì nhìn từng giá trị rời rạc.
    bins = [-0.1, 0, 10, 20, 30, 40, float("inf")]
    return pd.cut(discount_rate.fillna(0), bins=bins, labels=DISCOUNT_BAND_ORDER)


def _prepare_discount_distribution(df: pd.DataFrame) -> pd.DataFrame:
    # Chuẩn bị dữ liệu cho biểu đồ phân phối lượt mua theo mức giảm giá.
    work_df = df.copy()
    work_df = work_df[(work_df["price"] > 0) & (work_df["historical_sold"] >= 0)].copy()
    work_df["discount_band"] = _build_discount_band(work_df["discount_rate"])
    work_df = work_df.dropna(subset=["discount_band"])
    work_df["discount_band"] = pd.Categorical(
        work_df["discount_band"], categories=DISCOUNT_BAND_ORDER, ordered=True
    )
    return work_df


def _prepare_category_efficiency(df: pd.DataFrame, top_n: int = 12) -> pd.DataFrame:
    # Giữ lại các ngành hàng có tổng lượt mua lớn để tránh biểu đồ bị loãng.
    work_df = df.copy()
    work_df["category"] = work_df["category"].fillna("Chưa phân loại")

    grouped = (
        work_df.groupby("category", as_index=False)
        .agg(
            avg_discount_rate=("discount_rate", "mean"),
            avg_sold=("historical_sold", "mean"),
            total_sold=("historical_sold", "sum"),
            product_count=("product_id", "count"),
            median_price=("price", "median"),
        )
        .sort_values("total_sold", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    grouped["avg_discount_label"] = grouped["avg_discount_rate"].map(lambda value: f"{value:.1f}%")
    grouped["avg_sold_label"] = grouped["avg_sold"].map(lambda value: f"{value:,.1f}")
    grouped["total_sold_label"] = grouped["total_sold"].map(lambda value: f"{value:,.0f}")
    return grouped


def render_tab(df: pd.DataFrame, filters: dict) -> None:
    # Tab 3 tập trung vào việc giảm giá bao nhiêu là đủ và ngành hàng nào giảm giá hiệu quả hơn.
    inject_shared_tab_styles()
    inject_chart_card_styles(CHART_WRAPPER_CLASS)

    if df.empty:
        show_no_data_message("Tỉ lệ giảm giá")
        return

    distribution_df = _prepare_discount_distribution(df)
    category_df = _prepare_category_efficiency(df)

    if distribution_df.empty or category_df.empty:
        st.warning("Không có đủ dữ liệu giảm giá để vẽ biểu đồ.")
        return

    discount_distribution_fig = px.box(
        distribution_df,
        x="discount_band",
        y="historical_sold",
        color="discount_band",
        category_orders={"discount_band": DISCOUNT_BAND_ORDER},
        color_discrete_sequence=DISCOUNT_COLORS,
        title="Lượt mua theo mức giảm giá",
    )
    discount_distribution_fig.update_traces(
        boxmean=True,
        hovertemplate="Mức giảm giá: %{x}<br>Lượt mua: %{y:,.0f}<extra></extra>",
    )
    discount_distribution_fig.update_layout(
        title=dict(x=0.5, xanchor="center"),
        xaxis=dict(title=None, automargin=True),
        yaxis=dict(title="Lượt mua trên mỗi sản phẩm", type="log", automargin=True),
        margin=dict(t=48, l=30, r=10, b=30),
        showlegend=False,
    )
    style_figure(discount_distribution_fig, height=370)
    discount_distribution_fig.update_layout(title_font=dict(size=15))

    category_discount_fig = px.scatter(
        category_df,
        x="avg_discount_rate",
        y="avg_sold",
        size="total_sold",
        color="median_price",
        size_max=54,
        color_continuous_scale=["#FDE6C8", "#F7BE77", "#EA7D1C", "#B85400"],
        custom_data=["category", "avg_discount_label", "avg_sold_label", "total_sold_label", "product_count"],
        title="Hiệu quả giảm giá theo ngành hàng",
    )
    category_discount_fig.update_traces(
        marker=dict(line=dict(color="rgba(255,255,255,0.65)", width=1.2), opacity=0.88),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Giảm giá trung bình: %{customdata[1]}<br>"
            "Lượt mua TB/SP: %{customdata[2]}<br>"
            "Tổng lượt mua: %{customdata[3]}<br>"
            "Số sản phẩm: %{customdata[4]:,.0f}<extra></extra>"
        ),
    )
    category_discount_fig.update_layout(
        title=dict(x=0.5, xanchor="center"),
        xaxis=dict(title="Giảm giá trung bình (%)", automargin=True),
        yaxis=dict(title="Lượt mua trung bình / sản phẩm", automargin=True),
        margin=dict(t=48, l=28, r=18, b=28),
        coloraxis_colorbar=dict(title="Giá trung vị"),
    )
    style_figure(category_discount_fig, height=370)
    category_discount_fig.update_layout(title_font=dict(size=15))

    left_col, right_col = st.columns(2, gap="small")

    with left_col:
        st.markdown(f"<div class='{CHART_WRAPPER_CLASS}'>", unsafe_allow_html=True)
        st.plotly_chart(
            discount_distribution_fig,
            use_container_width=True,
            config={"displayModeBar": False, "responsive": True},
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        st.markdown(f"<div class='{CHART_WRAPPER_CLASS}'>", unsafe_allow_html=True)
        st.plotly_chart(
            category_discount_fig,
            use_container_width=True,
            config={"displayModeBar": False, "responsive": True},
        )
        st.markdown("</div>", unsafe_allow_html=True)
