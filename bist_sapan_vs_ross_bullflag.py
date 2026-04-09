import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, date
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="BIST Strateji Karşılaştırma",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0a0c10; }
    .metric-card {
        background: #0f1117;
        border: 1px solid #1e2535;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    .metric-label { color: #64748b; font-size: 12px; margin-bottom: 4px; }
    .metric-value { color: #f1f5f9; font-size: 22px; font-weight: 700; }
    .metric-value.green { color: #22c55e; }
    .metric-value.red   { color: #ef4444; }
    .metric-value.blue  { color: #38bdf8; }
    .strat-header-sapan    { color: #f59e0b; font-weight: 700; }
    .strat-header-bullflag { color: #38bdf8; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ─── HİSSE LİSTESİ ────────────────────────────────────────────────────────────
HISSELER = [
    "AKSA","AKSEN","ARCLK","ARENA","ARSAN","ASELS","ASTOR","AYGAZ","BIMAS","BRSAN",
    "BURCE","BURVA","CCOLA","CRDFA","CVKMD","DOHOL","EREGL","FROTO","GARAN","GUBRF",
    "HALKB","HEDEF","HEKTS","HURGZ","ISCTR","ISGSY","ISGYO","ISKPL","KCHOL","KLRHO",
    "KORDS","KRGYO","KUVVA","LOGO","MAVI","MGROS","ODAS","OTKAR","OYAYO","PGSUS",
    "PETKM","SAHOL","SASA","SISE","SKBNK","SOKM","TAVHL","TCELL","THYAO","TKFEN",
    "TOASO","TSKB","TTKOM","TTRAK","TUPRS","TURGG","ULKER","VAKBN","VESTL","YKBNK",
    "BFREN","BIGCH","BLCYT","BYDNR","BAHKM","BMSCH","PASEU","GRTHO","AKSUE","BRKVY",
    "ETYAT","BORLS","AHGAZ","POLTK","BERA","FLAP","DCTTR","IEYHO","GZNMI","RTALB",
    "DYOBY","MANAS","DNISI","OZRDN","GLCVY","SANFM","CRFSA","AVTUR","KLGYO","BRISA",
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

def safe_float(val):
    """DataFrame, Series veya scalar'dan güvenli float çıkar."""
    if isinstance(val, pd.DataFrame):
        val = val.iloc[0, 0]
    elif isinstance(val, pd.Series):
        val = val.iloc[0]
    return float(val)

def veri_cek(ticker, baslangic, bitis):
    try:
        df = yf.download(
            ticker + ".IS",
            start=baslangic, end=bitis,
            interval="1d", progress=False, auto_adjust=True
        )
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

def macd_hesapla(close, hizli=50, yavas=100, sinyal=9):
    close = squeeze(close)
    ema_h = close.ewm(span=hizli,  adjust=False).mean()
    ema_y = close.ewm(span=yavas,  adjust=False).mean()
    macd      = ema_h - ema_y
    macd_sig  = macd.ewm(span=sinyal, adjust=False).mean()
    macd_his  = macd - macd_sig
    return macd, macd_sig, macd_his

# ─── SAPAN STRATEJİSİ SİNYAL ─────────────────────────────────────────────────
def sapan_sinyal(df, ema_tolerans=0.03, atr_kat=1.5, rr_kat=1.5):
    """
    Sapan Stratejisi sinyal kontrolü.
    Dön: (giris, stop, hedef) veya None
    """
    df = df.copy()
    for col in df.columns:
        df[col] = squeeze(df[col])

    close  = df["Close"]
    df["EMA20"]  = ema(close, 20)
    df["EMA50"]  = ema(close, 50)
    df["EMA100"] = ema(close, 100)
    df["EMA200"] = ema(close, 200)
    df["ATR"]    = atr_hesapla(df, 14)
    df["STOCH_K"], _ = stochastic_hesapla(df, 5, 3, 3)
    df["MACD"], _, _ = macd_hesapla(close, 50, 100, 9)
    df.dropna(subset=["EMA200","ATR","STOCH_K","MACD"], inplace=True)

    if len(df) < 3:
        return None

    son        = df.iloc[-1]
    onceki     = df.iloc[-2]
    iki_onceki = df.iloc[-3]

    # EMA Trend: EMA20 > EMA50 > EMA100 > EMA200
    if not (float(son["EMA20"]) > float(son["EMA50"]) >
            float(son["EMA100"]) > float(son["EMA200"])):
        return None

    # Stochastic < 30
    if float(onceki["STOCH_K"]) >= 30:
        return None

    # MACD filtresi
    macd_vals = df["MACD"].iloc[-6:-1]
    macd_pozitif = float(son["MACD"]) > 0
    negatif_sure = (macd_vals < 0).sum()
    if not macd_pozitif and negatif_sure >= 5:
        return None

    # Onay mumu yeşil ve dönüş mumunun yüksek'ini kırıyor
    if float(son["Close"]) <= float(son["Open"]):
        return None
    if float(son["Close"]) <= float(onceki["High"]):
        return None

    # EMA dokunuşu
    dokundu = False
    for ema_val in [float(onceki["EMA20"]), float(onceki["EMA50"]),
                    float(onceki["EMA100"]), float(onceki["EMA200"])]:
        if pd.isna(ema_val):
            continue
        band_low  = ema_val * (1 - ema_tolerans)
        band_high = ema_val * (1 + ema_tolerans)
        if float(onceki["Low"]) <= band_high and float(onceki["High"]) >= band_low:
            dokundu = True
            break
    if not dokundu:
        return None

    # Giriş / Stop / Hedef
    atr_val = float(son["ATR"])
    giris   = float(onceki["High"])
    stop    = giris - atr_kat * atr_val
    bir_r   = giris - stop
    if bir_r <= 0:
        return None
    hedef = giris + rr_kat * bir_r

    return giris, stop, hedef

# ─── BULL FLAG STRATEJİSİ SİNYAL ─────────────────────────────────────────────
def bullflag_sinyal(df, atr_kat=1.5, rr_kat=1.5,
                    hacim_kat=2.0, pullback_min=2, pullback_max=4):
    """
    Bull Flag Stratejisi sinyal kontrolü.
    Koşullar:
    1. Güçlü yükseliş: En az 3 ardışık yeşil mum, yüksek hacim
    2. Pullback: 2-4 kırmızı/yatay mum, düşük hacim
    3. Giriş: Pullback sonrası ilk yeni zirveyi kıran mum
    4. EMA20 üzerinde fiyat
    5. Stop: Pullback dibi (ATR ile sınırlı)
    Dön: (giris, stop, hedef) veya None
    """
    df = df.copy()
    for col in df.columns:
        df[col] = squeeze(df[col])

    close  = df["Close"]
    high   = df["High"]
    low    = df["Low"]
    open_  = df["Open"]
    volume = df["Volume"]

    df["EMA20"]  = ema(close, 20)
    df["ATR"]    = atr_hesapla(df, 14)
    df["Vol_MA20"] = volume.rolling(20).mean()
    df.dropna(subset=["EMA20","ATR","Vol_MA20"], inplace=True)

    if len(df) < 10:
        return None

    son = df.iloc[-1]

    # Onay mumu yeşil olmalı
    if float(son["Close"]) <= float(son["Open"]):
        return None

    # Fiyat EMA20 üzerinde olmalı
    if float(son["Close"]) < float(son["EMA20"]):
        return None

    # Pullback tespiti: son 2-4 mum düşüş/yatay
    for pb_len in range(pullback_min, pullback_max + 1):
        if len(df) < pb_len + 4:
            continue

        pullback_df = df.iloc[-(pb_len + 1):-1]

        # Pullback mumları: kapanış < açılış veya çok küçük hareket
        pb_ok = all(
            float(pullback_df["Close"].iloc[i]) <= float(pullback_df["Open"].iloc[i]) * 1.005
            for i in range(len(pullback_df))
        )
        if not pb_ok:
            continue

        # Pullback hacmi düşük olmalı (yükseliş hacminin altında)
        pb_vol_avg = pullback_df["Volume"].mean()
        pb_low     = float(pullback_df["Low"].min())

        # Yükseliş tespiti: pullback öncesi en az 3 yeşil mum
        yukselis_df = df.iloc[-(pb_len + 4):-(pb_len + 1)]
        if len(yukselis_df) < 3:
            continue

        yukselis_yesil = sum(
            1 for i in range(len(yukselis_df))
            if float(yukselis_df["Close"].iloc[i]) > float(yukselis_df["Open"].iloc[i])
        )
        if yukselis_yesil < 2:
            continue

        # Yükseliş hacmi yüksek olmalı
        yukselis_vol = yukselis_df["Volume"].mean()
        vol_ma = float(son["Vol_MA20"])
        if yukselis_vol < vol_ma * hacim_kat:
            continue

        # Pullback hacmi yükselişten düşük olmalı
        if pb_vol_avg >= yukselis_vol * 0.9:
            continue

        # Pullback öncesi en yüksek nokta
        pb_oncesi_high = float(yukselis_df["High"].max())

        # Onay mumu pullback yüksekliğini kırıyor mu?
        pullback_high = float(pullback_df["High"].max())
        if float(son["Close"]) <= pullback_high:
            continue

        # Giriş / Stop / Hedef
        atr_val = float(son["ATR"])
        giris   = pullback_high  # pullback zirvesini kıran fiyat
        stop    = pb_low
        bir_r   = giris - stop

        # Stop çok geniş olmasın (ATR * atr_kat ile sınırla)
        if bir_r > atr_kat * atr_val:
            stop  = giris - atr_kat * atr_val
            bir_r = giris - stop

        if bir_r <= 0:
            continue

        hedef = giris + rr_kat * bir_r
        return giris, stop, hedef

    return None

# ─── PORTFÖY BACKTEST MOTORu ──────────────────────────────────────────────────
def portfoy_backtest(hisseler, baslangic, bitis,
                     strateji_fn, strateji_params,
                     baslangic_sermaye=1_000_000,
                     maks_pozisyon=10,
                     pozisyon_yuzde=0.10,
                     zaman_stopu=18,
                     progress_bar=None):
    """
    Gerçekçi portföy backtesti:
    - Sermaye yetmezse yeni işlem açılmaz
    - Maks 10 eş zamanlı pozisyon
    - Her pozisyon sermayenin %10'u
    - Zaman stopu: 18 gün
    - Ertesi günün açılış fiyatından giriş
    """
    sermaye    = baslangic_sermaye
    pozisyonlar = {}  # {hisse: {giris, stop, hedef, lot, tarih, sermaye_kullanim}}
    islemler   = []
    sermaye_serisi = []
    tarihler   = []

    # Tüm hisselerin verisini çek
    tum_veriler = {}
    for i, hisse in enumerate(hisseler):
        if progress_bar:
            progress_bar.progress((i + 1) / len(hisseler),
                                  text=f"Veri indiriliyor: {hisse}")
        df = veri_cek(hisse, baslangic, bitis)
        if df is not None and len(df) >= 60:
            tum_veriler[hisse] = df

    if not tum_veriler:
        return None

    # Ortak tarih aralığı oluştur
    tum_tarihler = sorted(set(
        t for df in tum_veriler.values() for t in df.index
    ))

    for gun_idx, bugun in enumerate(tum_tarihler):
        # ── Açık Pozisyonları Güncelle ──────────────────────────────────────
        kapatilacaklar = []
        for hisse, poz in pozisyonlar.items():
            if hisse not in tum_veriler:
                kapatilacaklar.append((hisse, "veri_yok", 0))
                continue
            df = tum_veriler[hisse]
            if bugun not in df.index:
                continue

            gun_verisi = df.loc[bugun]
            yuksek  = safe_float(gun_verisi["High"])
            dusuk   = safe_float(gun_verisi["Low"])
            kapanis = safe_float(gun_verisi["Close"])

            # Stop tetiklendi mi?
            if dusuk <= poz["stop"]:
                kapatilacaklar.append((hisse, "stop", poz["stop"]))
            # Hedef tetiklendi mi?
            elif yuksek >= poz["hedef"]:
                kapatilacaklar.append((hisse, "hedef", poz["hedef"]))
            # Zaman stopu?
            elif (gun_idx - poz["gun_idx"]) >= zaman_stopu:
                kapatilacaklar.append((hisse, "zaman", kapanis))

        for hisse, neden, cikis_fiyat in kapatilacaklar:
            poz = pozisyonlar.pop(hisse)
            kaz = (cikis_fiyat - poz["giris"]) * poz["lot"]
            sermaye += poz["sermaye_kullanim"] + kaz
            islemler.append({
                "Tarih_Giris" : poz["tarih"],
                "Tarih_Cikis" : bugun,
                "Hisse"       : hisse,
                "Giris"       : round(poz["giris"], 2),
                "Cikis"       : round(cikis_fiyat, 2),
                "Stop"        : round(poz["stop"], 2),
                "Hedef"       : round(poz["hedef"], 2),
                "Lot"         : poz["lot"],
                "Kar_Zarar"   : round(kaz, 2),
                "Neden"       : neden,
                "Sonuc"       : "Kazandı" if kaz > 0 else "Kaybetti",
            })

        # ── Yeni Sinyal Tara ────────────────────────────────────────────────
        if len(pozisyonlar) < maks_pozisyon:
            for hisse, df in tum_veriler.items():
                if hisse in pozisyonlar:
                    continue
                if len(pozisyonlar) >= maks_pozisyon:
                    break

                # Bugüne kadar olan veriyle sinyal üret (look-ahead bias yok)
                df_slice = df[df.index <= bugun]
                if len(df_slice) < 60:
                    continue

                # Sinyal bugün oluştu mu?
                sonuc = strateji_fn(df_slice, **strateji_params)
                if sonuc is None:
                    continue

                giris, stop, hedef = sonuc

                # Ertesi gün açılışını bul
                sonraki_gunler = [t for t in tum_tarihler if t > bugun]
                if not sonraki_gunler:
                    continue
                sonraki_gun = sonraki_gunler[0]

                if hisse not in tum_veriler:
                    continue
                df_hisse = tum_veriler[hisse]
                if sonraki_gun not in df_hisse.index:
                    continue

                acilis = safe_float(df_hisse.loc[sonraki_gun]["Open"])

                # Açılış gap kontrolü: çok yüksek açılırsa atla
                if acilis > giris * 1.03:
                    continue

                # Gerçek giriş açılış fiyatı
                gercek_giris = acilis
                bir_r = gercek_giris - stop
                if bir_r <= 0:
                    continue
                gercek_hedef = gercek_giris + (hedef - giris) + (acilis - giris)

                # Sermaye kontrolü
                sermaye_kullanim = sermaye * pozisyon_yuzde
                if sermaye_kullanim > sermaye:
                    continue
                if sermaye < baslangic_sermaye * 0.05:  # Sermaye bitti
                    continue

                lot = int(sermaye_kullanim / gercek_giris)
                if lot < 1:
                    continue

                gercek_maliyet = lot * gercek_giris
                sermaye -= gercek_maliyet

                pozisyonlar[hisse] = {
                    "giris"          : gercek_giris,
                    "stop"           : stop,
                    "hedef"          : gercek_hedef,
                    "lot"            : lot,
                    "tarih"          : sonraki_gun,
                    "gun_idx"        : gun_idx,
                    "sermaye_kullanim": gercek_maliyet,
                }

        # Günlük sermaye kaydı (açık pozisyonların anlık değeri dahil)
        acik_deger = sum(
            poz["lot"] * safe_float(tum_veriler[h].loc[bugun]["Close"])
            for h, poz in pozisyonlar.items()
            if h in tum_veriler and bugun in tum_veriler[h].index
        )
        toplam_deger = sermaye + acik_deger
        sermaye_serisi.append(toplam_deger)
        tarihler.append(bugun)

    # Açık kalan pozisyonları son fiyatla kapat
    son_gun = tum_tarihler[-1] if tum_tarihler else None
    if son_gun:
        for hisse, poz in list(pozisyonlar.items()):
            if hisse in tum_veriler and son_gun in tum_veriler[hisse].index:
                kapanis = safe_float(tum_veriler[hisse].loc[son_gun]["Close"])
                kaz = (kapanis - poz["giris"]) * poz["lot"]
                islemler.append({
                    "Tarih_Giris" : poz["tarih"],
                    "Tarih_Cikis" : son_gun,
                    "Hisse"       : hisse,
                    "Giris"       : round(poz["giris"], 2),
                    "Cikis"       : round(kapanis, 2),
                    "Stop"        : round(poz["stop"], 2),
                    "Hedef"       : round(poz["hedef"], 2),
                    "Lot"         : poz["lot"],
                    "Kar_Zarar"   : round(kaz, 2),
                    "Neden"       : "dönem_sonu",
                    "Sonuc"       : "Kazandı" if kaz > 0 else "Kaybetti",
                })

    df_islemler = pd.DataFrame(islemler)
    df_sermaye  = pd.DataFrame({"Tarih": tarihler, "Sermaye": sermaye_serisi})
    df_sermaye.set_index("Tarih", inplace=True)

    return df_islemler, df_sermaye

# ─── METRİK HESAPLA ───────────────────────────────────────────────────────────
def metrik_hesapla(df_islemler, df_sermaye, baslangic_sermaye):
    if df_islemler is None or df_islemler.empty:
        return {}

    toplam_islem  = len(df_islemler)
    kazananlar    = df_islemler[df_islemler["Sonuc"] == "Kazandı"]
    kaybedenler   = df_islemler[df_islemler["Sonuc"] == "Kaybetti"]
    win_rate      = len(kazananlar) / toplam_islem * 100 if toplam_islem > 0 else 0
    ort_kazanc    = kazananlar["Kar_Zarar"].mean() if len(kazananlar) > 0 else 0
    ort_kayip     = kaybedenler["Kar_Zarar"].mean() if len(kaybedenler) > 0 else 0
    toplam_kaz    = df_islemler["Kar_Zarar"].sum()
    gercek_rr     = abs(ort_kazanc / ort_kayip) if ort_kayip != 0 else 0

    # Max Drawdown
    if df_sermaye is not None and not df_sermaye.empty:
        peak      = df_sermaye["Sermaye"].cummax()
        drawdown  = (df_sermaye["Sermaye"] - peak) / peak * 100
        max_dd    = drawdown.min()
        son_deger = df_sermaye["Sermaye"].iloc[-1]
    else:
        max_dd    = 0
        son_deger = baslangic_sermaye

    toplam_getiri = (son_deger - baslangic_sermaye) / baslangic_sermaye * 100

    # Ardışık max kayıp
    sonuclar = df_islemler["Sonuc"].tolist()
    max_kay_seri = 0
    mevcut = 0
    for s in sonuclar:
        if s == "Kaybetti":
            mevcut += 1
            max_kay_seri = max(max_kay_seri, mevcut)
        else:
            mevcut = 0

    # Beklenti değeri (EV)
    ev = (win_rate/100 * ort_kazanc) + ((1 - win_rate/100) * ort_kayip) if toplam_islem > 0 else 0

    # Kazanma nedeni dağılımı
    hedef_oran = len(df_islemler[df_islemler["Neden"] == "hedef"]) / toplam_islem * 100 if toplam_islem > 0 else 0
    stop_oran  = len(df_islemler[df_islemler["Neden"] == "stop"])  / toplam_islem * 100 if toplam_islem > 0 else 0
    zaman_oran = len(df_islemler[df_islemler["Neden"].isin(["zaman","dönem_sonu"])]) / toplam_islem * 100 if toplam_islem > 0 else 0

    return {
        "toplam_islem"  : toplam_islem,
        "win_rate"      : win_rate,
        "ort_kazanc"    : ort_kazanc,
        "ort_kayip"     : ort_kayip,
        "gercek_rr"     : gercek_rr,
        "toplam_kaz"    : toplam_kaz,
        "toplam_getiri" : toplam_getiri,
        "max_dd"        : max_dd,
        "max_kay_seri"  : max_kay_seri,
        "ev"            : ev,
        "son_deger"     : son_deger,
        "hedef_oran"    : hedef_oran,
        "stop_oran"     : stop_oran,
        "zaman_oran"    : zaman_oran,
    }

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
st.sidebar.title("⚙️ Backtest Ayarları")

st.sidebar.markdown("### 📅 Dönem")
baslangic_secenekler = {
    "2020 Başı (Pandemi dahil)": date(2020, 1, 1),
    "2022 Başı (Sapan dönemi)":  date(2022, 1, 1),
    "2023 Başı (Son dönem)":     date(2023, 1, 1),
}
secilen_donem = st.sidebar.selectbox("Başlangıç tarihi", list(baslangic_secenekler.keys()), index=1)
baslangic_tarihi = baslangic_secenekler[secilen_donem]
bitis_tarihi = date.today()

st.sidebar.markdown("### 💼 Portföy")
baslangic_sermaye = st.sidebar.number_input(
    "Başlangıç Sermayesi (TL)",
    min_value=100_000, max_value=10_000_000,
    value=1_000_000, step=100_000
)

st.sidebar.markdown("### 📊 Ortak Parametreler")
atr_kat = st.sidebar.select_slider("ATR Stop Katsayısı", [1.0, 1.5, 2.0, 2.5], value=1.5)
rr_kat  = st.sidebar.select_slider("R:R Katsayısı",     [1.0, 1.5, 2.0, 2.5, 3.0], value=1.5)

st.sidebar.markdown("### 🎯 Sapan Parametreleri")
ema_tolerans = st.sidebar.select_slider("EMA Toleransı (%)", [1, 2, 3], value=3) / 100

st.sidebar.markdown("### 🚩 Bull Flag Parametreleri")
hacim_kat    = st.sidebar.select_slider("Hacim Eşiği (x MA20)", [1.5, 2.0, 2.5, 3.0], value=2.0)
pullback_min = st.sidebar.slider("Pullback Min Mum", 1, 3, 2)
pullback_max = st.sidebar.slider("Pullback Max Mum", 3, 6, 4)

calistir = st.sidebar.button("🚀 Backtest Çalıştır", use_container_width=True, type="primary")

# ─── ANA SAYFA ────────────────────────────────────────────────────────────────
st.title("⚖️ BIST Strateji Karşılaştırma")
st.caption("Sapan Stratejisi  vs  Bull Flag Stratejisi  |  Gerçekçi Portföy Backtesti")

col_info1, col_info2, col_info3, col_info4 = st.columns(4)
with col_info1:
    st.info(f"📅 **{secilen_donem}**")
with col_info2:
    st.info(f"💰 **{baslangic_sermaye:,.0f} TL** başlangıç")
with col_info3:
    st.info(f"📦 **{len(HISSELER)} hisse** taranıyor")
with col_info4:
    st.info("⚙️ **Maks 10 pozisyon | %10 per işlem**")

if not calistir:
    st.markdown("""
    <div style='text-align:center; padding: 60px; color: #475569;'>
        <h2>Sol panelden parametreleri ayarlayın ve</h2>
        <h1>🚀 Backtest Çalıştır</h1>
        <p>butonuna basın</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─── BACKTEST ÇALIŞTIR ────────────────────────────────────────────────────────
st.markdown("---")

col_s, col_b = st.columns(2)

with col_s:
    st.markdown("### 🟡 Sapan Stratejisi")
    pb_sapan = st.progress(0, text="Başlıyor...")

with col_b:
    st.markdown("### 🔵 Bull Flag Stratejisi")
    pb_bullflag = st.progress(0, text="Başlıyor...")

# Sapan backtest
sapan_params = {
    "ema_tolerans": ema_tolerans,
    "atr_kat"     : atr_kat,
    "rr_kat"      : rr_kat,
}
sapan_sonuc = portfoy_backtest(
    HISSELER, baslangic_tarihi, bitis_tarihi,
    sapan_sinyal, sapan_params,
    baslangic_sermaye=baslangic_sermaye,
    progress_bar=pb_sapan
)
pb_sapan.progress(1.0, text="✅ Tamamlandı")

# Bull Flag backtest
bf_params = {
    "atr_kat"    : atr_kat,
    "rr_kat"     : rr_kat,
    "hacim_kat"  : hacim_kat,
    "pullback_min": pullback_min,
    "pullback_max": pullback_max,
}
bf_sonuc = portfoy_backtest(
    HISSELER, baslangic_tarihi, bitis_tarihi,
    bullflag_sinyal, bf_params,
    baslangic_sermaye=baslangic_sermaye,
    progress_bar=pb_bullflag
)
pb_bullflag.progress(1.0, text="✅ Tamamlandı")

# ─── METRİKLER ────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## 📊 Karşılaştırma Tablosu")

if sapan_sonuc is None or bf_sonuc is None:
    st.error("Backtest verisi alınamadı. Lütfen tekrar deneyin.")
    st.stop()

df_sapan_islem,   df_sapan_sermaye   = sapan_sonuc
df_bf_islem,      df_bf_sermaye      = bf_sonuc

m_s = metrik_hesapla(df_sapan_islem,   df_sapan_sermaye,   baslangic_sermaye)
m_b = metrik_hesapla(df_bf_islem,      df_bf_sermaye,      baslangic_sermaye)

def renk(val, ters=False):
    if ters:
        return "green" if val < 0 else "red"
    return "green" if val > 0 else "red"

def fmt_tl(val):
    return f"{val:+,.0f} TL"

def fmt_pct(val):
    return f"{val:+.1f}%"

# Karşılaştırma tablosu
metrikler = [
    ("Toplam İşlem",         m_s["toplam_islem"],  m_b["toplam_islem"],  "{:.0f}", False, False),
    ("Win Rate (%)",         m_s["win_rate"],       m_b["win_rate"],       "{:.1f}%", False, True),
    ("Ort. Kazanç (TL)",     m_s["ort_kazanc"],    m_b["ort_kazanc"],    "{:+,.0f}", False, True),
    ("Ort. Kayıp (TL)",      m_s["ort_kayip"],     m_b["ort_kayip"],     "{:+,.0f}", False, False),
    ("Gerçekleşen R:R",      m_s["gercek_rr"],     m_b["gercek_rr"],     "{:.2f}x", False, True),
    ("Toplam K/Z (TL)",      m_s["toplam_kaz"],    m_b["toplam_kaz"],    "{:+,.0f}", False, True),
    ("Toplam Getiri (%)",    m_s["toplam_getiri"], m_b["toplam_getiri"], "{:+.1f}%", False, True),
    ("Max Drawdown (%)",     m_s["max_dd"],        m_b["max_dd"],        "{:.1f}%", True, False),
    ("Max Ardışık Kayıp",    m_s["max_kay_seri"],  m_b["max_kay_seri"],  "{:.0f}", True, False),
    ("Beklenti Değeri (EV)", m_s["ev"],            m_b["ev"],            "{:+,.0f}", False, True),
    ("Son Sermaye (TL)",     m_s["son_deger"],     m_b["son_deger"],     "{:,.0f}", False, True),
    ("Hedefe Ulaşma (%)",   m_s["hedef_oran"],    m_b["hedef_oran"],    "{:.1f}%", False, True),
    ("Stop Yeme (%)",       m_s["stop_oran"],     m_b["stop_oran"],     "{:.1f}%", True, False),
    ("Zaman Stopu (%)",     m_s["zaman_oran"],    m_b["zaman_oran"],    "{:.1f}%", False, False),
]

# Tablo başlığı
h1, h2, h3, h4 = st.columns([2.5, 1, 1, 0.5])
h1.markdown("**Metrik**")
h2.markdown("🟡 **Sapan**")
h3.markdown("🔵 **Bull Flag**")
h4.markdown("**Fark**")
st.markdown("---")

for metrik_adi, val_s, val_b, fmt, ters, buyuk_iyi in metrikler:
    c1, c2, c3, c4 = st.columns([2.5, 1, 1, 0.5])
    c1.write(metrik_adi)

    try:
        s_str = fmt.format(val_s) if val_s is not None else "—"
        b_str = fmt.format(val_b) if val_b is not None else "—"
    except:
        s_str = str(val_s)
        b_str = str(val_b)

    # Renk mantığı
    if isinstance(val_s, (int, float)) and isinstance(val_b, (int, float)):
        if buyuk_iyi:
            s_color = "green" if val_s >= val_b else "red"
            b_color = "green" if val_b >= val_s else "red"
        elif ters:
            s_color = "green" if val_s <= val_b else "red"
            b_color = "green" if val_b <= val_s else "red"
        else:
            s_color = b_color = "normal"

        c2.markdown(f"<span style='color:{'#22c55e' if s_color=='green' else '#ef4444' if s_color=='red' else '#f1f5f9'}'>{s_str}</span>", unsafe_allow_html=True)
        c3.markdown(f"<span style='color:{'#22c55e' if b_color=='green' else '#ef4444' if b_color=='red' else '#f1f5f9'}'>{b_str}</span>", unsafe_allow_html=True)

        # Fark
        try:
            fark = val_s - val_b
            if abs(fark) > 0.01:
                fark_renk = "#22c55e" if (fark > 0) == buyuk_iyi else "#ef4444"
                c4.markdown(f"<span style='color:{fark_renk};font-size:12px'>{'+' if fark > 0 else ''}{fark:.1f}</span>", unsafe_allow_html=True)
        except:
            pass
    else:
        c2.write(s_str)
        c3.write(b_str)

# ─── EKİTİ EĞRİSİ ────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## 📈 Sermaye Eğrisi Karşılaştırması")

fig = go.Figure()

if not df_sapan_sermaye.empty:
    fig.add_trace(go.Scatter(
        x=df_sapan_sermaye.index,
        y=df_sapan_sermaye["Sermaye"],
        name="🟡 Sapan",
        line=dict(color="#f59e0b", width=2),
        fill="tozeroy",
        fillcolor="rgba(245,158,11,0.05)",
    ))

if not df_bf_sermaye.empty:
    fig.add_trace(go.Scatter(
        x=df_bf_sermaye.index,
        y=df_bf_sermaye["Sermaye"],
        name="🔵 Bull Flag",
        line=dict(color="#38bdf8", width=2),
        fill="tozeroy",
        fillcolor="rgba(56,189,248,0.05)",
    ))

# Başlangıç çizgisi
fig.add_hline(
    y=baslangic_sermaye,
    line_dash="dot", line_color="#64748b",
    annotation_text=f"Başlangıç: {baslangic_sermaye:,.0f} TL",
    annotation_position="bottom right"
)

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0d0f14",
    plot_bgcolor="#0d0f14",
    height=400,
    showlegend=True,
    hovermode="x unified",
    xaxis_rangeslider_visible=False,
    margin=dict(l=10, r=10, t=30, b=10),
    font=dict(family="Consolas", size=11),
    yaxis=dict(tickformat=",.0f", gridcolor="#1e2535"),
    xaxis=dict(gridcolor="#1e2535"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
)

st.plotly_chart(fig, use_container_width=True)

# ─── İŞLEM DETAYLARI ─────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## 📋 İşlem Detayları")

tab1, tab2 = st.tabs(["🟡 Sapan İşlemleri", "🔵 Bull Flag İşlemleri"])

def tablo_goster(df, renk_str):
    if df is None or df.empty:
        st.info("İşlem bulunamadı.")
        return

    df_goster = df.copy()
    df_goster["Tarih_Giris"] = pd.to_datetime(df_goster["Tarih_Giris"]).dt.strftime("%Y-%m-%d")
    df_goster["Tarih_Cikis"] = pd.to_datetime(df_goster["Tarih_Cikis"]).dt.strftime("%Y-%m-%d")

    st.dataframe(
        df_goster[[
            "Tarih_Giris","Tarih_Cikis","Hisse",
            "Giris","Cikis","Stop","Hedef",
            "Lot","Kar_Zarar","Neden","Sonuc"
        ]].rename(columns={
            "Tarih_Giris": "Giriş",
            "Tarih_Cikis": "Çıkış",
            "Kar_Zarar": "K/Z (TL)",
        }).style.apply(
            lambda row: [
                f"color: {'#22c55e' if row['Sonuc']=='Kazandı' else '#ef4444'}" for _ in row
            ], axis=1
        ),
        use_container_width=True,
        height=400,
    )

    csv = df_goster.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        f"⬇️ CSV İndir",
        data=csv,
        file_name=f"backtest_{renk_str}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

with tab1:
    tablo_goster(df_sapan_islem, "sapan")

with tab2:
    tablo_goster(df_bf_islem, "bullflag")

# ─── KAZANÇ DAĞILIMI ─────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("## 📊 Kazanç/Kayıp Dağılımı")

fig2 = make_subplots(rows=1, cols=2,
                     subplot_titles=("🟡 Sapan", "🔵 Bull Flag"))

for i, (df_i, renk_i, isim) in enumerate([
    (df_sapan_islem, "#f59e0b", "Sapan"),
    (df_bf_islem,    "#38bdf8", "Bull Flag")
], 1):
    if df_i is not None and not df_i.empty:
        colors = ["#22c55e" if v > 0 else "#ef4444" for v in df_i["Kar_Zarar"]]
        fig2.add_trace(go.Bar(
            x=list(range(len(df_i))),
            y=df_i["Kar_Zarar"].values,
            name=isim,
            marker_color=colors,
            opacity=0.8,
        ), row=1, col=i)
        fig2.add_hline(y=0, line_dash="dot", line_color="#64748b", row=1, col=i)

fig2.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0d0f14",
    plot_bgcolor="#0d0f14",
    height=300,
    showlegend=False,
    margin=dict(l=10, r=10, t=40, b=10),
    font=dict(family="Consolas", size=11),
)
fig2.update_yaxes(gridcolor="#1e2535", tickformat=",.0f")
fig2.update_xaxes(gridcolor="#1e2535")

st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.caption("⚠️ Bu analiz yatırım tavsiyesi değildir. Geçmiş performans gelecek sonuçları garanti etmez.")
