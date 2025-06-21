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

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd
import qrcode
import io
from datetime import datetime, timedelta

def generate_daily_statistics(df_avg, df_weekly):
    # Подготовка данных
    df_avg["date"] = pd.to_datetime(df_avg["date"])
    latest_date_avg = df_avg["date"].max()
    this_week_avg = df_avg[df_avg["date"] > latest_date_avg - timedelta(days=7)].copy()
    this_week_avg["day"] = this_week_avg["date"].dt.strftime("%A")

    df_weekly["date"] = pd.to_datetime(df_weekly["date"])
    latest_date = df_weekly["date"].max()
    this_week = df_weekly[df_weekly["date"] > latest_date - timedelta(days=7)].copy()
    this_week["day"] = this_week["date"].dt.strftime("%A")

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    this_week_avg["day"] = pd.Categorical(this_week_avg["day"], categories=days, ordered=True)
    this_week["day"] = pd.Categorical(this_week["day"], categories=days, ordered=True)
    this_week_avg.sort_values("day", inplace=True)
    this_week.sort_values("day", inplace=True)

    fig = plt.figure(figsize=(12, 16))
    gs = gridspec.GridSpec(3, 1)

    # 1. Заказы
    ax1 = fig.add_subplot(gs[0])
    ax1.bar(this_week_avg["day"], this_week_avg["median_orders_sum_per_user"], label="Средний селлер", color="orange", alpha=0.6)
    ax1.bar(this_week["day"], this_week["orders_sum_rub"], label="Ваш кабинет", color="crimson", alpha=0.6)
    ax1.set_ylabel("Сумма заказов")
    ax1.set_title("Сравнение сумм заказов по дням")
    ax1.legend()

    # 2. ДРР
    ax2 = fig.add_subplot(gs[1])
    ax2.plot(this_week_avg["day"], this_week_avg["median_drr"] * 100, label="Средний селлер", linestyle="--", marker="o", color="orange")
    ax2.plot(this_week["day"], (this_week["sum"] / this_week["orders_sum_rub"]) * 100, label="Ваш кабинет", marker="o", color="orangered")
    ax2.set_ylabel("ДРР (%)")
    ax2.set_title("Сравнение ДРР по дням")
    ax2.legend()

    # 3. Заказы и ДРР Автотаблиц
    ax3 = fig.add_subplot(gs[2])
    ax3.bar(this_week_avg["day"], this_week_avg["avg_orders_sum_per_user"], label="Пользователь Автотаблиц", color="yellowgreen", alpha=0.6)
    ax3.set_ylabel("Сумма заказов")
    ax3_twin = ax3.twinx()
    ax3_twin.plot(this_week_avg["day"], this_week_avg["drr"] * 100, label="ДРР Пользователь Автотаблиц", color="dimgray", marker="o")
    ax3_twin.set_ylabel("ДРР (%)")
    ax3.set_title("Пользователь Автотаблиц")
    ax3.legend(loc="upper left")
    ax3_twin.legend(loc="upper right")

    # QR-код
    qr = qrcode.QRCode(box_size=2, border=1)
    qr.add_data("https://t.me/selleralarm_bot")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    qr_img = plt.imread(buf)
    fig.figimage(qr_img, xo=1050, yo=130)

    # Аннотация
    fig.text(0.8, 0.15,
             "Средние показатели\nпользователя Авто-таблиц!\nКстати, они уже доступны \nв боте! @selleralarm_bot",
             fontsize=10, ha="center", va="top", bbox=dict(facecolor='white', alpha=0.7, boxstyle='round'))

    fig.suptitle(
        f"Сравните свои показатели с показателями других селлеров за текущую неделю! Дата: {datetime.now().strftime('%d/%m/%Y')}",
        fontsize=14)

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    plt.close(fig)
    return fig