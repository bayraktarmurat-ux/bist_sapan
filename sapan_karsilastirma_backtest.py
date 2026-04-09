import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Sapan Karsilastirma Backtest",
    page_icon="📊",
    layout="wide"
)

# ─── BIST100 LİSTESİ ────────────────────────────────────────────────────────
BIST100 = [
    "AKBNK","AKFEN","AKGRT","AKSA","AKSEN","AEFES","ALARK","ALBRK","ALFAS",
    "ANACM","ANSGR","ARCLK","ASELS","ASTOR","ASUZU","AYDEM","AYGAZ","BAGFS",
    "BERA","BIMAS","BRISA","BRYAT","BTCIM","BUCIM","CCOLA","CIMSA","CLEBI",
    "CRDFA","DOAS","DOHOL","ECILC","EGEEN","EKGYO","ENKAI","ENJSA","EREGL",
    "FENER","FROTO","GARAN","GESAN","GLBMD","GLYHO","GOODY","GUBRF","GWIND",
    "HALKB","HEKTS","HUNER","ISCTR","ISDMR","ISGYO","ISGSY","ISKUR","JANTS",
    "KCHOL","KERVT","KLGYO","KLNMA","KLRHO","KMPUR","KNFRT","KONTR","KONYA",
    "KOZAA","KOZAL","KRDMD","LOGO","MAVI","MGROS","ODAS","OTKAR","OYAKC",
    "PETKM","PGSUS","SAHOL","SASA","SISE","SKBNK","SMRTG","SOKM","TAVHL",
    "TCELL","THYAO","TKFEN","TOASO","TSKB","TTKOM","TTRAK","TUPRS","TURSG",
    "ULKER","VAKBN","VESTL","YKBNK","ZOREN","AGHOL","AGESA","DEVA","EKOS",
    "EMKEL","ENERY","EUPWR","FLAP","KARSN","KAREL",
]

# ─── YARDIMCI ───────────────────────────────────────────────────────────────
def sq(s):
    if hasattr(s, "squeeze"):
        s = s.squeeze()
    if hasattr(s, "iloc") and s.ndim == 2:
        s = s.iloc[:, 0]
    return s

def ema_s(ser, p):
    return sq(ser).ewm(span=p, adjust=False).mean()

def atr_h(df, p=14):
    c = sq(df["Close"]); h = sq(df["High"]); l = sq(df["Low"])
    tr = pd.concat([h-l, (h-c.shift(1)).abs(), (l-c.shift(1)).abs()], axis=1).max(axis=1)
    return tr.ewm(span=p, adjust=False).mean()

def stoch_h(df, k=5, d=3, sm=3):
    h = sq(df["High"]); l = sq(df["Low"]); c = sq(df["Close"])
    sk = 100*(c - l.rolling(k).min()) / (h.rolling(k).max() - l.rolling(k).min() + 1e-10)
    return sk.rolling(d).mean()

def macd_h(c, h=50, y=100, s=9):
    c = sq(c)
    m = c.ewm(span=h, adjust=False).mean() - c.ewm(span=y, adjust=False).mean()
    return m, m.ewm(span=s, adjust=False).mean()

def ema_dok(low, high, e20, e50, e100, e200, tol):
    for ev in [e20, e50, e100, e200]:
        if pd.isna(ev): continue
        if low <= ev*(1+tol) and high >= ev*(1-tol):
            return True
    return False

def higher_low_k(df, idx, lb=30):
    if idx < 2: return True
    rl = float(df["Low"].iloc[idx])
    sub = df["Low"].iloc[max(0, idx-lb):idx]
    if len(sub) == 0: return True
    if rl >= float(sub.min()): return True
    for col in ["EMA100","EMA200"]:
        if col in df.columns:
            ev = float(df[col].iloc[idx])
            if not pd.isna(ev) and rl <= ev*1.02:
                return True
    return False

# ─── VERİ ÇEKME ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def veri_cek(sembol, yil_bas=2022):
    try:
        df = yf.download(sembol+".IS", start=f"{yil_bas}-01-01",
                         interval="1d", progress=False, auto_adjust=True)
        if df.empty or len(df) < 100: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df[["Open","High","Low","Close","Volume"]].dropna()
        for col in df.columns:
            df[col] = sq(df[col])
        return df
    except Exception:
        return None

def ind_ekle(df):
    df = df.copy()
    c = df["Close"]
    df["EMA20"]  = ema_s(c, 20)
    df["EMA50"]  = ema_s(c, 50)
    df["EMA100"] = ema_s(c, 100)
    df["EMA200"] = ema_s(c, 200)
    df["ATR"]    = atr_h(df, 14)
    df["STOCH_K"]= stoch_h(df, 5, 3, 3)
    df["MACD"], _= macd_h(c, 50, 100, 9)
    df.dropna(subset=["EMA200","ATR","STOCH_K","MACD"], inplace=True)
    return df.reset_index()

# ─── SİNYAL TESPİT ──────────────────────────────────────────────────────────
def sinyalleri_bul(df, ema_tol):
    bulunanlar = []
    for i in range(2, len(df)):
        son = df.iloc[i]; onc = df.iloc[i-1]; iki = df.iloc[i-2]

        # 1. EMA zinciri
        if not (float(son["EMA20"]) > float(son["EMA50"]) >
                float(son["EMA100"]) > float(son["EMA200"])):
            continue
        # 2. Stoch < 30
        if float(onc["STOCH_K"]) >= 30: continue
        # 3. MACD
        mv = df["MACD"].iloc[max(0,i-6):i]
        if float(son["MACD"]) <= 0 and (mv < 0).sum() >= 5: continue
        # 4. Onay mumu yesil
        if float(son["Close"]) <= float(son["Open"]): continue
        # 5. Onay mumu high kirdi
        if float(son["Close"]) <= float(onc["High"]): continue
        # 6. EMA dokunusu
        if not ema_dok(float(onc["Low"]), float(onc["High"]),
                       float(onc["EMA20"]), float(onc["EMA50"]),
                       float(onc["EMA100"]), float(onc["EMA200"]), ema_tol):
            continue
        # 7. Higher low
        if not higher_low_k(df, i-1): continue

        bulunanlar.append({
            "idx"          : i,
            "reversal_high": float(onc["High"]),
            "onay_open"    : float(son["Open"]),
            "atr"          : float(son["ATR"]),
        })
    return bulunanlar

# ─── İŞLEM SİMÜLASYONU ──────────────────────────────────────────────────────
def islem_sim(df, sin, atr_kat, rr_kat, trail_kat, giris_tipi, stop_tipi, max_gun=30):
    giris = sin["reversal_high"] if giris_tipi == "high" else sin["onay_open"]
    atr   = sin["atr"]
    stop0 = giris - atr_kat * atr
    bir_r = giris - stop0
    if bir_r <= 0: return None
    hedef = giris + rr_kat * bir_r

    baslangic = sin["idx"] + 1
    if baslangic >= len(df): return None

    mevcut_stop = stop0
    kap_fiyat = kap_neden = None

    for g in range(baslangic, min(baslangic + max_gun, len(df))):
        row = df.iloc[g]
        g_low  = float(row["Low"])
        g_high = float(row["High"])
        g_kap  = float(row["Close"])
        g_atr  = float(row["ATR"])

        # Trailing stop guncelle
        if stop_tipi == "trailing":
            ys = g_kap - trail_kat * g_atr
            if ys > mevcut_stop:
                mevcut_stop = ys

        # Stop tetiklendi
        if g_low <= mevcut_stop:
            kap_fiyat = mevcut_stop
            kap_neden = "stop"
            break

        # Sabit hedef
        if stop_tipi == "sabit" and g_high >= hedef:
            kap_fiyat = hedef
            kap_neden = "hedef"
            break

    if kap_fiyat is None:
        son_g = min(baslangic + max_gun - 1, len(df)-1)
        kap_fiyat = float(df.iloc[son_g]["Close"])
        kap_neden = "zaman"

    kar_pct = (kap_fiyat - giris) / giris * 100
    return {
        "kar_pct" : kar_pct,
        "kazandi" : kap_fiyat > giris,
        "neden"   : kap_neden,
        "bir_r"   : bir_r,
    }

# ─── KOMBİNASYON BACKTEST ───────────────────────────────────────────────────
def kombin_backtest(tum_veri, ema_tol, atr_kat, rr_kat,
                    trail_kat, giris_tipi, stop_tipi, max_gun):
    islemler = []
    for sembol, df in tum_veri.items():
        if df is None or len(df) < 50: continue
        for sin in sinyalleri_bul(df, ema_tol):
            r = islem_sim(df, sin, atr_kat, rr_kat, trail_kat,
                          giris_tipi, stop_tipi, max_gun)
            if r: islemler.append(r)

    if not islemler: return None
    df_i = pd.DataFrame(islemler)
    kaz  = df_i[df_i["kazandi"]]
    kay  = df_i[~df_i["kazandi"]]
    n    = len(df_i)
    wr   = len(kaz)/n*100 if n > 0 else 0
    ok   = kaz["kar_pct"].mean() if len(kaz) > 0 else 0
    ol   = kay["kar_pct"].mean() if len(kay) > 0 else 0
    exp  = (wr/100*ok + (1-wr/100)*ol) if n > 0 else 0
    net  = df_i["kar_pct"].sum()
    ort  = df_i["kar_pct"].mean()

    # Max drawdown
    kum = (1 + df_i["kar_pct"]/100).cumprod()
    mdd = ((kum - kum.cummax()) / kum.cummax() * 100).min()

    return dict(n=n, win_rate=round(wr,1), net_getiri=round(net,1),
                ort_getiri=round(ort,2), expectancy=round(exp,2),
                max_drawdown=round(mdd,1), ort_kazanc=round(ok,2),
                ort_kayip=round(ol,2))

# ─── ISIL HARİTASI ──────────────────────────────────────────────────────────
def isi_harita(df_s, metrik, baslik, col_key):
    if df_s.empty: return
    if len(df_s["atr_kat"].unique()) < 2 or len(df_s["rr_kat"].unique()) < 2:
        st.dataframe(df_s[["atr_kat","rr_kat",metrik]], use_container_width=True)
        return
    pivot = df_s.pivot_table(index="atr_kat", columns="rr_kat",
                              values=metrik, aggfunc="mean")
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=[f"R:R {c}" for c in pivot.columns],
        y=[f"ATR {r}" for r in pivot.index],
        colorscale="RdYlGn",
        text=[[f"{v:.1f}" if pd.notna(v) else "" for v in row]
              for row in pivot.values],
        texttemplate="%{text}",
        textfont={"size":11},
        showscale=True,
        colorbar=dict(thickness=12, len=0.8),
        hovertemplate="ATR:%{y}<br>R:R:%{x}<br>Deger:%{z:.2f}<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text=baslik, font=dict(size=12)),
        height=260, margin=dict(l=5,r=5,t=35,b=5),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=10),
    )
    st.plotly_chart(fig, use_container_width=True, key=col_key)

# ─── SENARYO SEKME ──────────────────────────────────────────────────────────
def senaryo_tab(kod, rows, rr_alan_adi):
    if not rows:
        st.warning("Bu senaryo icin sonuc yok.")
        return
    df_s = pd.DataFrame(rows).sort_values("net_getiri", ascending=False)

    # En iyi 3
    st.markdown("##### En iyi 3 kombinasyon")
    cols_g = [c for c in ["ema_tol","atr_kat","rr_kat","n","win_rate",
                           "net_getiri","ort_getiri","expectancy","max_drawdown"]
              if c in df_s.columns]
    st.dataframe(
        df_s[cols_g].head(3).rename(columns={
            "ema_tol":"EMA%","atr_kat":"ATR","rr_kat":rr_alan_adi,
            "n":"N","win_rate":"Win%","net_getiri":"Net%",
            "ort_getiri":"Ort%","expectancy":"Exp%","max_drawdown":"MaxDD%"
        }),
        use_container_width=True, hide_index=True
    )

    # EMA filtresi
    ema_vals = sorted(df_s["ema_tol"].unique())
    if len(ema_vals) > 1:
        sel_ema = st.selectbox("EMA toleransi", ema_vals, key=f"ema_{kod}")
        df_f = df_s[df_s["ema_tol"] == sel_ema]
    else:
        df_f = df_s

    # Isil haritalar — 2x2 grid
    c1, c2 = st.columns(2)
    with c1:
        isi_harita(df_f, "net_getiri",   "Net Getiri %",   f"net_{kod}")
        isi_harita(df_f, "expectancy",   "Expectancy %",   f"exp_{kod}")
    with c2:
        isi_harita(df_f, "win_rate",     "Win Rate %",     f"wr_{kod}")
        isi_harita(df_f, "max_drawdown", "Max Drawdown %", f"dd_{kod}")

    # Tam tablo + CSV
    with st.expander("Tum kombinasyonlar"):
        st.dataframe(
            df_s[cols_g].rename(columns={
                "ema_tol":"EMA%","atr_kat":"ATR","rr_kat":rr_alan_adi,
                "n":"N","win_rate":"Win%","net_getiri":"Net%",
                "ort_getiri":"Ort%","expectancy":"Exp%","max_drawdown":"MaxDD%"
            }),
            use_container_width=True, hide_index=True
        )
    csv = df_s.to_csv(index=False).encode("utf-8-sig")
    st.download_button(f"CSV — Senaryo {kod}", csv,
                       f"sapan_sn_{kod}.csv", "text/csv", key=f"csv_{kod}")

# ─── MAIN ───────────────────────────────────────────────────────────────────
def main():
    st.title("📊 Sapan — 4 Senaryo Karsilastirma Backtest")
    st.caption(
        "**A** High+Sabit  |  **B** Acilis+Sabit  |  "
        "**C** High+Trailing  |  **D** Acilis+Trailing"
    )

    # ── Sidebar ───────────────────────────────────────────────────────────
    with st.sidebar:
        st.title("Parametreler")
        yil_bas = st.selectbox("Baslangic yili", [2021, 2022, 2023], index=1)
        max_gun = st.slider("Zaman stopu (gun)", 10, 60, 30, 5)

        st.markdown("### EMA toleransi (%)")
        ema_sec = st.multiselect("EMA tol", [1, 2, 3], default=[2])

        st.markdown("### ATR katsayisi (ilk stop)")
        atr_sec = st.multiselect("ATR", [1.0,1.5,2.0,2.5,3.0], default=[1.0,1.5,2.0,2.5])

        st.markdown("### R:R orani (sabit stop — A ve B)")
        rr_sec  = st.multiselect("R:R", [1.0,1.5,2.0,2.5,3.0,3.5,4.0],
                                 default=[1.0,1.5,2.0,2.5,3.0])

        st.markdown("### Trailing ATR katsayisi (C ve D)")
        tr_sec  = st.multiselect("Trail ATR", [0.5,1.0,1.5,2.0,2.5,3.0],
                                 default=[1.0,1.5,2.0,2.5])

        liste_sec = st.radio("Hisse listesi",
                             ["BIST100 (tumu)", "Ilk 50 hisse"])
        hisseler  = BIST100 if "tumu" in liste_sec else BIST100[:50]

    if not ema_sec or not atr_sec or not rr_sec or not tr_sec:
        st.warning("Tum parametrelerden en az birer secim yapin.")
        return

    sn_a = len(ema_sec)*len(atr_sec)*len(rr_sec)
    sn_c = len(ema_sec)*len(atr_sec)*len(tr_sec)
    st.info(
        f"Sabit senaryo basina **{sn_a}** kombinasyon  |  "
        f"Trailing senaryo basina **{sn_c}** kombinasyon  |  "
        f"**{len(hisseler)}** hisse"
    )

    # ── Bilgi tablosu ─────────────────────────────────────────────────────
    with st.expander("Senaryolar hakkinda"):
        st.markdown("""
| Senaryo | Giris | Stop | Not |
|---|---|---|---|
| **A** | Donus mumunun high'i | Sabit ATR×katsayi | Mevcut strateji — teorik |
| **B** | Ertesi gun acilis | Sabit ATR×katsayi | Gercekci (slippage dahil) |
| **C** | Donus mumunun high'i | Trailing ATR | Teorik giris + trend takibi |
| **D** | Ertesi gun acilis | Trailing ATR | Tam gercekci + trend takibi |

Trailing stop: her gun `stop = kapanis - ATR × trailing_katsayi` hesaplanir.
Stop sadece yukari gider. Trend tersine donunce tetiklenir.
Zaman stopu her senaryoda ayni (varsayilan 30 gun).
        """)

    # ── Baslat ────────────────────────────────────────────────────────────
    if st.button("🚀 Backtesti Baslat", type="primary", use_container_width=True):

        # Veri cek
        with st.status("Veriler cekiliyor...", expanded=True) as status:
            tum_veri = {}
            for i, sem in enumerate(hisseler):
                st.write(f"{sem} ({i+1}/{len(hisseler)})")
                df_raw = veri_cek(sem, yil_bas)
                if df_raw is not None:
                    tum_veri[sem] = ind_ekle(df_raw)
            status.update(label=f"{len(tum_veri)}/{len(hisseler)} hisse hazir.",
                          state="complete")

        # Kombinasyon dongusu
        sonuclar = {"A":[], "B":[], "C":[], "D":[]}

        toplam_sabit   = sn_a
        toplam_trail   = sn_c
        prog_s = st.progress(0, text="Sabit stop kombinasyonlari...")
        adim   = 0
        for et in ema_sec:
            for ak in atr_sec:
                for rk in rr_sec:
                    adim += 1
                    prog_s.progress(adim/toplam_sabit,
                        text=f"Sabit | EMA:{et}% ATR:{ak} R:R:{rk} ({adim}/{toplam_sabit})")
                    for giris, kod in [("high","A"), ("acilis","B")]:
                        r = kombin_backtest(tum_veri, et/100, ak, rk,
                                            None, giris, "sabit", max_gun)
                        if r:
                            r.update({"ema_tol":et,"atr_kat":ak,"rr_kat":rk})
                            sonuclar[kod].append(r)
        prog_s.empty()

        prog_t = st.progress(0, text="Trailing stop kombinasyonlari...")
        adim   = 0
        for et in ema_sec:
            for ak in atr_sec:
                for tk in tr_sec:
                    adim += 1
                    prog_t.progress(adim/toplam_trail,
                        text=f"Trailing | EMA:{et}% ATR:{ak} Trail:{tk} ({adim}/{toplam_trail})")
                    for giris, kod in [("high","C"), ("acilis","D")]:
                        r = kombin_backtest(tum_veri, et/100, ak, 0,
                                            tk, giris, "trailing", max_gun)
                        if r:
                            r.update({"ema_tol":et,"atr_kat":ak,"rr_kat":tk})
                            sonuclar[kod].append(r)
        prog_t.empty()

        st.session_state["sonuclar"] = sonuclar
        st.success("Backtest tamamlandi!")

    if "sonuclar" not in st.session_state:
        return

    sonuclar = st.session_state["sonuclar"]
    RENK     = {"A":"#3b82f6","B":"#10b981","C":"#f59e0b","D":"#ef4444"}
    ISIM     = {
        "A":"A — High + Sabit stop",
        "B":"B — Acilis + Sabit stop",
        "C":"C — High + Trailing stop",
        "D":"D — Acilis + Trailing stop",
    }

    # ── Özet bar chart ────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## Ozet — En iyi kombinasyon, her senaryo")

    ozet = []
    for kod in ["A","B","C","D"]:
        rows = sonuclar[kod]
        if not rows: continue
        df_s = pd.DataFrame(rows)
        best = df_s.loc[df_s["net_getiri"].idxmax()]
        ozet.append({
            "Senaryo"   : ISIM[kod],
            "Net %"     : best["net_getiri"],
            "Win %"     : best["win_rate"],
            "Exp %"     : best["expectancy"],
            "MaxDD %"   : best["max_drawdown"],
            "N islem"   : int(best["n"]),
            "ATR"       : best["atr_kat"],
            "R:R/Trail" : best["rr_kat"],
            "EMA Tol %" : best["ema_tol"],
        })

    if ozet:
        df_oz = pd.DataFrame(ozet)
        st.dataframe(df_oz, use_container_width=True, hide_index=True)

        fig_bar = go.Figure()
        for row in ozet:
            kod = list(ISIM.keys())[[v for v in ISIM.values()].index(row["Senaryo"])]
            fig_bar.add_trace(go.Bar(
                name=row["Senaryo"], x=[row["Senaryo"][:2]],
                y=[row["Net %"]], marker_color=RENK[kod],
                text=[f"{row['Net %']:.1f}%"], textposition="outside",
            ))
        fig_bar.update_layout(
            title="En iyi kombinasyonun net getirisi",
            height=320, showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10,r=10,t=40,b=10), yaxis_title="Net Getiri %",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── 4 sekme ───────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## Senaryo Detaylari")

    tab_a, tab_b, tab_c, tab_d = st.tabs([
        "A — High + Sabit", "B — Acilis + Sabit",
        "C — High + Trailing", "D — Acilis + Trailing",
    ])
    with tab_a: senaryo_tab("A", sonuclar["A"], "R:R")
    with tab_b: senaryo_tab("B", sonuclar["B"], "R:R")
    with tab_c: senaryo_tab("C", sonuclar["C"], "Trail ATR")
    with tab_d: senaryo_tab("D", sonuclar["D"], "Trail ATR")

    # ── Capraz karsilastirma ──────────────────────────────────────────────
    st.markdown("---")
    st.markdown("## Capraz Karsilastirma — ATR katsayisina gore")

    metrik = st.selectbox("Metrik", [
        "net_getiri","win_rate","expectancy","max_drawdown","ort_getiri"
    ], format_func=lambda x: {
        "net_getiri":"Net Getiri %","win_rate":"Win Rate %",
        "expectancy":"Expectancy %","max_drawdown":"Max Drawdown %",
        "ort_getiri":"Ort Getiri %"
    }[x])

    fig_cx = go.Figure()
    for kod in ["A","B","C","D"]:
        rows = sonuclar[kod]
        if not rows: continue
        df_s = pd.DataFrame(rows)
        grp  = df_s.groupby("atr_kat")[metrik].mean().reset_index()
        fig_cx.add_trace(go.Scatter(
            x=grp["atr_kat"], y=grp[metrik],
            name=ISIM[kod], mode="lines+markers",
            line=dict(color=RENK[kod], width=2), marker=dict(size=7),
        ))
    fig_cx.update_layout(
        title=f"ATR katsayisina gore ortalama {metrik}",
        xaxis_title="ATR Katsayisi", yaxis_title=metrik, height=380,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10,r=10,t=40,b=10),
        legend=dict(orientation="h", y=-0.25),
    )
    st.plotly_chart(fig_cx, use_container_width=True)

    st.markdown("---")
    st.caption("Bu analiz yatirim tavsiyesi degildir.")

if __name__ == "__main__":
    main()
