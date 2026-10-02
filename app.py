import os

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Analisis Bahan Tagih C0 & C1 FIFGROUP Cabang Rungkut 3 Bulan Terakhir",
    page_icon="📊",
    layout="wide"
)

# Letakkan file logo (logo_fifgroup.png) di folder yang sama dengan app.py
LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_fifgroup.png")

# Styling ringan: tampilan terang & bersih
st.markdown(
    """
    <style>
    /* Paksa tema terang walau Streamlit/OS memakai mode gelap */
    :root {color-scheme: light;}
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
    }
    [data-testid="stSidebar"], [data-testid="stSidebar"] > div {
        background-color: #F1F5F9 !important;
    }
    .stApp p, .stApp span, .stApp label, .stApp li,
    .stApp h1, .stApp h2, .stApp h3, .stApp h4,
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"],
    [data-testid="stCaptionContainer"] {
        color: #0F172A !important;
    }
    [data-testid="stCaptionContainer"] {color: #64748B !important;}
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
        background-color: #FFFFFF !important;
        border-color: #CBD5E1 !important;
    }
    .block-container {padding-top: 2rem; max-width: 1300px;}
    [data-testid="stMetricValue"] {font-size: 1.45rem;}
    /* Angka Rupiah ditampilkan penuh, tidak dipotong dengan "..." */
    [data-testid="stMetricValue"], [data-testid="stMetricValue"] div,
    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] div, [data-testid="stMetricLabel"] p {
        overflow: visible !important;
        text-overflow: clip !important;
        white-space: normal !important;
        word-break: break-word;
    }
    [data-testid="stMetric"] {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 14px 16px;
    }
    h1, h2, h3 {color: #0F172A;}
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# HEADER + LOGO
# ============================================================
logo_col, title_col = st.columns([1, 6], vertical_alignment="center")

with logo_col:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=130)
    else:
        st.markdown("**FIFGROUP**  \n*member of ASTRA*")

with title_col:
    st.title("Analisis Pelunasan, Pickup, Rollback, Rolling & Settle")
    st.caption(
        "Dashboard interaktif C0 & C1 per produk (MMU, MPF, NMC, REFI) berdasarkan data B7, B8, dan B9. "
        "Seluruh amount dalam Rupiah (Sum of PKK_AW)."
    )

if os.path.exists(LOGO_PATH):
    st.sidebar.image(LOGO_PATH, width=90)

# ============================================================
# DATA (dari pivot, urutan nilai: Pelunasan, Pickup, Rollback, Rolling, Settle)
# Sel kosong pada pivot = 0
# ============================================================
STATUSES = ["Pelunasan", "Pickup", "Rollback", "Rolling", "Settle"]
PCT_STATUSES = ["Pelunasan", "Pickup", "Rollback", "Rolling", "Settle"]
PERIODES = ["B7", "B8", "B9"]
PRODUKS = ["MMU", "MPF", "NMC", "REFI"]

RAW = {
    "B7": {
        "C0": {
            "MMU":  [1159739, 0, 29669545, 26467303, 633912841],
            "MPF":  [476963, 0, 0, 24254195, 88675133],
            "NMC":  [122517847, 54072540, 131082405, 1270541060, 12724573903],
            "REFI": [382825727, 41585152, 33019339, 1518570726, 10785695979],
        },
        "C1": {
            "MMU":  [1232420, 0, 5291528, 5090449, 204810345],
            "MPF":  [1485158, 0, 1882552, 4608982, 28168177],
            "NMC":  [88793560, 13363194, 471509958, 581412431, 4825829831],
            "REFI": [277960721, 66162280, 687498801, 595342578, 4909343577],
        },
    },
    "B8": {
        "C0": {
            "MMU":  [5149791, 0, 0, 18079718, 703270515],
            "MPF":  [800785, 0, 0, 43975524, 98519099],
            "NMC":  [48824481, 46439214, 48215918, 1407791309, 12225288497],
            "REFI": [290267683, 7664836, 134145413, 1808162150, 10661772426],
        },
        "C1": {
            "MMU":  [26811866, 0, 24539229, 24463945, 215193769],
            "MPF":  [986433, 0, 3054521, 23221340, 20248801],
            "NMC":  [81774639, 36785899, 528453531, 611134607, 4687280557],
            "REFI": [273811872, 34629316, 356654616, 737942117, 4696311623],
        },
    },
    "B9": {
        "C0": {
            "MMU":  [48924153, 0, 0, 34253213, 653269439],
            "MPF":  [585525, 0, 0, 16170206, 70354842],
            "NMC":  [120637905, 21281746, 95184210, 918852174, 12290607244],
            "REFI": [338250658, 43217027, 153923804, 1404066059, 10980044223],
        },
        "C1": {
            "MMU":  [0, 0, 18079718, 28838308, 186847096],
            "MPF":  [844455, 0, 12309544, 23029732, 36186768],
            "NMC":  [77031566, 12549843, 591876006, 606458618, 4575373123],
            "REFI": [308888383, 48571046, 450646038, 678902571, 4686014618],
        },
    },
}

rows = []
for periode_k, groups_k in RAW.items():
    for kel_k, prods_k in groups_k.items():
        for prod_k, vals in prods_k.items():
            rows.append({"Periode": periode_k, "Kelompok": kel_k, "Produk": prod_k,
                         **dict(zip(STATUSES, vals))})
raw_df = pd.DataFrame(rows)
raw_df["Grand Total"] = raw_df[STATUSES].sum(axis=1)

# ============================================================
# FORMAT & STYLE
# ============================================================
def rupiah(value):
    return f"Rp {value:,.0f}".replace(",", ".")

def pct_fmt(value):
    return f"{value:.2f}".replace(".", ",") + "%"

COLORS_GROUP = {"C0": "#2563EB", "C1": "#F97316"}  # C0 biru, C1 oranye
COLORS_STATUS = ["#94A3B8", "#0EA5E9", "#EF4444", "#F59E0B", "#10B981"]
COLORS_PRODUK = {"MMU": "#2563EB", "MPF": "#10B981", "NMC": "#F59E0B", "REFI": "#8B5CF6"}

def style_fig(fig, pct=False, amount=False):
    """Terapkan tema terang yang konsisten pada semua grafik."""
    fig.update_layout(
        template="plotly_white",
        separators=",.",              # format Indonesia: 1.000.000,50
        legend_title_text="",
        margin=dict(t=40, b=20, l=10, r=10),
        font=dict(size=13, color="#1E293B"),
    )
    if pct:
        fig.update_yaxes(ticksuffix="%")
    if amount:
        fig.update_yaxes(tickformat=",.0f")
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    return fig

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.header("Filter")

periode = st.sidebar.multiselect("Pilih periode", PERIODES, default=PERIODES)
kelompok = st.sidebar.radio("Pilih kelompok", ["Semua", "C0", "C1"], index=0)
produk = st.sidebar.multiselect("Pilih produk", PRODUKS, default=PRODUKS)



if not periode or not produk:
    st.warning("Pilih minimal satu periode dan satu produk.")
    st.stop()

groups = ["C0", "C1"] if kelompok == "Semua" else [kelompok]

# ============================================================
# HITUNG PEMBAGI & PERSENTASE
# ============================================================
df = raw_df.copy()
df["Pembagi"] = df["Grand Total"]  # Grand Total C0 untuk C0, Grand Total C1 untuk C1

def aggregate(frame, by):
    """Jumlahkan amount & pembagi, lalu hitung persentase (bukan rata-rata persentase)."""
    g = frame.groupby(by, as_index=False)[STATUSES + ["Grand Total", "Pembagi"]].sum()
    for s in PCT_STATUSES:
        g[f"{s} %"] = g[s] / g["Pembagi"] * 100
    return g

fdf = df[
    df["Periode"].isin(periode)
    & df["Kelompok"].isin(groups)
    & df["Produk"].isin(produk)
].copy()



# ============================================================
# KPI PERSENTASE
# ============================================================
st.subheader("Ringkasan Persentase terhadap Grand Total per Bulan")

monthly = aggregate(fdf, ["Periode", "Kelompok"])
periods_sel = [p for p in PERIODES if p in periode]
# Rollback naik = kurang baik (merah), Settle naik = baik (hijau); Pelunasan, Pickup & Rolling netral
DELTA_COLOR = {"Pelunasan": "off", "Pickup": "off", "Rollback": "inverse", "Rolling": "off", "Settle": "normal"}

for i, p in enumerate(periods_sel):
    st.markdown(f"#### {p}")
    for g in groups:
        r = monthly[(monthly["Periode"] == p) & (monthly["Kelompok"] == g)].iloc[0]
        prev = None
        if i > 0:
            prev = monthly[
                (monthly["Periode"] == periods_sel[i - 1]) & (monthly["Kelompok"] == g)
            ].iloc[0]
        st.markdown(f"**{g}**")
        cols = st.columns(len(PCT_STATUSES))
        for c, s in zip(cols, PCT_STATUSES):
            delta = None
            if prev is not None:
                d = r[f"{s} %"] - prev[f"{s} %"]
                delta = f"{d:+.2f} poin".replace(".", ",")
            c.metric(
                s, pct_fmt(r[f"{s} %"]), delta=delta, delta_color=DELTA_COLOR[s],
                help=f"Amount {s} {g} {p}: {rupiah(r[s])}"
            )

st.caption(
    "Panah kecil = selisih terhadap bulan sebelumnya dalam poin persentase "
    "(Rollback naik berwarna merah, Settle naik berwarna hijau). Arahkan kursor ke angka untuk melihat amount-nya."
)

st.divider()

# ============================================================
# RINGKASAN PERSENTASE PER PRODUK PER BULAN
# ============================================================
st.subheader("Ringkasan Persentase per Produk per Bulan")

prod_month = aggregate(fdf, ["Periode", "Kelompok", "Produk"])
produk_sel = [x for x in PRODUKS if x in produk]

def metric_row(r, prev, g, p, label):
    """Satu baris 5 metric persentase (dengan selisih vs bulan sebelumnya bila ada)."""
    st.markdown(f"**{g}**")
    cols = st.columns(len(PCT_STATUSES))
    for c, status in zip(cols, PCT_STATUSES):
        delta = None
        if prev is not None:
            d = r[f"{status} %"] - prev[f"{status} %"]
            delta = f"{d:+.2f} poin".replace(".", ",")
        c.metric(
            status, pct_fmt(r[f"{status} %"]), delta=delta, delta_color=DELTA_COLOR[status],
            help=f"Amount {status} {label} {g} {p}: {rupiah(r[status])}"
        )

prod_tabs = st.tabs(produk_sel)
for tab, prod_name in zip(prod_tabs, produk_sel):
    with tab:
        for i, p in enumerate(periods_sel):
            st.markdown(f"#### {prod_name} - {p}")
            for g in groups:
                r = prod_month[
                    (prod_month["Periode"] == p) & (prod_month["Kelompok"] == g)
                    & (prod_month["Produk"] == prod_name)
                ].iloc[0]
                prev = None
                if i > 0:
                    prev = prod_month[
                        (prod_month["Periode"] == periods_sel[i - 1]) & (prod_month["Kelompok"] == g)
                        & (prod_month["Produk"] == prod_name)
                    ].iloc[0]
                metric_row(r, prev, g, p, prod_name)

st.caption(
    "Setiap produk dihitung terhadap Grand Total produk itu sendiri pada kelompok (C0 atau C1) dan bulan yang sama. "
    "Klik tab produk untuk berpindah antar MMU, MPF, NMC, dan REFI."
)

st.divider()

# ============================================================
# KPI AMOUNT
# ============================================================
st.subheader("Ringkasan Amount PKK_AW")

k = fdf[STATUSES + ["Grand Total"]].sum()
a1, a2, a3 = st.columns(3)
a1.metric("Grand Total", rupiah(k["Grand Total"]))
a2.metric("Pelunasan", rupiah(k["Pelunasan"]))
a3.metric("Pickup", rupiah(k["Pickup"]))

b1, b2, b3 = st.columns(3)
b1.metric("Rollback", rupiah(k["Rollback"]))
b2.metric("Rolling", rupiah(k["Rolling"]))
b3.metric("Settle", rupiah(k["Settle"]))

st.caption("Amount menggunakan nilai Sum of PKK_AW dalam Rupiah, sesuai filter periode, kelompok, dan produk.")

st.divider()

# ============================================================
# 1. PERSENTASE PER STATUS PER PERIODE
# ============================================================
st.subheader("1. Persentase Pelunasan, Pickup, Rollback, Rolling & Settle per Periode")

by_period = aggregate(fdf, ["Periode", "Kelompok"])
long_period = by_period.melt(
    id_vars=["Periode", "Kelompok"],
    value_vars=[f"{s} %" for s in PCT_STATUSES],
    var_name="Status",
    value_name="Persentase"
)
long_period["Status"] = long_period["Status"].str.replace(" %", "", regex=False)

fig_period = px.bar(
    long_period, x="Periode", y="Persentase", color="Kelompok",
    facet_col="Status", barmode="group", text="Persentase",
    color_discrete_map=COLORS_GROUP,
    category_orders={"Status": PCT_STATUSES, "Kelompok": ["C0", "C1"], "Periode": PERIODES},
    labels={"Persentase": "Persentase (%)"}
)
fig_period.update_traces(texttemplate="%{text:.2f}%", textposition="outside", cliponaxis=False)
fig_period.update_yaxes(matches=None, showticklabels=True)
fig_period.update_layout(height=460)
st.plotly_chart(style_fig(fig_period, pct=True), use_container_width=True)
st.caption("Skala sumbu Y tiap status dibuat terpisah agar status dengan persentase kecil (mis. Pickup) tetap terbaca.")

# ============================================================
# 2. PERSENTASE PER PRODUK
# ============================================================
st.subheader("2. Persentase per Produk")

status_prod = st.selectbox("Pilih status", PCT_STATUSES, index=1, key="status_prod")
col_prod = f"{status_prod} %"

prod_df = aggregate(fdf, ["Periode", "Kelompok", "Produk"])

fig_prod = px.bar(
    prod_df, x="Produk", y=col_prod, color="Kelompok",
    facet_col="Periode", barmode="group", text=col_prod,
    color_discrete_map=COLORS_GROUP,
    category_orders={"Produk": PRODUKS, "Kelompok": ["C0", "C1"], "Periode": PERIODES},
    labels={col_prod: f"{status_prod} (%)"}
)
fig_prod.update_traces(texttemplate="%{text:.2f}%", textposition="outside", cliponaxis=False)
fig_prod.update_layout(height=460)
st.plotly_chart(style_fig(fig_prod, pct=True), use_container_width=True)

# ============================================================
# 3. TREND PER PRODUK
# ============================================================
st.subheader("3. Trend Persentase per Produk")

status_trend = st.selectbox("Pilih indikator", PCT_STATUSES, index=1, key="status_trend")
col_trend = f"{status_trend} %"

fig_trend = px.line(
    prod_df, x="Periode", y=col_trend, color="Produk", line_dash="Kelompok",
    markers=True,
    color_discrete_map=COLORS_PRODUK,
    category_orders={"Produk": PRODUKS, "Kelompok": ["C0", "C1"], "Periode": PERIODES},
    labels={col_trend: f"{status_trend} (%)"}
)
fig_trend.update_layout(height=440)
st.plotly_chart(style_fig(fig_trend, pct=True), use_container_width=True)
st.caption("Garis putus-putus = C1, garis penuh = C0.")

# ============================================================
# 4. AMOUNT PER STATUS
# ============================================================
st.subheader("4. Komposisi Amount PKK_AW per Status")

amount_long = (
    aggregate(fdf, ["Periode", "Kelompok"])
    .melt(id_vars=["Periode", "Kelompok"], value_vars=STATUSES,
          var_name="Status", value_name="Amount")
)

fig_amount = px.bar(
    amount_long, x="Periode", y="Amount", color="Status",
    facet_col="Kelompok", barmode="stack",
    color_discrete_sequence=COLORS_STATUS,
    category_orders={"Status": STATUSES, "Kelompok": ["C0", "C1"], "Periode": PERIODES},
    labels={"Amount": "PKK_AW (Rp)"}
)
st.plotly_chart(style_fig(fig_amount, amount=True), use_container_width=True)

# ============================================================
# 5. TABEL PERSENTASE
# ============================================================
st.subheader("5. Tabel Persentase per Produk")

pct_table = prod_df[["Periode", "Kelompok", "Produk"] + [f"{s} %" for s in PCT_STATUSES]].copy()
for s in PCT_STATUSES:
    pct_table[f"{s} %"] = pct_table[f"{s} %"].map(pct_fmt)
st.dataframe(pct_table, use_container_width=True, hide_index=True)

# ============================================================
# 6. DATA DETAIL (AMOUNT)
# ============================================================
st.subheader("6. Data Detail Amount")

detail_cols = ["Periode", "Kelompok", "Produk"] + STATUSES + ["Grand Total", "Pembagi"]
detail = fdf.sort_values(["Periode", "Kelompok", "Produk"])[detail_cols].copy()
for c in STATUSES + ["Grand Total", "Pembagi"]:
    detail[c] = detail[c].apply(rupiah)
amount_cfg = {
    c: st.column_config.TextColumn(c, width="medium")
    for c in STATUSES + ["Grand Total", "Pembagi"]
}
st.dataframe(detail, use_container_width=True, hide_index=True, column_config=amount_cfg)
st.caption("Kolom Pembagi = Grand Total kelompok (C0 atau C1) yang dipakai sebagai penyebut persentase.")

# ============================================================
# 7. INSIGHT
# ============================================================
st.subheader("7. Insight")

def fmt_delta(now, prev):
    d = now - prev
    arah = "naik" if d > 0 else "turun" if d < 0 else "tetap"
    return f"{arah} {abs(d):.2f}".replace(".", ",") + " poin persentase"

tot_p = aggregate(fdf, ["Periode", "Kelompok"])
periods_f = [p for p in PERIODES if p in periode]

st.markdown("### Sorotan")
for g in groups:
    sub = tot_p[tot_p["Kelompok"] == g]
    hi = sub.loc[sub["Rollback %"].idxmax()]
    lo = sub.loc[sub["Settle %"].idxmin()]
    st.write(
        f"• **{g}:** Rollback tertinggi pada **{hi['Periode']}** ({pct_fmt(hi['Rollback %'])}), "
        f"Settle terendah pada **{lo['Periode']}** ({pct_fmt(lo['Settle %'])})."
    )

st.markdown("### Per Periode")
for i, p in enumerate(periods_f):
    st.markdown(f"#### {p}")
    for g in groups:
        r = tot_p[(tot_p["Periode"] == p) & (tot_p["Kelompok"] == g)].iloc[0]
        st.write(
            f"**{g}:** "
            f"Pelunasan {pct_fmt(r['Pelunasan %'])} ({rupiah(r['Pelunasan'])}), "
            f"Pickup {pct_fmt(r['Pickup %'])} ({rupiah(r['Pickup'])}), "
            f"Rollback {pct_fmt(r['Rollback %'])} ({rupiah(r['Rollback'])}), "
            f"Rolling {pct_fmt(r['Rolling %'])} ({rupiah(r['Rolling'])}), "
            f"Settle {pct_fmt(r['Settle %'])} ({rupiah(r['Settle'])})."
        )

        sub = prod_df[(prod_df["Periode"] == p) & (prod_df["Kelompok"] == g)]
        top = sub.loc[sub["Rollback %"].idxmax()]
        if top["Rollback %"] > 0:
            st.write(
                f"• Rollback terbesar pada produk **{top['Produk']}**: "
                f"{pct_fmt(top['Rollback %'])} ({rupiah(top['Rollback'])})."
            )

        if i > 0:
            prev_p = periods_f[i - 1]
            pr = tot_p[(tot_p["Periode"] == prev_p) & (tot_p["Kelompok"] == g)].iloc[0]
            st.write(
                f"• Dibanding {prev_p}: Rollback {fmt_delta(r['Rollback %'], pr['Rollback %'])}, "
                f"Settle {fmt_delta(r['Settle %'], pr['Settle %'])}."
            )