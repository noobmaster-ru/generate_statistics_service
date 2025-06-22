import pandas as pd
import matplotlib
matplotlib.use("Agg") 
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import qrcode
import io
from datetime import datetime, timedelta

def generate_daily_statistics(df_avg, df_weekly):
    df_avg["date"] = pd.to_datetime(df_avg["date"])
    latest_date_avg = df_avg["date"].max()
    this_week_avg = df_avg[df_avg["date"] > latest_date_avg - timedelta(days=7)].copy()
    this_week_avg["day"] = this_week_avg["date"].dt.strftime("%A")

    df_weekly["date"] = pd.to_datetime(df_weekly["date"])
    latest_date = df_weekly["date"].max()
    this_week = df_weekly[df_weekly["date"] > latest_date - timedelta(days=7)].copy()
    this_week["day"] = this_week["date"].dt.strftime("%A")

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    ru_days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    day_map = dict(zip(days, ru_days))

    this_week_avg["day"] = pd.Categorical(this_week_avg["day"], categories=days, ordered=True)
    this_week["day"] = pd.Categorical(this_week["day"], categories=days, ordered=True)
    this_week_avg.sort_values("day", inplace=True)
    this_week.sort_values("day", inplace=True)

    fig = plt.figure(figsize=(12, 16))
    gs = gridspec.GridSpec(3, 3, width_ratios=[1, 1, 1], height_ratios=[1, 1, 1])
    ax1 = fig.add_subplot(gs[0, :2])
    ax2 = fig.add_subplot(gs[1, :])
    ax3 = fig.add_subplot(gs[2, :])
    x = [day_map[d] for d in days]

    # ---  Orders ---
    ax1.bar(x, this_week_avg["median_orders_sum_per_user"], label="Средний селлер", color="orange", alpha=0.6)
    ax1.bar(x, this_week["orders_sum_rub"], label="Ваш кабинет", color="crimson", alpha=0.6)
    ax1.set_ylabel("Сумма заказов в млн. руб")
    ax1.set_title("Сравнение сумм заказов по дням")
    ax1.legend()

    # ---  DRR ---
    ax2.plot(x, this_week_avg["median_drr"] * 100, label="Средний селлер", linestyle="--", marker="o", color="orange")
    ax2.plot(x, (this_week["sum"] / this_week["orders_sum_rub"]) * 100, label="Ваш кабинет", marker="o", color="orangered")
    ax2.set_ylabel("ДРР (%)")
    ax2.set_title("Сравнение ДРР по дням")
    ax2.legend()

    #  ---  Orders &  DRR  autotables ---
    ax3.bar(x, this_week_avg["avg_orders_sum_per_user"], label="Пользователь Автотаблиц", color="yellowgreen", alpha=0.6)
    ax3.set_ylabel("Сумма заказов")
    ax3_twin = ax3.twinx()
    ax3_twin.plot(x, this_week_avg["drr"] * 100, label="ДРР Пользователь Автотаблиц", color="dimgray", marker="o")
    ax3_twin.set_ylabel("ДРР (%)")
    ax3.set_title("Пользователь Автотаблиц")
    ax3.legend(loc="upper left")
    ax3_twin.legend(loc="upper right")

    for ax in [ax1, ax2, ax3]:
        ax.set_xticks(range(len(x)))
        ax.set_xticklabels(x, fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.5)

    # QR-код
    qr = qrcode.QRCode(box_size=2, border=1)
    qr.add_data("https://t.me/selleralarm_bot")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    qr_img = plt.imread(buf)

    # grid in  [0,2]
    inner_gs = gridspec.GridSpecFromSubplotSpec(
        2, 1, 
        subplot_spec=gs[0, 2],
        height_ratios=[1, 6] 
    )

    # lower part: QR-code
    ax_qr = fig.add_subplot(inner_gs[1])
    ax_qr.imshow(qr_img)
    ax_qr.axis('off')

    # Upper part: text
    ax_text = fig.add_subplot(inner_gs[0])
    ax_text.axis('off')
    text_content = (
        "Введи в боте /avg_stats и \n"
        "сравни свои показатели\n"
        "со средним по рынку @selleralarm_bot"
    )
    ax_text.text(
        0.5, 0.5,  
        text_content,
        fontsize=14,
        ha='center',  
        va='center',
        linespacing=1.5
    )
    current_date = datetime.now().strftime("%d/%m/%Y")
    fig.suptitle(f"ООО Сигма Еком: Прошлая неделя VS Текущая неделя · {current_date}", fontsize=26)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.close(fig)
    return fig


def generate_weekly_statistics(df):
    df["date"] = pd.to_datetime(df["date"])

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

    fig = plt.figure(figsize=(12, 16))
    gs = gridspec.GridSpec(3, 3, width_ratios=[1, 1, 1], height_ratios=[1, 1, 1])
    ax1 = fig.add_subplot(gs[0, :2])
    ax2 = fig.add_subplot(gs[1, :])
    ax3 = fig.add_subplot(gs[2, :])

    # ---  Orders ---
    ax1.bar(x, last_week["orders_sum_rub"], label="Прошлая неделя", color="lightslategrey")
    ax1.bar(x, this_week["orders_sum_rub"], label="Текущая неделя", color="crimson", alpha=0.7)
    ax1.set_title("Сумма заказов")
    ax1.legend()
    ax1.set_ylabel("Сумма",rotation=0)

    # ---  DRR ---
    drr_last = (last_week["sum"] / last_week["orders_sum_rub"] * 100).values
    drr_this = (this_week["sum"] / this_week["orders_sum_rub"] * 100).values
    ax2.plot(x, drr_last, label="ДРР Прошлая неделя", linestyle="--", color="gray")
    ax2.plot(x, drr_this, label="ДРР Текущая неделя", color="orangered")
    ax2.set_title("ДРР в %")
    ax2.set_ylabel("%",rotation=0)
    ax2.legend()

    # --- CTR ---
    ctr_last = (last_week["cliks"] / last_week["views"] * 100).values
    ctr_this = (this_week["cliks"] / this_week["views"] * 100).values
    ax3.plot(x, ctr_last, label="CTR Прошлая неделя", linestyle="--", color="gray")
    ax3.plot(x, ctr_this, label="CTR Текущая неделя", color="orangered")
    ax3.set_title("CTR в % ")
    ax3.set_ylabel("%",rotation=0)
    ax3.legend()

    for ax in [ax1, ax2, ax3]:
        ax.set_xticks(range(len(x)))
        ax.set_xticklabels(x, fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.5)

    # --- QR-code ---
    qr = qrcode.QRCode(box_size=2, border=2)
    qr.add_data("https://t.me/selleralarm_bot")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    qr_img = plt.imread(buf)

    # grid in [0,2]
    inner_gs = gridspec.GridSpecFromSubplotSpec(
        2, 1,  
        subplot_spec=gs[0, 2],
        height_ratios=[1, 6] 
    )

    # lower part: QR-code
    ax_qr = fig.add_subplot(inner_gs[1])
    ax_qr.imshow(qr_img)
    ax_qr.axis('off')

    # upper part: text
    ax_text = fig.add_subplot(inner_gs[0])
    ax_text.axis('off')
    text_content = (
        "Введи в боте /avg_stats и \n"
        "сравни свои показатели\n"
        "со средним по рынку @selleralarm_bot"
    )
    ax_text.text(
        0.5, 0.5,  
        text_content,
        fontsize=14,
        ha='center',  
        va='center',
        linespacing=1.5
    )
    current_date = datetime.now().strftime("%d/%m/%Y")
    fig.suptitle(f"ООО Сигма Еком: Прошлая неделя VS Текущая неделя · {current_date}", fontsize=26)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.close(fig)
    return fig