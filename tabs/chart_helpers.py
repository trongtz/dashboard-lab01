from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st


def style_figure(fig: go.Figure, height: int = 260) -> go.Figure:
    # Chuẩn hóa typography, nền và lề cho mọi biểu đồ Plotly trong dashboard.
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=38, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#16324F", size=14),
        title=dict(font=dict(color="#16324F", size=22)),
        legend=dict(font=dict(color="#385069", size=13), title=dict(font=dict(color="#385069"))),
        xaxis=dict(
            gridcolor="rgba(22, 50, 79, 0.10)",
            zeroline=False,
            title_font=dict(color="#385069", size=14),
            tickfont=dict(color="#385069", size=13),
        ),
        yaxis=dict(
            gridcolor="rgba(22, 50, 79, 0.10)",
            zeroline=False,
            title_font=dict(color="#385069", size=14),
            tickfont=dict(color="#385069", size=13),
        ),
        transition=dict(duration=450),
    )
    return fig


def show_no_data_message(tab_name: str) -> None:
    # Thông báo rỗng dùng chung để tránh lặp code ở từng tab.
    st.info(f"Không có dữ liệu cho mục {tab_name}. Hãy điều chỉnh bộ lọc.")
