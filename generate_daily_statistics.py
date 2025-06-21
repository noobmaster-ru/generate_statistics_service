# import pandas as pd
# from datetime import datetime, timedelta
# from plotly.subplots import make_subplots
# import plotly.graph_objects as go
# import qrcode
# import io
# import base64
# from loguru import logger


# def generate_daily_statistics(df_avg, df_weekly):
#     # logger.info(f"generate daily statisticss started")

#     # Средние по боту
#     df_avg["date"] = pd.to_datetime(df_avg["date"])  # average_cabinet_info.csv

#     latest_date_avg = df_avg["date"].max()
#     this_week_avg = df_avg[df_avg["date"] > latest_date_avg - timedelta(days=7)]

#     this_week_avg = this_week_avg.copy()
#     this_week_avg["week"] = "Текущая неделя"

#     this_week_avg["day"] = this_week_avg["date"].dt.strftime("%A")

#     # данные кабинета

#     df = df_weekly  # cabinet_info.csv
#     df["date"] = pd.to_datetime(df["date"])
#     # logger.info(f"df is {df}")
#     latest_date = df["date"].max()
#     this_week = df[df["date"] > latest_date - timedelta(days=7)]

#     this_week = this_week.copy()
#     this_week["week"] = "Текущая неделя"

#     this_week["day"] = this_week["date"].dt.strftime("%A")
#     # fig = go.Figure()
#     fig = make_subplots(
#         rows=3,
#         cols=1,
#         shared_xaxes=False,  # общий x-ось для всех графиков
#         vertical_spacing=0.03,  # расстояние между графиками
#         specs=[
#             [{"secondary_y": False}],
#             [{"secondary_y": False}],
#             [{"secondary_y": True}],
#         ],
#     )
#     # logger.info(f"fig is {fig}")
#     fig.add_trace(
#         go.Bar(
#             x=this_week_avg["day"],
#             y=this_week_avg["median_orders_sum_per_user"],
#             name="Заказы Средний Селлер бота",
#             # marker_color='lightslategrey',
#             text=this_week_avg["median_orders_sum_per_user"].round(1),
#             marker=dict(
#                 color="orange",
#                 pattern=dict(shape="\\", fgcolor="white", bgcolor="orange"),
#             ),
#         ),
#         row=1,
#         col=1,
#     )
#     # logger.info(f"fig after adding traces")

#     fig.add_trace(
#         go.Bar(
#             x=this_week["day"],
#             y=this_week["orders_sum_rub"],
#             name="Заказы Ваш кабинет",
#             marker_color="crimson",
#             text=this_week["orders_sum_rub"],
#         ),
#         row=1,
#         col=1,
#     )
#     fig.update_traces(
#         texttemplate="%{text:.4s}",
#         textposition="inside",
#         marker=dict(cornerradius="20%"),
#     )

#     fig.add_trace(
#         go.Scatter(
#             x=this_week_avg["day"],
#             y=(this_week_avg["median_drr"] * 100),
#             marker_color="orange",
#             name="ДРР Средний Селлер бота",
#             mode="lines+markers+text",
#             text=(this_week_avg["median_drr"] * 100).round(2).astype(str) + "%",
#             textposition="bottom left",
#             textfont=dict(size=12),
#             line=dict(width=3, dash="longdash"),
#         ),
#         row=2,
#         col=1,
#     )

#     fig.add_trace(
#         go.Scatter(
#             x=this_week["day"],
#             y=(this_week["sum"] / this_week["orders_sum_rub"] * 100),
#             marker=dict(color="orangered", size=6),
#             name="ДРР Ваш кабинет",
#             mode="lines+markers+text",
#             text=(this_week["sum"] / this_week["orders_sum_rub"] * 100)
#             .round(2)
#             .astype(str)
#             + "%",
#             textposition="bottom right",
#             textfont=dict(size=12),
#             line=dict(width=3),
#         ),
#         row=2,
#         col=1,
#     )

#     fig.add_trace(
#         go.Bar(
#             x=this_week_avg["day"],
#             y=this_week_avg["avg_orders_sum_per_user"],
#             name="Заказы Пользователь Автотаблиц",
#             text=this_week_avg["avg_orders_sum_per_user"].round(2),
#             marker=dict(
#                 color="yellowgreen",
#                 pattern=dict(shape="\\", fgcolor="white", bgcolor="yellowgreen"),
#             ),
#         ),
#         row=3,
#         col=1,
#     )

#     fig.add_trace(
#         go.Scatter(
#             x=this_week_avg["day"],
#             y=(this_week_avg["drr"] * 100),
#             marker=dict(color="dimgray", size=6),
#             name="ДРР Пользователь Автотаблиц",
#             mode="lines+markers+text",
#             text=(this_week_avg["drr"] * 100).round(2).astype(str) + "%",
#             textposition="bottom right",
#             textfont=dict(size=12),
#             line=dict(width=3),
#         ),
#         secondary_y=True,
#         row=3,
#         col=1,
#     )
#     # logger.info(f"fig after adding traces")
#     fig.update_yaxes(title_text="Сумма заказов", row=1, col=1)
#     fig.update_yaxes(title_text="ДРР (%)", row=2, col=1)
#     fig.update_yaxes(
#         title_text="Сумма заказов / ДРР (%)",
#         row=3,
#         col=1,
#         secondary_y=False,
#     )

#     qr = qrcode.QRCode(box_size=10, border=4)
#     qr.add_data("https://t.me/selleralarm_bot")
#     qr.make(fit=True)
#     img = qr.make_image(fill_color="black", back_color="white")

#     buffer = io.BytesIO()
#     img.save(buffer, format="PNG")
#     img_str = base64.b64encode(buffer.getvalue()).decode()

#     fig.add_layout_image(
#         dict(
#             source="data:image/png;base64," + img_str,
#             xref="paper",
#             yref="paper",
#             x=1.13,
#             y=0.132,
#             sizex=0.2,
#             sizey=0.2,
#             xanchor="center",
#             yanchor="middle",
#             layer="above",
#         )
#     )

#     fig.add_annotation(
#         dict(
#             x=1.13,
#             y=0.298,
#             xref="paper",
#             yref="paper",
#             text="Средние показатели<br>пользователя 📊Авто-таблиц!<br>Кстати, они уже доступны <br>в боте! @selleralarm_bot",
#             showarrow=False,
#             font=dict(
#                 family="Montserrat, sans-serif",
#                 size=20,
#             ),
#             align="center",
#             xanchor="center",
#             yanchor="top",
#             borderwidth=1,
#             borderpad=4,
#             opacity=0.9,
#         )
#     )

#     current_date = datetime.now().strftime("%d/%m/%Y")
#     # logger.info(f"current date is {current_date}")
#     fig.update_layout(
#         height=1280,  # Увеличиваем высоту графика
#         width=1280,  # Уменьшаем ширину графика
#         title=dict(
#             text=f"Сравните свои показатели с показателями других селлеров за текущую неделю! Дата:{current_date}"
#         ),
#         margin=dict(t=50, b=10),  # Уменьшаем отступ сверху и снизу
#         bargap=0.1,  # gap between bars of adjacent location coordinates.
#         bargroupgap=0.05,  # gap between bars of the same location coordinate.
#     )

#     return fig


import pandas as pd
import matplotlib
matplotlib.use("Agg")  # <-- отключает GUI, включает off-screen rendering
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import qrcode
import io
import base64
from datetime import datetime, timedelta


def generate_daily_statistics(df): # надо переписать для daily через matplotlib




    ## это всё через plotly!!! надо переписать на matplotlib
    df["date"] = pd.to_datetime(df["date"])
    # df["date"] = pd.to_datetime(df["date"])

    # Добавить это:
    numeric_columns = ["orders_sum_rub", "sum", "cliks", "views"]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    latest_date = df["date"].max()
    this_week = df[df["date"] > latest_date - timedelta(days=7)].copy()
    last_week = df[(df["date"] <= latest_date - timedelta(days=7)) & (df["date"] > latest_date - timedelta(days=14))].copy()

    this_week["week"] = "Текущая неделя"
    last_week["week"] = "Прошлая неделя"

    ordered_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    ru_days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    day_map = dict(zip(ordered_days, ru_days))

    this_week["day"] = pd.Categorical(this_week["date"].dt.strftime("%A"), categories=ordered_days, ordered=True)
    last_week["day"] = pd.Categorical(last_week["date"].dt.strftime("%A"), categories=ordered_days, ordered=True)

    this_week.sort_values("day", inplace=True)
    last_week.sort_values("day", inplace=True)

    x = [day_map[d] for d in ordered_days]

    fig = plt.figure(figsize=(12, 14))
    gs = gridspec.GridSpec(3, 2, width_ratios=[4, 1], height_ratios=[1, 1, 1])
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[2, 0])

    # --- Plot 1: Orders ---
    ax1.bar(x, last_week["orders_sum_rub"], label="Прошлая неделя", color="lightslategrey")
    ax1.bar(x, this_week["orders_sum_rub"], label="Текущая неделя", color="crimson", alpha=0.7)
    ax1.set_title("Сумма заказов")
    ax1.legend()
    ax1.set_ylabel("Сумма")

    # --- Plot 2: DRR ---
    drr_last = (last_week["sum"] / last_week["orders_sum_rub"] * 100).values
    drr_this = (this_week["sum"] / this_week["orders_sum_rub"] * 100).values
    ax2.plot(x, drr_last, label="ДРР Прошлая неделя", linestyle="--", color="gray")
    ax2.plot(x, drr_this, label="ДРР Текущая неделя", color="orangered")
    ax2.set_title("ДРР (%)")
    ax2.set_ylabel("%")
    ax2.legend()

    # --- Plot 3: CTR ---
    ctr_last = (last_week["cliks"] / last_week["views"] * 100).values
    ctr_this = (this_week["cliks"] / this_week["views"] * 100).values
    ax3.plot(x, ctr_last, label="CTR Прошлая неделя", linestyle="--", color="gray")
    ax3.plot(x, ctr_this, label="CTR Текущая неделя", color="orangered")
    ax3.set_title("CTR (%)")
    ax3.set_ylabel("%")
    ax3.legend()

    for ax in [ax1, ax2, ax3]:
        ax.set_xticks(range(len(x)))
        ax.set_xticklabels(x, fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.5)

    # --- QR Code ---
    qr = qrcode.QRCode(box_size=2, border=2)
    qr.add_data("https://t.me/selleralarm_bot")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    qr_img = plt.imread(buf)

    ax_qr = fig.add_subplot(gs[:, 1])
    ax_qr.imshow(qr_img)
    ax_qr.axis('off')
    ax_qr.set_title("@selleralarm_bot", fontsize=12)

    current_date = datetime.now().strftime("%d/%m/%Y")
    fig.suptitle(f"ООО Сигма Еком: Прошлая неделя VS Текущая неделя · {current_date}", fontsize=16)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.close(fig)
    return fig