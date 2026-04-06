import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, date
import json
import os
import plotly.graph_objects as go

st.set_page_config(
    page_title="Sapan İşlem Defteri",
    page_icon="📒",
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
    .metric-value { font-size: 22px; font-weight: 700; }
    .metric-pos { color: #22c55e; }
    .metric-neg { color: #ef4444; }
    .metric-neu { color: #94a3b8; }
    .metric-warn { color: #f59e0b; }
    .poz-kart {
        background: #1a2235;
        border: 1px solid #2d3548;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 10px;
    }
    .poz-kart-warn { border-color: #f59e0b44; }
    .poz-kart-danger { border-color: #ef444444; }
</style>
""", unsafe_allow_html=True)

# ─── VERİ DOSYASI ─────────────────────────────────────────────────────────────
VERI_DOSYASI = "sapan_islem_defteri.csv"
SUTUNLAR = [
    "id", "acilis_tarihi", "hisse", "formasyon", "giris", "stop", "hedef",
    "lot", "giris_tl", "risk_tl", "stoch", "macd", "not_",
    "kapanis_tarihi", "cikis_fiyati", "sonuc", "kaz_tl", "gun_sayisi"
]

def veri_yukle():
    if "df" not in st.session_state:
        if os.path.exists(VERI_DOSYASI):
            try:
                st.session_state["df"] = pd.read_csv(VERI_DOSYASI)
            except Exception:
                st.session_state["df"] = pd.DataFrame(columns=SUTUNLAR)
        else:
            st.session_state["df"] = pd.DataFrame(columns=SUTUNLAR)
    return st.session_state["df"]

def veri_kaydet(df):
    st.session_state["df"] = df
    try:
        df.to_csv(VERI_DOSYASI, index=False, encoding="utf-8-sig")
    except Exception:
        pass  # Cloud'da yazma hatası olabilir, sessizce geç

def yeni_id(df):
    if len(df) == 0:
        return 1
    return int(df["id"].max()) + 1

def guncel_fiyat_cek(hisse):
    try:
        ticker = yf.Ticker(hisse + ".IS")
        bilgi  = ticker.fast_info
        return round(float(bilgi.last_price), 2)
    except Exception:
        return None

def gun_hesapla(acilis_tarihi_str):
    try:
        acilis = datetime.strptime(acilis_tarihi_str, "%d.%m.%Y")
        return (datetime.now() - acilis).days
    except Exception:
        return 0

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
st.sidebar.title("📒 Sapan İşlem Defteri")
st.sidebar.markdown("---")

# CSV yükleme
yuklenen = st.sidebar.file_uploader("📂 CSV Yükle (yedekten geri yükle)", type="csv")
if yuklenen is not None:
    try:
        df_yukle = pd.read_csv(yuklenen)
        st.session_state["df"] = df_yukle
        veri_kaydet(df_yukle)
        st.sidebar.success("✅ Veri yüklendi!")
    except Exception as e:
        st.sidebar.error(f"Hata: {e}")

st.sidebar.markdown("### ⚙️ Strateji Parametreleri")
zaman_stopu = st.sidebar.slider("Zaman Stopu (gün)", 10, 40, 30, 1)
risk_yuzdesi = st.sidebar.slider("Risk % (1R)", 0.5, 5.0, 1.0, 0.5)
portfoy = st.sidebar.number_input("Portföy (TL)", min_value=10000,
                                   max_value=10_000_000, value=950_000, step=10000)

# ─── ANA SAYFA ────────────────────────────────────────────────────────────────
st.title("📒 Sapan Stratejisi — İşlem Defteri")

df = veri_yukle()

# ─── SEKME ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Açık Pozisyonlar",
    "➕ Yeni İşlem",
    "📊 Kapalı İşlemler",
    "📈 İstatistikler"
])

# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### Açık Pozisyonlar")

    acik = df[df["kapanis_tarihi"].isna() | (df["kapanis_tarihi"] == "")]

    if len(acik) == 0:
        st.info("Henüz açık pozisyon yok.")
    else:
        # Fiyat güncelle butonu
        if st.button("🔄 Fiyatları Güncelle", use_container_width=False):
            with st.spinner("Fiyatlar çekiliyor..."):
                for idx in acik.index:
                    hisse = df.loc[idx, "hisse"]
                    fiyat = guncel_fiyat_cek(hisse)
                    if fiyat:
                        df.loc[idx, "_guncel_fiyat"] = fiyat
                veri_kaydet(df)
            st.rerun()

        for idx in acik.index:
            row = df.loc[idx]
            gun = gun_hesapla(str(row["acilis_tarihi"]))
            guncel = row.get("_guncel_fiyat", None)
            if pd.isna(guncel) if guncel is not None else True:
                guncel = None
            else:
                guncel = float(guncel)

            giris  = float(row["giris"])
            stop   = float(row["stop"])
            hedef  = float(row["hedef"])
            lot    = int(row["lot"])

            # Kart rengi
            kart_class = "poz-kart"
            if gun >= zaman_stopu:
                kart_class += " poz-kart-danger"
            elif gun >= zaman_stopu * 0.7:
                kart_class += " poz-kart-warn"

            # K/Z hesabı
            if guncel:
                kz_tl   = round((guncel - giris) * lot, 0)
                kz_pct  = round((guncel - giris) / giris * 100, 1)
                stop_uzaklik  = round((guncel - stop) / giris * 100, 1)
                hedef_uzaklik = round((hedef - guncel) / giris * 100, 1)
                kz_renk = "metric-pos" if kz_tl >= 0 else "metric-neg"
            else:
                kz_tl = kz_pct = None
                stop_uzaklik = hedef_uzaklik = None
                kz_renk = "metric-neu"

            with st.container():
                c1, c2, c3, c4, c5, c6 = st.columns([2,1.5,1.5,1.5,1.5,2])

                # Hisse adı ve gün
                gun_renk = "#ef4444" if gun >= zaman_stopu else "#f59e0b" if gun >= zaman_stopu*0.7 else "#94a3b8"
                c1.markdown(f"""
                <div style="padding:6px 0">
                    <div style="font-size:18px;font-weight:700;color:#f1f5f9">{row['hisse']}</div>
                    <div style="font-size:11px;color:#8b95a8">{row['formasyon']} | {row['acilis_tarihi']}</div>
                    <div style="font-size:12px;color:{gun_renk};font-weight:600">{gun} / {zaman_stopu} gün</div>
                </div>""", unsafe_allow_html=True)

                guncel_str = f"{guncel:.2f}" if guncel else "—"
                guncel_renk = "metric-pos" if guncel and guncel > giris else "metric-neg" if guncel else "metric-neu"

                c2.markdown(f"""<div class="metric-card">
                    <div class="metric-label">Giriş</div>
                    <div class="metric-value metric-neu">{giris:.2f}</div>
                </div>""", unsafe_allow_html=True)

                c3.markdown(f"""<div class="metric-card">
                    <div class="metric-label">Güncel</div>
                    <div class="metric-value {guncel_renk}">{guncel_str}</div>
                </div>""", unsafe_allow_html=True)

                c4.markdown(f"""<div class="metric-card">
                    <div class="metric-label">Stop</div>
                    <div class="metric-value metric-neg">{stop:.2f}</div>
                </div>""", unsafe_allow_html=True)

                c5.markdown(f"""<div class="metric-card">
                    <div class="metric-label">Hedef</div>
                    <div class="metric-value metric-pos">{hedef:.2f}</div>
                </div>""", unsafe_allow_html=True)

                kz_str = f"{kz_tl:+,.0f} TL ({kz_pct:+.1f}%)" if kz_tl is not None else "—"
                c6.markdown(f"""<div class="metric-card">
                    <div class="metric-label">K/Z</div>
                    <div class="metric-value {kz_renk}" style="font-size:16px">{kz_str}</div>
                </div>""", unsafe_allow_html=True)

                # Zaman stopu uyarısı
                if gun >= zaman_stopu:
                    st.warning(f"⏱️ **{row['hisse']}** — {zaman_stopu} gün doldu! Pozisyonu kapat.")

                # İlerleme çubukları
                if guncel:
                    toplam = hedef - stop
                    ilerleme = (guncel - stop) / toplam if toplam > 0 else 0
                    ilerleme = max(0, min(1, ilerleme))
                    st.progress(ilerleme, text=f"Stop {stop:.2f} ◀ {guncel:.2f} ▶ Hedef {hedef:.2f} | Lot: {lot}")

                # Kapat butonu
                with st.expander(f"🔒 {row['hisse']} Pozisyonu Kapat"):
                    col_a, col_b, col_c = st.columns(3)
                    cikis_f = col_a.number_input("Çıkış Fiyatı", value=float(guncel or giris),
                                                   key=f"cikis_{idx}", step=0.01)
                    sonuc_sec = col_b.selectbox("Sonuç", ["✅ Hedef", "❌ Stop", "⏱️ Zaman", "📤 Manuel"],
                                                 key=f"sonuc_{idx}")
                    if col_c.button("Kapat", key=f"btn_{idx}", type="primary"):
                        kaz = round((cikis_f - giris) * lot, 0)
                        df.loc[idx, "kapanis_tarihi"] = datetime.now().strftime("%d.%m.%Y")
                        df.loc[idx, "cikis_fiyati"]  = cikis_f
                        df.loc[idx, "sonuc"]          = sonuc_sec
                        df.loc[idx, "kaz_tl"]         = kaz
                        df.loc[idx, "gun_sayisi"]     = gun
                        veri_kaydet(df)
                        st.success(f"✅ {row['hisse']} kapatıldı! K/Z: {kaz:+,.0f} TL")
                        st.rerun()

                st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### ➕ Yeni İşlem Gir")

    with st.form("yeni_islem", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        hisse      = c1.text_input("Hisse Kodu", placeholder="THYAO").upper().strip()
        acilis_t   = c2.date_input("Giriş Tarihi", value=date.today())
        formasyon  = c3.selectbox("Formasyon", ["Orjinal 2 Mum","Gövde Deliş","İç Dönüş","Pin Bar","Diğer"])

        c4, c5, c6, c7 = st.columns(4)
        giris_f = c4.number_input("Giriş Fiyatı (TL)", min_value=0.01, step=0.01)
        stop_f  = c5.number_input("Stop Fiyatı (TL)",  min_value=0.01, step=0.01)
        hedef_f = c6.number_input("Hedef Fiyatı (TL)", min_value=0.01, step=0.01)
        lot_f   = c7.number_input("Lot (adet)", min_value=1, step=1)

        c8, c9, c10 = st.columns(3)
        stoch_f = c8.number_input("Stochastic", min_value=0.0, max_value=100.0, step=0.1)
        macd_f  = c9.number_input("MACD", step=0.0001, format="%.4f")
        not_f   = c10.text_input("Not (isteğe bağlı)", placeholder="Neden girdim?")

        # Otomatik hesaplar
        if giris_f > 0 and stop_f > 0:
            risk_h   = giris_f - stop_f
            giris_tl = round(giris_f * lot_f, 0) if lot_f > 0 else 0
            risk_tl  = round(risk_h * lot_f, 0) if lot_f > 0 else 0
            rr       = round((hedef_f - giris_f) / risk_h, 2) if risk_h > 0 and hedef_f > 0 else 0
            st.info(f"Giriş Tutarı: **{giris_tl:,.0f} TL** | Risk (1R): **{risk_tl:,.0f} TL** | R:R: **1:{rr}**")
        else:
            giris_tl = risk_tl = 0

        gonder = st.form_submit_button("✅ İşlemi Kaydet", use_container_width=True, type="primary")

        if gonder:
            if not hisse:
                st.error("Hisse kodu boş olamaz!")
            elif giris_f <= 0 or stop_f <= 0 or hedef_f <= 0:
                st.error("Fiyat alanları doldurulmalı!")
            elif stop_f >= giris_f:
                st.error("Stop fiyatı giriş fiyatından küçük olmalı!")
            elif hedef_f <= giris_f:
                st.error("Hedef fiyatı giriş fiyatından büyük olmalı!")
            else:
                yeni = {
                    "id"            : yeni_id(df),
                    "acilis_tarihi" : acilis_t.strftime("%d.%m.%Y"),
                    "hisse"         : hisse,
                    "formasyon"     : formasyon,
                    "giris"         : giris_f,
                    "stop"          : stop_f,
                    "hedef"         : hedef_f,
                    "lot"           : lot_f,
                    "giris_tl"      : giris_tl,
                    "risk_tl"       : risk_tl,
                    "stoch"         : stoch_f,
                    "macd"          : macd_f,
                    "not_"          : not_f,
                    "kapanis_tarihi": "",
                    "cikis_fiyati"  : "",
                    "sonuc"         : "",
                    "kaz_tl"        : "",
                    "gun_sayisi"    : "",
                }
                df = pd.concat([df, pd.DataFrame([yeni])], ignore_index=True)
                veri_kaydet(df)
                st.success(f"✅ {hisse} işlemi kaydedildi!")
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 📊 Kapalı İşlemler")

    kapali = df[df["kapanis_tarihi"].notna() & (df["kapanis_tarihi"] != "")].copy()

    if len(kapali) == 0:
        st.info("Henüz kapatılmış işlem yok.")
    else:
        kapali["kaz_tl"] = pd.to_numeric(kapali["kaz_tl"], errors="coerce").fillna(0)

        # Filtreler
        col_f1, col_f2 = st.columns(2)
        sonuc_filtre = col_f1.multiselect("Sonuç Filtrele",
            ["✅ Hedef","❌ Stop","⏱️ Zaman","📤 Manuel"],
            default=["✅ Hedef","❌ Stop","⏱️ Zaman","📤 Manuel"])
        hisse_filtre = col_f2.text_input("Hisse Ara", placeholder="THYAO")

        if sonuc_filtre:
            kapali = kapali[kapali["sonuc"].isin(sonuc_filtre)]
        if hisse_filtre:
            kapali = kapali[kapali["hisse"].str.contains(hisse_filtre.upper())]

        # Tablo
        goster = kapali[["acilis_tarihi","kapanis_tarihi","gun_sayisi","hisse",
                          "formasyon","lot","giris","cikis_fiyati","stop","hedef",
                          "sonuc","kaz_tl"]].copy()
        goster["kaz_tl"] = goster["kaz_tl"].apply(lambda x: f"{float(x):+,.0f} TL" if x != "" else "")
        st.dataframe(goster, use_container_width=True, hide_index=True)

        # CSV indir
        csv = kapali.to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇️ CSV İndir", data=csv,
            file_name=f"sapan_islemler_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv")

# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### 📈 İstatistikler")

    kapali_stat = df[df["kapanis_tarihi"].notna() & (df["kapanis_tarihi"] != "")].copy()
    kapali_stat["kaz_tl"] = pd.to_numeric(kapali_stat["kaz_tl"], errors="coerce").fillna(0)
    acik_stat   = df[df["kapanis_tarihi"].isna() | (df["kapanis_tarihi"] == "")]

    tamam    = kapali_stat[kapali_stat["sonuc"].isin(["✅ Hedef","❌ Stop","⏱️ Zaman","📤 Manuel"])]
    kazanan  = kapali_stat[kapali_stat["sonuc"] == "✅ Hedef"]
    kaybeden = kapali_stat[kapali_stat["sonuc"] == "❌ Stop"]
    toplam   = len(tamam)
    wr       = len(kazanan) / toplam * 100 if toplam > 0 else 0
    toplam_kz = kapali_stat["kaz_tl"].sum()
    ort_kaz  = kazanan["kaz_tl"].mean() if len(kazanan) > 0 else 0
    ort_kay  = kaybeden["kaz_tl"].mean() if len(kaybeden) > 0 else 0

    # Metrik kartları
    c1,c2,c3,c4 = st.columns(4)
    for col, lbl, val, renk in [
        (c1, "Toplam İşlem",   str(toplam),              "metric-neu"),
        (c2, "Win Rate",       f"{wr:.1f}%",              "metric-pos" if wr>=50 else "metric-warn"),
        (c3, "Toplam K/Z",     f"{toplam_kz:+,.0f} TL",  "metric-pos" if toplam_kz>=0 else "metric-neg"),
        (c4, "Açık Pozisyon",  str(len(acik_stat)),      "metric-neu"),
    ]:
        col.markdown(f"""<div class="metric-card">
            <div class="metric-label">{lbl}</div>
            <div class="metric-value {renk}">{val}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")

    c5,c6,c7,c8 = st.columns(4)
    for col, lbl, val, renk in [
        (c5, "Kazanan (✅)",    str(len(kazanan)),         "metric-pos"),
        (c6, "Kaybeden (❌)",   str(len(kaybeden)),        "metric-neg"),
        (c7, "Ort. Kazanç",    f"{ort_kaz:+,.0f} TL",    "metric-pos"),
        (c8, "Ort. Kayıp",     f"{ort_kay:+,.0f} TL",    "metric-neg"),
    ]:
        col.markdown(f"""<div class="metric-card">
            <div class="metric-label">{lbl}</div>
            <div class="metric-value {renk}">{val}</div>
        </div>""", unsafe_allow_html=True)

    if len(tamam) > 0:
        st.markdown("---")

        # Aylık K/Z grafiği
        kapali_stat["kapanis_dt"] = pd.to_datetime(
            kapali_stat["kapanis_tarihi"], format="%d.%m.%Y", errors="coerce")
        kapali_stat["Ay"] = kapali_stat["kapanis_dt"].dt.to_period("M")
        aylik = kapali_stat.groupby("Ay")["kaz_tl"].sum().reset_index()
        aylik["Kümülatif"] = portfoy + aylik["kaz_tl"].cumsum()

        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.markdown("**Aylık K/Z**")
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=aylik["Ay"].astype(str), y=aylik["kaz_tl"],
                marker_color=[("#3fb950" if v>=0 else "#ef4444") for v in aylik["kaz_tl"]],
                text=[f"{v:+,.0f}" for v in aylik["kaz_tl"]],
                textposition="outside"
            ))
            fig.update_layout(template="plotly_dark", paper_bgcolor="#0d0f14",
                plot_bgcolor="#0d0f14", height=280,
                margin=dict(l=10,r=10,t=10,b=10),
                yaxis=dict(gridcolor="#1e293b"), xaxis=dict(gridcolor="#1e293b"),
                showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with col_g2:
            st.markdown("**Kümülatif Portföy**")
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=aylik["Ay"].astype(str), y=aylik["Kümülatif"],
                fill="tozeroy", line=dict(color="#38bdf8", width=2),
                fillcolor="rgba(56,189,248,0.08)"
            ))
            fig2.add_hline(y=portfoy, line_dash="dash", line_color="#64748b",
                           annotation_text=f"Başlangıç: {portfoy:,.0f}")
            fig2.update_layout(template="plotly_dark", paper_bgcolor="#0d0f14",
                plot_bgcolor="#0d0f14", height=280,
                margin=dict(l=10,r=10,t=10,b=10),
                yaxis=dict(gridcolor="#1e293b", tickformat=",.0f"),
                xaxis=dict(gridcolor="#1e293b"), showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)

        # Formasyon dağılımı
        st.markdown("**Formasyona Göre Performans**")
        form_stat = kapali_stat.groupby("formasyon").agg(
            Islem=("kaz_tl","count"),
            ToplamKZ=("kaz_tl","sum"),
            OrtKZ=("kaz_tl","mean")
        ).reset_index()
        form_stat["ToplamKZ"] = form_stat["ToplamKZ"].apply(lambda x: f"{x:+,.0f} TL")
        form_stat["OrtKZ"]    = form_stat["OrtKZ"].apply(lambda x: f"{x:+,.0f} TL")
        st.dataframe(form_stat, use_container_width=True, hide_index=True)

    # Tüm veriyi CSV indir
    st.markdown("---")
    csv_tum = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ Tüm Veriyi İndir (Yedek)", data=csv_tum,
        file_name=f"sapan_defteri_yedek_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv")

st.markdown("---")
st.caption("⚠️ Bu uygulama yatırım tavsiyesi vermez. Veriler lokal olarak saklanır.")
