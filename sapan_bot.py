import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import json
import os
import requests
from datetime import datetime, timedelta
import time

# ─── AYARLAR ────────────────────────────────────────────────────────────────
TOLERANS = 0.03          # %3
ATR_CARPAN = 2.5
RR_ORANI = 1.5
MAX_POZISYON = 10
PORTFOY_BUYUKLUGU = 100_000  # TL
POZISYON_ORANI = 0.10        # %10 per trade
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = "884770362"
VERI_DOSYASI = "sapan_sanal_portfoy.json"

# ─── BIST HİSSELERİ ─────────────────────────────────────────────────────────
BIST_HISSELER = [
    "AKBNK","AKSEN","ALARK","ARCLK","ASELS","BIMAS","DOHOL","EKGYO",
    "ENKAI","EREGL","FROTO","GARAN","GUBRF","HEKTS","ISCTR","KCHOL",
    "KOZAA","KOZAL","KRDMD","LOGO","MGROS","ODAS","OTKAR","OYAKC",
    "PETKM","PGSUS","SAHOL","SASA","SISE","SOKM","TAVHL","TCELL",
    "THYAO","TKFEN","TMSN","TOASO","TSKB","TTKOM","TTRAK","TUPRS",
    "ULKER","VAKBN","VESTL","YKBNK","ZOREN","AEFES","AGHOL","AGESA",
    "AKENR","AKCNS","AKFGY","AKFYE","ALBRK","ALFAS","ALGYO","ALKIM",
    "ALTIN","ALYAG","ANACM","ANHYT","ANSGR","ARSAN","ASUZU","ATAGY",
    "ATAKP","ATATP","AYCES","AYES","BAGFS","BASGZ","BERA","BIENY",
    "BINHO","BIOEN","BIZIM","BJKAS","BMELK","BNTAS","BORLS","BOSSA",
    "BRISA","BRKSN","BRYAT","BSOKE","BTCIM","BUCIM","BURCE","BURVA",
    "CCOLA","CEMAS","CEMTS","CIMSA","CLEBI","CMENT","COSMO","CRDFA",
    "CRFSA","CUSAN","DAGHL","DAPGM","DEVA","DGATE","DGKLB","DITAS",
    "DMSAS","DNISI","DOAS","DOBUR","DOGUB","DURDO","DYOBY","DZGYO",
    "ECILC","EDIP","EGEEN","EGGUB","EGPRO","EGSER","EMKEL","EMNIS",
    "ENERY","ENJSA","EPLAS","ERSU","ESCOM","ESEN","ETILR","EUREN",
    "EYGYO","FENER","FLAP","FMIZP","FONET","FORMT","FORTE","GENTS",
    "GEREL","GESAN","GLBMD","GLCVY","GLYHO","GMTAS","GOODY","GOZDE",
    "GRSEL","GSDDE","GSDHO","GSRAY","GZNMI","HATEK","HDFGS","HURGZ",
    "ICBCT","IDEAS","IDGYO","IEYHO","IHEVA","IHGZT","IHLAS","IHLGM",
    "IMASM","INDES","INFO","INGRM","INTEM","IPEKE","ISATR","ISDMR",
    "ISFIN","ISGSY","ISGYO","ISYAT","ITTFH","JANTS","KAPLM","KAREL",
    "KARSN","KATMR","KAYSE","KERVT","KFEIN","KGYO","KIMMR","KLGYO",
    "KLKIM","KLMSN","KLNMA","KLRHO","KLSER","KNFRT","KONTR","KONYA",
    "KOPOL","KORDS","KRPLS","KRSTL","KRTEK","KTLEV","KUTPO","KUVVA",
    "LIDER","LIDFA","LKMNH","LRSHO","LUKSK","MAALT","MACKO","MAGEN",
    "MARTI","MAVI","MEDTR","MEGAP","MERIT","METUR","MIPAZ","MPARK",
    "MRGYO","MRSHL","MTRYO","MZHLD","NATEN","NETAS","NIBAS","NTHOL",
    "NTTUR","NUHCM","NUGYO","NXGYO","OBASE","OFSYM","ONCSM","ORCAY",
    "ORGE","ORMA","OSTIM","OYLUM","OYYAT","OZGYO","OZKGY","PAPIL",
    "PEHOL","PENGD","PENTA","PETUN","PKENT","PLTUR","PNLSN","POLHO",
    "PRZMA","PSDTC","PRKAB","PRKME","PSGYO","QNBFB","QNBFL","RAYSG",
    "RNPOL","RODRG","ROYAL","RTALB","RUBNS","RYSAS","SAFKR","SAMAT",
    "SANFM","SARKY","SAYAS","SDTTR","SEKFK","SEKUR","SELEC","SELVA",
    "SEYKM","SILVR","SKTAS","SMART","SNGYO","SNKRN","SODSN","SOKE",
    "SONME","SRVGY","SUNTK","SUWEN","SZGYO","TARKM","TATGD","TBORG",
    "TDGYO","TEKTU","TEZOL","TKNSA","TLMAN","TMPOL","TPVST","TRGYO",
    "TRILC","TSPOR","TUCLK","TUKAS","TULPR","TUREX","TURGG","TURSG",
    "UKIM","ULUSE","ULUUN","UNLU","USAK","USDMR","UTPYA","UYUM",
    "VANGD","VBTYZ","VERUS","VKFYO","VKGYO","VYPAS","YAPRK","YATAS",
    "YEOTK","YGYO","YKGYO","YONGA","YUNSA","YYAPI","ZEDUR","ZRGYO",
]

# ─── JSON VERİ YÖNETİMİ ─────────────────────────────────────────────────────
def veri_yukle():
    if os.path.exists(VERI_DOSYASI):
        with open(VERI_DOSYASI, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"acik_pozisyonlar": [], "kapali_islemler": [], "tarama_tarihi": ""}

def veri_kaydet(veri):
    with open(VERI_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)

# ─── TEKNİK ANALİZ ─────────────────────────────────────────────────────────
def sapan_hesapla(df):
    """
    Sapan (Slingshot) Stratejisi:
    1. Hisse en az 3 gün üst üste düşmüş olmalı (tolerans: -%3)
    2. Son kapanış, son düşüşten sonra yukarı dönmeli (tolerans: +%3)
    3. ATR stop hesabı: giriş - ATR * 2.5
    4. Hedef: giriş + (risk * 1.5)
    """
    if len(df) < 10:
        return None

    close = df["Close"].values
    high = df["High"].values
    low = df["Low"].values

    # ATR hesapla (14 günlük)
    tr_list = []
    for i in range(1, len(close)):
        tr = max(high[i] - low[i],
                 abs(high[i] - close[i-1]),
                 abs(low[i] - close[i-1]))
        tr_list.append(tr)
    atr = np.mean(tr_list[-14:]) if len(tr_list) >= 14 else np.mean(tr_list)

    # Son 5 günü incele
    son5 = close[-5:]

    # Düşüş serisi tespiti: en az 3 gün düşüş
    dusus_sayisi = 0
    dip_fiyat = None
    for i in range(len(son5) - 2, -1, -1):
        if son5[i] < son5[i-1] * (1 + TOLERANS) if i > 0 else False:
            pass
        if i > 0 and son5[i] < son5[i-1]:
            dusus_sayisi += 1
            if dip_fiyat is None:
                dip_fiyat = son5[i]
        else:
            break

    # Alternatif: son kapanıştan önceki 3+ günlük düşüş kontrolü
    # Daha sağlam yöntem:
    dusus_sayisi = 0
    for i in range(len(son5) - 2, 0, -1):
        if son5[i] <= son5[i-1] * (1 + TOLERANS / 2):
            dusus_sayisi += 1
        else:
            break

    if dusus_sayisi < 2:
        return None

    # Son gün yukarı dönüş (tolerans içinde)
    son_kapanis = close[-1]
    onceki_kapanis = close[-2]
    dip = min(close[-dusus_sayisi-2:-1])

    # Yukarı dönüş koşulu
    if son_kapanis <= onceki_kapanis * (1 - TOLERANS / 4):
        return None
    if son_kapanis <= dip * (1 + TOLERANS / 2):
        return None

    # Giriş fiyatı (bir sonraki günün açılışı - simüle: bugünün kapanışı)
    giris = son_kapanis
    stop = giris - (atr * ATR_CARPAN)
    risk = giris - stop
    hedef = giris + (risk * RR_ORANI)

    if stop <= 0 or risk <= 0:
        return None

    return {
        "giris": round(giris, 2),
        "stop": round(stop, 2),
        "hedef": round(hedef, 2),
        "atr": round(atr, 2),
        "risk_tl": round(risk, 2),
        "dusus_gun": dusus_sayisi,
    }

def hisse_tara(hisse_listesi, progress_bar=None):
    sinyaller = []
    toplam = len(hisse_listesi)
    for i, sembol in enumerate(hisse_listesi):
        try:
            ticker = sembol + ".IS"
            df = yf.download(ticker, period="30d", interval="1d",
                             auto_adjust=True, progress=False)
            if df.empty or len(df) < 10:
                continue
            if df.ndim == 2 and isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)
            sonuc = sapan_hesapla(df)
            if sonuc:
                sinyaller.append({"sembol": sembol, **sonuc,
                                  "tarih": datetime.now().strftime("%Y-%m-%d %H:%M")})
        except Exception:
            pass
        if progress_bar:
            progress_bar.progress((i + 1) / toplam)
        time.sleep(0.05)
    return sinyaller

# ─── TELEGRAM ───────────────────────────────────────────────────────────────
def telegram_gonder(mesaj):
    if not TELEGRAM_TOKEN:
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        r = requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID,
                                     "text": mesaj, "parse_mode": "HTML"})
        return r.status_code == 200
    except Exception:
        return False

def sinyal_mesaji_olustur(sinyal):
    return (
        f"🪃 <b>SAPAN SİNYALİ — {sinyal['sembol']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📈 Giriş: <b>{sinyal['giris']:.2f} ₺</b>\n"
        f"🎯 Hedef: <b>{sinyal['hedef']:.2f} ₺</b> (+{((sinyal['hedef']/sinyal['giris'])-1)*100:.1f}%)\n"
        f"🛑 Stop:  <b>{sinyal['stop']:.2f} ₺</b> (-{((1-sinyal['stop']/sinyal['giris']))*100:.1f}%)\n"
        f"📊 ATR: {sinyal['atr']:.2f} | Düşüş: {sinyal['dusus_gun']} gün\n"
        f"⚙️ Tolerans %3 | ATR×2.5 | R:R 1.5\n"
        f"🕐 {sinyal['tarih']}"
    )

# ─── PORTFÖY İŞLEMLERİ ──────────────────────────────────────────────────────
def pozisyon_ac(sinyal, veri):
    # Zaten açık mı?
    if any(p["sembol"] == sinyal["sembol"] for p in veri["acik_pozisyonlar"]):
        return False, "Zaten açık pozisyon var"
    if len(veri["acik_pozisyonlar"]) >= MAX_POZISYON:
        return False, f"Maksimum {MAX_POZISYON} pozisyon dolu"

    lot_degeri = PORTFOY_BUYUKLUGU * POZISYON_ORANI
    adet = int(lot_degeri / sinyal["giris"])
    if adet < 1:
        return False, "Yetersiz lot"

    pozisyon = {
        "sembol": sinyal["sembol"],
        "giris": sinyal["giris"],
        "stop": sinyal["stop"],
        "hedef": sinyal["hedef"],
        "adet": adet,
        "maliyet": round(adet * sinyal["giris"], 2),
        "tarih": sinyal["tarih"],
        "atr": sinyal["atr"],
    }
    veri["acik_pozisyonlar"].append(pozisyon)
    veri_kaydet(veri)
    return True, pozisyon

def pozisyon_kapat(sembol, kapanis_fiyati, veri, neden="Manuel"):
    pozisyon = next((p for p in veri["acik_pozisyonlar"] if p["sembol"] == sembol), None)
    if not pozisyon:
        return False, "Pozisyon bulunamadı"

    kar_zarar = round((kapanis_fiyati - pozisyon["giris"]) * pozisyon["adet"], 2)
    kar_yuzde = round((kapanis_fiyati / pozisyon["giris"] - 1) * 100, 2)

    kapali = {**pozisyon,
              "kapis_fiyati": kapanis_fiyati,
              "kapis_tarihi": datetime.now().strftime("%Y-%m-%d %H:%M"),
              "kar_zarar_tl": kar_zarar,
              "kar_yuzde": kar_yuzde,
              "neden": neden}

    veri["acik_pozisyonlar"] = [p for p in veri["acik_pozisyonlar"] if p["sembol"] != sembol]
    veri["kapali_islemler"].append(kapali)
    veri_kaydet(veri)
    return True, kapali

def guncel_fiyat_al(sembol):
    try:
        ticker = sembol + ".IS"
        df = yf.download(ticker, period="2d", interval="1d",
                         auto_adjust=True, progress=False)
        if df.empty:
            return None
        if df.ndim == 2 and isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
        return float(df["Close"].iloc[-1])
    except Exception:
        return None

def portfoy_degerlendirme(acik_pozisyonlar):
    rows = []
    for p in acik_pozisyonlar:
        guncel = guncel_fiyat_al(p["sembol"])
        if guncel is None:
            guncel = p["giris"]
        kz = round((guncel - p["giris"]) * p["adet"], 2)
        kz_pct = round((guncel / p["giris"] - 1) * 100, 2)
        durum = "🎯 Hedefe yakın" if guncel >= p["hedef"] * 0.95 else \
                "🛑 Stopa yakın" if guncel <= p["stop"] * 1.05 else "⏳ Aktif"
        rows.append({
            "Sembol": p["sembol"],
            "Giriş": p["giris"],
            "Güncel": guncel,
            "Stop": p["stop"],
            "Hedef": p["hedef"],
            "Adet": p["adet"],
            "K/Z (₺)": kz,
            "K/Z (%)": kz_pct,
            "Durum": durum,
            "Tarih": p["tarih"],
        })
    return pd.DataFrame(rows)

# ─── STREAMLIT ARAYÜZÜ ──────────────────────────────────────────────────────
def main():
    st.set_page_config(page_title="🪃 Sapan Bot", page_icon="🪃", layout="wide")
    st.title("🪃 Sapan (Slingshot) Strateji Botu")
    st.caption("Tolerans %3 | ATR×2.5 | R:R 1.5 | Sanal Portföy Takibi")

    veri = veri_yukle()

    # ── TAB MENÜSÜ ────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📡 Sinyal Tara", "💼 Açık Pozisyonlar", "📊 Geçmiş İşlemler", "⚙️ Ayarlar"])

    # ══════════════════════════════════════════════════════════════════════
    # TAB 1: SİNYAL TARAMA
    # ══════════════════════════════════════════════════════════════════════
    with tab1:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown("**Strateji:** Düşüş serisi (≥3 gün) → Yukarı dönüş sinyali")
        with col2:
            telegram_bildir = st.checkbox("Telegram'a gönder", value=True)
        with col3:
            hizli_mod = st.checkbox("Hızlı mod (ilk 80 hisse)", value=False)

        if st.button("🔍 Tara", type="primary", use_container_width=True):
            liste = BIST_HISSELER[:80] if hizli_mod else BIST_HISSELER
            st.info(f"{len(liste)} hisse taranıyor...")
            progress = st.progress(0)
            sinyaller = hisse_tara(liste, progress)
            progress.empty()

            veri["tarama_tarihi"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            veri_kaydet(veri)

            if not sinyaller:
                st.warning("Bugün sinyal bulunamadı.")
            else:
                st.success(f"✅ {len(sinyaller)} sinyal bulundu!")
                st.session_state["son_sinyaller"] = sinyaller

                if telegram_bildir and TELEGRAM_TOKEN:
                    for s in sinyaller:
                        telegram_gonder(sinyal_mesaji_olustur(s))
                    st.info(f"📱 {len(sinyaller)} sinyal Telegram'a gönderildi.")

        # Sinyaller tablosu
        if "son_sinyaller" in st.session_state and st.session_state["son_sinyaller"]:
            sinyaller = st.session_state["son_sinyaller"]
            df_sin = pd.DataFrame(sinyaller)
            df_sin["Kâr Pot. %"] = ((df_sin["hedef"] / df_sin["giris"] - 1) * 100).round(1)
            df_sin["Risk %"] = ((1 - df_sin["stop"] / df_sin["giris"]) * 100).round(1)

            st.markdown("### 📋 Sinyaller")
            st.dataframe(
                df_sin[["sembol","giris","stop","hedef","atr","dusus_gun","Kâr Pot. %","Risk %","tarih"]].rename(columns={
                    "sembol":"Sembol","giris":"Giriş","stop":"Stop","hedef":"Hedef",
                    "atr":"ATR","dusus_gun":"Düşüş Gün","tarih":"Tarih"
                }),
                use_container_width=True, hide_index=True
            )

            # Pozisyon aç butonu
            st.markdown("### ➕ Pozisyon Aç")
            secilen = st.selectbox("Sinyal seç", [s["sembol"] for s in sinyaller])
            sinyal_sec = next(s for s in sinyaller if s["sembol"] == secilen)

            col_g, col_s, col_h = st.columns(3)
            col_g.metric("Giriş", f"{sinyal_sec['giris']:.2f} ₺")
            col_s.metric("Stop", f"{sinyal_sec['stop']:.2f} ₺",
                         f"-{((1-sinyal_sec['stop']/sinyal_sec['giris'])*100):.1f}%")
            col_h.metric("Hedef", f"{sinyal_sec['hedef']:.2f} ₺",
                         f"+{((sinyal_sec['hedef']/sinyal_sec['giris']-1)*100):.1f}%")

            if st.button(f"✅ {secilen} Pozisyon Aç (Sanal)", use_container_width=True):
                ok, sonuc = pozisyon_ac(sinyal_sec, veri)
                if ok:
                    st.success(f"✅ {secilen} pozisyon açıldı — {sonuc['adet']} adet @ {sonuc['giris']:.2f} ₺")
                    if TELEGRAM_TOKEN:
                        telegram_gonder(
                            f"✅ <b>SANAL POZİSYON AÇILDI</b>\n"
                            f"📌 {secilen} | {sonuc['adet']} adet @ {sonuc['giris']:.2f} ₺\n"
                            f"🎯 Hedef: {sonuc['hedef']:.2f} ₺ | 🛑 Stop: {sonuc['stop']:.2f} ₺"
                        )
                    st.rerun()
                else:
                    st.error(f"❌ {sonuc}")

    # ══════════════════════════════════════════════════════════════════════
    # TAB 2: AÇIK POZİSYONLAR
    # ══════════════════════════════════════════════════════════════════════
    with tab2:
        if not veri["acik_pozisyonlar"]:
            st.info("Henüz açık pozisyon yok.")
        else:
            # Özet metrikler
            st.markdown("### 📊 Portföy Özeti")
            df_portfoy = portfoy_degerlendirme(veri["acik_pozisyonlar"])
            toplam_kz = df_portfoy["K/Z (₺)"].sum()
            toplam_maliyet = sum(p["maliyet"] for p in veri["acik_pozisyonlar"])

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Açık Pozisyon", len(veri["acik_pozisyonlar"]))
            col2.metric("Toplam Maliyet", f"{toplam_maliyet:,.0f} ₺")
            col3.metric("Toplam K/Z", f"{toplam_kz:+,.0f} ₺",
                        delta_color="normal" if toplam_kz >= 0 else "inverse")
            col4.metric("Portföy Getiri", f"{(toplam_kz/toplam_maliyet*100):+.1f}%" if toplam_maliyet > 0 else "—")

            # Pozisyon tablosu
            st.markdown("### 📋 Pozisyonlar")
            st.dataframe(df_portfoy, use_container_width=True, hide_index=True)

            # Pozisyon kapat
            st.markdown("### ❌ Pozisyon Kapat")
            col_a, col_b, col_c = st.columns([2, 1, 1])
            with col_a:
                kapat_sembol = st.selectbox(
                    "Hisse", [p["sembol"] for p in veri["acik_pozisyonlar"]])
            with col_b:
                neden = st.selectbox("Neden", ["Hedef Geldi", "Stop Tetiklendi", "Manuel"])
            with col_c:
                p = next((x for x in veri["acik_pozisyonlar"] if x["sembol"] == kapat_sembol), None)
                guncel_f = guncel_fiyat_al(kapat_sembol) if p else None
                kapat_fiyat = st.number_input(
                    "Kapanış Fiyatı",
                    value=float(guncel_f or (p["giris"] if p else 0)),
                    min_value=0.01, step=0.01)

            if st.button(f"❌ {kapat_sembol} Kapat", use_container_width=True):
                ok, sonuc = pozisyon_kapat(kapat_sembol, kapat_fiyat, veri, neden)
                if ok:
                    kz = sonuc["kar_zarar_tl"]
                    st.success(f"{'✅' if kz >= 0 else '🔴'} {kapat_sembol} kapatıldı | K/Z: {kz:+,.2f} ₺ ({sonuc['kar_yuzde']:+.1f}%)")
                    if TELEGRAM_TOKEN:
                        telegram_gonder(
                            f"{'✅' if kz >= 0 else '🔴'} <b>POZİSYON KAPANDI — {kapat_sembol}</b>\n"
                            f"Neden: {neden}\n"
                            f"Giriş: {sonuc['giris']:.2f} ₺ → Çıkış: {kapat_fiyat:.2f} ₺\n"
                            f"K/Z: <b>{kz:+,.2f} ₺ ({sonuc['kar_yuzde']:+.1f}%)</b>"
                        )
                    st.rerun()
                else:
                    st.error(sonuc)

            # Tüm pozisyonları güncelle
            if st.button("🔄 Fiyatları Güncelle", use_container_width=True):
                st.rerun()

    # ══════════════════════════════════════════════════════════════════════
    # TAB 3: GEÇMİŞ İŞLEMLER
    # ══════════════════════════════════════════════════════════════════════
    with tab3:
        if not veri["kapali_islemler"]:
            st.info("Henüz kapatılmış işlem yok.")
        else:
            df_kapali = pd.DataFrame(veri["kapali_islemler"])

            # İstatistikler
            kazananlar = df_kapali[df_kapali["kar_zarar_tl"] > 0]
            kaybedenler = df_kapali[df_kapali["kar_zarar_tl"] <= 0]
            toplam_kz = df_kapali["kar_zarar_tl"].sum()
            win_rate = len(kazananlar) / len(df_kapali) * 100 if len(df_kapali) > 0 else 0

            st.markdown("### 📊 Performans Özeti")
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Toplam İşlem", len(df_kapali))
            col2.metric("Kazanan", len(kazananlar))
            col3.metric("Kaybeden", len(kaybedenler))
            col4.metric("Win Rate", f"{win_rate:.1f}%")
            col5.metric("Net K/Z", f"{toplam_kz:+,.0f} ₺")

            if len(kazananlar) > 0 and len(kaybedenler) > 0:
                ort_kazanc = kazananlar["kar_zarar_tl"].mean()
                ort_kayip = abs(kaybedenler["kar_zarar_tl"].mean())
                col1b, col2b, col3b = st.columns(3)
                col1b.metric("Ort. Kazanç", f"{ort_kazanc:+,.0f} ₺")
                col2b.metric("Ort. Kayıp", f"-{ort_kayip:,.0f} ₺")
                col3b.metric("Beklenti (Expectancy)", f"{(win_rate/100*ort_kazanc - (1-win_rate/100)*ort_kayip):+,.0f} ₺")

            st.markdown("### 📋 İşlem Geçmişi")
            goster_cols = ["sembol","giris","kapis_fiyati","adet","kar_zarar_tl","kar_yuzde","neden","kapis_tarihi"]
            mevcut = [c for c in goster_cols if c in df_kapali.columns]
            st.dataframe(
                df_kapali[mevcut].rename(columns={
                    "sembol":"Sembol","giris":"Giriş","kapis_fiyati":"Çıkış",
                    "adet":"Adet","kar_zarar_tl":"K/Z (₺)","kar_yuzde":"K/Z (%)",
                    "neden":"Neden","kapis_tarihi":"Kapanış Tarihi"
                }).sort_values("Kapanış Tarihi", ascending=False),
                use_container_width=True, hide_index=True
            )

            # Veriyi sıfırla
            if st.button("🗑️ Tüm Geçmişi Temizle", type="secondary"):
                if st.session_state.get("temizle_onay"):
                    veri["kapali_islemler"] = []
                    veri_kaydet(veri)
                    st.session_state["temizle_onay"] = False
                    st.rerun()
                else:
                    st.session_state["temizle_onay"] = True
                    st.warning("Emin misin? Tekrar bas.")

    # ══════════════════════════════════════════════════════════════════════
    # TAB 4: AYARLAR
    # ══════════════════════════════════════════════════════════════════════
    with tab4:
        st.markdown("### ⚙️ Strateji Parametreleri")
        st.info("Mevcut en iyi kombinasyon: **Tolerans %3 | ATR×2.5 | R:R 1.5** → 2022-2026 backtestinde +1297% getiri, %59.6 win rate")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Tolerans", "%3")
        with col2:
            st.metric("ATR Çarpanı", "2.5")
        with col3:
            st.metric("R:R Oranı", "1.5")

        st.markdown("### 📱 Telegram Ayarları")
        st.code(f"Chat ID: {TELEGRAM_CHAT_ID}")
        if TELEGRAM_TOKEN:
            st.success("✅ Telegram Token tanımlı (environment variable)")
        else:
            st.warning("⚠️ TELEGRAM_TOKEN environment variable tanımlı değil. Streamlit secrets'a ekle.")
            st.code('TELEGRAM_TOKEN = "your_token_here"  # .streamlit/secrets.toml')

        st.markdown("### 💼 Portföy Ayarları")
        col1, col2 = st.columns(2)
        col1.metric("Portföy Büyüklüğü", f"{PORTFOY_BUYUKLUGU:,} ₺")
        col2.metric("Pozisyon Başına", f"%{POZISYON_ORANI*100:.0f} ({PORTFOY_BUYUKLUGU*POZISYON_ORANI:,.0f} ₺)")

        st.markdown("### 📁 Veri Dosyası")
        st.code(f"Konum: {os.path.abspath(VERI_DOSYASI)}")
        if veri["tarama_tarihi"]:
            st.caption(f"Son tarama: {veri['tarama_tarihi']}")

        if st.button("📥 JSON Veriyi İndir"):
            st.download_button(
                "⬇️ sapan_sanal_portfoy.json",
                data=json.dumps(veri, ensure_ascii=False, indent=2),
                file_name="sapan_sanal_portfoy.json",
                mime="application/json"
            )

if __name__ == "__main__":
    main()
