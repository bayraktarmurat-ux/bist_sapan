import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, date
import plotly.graph_objects as go

st.set_page_config(
    page_title="Sapan Kombinasyon Backtest",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .metric-card {
        background: #1e2433;
        border: 1px solid #2d3548;
        border-radius: 10px;
        padding: 16px 20px;
        text-align: center;
    }
    .metric-label { font-size: 12px; color: #8b95a8; margin-bottom: 4px; }
    .metric-value { font-size: 22px; font-weight: 700; }
    .metric-pos { color: #22c55e; }
    .metric-neg { color: #ef4444; }
    .metric-neu { color: #94a3b8; }
    .stProgress > div > div { background-color: #38bdf8; }
</style>
""", unsafe_allow_html=True)

# ─── KOMBİNASYONLAR ────────────────────────────────────────────────────────────
ATR_LISTESI      = [1.0, 1.5, 2.0, 2.5, 3.0]
RR_LISTESI       = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
TOLERANS_LISTESI = [0.01, 0.02, 0.03]  # %1, %2, %3
# 5 ATR x 7 R:R x 3 Tolerans = 105 kombinasyon

# ─── HİSSE LİSTELERİ ───────────────────────────────────────────────────────────
# TOP50 — Sapan Stratejisi backtest sonuçlarına göre en iyi 50 hisse
TOP50 = {
    "BURCE","BURVA","GRTHO","PASEU","CRDFA","BYDNR","BAHKM","BMSCH","AKSUE","ARSAN",
    "AKYHO","BRSAN","HEDEF","ISGSY","ICUGS","CRFSA","AVTUR","AKSA","KRGYO","BIGCH",
    "BRKVY","ETYAT","BORLS","BFREN","ULAS","AHGAZ","POLTK","BLCYT","BERA","KLRHO",
    "FLAP","OYAYO","DCTTR","IEYHO","ISKPL","CCOLA","GZNMI","KUVVA","HURGZ","ARENA",
    "RTALB","DYOBY","MANAS","DNISI","OZRDN","GLCVY","SANFM","TURGG","CVKMD","GUBRF",
}

BIST_HISSELER = [
    "ACSEL","ADEL","ADESE","ADGYO","AFYON","AGHOL","AGESA","AGROT","AHSGY","AHGAZ",
    "AKYHO","AKENR","AKFGY","AKFIS","AKFYE","AKHAN","ATEKS","AKSGY","AKMGY","AKSA",
    "AKSEN","AKGRT","AKSUE","ALCAR","ALGYO","ALARK","ALBRK","ALCTL","ALFAS","ALKIM",
    "ALKA","AYCES","ALTNY","ALKLC","ALVES","ANSGR","AEFES","ANHYT","ASUZU","ANGEN",
    "ANELE","ARCLK","ARDYZ","ARENA","ARFYE","ARMGD","ARSAN","ARTMS","ARZUM","ASGYO",
    "ASELS","ASTOR","ATAGY","ATATR","ATAKP","AGYO","ATSYH","ATLAS","ATATP","AVOD",
    "AVGYO","AVTUR","AVHOL","AVPGY","AYDEM","AYEN","AYES","AYGAZ","AZTEK","A1CAP",
    "A1YEN","BAGFS","BAHKM","BAKAB","BALAT","BALSU","BNTAS","BANVT","BARMA","BASGZ",
    "BASCM","BEGYO","BTCIM","BSOKE","BYDNR","BAYRK","BERA","BRKSN","BESLR","BESTE",
    "BJKAS","BEYAZ","BIENY","BIGTK","BLCYT","BIMAS","BINBN","BIOEN","BRKVY","BRKO",
    "BIGEN","BRLSM","BRMEN","BIZIM","BLUME","BMSTL","BMSCH","BOBET","BORSK","BORLS",
    "BRSAN","BRYAT","BFREN","BOSSA","BRISA","BULGS","BURCE","BURVA","BUCIM","BVSAN",
    "BIGCH","CRFSA","CASA","CEMZY","CEOEM","CCOLA","CONSE","COSMO","CRDFA","CVKMD",
    "CWENE","CGCAM","CANTE","CATES","CLEBI","CELHA","CEMAS","CEMTS","CMBTN","CMENT",
    "CIMSA","CUSAN","DAGI","DAPGM","DARDL","DGATE","DCTTR","DMSAS","DENGE","DZGYO",
    "DERIM","DERHL","DESA","DESPC","DSTKF","DEVA","DNISI","DIRIT","DITAS","DMRGD",
    "DOCO","DOFRB","DOFER","DOHOL","DGNMO","ARASE","DOGUB","DGGYO","DOAS","DOKTA",
    "DURDO","DURKN","DUNYH","DYOBY","EBEBK","ECOGR","ECZYT","EDATA","EDIP","EFOR",
    "EGEEN","EGGUB","EGPRO","EGSER","EPLAS","EGEGY","ECILC","EKIZ","EKOS","EKSUN",
    "ELITE","EMKEL","EMNIS","EKGYO","EMPAE","ENDAE","ENJSA","ENERY","ENKAI","ENSRI",
    "ERBOS","ERCB","EREGL","KIMMR","ERSU","ESCAR","ESCOM","ESEN","ETILR","EUKYO",
    "EUYO","ETYAT","EUHOL","TEZOL","EUREN","EUPWR","EYGYO","FADE","FMIZP","FENER",
    "FLAP","FONET","FROTO","FORMT","FRMPL","FORTE","FRIGO","FZLGY","GWIND","GSRAY",
    "GARFA","GRNYO","GATEG","GEDIK","GEDZA","GLCVY","GENIL","GENTS","GENKM","GEREL",
    "GZNMI","GIPTA","GMTAS","GESAN","GLBMD","GLYHO","GOODY","GOKNR","GOLTS","GOZDE",
    "GRTHO","GSDDE","GSDHO","GUBRF","GLRYH","GLRMK","GUNDG","GRSEL","SAHOL","HLGYO",
    "HRKET","HATEK","HATSN","HDFGS","HEDEF","HEKTS","HKTM","HTTBT","HOROZ","HUBVC",
    "HUNER","HURGZ","ENTRA","ICBCT","ICUGS","INGRM","INVEO","INVES","ISKPL","IEYHO",
    "IDGYO","IHEVA","IHLGM","IHGZT","IHAAS","IHLAS","IHYAY","IMASM","INDES","INFO",
    "INTEK","INTEM","ISDMR","ISFIN","ISGYO","ISGSY","ISMEN","ISYAT","ISBIR","ISSEN",
    "IZINV","IZENR","IZMDC","IZFAS","JANTS","KFEIN","KLKIM","KLSER","KLYPV","KAPLM",
    "KRDMA","KRDMB","KRDMD","KAREL","KARSN","KRTEK","KARTN","KTLEV","KATMR","KAYSE",
    "KENT","KRVGD","KERVN","TCKRC","KZBGY","KLGYO","KLRHO","KMPUR","KLMSN","KCAER",
    "KCHOL","KOCMT","KLSYN","KNFRT","KONTR","KONYA","KONKA","KGYO","KORDS","KRPLS",
    "KOTON","KOPOL","KRGYO","KRSTL","KRONT","KSTUR","KUVVA","KUYAS","KBORU","KZGYO",
    "KUTPO","KTSKR","LIDER","LIDFA","LILAK","LMKDC","LINK","LOGO","LKMNH","LRSHO",
    "LUKSK","LYDHO","LYDYE","MACKO","MAKIM","MAKTK","MANAS","MAGEN","MARKA","MARMR",
    "MAALT","MRSHL","MRGYO","MARTI","MTRKS","MAVI","MZHLD","MEDTR","MEGMT","MEGAP",
    "MEKAG","MNDRS","MEPET","MERCN","MERIT","MERKO","METRO","MTRYO","MEYSU","MHRGY",
    "MIATK","MGROS","MSGYO","MPARK","MMCAS","MOBTL","MOGAN","MNDTR","MOPAS","EGEPO",
    "NATEN","NTGAZ","NTHOL","NETAS","NETCD","NIBAS","NUHCM","NUGYO","OBAMS","OBASE",
    "ODAS","ODINE","OFSYM","ONCSM","ONRYT","ORCAY","ORGE","ORMA","OSMEN","OSTIM",
    "OTKAR","OTTO","OYAKC","OYYAT","OYAYO","OYLUM","OZKGY","OZATD","OZGYO","OZRDN",
    "OZSUB","OZYSR","PAMEL","PNLSN","PAGYO","PAPIL","PRDGS","PRKME","PARSN","PASEU",
    "PSGYO","PAHOL","PATEK","PCILT","PGSUS","PEKGY","PENGD","PENTA","PSDTC","PETKM",
    "PKENT","PETUN","PINSU","PNSUT","PKART","PLTUR","POLHO","POLTK","PRZMA","RNPOL",
    "RALYH","RAYSG","REEDR","RYGYO","RYSAS","RODRG","ROYAL","RGYAS","RTALB","RUBNS",
    "RUZYE","SAFKR","SANEL","SNICA","SANFM","SANKO","SAMAT","SARKY","SASA","SVGYO",
    "SAYAS","SDTTR","SEGMN","SEKUR","SELEC","SELVA","SERNT","SRVGY","SEYKM","SILVR",
    "SNGYO","SKYLP","SMRTG","SMART","SODSN","SOKE","SKTAS","SONME","SNPAM","SUMAS",
    "SUNTK","SURGY","SUWEN","SMRVA","SEKFK","SEGYO","SKYMD","SKBNK","SOKM","TABGD",
    "TATGD","TATEN","TAVHL","TEKTU","TKFEN","TKNSA","TMPOL","TRHOL","TERA","TEHOL",
    "TGSAS","TOASO","TRGYO","TRMET","TRENJ","TLMAN","TSPOR","TDGYO","TSGYO","TUCLK",
    "TUKAS","TRCAS","TUREX","MARBL","TRILC","TCELL","TMSN","TUPRS","TRALT","THYAO",
    "PRKAB","TTKOM","TTRAK","TBORG","TURGG","GARAN","HALKB","ISATR","ISBTR","ISCTR",
    "ISKUR","KLNMA","TSKB","TURSG","SISE","VAKBN","UFUK","ULAS","ULUFA","ULUSE",
    "ULUUN","UMPAS","USAK","UCAYM","ULKER","UNLU","VAKFA","VAKFN","VKGYO","VKFYO",
    "VAKKO","VANGD","VBTYZ","VRGYO","VERUS","VERTU","VESBE","VESTL","VKING","VSNMD",
    "YKBNK","YAPRK","YATAS","YYLGD","YAYLA","YGGYO","YEOTK","YGYO","YYAPI","YESIL",
    "YBTAS","YIGIT","YONGA","YKSLN","YUNSA","ZGYO","ZEDUR","ZERGY","ZRGYO","ZOREN",
    "BINHO",
]

# ─── YARDIMCI FONKSİYONLAR ─────────────────────────────────────────────────────
def squeeze(s):
    if hasattr(s, "squeeze"):
        s = s.squeeze()
    if hasattr(s, "iloc") and s.ndim == 2:
        s = s.iloc[:, 0]
    return s

def veri_cek(ticker, bas, bit):
    try:
        df = yf.download(ticker + ".IS", start=str(bas), end=str(bit),
                         interval="1d", progress=False, auto_adjust=True)
        if df.empty or len(df) < 50:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df[["Open","High","Low","Close","Volume"]].dropna()
        for col in df.columns:
            df[col] = squeeze(df[col])
        df.index = df.index.tz_localize(None)
        return df
    except Exception:
        return None

def endeks_filtre_olustur(bas, bit):
    try:
        df = yf.download("XU100.IS",
                         start=(bas - pd.DateOffset(years=1)).strftime("%Y-%m-%d"),
                         end=str(bit), interval="1d", progress=False, auto_adjust=True)
        if df.empty:
            return {}
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.index = df.index.tz_localize(None)
        df["EMA200"] = squeeze(df["Close"]).ewm(span=200, adjust=False).mean()
        df.dropna(subset=["EMA200"], inplace=True)
        return {row.Index.date(): float(row.Close) > float(row.EMA200)
                for row in df.itertuples()}
    except Exception:
        return {}

def hesapla_ind(df, atr_per=14):
    """Sapan Stratejisi için tüm indikatörleri hesapla."""
    c = squeeze(df["Close"])
    h = squeeze(df["High"])
    l = squeeze(df["Low"])

    # EMA'lar
    for p in [20, 50, 100, 200]:
        df[f"EMA{p}"] = c.ewm(span=p, adjust=False).mean()

    # ATR
    hl = h - l
    hc = (h - c.shift(1)).abs()
    lc = (l - c.shift(1)).abs()
    df["ATR"] = pd.concat([hl, hc, lc], axis=1).max(axis=1).ewm(
        span=atr_per, adjust=False).mean()

    # Stochastic (5,3,3)
    lowest_low   = l.rolling(5).min()
    highest_high = h.rolling(5).max()
    stoch_k_raw  = 100 * (c - lowest_low) / (highest_high - lowest_low + 1e-10)
    df["STOCH_K"] = stoch_k_raw.rolling(3).mean()

    # MACD (50,100,9)
    ema_h = c.ewm(span=50,  adjust=False).mean()
    ema_y = c.ewm(span=100, adjust=False).mean()
    df["MACD"] = ema_h - ema_y

    return df

def ema_dokunusu_var_mi(low_val, high_val, ema20, ema50, ema100, ema200, tolerans):
    for ema_val in [ema20, ema50, ema100, ema200]:
        if pd.isna(ema_val):
            continue
        if low_val <= ema_val * (1 + tolerans) and high_val >= ema_val * (1 - tolerans):
            return True
    return False

def higher_low_kontrol(df, reversal_idx, lookback=30):
    if reversal_idx < 2:
        return True
    reversal_low = float(df["Low"].iloc[reversal_idx])
    sub = df["Low"].iloc[max(0, reversal_idx-lookback):reversal_idx]
    if len(sub) == 0:
        return True
    son_dip = float(sub.min())
    if reversal_low >= son_dip:
        return True
    for col in ["EMA100", "EMA200"]:
        if col in df.columns:
            ema_val = float(df[col].iloc[reversal_idx])
            if not pd.isna(ema_val) and reversal_low <= ema_val * 1.02:
                return True
    return False

# ─── SAPAN SİNYAL ÜRETİMİ (ATR bazlı stop) ────────────────────────────────────
def sinyal_uret(hisse_verileri, bas_ts, bit_ts, endeks_f, endeks_aktif,
                atr_kat, ema_tolerans):
    """
    Sapan Stratejisi filtreleriyle sinyal üretir.
    Stop = Giriş - ATR × atr_kat (hedef R:R'a göre backtest_calistir'da eklenir)
    """
    gunluk_sinyaller = {}

    for sembol, df in hisse_verileri.items():
        for i in range(2, len(df)):
            son        = df.iloc[i]
            onceki     = df.iloc[i-1]
            iki_onceki = df.iloc[i-2]

            if son.name < bas_ts or son.name > bit_ts:
                continue
            if endeks_aktif and not endeks_f.get(son.name.date(), True):
                continue

            # ── FİLTRE 1: EMA Trend ──────────────────────────────────────────
            if not (float(son["EMA20"]) > float(son["EMA50"]) >
                    float(son["EMA100"]) > float(son["EMA200"])):
                continue

            # ── FİLTRE 2: Stochastic < 30 (dönüş mumunda) ────────────────────
            if float(onceki["STOCH_K"]) >= 30:
                continue

            # ── FİLTRE 3: MACD pozitif VEYA 5'ten az süredir negatif ─────────
            macd_vals    = df["MACD"].iloc[max(0,i-5):i]
            macd_pozitif = float(son["MACD"]) > 0
            negatif_sure = (macd_vals < 0).sum()
            if not macd_pozitif and negatif_sure >= 5:
                continue

            # ── FİLTRE 4: Onay mumu yeşil, dönüş mumunun high'ını kırmış ─────
            if float(son["Close"]) <= float(son["Open"]):
                continue
            if float(son["Close"]) <= float(onceki["High"]):
                continue

            # ── FİLTRE 5: EMA dokunuşu ───────────────────────────────────────
            if not ema_dokunusu_var_mi(
                float(onceki["Low"]), float(onceki["High"]),
                float(onceki["EMA20"]), float(onceki["EMA50"]),
                float(onceki["EMA100"]), float(onceki["EMA200"]),
                tolerans=ema_tolerans
            ):
                continue

            # ── FİLTRE 6: Higher Low ─────────────────────────────────────────
            if not higher_low_kontrol(df, i-1):
                continue

            # ── GİRİŞ / STOP (ATR bazlı) ─────────────────────────────────────
            giris   = float(son["Close"])
            atr_val = float(son["ATR"])
            stop    = round(giris - atr_kat * atr_val, 2)
            if giris - stop <= 0:
                continue

            tarih = son.name
            if tarih not in gunluk_sinyaller:
                gunluk_sinyaller[tarih] = []
            gunluk_sinyaller[tarih].append({
                "sembol": sembol,
                "giris" : giris,
                "stop"  : stop,
                "atr_v" : atr_val,
                "top50" : sembol in TOP50,
            })

    return gunluk_sinyaller

def backtest_calistir(gunluk_sinyaller, hisse_verileri, bas_ts, bit_ts,
                      portfoy, max_pozisyon, poz_yuzde, rr_kat):
    """Belirli bir R:R katsayısıyla backtest simülasyonu yapar."""
    portfoy_s    = portfoy
    acik_pozlar  = []
    kapali_islem = []
    atlanan      = 0

    # Sinyallere hedef ekle
    sinyaller_rr = {}
    for tarih, liste in gunluk_sinyaller.items():
        sinyaller_rr[tarih] = []
        for s in liste:
            hedef = s["giris"] + (s["giris"] - s["stop"]) * rr_kat
            sinyaller_rr[tarih].append({**s, "hedef": hedef})

    tum_tarihler = sorted(set(
        d for df in hisse_verileri.values()
        for d in df.index
        if bas_ts <= d <= bit_ts
    ))

    for tarih in tum_tarihler:
        # Açık pozisyonları kontrol et
        kapalanlar = []
        for poz in acik_pozlar:
            sembol = poz["sembol"]
            if sembol not in hisse_verileri:
                continue
            df     = hisse_verileri[sembol]
            gunluk = df[df.index == tarih]
            if gunluk.empty:
                continue
            gun_low  = float(gunluk.iloc[0]["Low"])
            gun_high = float(gunluk.iloc[0]["High"])
            sonuc = None
            if gun_low <= poz["stop"]:
                sonuc = "stop"
                cikis = poz["stop"]
            elif gun_high >= poz["hedef"]:
                sonuc = "hedef"
                cikis = poz["hedef"]
            if sonuc:
                kaz = (cikis - poz["giris"]) * poz["lot"]
                portfoy_s += kaz
                kapali_islem.append({
                    "Sonuç"   : "✅ Hedef" if sonuc == "hedef" else "❌ Stop",
                    "K/Z (TL)": round(kaz, 0),
                })
                kapalanlar.append(poz)
        for k in kapalanlar:
            acik_pozlar.remove(k)

        # Yeni sinyaller
        if tarih in sinyaller_rr:
            sinyaller_bugun = sorted(
                sinyaller_rr[tarih], key=lambda x: (not x["top50"])
            )
            for sinyal in sinyaller_bugun:
                if any(p["sembol"] == sinyal["sembol"] for p in acik_pozlar):
                    continue
                if len(acik_pozlar) >= max_pozisyon:
                    atlanan += 1
                    continue
                poz_tl = portfoy_s * (poz_yuzde / 100)
                lot    = max(1, int(poz_tl / sinyal["giris"]))
                acik_pozlar.append({
                    "sembol": sinyal["sembol"],
                    "giris" : sinyal["giris"],
                    "stop"  : sinyal["stop"],
                    "hedef" : sinyal["hedef"],
                    "lot"   : lot,
                    "top50" : sinyal["top50"],
                })

    # Açık pozisyonları son fiyatla kapat
    for poz in acik_pozlar:
        sembol = poz["sembol"]
        if sembol not in hisse_verileri:
            continue
        df    = hisse_verileri[sembol]
        son   = df.iloc[-1]
        cikis = float(son["Close"])
        kaz   = (cikis - poz["giris"]) * poz["lot"]
        portfoy_s += kaz
        kapali_islem.append({
            "Sonuç"   : "⏳ Açık",
            "K/Z (TL)": round(kaz, 0),
        })

    # Metrikleri hesapla
    df_k     = pd.DataFrame(kapali_islem) if kapali_islem else pd.DataFrame(
        columns=["Sonuç", "K/Z (TL)"])
    tamam    = df_k[df_k["Sonuç"].str.contains("Hedef|Stop", na=False)]
    kazanan  = df_k[df_k["Sonuç"] == "✅ Hedef"]
    kaybeden = df_k[df_k["Sonuç"] == "❌ Stop"]
    toplam   = len(tamam)
    wr       = len(kazanan) / toplam * 100 if toplam > 0 else 0
    getiri   = (portfoy_s - portfoy) / portfoy * 100

    return {
        "Son Portföy (TL)": round(portfoy_s, 0),
        "Getiri (%)"      : round(getiri, 1),
        "Win Rate (%)"    : round(wr, 1),
        "Toplam İşlem"    : toplam,
        "Kazanan"         : len(kazanan),
        "Kaybeden"        : len(kaybeden),
        "Atlanan Sinyal"  : atlanan,
    }

# ─── SIDEBAR ────────────────────────────────────────────────────────────────────
st.sidebar.title("⚙️ Backtest Ayarları")

st.sidebar.markdown("### 📅 Tarih Aralığı")
col1, col2 = st.sidebar.columns(2)
bas_tarih = col1.date_input("Başlangıç", value=date(2022, 1, 1),
                             min_value=date(2010, 1, 1), max_value=date.today())
bit_tarih = col2.date_input("Bitiş", value=date.today(),
                             min_value=date(2010, 1, 1), max_value=date.today())

st.sidebar.markdown("### 💰 Sermaye & Pozisyon")
portfoy      = st.sidebar.number_input("Başlangıç Sermaye (TL)", min_value=10_000,
                                        max_value=100_000_000, value=1_000_000, step=10_000)
max_pozisyon = st.sidebar.slider("Max Eş Zamanlı Pozisyon", 1, 20, 10, 1)
poz_yuzde    = st.sidebar.slider("Pozisyon Büyüklüğü (%)", 5.0, 50.0,
                                  round(100 / max_pozisyon, 1), 5.0)

st.sidebar.markdown("### 📐 Strateji Parametreleri")
atr_per = st.sidebar.slider("ATR Periyodu", 7, 21, 14, 1)

st.sidebar.markdown("### 🔍 Filtreler")
endeks_aktif = st.sidebar.checkbox("Endeks Filtresi (BIST100 > EMA200)", value=True)

# ─── BAŞLIK ─────────────────────────────────────────────────────────────────────
st.title("📊 Sapan Stratejisi Kombinasyon Backtest")
st.caption("ATR × R:R × EMA Tolerans | 5 ATR × 7 R:R × 3 Tolerans = 105 Kombinasyon")

st.info(f"""
**Çalışma Mantığı:**
- Sinyal üretimi: **Sapan Stratejisi** (EMA Trend + Stoch(5,3,3) + MACD(50,100,9) + Price Action + Higher Low)
- Veri **bir kez** indirilir, göstergeler **bir kez** hesaplanır
- Her **ATR × Tolerans** kombinasyonu için sinyaller ayrı üretilir (15 geçiş)
- Her **R:R** için pozisyon simülasyonu çalıştırılır (toplam **105 backtest**)
- Stop = Giriş − ATR({atr_per}) × Katsayı | Hedef = Giriş + Stop Mesafesi × R:R
- EMA Tolerans: Mumun EMA'ya kaç % yakınına gelmesi dokunuş sayılır (%1, %2, %3)
""")

# ─── ÇALIŞTIR ───────────────────────────────────────────────────────────────────
if st.button("🚀 Kombinasyon Backtest Başlat", use_container_width=True, type="primary"):

    bas_ts   = pd.Timestamp(bas_tarih)
    bit_ts   = pd.Timestamp(bit_tarih)
    veri_bas = bas_ts - pd.DateOffset(years=1)
    veri_bit = bit_ts + pd.DateOffset(days=2)

    # 1) Endeks filtresi
    endeks_f = {}
    if endeks_aktif:
        with st.spinner("Endeks verisi indiriliyor..."):
            endeks_f = endeks_filtre_olustur(bas_ts, veri_bit)

    # 2) Hisse verileri (tek seferlik indirme)
    hisse_verileri = {}
    progress = st.progress(0, text="Hisse verileri indiriliyor...")
    for hi, sembol in enumerate(BIST_HISSELER):
        progress.progress(
            (hi + 1) / len(BIST_HISSELER),
            text=f"İndiriliyor: {sembol} ({hi+1}/{len(BIST_HISSELER)})"
        )
        df_raw = veri_cek(sembol,
                          veri_bas.to_pydatetime().date(),
                          veri_bit.to_pydatetime().date())
        if df_raw is None:
            continue
        try:
            df = hesapla_ind(df_raw.copy(), atr_per)
            df.dropna(subset=["EMA200", "STOCH_K", "MACD", "ATR"], inplace=True)
            if len(df) >= 50:
                hisse_verileri[sembol] = df
        except Exception:
            continue
    progress.empty()
    st.success(f"✅ {len(hisse_verileri)} hisse yüklendi.")

    # 3) Her ATR × Tolerans için sinyalleri üret, her R:R için backtest çalıştır
    sonuclar    = []
    toplam_adim = len(ATR_LISTESI) * len(TOLERANS_LISTESI) * len(RR_LISTESI)
    adim = 0
    prog2 = st.progress(0, text="Kombinasyonlar hesaplanıyor...")

    for tolerans in TOLERANS_LISTESI:
        for atr_kat in ATR_LISTESI:
            gunluk_sinyaller = sinyal_uret(
                hisse_verileri, bas_ts, bit_ts,
                endeks_f, endeks_aktif, atr_kat, tolerans
            )
            for rr_kat in RR_LISTESI:
                adim += 1
                prog2.progress(
                    adim / toplam_adim,
                    text=f"Tolerans %{int(tolerans*100)} | ATR {atr_kat} | R:R {rr_kat} ({adim}/{toplam_adim})"
                )
                sonuc = backtest_calistir(
                    gunluk_sinyaller, hisse_verileri, bas_ts, bit_ts,
                    portfoy, max_pozisyon, poz_yuzde, rr_kat
                )
                sonuclar.append({
                    "Tolerans (%)": int(tolerans * 100),
                    "ATR"         : atr_kat,
                    "R:R"         : rr_kat,
                    **sonuc
                })

    prog2.empty()
    st.session_state["sonuclar"] = sonuclar
    st.session_state["portfoy0"] = portfoy

# ─── SONUÇLAR ───────────────────────────────────────────────────────────────────
if "sonuclar" in st.session_state:
    sonuclar = st.session_state["sonuclar"]
    portfoy0 = st.session_state["portfoy0"]
    df_sonuc = pd.DataFrame(sonuclar)

    st.markdown("---")
    st.subheader("📋 Kombinasyon Karşılaştırma Tablosu")

    def renk_getiri(val):
        if isinstance(val, (int, float)):
            color = "#22c55e" if val >= 0 else "#ef4444"
            return f"color: {color}; font-weight: 600"
        return ""

    def renk_wr(val):
        if isinstance(val, (int, float)):
            if val >= 50:   return "color: #22c55e; font-weight: 600"
            elif val >= 35: return "color: #f59e0b; font-weight: 600"
            else:           return "color: #ef4444; font-weight: 600"
        return ""

    df_goster = df_sonuc.copy()
    df_goster["Getiri (%)"]       = df_goster["Getiri (%)"].apply(lambda x: f"{x:+.1f}%")
    df_goster["Win Rate (%)"]     = df_goster["Win Rate (%)"].apply(lambda x: f"{x:.1f}%")
    df_goster["Son Portföy (TL)"] = df_goster["Son Portföy (TL)"].apply(lambda x: f"{x:,.0f}")
    df_goster["Kaz/Kay"]          = df_goster["Kazanan"].astype(str) + " / " + df_goster["Kaybeden"].astype(str)
    df_goster = df_goster[[
        "Tolerans (%)","ATR","R:R","Son Portföy (TL)","Getiri (%)","Win Rate (%)",
        "Toplam İşlem","Kaz/Kay","Atlanan Sinyal"
    ]]

    st.dataframe(df_goster, use_container_width=True, hide_index=True, height=600)

    # ─── TOLERANSA GÖRE SEKMELER ────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("🌡️ Isıl Haritalar (Toleransa Göre)")

    tab1, tab2, tab3 = st.tabs(["📊 Tolerans %1", "📊 Tolerans %2", "📊 Tolerans %3"])

    for tab, tolerans_val in zip([tab1, tab2, tab3], [1, 2, 3]):
        with tab:
            df_t = df_sonuc[df_sonuc["Tolerans (%)"] == tolerans_val]

            # Getiri ısıl haritası
            st.markdown(f"**Getiri Isıl Haritası — Tolerans %{tolerans_val}**")
            pivot = df_t.pivot(index="ATR", columns="R:R", values="Getiri (%)")
            pivot = pivot.sort_index(ascending=False)

            fig = go.Figure(go.Heatmap(
                z=pivot.values,
                x=[f"R:R {c}" for c in pivot.columns],
                y=[f"ATR {r}" for r in pivot.index],
                colorscale="RdYlGn",
                text=[[f"+{v:.1f}%" if v >= 0 else f"{v:.1f}%" for v in row] for row in pivot.values],
                texttemplate="%{text}",
                textfont={"size": 13, "color": "white"},
                hoverongaps=False,
                colorbar=dict(title="Getiri %"),
            ))
            fig.update_layout(
                template="plotly_dark", paper_bgcolor="#0d0f14",
                plot_bgcolor="#0d0f14", height=320,
                margin=dict(l=10, r=10, t=20, b=10),
                xaxis=dict(side="top"),
            )
            st.plotly_chart(fig, use_container_width=True)

            # Win Rate ısıl haritası
            st.markdown(f"**Win Rate Isıl Haritası — Tolerans %{tolerans_val}**")
            pivot_wr = df_t.pivot(index="ATR", columns="R:R", values="Win Rate (%)")
            pivot_wr = pivot_wr.sort_index(ascending=False)

            fig2 = go.Figure(go.Heatmap(
                z=pivot_wr.values,
                x=[f"R:R {c}" for c in pivot_wr.columns],
                y=[f"ATR {r}" for r in pivot_wr.index],
                colorscale="RdYlGn",
                zmin=20, zmax=70,
                text=[[f"{v:.1f}%" for v in row] for row in pivot_wr.values],
                texttemplate="%{text}",
                textfont={"size": 13, "color": "white"},
                hoverongaps=False,
                colorbar=dict(title="Win Rate %"),
            ))
            fig2.update_layout(
                template="plotly_dark", paper_bgcolor="#0d0f14",
                plot_bgcolor="#0d0f14", height=320,
                margin=dict(l=10, r=10, t=20, b=10),
                xaxis=dict(side="top"),
            )
            st.plotly_chart(fig2, use_container_width=True)

    # ─── EN İYİ / EN KÖTÜ ───────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("🏆 Öne Çıkan Kombinasyonlar")

    col1, col2, col3 = st.columns(3)

    best_getiri  = df_sonuc.loc[df_sonuc["Getiri (%)"].idxmax()]
    best_wr      = df_sonuc.loc[df_sonuc["Win Rate (%)"].idxmax()]
    worst_getiri = df_sonuc.loc[df_sonuc["Getiri (%)"].idxmin()]

    for col, baslik, satir, renk in [
        (col1, "📈 En Yüksek Getiri",   best_getiri,  "metric-pos"),
        (col2, "🎯 En Yüksek Win Rate", best_wr,      "metric-pos"),
        (col3, "📉 En Düşük Getiri",    worst_getiri, "metric-neg"),
    ]:
        col.markdown(f"**{baslik}**")
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Tolerans %{satir['Tolerans (%)']} | ATR {satir['ATR']} | R:R {satir['R:R']}</div>
            <div class="metric-value {renk}">{satir['Getiri (%)']:+.1f}%</div>
            <div class="metric-label" style="margin-top:6px">
                Win Rate: {satir['Win Rate (%)']:.1f}% &nbsp;|&nbsp;
                İşlem: {satir['Toplam İşlem']}
            </div>
        </div>""", unsafe_allow_html=True)

    # ─── CSV İNDİR ──────────────────────────────────────────────────────────────
    st.markdown("---")

    df_csv = df_sonuc[[
        "Tolerans (%)","ATR","R:R","Son Portföy (TL)","Getiri (%)","Win Rate (%)",
        "Toplam İşlem","Kazanan","Kaybeden","Atlanan Sinyal"
    ]].copy()

    csv_data = df_csv.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

    col_d, col_c = st.columns([1, 3])
    col_d.download_button(
        label="⬇️ CSV İndir",
        data=csv_data,
        file_name=f"sapan_kombinasyon_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.markdown("---")
    st.caption("⚠️ Bu analiz yatırım tavsiyesi değildir.")
