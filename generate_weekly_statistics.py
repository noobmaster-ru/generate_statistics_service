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
    df["date"] = pd.to_datetime(df["date"])

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