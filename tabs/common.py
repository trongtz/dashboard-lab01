from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def inject_tab_styles() -> None:
    st.markdown(
        """
        <style>
            .element-container {
                margin-bottom: 0.08rem;
            }
            .metric-card {
                background: linear-gradient(180deg, rgba(255, 253, 249, 0.98), rgba(255, 236, 214, 0.98));
                border-radius: 22px;
                padding: 0.58rem;
                border: 1px solid rgba(255, 106, 0, 0.18);
                box-shadow: 0 10px 22px rgba(217, 126, 34, 0.16);
                transition: transform 0.18s ease;
            }
            .metric-card:hover {
                transform: scale(1.015);
            }
            .stPlotlyChart {
                background: linear-gradient(180deg, rgba(255, 253, 249, 0.98), rgba(255, 236, 214, 0.98));
                border: 1px solid rgba(255, 106, 0, 0.16);
                border-radius: 22px;
                padding: 0.18rem;
                box-shadow: 0 10px 22px rgba(217, 126, 34, 0.16);
                margin-top: 0;
            }
            .stDataFrame {
                background: rgba(255, 249, 242, 0.98);
                border: 1px solid rgba(255, 106, 0, 0.16);
                border-radius: 14px;
                padding: 0.2rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def style_figure(fig: go.Figure, height: int = 260) -> go.Figure:
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


def add_linear_trendline(
    fig: go.Figure,
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    line_color: str,
    name: str = "Trendline",
) -> None:
    clean_df = df[[x_col, y_col]].dropna()
    if clean_df.shape[0] < 2:
        return

    x_values = clean_df[x_col].to_numpy(dtype=float)
    y_values = clean_df[y_col].to_numpy(dtype=float)
    slope, intercept = np.polyfit(x_values, y_values, 1)

    x_line = np.linspace(x_values.min(), x_values.max(), 100)
    y_line = slope * x_line + intercept

    fig.add_trace(
        go.Scatter(
            x=x_line,
            y=y_line,
            mode="lines",
            name=name,
            line=dict(color=line_color, width=2, dash="dash"),
            hoverinfo="skip",
        )
    )


def show_no_data_message(tab_name: str) -> None:
    st.info(f"Không có dữ liệu cho mục {tab_name}. Hãy điều chỉnh bộ lọc.")
