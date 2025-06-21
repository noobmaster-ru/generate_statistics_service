# import pandas as pd
# from datetime import datetime, timedelta
# from plotly.subplots import make_subplots
# import plotly.graph_objects as go
# import qrcode
# import io
# import base64

# def generate_weekly_statistics(df):
#     df["date"] = pd.to_datetime(df["date"])

#     latest_date = df["date"].max()
#     this_week = df[df["date"] > latest_date - timedelta(days=7)]
#     last_week = df[(df["date"] <= latest_date - timedelta(days=7)) & (df["date"] > latest_date - timedelta(days=14))]

#     this_week = this_week.copy()
#     last_week = last_week.copy()
#     this_week["week"] = "Текущая неделя"
#     last_week["week"] = "Прошлая неделя"

#     this_week["day"] = this_week["date"].dt.strftime("%A")
#     last_week["day"] = last_week["date"].dt.strftime("%A")

#     # Правильный порядок дней
#     ordered_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
#     ru_days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

#     for df_ in [this_week, last_week]:
#         df_["day"] = pd.Categorical(df_["day"], categories=ordered_days, ordered=True)
#         df_.sort_values("day", inplace=True)

#     fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05)

#     # ===== 1. Bar: Заказы =====
#     fig.add_trace(
#         go.Bar(
#             x=last_week["day"],
#             y=last_week["orders_sum_rub"],
#             name="Заказы Прошлая неделя",
#             text=last_week["orders_sum_rub"],
#             marker=dict(
#                 color="lightslategrey",
#                 pattern=dict(shape="\\", fgcolor="white", bgcolor="lightslategrey"),
#             ),
#         ),
#         row=1, col=1,
#     )
#     fig.add_trace(
#         go.Bar(
#             x=this_week["day"],
#             y=this_week["orders_sum_rub"],
#             name="Заказы Текущая неделя",
#             marker_color="crimson",
#             text=this_week["orders_sum_rub"],
#         ),
#         row=1, col=1,
#     )
#     fig.update_traces(
#         selector=dict(type='bar'),
#         texttemplate="%{text}",
#         textposition="inside",
#     )

#     # ===== 2. Line: ДРР =====
#     fig.add_trace(
#         go.Scatter(
#             x=last_week["day"],
#             y=(last_week["sum"] / last_week["orders_sum_rub"]) * 100,
#             name="ДРР Прошлая неделя",
#             mode="lines+markers",
#             line=dict(width=3, dash="dash"),
#             marker=dict(color="dimgray"),
#         ),
#         row=2, col=1,
#     )
#     fig.add_trace(
#         go.Scatter(
#             x=this_week["day"],
#             y=(this_week["sum"] / this_week["orders_sum_rub"]) * 100,
#             name="ДРР Текущая неделя",
#             mode="lines+markers",
#             line=dict(width=3),
#             marker=dict(color="orangered"),
#         ),
#         row=2, col=1,
#     )

#     # ===== 3. Line: CTR =====
#     fig.add_trace(
#         go.Scatter(
#             x=last_week["day"],
#             y=(last_week["cliks"] / last_week["views"]) * 100,
#             name="CTR Прошлая неделя",
#             mode="lines+markers",
#             line=dict(width=3, dash="dash"),
#             marker=dict(color="dimgray"),
#         ),
#         row=3, col=1,
#     )
#     fig.add_trace(
#         go.Scatter(
#             x=this_week["day"],
#             y=(this_week["cliks"] / this_week["views"]) * 100,
#             name="CTR Текущая неделя",
#             mode="lines+markers",
#             line=dict(width=3),
#             marker=dict(color="orangered"),
#         ),
#         row=3, col=1,
#     )

#     # Подписи осей
#     fig.update_yaxes(title_text="Сумма заказов", row=1, col=1)
#     fig.update_yaxes(title_text="ДРР (%)", row=2, col=1)
#     fig.update_yaxes(title_text="CTR (%)", row=3, col=1)

#     # Настройки оси X (дни недели)
#     for row in [1, 2, 3]:
#         fig.update_xaxes(
#             row=row, col=1,
#             tickangle=0,
#             tickmode='array',
#             tickvals=ordered_days,
#             ticktext=ru_days,
#             tickfont=dict(size=14)
#         )

#     # ===== QR-код и аннотация =====
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
#             xref="paper", yref="paper",
#             x=1.45, y=0.03,
#             sizex=0.35, sizey=0.35,
#             xanchor="right", yanchor="bottom",
#             layer="above",
#         )
#     )

#     fig.add_annotation(
#         dict(
#             x=1.45, y=0.4,
#             xref="paper", yref="paper",
#             text="Введи <b>/avg_stats</b> в боте<br>и свои показатели<br>со средними по рынку<br>@selleralarm_bot",
#             showarrow=False,
#             font=dict(family="Montserrat", size=14),
#             align="center",
#             xanchor="right", yanchor="bottom",
#             borderwidth=1, borderpad=4, opacity=0.9,
#         )
#     )

#     # ===== Финальная настройка =====
#     cabinet_name = "ООО Сигма Еком"
#     current_date = datetime.now().strftime("%d/%m/%Y")
#     fig.update_layout(
#         height=1280,
#         width=1280,
#         title=dict(
#             text=f"{cabinet_name}: Прошлая неделя VS Текущая неделя · {current_date}",
#             x=0.5,
#             font=dict(size=16)
#         ),
#         margin=dict(t=60, b=40),
#         bargap=0.2,
#         bargroupgap=0.1,
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


def generate_weekly_statistics(df):
    df["date"] = pd.to_datetime(df["date"])

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