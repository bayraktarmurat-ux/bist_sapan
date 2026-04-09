import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import json, os, requests, time
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─── AYARLAR ────────────────────────────────────────────────────────────────
TELEGRAM_TOKEN   = st.secrets.get("TELEGRAM_TOKEN", os.environ.get("TELEGRAM_TOKEN", ""))
TELEGRAM_CHAT_ID = "884770362"
VERI_DOSYASI     = "sapan_sanal_portfoy.json"
MAX_POZISYON     = 10

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
    "YBTAS","YIGIT","YONGA","YKSLN","YUNSA","ZGYO","ZEDUR","ZERGY","ZRGYO","ZOREN","BINHO",
]

# ─── YARDIMCI FONKSİYONLAR ──────────────────────────────────────────────────
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
    tr = pd.concat([high - low,
                    (high - close.shift(1)).abs(),
                    (low  - close.shift(1)).abs()], axis=1).max(axis=1)
    return tr.ewm(span=periyot, adjust=False).mean()

def stochastic_hesapla(df, k=5, d=3, smooth=3):
    high  = squeeze(df["High"])
    low   = squeeze(df["Low"])
    close = squeeze(df["Close"])
    ll = low.rolling(k).min()
    hh = high.rolling(k).max()
    sk = 100 * (close - ll) / (hh - ll + 1e-10)
    sk_smooth = sk.rolling(d).mean()
    sd = sk_smooth.rolling(smooth).mean()
    return sk_smooth, sd

def macd_hesapla(close, hizli=50, yavas=100, sinyal=9):
    close    = squeeze(close)
    ema_h    = close.ewm(span=hizli,  adjust=False).mean()
    ema_y    = close.ewm(span=yavas,  adjust=False).mean()
    macd     = ema_h - ema_y
    macd_sig = macd.ewm(span=sinyal, adjust=False).mean()
    macd_his = macd - macd_sig
    return macd, macd_sig, macd_his

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

@st.cache_data(ttl=3600)
def endeks_kontrol():
    for sembol in ["XU100.IS", "^XU100", "BIST100.IS"]:
        try:
            df = yf.download(sembol, period="300d", interval="1d",
                             progress=False, auto_adjust=True)
            if df.empty or len(df) < 10:
                continue
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            for col in df.columns:
                df[col] = squeeze(df[col])
            df["EMA200"] = df["Close"].ewm(span=200, adjust=False).mean()
            df.dropna(subset=["EMA200"], inplace=True)
            if df.empty:
                continue
            son     = df.iloc[-1]
            kapanis = float(son["Close"])
            e200    = float(son["EMA200"])
            aktif   = kapanis > e200
            fark    = (kapanis - e200) / e200 * 100
            return aktif, kapanis, e200, fark
        except Exception:
            continue
    return None, None, None, None

# ─── YARDIMCI KONTROLLER ────────────────────────────────────────────────────
def ema_dokunusu_var_mi(low_val, high_val, ema20, ema50, ema100, ema200, tolerans=0.02):
    for ema_val in [ema20, ema50, ema100, ema200]:
        if pd.isna(ema_val):
            continue
        band_low  = ema_val * (1 - tolerans)
        band_high = ema_val * (1 + tolerans)
        if low_val <= band_high and high_val >= band_low:
            return True, ema_val
    return False, None

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
    ema100_val = float(df["EMA100"].iloc[reversal_idx]) if "EMA100" in df.columns else None
    ema200_val = float(df["EMA200"].iloc[reversal_idx]) if "EMA200" in df.columns else None
    for ema_val in [ema100_val, ema200_val]:
        if ema_val is None or pd.isna(ema_val):
            continue
        if reversal_low <= ema_val * 1.02:
            return True
    return False

def yakin_direnc_var_mi(df, giris_fiyati, lookback=60, tolerans=0.05):
    highs = squeeze(df["High"]).iloc[-lookback:]
    pivot_highs = []
    for i in range(2, len(highs)-2):
        if (highs.iloc[i] > highs.iloc[i-1] and highs.iloc[i] > highs.iloc[i+1] and
                highs.iloc[i] > highs.iloc[i-2] and highs.iloc[i] > highs.iloc[i+2]):
            pivot_highs.append(float(highs.iloc[i]))
    for ph in pivot_highs:
        if giris_fiyati < ph <= giris_fiyati * (1 + tolerans):
            return True
    return False

def range_icinde_mi(df, lookback=20, esik=0.08):
    closes = squeeze(df["Close"]).iloc[-lookback:]
    if len(closes) < lookback:
        return False
    band = (closes.max() - closes.min()) / closes.mean()
    return band < esik

def yumusak_duzeltme_mi(df, reversal_idx, lookback=10, max_dusus=0.08):
    start = max(0, reversal_idx - lookback)
    sub   = squeeze(df["Close"]).iloc[start:reversal_idx+1]
    if len(sub) < 2:
        return False
    return (sub.max() - sub.min()) / sub.max() < max_dusus

def v_donusu_mu(df, reversal_idx, onceki_gun=5, min_dusus=0.04):
    if reversal_idx < onceki_gun:
        return False
    sub = squeeze(df["Close"]).iloc[reversal_idx-onceki_gun:reversal_idx+1]
    dusus = (sub.max() - sub.min()) / sub.max()
    rev_open  = float(df["Open"].iloc[reversal_idx])
    rev_close = float(df["Close"].iloc[reversal_idx])
    rev_atr   = float(df["ATR"].iloc[reversal_idx]) if "ATR" in df.columns else 0
    buyuk_yesil = (rev_close > rev_open) and (rev_close - rev_open) > rev_atr * 0.5
    return dusus >= min_dusus and buyuk_yesil

def yukselen_dipler_guclu_mu(df, reversal_idx, lookback=30):
    if reversal_idx < 10:
        return False
    sub_low = squeeze(df["Low"]).iloc[max(0, reversal_idx-lookback):reversal_idx+1]
    dipler = []
    for i in range(1, len(sub_low)-1):
        if sub_low.iloc[i] < sub_low.iloc[i-1] and sub_low.iloc[i] < sub_low.iloc[i+1]:
            dipler.append(float(sub_low.iloc[i]))
    if len(dipler) < 2:
        return False
    return dipler[-1] > dipler[-2]

# ─── ANA SİNYAL FONKSİYONU ──────────────────────────────────────────────────
def sinyal_tara(df, params):
    ema_tolerans = params["ema_tolerans"]
    atr_kat      = params["atr_kat"]
    rr_kat       = params["rr_kat"]

    df = df.copy()
    for col in ["Open","High","Low","Close","Volume"]:
        if col in df.columns:
            df[col] = squeeze(df[col])

    close = df["Close"]

    df["EMA20"]  = ema(close, 20)
    df["EMA50"]  = ema(close, 50)
    df["EMA100"] = ema(close, 100)
    df["EMA200"] = ema(close, 200)
    df["ATR"]    = atr_hesapla(df, 14)
    df["STOCH_K"], df["STOCH_D"] = stochastic_hesapla(df, 5, 3, 3)
    df["MACD"], df["MACD_SIG"], df["MACD_HIS"] = macd_hesapla(close, 50, 100, 9)

    df.dropna(subset=["EMA200","ATR","STOCH_K","MACD"], inplace=True)
    if len(df) < 3:
        return None, "veri_yetersiz"

    son        = df.iloc[-1]
    onceki     = df.iloc[-2]
    iki_onceki = df.iloc[-3]

    # 1. EMA trend zinciri
    if not (float(son["EMA20"]) > float(son["EMA50"]) >
            float(son["EMA100"]) > float(son["EMA200"])):
        return None, "trend"

    # 2. Stochastic < 30 (dönüş mumunda)
    if float(onceki["STOCH_K"]) >= 30:
        return None, "stoch"

    # 3. MACD pozitif VEYA 5'ten az süredir negatif
    macd_vals    = df["MACD"].iloc[-6:-1]
    macd_pozitif = float(son["MACD"]) > 0
    negatif_sure = (macd_vals < 0).sum()
    if not macd_pozitif and negatif_sure >= 5:
        return None, "macd"

    # 4. Onay mumu yeşil
    if not (float(son["Close"]) > float(son["Open"])):
        return None, "pa_onay"

    # 5. Onay mumu dönüş mumunun high'ını kırıyor
    if not (float(son["Close"]) > float(onceki["High"])):
        return None, "pa_kirilim"

    reversal_idx = len(df) - 2

    # 6. EMA dokunuşu (dönüş mumunda)
    dokundu, dokunulan_ema = ema_dokunusu_var_mi(
        float(onceki["Low"]), float(onceki["High"]),
        float(onceki["EMA20"]), float(onceki["EMA50"]),
        float(onceki["EMA100"]), float(onceki["EMA200"]),
        tolerans=ema_tolerans
    )
    if not dokundu:
        return None, "ema_dokunusu"

    # Formasyon tespiti
    rev_govde     = abs(float(onceki["Close"]) - float(onceki["Open"]))
    rev_alt_fitil = (float(onceki["Open"] if float(onceki["Close"]) > float(onceki["Open"])
                           else onceki["Close"]) - float(onceki["Low"]))
    rev_range     = float(onceki["High"]) - float(onceki["Low"])

    formasyon = None
    if rev_range > 0:
        alt_fitil_oran = rev_alt_fitil / rev_range
        govde_oran     = rev_govde / rev_range

        if alt_fitil_oran >= 0.5 and govde_oran <= 0.35:
            formasyon = "Pin Bar"
        else:
            govde_dusuk = min(float(onceki["Open"]), float(onceki["Close"]))
            govde_yukse = max(float(onceki["Open"]), float(onceki["Close"]))
            govde_ema_deler = any(
                govde_dusuk <= ev <= govde_yukse
                for ev in [float(onceki["EMA20"]), float(onceki["EMA50"]),
                            float(onceki["EMA100"]), float(onceki["EMA200"])]
            )
            ic_donus = (float(onceki["High"]) < float(iki_onceki["High"]) and
                        float(onceki["Low"])  > float(iki_onceki["Low"]))

            if govde_ema_deler:
                formasyon = "Govde Delis"
            elif ic_donus:
                formasyon = "Ic Donus"
            else:
                formasyon = "Orjinal 2 Mum"

    if formasyon is None:
        return None, "pa_formasyon"

    # 7. Higher low
    if not higher_low_kontrol(df, reversal_idx):
        return None, "higher_low"

    # Kalite puanı
    kalite = 0
    kalite_detay = []
    if v_donusu_mu(df, reversal_idx):
        kalite += 1; kalite_detay.append("V Donus")
    if float(onceki["STOCH_K"]) < 20:
        kalite += 1; kalite_detay.append("Stoch<20")
    if yumusak_duzeltme_mi(df, reversal_idx):
        kalite += 1; kalite_detay.append("Yumusak Duzeltme")
    if yukselen_dipler_guclu_mu(df, reversal_idx):
        kalite += 1; kalite_detay.append("Guclu Higher Low")

    # Uyarılar
    uyarilar = []
    giris = float(onceki["High"])
    if yakin_direnc_var_mi(df, giris):
        uyarilar.append("Yakin Direnc")
    if range_icinde_mi(df):
        uyarilar.append("Range")

    # Giriş / Stop / Hedef
    atr_val = float(son["ATR"])
    stop    = round(giris - atr_kat * atr_val, 2)
    bir_r   = giris - stop
    if bir_r <= 0:
        return None, "stop_hatasi"

    hedef_r = rr_kat * (0.8 if uyarilar else 1.0)
    hedef_r = round(max(1.0, hedef_r), 1)
    hedef   = round(giris + hedef_r * bir_r, 2)
    r_oran  = bir_r / atr_val if atr_val > 0 else 0

    return {
        "Kapanis"    : round(float(son["Close"]), 2),
        "Giris"      : round(giris, 2),
        "Stop"       : stop,
        "Hedef"      : hedef,
        "HedefR"     : hedef_r,
        "1R_TL"      : round(bir_r, 2),
        "1R_ATR_Oran": round(r_oran, 2),
        "ATR"        : round(atr_val, 2),
        "Formasyon"  : formasyon,
        "Kalite"     : kalite,
        "KaliteDetay": ", ".join(kalite_detay) if kalite_detay else "-",
        "Uyarilar"   : " | ".join(uyarilar) if uyarilar else "-",
        "Stoch"      : round(float(onceki["STOCH_K"]), 1),
        "MACD"       : round(float(son["MACD"]), 4),
        "DokunulanEMA": round(dokunulan_ema, 2) if dokunulan_ema else 0,
        "Stop_pct"   : round((giris - stop) / giris * 100, 1),
        "Hedef_pct"  : round((hedef - giris) / giris * 100, 1),
    }, "ok"

# ─── TELEGRAM ───────────────────────────────────────────────────────────────
def telegram_gonder(mesaj):
    if not TELEGRAM_TOKEN:
        return False
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": mesaj, "parse_mode": "HTML"},
            timeout=10
        )
        return r.status_code == 200
    except Exception:
        return False

def sinyal_mesaji_olustur(hisse, s, portfoy, risk_yuzde):
    risk_tl = portfoy * risk_yuzde / 100
    bir_r   = s["Giris"] - s["Stop"]
    lot     = max(1, int(risk_tl / bir_r)) if bir_r > 0 else 0
    top_tag = "STAR TOP50\n" if hisse in TOP50 else ""
    return (
        f"SAPAN SINYALI - {hisse}\n"
        f"{top_tag}"
        f"Giris:  {s['Giris']:.2f} TL\n"
        f"Hedef:  {s['Hedef']:.2f} TL (+%{s['Hedef_pct']}) - {s['HedefR']}R\n"
        f"Stop:   {s['Stop']:.2f} TL (-%{s['Stop_pct']})\n"
        f"Formasyon: {s['Formasyon']}\n"
        f"Stoch: {s['Stoch']} | MACD: {s['MACD']:.4f}\n"
        f"Lot: {lot:,} adet\n"
        f"Kalite: {'*' * s['Kalite'] if s['Kalite'] > 0 else '-'} {s['KaliteDetay']}\n"
        f"{'Uyari: ' + s['Uyarilar'] if s['Uyarilar'] != '-' else ''}"
    ).strip()

# ─── SANAL PORTFÖY ──────────────────────────────────────────────────────────
def veri_yukle():
    if os.path.exists(VERI_DOSYASI):
        with open(VERI_DOSYASI, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"acik_pozisyonlar": [], "kapali_islemler": [], "tarama_tarihi": ""}

def veri_kaydet(veri):
    with open(VERI_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)

def guncel_fiyat_al(sembol):
    try:
        df = yf.download(sembol + ".IS", period="2d", interval="1d",
                         auto_adjust=True, progress=False)
        if df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        val = df["Close"].iloc[-1]
        return float(val.iloc[0]) if hasattr(val, "iloc") else float(val)
    except Exception:
        return None

def pozisyon_ac(s_row, portfoy, risk_yuzde, veri):
    hisse = s_row["Hisse"]
    if any(p["sembol"] == hisse for p in veri["acik_pozisyonlar"]):
        return False, "Zaten acik pozisyon var"
    if len(veri["acik_pozisyonlar"]) >= MAX_POZISYON:
        return False, f"Maksimum {MAX_POZISYON} pozisyon dolu"
    giris = float(s_row["Giris"])
    stop  = float(s_row["Stop"])
    hedef = float(s_row["Hedef"])
    bir_r = giris - stop
    if bir_r <= 0:
        return False, "Gecersiz risk"
    risk_tl = portfoy * risk_yuzde / 100
    lot = max(1, int(risk_tl / bir_r))
    poz = {
        "sembol"    : hisse,
        "giris"     : giris,
        "stop"      : stop,
        "hedef"     : hedef,
        "hedef_r"   : float(s_row.get("HedefR", 1.5)),
        "adet"      : lot,
        "maliyet"   : round(lot * giris, 2),
        "tarih"     : datetime.now().strftime("%Y-%m-%d %H:%M"),
        "formasyon" : str(s_row.get("Formasyon", "")),
    }
    veri["acik_pozisyonlar"].append(poz)
    veri_kaydet(veri)
    return True, poz

def pozisyon_kapat(sembol, kapanis_fiyati, veri, neden="Manuel"):
    poz = next((p for p in veri["acik_pozisyonlar"] if p["sembol"] == sembol), None)
    if not poz:
        return False, "Pozisyon bulunamadi"
    kap_f = float(kapanis_fiyati)
    gir_f = float(poz["giris"])
    kz    = round((kap_f - gir_f) * int(poz["adet"]), 2)
    kz_pct= round((kap_f / gir_f - 1) * 100, 2) if gir_f > 0 else 0.0
    kapali = {**poz, "kapis_fiyati": kap_f,
              "kapis_tarihi": datetime.now().strftime("%Y-%m-%d %H:%M"),
              "kar_zarar_tl": kz, "kar_yuzde": kz_pct, "neden": neden}
    veri["acik_pozisyonlar"] = [p for p in veri["acik_pozisyonlar"] if p["sembol"] != sembol]
    veri["kapali_islemler"].append(kapali)
    veri_kaydet(veri)
    return True, kapali

# ─── STREAMLIT ──────────────────────────────────────────────────────────────
def main():
    st.set_page_config(page_title="Sapan Bot", page_icon="📈", layout="wide")
    st.title("Sapan Strateji Botu")
    st.caption("EMA Trend | EMA Dokanus | Stoch(5,3,3)<30 | MACD(50,100,9) | Price Action | Higher Low | Sanal Portfoy")

    veri = veri_yukle()

    st.sidebar.title("Parametreler")
    portfoy    = st.sidebar.number_input("Portfoy (TL)", 10000, 10_000_000, 950_000, 10000)
    risk_yuzde = st.sidebar.slider("Risk % (1R)", 0.5, 5.0, 1.0, 0.5)
    ema_tol    = st.sidebar.select_slider("EMA Toleransi (%)", [1, 2, 3], 2) / 100
    atr_kat    = st.sidebar.select_slider("ATR Katsayisi (Stop)", [1.0,1.5,2.0,2.5,3.0], 1.5)
    rr_kat     = st.sidebar.select_slider("R:R", [1.0,1.5,2.0,2.5,3.0,3.5,4.0], 1.5)
    endeks_bypass   = st.sidebar.checkbox("Endeks filtresini atla", False)
    telegram_bildir = st.sidebar.checkbox("Telegram bildirimi", True)

    params = {"ema_tolerans": ema_tol, "atr_kat": atr_kat, "rr_kat": rr_kat}

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Sinyal Tara", "Acik Pozisyonlar", "Gecmis Islemler", "Grafik"])

    # ══ TAB 1: TARAMA ═══════════════════════════════════════════════════
    with tab1:
        aktif, xu100, xu_ema200, xu_fark = endeks_kontrol()
        if aktif is None:
            st.warning("BIST100 verisi alinamadi - endeks filtresi devre disi.")
            endeks_gecti = True
        elif aktif:
            st.success(f"BIST100 Aktif - {xu100:,.0f} | EMA200: {xu_ema200:,.0f} | +{xu_fark:.1f}%")
            endeks_gecti = True
        else:
            st.error(f"BIST100 EMA200 Altinda - {xu100:,.0f} | EMA200: {xu_ema200:,.0f} | {xu_fark:.1f}%")
            endeks_gecti = False

        if endeks_bypass:
            endeks_gecti = True
            st.warning("Endeks filtresi devre disi birakildi.")

        if st.button("Tara", type="primary", use_container_width=True,
                     disabled=not endeks_gecti):
            risk_tl   = portfoy * risk_yuzde / 100
            sinyaller = []
            elenen    = {k: 0 for k in ["trend","stoch","macd","pa_onay",
                                         "pa_kirilim","ema_dokunusu","higher_low",
                                         "pa_formasyon","stop_hatasi","diger"]}
            hatalar   = []
            progress  = st.progress(0, text="Tarama basliyor...")
            toplam    = len(HISSELER)

            for i, hisse in enumerate(HISSELER):
                progress.progress((i+1)/toplam, text=f"Taraniyor: {hisse} ({i+1}/{toplam})")
                df = veri_cek(hisse)
                if df is None:
                    hatalar.append(hisse)
                    continue

                sonuc, sebep = sinyal_tara(df, params)
                if sonuc is None:
                    elenen[sebep if sebep in elenen else "diger"] += 1
                    continue

                giris  = sonuc["Giris"]
                stop   = sonuc["Stop"]
                bir_r  = giris - stop
                if bir_r <= 0:
                    continue
                lot      = max(1, int(risk_tl / bir_r))
                giris_tl = round(lot * giris, 2)
                yildiz   = "*" * sonuc["Kalite"] if sonuc["Kalite"] > 0 else "-"

                sinyaller.append({
                    "TOP50"      : "STAR" if hisse in TOP50 else "",
                    "Hisse"      : hisse,
                    "Kapanis"    : sonuc["Kapanis"],
                    "Giris"      : sonuc["Giris"],
                    "Stop"       : sonuc["Stop"],
                    "Stop%"      : sonuc["Stop_pct"],
                    "Hedef"      : sonuc["Hedef"],
                    "Hedef%"     : sonuc["Hedef_pct"],
                    "HedefR"     : sonuc["HedefR"],
                    "1R_ATR"     : sonuc["1R_ATR_Oran"],
                    "Formasyon"  : sonuc["Formasyon"],
                    "Stoch"      : sonuc["Stoch"],
                    "MACD"       : sonuc["MACD"],
                    "Kalite"     : yildiz,
                    "KaliteDetay": sonuc["KaliteDetay"],
                    "Uyarilar"   : sonuc["Uyarilar"],
                    "Lot"        : lot,
                    "Giris TL"   : giris_tl,
                    "Risk TL"    : round(risk_tl, 2),
                    "_kalite_num": sonuc["Kalite"],
                })

                if telegram_bildir and TELEGRAM_TOKEN:
                    telegram_gonder(sinyal_mesaji_olustur(hisse, sonuc, portfoy, risk_yuzde))

            progress.empty()
            veri["tarama_tarihi"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            veri_kaydet(veri)
            st.session_state["sinyaller"] = sinyaller
            st.session_state["hatalar"]   = hatalar
            st.session_state["elenen"]    = elenen
            st.session_state["tarih"]     = datetime.now().strftime("%d.%m.%Y %H:%M")

            if sinyaller and telegram_bildir and TELEGRAM_TOKEN:
                telegram_gonder(f"Tarama tamamlandi: {len(sinyaller)} sinyal bulundu.")

        if "sinyaller" in st.session_state:
            sinyaller = st.session_state["sinyaller"]
            elenen    = st.session_state.get("elenen", {})
            hatalar   = st.session_state.get("hatalar", [])
            tarih     = st.session_state.get("tarih", "")

            st.markdown(f"### Tarama Sonuclari - {tarih}")
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("Sinyal", len(sinyaller))
            c2.metric("Taranan", len(HISSELER))
            c3.metric("Veri Hatasi", len(hatalar))
            c4.metric("Endeks", "Aktif" if endeks_gecti else "Pasif")

            with st.expander("Filtre istatistikleri - kac hisse nerede elendi?"):
                c1,c2,c3,c4 = st.columns(4)
                c1.metric("EMA Trend",    elenen.get("trend",0))
                c2.metric("Stoch >= 30",  elenen.get("stoch",0))
                c3.metric("MACD",         elenen.get("macd",0))
                c4.metric("EMA Dokanusu", elenen.get("ema_dokunusu",0))
                c5,c6,c7,c8 = st.columns(4)
                c5.metric("Onay Mumu",   elenen.get("pa_onay",0))
                c6.metric("Kirilim Yok", elenen.get("pa_kirilim",0))
                c7.metric("Higher Low",  elenen.get("higher_low",0))
                c8.metric("Formasyon",   elenen.get("pa_formasyon",0))

            if not sinyaller:
                st.warning("Bugun kriterlere uyan hisse bulunamadi.")
            else:
                df_sonuc = pd.DataFrame(sinyaller).sort_values(
                    by=["TOP50","_kalite_num"], ascending=[False,False])

                yuksek = df_sonuc[df_sonuc["_kalite_num"] >= 3]
                if len(yuksek) > 0:
                    st.success(f"{len(yuksek)} yuksek kaliteli setup (3+ yildiz)!")

                st.dataframe(
                    df_sonuc[[
                        "TOP50","Hisse","Kapanis","Giris","Stop","Stop%",
                        "Hedef","Hedef%","HedefR","Formasyon",
                        "Stoch","MACD","Kalite","KaliteDetay","Uyarilar",
                        "Lot","Giris TL","Risk TL"
                    ]],
                    use_container_width=True, hide_index=True
                )

                csv = df_sonuc.drop(columns=["_kalite_num"]).to_csv(index=False).encode("utf-8-sig")
                st.download_button("CSV Indir", csv,
                    f"sapan_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv")

                st.markdown("### Sanal Pozisyon Ac")
                secilen = st.selectbox("Hisse sec", [s["Hisse"] for s in sinyaller])
                s_row   = next(s for s in sinyaller if s["Hisse"] == secilen)
                c1,c2,c3,c4 = st.columns(4)
                c1.metric("Giris", f"{s_row['Giris']:.2f} TL")
                c2.metric("Stop",  f"{s_row['Stop']:.2f} TL", f"-%{s_row['Stop%']}")
                c3.metric("Hedef", f"{s_row['Hedef']:.2f} TL", f"+%{s_row['Hedef%']}")
                c4.metric("Lot",   f"{s_row['Lot']:,} adet")

                if st.button(f"{secilen} Pozisyon Ac (Sanal)", use_container_width=True):
                    ok, sonuc = pozisyon_ac(s_row, portfoy, risk_yuzde, veri)
                    if ok:
                        st.success(f"{secilen} acildi - {sonuc['adet']:,} adet @ {sonuc['giris']:.2f} TL")
                        if TELEGRAM_TOKEN:
                            telegram_gonder(
                                f"SANAL POZISYON ACILDI - {secilen}\n"
                                f"{sonuc['adet']:,} adet @ {sonuc['giris']:.2f} TL\n"
                                f"Hedef: {sonuc['hedef']:.2f} | Stop: {sonuc['stop']:.2f}"
                            )
                        st.rerun()
                    else:
                        st.error(f"Hata: {sonuc}")

    # ══ TAB 2: ACIK POZISYONLAR ══════════════════════════════════════════
    with tab2:
        if not veri["acik_pozisyonlar"]:
            st.info("Henuz acik pozisyon yok.")
        else:
            rows = []
            for p in veri["acik_pozisyonlar"]:
                guncel = guncel_fiyat_al(p["sembol"]) or p["giris"]
                kz     = round((guncel - p["giris"]) * p["adet"], 2)
                kz_pct = round((guncel / p["giris"] - 1) * 100, 2)
                durum  = ("Hedefe yakin" if guncel >= p["hedef"] * 0.95 else
                          "Stopa yakin"  if guncel <= p["stop"]  * 1.05 else "Aktif")
                rows.append({
                    "Sembol": p["sembol"], "Giris": p["giris"], "Guncel": guncel,
                    "Stop": p["stop"], "Hedef": p["hedef"], "Adet": p["adet"],
                    "KZ_TL": kz, "KZ_pct": kz_pct, "Durum": durum,
                    "Formasyon": p.get("formasyon",""), "Tarih": p["tarih"],
                })

            df_poz = pd.DataFrame(rows)
            toplam_kz  = df_poz["KZ_TL"].sum()
            toplam_mal = sum(p["maliyet"] for p in veri["acik_pozisyonlar"])

            c1,c2,c3,c4 = st.columns(4)
            c1.metric("Acik Pozisyon", len(veri["acik_pozisyonlar"]))
            c2.metric("Toplam Maliyet", f"{toplam_mal:,.0f} TL")
            c3.metric("Toplam K/Z", f"{toplam_kz:+,.0f} TL")
            c4.metric("Getiri", f"{(toplam_kz/toplam_mal*100):+.1f}%" if toplam_mal>0 else "-")

            st.dataframe(df_poz, use_container_width=True, hide_index=True)

            st.markdown("### Pozisyon Kapat")
            ca,cb,cc = st.columns([2,1,1])
            with ca:
                kapat_sem = st.selectbox("Hisse", [p["sembol"] for p in veri["acik_pozisyonlar"]])
            with cb:
                neden = st.selectbox("Neden", ["Hedef Geldi","Stop Tetiklendi","Manuel"])
            with cc:
                p_sec    = next((x for x in veri["acik_pozisyonlar"] if x["sembol"] == kapat_sem), None)
                guncel_f = guncel_fiyat_al(kapat_sem) if p_sec else None
                kapat_f  = st.number_input("Kapanis Fiyati",
                    value=float(guncel_f or (p_sec["giris"] if p_sec else 0)),
                    min_value=0.01, step=0.01)

            if st.button(f"{kapat_sem} Kapat", use_container_width=True):
                ok, sonuc = pozisyon_kapat(kapat_sem, kapat_f, veri, neden)
                if ok:
                    kz = sonuc["kar_zarar_tl"]
                    st.success(f"{kapat_sem} kapatildi | {kz:+,.2f} TL ({sonuc['kar_yuzde']:+.1f}%)")
                    if TELEGRAM_TOKEN:
                        telegram_gonder(
                            f"POZISYON KAPANDI - {kapat_sem}\n"
                            f"Neden: {neden}\n"
                            f"{sonuc['giris']:.2f} -> {kapat_f:.2f} TL | K/Z: {kz:+,.2f} TL"
                        )
                    st.rerun()
                else:
                    st.error(sonuc)

            if st.button("Fiyatlari Guncelle", use_container_width=True):
                st.rerun()

    # ══ TAB 3: GECMIS ISLEMLER ═══════════════════════════════════════════
    with tab3:
        if not veri["kapali_islemler"]:
            st.info("Henuz kapatilmis islem yok.")
        else:
            df_k    = pd.DataFrame(veri["kapali_islemler"])
            kazanan = df_k[df_k["kar_zarar_tl"] > 0]
            kaybeden= df_k[df_k["kar_zarar_tl"] <= 0]
            toplam_kz = df_k["kar_zarar_tl"].sum()
            win_rate  = len(kazanan)/len(df_k)*100 if len(df_k)>0 else 0

            c1,c2,c3,c4,c5 = st.columns(5)
            c1.metric("Toplam", len(df_k))
            c2.metric("Kazanan", len(kazanan))
            c3.metric("Kaybeden", len(kaybeden))
            c4.metric("Win Rate", f"{win_rate:.1f}%")
            c5.metric("Net K/Z", f"{toplam_kz:+,.0f} TL")

            if len(kazanan) > 0 and len(kaybeden) > 0:
                ort_k = kazanan["kar_zarar_tl"].mean()
                ort_l = abs(kaybeden["kar_zarar_tl"].mean())
                exp   = win_rate/100*ort_k - (1-win_rate/100)*ort_l
                c1b,c2b,c3b = st.columns(3)
                c1b.metric("Ort. Kazanc", f"{ort_k:+,.0f} TL")
                c2b.metric("Ort. Kayip",  f"-{ort_l:,.0f} TL")
                c3b.metric("Expectancy",  f"{exp:+,.0f} TL")

            mevcut = [c for c in ["sembol","giris","kapis_fiyati","adet",
                                   "kar_zarar_tl","kar_yuzde","neden","kapis_tarihi"]
                      if c in df_k.columns]
            st.dataframe(
                df_k[mevcut].rename(columns={
                    "sembol":"Sembol","giris":"Giris","kapis_fiyati":"Cikis",
                    "adet":"Adet","kar_zarar_tl":"KZ TL","kar_yuzde":"KZ %",
                    "neden":"Neden","kapis_tarihi":"Kapanis"
                }).sort_values("Kapanis", ascending=False),
                use_container_width=True, hide_index=True
            )

    # ══ TAB 4: GRAFIK ════════════════════════════════════════════════════
    with tab4:
        if "sinyaller" not in st.session_state or not st.session_state["sinyaller"]:
            st.info("Once tarama yap.")
        else:
            sinyaller = st.session_state["sinyaller"]
            secili    = st.selectbox("Hisse secin:", [s["Hisse"] for s in sinyaller], key="grafik_sec")
            df_g = veri_cek(secili, gun=150)

            if df_g is not None:
                c = df_g["Close"]
                df_g["EMA20"]   = ema(c, 20)
                df_g["EMA50"]   = ema(c, 50)
                df_g["EMA100"]  = ema(c, 100)
                df_g["EMA200"]  = ema(c, 200)
                df_g["STOCH_K"], df_g["STOCH_D"] = stochastic_hesapla(df_g)
                df_g["MACD"], df_g["MACD_SIG"], df_g["MACD_HIS"] = macd_hesapla(c)

                s_sec = next(s for s in sinyaller if s["Hisse"] == secili)

                fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                    row_heights=[0.55,0.22,0.23], vertical_spacing=0.03,
                    subplot_titles=("Fiyat","MACD (50,100,9)","Stochastic (5,3,3)"))

                fig.add_trace(go.Candlestick(
                    x=df_g.index, open=df_g["Open"], high=df_g["High"],
                    low=df_g["Low"], close=df_g["Close"], name="Fiyat",
                    increasing_line_color="#22c55e", decreasing_line_color="#ef4444"
                ), row=1, col=1)

                for col_name, renk, genislik in [
                    ("EMA20","#38bdf8",1.5),("EMA50","#f59e0b",1.5),
                    ("EMA100","#a78bfa",1.0),("EMA200","#f472b6",1.0)
                ]:
                    fig.add_trace(go.Scatter(x=df_g.index, y=df_g[col_name],
                        name=col_name, line=dict(color=renk, width=genislik)), row=1, col=1)

                son_tarih = df_g.index[-1]
                bitis     = son_tarih + timedelta(days=15)
                for seviye, renk, isim in [
                    (s_sec["Stop"],  "#ef4444", "Stop"),
                    (s_sec["Giris"], "#facc15", "Giris"),
                    (s_sec["Hedef"], "#22c55e", f"Hedef {s_sec['HedefR']}R"),
                ]:
                    fig.add_shape(type="line", x0=son_tarih, x1=bitis,
                        y0=seviye, y1=seviye,
                        line=dict(color=renk, width=1.5, dash="dash"), row=1, col=1)
                    fig.add_annotation(x=bitis, y=seviye,
                        text=f"{isim} {seviye:.2f}", showarrow=False,
                        font=dict(color=renk, size=10), xanchor="left", row=1, col=1)

                colors_m = ["#3fb950" if v >= 0 else "#ef4444" for v in df_g["MACD_HIS"]]
                fig.add_trace(go.Bar(x=df_g.index, y=df_g["MACD_HIS"],
                    marker_color=colors_m, name="MACD His.", opacity=0.7), row=2, col=1)
                fig.add_trace(go.Scatter(x=df_g.index, y=df_g["MACD"],
                    line=dict(color="#38bdf8",width=1.2), name="MACD"), row=2, col=1)
                fig.add_trace(go.Scatter(x=df_g.index, y=df_g["MACD_SIG"],
                    line=dict(color="#f59e0b",width=1.2), name="Sinyal"), row=2, col=1)
                fig.add_hline(y=0, line_dash="dot", line_color="#64748b", row=2, col=1)

                fig.add_trace(go.Scatter(x=df_g.index, y=df_g["STOCH_K"],
                    line=dict(color="#38bdf8",width=1.5), name="Stoch K"), row=3, col=1)
                fig.add_trace(go.Scatter(x=df_g.index, y=df_g["STOCH_D"],
                    line=dict(color="#f59e0b",width=1.2), name="Stoch D"), row=3, col=1)
                for y_val, renk in [(20,"#f97316"),(30,"#ef4444"),(80,"#22c55e")]:
                    fig.add_hline(y=y_val, line_dash="dot", line_color=renk, row=3, col=1)
                fig.add_vline(x=son_tarih, line_dash="dot",
                    line_color="#facc15", line_width=1, row="all", col=1)

                fig.update_layout(
                    template="plotly_dark", paper_bgcolor="#0d0f14", plot_bgcolor="#0d0f14",
                    height=750, showlegend=True, xaxis_rangeslider_visible=False,
                    margin=dict(l=10,r=100,t=30,b=10), font=dict(family="Consolas",size=11)
                )
                fig.update_yaxes(gridcolor="#1e293b")
                fig.update_xaxes(gridcolor="#1e293b")
                st.plotly_chart(fig, use_container_width=True)

                st.markdown(f"""
| | |
|---|---|
| **Formasyon** | {s_sec['Formasyon']} |
| **Giris** | {s_sec['Giris']:.2f} TL |
| **Stop** | {s_sec['Stop']:.2f} TL (-%{s_sec['Stop%']}) |
| **Hedef** | {s_sec['Hedef']:.2f} TL (+%{s_sec['Hedef%']}) - {s_sec['HedefR']}R |
| **Stochastic** | {s_sec['Stoch']} |
| **MACD** | {s_sec['MACD']} |
| **Kalite** | {s_sec['Kalite']} - {s_sec['KaliteDetay']} |
| **Uyarilar** | {s_sec['Uyarilar']} |
| **Lot** | {s_sec['Lot']:,} adet |
| **Giris TL** | {s_sec['Giris TL']:,.0f} TL |
""")
                st.info("Fiyat 1R'ye ulasinca stop'unu giris noktasina cek! (Tapi) | Zaman stopu: 18 gun")

    st.markdown("---")
    st.caption("Bu analiz yatirim tavsiyesi degildir.")

if __name__ == "__main__":
    main()
