import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, date
import plotly.graph_objects as go
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Strateji Karşılaştırma",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .metric-card {
        background: #1e2433;
        border: 1px solid #2d3548;
        border-radius: 10px;
        padding: 14px 18px;
        text-align: center;
    }
    .metric-label { font-size: 11px; color: #8b95a8; margin-bottom: 4px; }
    .metric-value { font-size: 20px; font-weight: 700; }
    .metric-pos { color: #22c55e; }
    .metric-neg { color: #ef4444; }
    .metric-neu { color: #94a3b8; }
    .macd-color  { color: #38bdf8; }
    .sapan-color { color: #f59e0b; }
</style>
""", unsafe_allow_html=True)

# ─── HİSSE LİSTESİ ────────────────────────────────────────────────────────────
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

TOP50_MACD = {
    "POLTK","BMSTL","LIDER","AVTUR","MOBTL","ISCTR","DOAS","TRCAS","CMBTN","ISBTR",
    "LUKSK","DOHOL","DOCO","VBTYZ","MERIT","TEHOL","VAKKO","ALGYO","FRIGO","BMSCH",
    "HEDEF","ETILR","ASELS","ESCOM","AKSA","ULUUN","GRTHO","OYAKC","FMIZP","RYSAS",
    "KARSN","SMRVA","BRYAT","YAPRK","NETAS","SELEC","SAFKR","CELHA","ECILC","BURCE",
    "GLCVY","EGEEN","ACSEL","KUYAS","RYGYO","INDES","MAGEN","AKSEN","ARCLK","YYAPI",
}

TOP50_SAPAN = {
    "BURCE","BURVA","GRTHO","PASEU","CRDFA","BYDNR","BAHKM","BMSCH","AKSUE","ARSAN",
    "AKYHO","BRSAN","HEDEF","ISGSY","ICUGS","CRFSA","AVTUR","AKSA","KRGYO","BIGCH",
    "BRKVY","ETYAT","BORLS","BFREN","ULAS","AHGAZ","POLTK","BLCYT","BERA","KLRHO",
    "FLAP","OYAYO","DCTTR","IEYHO","ISKPL","CCOLA","GZNMI","KUVVA","HURGZ","ARENA",
    "RTALB","DYOBY","MANAS","DNISI","OZRDN","GLCVY","SANFM","TURGG","CVKMD","GUBRF",
}

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Ortak Parametreler")

    st.markdown("### 📅 Tarih Aralığı")
    c1, c2 = st.columns(2)
    bas_tarih = c1.date_input("Başlangıç", value=date(2020, 1, 1),
                               min_value=date(2010,1,1), max_value=date.today())
    bit_tarih = c2.date_input("Bitiş", value=date.today(),
                               min_value=date(2010,1,1), max_value=date.today())

    st.markdown("### 💰 Sermaye & Risk")
    baslangic   = st.number_input("Başlangıç Sermaye (₺)", value=1_000_000, step=50_000)
    risk_pct    = st.slider("İşlem Başına Risk (%)", 0.5, 5.0, 1.0, 0.1,
                            help="Her işlemde güncel sermayenin bu kadarı riske atılır.\n"
                                 "Lot = Risk₺ ÷ Stop Mesafesi")
    atr_per     = st.slider("ATR Periyodu", 7, 21, 14, 1)
    atr_kat     = st.slider("ATR Stop Çarpanı", 0.5, 3.0, 1.5, 0.5)
    rr_kat      = st.select_slider("R:R Katsayısı",
                   options=[1.0,1.5,2.0,2.5,3.0,3.5,4.0], value=3.0)

    st.markdown("### 📊 MACD Parametreleri")
    macd_h = st.slider("MACD Hızlı EMA",  5, 20, 12, 1)
    macd_y = st.slider("MACD Yavaş EMA", 10, 50, 26, 1)
    macd_s = st.slider("MACD Sinyal",     5, 20,  9, 1)
    hacim_carpan = st.slider("Hacim Çarpanı (MACD)", 1.0, 3.0, 1.5, 0.5)

    st.markdown("### 🪃 Sapan Parametreleri")
    ema_tolerans = st.slider("EMA Tolerans (%)", 1, 3, 2, 1) / 100

    st.markdown("### 🔍 Filtreler")
    endeks_aktif = st.checkbox("Endeks Filtresi (XU100 > EMA200)", value=True)

    calistir = st.button("🚀 Karşılaştırmayı Başlat", type="primary", use_container_width=True)

# ─── BAŞLIK ───────────────────────────────────────────────────────────────────
st.title("⚔️ Strateji Karşılaştırması")
st.caption("MACD Histogram Reversal  vs  Sapan Stratejisi  |  Ertesi Gün Açılışı  |  Fixed Risk Sizing")

# ─── YARDIMCI FONKSİYONLAR ────────────────────────────────────────────────────
def sq(s):
    if hasattr(s, "squeeze"): s = s.squeeze()
    if hasattr(s, "iloc") and s.ndim == 2: s = s.iloc[:, 0]
    return s

def toplu_veri_cek(sembol_listesi, bas, bit, batch_size=50):
    """
    Hisseleri batch'ler halinde toplu indirir.
    yf.download() tek istekte birden fazla ticker alabilir → çok daha hızlı.
    """
    tum_veriler = {}
    tikerler = [s + ".IS" for s in sembol_listesi]

    for i in range(0, len(tikerler), batch_size):
        batch = tikerler[i:i + batch_size]
        try:
            df_raw = yf.download(
                batch,
                start=str(bas), end=str(bit),
                interval="1d", progress=False,
                auto_adjust=True, group_by="ticker",
            )
            if df_raw is None or df_raw.empty:
                continue

            for ticker in batch:
                sembol = ticker.replace(".IS", "")
                try:
                    if len(batch) == 1:
                        df = df_raw.copy()
                    else:
                        if ticker not in df_raw.columns.get_level_values(0):
                            continue
                        df = df_raw[ticker].copy()

                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)

                    df = df[["Open","High","Low","Close","Volume"]].dropna()
                    if len(df) < 50:
                        continue

                    for col in df.columns:
                        df[col] = sq(df[col])
                    df.index = df.index.tz_localize(None)
                    tum_veriler[sembol] = df
                except Exception:
                    continue
        except Exception:
            continue

    return tum_veriler

def endeks_filtre(bas, bit):
    try:
        df = yf.download("XU100.IS",
                         start=(bas - pd.DateOffset(years=1)).strftime("%Y-%m-%d"),
                         end=str(bit), interval="1d", progress=False, auto_adjust=True)
        if df.empty: return {}
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.index = df.index.tz_localize(None)
        cl = sq(df["Close"])
        df["EMA200"] = cl.ewm(span=200, adjust=False).mean()
        df.dropna(subset=["EMA200"], inplace=True)
        return {row.Index.date(): float(row.Close) > float(row.EMA200)
                for row in df.itertuples()}
    except Exception: return {}

def ind_hesapla(df, atr_per, macd_h, macd_y, macd_s):
    """Her iki strateji için tüm indikatörleri tek seferde hesapla."""
    c = sq(df["Close"]); h = sq(df["High"])
    l = sq(df["Low"]);   v = sq(df["Volume"])

    for p in [20, 50, 100, 200]:
        df[f"EMA{p}"] = c.ewm(span=p, adjust=False).mean()

    # MACD
    ml          = c.ewm(span=macd_h, adjust=False).mean() - c.ewm(span=macd_y, adjust=False).mean()
    sig         = ml.ewm(span=macd_s, adjust=False).mean()
    df["MACD_HIS"] = ml - sig

    # Stochastic (5,3,3) — Sapan için
    ll = l.rolling(5).min(); hh = h.rolling(5).max()
    df["STOCH_K"] = ((c - ll) / (hh - ll + 1e-10) * 100).rolling(3).mean()

    # MACD(50,100) — Sapan için
    df["MACD_SAPAN"] = c.ewm(span=50, adjust=False).mean() - c.ewm(span=100, adjust=False).mean()

    # ATR
    hl = h - l
    hc = (h - c.shift(1)).abs()
    lc = (l - c.shift(1)).abs()
    df["ATR"]     = pd.concat([hl, hc, lc], axis=1).max(axis=1).rolling(atr_per).mean()
    df["VOL_ORT"] = v.rolling(20).mean()
    return df

def ema_dokunu(low, high, e20, e50, e100, e200, tol):
    for ev in [e20, e50, e100, e200]:
        if pd.isna(ev): continue
        if low <= ev * (1 + tol) and high >= ev * (1 - tol): return True
    return False

def higher_low(df, idx, lb=30):
    if idx < 2: return True
    rl = float(df["Low"].iloc[idx])
    sub = df["Low"].iloc[max(0, idx-lb):idx]
    if len(sub) == 0: return True
    if rl >= float(sub.min()): return True
    for col in ["EMA100","EMA200"]:
        if col in df.columns:
            ev = float(df[col].iloc[idx])
            if not pd.isna(ev) and rl <= ev * 1.02: return True
    return False

# ─── SİNYAL ÜRETİCİLERİ (her ikisi de: sinyal günü tespiti + ertesi gün Open) ─
def macd_sinyalleri(hisse_verileri, bas_ts, bit_ts, endeks_f, endeks_aktif,
                    atr_kat, rr_kat, hacim_carpan):
    gunluk = {}
    for sembol, df in hisse_verileri.items():
        for i in range(1, len(df) - 1):
            sinyal_gun = df.index[i]
            if sinyal_gun < bas_ts or sinyal_gun > bit_ts: continue
            if endeks_aktif and not endeks_f.get(sinyal_gun.date(), True): continue

            son    = df.iloc[i]
            onceki = df.iloc[i - 1]

            # EMA trend
            if not (float(son["EMA20"]) > float(son["EMA50"]) >
                    float(son["EMA100"]) > float(son["EMA200"])): continue
            # MACD histogram dönüşü
            if not (float(onceki["MACD_HIS"]) < 0 and float(son["MACD_HIS"]) > 0): continue
            # Hacim
            vol_ort = float(son["VOL_ORT"])
            if vol_ort > 0 and float(son["Volume"]) < vol_ort * hacim_carpan: continue
            # Fiyat > EMA20
            if float(son["Close"]) <= float(son["EMA20"]): continue

            # Giriş: ertesi gün open
            giris_gun = df.index[i + 1]
            giris     = float(df.iloc[i + 1]["Open"])
            atr_v     = float(son["ATR"])
            if pd.isna(atr_v) or atr_v <= 0: continue
            stop  = giris - atr_kat * atr_v
            hedef = giris + (giris - stop) * rr_kat
            if giris - stop <= 0: continue

            if giris_gun not in gunluk: gunluk[giris_gun] = []
            gunluk[giris_gun].append({
                "sembol": sembol, "giris": giris,
                "stop": stop, "hedef": hedef,
                "stop_mesafe": giris - stop,
                "top50": sembol in TOP50_MACD,
            })
    return gunluk

def sapan_sinyalleri(hisse_verileri, bas_ts, bit_ts, endeks_f, endeks_aktif,
                     atr_kat, rr_kat, ema_tolerans):
    gunluk = {}
    for sembol, df in hisse_verileri.items():
        for i in range(2, len(df) - 1):
            sinyal_gun = df.index[i]
            if sinyal_gun < bas_ts or sinyal_gun > bit_ts: continue
            if endeks_aktif and not endeks_f.get(sinyal_gun.date(), True): continue

            son        = df.iloc[i]
            onceki     = df.iloc[i - 1]

            # EMA trend
            if not (float(son["EMA20"]) > float(son["EMA50"]) >
                    float(son["EMA100"]) > float(son["EMA200"])): continue
            # Stoch < 30
            if float(onceki["STOCH_K"]) >= 30: continue
            # MACD filtresi
            macd_vals = df["MACD_SAPAN"].iloc[max(0,i-5):i]
            if not (float(son["MACD_SAPAN"]) > 0 or (macd_vals < 0).sum() < 5): continue
            # Onay mumu
            if float(son["Close"]) <= float(son["Open"]): continue
            if float(son["Close"]) <= float(onceki["High"]): continue
            # EMA dokunuşu
            if not ema_dokunu(
                float(onceki["Low"]), float(onceki["High"]),
                float(onceki["EMA20"]), float(onceki["EMA50"]),
                float(onceki["EMA100"]), float(onceki["EMA200"]),
                ema_tolerans
            ): continue
            # Higher Low
            if not higher_low(df, i - 1): continue

            # Giriş: ertesi gün open
            giris_gun = df.index[i + 1]
            giris     = float(df.iloc[i + 1]["Open"])
            atr_v     = float(son["ATR"])
            if pd.isna(atr_v) or atr_v <= 0: continue
            stop  = giris - atr_kat * atr_v
            hedef = giris + (giris - stop) * rr_kat
            if giris - stop <= 0: continue

            if giris_gun not in gunluk: gunluk[giris_gun] = []
            gunluk[giris_gun].append({
                "sembol": sembol, "giris": giris,
                "stop": stop, "hedef": hedef,
                "stop_mesafe": giris - stop,
                "top50": sembol in TOP50_SAPAN,
            })
    return gunluk

# ─── PORTFÖY SİMÜLASYONU (Fixed Risk Sizing) ──────────────────────────────────
def portfoy_sim(gunluk_sinyaller, hisse_verileri, bas_ts, bit_ts,
                baslangic, risk_pct):
    """
    Fixed Risk Sizing:
      risk_tl  = güncel_sermaye × risk_pct/100
      lot      = risk_tl / stop_mesafe
      poz_tl   = lot × giriş_fiyatı
      poz_tl > kalan_sermaye → atla
    """
    sermaye  = float(baslangic)
    aktif    = []
    islemler = []
    equity   = {}

    tum_tarihler = sorted(set(
        d for df in hisse_verileri.values()
        for d in df.index if bas_ts <= d <= bit_ts
    ))

    # Giriş tarihine göre indeksle
    giris_harita = {}
    for tarih, liste in gunluk_sinyaller.items():
        if bas_ts <= tarih <= bit_ts:
            giris_harita[tarih] = sorted(liste, key=lambda x: not x["top50"])

    for tarih in tum_tarihler:
        # 1. Açık pozisyonları kontrol et
        hala_acik = []
        for poz in aktif:
            df = hisse_verileri.get(poz["sembol"])
            if df is None:
                hala_acik.append(poz); continue
            gun = df[df.index == tarih]
            if gun.empty:
                hala_acik.append(poz); continue

            lo = float(gun.iloc[0]["Low"])
            hi = float(gun.iloc[0]["High"])
            sonuc = cikis = None

            if lo <= poz["stop"]:
                sonuc = "STOP";  cikis = poz["stop"]
            elif hi >= poz["hedef"]:
                sonuc = "HEDEF"; cikis = poz["hedef"]

            if sonuc:
                kz = (cikis - poz["giris"]) * poz["lot"]
                sermaye += poz["poz_tl"] + kz
                islemler.append({
                    "Hisse":         poz["sembol"],
                    "Giriş Günü":    poz["giris_gun"].date(),
                    "Çıkış Günü":    tarih.date(),
                    "Giriş ₺":       round(poz["giris"],    2),
                    "Stop ₺":        round(poz["stop"],     2),
                    "Hedef ₺":       round(poz["hedef"],    2),
                    "Çıkış Fiyat":   round(cikis,           2),
                    "Lot":           round(poz["lot"],       0),
                    "Pozisyon ₺":    round(poz["poz_tl"],   0),
                    "Riske Atılan ₺":round(poz["risk_tl"],  0),
                    "Kar/Zarar ₺":   round(kz,              0),
                    "Getiri%":       round((cikis-poz["giris"])/poz["giris"]*100, 2),
                    "Sonuç":         sonuc,
                })
            else:
                hala_acik.append(poz)
        aktif = hala_acik

        # 2. Yeni giriş
        if tarih in giris_harita:
            for sin in giris_harita[tarih]:
                if any(p["sembol"] == sin["sembol"] for p in aktif): continue
                risk_tl = sermaye * (risk_pct / 100)
                lot     = risk_tl / sin["stop_mesafe"]
                poz_tl  = lot * sin["giris"]
                if poz_tl > sermaye or sermaye <= 0: continue
                sermaye -= poz_tl
                aktif.append({
                    "sembol":    sin["sembol"],
                    "giris_gun": tarih,
                    "giris":     sin["giris"],
                    "stop":      sin["stop"],
                    "hedef":     sin["hedef"],
                    "lot":       lot,
                    "poz_tl":    poz_tl,
                    "risk_tl":   risk_tl,
                })

        # 3. Equity kaydı
        acik_deger = sum(
            poz["lot"] * float(hisse_verileri[poz["sembol"]].loc[tarih, "Close"])
            if tarih in hisse_verileri.get(poz["sembol"], pd.DataFrame()).index
            else poz["poz_tl"]
            for poz in aktif
        )
        equity[tarih] = sermaye + acik_deger

    # Açık kalan pozisyonları son kapanışa kapat
    for poz in aktif:
        df = hisse_verileri.get(poz["sembol"])
        if df is None or df.empty: continue
        cikis = float(df.iloc[-1]["Close"])
        kz    = (cikis - poz["giris"]) * poz["lot"]
        sermaye += poz["poz_tl"] + kz
        islemler.append({
            "Hisse":         poz["sembol"],
            "Giriş Günü":    poz["giris_gun"].date(),
            "Çıkış Günü":    df.index[-1].date(),
            "Giriş ₺":       round(poz["giris"],    2),
            "Stop ₺":        round(poz["stop"],     2),
            "Hedef ₺":       round(poz["hedef"],    2),
            "Çıkış Fiyat":   round(cikis,           2),
            "Lot":           round(poz["lot"],       0),
            "Pozisyon ₺":    round(poz["poz_tl"],   0),
            "Riske Atılan ₺":round(poz["risk_tl"],  0),
            "Kar/Zarar ₺":   round(kz,              0),
            "Getiri%":       round((cikis-poz["giris"])/poz["giris"]*100, 2),
            "Sonuç":         "AÇIK",
        })

    return pd.DataFrame(islemler), pd.Series(equity).sort_index()

def metrik_hesapla(df, equity, baslangic):
    if df.empty:
        return {k: 0 for k in ["toplam","wr","pf","getiri","net_kz","max_dd",
                                "ort_kz","kazanan","kaybeden"]}
    tamam    = df[df["Sonuç"].isin(["HEDEF","STOP"])]
    kaz      = tamam[tamam["Sonuç"] == "HEDEF"]
    kay      = tamam[tamam["Sonuç"] == "STOP"]
    toplam   = len(tamam)
    wr       = len(kaz) / toplam * 100 if toplam > 0 else 0
    kaz_sum  = kaz["Kar/Zarar ₺"].sum()
    kay_sum  = abs(kay["Kar/Zarar ₺"].sum())
    pf       = kaz_sum / kay_sum if kay_sum > 0 else float("inf")
    son_s    = equity.iloc[-1] if len(equity) > 0 else baslangic
    getiri   = (son_s / baslangic - 1) * 100
    net_kz   = df["Kar/Zarar ₺"].sum()
    peak     = equity.cummax()
    max_dd   = ((equity - peak) / peak * 100).min() if len(equity) > 0 else 0
    ort_kz   = df["Kar/Zarar ₺"].mean()
    return {
        "toplam": toplam, "wr": wr, "pf": pf, "getiri": getiri,
        "net_kz": net_kz, "max_dd": max_dd, "ort_kz": ort_kz,
        "kazanan": len(kaz), "kaybeden": len(kay),
        "son_sermaye": son_s,
    }

def metrik_kart(col, label, macd_val, sapan_val, fmt="{:.1f}", suffix=""):
    m_str = fmt.format(macd_val)  + suffix
    s_str = fmt.format(sapan_val) + suffix
    m_renk = ("metric-pos" if macd_val  > 0 else "metric-neg") if suffix in ["%","₺"] else "metric-neu"
    s_renk = ("metric-pos" if sapan_val > 0 else "metric-neg") if suffix in ["%","₺"] else "metric-neu"
    col.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div style="display:flex;justify-content:space-around;margin-top:6px">
            <div>
                <div class="metric-label" style="color:#38bdf8">📊 MACD</div>
                <div class="metric-value {m_renk}">{m_str}</div>
            </div>
            <div style="border-left:1px solid #2d3548;margin:0 8px"></div>
            <div>
                <div class="metric-label" style="color:#f59e0b">🪃 Sapan</div>
                <div class="metric-value {s_renk}">{s_str}</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

# ─── ANA AKIŞ ─────────────────────────────────────────────────────────────────
if calistir:
    bas_ts   = pd.Timestamp(bas_tarih)
    bit_ts   = pd.Timestamp(bit_tarih)
    veri_bas = bas_ts - pd.DateOffset(years=1)
    veri_bit = bit_ts + pd.DateOffset(days=2)

    # Endeks
    endeks_f = {}
    if endeks_aktif:
        with st.spinner("Endeks verisi indiriliyor..."):
            endeks_f = endeks_filtre(bas_ts, veri_bit)

    # Veri indir & indikatör hesapla (toplu indirme)
    hisse_verileri = {}
    BATCH = 50
    n_batch = (len(BIST_HISSELER) + BATCH - 1) // BATCH
    bar   = st.progress(0, text="Hisseler toplu indiriliyor...")
    durum = st.empty()

    for bi in range(n_batch):
        batch_semboller = BIST_HISSELER[bi*BATCH : (bi+1)*BATCH]
        bar.progress(
            (bi+1)/n_batch,
            text=f"Batch {bi+1}/{n_batch} indiriliyor... "
                 f"({bi*BATCH+1}–{min((bi+1)*BATCH, len(BIST_HISSELER))}/{len(BIST_HISSELER)})"
        )
        ham = toplu_veri_cek(
            batch_semboller,
            veri_bas.to_pydatetime().date(),
            veri_bit.to_pydatetime().date(),
            batch_size=BATCH,
        )
        for sembol, df_raw in ham.items():
            try:
                df = ind_hesapla(df_raw.copy(), atr_per, macd_h, macd_y, macd_s)
                df.dropna(subset=["EMA200","MACD_HIS","STOCH_K","ATR","VOL_ORT"], inplace=True)
                if len(df) >= 50:
                    hisse_verileri[sembol] = df
            except Exception:
                continue

    bar.empty()
    durum.empty()
    st.success(f"✅ {len(hisse_verileri)} hisse yüklendi ({n_batch} batch).")

    # Sinyaller
    with st.spinner("MACD sinyalleri üretiliyor..."):
        macd_gun = macd_sinyalleri(
            hisse_verileri, bas_ts, bit_ts, endeks_f, endeks_aktif,
            atr_kat, rr_kat, hacim_carpan)

    with st.spinner("Sapan sinyalleri üretiliyor..."):
        sapan_gun = sapan_sinyalleri(
            hisse_verileri, bas_ts, bit_ts, endeks_f, endeks_aktif,
            atr_kat, rr_kat, ema_tolerans)

    macd_sig_sayi  = sum(len(v) for v in macd_gun.values())
    sapan_sig_sayi = sum(len(v) for v in sapan_gun.values())
    st.info(f"📡 MACD: **{macd_sig_sayi}** sinyal  |  🪃 Sapan: **{sapan_sig_sayi}** sinyal")

    # Portföy simülasyonu
    with st.spinner("MACD portföy simülasyonu..."):
        df_macd, eq_macd = portfoy_sim(
            macd_gun, hisse_verileri, bas_ts, bit_ts, baslangic, risk_pct)

    with st.spinner("Sapan portföy simülasyonu..."):
        df_sapan, eq_sapan = portfoy_sim(
            sapan_gun, hisse_verileri, bas_ts, bit_ts, baslangic, risk_pct)

    st.session_state.update({
        "df_macd": df_macd, "eq_macd": eq_macd,
        "df_sapan": df_sapan, "eq_sapan": eq_sapan,
        "baslangic": baslangic,
    })

# ─── SONUÇLAR ─────────────────────────────────────────────────────────────────
if "df_macd" in st.session_state:
    df_macd  = st.session_state["df_macd"]
    eq_macd  = st.session_state["eq_macd"]
    df_sapan = st.session_state["df_sapan"]
    eq_sapan = st.session_state["eq_sapan"]
    baslangic= st.session_state["baslangic"]

    m = metrik_hesapla(df_macd,  eq_macd,  baslangic)
    s = metrik_hesapla(df_sapan, eq_sapan, baslangic)

    st.markdown("---")
    st.subheader("📊 Karşılaştırma Özeti")

    c1,c2,c3,c4 = st.columns(4)
    metrik_kart(c1, "Portföy Getirisi",  m["getiri"],    s["getiri"],    "{:+.1f}", "%")
    metrik_kart(c2, "Net Kar/Zarar",     m["net_kz"],    s["net_kz"],    "{:+,.0f}", "₺")
    metrik_kart(c3, "Win Rate",          m["wr"],        s["wr"],        "{:.1f}", "%")
    metrik_kart(c4, "Profit Factor",     m["pf"],        s["pf"],        "{:.2f}", "")

    st.markdown("")
    c5,c6,c7,c8 = st.columns(4)
    metrik_kart(c5, "Max Drawdown",      m["max_dd"],    s["max_dd"],    "{:.1f}", "%")
    metrik_kart(c6, "Toplam İşlem",      m["toplam"],    s["toplam"],    "{:.0f}", "")
    metrik_kart(c7, "Kazanan / Kaybeden",
                m["kazanan"], s["kazanan"], "{:.0f}", "")
    metrik_kart(c8, "Ort. Kar/Zarar ₺",  m["ort_kz"],   s["ort_kz"],    "{:+,.0f}", "₺")

    # ── Equity Curve ──────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📉 Portföy Büyüme Eğrisi")

    fig = go.Figure()
    if len(eq_macd) > 1:
        fig.add_trace(go.Scatter(
            x=eq_macd.index, y=eq_macd.values,
            mode="lines", name="📊 MACD",
            line=dict(color="#38bdf8", width=2),
            fill="tozeroy", fillcolor="rgba(56,189,248,0.05)"
        ))
    if len(eq_sapan) > 1:
        fig.add_trace(go.Scatter(
            x=eq_sapan.index, y=eq_sapan.values,
            mode="lines", name="🪃 Sapan",
            line=dict(color="#f59e0b", width=2),
            fill="tozeroy", fillcolor="rgba(245,158,11,0.05)"
        ))
    fig.add_hline(y=baslangic, line_dash="dash", line_color="#64748b",
                  annotation_text=f"Başlangıç: {baslangic:,.0f}₺")
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="#0d0f14",
        plot_bgcolor="#0d0f14", height=420,
        margin=dict(l=10,r=10,t=20,b=10),
        yaxis=dict(gridcolor="#1e293b", tickformat=",.0f", ticksuffix="₺"),
        xaxis=dict(gridcolor="#1e293b"),
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Aylık Isı Haritaları ──────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("🗓️ Aylık Kar/Zarar Isı Haritaları (₺)")
    tab_m, tab_s = st.tabs(["📊 MACD", "🪃 Sapan"])

    def isi_haritasi(df_ist, title, renk):
        if df_ist.empty:
            st.info("Veri yok.")
            return
        df_ist = df_ist.copy()
        df_ist["_yil"] = df_ist["Giriş Günü"].apply(lambda x: x.year)
        df_ist["_ay"]  = df_ist["Giriş Günü"].apply(lambda x: x.month)
        pivot = df_ist.pivot_table(
            values="Kar/Zarar ₺", index="_yil", columns="_ay", aggfunc="sum")
        ay = {1:"Oca",2:"Şub",3:"Mar",4:"Nis",5:"May",6:"Haz",
              7:"Tem",8:"Ağu",9:"Eyl",10:"Eki",11:"Kas",12:"Ara"}
        pivot.columns = [ay.get(c,c) for c in pivot.columns]
        pivot.index   = [str(y) for y in pivot.index]
        import numpy as np
        z   = pivot.values
        txt = [[f"{v:,.0f}₺" if not np.isnan(v) else "" for v in row] for row in z]
        fig2 = go.Figure(go.Heatmap(
            z=z, x=list(pivot.columns), y=list(pivot.index),
            text=txt, texttemplate="%{text}",
            colorscale=[[0,"#b71c1c"],[0.45,"#ef9a9a"],
                        [0.5,"#1e2433"],[0.55,"#a5d6a7"],[1,"#1b5e20"]],
            zmid=0, showscale=True, colorbar=dict(title="₺"),
        ))
        fig2.update_layout(
            template="plotly_dark", paper_bgcolor="#0d0f14",
            plot_bgcolor="#0d0f14",
            height=max(300, len(pivot.index)*48+100),
            margin=dict(l=60,r=40,t=30,b=40),
            title=title,
        )
        st.plotly_chart(fig2, use_container_width=True)

    with tab_m:
        isi_haritasi(df_macd,  "MACD — Aylık Kar/Zarar", "#38bdf8")
    with tab_s:
        isi_haritasi(df_sapan, "Sapan — Aylık Kar/Zarar", "#f59e0b")

    # ── İşlem Tabloları ───────────────────────────────────────────────────────
    st.markdown("---")
    tab_im, tab_is, tab_csv = st.tabs(["📋 MACD İşlemleri", "📋 Sapan İşlemleri", "⬇️ CSV"])

    with tab_im:
        if not df_macd.empty:
            st.dataframe(df_macd, use_container_width=True, hide_index=True)
        else:
            st.info("İşlem yok.")

    with tab_is:
        if not df_sapan.empty:
            st.dataframe(df_sapan, use_container_width=True, hide_index=True)
        else:
            st.info("İşlem yok.")

    with tab_csv:
        col1, col2 = st.columns(2)
        if not df_macd.empty:
            col1.download_button(
                "⬇️ MACD İşlemleri CSV",
                df_macd.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
                file_name=f"macd_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv", use_container_width=True,
            )
        if not df_sapan.empty:
            col2.download_button(
                "⬇️ Sapan İşlemleri CSV",
                df_sapan.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
                file_name=f"sapan_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv", use_container_width=True,
            )

    st.markdown("---")
    st.caption("⚠️ Bu analiz yatırım tavsiyesi değildir.")

else:
    st.info("👈 Sol panelden parametreleri ayarlayın ve **Karşılaştırmayı Başlat** butonuna basın.")
    st.markdown("""
    ### ⚔️ Karşılaştırma Mantığı

    | | 📊 MACD Stratejisi | 🪃 Sapan Stratejisi |
    |---|---|---|
    | **Sinyal** | MACD Histogram dönüşü | EMA dokunuşu + Price Action + Higher Low |
    | **Filtreler** | EMA trend + Hacim + Fiyat>EMA20 | EMA trend + Stoch<30 + MACD(50,100) |
    | **Giriş** | ⭐ Ertesi gün Open | ⭐ Ertesi gün Open |
    | **Stop** | Giriş − ATR×çarpan | Giriş − ATR×çarpan |
    | **Hedef** | Stop mesafesi × R:R | Stop mesafesi × R:R |
    | **Risk Modeli** | ⭐ Fixed Risk Sizing | ⭐ Fixed Risk Sizing |
    | **Sermaye Kontrolü** | Nakit yoksa atla | Nakit yoksa atla |

    **Adil karşılaştırma için her iki strateji:**
    - Aynı veri, aynı tarih aralığı
    - Aynı risk modeli (Fixed Risk Sizing)
    - Aynı giriş mantığı (ertesi gün açılış)
    - Aynı ATR ve R:R parametreleri
    """)
