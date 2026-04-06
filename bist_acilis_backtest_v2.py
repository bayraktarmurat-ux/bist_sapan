import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import plotly.graph_objects as go
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="BIST Gerçekçi Backtest", layout="wide")
st.title("📈 MACD Histogram Reversal — Gerçekçi Portföy Backtest")
st.caption("Fixed Risk Sizing | Giriş: Ertesi Gün Open | Stop: ATR tabanlı | Pozisyon: Riske göre otomatik")

# ── Hisse Listesi ─────────────────────────────────────────────────────────────
BIST_HISSELER = [
    "AEFES","AGESA","AKBNK","AKFGY","AKGRT","AKSA","AKSEN","ALARK","ALBRK",
    "ALCAR","ALFAS","ALGYO","ALKIM","ALTNY","ANACM","ANELE","ANGEN","ANIM",
    "ANSGR","ARASE","ARCLK","ARDYZ","ARENA","ARSAN","ASELS","ASGYO","ASTOR",
    "ATAKP","ATATP","ATEKS","ATLAS","ATSYH","AVOD","AYCES","AYES","AYGAZ",
    "AZTEK","BAGFS","BAKAB","BALAT","BANVT","BERA","BFREN","BIENY","BIMAS",
    "BINHO","BIOEN","BIZIM","BLCYT","BMEKS","BMSTL","BOBET","BORLS","BORVA",
    "BOSSA","BRISA","BRKO","BRMEN","BRKVY","BRSAN","BRYAT","BSOKE","BTCIM",
    "BUCIM","BURCE","BURVA","BVSAN","CANTE","CCOLA","CELHA","CEMAS","CEMTS",
    "CIMSA","CLEBI","CMBTN","CMENT","CONSE","COSMO","CRDFA","CRFSA","CUSAN",
    "DAGHL","DAGI","DAPGM","DARDL","DATA","DENGE","DERHL","DESA","DESPC",
    "DEVA","DGATE","DGNMO","DITAS","DMSAS","DOAS","DOBUR","DOCO","DOGUB",
    "DOHOL","DOKTA","DURDO","DYOBY","DZGYO","ECILC","ECZYT","EDATA","EDIP",
    "EFORC","EGEEN","EGGUB","EGPRO","EGSER","EKGYO","EKIZ","EKSUN","ELITE",
    "EMKEL","EMNIS","ENERY","ENGYO","ENKAI","ENSRI","EPLAS","ERBOS","ERCB",
    "EREGL","ERSU","ESCAR","ESCOM","ESEN","ETILR","ETYAT","EUHOL","EUYO",
    "EYGYO","FADE","FENER","FMIZP","FONET","FORMT","FORTE","FRIGO","FROTO",
    "FZLGY","GARAN","GARFA","GEDIK","GEDZA","GENIL","GENTS","GEREL","GESAN",
    "GIPTA","GLBMD","GLCVY","GLRYH","GLYHO","GMTAS","GOLTS","GOODY","GOZDE",
    "GRSEL","GRTRK","GSDDE","GSDHO","GSRAY","GUBRF","GUNDO","GUNKM","GUNSEL",
    "HUNER","HALKB","HATEK","HDFGS","HEDEF","HEKTS","HLGYO","HTTBT","HUBVC",
    "HURGZ","ICBCT","ICUGS","IDEAS","IDGYO","IEYHO","IHEVA","IHLGM","IHYAY",
    "IMASM","INDES","INFO","INGRM","INTEM","INVEO","IPEKE","ISATR","ISBTR",
    "ISCTR","ISFIN","ISGSY","ISGYO","ISKPL","ISKUR","ISYAT","IZENR","IZFAS",
    "IZINV","IZMDC","JANTS","KAPLM","KAREL","KARSN","KARTN","KATMR","KAYSE",
    "KCAER","KCHOL","KENT","KERVT","KFEIN","KGYO","KIMMR","KLGYO","KLMSN",
    "KLNMA","KLRHO","KLSER","KLSYN","KMPUR","KNFRT","KONYA","KORDS","KOZAA",
    "KOZAL","KRDMA","KRDMB","KRDMD","KRGYO","KRPLS","KRSTL","KRTEK","KRVGD",
    "KSTUR","KTLEV","KTSKR","KUTPO","KUYAS","KZBGY","LIDER","LIDFA","LKMNH",
    "LOGO","LRSHO","LUKSK","MAGAN","MAKIM","MAKTK","MANAS","MARBL","MARKA",
    "MARTI","MAVI","MEDTR","MEGAP","MEKAG","MERCN","MERIT","MERKO","METRO",
    "METUR","MGROS","MIPAZ","MNDRS","MNDTR","MOBTL","MOGAN","MPARK","MRGYO",
    "MRSHL","MSGYO","MTRKS","MZHLD","NATEN","NETAS","NIBAS","NTGAZ","NTHOL",
    "NUGYO","NUHCM","OBAMS","ODAS","OFSYM","ONCSM","ONRYT","ORCAY","ORGE",
    "ORMA","OSMEN","OTKAR","OTTO","OYAKC","OYAYO","OYLUM","OZGYO","OZKGY",
    "OZRDN","OZSUB","PAGYO","PAMEL","PAPIL","PCILT","PEKGY","PENGD","PENTA",
    "PETKM","PETUN","PGSUS","PINSU","PKART","PKENT","PLTUR","POLHO","POLTK",
    "PRDCH","PRZMA","PSDTC","PSGYO","QNBFB","QNBFL","QUAGR","RALYH","RAYSG",
    "RHEAG","RNPOL","RODRG","ROYAL","RTALB","RUBNS","RYSAS","SAFKR","SAHOL",
    "SAMAT","SANEL","SANFM","SANKO","SARKY","SASA","SAYAS","SDTTR","SEGYO",
    "SEKFK","SEKUR","SELEC","SELGD","SELVA","SEYKM","SILVR","SISE","SKBNK",
    "SKTAS","SKYMD","SMART","SNGYO","SNKRN","SNPAM","SODSN","SOKE","SOKM",
    "SONME","SRVGY","SUMAS","SUNTK","SURGY","SUWEN","TABGD","TALGO","TATGD",
    "TAVHL","TBORG","TCELL","TDGYO","TEKTU","TERA","TETMT","THYAO","TKFEN",
    "TKNSA","TLMAN","TMPOL","TMSN","TOASO","TRCAS","TRGYO","TRILC","TSPOR",
    "TTKOM","TTRAK","TUCLK","TUKAS","TUPRS","TURGG","TURSG","ULUFA","ULUSE",
    "ULUUN","UMPAS","UNLU","USAK","USDTR","UTPYA","UYUM","VAKBN","VAKFN",
    "VAKKO","VANGD","VBTYZ","VERTU","VERUS","VESBE","VESTL","VKGYO","VKFYO",
    "VKING","VOBJF","WINTA","WNGAR","YATAS","YAYLA","YGYO","YKSLN","YONGA",
    "YUNSA","YYAPI","ZEDUR","ZRGYO","ZYMRT"
]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Backtest Parametreleri")

    st.subheader("📅 Tarih Aralığı")
    bas_tarih   = st.date_input("Başlangıç", value=datetime(2020, 1, 1))
    bitis_tarih = st.date_input("Bitiş",     value=datetime.today())

    st.subheader("📊 MACD")
    macd_fast   = st.slider("Hızlı EMA",  8,  20, 12)
    macd_slow   = st.slider("Yavaş EMA", 20,  40, 26)
    macd_signal = st.slider("Sinyal",     5,  15,  9)

    st.subheader("📈 EMA Trend Filtresi")
    ema20  = st.slider("EMA 1",  10,  30,  20)
    ema50  = st.slider("EMA 2",  30,  70,  50)
    ema100 = st.slider("EMA 3",  70, 130, 100)
    ema200 = st.slider("EMA 4", 150, 250, 200)

    st.subheader("🛡️ Risk Yönetimi")
    atr_period = st.slider("ATR Periyodu",     5, 21,  14)
    atr_mult   = st.slider("ATR Stop Çarpanı", 0.5, 3.0, 1.5, step=0.1)
    rr_ratio   = st.slider("R:R Oranı",        1.0, 5.0, 3.0, step=0.5)

    st.subheader("💰 Sermaye & Risk")
    baslangic_sermaye = st.number_input(
        "Başlangıç Sermayesi (₺)", value=1_000_000, step=50_000)
    risk_yuzdesi = st.slider(
        "İşlem Başına Risk (%)", 0.5, 5.0, 1.0, step=0.1,
        help="Her işlemde bu kadar sermaye riske atılır.\n"
             "Pozisyon = Risk ₺ ÷ Stop Mesafesi (lot cinsinden)")

    st.subheader("🔍 Ek Filtreler")
    hacim_filtre = st.checkbox("Hacim > 20g Ortalaması", value=True)
    fiyat_filtre = st.checkbox("Kapanış > EMA20",        value=True)

    calistir = st.button("🚀 Backtesti Çalıştır", type="primary", use_container_width=True)

# ── Yardımcı Fonksiyonlar ─────────────────────────────────────────────────────
def ema_h(s, p):
    return s.ewm(span=p, adjust=False).mean()

def atr_h(df, p=14):
    hi = pd.Series(df["High"].values.flatten(),  index=df.index)
    lo = pd.Series(df["Low"].values.flatten(),   index=df.index)
    cl = pd.Series(df["Close"].values.flatten(), index=df.index)
    pc = cl.shift(1)
    tr = pd.concat([(hi-lo), (hi-pc).abs(), (lo-pc).abs()], axis=1).max(axis=1)
    return tr.ewm(span=p, adjust=False).mean()

def indiktor(df, p):
    cl  = pd.Series(df["Close"].values.flatten(),  index=df.index)
    op  = pd.Series(df["Open"].values.flatten(),   index=df.index)
    hi  = pd.Series(df["High"].values.flatten(),   index=df.index)
    lo  = pd.Series(df["Low"].values.flatten(),    index=df.index)
    vol = pd.Series(df["Volume"].values.flatten(), index=df.index)

    e20  = ema_h(cl, p["ema20"])
    e50  = ema_h(cl, p["ema50"])
    e100 = ema_h(cl, p["ema100"])
    e200 = ema_h(cl, p["ema200"])
    trend = (e20 > e50) & (e50 > e100) & (e100 > e200)

    ml  = ema_h(cl, p["macd_fast"]) - ema_h(cl, p["macd_slow"])
    sig = ema_h(ml, p["macd_signal"])
    his = ml - sig
    hist_donus = (his > 0) & (his.shift(1) <= 0)

    atr     = atr_h(df, p["atr_period"])
    vol_ok  = (vol > vol.rolling(20).mean()) if p["hacim"] else pd.Series(True, index=df.index)
    fiy_ok  = (cl > e20)                     if p["fiyat"] else pd.Series(True, index=df.index)
    sinyal  = trend & hist_donus & vol_ok & fiy_ok

    return pd.DataFrame({
        "Close": cl, "Open": op, "High": hi, "Low": lo,
        "ATR": atr, "Sinyal": sinyal,
    })

# ── Adım 1: Ham Sinyal Listesi ────────────────────────────────────────────────
def sinyalleri_topla(hisse_listesi, params, start, end):
    kayitlar = []
    bar = st.progress(0, text="Hisseler taranıyor...")
    n   = len(hisse_listesi)

    for i, hisse in enumerate(hisse_listesi):
        bar.progress((i+1)/n, text=f"Taraniyor: {hisse} ({i+1}/{n})")
        try:
            df = yf.download(hisse+".IS", start=start, end=end,
                             progress=False, auto_adjust=True)
            if df is None or len(df) < 250:
                continue

            ind    = indiktor(df, params)
            gunler = df.index.tolist()

            for gun in ind[ind["Sinyal"]].index:
                idx = gunler.index(gun)
                if idx + 1 >= len(gunler):
                    continue
                ertesi      = gunler[idx + 1]
                giris       = float(ind.loc[ertesi, "Open"])
                atr_val     = float(ind.loc[gun, "ATR"])
                if giris <= 0 or atr_val <= 0 or np.isnan(giris) or np.isnan(atr_val):
                    continue
                stop_mesafe = atr_val * params["atr_mult"]
                if stop_mesafe <= 0:
                    continue
                kayitlar.append({
                    "Hisse":       hisse,
                    "Sinyal_Gun":  gun,
                    "Giris_Gun":   ertesi,
                    "Giris":       giris,
                    "Stop":        giris - stop_mesafe,
                    "Hedef":       giris + stop_mesafe * params["rr_ratio"],
                    "Stop_Mesafe": stop_mesafe,
                    "_sonraki":    gunler[idx+2:],
                    "_ind":        ind,
                })
        except Exception:
            continue

    bar.empty()
    return sorted(kayitlar, key=lambda x: x["Giris_Gun"])

# ── Adım 2: Portföy Simülasyonu ───────────────────────────────────────────────
def portfoy_sim(kayitlar, baslangic, risk_pct):
    """
    Kronolojik sırayla işlem açar/kapatır.
    Pozisyon büyüklüğü = Risk₺ / Stop_Mesafesi  (lot)
    Pozisyon tutarı    = Lot × Giriş fiyatı
    Sermaye < Pozisyon tutarı ise o sinyal atlanır.
    """
    sermaye   = float(baslangic)
    aktif     = []      # açık pozisyonlar
    islemler  = []
    equity_log= {}

    tum_gunler = sorted(set(k["Giris_Gun"] for k in kayitlar))
    giris_ptr  = 0

    for bugun in tum_gunler:

        # 1. Açık pozisyonlarda bugüne kadar çıkış oldu mu?
        hala_acik = []
        for poz in aktif:
            ind      = poz["_ind"]
            kapandi  = False
            islenmis = []

            for sg in poz["_sonraki"]:
                if sg > bugun:
                    break
                islenmis.append(sg)
                if sg not in ind.index:
                    continue
                yuksek = float(ind.loc[sg, "High"])
                dusuk  = float(ind.loc[sg, "Low"])
                if np.isnan(yuksek) or np.isnan(dusuk):
                    break

                cikis_gun   = None
                cikis_fiyat = None
                sonuc       = None

                if dusuk <= poz["Stop"]:
                    cikis_fiyat = poz["Stop"]
                    cikis_gun   = sg
                    sonuc       = "STOP"
                elif yuksek >= poz["Hedef"]:
                    cikis_fiyat = poz["Hedef"]
                    cikis_gun   = sg
                    sonuc       = "HEDEF"

                if sonuc:
                    kz = (cikis_fiyat - poz["Giris"]) * poz["Lot"]
                    sermaye += poz["Pozisyon_TL"] + kz
                    islemler.append({
                        "Hisse":         poz["Hisse"],
                        "Sinyal Günü":   poz["Sinyal_Gun"].date(),
                        "Giriş Günü":    poz["Giris_Gun"].date(),
                        "Giriş ₺":       round(poz["Giris"],       2),
                        "Stop ₺":        round(poz["Stop"],         2),
                        "Hedef ₺":       round(poz["Hedef"],        2),
                        "Çıkış Günü":    cikis_gun.date(),
                        "Çıkış Fiyat":   round(cikis_fiyat,         2),
                        "Sonuç":         sonuc,
                        "Lot":           round(poz["Lot"],           0),
                        "Pozisyon ₺":    round(poz["Pozisyon_TL"],  0),
                        "Riske Atılan ₺":round(poz["Risk_TL"],      0),
                        "Kar/Zarar ₺":   round(kz,                  0),
                        "Getiri%":       round((cikis_fiyat-poz["Giris"])/poz["Giris"]*100, 2),
                    })
                    # Kalan günleri güncelle
                    poz["_sonraki"] = [g for g in poz["_sonraki"] if g > cikis_gun]
                    kapandi = True
                    break

            if not kapandi:
                # İşlenmiş günleri listeden çıkar
                poz["_sonraki"] = [g for g in poz["_sonraki"] if g not in islenmis]
                hala_acik.append(poz)

        aktif = hala_acik

        # 2. Bugün giriş sinyali olanları işle
        while giris_ptr < len(kayitlar) and kayitlar[giris_ptr]["Giris_Gun"] == bugun:
            k = kayitlar[giris_ptr]
            giris_ptr += 1

            risk_tl    = sermaye * (risk_pct / 100)
            lot        = risk_tl / k["Stop_Mesafe"]
            poz_tl     = lot * k["Giris"]

            if poz_tl > sermaye or sermaye <= 0:
                continue  # Yeterli sermaye yok → atla

            sermaye -= poz_tl
            aktif.append({
                **k,
                "Lot":         lot,
                "Pozisyon_TL": poz_tl,
                "Risk_TL":     risk_tl,
            })

        # 3. Equity kaydı (nakit + açık poz. anlık değeri)
        acik_deger = 0.0
        for poz in aktif:
            ind = poz["_ind"]
            if bugun in ind.index:
                guncel = float(ind.loc[bugun, "Close"])
                acik_deger += poz["Lot"] * guncel
            else:
                acik_deger += poz["Pozisyon_TL"]
        equity_log[bugun] = sermaye + acik_deger

    # Hâlâ açık pozisyonları son kapanışa göre kapat
    for poz in aktif:
        ind = poz["_ind"]
        kalan = poz["_sonraki"]
        if not kalan:
            continue
        son_gun = kalan[-1]
        if son_gun not in ind.index:
            continue
        cikis_fiyat = float(ind.loc[son_gun, "Close"])
        kz = (cikis_fiyat - poz["Giris"]) * poz["Lot"]
        sermaye += poz["Pozisyon_TL"] + kz
        islemler.append({
            "Hisse":         poz["Hisse"],
            "Sinyal Günü":   poz["Sinyal_Gun"].date(),
            "Giriş Günü":    poz["Giris_Gun"].date(),
            "Giriş ₺":       round(poz["Giris"],       2),
            "Stop ₺":        round(poz["Stop"],         2),
            "Hedef ₺":       round(poz["Hedef"],        2),
            "Çıkış Günü":    son_gun.date(),
            "Çıkış Fiyat":   round(cikis_fiyat,         2),
            "Sonuç":         "AÇIK",
            "Lot":           round(poz["Lot"],           0),
            "Pozisyon ₺":    round(poz["Pozisyon_TL"],  0),
            "Riske Atılan ₺":round(poz["Risk_TL"],      0),
            "Kar/Zarar ₺":   round(kz,                  0),
            "Getiri%":       round((cikis_fiyat-poz["Giris"])/poz["Giris"]*100, 2),
        })

    return islemler, pd.Series(equity_log).sort_index()

# ── Ana Akış ──────────────────────────────────────────────────────────────────
if calistir:
    params = {
        "macd_fast": macd_fast, "macd_slow": macd_slow, "macd_signal": macd_signal,
        "ema20": ema20, "ema50": ema50, "ema100": ema100, "ema200": ema200,
        "atr_period": atr_period, "atr_mult": atr_mult, "rr_ratio": rr_ratio,
        "hacim": hacim_filtre, "fiyat": fiyat_filtre,
    }

    kayitlar = sinyalleri_topla(
        BIST_HISSELER, params, str(bas_tarih), str(bitis_tarih))

    if not kayitlar:
        st.warning("Hiç sinyal bulunamadı.")
        st.stop()

    st.info(f"✅ {len(kayitlar):,} sinyal bulundu. Portföy simülasyonu başlıyor...")

    with st.spinner("Simülasyon çalışıyor..."):
        islemler, equity = portfoy_sim(kayitlar, baslangic_sermaye, risk_yuzdesi)

    if not islemler:
        st.warning("Hiç işlem gerçekleşmedi (sermaye yetersiz olabilir).")
        st.stop()

    df = pd.DataFrame(islemler)

    # ── Metrikler ─────────────────────────────────────────────────────────────
    toplam     = len(df)
    kaz        = df[df["Kar/Zarar ₺"] > 0]
    kay        = df[df["Kar/Zarar ₺"] <= 0]
    win_rate   = len(kaz) / toplam * 100
    pf         = (abs(kaz["Kar/Zarar ₺"].sum()) / abs(kay["Kar/Zarar ₺"].sum())
                  if len(kay) > 0 and kay["Kar/Zarar ₺"].sum() != 0 else float("inf"))
    son_sermaye    = equity.iloc[-1] if len(equity) > 0 else baslangic_sermaye
    toplam_getiri  = (son_sermaye / baslangic_sermaye - 1) * 100
    net_kar        = df["Kar/Zarar ₺"].sum()
    peak           = equity.cummax()
    max_dd         = ((equity - peak) / peak * 100).min()

    st.markdown("---")
    st.subheader("📊 Özet")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Toplam İşlem",     f"{toplam:,}")
    c2.metric("Win Rate",          f"{win_rate:.1f}%")
    c3.metric("Profit Factor",     f"{pf:.2f}")
    c4.metric("Portföy Getirisi",  f"{toplam_getiri:.1f}%",
              delta=f"{toplam_getiri:.1f}% vs %0 sapan")

    c5,c6,c7,c8 = st.columns(4)
    c5.metric("Net Kar/Zarar",     f"{net_kar:,.0f}₺")
    c6.metric("Son Sermaye",        f"{son_sermaye:,.0f}₺")
    c7.metric("Max Drawdown",       f"{max_dd:.1f}%")
    c8.metric("Ort. Getiri/İşlem",  f"{df['Getiri%'].mean():.2f}%")

    c9,c10,c11,c12 = st.columns(4)
    c9.metric("Hedef Vuran",
              f"{len(df[df['Sonuç']=='HEDEF'])} "
              f"(%{len(df[df['Sonuç']=='HEDEF'])/toplam*100:.0f})")
    c10.metric("Stop Vuran",
               f"{len(df[df['Sonuç']=='STOP'])} "
               f"(%{len(df[df['Sonuç']=='STOP'])/toplam*100:.0f})")
    c11.metric("Ort. Kazanç ₺",
               f"{kaz['Kar/Zarar ₺'].mean():,.0f}₺" if len(kaz) > 0 else "—")
    c12.metric("Ort. Kayıp ₺",
               f"{kay['Kar/Zarar ₺'].mean():,.0f}₺" if len(kay) > 0 else "—")

    # ── Equity Curve ──────────────────────────────────────────────────────────
    if len(equity) > 1:
        st.markdown("---")
        st.subheader("📉 Portföy Büyüme Eğrisi")
        fig_eq = go.Figure()
        fig_eq.add_trace(go.Scatter(
            x=equity.index, y=equity.values,
            mode="lines", name="Portföy Değeri",
            line=dict(color="#2196F3", width=2),
            fill="tozeroy", fillcolor="rgba(33,150,243,0.07)"
        ))
        fig_eq.add_hline(y=baslangic_sermaye, line_dash="dash",
                         line_color="gray", annotation_text="Başlangıç Sermayesi")
        fig_eq.update_layout(
            height=350, yaxis_title="Portföy Değeri (₺)",
            margin=dict(l=60,r=30,t=30,b=40), hovermode="x unified",
        )
        st.plotly_chart(fig_eq, use_container_width=True)

    # ── Aylık Isı Haritası ────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("🗓️ Aylık Kar/Zarar Isı Haritası (₺)")

    df["_yil"] = df["Giriş Günü"].apply(lambda x: x.year)
    df["_ay"]  = df["Giriş Günü"].apply(lambda x: x.month)
    pivot = df.pivot_table(values="Kar/Zarar ₺", index="_yil", columns="_ay", aggfunc="sum")
    ay    = {1:"Oca",2:"Şub",3:"Mar",4:"Nis",5:"May",6:"Haz",
             7:"Tem",8:"Ağu",9:"Eyl",10:"Eki",11:"Kas",12:"Ara"}
    pivot.columns = [ay.get(c,c) for c in pivot.columns]
    pivot.index   = [str(y) for y in pivot.index]

    z   = pivot.values
    txt = [[f"{v:,.0f}₺" if not np.isnan(v) else "" for v in row] for row in z]

    fig_isi = go.Figure(go.Heatmap(
        z=z, x=list(pivot.columns), y=list(pivot.index),
        text=txt, texttemplate="%{text}",
        colorscale=[[0,"#b71c1c"],[0.45,"#ef9a9a"],
                    [0.5,"#f5f5f5"],[0.55,"#a5d6a7"],[1,"#1b5e20"]],
        zmid=0, showscale=True, colorbar=dict(title="₺"),
    ))
    fig_isi.update_layout(
        height=max(300, len(pivot.index)*45+100),
        margin=dict(l=60,r=40,t=30,b=40),
    )
    st.plotly_chart(fig_isi, use_container_width=True)

    # ── İşlem Tablosu + CSV ───────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📋 Tüm İşlemler")
    goster = df.drop(columns=["_yil","_ay"], errors="ignore")

    st.dataframe(
        goster.style.applymap(
            lambda v: ("color:#2e7d32;font-weight:bold" if isinstance(v,(int,float)) and v>0
                  else "color:#c62828;font-weight:bold" if isinstance(v,(int,float)) and v<0
                  else ""),
            subset=["Kar/Zarar ₺","Getiri%"]
        ),
        use_container_width=True, hide_index=True,
    )

    csv = goster.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        "⬇️ CSV İndir", csv,
        file_name=f"bist_portfoy_{datetime.today().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )

else:
    st.info("👈 Sol panelden parametreleri ayarlayın ve **Backtesti Çalıştır** butonuna basın.")
    st.markdown("""
    ### 🔍 Strateji & Risk Modeli

    | Kural | Detay |
    |-------|-------|
    | **Trend Filtresi** | EMA20 > EMA50 > EMA100 > EMA200 |
    | **Giriş Sinyali** | MACD Histogram: negatif → pozitif dönüş |
    | **Giriş Fiyatı** | ⭐ Sinyal sonrası ertesi gün **açılış (Open)** |
    | **Stop Loss** | Giriş − (ATR × çarpan) |
    | **Hedef** | Giriş + (Stop mesafesi × R:R) |
    | **Pozisyon Büyüklüğü** | **Risk ₺ ÷ Stop Mesafesi = Lot** |
    | **Risk/İşlem** | Güncel sermayenin %1'i (ayarlanabilir) |
    | **Sermaye Kontrolü** | ✅ Nakit yoksa işlem açılmaz |
    | **Benchmark** | %0 sabit sapan |
    """)
