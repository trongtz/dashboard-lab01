from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from tabs.discount_rate_tab import render_tab as render_discount_rate_tab
from tabs.price_segment_tab import render_tab as render_price_segment_tab
from tabs.product_category_tab import render_tab as render_product_category_tab

st.set_page_config(page_title="Bảng điều khiển phân tích Tiki", page_icon="📊", layout="wide")

COLOR_PRIMARY = "#2F7FD1"
COLOR_SECONDARY = "#174A8B"
COLOR_ACCENT = "#6FAFEA"
BG_GRADIENT = "linear-gradient(180deg, #D6ECFF 0%, #B9DCFA 46%, #9ECAF2 100%)"
CARD_BG = "rgba(238, 247, 255, 0.92)"
CARD_BORDER = "rgba(47, 127, 209, 0.18)"
TEXT_MAIN = "#16324F"
TEXT_DIM = "#5F6F81"


@st.cache_data
def load_data(path: str = "data.csv") -> pd.DataFrame:
    # Chuẩn hóa tên cột từ file gốc để các tab chỉ làm việc với một schema thống nhất.
    rename_map = {
        "id": "product_id",
        "brand_name": "brand",
        "category_l1_name": "category",
        "current_price": "price",
        "all_time_quantity_sold": "historical_sold",
        "rating_average": "rating",
    }
    df = pd.read_csv(path).rename(columns=rename_map)

    if "category" not in df.columns:
        for fallback in ("primary_category", "primary_category_name"):
            if fallback in df.columns:
                df["category"] = df[fallback]
                break
        else:
            df["category"] = "Chưa phân loại"

    df["category"] = df["category"].fillna("Chưa phân loại")

    numeric_cols = ["price", "original_price", "discount", "discount_rate", "rating", "review_count", "historical_sold"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for target in ("historical_sold", "review_count", "rating"):
        if target not in df.columns:
            df[target] = 0
        else:
            df[target] = df[target].fillna(0)

    df["sales_per_review"] = df["historical_sold"] / df["review_count"].replace(0, np.nan)
    df["sales_per_review"] = df["sales_per_review"].fillna(0)
    df["popularity_score"] = df["historical_sold"] * (df["rating"].fillna(0) / 5 + 1)
    return df


def inject_styles() -> None:
    st.markdown(
        f"""
        <style>
            @import url("https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700&family=Inter:wght@400;600;700&display=swap");

            @keyframes tikiGlowShift {{
                0% {{ background-position: 0% 50%; }}
                50% {{ background-position: 100% 50%; }}
                100% {{ background-position: 0% 50%; }}
            }}

            @keyframes emberGlow {{
                0% {{ box-shadow: 0 0 0 rgba(47, 127, 209, 0), 0 12px 24px rgba(47, 127, 209, 0.10); }}
                50% {{ box-shadow: 0 0 26px rgba(47, 127, 209, 0.16), 0 18px 34px rgba(47, 127, 209, 0.12); }}
                100% {{ box-shadow: 0 0 0 rgba(47, 127, 209, 0), 0 12px 24px rgba(47, 127, 209, 0.10); }}
            }}

            :root {{
                --primary: {COLOR_PRIMARY};
                --secondary: {COLOR_SECONDARY};
                --accent: {COLOR_ACCENT};
                --card: {CARD_BG};
                --card-border: {CARD_BORDER};
                --text-main: {TEXT_MAIN};
                --text-dim: {TEXT_DIM};
                --background: {BG_GRADIENT};
            }}

            html, body, [class*="css"] {{
                font-family: "Inter", "Manrope", system-ui, -apple-system, sans-serif;
            }}

            body, .stApp, .block-container {{
                color: var(--text-main);
            }}

            .stApp {{
                background: {BG_GRADIENT};
                background-size: 180% 180%;
                min-height: 100vh;
                overflow: auto;
                animation: tikiGlowShift 12s ease-in-out infinite;
            }}

            [data-testid="stSidebar"] {{
                display: none;
            }}

            [data-testid="stHeader"] {{
                background: transparent;
                height: 0;
            }}

            .block-container {{
                max-width: 1260px;
                margin: 0 auto;
                padding: 0.02rem 1rem 0.45rem;
                background: linear-gradient(180deg, rgba(232, 243, 252, 0.97), rgba(210, 230, 247, 0.97));
                background-size: 160% 160%;
                border-radius: 20px;
                border: 1px solid rgba(47, 127, 209, 0.14);
                box-shadow: 0 24px 54px rgba(47, 127, 209, 0.14);
                animation: tikiGlowShift 14s ease-in-out infinite, emberGlow 10s ease-in-out infinite;
            }}

            .title-chip {{
                background: linear-gradient(135deg, #fafdff, #deefff);
                background-size: 160% 160%;
                border: 1px solid rgba(47, 127, 209, 0.18);
                border-radius: 14px;
                padding: 0.04rem 0.72rem;
                min-height: 2.1rem;
                display: inline-flex;
                align-items: center;
                font-size: 0.95rem;
                font-weight: 700;
                color: #15324a;
                letter-spacing: 0.01em;
                box-shadow: 0 10px 18px rgba(47, 127, 209, 0.10);
                animation: tikiGlowShift 10s ease-in-out infinite, emberGlow 8s ease-in-out infinite;
            }}

            .toolbar-row {{
                margin-bottom: -0.82rem;
            }}

            .stTabs [data-baseweb="tab-list"] {{
                gap: 0.35rem;
                margin-top: -0.5rem;
                margin-bottom: 0;
            }}

            .stTabs [data-baseweb="tab-highlight"] {{
                background: #174A8B !important;
                height: 0.16rem !important;
                border-radius: 999px !important;
                margin-top: 0.12rem !important;
            }}

            .stTabs [data-baseweb="tab"] {{
                border-radius: 14px;
                background: rgba(247, 251, 255, 0.92);
                color: #385069;
                border: 1px solid rgba(47, 127, 209, 0.16);
                padding: 0.04rem 0.62rem;
                min-height: 2.05rem;
                font-size: 0.8rem;
                font-weight: 600;
            }}

            .stTabs [aria-selected="true"] {{
                background: linear-gradient(120deg, #6FAFEA, #2F7FD1);
                border: 1px solid rgba(47, 127, 209, 0.24);
                color: #fff !important;
                box-shadow: 0 10px 20px rgba(47, 127, 209, 0.18);
            }}

            .stTabs [data-baseweb="tab-panel"] {{
                height: calc(100vh - 4.8rem);
                overflow-y: auto;
                padding-top: 0 !important;
                margin-top: -0.6rem;
            }}

            .stCheckbox label {{
                color: #16324F !important;
            }}

            div[data-testid="stPopover"] button {{
                min-height: 2.1rem;
                background: rgba(247, 251, 255, 0.96);
                border: 1px solid rgba(47, 127, 209, 0.18);
                border-radius: 12px;
                color: #16324F;
                width: 100%;
                min-width: 0;
                justify-content: space-between;
                padding-inline: 0.72rem;
                font-size: 0.84rem;
                font-weight: 600;
            }}

            div[data-testid="stPopoverContent"] {{
                min-width: 320px;
            }}

            .checkbox-panel {{
                max-height: 300px;
                overflow-y: auto;
                padding-right: 0.15rem;
                margin-top: 0.2rem;
            }}

            .stPlotlyChart {{
                border: none !important;
                margin-top: 0 !important;
            }}

            .element-container {{
                margin-bottom: 0.15rem !important;
            }}

            .stSpinner > div p,
            .stAlert > div,
            .stInfo > div {{
                color: var(--text-main);
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def filter_data(df: pd.DataFrame, selected_categories: list[str]) -> pd.DataFrame:
    # Bộ lọc danh mục chỉ áp vào tab 2 và 3; tab 1 vẫn cần dữ liệu gốc để tính "Khác" cho đúng.
    filtered = df.copy()
    if selected_categories:
        filtered = filtered[filtered["category"].isin(selected_categories)]
    else:
        filtered = filtered.iloc[0:0]
    return filtered


def _build_category_selector(categories: list[str]) -> list[str]:
    # Lưu trạng thái checkbox theo session để người dùng đổi tab vẫn không mất lựa chọn.
    for category in categories:
        key = f"category_filter_{category}"
        if key not in st.session_state:
            st.session_state[key] = True

    with st.popover("Danh mục", use_container_width=True):
        action_left, action_right = st.columns(2, gap="small")
        with action_left:
            if st.button("Chọn tất cả", use_container_width=True):
                for category in categories:
                    st.session_state[f"category_filter_{category}"] = True
                st.rerun()
        with action_right:
            if st.button("Bỏ chọn tất cả", use_container_width=True):
                for category in categories:
                    st.session_state[f"category_filter_{category}"] = False
                st.rerun()

        st.markdown('<div class="checkbox-panel">', unsafe_allow_html=True)
        check_cols = st.columns(2, gap="small")
        for index, category in enumerate(categories):
            with check_cols[index % 2]:
                st.checkbox(category, key=f"category_filter_{category}")
        st.markdown("</div>", unsafe_allow_html=True)

    return [category for category in categories if st.session_state.get(f"category_filter_{category}", True)]


def render_top_bar(df: pd.DataFrame) -> list[str]:
    # Top bar giữ title bên trái và bộ lọc danh mục gọn ở góc phải như layout ban đầu.
    st.markdown('<div class="toolbar-row">', unsafe_allow_html=True)
    left_col, spacer_col, cat_col = st.columns([5.2, 4.0, 1.4], gap="small")

    with left_col:
        st.markdown('<div class="title-chip">Phân tích xu hướng mua hàng TIKI</div>', unsafe_allow_html=True)

    with spacer_col:
        st.markdown("")

    categories = sorted(df["category"].dropna().unique().tolist())
    with cat_col:
        selected_categories = _build_category_selector(categories)

    st.markdown('</div>', unsafe_allow_html=True)
    return selected_categories


def main() -> None:
    inject_styles()
    df = load_data()

    selected_categories = render_top_bar(df)

    with st.spinner("Đang cập nhật bảng điều khiển..."):
        filtered_df = filter_data(df, selected_categories)

    filters = {
        "category": selected_categories,
        "primary_color": COLOR_PRIMARY,
        "secondary_color": COLOR_SECONDARY,
        "accent_color": COLOR_ACCENT,
        "text_main": TEXT_MAIN,
        "text_dim": TEXT_DIM,
        "card_bg": CARD_BG,
    }

    tab_overview, tab_deep, tab_insights = st.tabs(
        ["Danh mục sản phẩm", "Phân khúc giá bán", "Tỉ lệ giảm giá"]
    )

    if filtered_df.empty:
        for tab in [tab_overview, tab_deep, tab_insights]:
            with tab:
                st.info("Không có dữ liệu phù hợp với bộ lọc đã chọn.")
        return

    with tab_overview:
        render_product_category_tab(df, filters)

    with tab_deep:
        render_price_segment_tab(filtered_df, filters)

    with tab_insights:
        render_discount_rate_tab(filtered_df, filters)


if __name__ == "__main__":
    main()
