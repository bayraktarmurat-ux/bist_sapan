import pandas as pd
import yfinance as yf
from datetime import datetime, date
import warnings
import os
warnings.filterwarnings("ignore")

# ─── KOMBİNASYONLAR ────────────────────────────────────────────────────────────
ATR_LISTESI      = [1.0, 1.5, 2.0, 2.5, 3.0]
RR_LISTESI       = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
TOLERANS_LISTESI = [0.01, 0.02, 0.03]  # %1, %2, %3
# 5 ATR x 7 R:R x 3 Tolerans = 105 kombinasyon

# ─── AYARLAR ───────────────────────────────────────────────────────────────────
BAS_TARIH    = date(2022, 1, 1)
BIT_TARIH    = date.today()
PORTFOY      = 1_000_000
MAX_POZISYON = 10
POZ_YUZDE    = 10.0   # % (her pozisyon portföyün bu kadarı)
ATR_PERIYOT  = 14
ENDEKS_AKTIF = True

CIKTI_DOSYA  = f"sapan_kombinasyon_acilis_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"

# ─── SAPAN STRATEJİSİ TOP50 ───────────────────────────────────────────────────
TOP50 = {
    "BURCE","BURVA","GRTHO","PASEU","CRDFA","BYDNR","BAHKM","BMSCH","AKSUE","ARSAN",
    "AKYHO","BRSAN","HEDEF","ISGSY","ICUGS","CRFSA","AVTUR","AKSA","KRGYO","BIGCH",
    "BRKVY","ETYAT","BORLS","BFREN","ULAS","AHGAZ","POLTK","BLCYT","BERA","KLRHO",
    "FLAP","OYAYO","DCTTR","IEYHO","ISKPL","CCOLA","GZNMI","KUVVA","HURGZ","ARENA",
    "RTALB","DYOBY","MANAS","DNISI","OZRDN","GLCVY","SANFM","TURGG","CVKMD","GUBRF",
}

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

# ─── YARDIMCI FONKSİYONLAR ────────────────────────────────────────────────────
def squeeze(s):
    if hasattr(s, "squeeze"):
        s = s.squeeze()
    if hasattr(s, "iloc") and s.ndim == 2:
        s = s.iloc[:, 0]
    return s


def temizle_index(df):
    try:
        if df.index.tz is not None:
            df.index = df.index.tz_convert(None)
        else:
            df.index = df.index.tz_localize(None)
    except Exception:
        df.index = pd.to_datetime(df.index.astype(str).str[:10])
    return df

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
        df = temizle_index(df)
        return df
    except Exception:
        return None

def endeks_filtre_olustur(bas, bit):
    print("  Endeks verisi indiriliyor...")
    try:
        df = yf.download("XU100.IS",
                         start=(bas - pd.DateOffset(years=1)).strftime("%Y-%m-%d"),
                         end=str(bit), interval="1d", progress=False, auto_adjust=True)
        if df.empty:
            return {}
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = temizle_index(df)
        df["EMA200"] = squeeze(df["Close"]).ewm(span=200, adjust=False).mean()
        df.dropna(subset=["EMA200"], inplace=True)
        return {row.Index.date(): float(row.Close) > float(row.EMA200)
                for row in df.itertuples()}
    except Exception as e:
        print(f"  Endeks hatasi: {e} — filtre devre disi.")
        return {}

def hesapla_ind(df, atr_per=14):
    c = squeeze(df["Close"])
    h = squeeze(df["High"])
    l = squeeze(df["Low"])
    for p in [20, 50, 100, 200]:
        df[f"EMA{p}"] = c.ewm(span=p, adjust=False).mean()
    hl = h - l
    hc = (h - c.shift(1)).abs()
    lc = (l - c.shift(1)).abs()
    df["ATR"] = pd.concat([hl, hc, lc], axis=1).max(axis=1).ewm(
        span=atr_per, adjust=False).mean()
    ll       = l.rolling(5).min()
    hh       = h.rolling(5).max()
    k_raw    = 100 * (c - ll) / (hh - ll + 1e-10)
    k_smooth = k_raw.rolling(3).mean()   # Smoothed %K
    df["STOCH_K"] = k_smooth
    df["STOCH_D"] = k_smooth.rolling(3).mean()  # %D
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
    if reversal_low >= float(sub.min()):
        return True
    for col in ["EMA100", "EMA200"]:
        if col in df.columns:
            ema_val = float(df[col].iloc[reversal_idx])
            if not pd.isna(ema_val) and reversal_low <= ema_val * 1.02:
                return True
    return False

def sinyal_uret(hisse_verileri, bas_ts, bit_ts, endeks_f, atr_kat, tolerans):
    gunluk_sinyaller = {}
    for sembol, df in hisse_verileri.items():
        for i in range(2, len(df) - 1):
            son        = df.iloc[i]
            onceki     = df.iloc[i-1]
            sonraki    = df.iloc[i+1]  # giriş günü
            if son.name < bas_ts or son.name > bit_ts:
                continue
            if ENDEKS_AKTIF and not endeks_f.get(son.name.date(), True):
                continue
            if not (float(son["EMA20"]) > float(son["EMA50"]) >
                    float(son["EMA100"]) > float(son["EMA200"])):
                continue
            if float(onceki["STOCH_K"]) >= 30:
                continue
            macd_vals    = df["MACD"].iloc[max(0,i-5):i]
            macd_pozitif = float(son["MACD"]) > 0
            negatif_sure = (macd_vals < 0).sum()
            if not macd_pozitif and negatif_sure >= 5:
                continue
            if float(son["Close"]) <= float(son["Open"]):
                continue
            if float(son["Close"]) <= float(onceki["High"]):
                continue
            if not ema_dokunusu_var_mi(
                float(onceki["Low"]), float(onceki["High"]),
                float(onceki["EMA20"]), float(onceki["EMA50"]),
                float(onceki["EMA100"]), float(onceki["EMA200"]),
                tolerans=tolerans
            ):
                continue
            if not higher_low_kontrol(df, i-1):
                continue
            # Giriş: ertesi günün açılışı
            giris   = float(sonraki["Open"])
            atr_val = float(son["ATR"])
            stop    = round(giris - atr_kat * atr_val, 2)
            if giris - stop <= 0:
                continue
            tarih = sonraki.name  # giriş tarihi
            if tarih not in gunluk_sinyaller:
                gunluk_sinyaller[tarih] = []
            gunluk_sinyaller[tarih].append({
                "sembol": sembol,
                "giris" : giris,
                "stop"  : stop,
                "top50" : sembol in TOP50,
            })
    return gunluk_sinyaller

def backtest_calistir(gunluk_sinyaller, hisse_verileri, bas_ts, bit_ts, rr_kat):
    portfoy_s    = PORTFOY
    acik_pozlar  = []
    kapali_islem = []
    atlanan      = 0

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
        kapalanlar = []
        for poz in acik_pozlar:
            sembol = poz["sembol"]
            if sembol not in hisse_verileri:
                continue
            gunluk = hisse_verileri[sembol]
            gunluk = gunluk[gunluk.index == tarih]
            if gunluk.empty:
                continue
            gun_low  = float(gunluk.iloc[0]["Low"])
            gun_high = float(gunluk.iloc[0]["High"])
            sonuc = None
            if gun_low <= poz["stop"]:
                sonuc = "stop"; cikis = poz["stop"]
            elif gun_high >= poz["hedef"]:
                sonuc = "hedef"; cikis = poz["hedef"]
            if sonuc:
                kaz = (cikis - poz["giris"]) * poz["lot"]
                portfoy_s += kaz
                kapali_islem.append({
                    "Sonuc"   : "Hedef" if sonuc == "hedef" else "Stop",
                    "KZ_TL"   : round(kaz, 0),
                })
                kapalanlar.append(poz)
        for k in kapalanlar:
            acik_pozlar.remove(k)

        if tarih in sinyaller_rr:
            sinyaller_bugun = sorted(sinyaller_rr[tarih], key=lambda x: (not x["top50"]))
            for sinyal in sinyaller_bugun:
                if any(p["sembol"] == sinyal["sembol"] for p in acik_pozlar):
                    continue
                if len(acik_pozlar) >= MAX_POZISYON:
                    atlanan += 1
                    continue
                poz_tl = portfoy_s * (POZ_YUZDE / 100)
                lot    = max(1, int(poz_tl / sinyal["giris"]))
                acik_pozlar.append({
                    "sembol": sinyal["sembol"],
                    "giris" : sinyal["giris"],
                    "stop"  : sinyal["stop"],
                    "hedef" : sinyal["hedef"],
                    "lot"   : lot,
                    "top50" : sinyal["top50"],
                })

    for poz in acik_pozlar:
        sembol = poz["sembol"]
        if sembol not in hisse_verileri:
            continue
        son   = hisse_verileri[sembol].iloc[-1]
        cikis = float(son["Close"])
        kaz   = (cikis - poz["giris"]) * poz["lot"]
        portfoy_s += kaz
        kapali_islem.append({"Sonuc": "Acik", "KZ_TL": round(kaz, 0)})

    df_k     = pd.DataFrame(kapali_islem) if kapali_islem else pd.DataFrame(
        columns=["Sonuc","KZ_TL"])
    tamam    = df_k[df_k["Sonuc"].isin(["Hedef","Stop"])]
    kazanan  = df_k[df_k["Sonuc"] == "Hedef"]
    kaybeden = df_k[df_k["Sonuc"] == "Stop"]
    toplam   = len(tamam)
    wr       = len(kazanan) / toplam * 100 if toplam > 0 else 0
    getiri   = (portfoy_s - PORTFOY) / PORTFOY * 100

    return {
        "Son Portfoy (TL)": round(portfoy_s, 0),
        "Getiri (%)"      : round(getiri, 1),
        "Win Rate (%)"    : round(wr, 1),
        "Toplam Islem"    : toplam,
        "Kazanan"         : len(kazanan),
        "Kaybeden"        : len(kaybeden),
        "Atlanan Sinyal"  : atlanan,
    }

# ─── ANA FONKSİYON ────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("SAPAN STRATEJİSİ KOMBİNASYON BACKTEST (AÇILIŞ FİYATI)")
    print("=" * 60)
    print(f"Tarih: {BAS_TARIH} -> {BIT_TARIH}")
    print(f"Portfoy: {PORTFOY:,} TL | Max Pozisyon: {MAX_POZISYON} | Poz: %{POZ_YUZDE}")
    print(f"Kombinasyon: {len(ATR_LISTESI)} ATR x {len(RR_LISTESI)} R:R x {len(TOLERANS_LISTESI)} Tolerans = "
          f"{len(ATR_LISTESI)*len(RR_LISTESI)*len(TOLERANS_LISTESI)} adet")
    print("=" * 60)

    bas_ts   = pd.Timestamp(BAS_TARIH)
    bit_ts   = pd.Timestamp(BIT_TARIH)
    veri_bas = bas_ts - pd.DateOffset(years=1)
    veri_bit = bit_ts + pd.DateOffset(days=2)

    # Endeks filtresi
    endeks_f = {}
    if ENDEKS_AKTIF:
        endeks_f = endeks_filtre_olustur(bas_ts, veri_bit)
        print(f"  Endeks filtresi: {len(endeks_f)} gun yuklendi.")

    # Hisse verileri
    print(f"\nHisse verileri indiriliyor ({len(BIST_HISSELER)} hisse)...")
    hisse_verileri = {}
    for hi, sembol in enumerate(BIST_HISSELER, 1):
        print(f"\r  {hi}/{len(BIST_HISSELER)} - {sembol}    ", end="", flush=True)
        df_raw = veri_cek(sembol,
                          veri_bas.to_pydatetime().date(),
                          veri_bit.to_pydatetime().date())
        if df_raw is None:
            continue
        try:
            df = hesapla_ind(df_raw.copy(), ATR_PERIYOT)
            df.dropna(subset=["EMA200","STOCH_K","MACD","ATR"], inplace=True)
            if len(df) >= 50:
                hisse_verileri[sembol] = df
        except Exception:
            continue
    print(f"\n  {len(hisse_verileri)} hisse yuklendi.")

    # Kombinasyon backtest
    print(f"\nKombinasyonlar hesaplaniyor...")
    sonuclar    = []
    toplam_adim = len(TOLERANS_LISTESI) * len(ATR_LISTESI) * len(RR_LISTESI)
    adim        = 0

    for tolerans in TOLERANS_LISTESI:
        for atr_kat in ATR_LISTESI:
            gunluk_sinyaller = sinyal_uret(
                hisse_verileri, bas_ts, bit_ts, endeks_f, atr_kat, tolerans
            )
            for rr_kat in RR_LISTESI:
                adim += 1
                print(f"\r  [{adim}/{toplam_adim}] Tolerans %{int(tolerans*100)} | "
                      f"ATR {atr_kat} | R:R {rr_kat}    ", end="", flush=True)
                sonuc = backtest_calistir(
                    gunluk_sinyaller, hisse_verileri, bas_ts, bit_ts, rr_kat
                )
                sonuclar.append({
                    "Tolerans (%)": int(tolerans * 100),
                    "ATR"         : atr_kat,
                    "R:R"         : rr_kat,
                    **sonuc
                })

    print("\n\nTamamlandi!")

    # Sonuçları DataFrame'e al
    df_sonuc = pd.DataFrame(sonuclar)

    # ─── KONSOL ÖZET ──────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("SONUÇLAR — EN İYİ 10 KOMBİNASYON (Getiriye Göre)")
    print("=" * 60)
    top10 = df_sonuc.nlargest(10, "Getiri (%)")
    for _, row in top10.iterrows():
        print(f"  Tolerans %{int(row['Tolerans (%)'])} | ATR {row['ATR']} | R:R {row['R:R']}"
              f"  ->  Getiri: {row['Getiri (%)']:+.1f}%"
              f"  |  Win Rate: {row['Win Rate (%)']:.1f}%"
              f"  |  Islem: {int(row['Toplam Islem'])}")

    print("\n" + "=" * 60)
    print("EN YÜKSEK WIN RATE — İLK 10")
    print("=" * 60)
    top10_wr = df_sonuc.nlargest(10, "Win Rate (%)")
    for _, row in top10_wr.iterrows():
        print(f"  Tolerans %{int(row['Tolerans (%)'])} | ATR {row['ATR']} | R:R {row['R:R']}"
              f"  ->  Win Rate: {row['Win Rate (%)']:.1f}%"
              f"  |  Getiri: {row['Getiri (%)']:+.1f}%"
              f"  |  Islem: {int(row['Toplam Islem'])}")

    best = df_sonuc.loc[df_sonuc["Getiri (%)"].idxmax()]
    print("\n" + "=" * 60)
    print("EN İYİ KOMBİNASYON:")
    print(f"  Tolerans: %{int(best['Tolerans (%)'])} | ATR: {best['ATR']} | R:R: {best['R:R']}")
    print(f"  Getiri  : {best['Getiri (%)']:+.1f}%")
    print(f"  Win Rate: {best['Win Rate (%)']:.1f}%")
    print(f"  Toplam Islem: {int(best['Toplam Islem'])} "
          f"(Kazanan: {int(best['Kazanan'])} | Kaybeden: {int(best['Kaybeden'])})")
    print(f"  Son Portfoy : {int(best['Son Portfoy (TL)']):,} TL")
    print("=" * 60)

    # CSV kaydet
    df_sonuc.to_csv(CIKTI_DOSYA, index=False, encoding="utf-8-sig")
    print(f"\nSonuclar kaydedildi: {CIKTI_DOSYA}")

if __name__ == "__main__":
    main()
