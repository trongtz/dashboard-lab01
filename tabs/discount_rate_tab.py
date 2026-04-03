from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    "#DCEFFC",
    "#BDDFF8",
    "#9BC9F2",
    "#6FAFEA",
    "#2F7FD1",
    "#174A8B",
]

CHART_WRAPPER_CLASS = "discount-rate-chart"
BLUE_SCALE = ["#DCEFFC", "#A9D6F5", "#6FAFEA", "#2F7FD1", "#174A8B"]


def _build_discount_band(discount_rate: pd.Series) -> pd.Series:
    # Gom tỷ lệ giảm giá thành các band để so sánh dễ hơn thay vì nhìn từng giá trị rời rạc.
    bins = [-0.1, 0, 10, 20, 30, 40, float("inf")]
    return pd.cut(discount_rate.fillna(0), bins=bins, labels=DISCOUNT_BAND_ORDER)


def _prepare_discount_distribution(df: pd.DataFrame) -> pd.DataFrame:
    # Tóm tắt theo từng band giảm giá để nhìn ngay mức nào kéo được sức mua tốt hơn.
    work_df = df.copy()
    work_df = work_df[(work_df["price"] > 0) & (work_df["historical_sold"] >= 0)].copy()
    work_df["discount_band"] = _build_discount_band(work_df["discount_rate"])
    work_df = work_df.dropna(subset=["discount_band"])

    grouped = (
        work_df.groupby("discount_band", observed=False)
        .agg(
            avg_sold=("historical_sold", "mean"),
            median_sold=("historical_sold", "median"),
            total_sold=("historical_sold", "sum"),
            product_count=("product_id", "count"),
        )
        .reset_index()
    )
    grouped["discount_band"] = pd.Categorical(grouped["discount_band"], categories=DISCOUNT_BAND_ORDER, ordered=True)
    grouped = grouped.sort_values("discount_band")
    grouped["discount_band"] = grouped["discount_band"].astype(str)
    grouped["avg_sold_label"] = grouped["avg_sold"].map(lambda value: f"{value:,.1f}")
    grouped["total_sold_label"] = grouped["total_sold"].map(lambda value: f"{value:,.0f}")
    return grouped


def _prepare_category_efficiency(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    # Chỉ giữ các ngành hàng lớn để biểu đồ gọn và dễ đọc hơn.
    work_df = df.copy()
    work_df["category"] = work_df["category"].fillna("Chưa phân loại")

    grouped = (
        work_df.groupby("category", as_index=False)
        .agg(
            avg_discount_rate=("discount_rate", "mean"),
            avg_sold=("historical_sold", "mean"),
            total_sold=("historical_sold", "sum"),
            product_count=("product_id", "count"),
        )
        .sort_values("avg_sold", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    grouped["avg_discount_label"] = grouped["avg_discount_rate"].map(lambda value: f"{value:.1f}%")
    grouped["avg_sold_label"] = grouped["avg_sold"].map(lambda value: f"{value:,.1f}")
    grouped["total_sold_label"] = grouped["total_sold"].map(lambda value: f"{value:,.0f}")
    grouped["category"] = grouped["category"].astype(str)
    return grouped


def render_tab(df: pd.DataFrame, filters: dict) -> None:
    # Tab 3 tập trung vào câu chuyện: giảm giá bao nhiêu là đủ và ngành hàng nào giảm giá hiệu quả hơn.
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

    # Dùng go.Bar để khóa cứng thứ tự và nhãn band giảm giá, tránh Plotly tự suy đoán sai trục X.
    discount_distribution_fig = go.Figure(
        data=[
            go.Bar(
                x=distribution_df["discount_band"].tolist(),
                y=distribution_df["avg_sold"].tolist(),
                text=distribution_df["avg_sold_label"].tolist(),
                textposition="outside",
                cliponaxis=False,
                marker=dict(color=DISCOUNT_COLORS[: len(distribution_df)]),
                customdata=distribution_df[["product_count", "total_sold_label", "median_sold"]].to_numpy(),
                hovertemplate=(
                    "Mức giảm giá: %{x}<br>"
                    "Lượt mua TB/SP: %{y:,.1f}<br>"
                    "Lượt mua trung vị/SP: %{customdata[2]:,.1f}<br>"
                    "Tổng lượt mua: %{customdata[1]}<br>"
                    "Số sản phẩm: %{customdata[0]:,.0f}<extra></extra>"
                ),
            )
        ]
    )
    discount_distribution_fig.update_layout(
        title=dict(text="Lượt mua theo mức giảm giá", x=0.5, xanchor="center"),
        xaxis=dict(
            title=None,
            automargin=True,
            type="category",
            categoryorder="array",
            categoryarray=DISCOUNT_BAND_ORDER,
        ),
        yaxis=dict(title="Lượt mua trung bình / sản phẩm", automargin=True),
        margin=dict(t=48, l=30, r=10, b=36),
        showlegend=False,
    )
    style_figure(discount_distribution_fig, height=370)
    discount_distribution_fig.update_layout(title_font=dict(size=15))

    category_discount_fig = px.bar(
        category_df,
        x="avg_sold",
        y="category",
        orientation="h",
        text="avg_sold_label",
        custom_data=["avg_discount_label", "total_sold_label", "product_count"],
        color="avg_discount_rate",
        color_continuous_scale=BLUE_SCALE,
        title="Ngành hàng giảm giá hiệu quả nhất",
    )
    category_discount_fig.update_traces(
        textposition="outside",
        cliponaxis=False,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Lượt mua TB/SP: %{x:,.1f}<br>"
            "Giảm giá trung bình: %{customdata[0]}<br>"
            "Tổng lượt mua: %{customdata[1]}<br>"
            "Số sản phẩm: %{customdata[2]:,.0f}<extra></extra>"
        ),
    )
    category_discount_fig.update_layout(
        title=dict(x=0.5, xanchor="center"),
        xaxis=dict(title="Lượt mua trung bình / sản phẩm", automargin=True),
        yaxis=dict(title=None, automargin=True, categoryorder="total ascending"),
        margin=dict(t=48, l=10, r=22, b=28),
        coloraxis_colorbar=dict(title="Giảm giá TB (%)"),
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
