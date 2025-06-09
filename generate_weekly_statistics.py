import pandas as pd
from datetime import datetime, timedelta
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import qrcode
import io
import base64


def generate_weekly_statistics(df):

    df["date"] = pd.to_datetime(df["date"])

    latest_date = df["date"].max()
    this_week = df[df["date"] > latest_date - timedelta(days=7)]
    last_week = df[
        (df["date"] <= latest_date - timedelta(days=7))
        & (df["date"] > latest_date - timedelta(days=14))
    ]

    this_week = this_week.copy()
    last_week = last_week.copy()
    this_week["week"] = "Текущая неделя"
    last_week["week"] = "Прошлая неделя"

    this_week["day"] = this_week["date"].dt.strftime("%A")
    last_week["day"] = last_week["date"].dt.strftime("%A")

    fig = make_subplots(rows=3, cols=1, shared_xaxes=False, vertical_spacing=0.03)

    fig.add_trace(
        go.Bar(
            x=last_week["day"],
            y=last_week["orders_sum_rub"],
            name="Заказы Прошлая неделя",
            text=last_week["orders_sum_rub"],
            marker=dict(
                color="lightslategrey",
                pattern=dict(shape="\\", fgcolor="white", bgcolor="lightslategrey"),
            ),
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Bar(
            x=this_week["day"],
            y=this_week["orders_sum_rub"],
            name="Заказы Текущая неделя",
            marker_color="crimson",
            text=this_week["orders_sum_rub"],
        ),
        row=1,
        col=1,
    )
    fig.update_traces(
        texttemplate="%{text:.4s}",
        textposition="inside",
        marker=dict(cornerradius="20%"),
    )

    fig.add_trace(
        go.Scatter(
            x=last_week["day"],
            y=(last_week["sum"] / last_week["orders_sum_rub"] * 100),
            marker_color="dimgray",
            name="ДРР Прошлая неделя",
            mode="lines+markers+text",
            text=(last_week["sum"] / last_week["orders_sum_rub"] * 100)
            .round(1)
            .astype(str)
            + "%",
            textposition="bottom left",
            textfont=dict(size=12),
            line=dict(width=3, dash="longdash"),
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=this_week["day"],
            y=(this_week["sum"] / this_week["orders_sum_rub"] * 100),
            marker=dict(color="orangered", size=6),
            name="ДРР Текущая неделя",
            mode="lines+markers+text",
            text=(this_week["sum"] / this_week["orders_sum_rub"] * 100)
            .round(1)
            .astype(str)
            + "%",
            textposition="bottom right",
            textfont=dict(size=12),
            line=dict(width=3),
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=last_week["day"],
            y=(last_week["cliks"] / last_week["views"] * 100),
            marker_color="dimgray",
            name="CTR Прошлая неделя",
            mode="lines+markers+text",
            text=(last_week["cliks"] / last_week["views"] * 100).round(1).astype(str)
            + "%",
            textposition="bottom left",
            textfont=dict(size=12),
            line=dict(width=3, dash="longdash"),  # ил)
        ),
        row=3,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=this_week["day"],
            y=(this_week["cliks"] / this_week["views"] * 100),
            marker=dict(color="orangered", size=6),
            name="CTR Текущая неделя",
            mode="lines+markers+text",
            text=(this_week["cliks"] / this_week["views"] * 100).round(1).astype(str)
            + "%",
            textposition="bottom right",
            textfont=dict(size=12),
            line=dict(width=3),
        ),
        row=3,
        col=1,
    )

    fig.update_yaxes(title_text="Сумма заказов", row=1, col=1)
    fig.update_yaxes(title_text="ДРР (%)", row=2, col=1)
    fig.update_yaxes(title_text="CTR (%)", row=3, col=1)

    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data("https://t.me/selleralarm_bot")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()

    fig.add_layout_image(
        dict(
            source="data:image/png;base64," + img_str,
            xref="paper",
            yref="paper",
            x=1.13,
            y=0.732,
            sizex=0.2,
            sizey=0.2,
            xanchor="center",
            yanchor="middle",
            layer="above",
        )
    )
    fig.add_annotation(
        dict(
            x=1.13,
            y=0.878,
            xref="paper",
            yref="paper",
            text="Введи в боте <b>/avg_stats</b><br>и сравни свои показатели<br>со средними по рынку<br>@selleralarm_bot",
            showarrow=False,
            font=dict(
                family="Montserrat, sans-serif",
                size=16,
            ),
            align="center",
            xanchor="center",
            yanchor="top",
            borderwidth=1,
            borderpad=4,
            opacity=0.9,
        )
    )

    cabinet_name = "ООО Сигма Еком"
    current_date = datetime.now().strftime("%d/%m/%Y")

    fig.update_layout(
        height=1280,
        width=1280,
        title=dict(
            text=f"{cabinet_name}: Прошлая неделя VS Текущая неделя. Дата:{current_date}"
        ),
        margin=dict(t=50, b=20),
        bargap=0.15,
        bargroupgap=0.1,
    )

    return fig
