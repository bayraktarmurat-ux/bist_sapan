import pandas as pd
import yfinance as yf
from datetime import datetime
import requests
import os
import warnings
warnings.filterwarnings("ignore")

# ─── TELEGRAM ─────────────────────────────────────────────────────────────────
TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# ─── STRATEJİ PARAMETRELERİ ───────────────────────────────────────────────────
PORTFOY        = 950_000
RISK_YUZDESI   = 1.0
EMA_TOLERANS   = 0.02   # %2 — kombinasyon testinde en iyi sonuç
ATR_KATSAYI    = 1.5    # Stop = Giriş − ATR × 1.5
RR_KATSAYI     = 1.5    # Hedef = Giriş + 1R × 1.5
ZAMAN_STOPU    = 30     # gün — backtest sonucuna göre optimize edildi
ENDEKS_SEMBOL  = "XU100.IS"

# ─── SAPAN STRATEJİSİ TOP50 ───────────────────────────────────────────────────
TOP50 = {
    "BURCE","BURVA","GRTHO","PASEU","CRDFA","BYDNR","BAHKM","BMSCH","AKSUE","ARSAN",
    "AKYHO","BRSAN","HEDEF","ISGSY","ICUGS","CRFSA","AVTUR","AKSA","KRGYO","BIGCH",
    "BRKVY","ETYAT","BORLS","BFREN","ULAS","AHGAZ","POLTK","BLCYT","BERA","KLRHO",
    "FLAP","OYAYO","DCTTR","IEYHO","ISKPL","CCOLA","GZNMI","KUVVA","HURGZ","ARENA",
    "RTALB","DYOBY","MANAS","DNISI","OZRDN","GLCVY","SANFM","TURGG","CVKMD","GUBRF",
}

# ─── HİSSE LİSTESİ ────────────────────────────────────────────────────────────
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

def veri_cek(ticker, gun=300):
    try:
        df = yf.download(ticker + ".IS", period=str(gun) + "d",
                         interval="1d", progress=False, auto_adjust=True)
        if df is None or df.empty or len(df) < 60:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df[["Open","High","Low","Close","Volume"]].copy()
        for col in df.columns:
            df[col] = squeeze(df[col])
        df = df.dropna()
        if len(df) < 60:
            return None
        return df
    except Exception:
        return None

# ─── ENDEKS FİLTRESİ ──────────────────────────────────────────────────────────
def endeks_kontrol():
    try:
        df = yf.download(ENDEKS_SEMBOL, period="300d",
                         interval="1d", progress=False, auto_adjust=True)
        if df.empty:
            return None, None, None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df["EMA200"] = squeeze(df["Close"]).ewm(span=200, adjust=False).mean()
        df.dropna(subset=["EMA200"], inplace=True)
        son  = df.iloc[-1]
        kap  = float(son["Close"])
        e200 = float(son["EMA200"])
        fark = (kap - e200) / e200 * 100
        return kap > e200, round(kap, 0), round(fark, 1)
    except Exception:
        return None, None, None

# ─── İNDİKATÖR HESAPLAMA ──────────────────────────────────────────────────────
def hesapla_ind(df):
    c = squeeze(df["Close"])
    h = squeeze(df["High"])
    l = squeeze(df["Low"])

    df["EMA20"]  = c.ewm(span=20,  adjust=False).mean()
    df["EMA50"]  = c.ewm(span=50,  adjust=False).mean()
    df["EMA100"] = c.ewm(span=100, adjust=False).mean()
    df["EMA200"] = c.ewm(span=200, adjust=False).mean()

    # ATR (14)
    hl = h - l
    hc = (h - c.shift(1)).abs()
    lc = (l - c.shift(1)).abs()
    df["ATR"] = pd.concat([hl, hc, lc], axis=1).max(axis=1).ewm(
        span=14, adjust=False).mean()

    # Stochastic (5,3,3)
    ll    = l.rolling(5).min()
    hh    = h.rolling(5).max()
    k_raw = 100 * (c - ll) / (hh - ll + 1e-9)
    df["STOCH_K"] = k_raw.rolling(3).mean()

    # MACD (50,100,9)
    ema_h = c.ewm(span=50,  adjust=False).mean()
    ema_y = c.ewm(span=100, adjust=False).mean()
    df["MACD"] = ema_h - ema_y

    return df

# ─── EMA DOKUNUŞ KONTROLÜ ─────────────────────────────────────────────────────
def ema_dokunusu_var_mi(low_val, high_val, ema20, ema50, ema100, ema200):
    for ema_val in [ema20, ema50, ema100, ema200]:
        if pd.isna(ema_val):
            continue
        if low_val <= ema_val * (1 + EMA_TOLERANS) and \
           high_val >= ema_val * (1 - EMA_TOLERANS):
            return True
    return False

# ─── HIGHER LOW KONTROLÜ ──────────────────────────────────────────────────────
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
    # İstisna: derin EMA dokunuşu
    for col in ["EMA100", "EMA200"]:
        if col in df.columns:
            ema_val = float(df[col].iloc[reversal_idx])
            if not pd.isna(ema_val) and reversal_low <= ema_val * 1.02:
                return True
    return False

# ─── SAPAN STRATEJİSİ SİNYAL TARAMA ──────────────────────────────────────────
def sinyal_tara(df):
    """
    Sapan Stratejisi:
    1. EMA20 > EMA50 > EMA100 > EMA200
    2. Stochastic (5,3,3) < 30 (dönüş mumunda)
    3. MACD (50,100,9) pozitif veya 5'ten az süredir negatif
    4. Onay mumu yeşil ve dönüş mumunun high'ını kırmış
    5. Dönüş mumu EMA'ya dokunmuş
    6. Higher low
    """
    df = df.copy()
    df = hesapla_ind(df)
    df.dropna(subset=["EMA200","STOCH_K","MACD","ATR"], inplace=True)

    if len(df) < 3:
        return None

    son        = df.iloc[-1]
    onceki     = df.iloc[-2]
    iki_onceki = df.iloc[-3]

    # 1. EMA Trend
    if not (float(son["EMA20"]) > float(son["EMA50"]) >
            float(son["EMA100"]) > float(son["EMA200"])):
        return None

    # 2. Stochastic < 30 (dönüş mumunda)
    if float(onceki["STOCH_K"]) >= 30:
        return None

    # 3. MACD pozitif veya 5'ten az süredir negatif
    macd_vals    = df["MACD"].iloc[-6:-1]
    macd_pozitif = float(son["MACD"]) > 0
    negatif_sure = (macd_vals < 0).sum()
    if not macd_pozitif and negatif_sure >= 5:
        return None

    # 4. Onay mumu yeşil ve dönüş mumunun high'ını kırmış
    if float(son["Close"]) <= float(son["Open"]):
        return None
    if float(son["Close"]) <= float(onceki["High"]):
        return None

    # 5. EMA dokunuşu (dönüş mumunda)
    if not ema_dokunusu_var_mi(
        float(onceki["Low"]), float(onceki["High"]),
        float(onceki["EMA20"]), float(onceki["EMA50"]),
        float(onceki["EMA100"]), float(onceki["EMA200"])
    ):
        return None

    # 6. Higher Low
    reversal_idx = len(df) - 2
    if not higher_low_kontrol(df, reversal_idx):
        return None

    # Formasyon tipi
    rev_govde    = abs(float(onceki["Close"]) - float(onceki["Open"]))
    rev_range    = float(onceki["High"]) - float(onceki["Low"])
    rev_alt_fitil = (min(float(onceki["Open"]), float(onceki["Close"])) -
                     float(onceki["Low"]))
    if rev_range > 0:
        alt_fitil_oran = rev_alt_fitil / rev_range
        govde_oran     = rev_govde / rev_range
        if alt_fitil_oran >= 0.5 and govde_oran <= 0.35:
            formasyon = "Pin Bar"
        else:
            govde_dusuk = min(float(onceki["Open"]), float(onceki["Close"]))
            govde_yukse = max(float(onceki["Open"]), float(onceki["Close"]))
            govde_ema_deler = any(
                govde_dusuk <= float(onceki[col]) <= govde_yukse
                for col in ["EMA20","EMA50","EMA100","EMA200"]
                if not pd.isna(float(onceki[col]))
            )
            ic_donus = (float(onceki["High"]) < float(iki_onceki["High"]) and
                        float(onceki["Low"])  > float(iki_onceki["Low"]))
            if govde_ema_deler:
                formasyon = "Govde Delis"
            elif ic_donus:
                formasyon = "Ic Donus"
            else:
                formasyon = "2 Mum"
    else:
        formasyon = "2 Mum"

    # Giriş / Stop / Hedef — ATR bazlı (backtest parametreleriyle uyumlu)
    giris   = float(son["Close"])  # onay mumu kapanışı = giriş
    atr_val = float(son["ATR"])
    stop    = round(giris - ATR_KATSAYI * atr_val, 2)
    bir_r   = giris - stop
    if bir_r <= 0:
        return None
    hedef   = round(giris + RR_KATSAYI * bir_r, 2)
    stop_p  = round((giris - stop) / giris * 100, 1)
    hedef_p = round((hedef - giris) / giris * 100, 1)
    stoch   = round(float(onceki["STOCH_K"]), 1)
    macd    = round(float(son["MACD"]), 4)

    return {
        "giris"    : round(giris, 2),
        "kapanis"  : round(float(son["Close"]), 2),
        "stop"     : stop,
        "stop_p"   : stop_p,
        "hedef"    : hedef,
        "hedef_p"  : hedef_p,
        "stoch"    : stoch,
        "macd"     : macd,
        "formasyon": formasyon,
    }

# ─── TELEGRAM ─────────────────────────────────────────────────────────────────
def telegram_gonder(mesaj):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram token/chat_id eksik!")
        return False
    url  = "https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": mesaj, "parse_mode": "HTML"}
    try:
        r = requests.post(url, data=data, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print("Telegram hatasi:", e)
        return False

# ─── ANA FONKSİYON ────────────────────────────────────────────────────────────
def main():
    print("Tarama basliyor:", datetime.now().strftime("%Y-%m-%d %H:%M"))
    tarih = datetime.now().strftime("%d.%m.%Y %H:%M")

    # Endeks kontrolu
    endeks_ok, xu100, xu_fark = endeks_kontrol()

    if endeks_ok is False:
        mesaj  = "<b>BIST Sapan Tarayici - " + tarih + "</b>\n\n"
        mesaj += "BIST100 EMA200 altinda!\n"
        mesaj += "XU100: " + str(xu100) + " TL"
        if xu_fark is not None:
            mesaj += " (" + str(xu_fark) + "%)"
        mesaj += "\n\nStrateji bugun pasif, islem onerilmez."
        telegram_gonder(mesaj)
        print("Endeks pasif, islem yok.")
        return

    endeks_durum = ""
    if xu100 and xu_fark is not None:
        isaret = "+" if xu_fark >= 0 else ""
        endeks_durum = "XU100: " + str(xu100) + " (" + isaret + str(xu_fark) + "%)"

    # Hisse tarama
    risk_tl   = PORTFOY * RISK_YUZDESI / 100
    sinyaller = []

    for hisse in HISSELER:
        df = veri_cek(hisse)
        if df is None:
            continue
        try:
            sonuc = sinyal_tara(df)
        except Exception as e:
            print("Hata -", hisse, ":", e)
            continue
        if sonuc is None:
            continue

        risk_hisse = sonuc["giris"] - sonuc["stop"]
        if risk_hisse <= 0:
            continue
        lot      = max(1, int(risk_tl / risk_hisse))
        giris_tl = round(lot * sonuc["giris"], 0)
        top50    = hisse in TOP50

        sinyaller.append({
            "hisse"    : hisse,
            "top50"    : top50,
            "giris"    : sonuc["giris"],
            "kapanis"  : sonuc["kapanis"],
            "stop"     : sonuc["stop"],
            "stop_p"   : sonuc["stop_p"],
            "hedef"    : sonuc["hedef"],
            "hedef_p"  : sonuc["hedef_p"],
            "stoch"    : sonuc["stoch"],
            "macd"     : sonuc["macd"],
            "formasyon": sonuc["formasyon"],
            "lot"      : lot,
            "giris_tl" : giris_tl,
            "risk_tl"  : round(risk_tl, 0),
        })

    # TOP50 once, sonra stoch kucukten buyuge sirala (en cok satilmis once)
    sinyaller.sort(key=lambda x: (not x["top50"], x["stoch"]))

    top50_count = sum(1 for s in sinyaller if s["top50"])

    # Sinyal yok
    if not sinyaller:
        mesaj  = "<b>BIST Sapan Tarayici - " + tarih + "</b>\n"
        if endeks_durum:
            mesaj += endeks_durum + "\n"
        mesaj += "\nBugun sinyal bulunamadi."
        telegram_gonder(mesaj)
        print("Sinyal yok.")
        return

    # Baslik mesaji
    baslik  = "<b>BIST Sapan Stratejisi - " + tarih + "</b>\n"
    if endeks_durum:
        baslik += endeks_durum + "\n"
    baslik += str(len(sinyaller)) + " sinyal"
    if top50_count > 0:
        baslik += " | " + str(top50_count) + " adet TOP50"
    baslik += "\nPortfoy: " + str(PORTFOY) + " TL | Risk: %" + str(RISK_YUZDESI)
    baslik += "\nATR: " + str(ATR_KATSAYI) + " | R:R 1:" + str(RR_KATSAYI) + " | Zaman Stopu: " + str(ZAMAN_STOPU) + " gun"
    baslik += "\n" + "─" * 22
    baslik += "\n<i>Giris icin onay mumu kapanis beklenmeli!</i>"
    telegram_gonder(baslik)

    # Her sinyal icin mesaj
    for s in sinyaller:
        star   = " STAR " if s["top50"] else ""
        mesaj  = "<b>" + star + s["hisse"] + star + "</b> [" + s["formasyon"] + "]\n"
        mesaj += "Kapanis: " + str(s["kapanis"]) + " TL\n"
        mesaj += "Giris:   <b>" + str(s["giris"]) + " TL</b>\n"
        mesaj += "Stop:    " + str(s["stop"]) + " (-%" + str(s["stop_p"]) + ")\n"
        mesaj += "Hedef:   " + str(s["hedef"]) + " (+%" + str(s["hedef_p"]) + ") [" + str(RR_KATSAYI) + "R]\n"
        mesaj += "Stoch:   " + str(s["stoch"]) + " | MACD: " + str(s["macd"]) + "\n"
        mesaj += "Lot:     " + str(s["lot"]) + " adet | " + str(int(s["giris_tl"])) + " TL\n"
        mesaj += "Risk:    " + str(int(s["risk_tl"])) + " TL\n"
        mesaj += "Zaman Stopu: " + str(ZAMAN_STOPU) + ". gunde kapat"
        telegram_gonder(mesaj)
        print("Sinyal gonderildi:", s["hisse"], "| TOP50:" if s["top50"] else "")

    print("Tamamlandi. Toplam sinyal:", len(sinyaller))

if __name__ == "__main__":
    main()
