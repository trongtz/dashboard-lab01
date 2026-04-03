from __future__ import annotations

import streamlit as st


def inject_shared_tab_styles() -> None:
    # Gom style dùng chung cho cả 3 tab để giao diện đồng bộ.
    st.markdown(
        """
        <style>
            .element-container {
                margin-bottom: 0.08rem;
            }
            .metric-card {
                background: linear-gradient(180deg, rgba(250, 253, 255, 0.98), rgba(232, 243, 252, 0.98));
                border-radius: 22px;
                padding: 0.58rem;
                border: 1px solid rgba(47, 127, 209, 0.16);
                box-shadow: 0 10px 22px rgba(47, 127, 209, 0.10);
                transition: transform 0.18s ease;
            }
            .metric-card:hover {
                transform: scale(1.015);
            }
            .stPlotlyChart {
                background: linear-gradient(180deg, rgba(250, 253, 255, 0.98), rgba(232, 243, 252, 0.98));
                border: 1px solid rgba(47, 127, 209, 0.14);
                border-radius: 22px;
                padding: 0.18rem;
                box-shadow: 0 10px 22px rgba(47, 127, 209, 0.10);
                margin-top: 0;
            }
            .stDataFrame {
                background: rgba(247, 251, 255, 0.98);
                border: 1px solid rgba(47, 127, 209, 0.14);
                border-radius: 14px;
                padding: 0.2rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_chart_card_styles(class_name: str) -> None:
    # Mỗi tab có thể dùng class riêng để bọc chart nhưng vẫn tái sử dụng cùng một kiểu khung.
    st.markdown(
        f"""
        <style>
            .{class_name} {{
                position: relative;
                overflow: hidden;
                border-radius: 22px;
            }}
            .{class_name} .stPlotlyChart {{
                border: 1px solid rgba(47, 127, 209, 0.14) !important;
                box-shadow: 0 12px 22px rgba(47, 127, 209, 0.10);
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )
