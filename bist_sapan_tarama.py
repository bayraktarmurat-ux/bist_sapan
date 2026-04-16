import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─── SAYFA AYARLARI ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BIST Sapan Stratejisi",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── HİSSE LİSTESİ ────────────────────────────────────────────────────────────
# TOP50 — Sapan Stratejisi backtest sonuçlarına göre en iyi 50 hisse
# Sıralama: Toplam K/Z (2022-2026 backtest)
TOP50 = {
    "BURCE","BURVA","GRTHO","PASEU","CRDFA","BYDNR","BAHKM","BMSCH","AKSUE","ARSAN",
    "AKYHO","BRSAN","HEDEF","ISGSY","ICUGS","CRFSA","AVTUR","AKSA","KRGYO","BIGCH",
    "BRKVY","ETYAT","BORLS","BFREN","ULAS","AHGAZ","POLTK","BLCYT","BERA","KLRHO",
    "FLAP","OYAYO","DCTTR","IEYHO","ISKPL","CCOLA","GZNMI","KUVVA","HURGZ","ARENA",
    "RTALB","DYOBY","MANAS","DNISI","OZRDN","GLCVY","SANFM","TURGG","CVKMD","GUBRF",
}

HISSELER = [
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

# ─── YARDIMCI FONKSİYONLAR ────────────────────────────────────────────────────
def squeeze(s):
    if hasattr(s, "squeeze"):
        s = s.squeeze()
    if hasattr(s, "iloc") and s.ndim == 2:
        s = s.iloc[:, 0]
    return s

def ema(seri, periyot):
    return squeeze(seri).ewm(span=periyot, adjust=False).mean()

def atr_hesapla(df, periyot=14):
    close = squeeze(df["Close"])
    high  = squeeze(df["High"])
    low   = squeeze(df["Low"])
    hl = high - low
    hc = (high - close.shift(1)).abs()
    lc = (low  - close.shift(1)).abs()
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    return tr.ewm(span=periyot, adjust=False).mean()

def veri_cek(ticker, gun=300):
    try:
        df = yf.download(ticker + ".IS", period=f"{gun}d",
                         interval="1d", progress=False, auto_adjust=True)
        if df.empty or len(df) < 60:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df[["Open","High","Low","Close","Volume"]].dropna()
        for col in df.columns:
            df[col] = squeeze(df[col])
        return df
    except Exception:
        return None

# ─── ENDEKS FİLTRESİ ──────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def endeks_kontrol():
    for sembol in ["XU100.IS", "^XU100", "BIST100.IS"]:
        try:
            df = yf.download(sembol, period="300d",
                             interval="1d", progress=False, auto_adjust=True)
            if df.empty or len(df) < 10:
                continue
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            for col in df.columns:
                df[col] = squeeze(df[col])
            df["EMA200"] = df["Close"].ewm(span=200, adjust=False).mean()
            df.dropna(subset=["EMA200"], inplace=True)
            if df.empty: continue
            son      = df.iloc[-1]
            kapanis  = float(son["Close"])
            ema200   = float(son["EMA200"])
            aktif    = kapanis > ema200
            fark_pct = (kapanis - ema200) / ema200 * 100
            return aktif, kapanis, ema200, fark_pct
        except Exception:
            continue
    return None, None, None, None

# ─── STOCHASTIC HESAPLA ────────────────────────────────────────────────────────
def stochastic_hesapla(df, k=5, d=3, smooth=3):
    high  = squeeze(df["High"])
    low   = squeeze(df["Low"])
    close = squeeze(df["Close"])
    lowest_low   = low.rolling(k).min()
    highest_high = high.rolling(k).max()
    stoch_k = 100 * (close - lowest_low) / (highest_high - lowest_low + 1e-10)
    stoch_k_smooth = stoch_k.rolling(d).mean()
    stoch_d = stoch_k_smooth.rolling(smooth).mean()
    return stoch_k_smooth, stoch_d

# ─── MACD HESAPLA ─────────────────────────────────────────────────────────────
def macd_hesapla(close, hizli=50, yavas=100, sinyal=9):
    close = squeeze(close)
    ema_h = close.ewm(span=hizli,  adjust=False).mean()
    ema_y = close.ewm(span=yavas,  adjust=False).mean()
    macd      = ema_h - ema_y
    macd_sig  = macd.ewm(span=sinyal, adjust=False).mean()
    macd_his  = macd - macd_sig
    return macd, macd_sig, macd_his

# ─── EMA DOKUNUŞ KONTROLÜ ─────────────────────────────────────────────────────
def ema_dokunusu_var_mi(low_val, high_val, ema20, ema50, ema100, ema200, tolerans=0.02):
    """Mumun fitilinin herhangi bir EMA'ya dokunup dokunmadığını kontrol eder."""
    for ema_val in [ema20, ema50, ema100, ema200]:
        if pd.isna(ema_val):
            continue
        # Mumun low-high aralığı EMA'yı kapsıyor mu?
        band_low  = ema_val * (1 - tolerans)
        band_high = ema_val * (1 + tolerans)
        if low_val <= band_high and high_val >= band_low:
            return True, ema_val
    return False, None

# ─── HIGHER LOW KONTROLÜ ──────────────────────────────────────────────────────
def higher_low_kontrol(df, reversal_idx, lookback=30):
    """
    Dönüş mumunun dibi > son dip mi?
    İstisna: Dönüş dibi < son dip ama daha derin EMA'ya dokunmuşsa geçerli.
    """
    if reversal_idx < 2:
        return True  # Yeterli veri yok, geç

    reversal_low = float(df["Low"].iloc[reversal_idx])

    # Son dipi bul (reversal_idx öncesi son yerel dip)
    sub = df["Low"].iloc[max(0, reversal_idx-lookback):reversal_idx]
    if len(sub) == 0:
        return True
    son_dip = float(sub.min())

    if reversal_low >= son_dip:
        return True  # Higher low — geçerli

    # İstisna: Daha derin EMA'ya dokunmuş mu?
    ema100_val = float(df["EMA100"].iloc[reversal_idx]) if "EMA100" in df.columns else None
    ema200_val = float(df["EMA200"].iloc[reversal_idx]) if "EMA200" in df.columns else None
    for ema_val in [ema100_val, ema200_val]:
        if ema_val is None or pd.isna(ema_val):
            continue
        if reversal_low <= ema_val * 1.02:  # EMA'ya dokunmuş
            return True  # İstisna — geçerli

    return False  # Lower low ve EMA desteği yok — elendi

# ─── YAKIN DİRENÇ KONTROLÜ ───────────────────────────────────────────────────
def yakin_direnc_var_mi(df, giris_fiyati, lookback=60, tolerans=0.05):
    """Son N günün pivot yükseklerinden giriş fiyatına yakın direnç var mı?"""
    highs = squeeze(df["High"]).iloc[-lookback:]
    # Yerel zirveler: her iki tarafından yüksek olan mumlar
    pivot_highs = []
    for i in range(2, len(highs)-2):
        if highs.iloc[i] > highs.iloc[i-1] and highs.iloc[i] > highs.iloc[i+1] and \
           highs.iloc[i] > highs.iloc[i-2] and highs.iloc[i] > highs.iloc[i+2]:
            pivot_highs.append(float(highs.iloc[i]))

    for ph in pivot_highs:
        if giris_fiyati < ph <= giris_fiyati * (1 + tolerans):
            return True
    return False

# ─── RANGE İÇİNDE Mİ KONTROLÜ ────────────────────────────────────────────────
def range_icinde_mi(df, lookback=20, esik=0.08):
    """Son N günde fiyat dar bir bantta sıkışmış mı?"""
    closes = squeeze(df["Close"]).iloc[-lookback:]
    if len(closes) < lookback:
        return False
    band = (closes.max() - closes.min()) / closes.mean()
    return band < esik

# ─── YUMUŞAK DÜZELTME KONTROLÜ ───────────────────────────────────────────────
def yumusak_duzeltme_mi(df, reversal_idx, lookback=10, max_dusus=0.08):
    """Dönüş öncesi sert çakılma yok mu? (Kalite puanı)"""
    start = max(0, reversal_idx - lookback)
    sub   = squeeze(df["Close"]).iloc[start:reversal_idx+1]
    if len(sub) < 2:
        return False
    max_dusus_gercek = (sub.max() - sub.min()) / sub.max()
    return max_dusus_gercek < max_dusus

# ─── V DÖNÜŞ KONTROLÜ ────────────────────────────────────────────────────────
def v_donusu_mu(df, reversal_idx, onceki_gun=5, min_dusus=0.04):
    """Dönüşten önce sert düşüş var mı ve dönüş mumu büyük yeşil mi? (Kalite puanı)"""
    if reversal_idx < onceki_gun:
        return False
    sub_close = squeeze(df["Close"]).iloc[reversal_idx-onceki_gun:reversal_idx+1]
    dusus = (sub_close.max() - sub_close.min()) / sub_close.max()
    # Dönüş mumu büyük yeşil mi?
    rev_open  = float(df["Open"].iloc[reversal_idx])
    rev_close = float(df["Close"].iloc[reversal_idx])
    rev_atr   = float(df["ATR"].iloc[reversal_idx]) if "ATR" in df.columns else 0
    buyuk_yesil = (rev_close > rev_open) and (rev_close - rev_open) > rev_atr * 0.5
    return dusus >= min_dusus and buyuk_yesil

# ─── YÜKSELEN DİPLER ZİNCİRİ ─────────────────────────────────────────────────
def yukselen_dipler_guclu_mu(df, reversal_idx, lookback=30):
    """Son dönüş dahil en az 2 ardışık higher low var mı? (Kalite puanı)"""
    if reversal_idx < 10:
        return False
    sub_low = squeeze(df["Low"]).iloc[max(0, reversal_idx-lookback):reversal_idx+1]
    # Yerel dipleri bul
    dipler = []
    for i in range(1, len(sub_low)-1):
        if sub_low.iloc[i] < sub_low.iloc[i-1] and sub_low.iloc[i] < sub_low.iloc[i+1]:
            dipler.append(float(sub_low.iloc[i]))
    if len(dipler) < 2:
        return False
    # Son iki dip yükselen mi?
    return dipler[-1] > dipler[-2]

# ─── ANA SİNYAL FONKSİYONU ────────────────────────────────────────────────────
def sinyal_tara(df, params):
    """
    SAPAN STRATEJİSİ:
    1. EMA20 > EMA50 > EMA100 > EMA200
    2. Fiyat herhangi bir EMA'ya dokunmuş
    3. Stochastic (5,3,3) < 30
    4. MACD (50,100,9) pozitif VEYA 5 mumdan az negatif
    5. Price action: 2 mum dönüş (orjinal/iç/gövde deliş) veya pin bar + onay
    6. Higher low (dönüş dibi > son dip) — istisna: derin EMA dokunuşu
    """
    ema_tolerans = params["ema_tolerans"]
    df = df.copy()
    for col in ["Open","High","Low","Close","Volume"]:
        if col in df.columns:
            df[col] = squeeze(df[col])

    close  = df["Close"]
    high   = df["High"]
    low    = df["Low"]
    open_  = df["Open"]

    # EMA'lar
    df["EMA20"]  = ema(close, 20)
    df["EMA50"]  = ema(close, 50)
    df["EMA100"] = ema(close, 100)
    df["EMA200"] = ema(close, 200)
    df["ATR"]    = atr_hesapla(df, 14)

    # Stochastic
    df["STOCH_K"], df["STOCH_D"] = stochastic_hesapla(df, 5, 3, 3)

    # MACD (50, 100, 9)
    df["MACD"], df["MACD_SIG"], df["MACD_HIS"] = macd_hesapla(close, 50, 100, 9)

    df.dropna(subset=["EMA200","ATR","STOCH_K","MACD"], inplace=True)
    if len(df) < 3:
        return None, "veri_yetersiz"

    son    = df.iloc[-1]
    onceki = df.iloc[-2]
    iki_onceki = df.iloc[-3]

    # ── FİLTRE 1: EMA Trend ──────────────────────────────────────────────────
    if not (float(son["EMA20"]) > float(son["EMA50"]) >
            float(son["EMA100"]) > float(son["EMA200"])):
        return None, "trend"

    # ── FİLTRE 3: Stochastic < 30 ────────────────────────────────────────────
    # Dönüş mumunda (onceki) stoch < 30 olmalı
    if float(onceki["STOCH_K"]) >= 30:
        return None, "stoch"

    # ── FİLTRE 4: MACD ───────────────────────────────────────────────────────
    # MACD pozitif VEYA son 5 mumda negatife dönmüş (5'ten az süredir negatif)
    macd_vals = df["MACD"].iloc[-6:-1]  # son 5 mum
    macd_pozitif = float(son["MACD"]) > 0
    negatif_sure = (macd_vals < 0).sum()
    if not macd_pozitif and negatif_sure >= 5:
        return None, "macd"

    # ── FİLTRE 5 & 2 & 6: Price Action Formasyonu ────────────────────────────
    # Onay mumu = son mum (son), dönüş mumu = onceki
    # Onay mumu mutlaka boğa (yeşil) olmalı
    onay_yesil = float(son["Close"]) > float(son["Open"])
    if not onay_yesil:
        return None, "pa_onay"

    # Onay mumu, dönüş mumunun high'ını kırmalı
    onay_kirilim = float(son["Close"]) > float(onceki["High"])
    if not onay_kirilim:
        return None, "pa_kirilim"

    reversal_idx = len(df) - 2  # onceki = dönüş mumu indeksi

    # Dönüş mumunun EMA'ya dokunuşu
    dokundu, dokunulan_ema = ema_dokunusu_var_mi(
        float(onceki["Low"]), float(onceki["High"]),
        float(onceki["EMA20"]), float(onceki["EMA50"]),
        float(onceki["EMA100"]), float(onceki["EMA200"]),
        tolerans=ema_tolerans
    )
    if not dokundu:
        return None, "ema_dokunusu"

    # Formasyon tipi tespiti
    formasyon = None

    # Pin bar tespiti (tek mum dönüş):
    # Gövde küçük, alt fitil uzun (gövdenin en az 2 katı)
    rev_govde = abs(float(onceki["Close"]) - float(onceki["Open"]))
    rev_alt_fitil = float(onceki["Open" if float(onceki["Close"]) > float(onceki["Open"]) else "Close"]) - float(onceki["Low"])
    rev_ust_fitil = float(onceki["High"]) - float(onceki["Close"] if float(onceki["Close"]) > float(onceki["Open"]) else onceki["Open"])
    rev_range = float(onceki["High"]) - float(onceki["Low"])

    if rev_range > 0:
        alt_fitil_oran = rev_alt_fitil / rev_range
        govde_oran     = rev_govde / rev_range if rev_range > 0 else 1

        if alt_fitil_oran >= 0.5 and govde_oran <= 0.35:
            formasyon = "Pin Bar"
        else:
            # 2 mum dönüş varyantları
            # Orjinal: dönüş mumu kırmızı, gövde EMA üstünde kapanmış
            rev_kirmizi = float(onceki["Close"]) < float(onceki["Open"])
            govde_ema_ustu = float(onceki["Close"]) > float(onceki["EMA20"]) * 0.98

            # Gövde deliş: gövde EMA'yı deler
            govde_dusuk = min(float(onceki["Open"]), float(onceki["Close"]))
            govde_yukse = max(float(onceki["Open"]), float(onceki["Close"]))
            govde_ema_deler = False
            for ema_val in [float(onceki["EMA20"]), float(onceki["EMA50"]),
                            float(onceki["EMA100"]), float(onceki["EMA200"])]:
                if govde_dusuk <= ema_val <= govde_yukse:
                    govde_ema_deler = True
                    break

            # İç dönüş: dönüş mumu, bir öncekinin içinde
            ic_donus = (float(onceki["High"]) < float(iki_onceki["High"]) and
                        float(onceki["Low"])  > float(iki_onceki["Low"]))

            if govde_ema_deler:
                formasyon = "Gövde Deliş"
            elif ic_donus:
                formasyon = "İç Dönüş"
            elif rev_kirmizi and govde_ema_ustu:
                formasyon = "Orjinal 2 Mum"
            else:
                formasyon = "Orjinal 2 Mum"  # genel kabul

    if formasyon is None:
        return None, "pa_formasyon"

    # ── FİLTRE 6: Higher Low ─────────────────────────────────────────────────
    if not higher_low_kontrol(df, reversal_idx):
        return None, "higher_low"

    # ── KALİTE PUANI ─────────────────────────────────────────────────────────
    kalite = 0
    kalite_detay = []

    if v_donusu_mu(df, reversal_idx):
        kalite += 1
        kalite_detay.append("V Dönüş")

    if float(onceki["STOCH_K"]) < 20:
        kalite += 1
        kalite_detay.append("Stoch<20")

    if yumusak_duzeltme_mi(df, reversal_idx):
        kalite += 1
        kalite_detay.append("Yumuşak Düzeltme")

    if yukselen_dipler_guclu_mu(df, reversal_idx):
        kalite += 1
        kalite_detay.append("Güçlü Higher Low")

    # ── UYARILAR ─────────────────────────────────────────────────────────────
    uyarilar = []
    kapanis = float(son["Close"])
    giris   = float(onceki["High"])  # onay mumu açılınca giriş

    if yakin_direnc_var_mi(df, giris):
        uyarilar.append("⚠️ Yakın Direnç")

    if range_icinde_mi(df):
        uyarilar.append("⚠️ Range")

    # ── GİRİŞ / STOP / HEDEF ─────────────────────────────────────────────────
    atr_val  = float(son["ATR"])
    atr_kat  = params["atr_kat"]
    rr_kat   = params["rr_kat"]

    giris    = float(son["Close"])   # onay mumu kapanışı = giriş
    kapanis  = float(son["Close"])
    stop     = round(giris - atr_kat * atr_val, 2)
    bir_r    = giris - stop
    if bir_r <= 0:
        return None, "stop_hatasi"

    hedef_r  = rr_kat * (0.8 if uyarilar else 1.0)  # direnç varsa hedefi %20 kıs
    hedef_r  = round(max(1.0, hedef_r), 1)
    hedef    = round(giris + hedef_r * bir_r, 2)
    r_oran   = bir_r / atr_val if atr_val > 0 else 0

    return {
        "Kapanis"      : round(kapanis, 2),
        "Giris"        : round(giris, 2),
        "Stop"         : stop,
        "Hedef"        : hedef,
        "HedefR"       : hedef_r,
        "1R_TL"        : round(bir_r, 2),
        "1R_ATR_Oran"  : round(r_oran, 2),
        "ATR"          : round(atr_val, 2),
        "Formasyon"    : formasyon,
        "Kalite"       : kalite,
        "KaliteDetay"  : ", ".join(kalite_detay) if kalite_detay else "—",
        "Uyarilar"     : " | ".join(uyarilar) if uyarilar else "—",
        "Stoch"        : round(float(onceki["STOCH_K"]), 1),
        "MACD"         : round(float(son["MACD"]), 4),
        "DokunulanEMA" : round(dokunulan_ema, 2) if dokunulan_ema else 0,
        "Stop%"        : round((giris - stop) / giris * 100, 1),
        "Hedef%"       : round((hedef - giris) / giris * 100, 1),
    }, "ok"

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
st.sidebar.title("⚙️ Ayarlar")

portfoy = st.sidebar.number_input(
    "Portföy (TL)", min_value=10000, max_value=10000000,
    value=950000, step=10000
)
risk_yuzde = st.sidebar.slider("Risk % (1R)", 0.5, 5.0, 1.0, 0.5)

st.sidebar.markdown("### 📊 Strateji Parametreleri")
ema_tolerans = st.sidebar.select_slider(
    "EMA Dokunuş Toleransı (%)",
    options=[1, 2, 3],
    value=2,
    help="Mumun EMA'ya kaç % yakınına gelmesi dokunuş sayılır"
) / 100

atr_kat = st.sidebar.select_slider(
    "ATR Katsayısı (Stop)",
    options=[1.0, 1.5, 2.0, 2.5, 3.0],
    value=1.5,
    help="Stop = Giriş − ATR × Katsayı"
)
rr_kat = st.sidebar.select_slider(
    "R:R Katsayısı",
    options=[1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0],
    value=1.5,
    help="Hedef = Giriş + Stop Mesafesi × R:R"
)

endeks_bypass = st.sidebar.checkbox(
    "⚠️ Endeks filtresini atla", value=False,
    help="BIST100 EMA200 altında olsa bile tarama yapılmasına izin verir."
)

params = {
    "ema_tolerans": ema_tolerans,
    "atr_kat"     : atr_kat,
    "rr_kat"      : rr_kat,
}

# ─── ANA SAYFA ────────────────────────────────────────────────────────────────
st.title("📈 BIST Sapan Stratejisi Tarayıcı")
st.caption("EMA Trend | EMA Dokunuş | Stoch(5,3,3)<30 | MACD(50,100,9) | Price Action | Higher Low | ATR Stop")

# ─── ENDEKS DURUMU ────────────────────────────────────────────────────────────
aktif, xu100, xu_ema200, xu_fark = endeks_kontrol()

if aktif is None:
    st.warning("⚠️ BIST100 verisi alınamadı — endeks filtresi devre dışı.")
    endeks_gecti = True
elif aktif:
    st.success(
        f"✅ **BIST100 Aktif** — "
        f"Kapanış: {xu100:,.0f}  |  EMA200: {xu_ema200:,.0f}  |  "
        f"Fark: **+{xu_fark:.1f}%** — Strateji bugün aktif."
    )
    endeks_gecti = True
else:
    st.error(
        f"🚫 **BIST100 EMA200 Altında** — "
        f"Kapanış: {xu100:,.0f}  |  EMA200: {xu_ema200:,.0f}  |  "
        f"Fark: **{xu_fark:.1f}%** — Strateji bugün pasif."
    )
    endeks_gecti = False

if endeks_bypass:
    endeks_gecti = True
    st.warning("⚠️ Endeks filtresi devre dışı bırakıldı.")

st.info("💡 **Hatırlatma:** Pozisyon almadan önce bilanço tarihini kontrol et → [investing.com/earnings-calendar](https://tr.investing.com/earnings-calendar/)")
st.markdown("---")

# ─── TARA BUTONU ──────────────────────────────────────────────────────────────
tara_disabled = not endeks_gecti

if tara_disabled:
    st.info("Endeks EMA200 altında — tarama devre dışı. Sol menüden 'Endeks filtresini atla' seçeneğini açabilirsiniz.")

if st.button("🔍 Tara", use_container_width=True, type="primary", disabled=tara_disabled):
    risk_tl   = portfoy * risk_yuzde / 100
    sinyaller = []
    hatalar   = []
    elenen    = {
        "trend": 0, "stoch": 0, "macd": 0,
        "pa_onay": 0, "pa_kirilim": 0, "ema_dokunusu": 0,
        "higher_low": 0, "pa_formasyon": 0, "stop_hatasi": 0, "diger": 0
    }

    progress = st.progress(0, text="Tarama başlıyor...")
    toplam   = len(HISSELER)

    for i, hisse in enumerate(HISSELER):
        progress.progress(
            (i + 1) / toplam,
            text=f"Taraniyor: {hisse} ({i+1}/{toplam})"
        )
        df = veri_cek(hisse)
        if df is None:
            hatalar.append(hisse)
            continue

        sonuc, sebep = sinyal_tara(df, params)

        if sonuc is None:
            if sebep in elenen:
                elenen[sebep] += 1
            else:
                elenen["diger"] += 1
            continue

        giris      = sonuc["Giris"]
        stop       = sonuc["Stop"]
        risk_hisse = giris - stop
        if risk_hisse <= 0:
            continue

        lot      = max(1, int(risk_tl / risk_hisse))
        giris_tl = round(lot * giris, 2)

        # Kalite yıldızı
        kalite = sonuc["Kalite"]
        yildiz = "⭐" * kalite if kalite > 0 else "—"

        sinyaller.append({
            "★"          : "★" if hisse in TOP50 else "",
            "Hisse"      : hisse,
            "Kapanis"    : sonuc["Kapanis"],
            "Giriş"      : sonuc["Giris"],
            "Stop"       : sonuc["Stop"],
            "Stop%"      : sonuc["Stop%"],
            "Hedef"      : sonuc["Hedef"],
            "Hedef%"     : sonuc["Hedef%"],
            "HedefR"     : sonuc["HedefR"],
            "1R_ATR"     : sonuc["1R_ATR_Oran"],
            "Formasyon"  : sonuc["Formasyon"],
            "Stoch"      : sonuc["Stoch"],
            "MACD"       : sonuc["MACD"],
            "Kalite"     : yildiz,
            "KaliteDetay": sonuc["KaliteDetay"],
            "Uyarılar"   : sonuc["Uyarilar"],
            "Lot"        : lot,
            "Giriş TL"   : giris_tl,
            "Risk TL"    : round(risk_tl, 2),
            "_kalite_num": kalite,
        })

    progress.empty()
    st.session_state["sinyaller"] = sinyaller
    st.session_state["hatalar"]   = hatalar
    st.session_state["elenen"]    = elenen
    st.session_state["tarih"]     = datetime.now().strftime("%d.%m.%Y %H:%M")

# ─── SONUÇLAR ─────────────────────────────────────────────────────────────────
if "sinyaller" in st.session_state:
    sinyaller = st.session_state["sinyaller"]
    tarih     = st.session_state["tarih"]
    hatalar   = st.session_state.get("hatalar", [])
    elenen    = st.session_state.get("elenen", {})

    st.markdown(f"### Tarama Sonuçları — {tarih}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sinyal Sayısı", len(sinyaller))
    col2.metric("Taranan Hisse", len(HISSELER))
    col3.metric("Veri Hatası",   len(hatalar))
    col4.metric("Endeks",        "✅ Aktif" if endeks_gecti else "🚫 Pasif")

    # Filtre istatistikleri
    with st.expander("📊 Filtre istatistikleri — kaç hisse nerede elendi?"):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("EMA Trend",     elenen.get("trend", 0))
        c2.metric("Stoch ≥ 30",    elenen.get("stoch", 0))
        c3.metric("MACD",          elenen.get("macd", 0))
        c4.metric("EMA Dokunuşu",  elenen.get("ema_dokunusu", 0))
        c5, c6, c7, c8 = st.columns(4)
        c5.metric("Onay Mumu",     elenen.get("pa_onay", 0))
        c6.metric("Kırılım Yok",   elenen.get("pa_kirilim", 0))
        c7.metric("Higher Low",    elenen.get("higher_low", 0))
        c8.metric("Formasyon",     elenen.get("pa_formasyon", 0))

    if len(hatalar) > 0:
        with st.expander(f"⚠️ Veri alınamayan {len(hatalar)} hisse"):
            cols = st.columns(6)
            for i, h in enumerate(sorted(hatalar)):
                tv_url = f"https://tr.tradingview.com/chart/?symbol=BIST:{h}"
                cols[i % 6].markdown(f"[{h}]({tv_url})")

    if len(sinyaller) == 0:
        st.warning("Bugün kriterlere uyan hisse bulunamadı.")
    else:
        # Kaliteye ve TOP50'ye göre sırala
        df_sonuc = pd.DataFrame(sinyaller).sort_values(
            by=["★", "_kalite_num"], ascending=[False, False]
        )

        # Uyarılı hisseleri vurgula
        uyarili = df_sonuc[df_sonuc["Uyarılar"] != "—"]
        if len(uyarili) > 0:
            st.warning(f"⚠️ {len(uyarili)} hissede uyarı var — dikkatli değerlendir.")

        # Yüksek kaliteli sinyaller
        yuksek_kalite = df_sonuc[df_sonuc["_kalite_num"] >= 3]
        if len(yuksek_kalite) > 0:
            st.success(f"⭐⭐⭐ {len(yuksek_kalite)} hisse yüksek kaliteli setup!")

        df_goster = df_sonuc.copy()
        df_goster["Hedef%"] = df_goster["Hedef%"].apply(lambda x: f"+%{x}")
        df_goster["Stop%"]  = df_goster["Stop%"].apply(lambda x: f"-%{x}")
        df_goster["HedefR"] = df_goster["HedefR"].apply(lambda x: f"{x}R")
        df_goster["1R_ATR"] = df_goster["1R_ATR"].apply(lambda x: f"{x}x")
        df_goster["📈 Grafik"] = df_goster["Hisse"].apply(
            lambda h: f"https://tr.tradingview.com/chart/?symbol=BIST:{h}"
        )

        st.dataframe(
            df_goster[[
                "★","Hisse","Kapanis","Giriş","Stop","Stop%",
                "Hedef","Hedef%","HedefR","1R_ATR","Formasyon",
                "Stoch","MACD","Kalite","KaliteDetay","Uyarılar",
                "Lot","Giriş TL","Risk TL","📈 Grafik"
            ]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "📈 Grafik": st.column_config.LinkColumn(
                    "📈 Grafik",
                    help="TradingView'da aç",
                    display_text="TradingView →"
                )
            }
        )

        toplam_giris = df_sonuc["Giriş TL"].sum()
        toplam_risk  = df_sonuc["Risk TL"].sum()
        c1, c2 = st.columns(2)
        c1.metric("Toplam Sermaye Kullanımı", f"{toplam_giris:,.0f} TL")
        c2.metric("Toplam Risk",
                  f"{toplam_risk:,.0f} TL  (%{toplam_risk/portfoy*100:.1f} portföy)")

        csv = df_sonuc.drop(columns=["_kalite_num"]).to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="⬇️ CSV İndir",
            data=csv,
            file_name="sapan_sinyaller_" + datetime.now().strftime("%Y%m%d_%H%M") + ".csv",
            mime="text/csv",
        )

        # ─── GRAFİK ───────────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### 📊 Grafik")

        secili = st.selectbox("Hisse seçin:", [r["Hisse"] for r in sinyaller])
        df_grafik = veri_cek(secili, gun=150)

        if df_grafik is not None:
            for col in ["Open","High","Low","Close","Volume"]:
                if col in df_grafik.columns:
                    df_grafik[col] = squeeze(df_grafik[col])

            c = df_grafik["Close"]
            df_grafik["EMA20"]    = ema(c, 20)
            df_grafik["EMA50"]    = ema(c, 50)
            df_grafik["EMA100"]   = ema(c, 100)
            df_grafik["EMA200"]   = ema(c, 200)
            df_grafik["STOCH_K"], df_grafik["STOCH_D"] = stochastic_hesapla(df_grafik)
            df_grafik["MACD"], df_grafik["MACD_SIG"], df_grafik["MACD_HIS"] = macd_hesapla(c)

            secili_sinyal = next(r for r in sinyaller if r["Hisse"] == secili)

            fig = make_subplots(
                rows=3, cols=1, shared_xaxes=True,
                row_heights=[0.55, 0.22, 0.23],
                vertical_spacing=0.03,
                subplot_titles=("Fiyat", "MACD (50,100,9)", "Stochastic (5,3,3)")
            )

            # Mum grafik
            fig.add_trace(go.Candlestick(
                x=df_grafik.index,
                open=df_grafik["Open"], high=df_grafik["High"],
                low=df_grafik["Low"],   close=df_grafik["Close"],
                name="Fiyat",
                increasing_line_color="#22c55e",
                decreasing_line_color="#ef4444",
            ), row=1, col=1)

            # EMA'lar
            for col_name, renk, genislik in [
                ("EMA20","#38bdf8",1.5), ("EMA50","#f59e0b",1.5),
                ("EMA100","#a78bfa",1),  ("EMA200","#f472b6",1),
            ]:
                fig.add_trace(go.Scatter(
                    x=df_grafik.index, y=df_grafik[col_name],
                    name=col_name, line=dict(color=renk, width=genislik)
                ), row=1, col=1)

            # Stop ve Hedef çizgileri
            son_tarih = df_grafik.index[-1]
            bitis     = son_tarih + timedelta(days=15)
            for seviye, renk, isim in [
                (secili_sinyal["Stop"],  "#ef4444", "Stop"),
                (secili_sinyal["Giriş"], "#facc15", "Giriş"),
                (secili_sinyal["Hedef"], "#22c55e", f"Hedef {secili_sinyal['HedefR']}R"),
            ]:
                fig.add_shape(
                    type="line",
                    x0=son_tarih, x1=bitis, y0=seviye, y1=seviye,
                    line=dict(color=renk, width=1.5, dash="dash"),
                    row=1, col=1
                )
                fig.add_annotation(
                    x=bitis, y=seviye,
                    text=f"{isim} {seviye:.2f}",
                    showarrow=False,
                    font=dict(color=renk, size=10),
                    xanchor="left", row=1, col=1
                )

            # MACD
            colors_macd = ["#3fb950" if v >= 0 else "#ef4444" for v in df_grafik["MACD_HIS"]]
            fig.add_trace(go.Bar(
                x=df_grafik.index, y=df_grafik["MACD_HIS"],
                name="MACD His.", marker_color=colors_macd, opacity=0.7
            ), row=2, col=1)
            fig.add_trace(go.Scatter(
                x=df_grafik.index, y=df_grafik["MACD"],
                name="MACD", line=dict(color="#38bdf8", width=1.2)
            ), row=2, col=1)
            fig.add_trace(go.Scatter(
                x=df_grafik.index, y=df_grafik["MACD_SIG"],
                name="Sinyal", line=dict(color="#f59e0b", width=1.2)
            ), row=2, col=1)
            fig.add_hline(y=0, line_dash="dot", line_color="#64748b", row=2, col=1)

            # Stochastic
            fig.add_trace(go.Scatter(
                x=df_grafik.index, y=df_grafik["STOCH_K"],
                name="Stoch K", line=dict(color="#38bdf8", width=1.5)
            ), row=3, col=1)
            fig.add_trace(go.Scatter(
                x=df_grafik.index, y=df_grafik["STOCH_D"],
                name="Stoch D", line=dict(color="#f59e0b", width=1.2)
            ), row=3, col=1)
            fig.add_hline(y=30, line_dash="dot", line_color="#ef4444",  row=3, col=1)
            fig.add_hline(y=20, line_dash="dot", line_color="#f97316",  row=3, col=1)
            fig.add_hline(y=80, line_dash="dot", line_color="#22c55e",  row=3, col=1)

            fig.add_vline(
                x=son_tarih, line_dash="dot",
                line_color="#facc15", line_width=1,
                row="all", col=1
            )

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0d0f14",
                plot_bgcolor="#0d0f14",
                height=750,
                showlegend=True,
                xaxis_rangeslider_visible=False,
                margin=dict(l=10, r=100, t=30, b=10),
                font=dict(family="Consolas", size=11),
            )
            fig.update_yaxes(gridcolor="#1e293b")
            fig.update_xaxes(gridcolor="#1e293b")

            st.plotly_chart(fig, use_container_width=True)

            # Detay tablosu
            st.markdown(f"""
| | |
|---|---|
| **Formasyon** | {secili_sinyal['Formasyon']} |
| **Giriş** | {secili_sinyal['Giriş']:.2f} TL |
| **Stop** | {secili_sinyal['Stop']:.2f} TL (-%{secili_sinyal['Stop%']}) |
| **Hedef** | {secili_sinyal['Hedef']:.2f} TL (+%{secili_sinyal['Hedef%']}) — {secili_sinyal['HedefR']}R |
| **1R/ATR Oranı** | {secili_sinyal['1R_ATR']}x (ideal: 1-1.5x) |
| **Stochastic** | {secili_sinyal['Stoch']} |
| **MACD** | {secili_sinyal['MACD']} |
| **Kalite** | {secili_sinyal['Kalite']} — {secili_sinyal['KaliteDetay']} |
| **Uyarılar** | {secili_sinyal['Uyarılar']} |
| **Lot** | {secili_sinyal['Lot']:,} adet |
| **Giriş Tutarı** | {secili_sinyal['Giriş TL']:,.0f} TL |
| **Risk (1R)** | {secili_sinyal['Risk TL']:,.0f} TL |
""")

            st.info("💡 Fiyat 1R'ye ulaşınca stop'unu giriş noktasına çek! (Tapi) | Zaman stopu: 18 gün")

    st.markdown("---")
    st.caption("⚠️ Bu analiz yatırım tavsiyesi değildir.")
