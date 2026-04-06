import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="BIST Açılış Backtest", layout="wide")
st.title("📈 MACD Histogram Reversal — Açılış Fiyatı Backtest")
st.caption("Strateji: EMA trend filtresi + MACD histogram dönüşü | Giriş: Sinyal sonrası ertesi gün Open")

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

# ── Sidebar Parametreler ───────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Backtest Parametreleri")

    st.subheader("📅 Tarih Aralığı")
    bas_tarih = st.date_input("Başlangıç", value=datetime(2020, 1, 1))
    bitis_tarih = st.date_input("Bitiş", value=datetime.today())

    st.subheader("📊 MACD Ayarları")
    macd_fast   = st.slider("MACD Hızlı EMA", 8, 20, 12)
    macd_slow   = st.slider("MACD Yavaş EMA", 20, 40, 26)
    macd_signal = st.slider("MACD Sinyal", 5, 15, 9)

    st.subheader("📈 EMA Trend Filtresi")
    ema20  = st.slider("EMA 1 (kısa)", 10, 30, 20)
    ema50  = st.slider("EMA 2", 30, 70, 50)
    ema100 = st.slider("EMA 3", 70, 130, 100)
    ema200 = st.slider("EMA 4 (uzun)", 150, 250, 200)

    st.subheader("🛡️ Risk Yönetimi")
    atr_period  = st.slider("ATR Periyodu", 5, 21, 14)
    atr_mult    = st.slider("ATR Stop Çarpanı", 0.5, 3.0, 1.5, step=0.1)
    rr_ratio    = st.slider("Risk:Ödül Oranı (R:R)", 1.0, 5.0, 3.0, step=0.5)

    st.subheader("💼 Portföy Ayarları")
    max_pozisyon  = st.slider("Max Eş Zamanlı Pozisyon", 1, 20, 10)
    pozisyon_yuzde = st.slider("Pozisyon Büyüklüğü (%)", 1, 20, 10)
    baslangic_sermaye = st.number_input("Başlangıç Sermaye (₺)", value=100000, step=10000)

    st.subheader("🔍 Ek Filtreler")
    hacim_filtre = st.checkbox("Hacim Filtresi (>20 günlük ort.)", value=True)
    fiyat_filtre = st.checkbox("EMA20 Üzerinde Fiyat Filtresi", value=True)

    calistir = st.button("🚀 Backtesti Çalıştır", type="primary", use_container_width=True)

# ── Yardımcı Fonksiyonlar ──────────────────────────────────────────────────────
def ema(seri, periyot):
    return seri.ewm(span=periyot, adjust=False).mean()

def hesapla_atr(df, periyot=14):
    high = pd.Series(df["High"].values.flatten(), index=df.index)
    low  = pd.Series(df["Low"].values.flatten(),  index=df.index)
    close = pd.Series(df["Close"].values.flatten(), index=df.index)
    prev_close = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low  - prev_close).abs()
    ], axis=1).max(axis=1)
    return tr.ewm(span=periyot, adjust=False).mean()

def hesapla_sinyaller(df, params):
    close  = pd.Series(df["Close"].values.flatten(), index=df.index)
    high   = pd.Series(df["High"].values.flatten(),  index=df.index)
    low    = pd.Series(df["Low"].values.flatten(),   index=df.index)
    volume = pd.Series(df["Volume"].values.flatten(), index=df.index)
    open_  = pd.Series(df["Open"].values.flatten(),  index=df.index)

    # EMA trend filtresi
    e20  = ema(close, params["ema20"])
    e50  = ema(close, params["ema50"])
    e100 = ema(close, params["ema100"])
    e200 = ema(close, params["ema200"])
    trend_yukari = (e20 > e50) & (e50 > e100) & (e100 > e200)

    # MACD
    macd_fast_ema  = ema(close, params["macd_fast"])
    macd_slow_ema  = ema(close, params["macd_slow"])
    macd_line      = macd_fast_ema - macd_slow_ema
    signal_line    = ema(macd_line, params["macd_signal"])
    histogram      = macd_line - signal_line

    # MACD Histogram dönüşü (negatiften pozitife geçiş)
    hist_donus = (histogram > 0) & (histogram.shift(1) <= 0)

    # ATR
    atr = hesapla_atr(df, params["atr_period"])

    # Hacim filtresi
    vol_ort = volume.rolling(20).mean()
    hacim_ok = volume > vol_ort if params["hacim_filtre"] else pd.Series(True, index=df.index)

    # EMA20 üzerinde fiyat
    fiyat_ok = close > e20 if params["fiyat_filtre"] else pd.Series(True, index=df.index)

    # Sinyal = tüm koşullar
    sinyal = trend_yukari & hist_donus & hacim_ok & fiyat_ok

    return pd.DataFrame({
        "Close": close,
        "Open": open_,
        "High": high,
        "Low": low,
        "ATR": atr,
        "Sinyal": sinyal,
        "e20": e20,
    })

def backtest_calistir(hisse_listesi, params, start, end):
    tum_islemler = []
    progress = st.progress(0, text="Hisseler taranıyor...")
    toplam = len(hisse_listesi)

    for i, hisse in enumerate(hisse_listesi):
        progress.progress((i + 1) / toplam, text=f"İşleniyor: {hisse} ({i+1}/{toplam})")
        try:
            ticker = hisse + ".IS"
            df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
            if df is None or len(df) < 250:
                continue

            ind = hesapla_sinyaller(df, params)
            sinyal_gunleri = ind[ind["Sinyal"]].index

            for gun in sinyal_gunleri:
                # Ertesi gün verisi var mı?
                gunler = df.index.tolist()
                gun_idx = gunler.index(gun)
                if gun_idx + 1 >= len(gunler):
                    continue

                ertesi = gunler[gun_idx + 1]
                giris  = float(ind.loc[ertesi, "Open"])
                atr    = float(ind.loc[gun, "ATR"])

                if giris <= 0 or atr <= 0 or np.isnan(giris) or np.isnan(atr):
                    continue

                stop   = giris - (atr * params["atr_mult"])
                hedef  = giris + (giris - stop) * params["rr_ratio"]
                risk   = giris - stop

                if risk <= 0:
                    continue

                # İşlem takibi: ertesi günden itibaren çıkış ara
                sonraki_gunler = gunler[gun_idx + 2:]
                sonuc = None
                cikis_fiyat = None
                cikis_gun = None

                for sg in sonraki_gunler:
                    yuksek = float(ind.loc[sg, "High"]) if sg in ind.index else np.nan
                    dusuk  = float(ind.loc[sg, "Low"])  if sg in ind.index else np.nan
                    if np.isnan(yuksek) or np.isnan(dusuk):
                        break
                    if dusuk <= stop:
                        sonuc = "STOP"
                        cikis_fiyat = stop
                        cikis_gun = sg
                        break
                    if yuksek >= hedef:
                        sonuc = "HEDEF"
                        cikis_fiyat = hedef
                        cikis_gun = sg
                        break

                if sonuc is None:
                    # Açık pozisyon — son kapanışa çık
                    if len(sonraki_gunler) > 0:
                        son_gun = sonraki_gunler[-1]
                        if son_gun in ind.index:
                            cikis_fiyat = float(ind.loc[son_gun, "Close"])
                            cikis_gun = son_gun
                            sonuc = "AÇIK"
                        else:
                            continue
                    else:
                        continue

                getiri_yuzde = (cikis_fiyat - giris) / giris * 100

                tum_islemler.append({
                    "Hisse": hisse,
                    "Sinyal Günü": gun.date(),
                    "Giriş Günü": ertesi.date(),
                    "Giriş": round(giris, 2),
                    "Stop": round(stop, 2),
                    "Hedef": round(hedef, 2),
                    "Çıkış Günü": cikis_gun.date() if cikis_gun else None,
                    "Çıkış Fiyat": round(cikis_fiyat, 2),
                    "Sonuç": sonuc,
                    "Getiri%": round(getiri_yuzde, 2),
                    "Ay": ertesi.strftime("%Y-%m"),
                })

        except Exception:
            continue

    progress.empty()
    return pd.DataFrame(tum_islemler)

def portfoy_getirisi_hesapla(df_islemler, baslangic_sermaye, max_poz, poz_yuzde):
    """Basit sıralı portföy simülasyonu (max pozisyon + sabit sizing)."""
    if df_islemler.empty:
        return pd.Series(dtype=float), 0.0

    sermaye = baslangic_sermaye
    aktif_pozisyonlar = {}  # hisse: {giris, stop, hedef, boyut}
    gunluk_sermaye = {}

    # Tüm tarihleri birleştir
    tum_tarihler = sorted(set(
        list(df_islemler["Giriş Günü"]) +
        list(df_islemler["Çıkış Günü"].dropna())
    ))

    giris_map = df_islemler.groupby("Giriş Günü")
    cikis_map = df_islemler.groupby("Çıkış Günü")

    for tarih in tum_tarihler:
        # Çıkışları işle
        if tarih in cikis_map.groups:
            for _, row in cikis_map.get_group(tarih).iterrows():
                key = (row["Hisse"], row["Giriş Günü"])
                if key in aktif_pozisyonlar:
                    poz = aktif_pozisyonlar.pop(key)
                    getiri = (row["Çıkış Fiyat"] - poz["giris"]) / poz["giris"]
                    sermaye += poz["boyut"] * getiri

        # Girişleri işle
        if tarih in giris_map.groups:
            for _, row in giris_map.get_group(tarih).iterrows():
                if len(aktif_pozisyonlar) >= max_poz:
                    continue
                boyut = sermaye * (poz_yuzde / 100)
                aktif_pozisyonlar[(row["Hisse"], tarih)] = {
                    "giris": row["Giriş"],
                    "boyut": boyut,
                }
                sermaye -= boyut  # nakit azalt (basit model)

        gunluk_sermaye[tarih] = sermaye + sum(p["boyut"] for p in aktif_pozisyonlar.values())

    portfoy_serisi = pd.Series(gunluk_sermaye)
    toplam_getiri = (portfoy_serisi.iloc[-1] / baslangic_sermaye - 1) * 100 if len(portfoy_serisi) > 0 else 0
    return portfoy_serisi, toplam_getiri

def aylik_isi_haritasi(df_islemler):
    """Aylık ortalama getiri ısı haritası verisi."""
    if df_islemler.empty:
        return pd.DataFrame()
    df_islemler["Yıl"] = df_islemler["Sinyal Günü"].apply(lambda x: x.year)
    df_islemler["AyNo"] = df_islemler["Giriş Günü"].apply(
        lambda x: datetime.strptime(str(x), "%Y-%m-%d").month
    )
    pivot = df_islemler.pivot_table(
        values="Getiri%", index="Yıl", columns="AyNo", aggfunc="mean"
    )
    ay_adlari = {1:"Oca",2:"Şub",3:"Mar",4:"Nis",5:"May",6:"Haz",
                 7:"Tem",8:"Ağu",9:"Eyl",10:"Eki",11:"Kas",12:"Ara"}
    pivot.columns = [ay_adlari.get(c, c) for c in pivot.columns]
    return pivot

# ── Ana Akış ──────────────────────────────────────────────────────────────────
if calistir:
    params = {
        "macd_fast": macd_fast, "macd_slow": macd_slow, "macd_signal": macd_signal,
        "ema20": ema20, "ema50": ema50, "ema100": ema100, "ema200": ema200,
        "atr_period": atr_period, "atr_mult": atr_mult, "rr_ratio": rr_ratio,
        "hacim_filtre": hacim_filtre, "fiyat_filtre": fiyat_filtre,
    }

    with st.spinner("Veriler indiriliyor ve backtest çalışıyor..."):
        df_sonuc = backtest_calistir(
            BIST_HISSELER, params,
            start=str(bas_tarih), end=str(bitis_tarih)
        )

    if df_sonuc.empty:
        st.warning("Hiç işlem sinyali bulunamadı. Parametreleri gevşetin.")
        st.stop()

    # ── Özet Metrikler ────────────────────────────────────────────────────────
    toplam_islem    = len(df_sonuc)
    kazananlar      = df_sonuc[df_sonuc["Getiri%"] > 0]
    kaybedenler     = df_sonuc[df_sonuc["Getiri%"] <= 0]
    win_rate        = len(kazananlar) / toplam_islem * 100
    ort_kazanc      = kazananlar["Getiri%"].mean() if len(kazananlar) > 0 else 0
    ort_kayip       = kaybedenler["Getiri%"].mean() if len(kaybedenler) > 0 else 0
    profit_factor   = abs(kazananlar["Getiri%"].sum() / kaybedenler["Getiri%"].sum()) if len(kaybedenler) > 0 and kaybedenler["Getiri%"].sum() != 0 else float("inf")
    hedef_vuran     = len(df_sonuc[df_sonuc["Sonuç"] == "HEDEF"])
    stop_vuran      = len(df_sonuc[df_sonuc["Sonuç"] == "STOP"])
    acik_kalan      = len(df_sonuc[df_sonuc["Sonuç"] == "AÇIK"])
    ort_getiri      = df_sonuc["Getiri%"].mean()
    medyan_getiri   = df_sonuc["Getiri%"].median()

    portfoy_serisi, toplam_getiri = portfoy_getirisi_hesapla(
        df_sonuc.copy(), baslangic_sermaye, max_pozisyon, pozisyon_yuzde
    )

    st.markdown("---")
    st.subheader("📊 Özet İstatistikler")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Toplam İşlem", f"{toplam_islem:,}")
    col2.metric("Win Rate", f"{win_rate:.1f}%")
    col3.metric("Profit Factor", f"{profit_factor:.2f}")
    col4.metric("Portföy Getirisi", f"{toplam_getiri:.1f}%",
                delta=f"{toplam_getiri:.1f}% vs %0 sapan")

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Ort. Kazanç", f"{ort_kazanc:.2f}%")
    col6.metric("Ort. Kayıp", f"{ort_kayip:.2f}%")
    col7.metric("Hedef Vuran", f"{hedef_vuran} ({hedef_vuran/toplam_islem*100:.0f}%)")
    col8.metric("Stop Vuran", f"{stop_vuran} ({stop_vuran/toplam_islem*100:.0f}%)")

    col9, col10, col11, col12 = st.columns(4)
    col9.metric("Ort. Getiri/İşlem", f"{ort_getiri:.2f}%")
    col10.metric("Medyan Getiri", f"{medyan_getiri:.2f}%")
    col11.metric("En İyi İşlem", f"{df_sonuc['Getiri%'].max():.2f}%")
    col12.metric("En Kötü İşlem", f"{df_sonuc['Getiri%'].min():.2f}%")

    # ── Aylık Isı Haritası ────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("🗓️ Aylık Getiri Isı Haritası (Ortalama %)")

    pivot = aylik_isi_haritasi(df_sonuc.copy())
    if not pivot.empty:
        import plotly.graph_objects as go

        z_vals   = pivot.values
        x_labels = list(pivot.columns)
        y_labels = [str(y) for y in pivot.index]

        text_vals = [[f"{v:.1f}%" if not np.isnan(v) else "" for v in row] for row in z_vals]

        fig = go.Figure(data=go.Heatmap(
            z=z_vals,
            x=x_labels,
            y=y_labels,
            text=text_vals,
            texttemplate="%{text}",
            colorscale=[
                [0.0, "#d32f2f"],
                [0.4, "#ef9a9a"],
                [0.5, "#f5f5f5"],
                [0.6, "#a5d6a7"],
                [1.0, "#1b5e20"],
            ],
            zmid=0,
            showscale=True,
            colorbar=dict(title="Getiri %"),
        ))
        fig.update_layout(
            height=max(300, len(y_labels) * 45 + 100),
            xaxis_title="Ay",
            yaxis_title="Yıl",
            margin=dict(l=60, r=40, t=30, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Isı haritası için yeterli veri yok.")

    # ── İstatistik Detay Tablosu ──────────────────────────────────────────────
    st.markdown("---")
    st.subheader("🏆 En İyi Performanslı Hisseler (Top 20)")
    hisse_ozet = df_sonuc.groupby("Hisse").agg(
        İşlem_Sayısı=("Getiri%", "count"),
        Ort_Getiri=("Getiri%", "mean"),
        Toplam_Getiri=("Getiri%", "sum"),
        Win_Rate=("Getiri%", lambda x: (x > 0).mean() * 100)
    ).sort_values("Ort_Getiri", ascending=False).head(20).reset_index()
    hisse_ozet = hisse_ozet.rename(columns={
        "İşlem_Sayısı": "İşlem",
        "Ort_Getiri": "Ort. Getiri%",
        "Toplam_Getiri": "Toplam Getiri%",
        "Win_Rate": "Win Rate%",
    })
    st.dataframe(
        hisse_ozet.style.format({
            "Ort. Getiri%": "{:.2f}",
            "Toplam Getiri%": "{:.2f}",
            "Win Rate%": "{:.1f}",
        }).background_gradient(subset=["Ort. Getiri%"], cmap="RdYlGn"),
        use_container_width=True,
        hide_index=True,
    )

    # ── Tüm İşlemler (CSV İndirme) ────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📋 Tüm İşlemler")
    st.dataframe(
        df_sonuc.style.applymap(
            lambda v: "color: green" if isinstance(v, (int, float)) and v > 0 else
                      ("color: red" if isinstance(v, (int, float)) and v < 0 else ""),
            subset=["Getiri%"]
        ),
        use_container_width=True,
        hide_index=True,
    )

    csv = df_sonuc.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        label="⬇️ İşlemleri CSV İndir",
        data=csv,
        file_name=f"bist_acilis_backtest_{datetime.today().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )

else:
    st.info("👈 Sol panelden parametreleri ayarlayın ve **Backtesti Çalıştır** butonuna basın.")
    st.markdown("""
    ### 🔍 Strateji Özeti
    | Kural | Detay |
    |-------|-------|
    | **Trend Filtresi** | EMA20 > EMA50 > EMA100 > EMA200 |
    | **Giriş Sinyali** | MACD Histogram: negatiften → pozitife dönüş |
    | **Giriş Fiyatı** | ⭐ Sinyal günü kapanışından sonra **ertesi gün açılış (Open)** |
    | **Stop Loss** | Giriş − (ATR × çarpan) |
    | **Hedef** | Giriş + (Risk × R:R oranı) |
    | **Ek Filtreler** | Hacim > 20g ort. | Fiyat > EMA20 |
    | **Benchmark** | %0 (sabit sapan) |
    """)
