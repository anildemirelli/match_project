import random

import pandas as pd
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, Player
import os

app = Flask(__name__)

# ✅ Güvenli config yükleme
config_path = os.path.join(os.path.dirname(__file__), 'config.py')
app.config.from_pyfile(config_path)

app.secret_key = 'halisaha_secret'

db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    ad_soyad = request.form.get('ad_soyad')
    email = request.form.get('email')
    password = request.form.get('password')

    existing_user = Player.query.filter_by(username=username).first()
    if existing_user:
        flash("❌ Bu kullanıcı adı zaten kayıtlı.")
        return redirect(url_for('index'))

    new_player = Player(
        username=username,
        ad_soyad=ad_soyad,
        email=email,
        password=password,
        type='oyuncu',
        sabit_mevki=None
    )

    db.session.add(new_player)
    db.session.commit()

    flash("✅ Kayıt başarılı!")
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = Player.query.filter_by(username=username).first()

        if user and user.password == password:
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_type'] = user.type

            flash(f"✅ Hoş geldin, {user.ad_soyad}!")

            if user.type == 'admin':
                return redirect(url_for('admin_panel'))
            else:
                return redirect(url_for('index'))

        else:
            flash("❌ Hatalı kullanıcı adı veya şifre")

    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return f"Merhaba {session['username']}! Burası oyuncu paneli."

@app.route('/admin')
def admin_panel():
    if session.get('user_type') != 'admin':
        return redirect(url_for('index'))
    return render_template("admin_panel.html")

@app.route("/oyuncu-guncelle", methods=["POST"])
def oyuncu_guncelle():
    data = request.get_json()
    player_id = data.get("id")

    player = Player.query.get(player_id)
    if not player:
        return jsonify({"error": "Oyuncu bulunamadı"}), 404

    player.ad_soyad = data.get("ad_soyad", player.ad_soyad)
    player.mevki1 = data.get("mevki1", player.mevki1)
    player.mevki2 = data.get("mevki2", player.mevki2)
    player.mevki3 = data.get("mevki3", player.mevki3)
    player.defance = int(data.get("defance", player.defance) or 0)
    player.attack = int(data.get("attack", player.attack) or 0)
    player.overall = int(data.get("overall", player.overall) or 0)
    player.type = data.get("type", player.type)
    player.sabit_mevki = data.get("sabit_mevki", player.sabit_mevki)
    player.tercih_side = data.get("tercih_side", player.tercih_side)

    try:
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/oyuncu-duzenle")
def oyuncu_duzenle():
    oyuncular = Player.query.all()
    return render_template("oyuncu_duzenle.html", oyuncular=oyuncular)

@app.route("/oyuncu-ekle", methods=["POST"])
def oyuncu_ekle():
    data = request.get_json()

    # Eksik alanlar varsa rastgele üret
    def get_value(k, default):
        return data.get(k) if data.get(k) not in [None, '', 'None'] else default

    new_player = Player(
        ad_soyad = get_value("ad_soyad", "Bilinmeyen"),
        mevki1 = get_value("mevki1", "ortasaha"),
        mevki2 = get_value("mevki2", "defans"),
        mevki3 = get_value("mevki3", "forvet"),
        defance = int(get_value("defance", random.randint(60, 90))),
        attack = int(get_value("attack", random.randint(60, 90))),
        overall = int(get_value("overall", random.randint(70, 95))),
        type = get_value("type", "oyuncu"),
        sabit_mevki = get_value("sabit_mevki", None),
        tercih_side = get_value("tercih_side", None),
        username = get_value("ad_soyad", "user") + str(random.randint(1000, 9999)),
        email = get_value("ad_soyad", "user").replace(" ", "").lower() + "@mail.com",
        password = "1234"  # Varsayılan parola, istenirse kullanıcıya gösterilebilir
    )

    try:
        db.session.add(new_player)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/create-match', methods=['GET', 'POST'])
def create_match():
    if 'user_id' not in session or session.get('user_type') != 'admin':
        flash("Bu sayfaya erişim yetkiniz yok.")
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Buraya maç kaydetme işlemi gelecek
        flash("✅ Maç kaydedildi (henüz işlev yok).")
        return redirect(url_for('create_match'))

    oyuncular = Player.query.filter_by(type='oyuncu').all()
    return render_template('match_create.html', oyuncular=oyuncular)

@app.route('/takim-olustur', methods=['POST'])
def takim_olustur():
    # 1. Gelen ID'leri al
    gelen_idler = request.json.get("ids", [])  # örnek: [5, 12, 18, ...]
    if not gelen_idler:
        return jsonify({"error": "ID listesi boş"}), 400

    # 2. Veritabanına bağlan
    conn = psycopg2.connect(
        user='postgres',
        password='jAcABlJPfhbptKOkSKUvVClMhddYOtEF',
        host='trolley.proxy.rlwy.net',
        port='39956',
        database='railway'
    )
    cur = conn.cursor()

    # 3. Sadece gelen ID'lere göre veri çek
    format_strings = ','.join(['%s'] * len(gelen_idler))
    cur.execute(f"""
        SELECT ad_soyad, mevki1, mevki2, mevki3, defance, attack, overall, sabit_mevki, tercih_side
        FROM player_database
        WHERE id IN ({format_strings})
    """, gelen_idler)
    rows = cur.fetchall()
    conn.close()

    # Kolonları tanımla ve normalize et
    columns = ['ad_soyad', 'mevki1', 'mevki2', 'mevki3', 'defance', 'attack', 'overall', 'sabit_mevki', 'tercih_side']
    veriler_df = pd.DataFrame(rows, columns=columns)
    veriler_df['mevki1'] = veriler_df['mevki1'].fillna("").str.strip().str.lower()
    veriler_df['mevki2'] = veriler_df['mevki2'].fillna("").str.strip().str.lower()
    veriler_df['mevki3'] = veriler_df['mevki3'].fillna("").str.strip().str.lower()
    veriler = veriler_df.to_dict('records')
    print("💡 Mevcut oyuncu mevki1 dağılımı:")
    from collections import Counter
    print(Counter([v.get("mevki1") for v in veriler]))
    # Hedef kadro ihtiyacı
    hedef = {'kaleci': 2, 'defans': 6, 'ortasaha': 8, 'forvet': 2}
    final_kadro = []
    ihtiyac = {}

    # 1. Aşama: mevki1'e göre uygun olanları yerleştir
    for poz, gereken in hedef.items():
        adaylar = [v for v in veriler if v['mevki1'] == poz]

        if len(adaylar) == gereken:
            final_kadro.extend(adaylar)
            veriler = [v for v in veriler if v['ad_soyad'] not in [a['ad_soyad'] for a in adaylar]]

        elif len(adaylar) < gereken:
            final_kadro.extend(adaylar)
            veriler = [v for v in veriler if v['ad_soyad'] not in [a['ad_soyad'] for a in adaylar]]
            ihtiyac[poz] = gereken - len(adaylar)

        elif len(adaylar) > gereken:
            # Fazla varsa hiç dokunma, ne eksik listesine yaz ne final kadroya al
            print(f"⚠️ {poz} pozisyonunda fazla oyuncu var, havuzda tutuluyor.")
            continue

    # 2. Aşama: eksikleri mevki2'den tamamla
    veriler = sorted(veriler, key=lambda x: x['overall'])
    print(f"\n🟨 Mevki1 sonrası kalan oyuncular ({len(veriler)} kişi):")
    # 🧪 Kaleci aramasında mevki2 kontrolü
    print("🧪 mevki2 == kaleci olan oyuncular:",
          [v['ad_soyad'] for v in veriler if str(v.get('mevki2', '')).strip().lower() == "kaleci"])

    for poz, eksik in list(ihtiyac.items()):
        print(f"\n🔍 [2. Aşama] '{poz}' pozisyonu için eksik: {eksik}")
        adaylar = []

        for v in veriler:
            print(f"  ⏳ İncelenen: {v['ad_soyad']}, mevki2: {repr(v.get('mevki2'))}")
            if str(v.get('mevki2', '')).strip().lower() == poz:
                print(f"    ✅ Aday olarak uygun: {v['ad_soyad']}")
                adaylar.append(v)

        adaylar = sorted(adaylar, key=lambda x: x['overall'])
        yeni_eklenenler = []

        for v in adaylar:
            if eksik == 0:
                break
            print(f"    ➕ {v['ad_soyad']} kadroya alındı (mevki2)")
            v['mevki1'] = poz  # pozisyonunu güncelle
            final_kadro.append(v)
            yeni_eklenenler.append(v)
            eksik -= 1

        veriler = [v for v in veriler if v['ad_soyad'] not in [p['ad_soyad'] for p in yeni_eklenenler]]

        if eksik == 0:
            del ihtiyac[poz]
        else:
            ihtiyac[poz] = eksik
            print(f"    ⚠️ Eksik kalan: {eksik}")

    # 3. Aşama: eksikler kaldıysa mevki3 üzerinden tamamla
    for poz, eksik in list(ihtiyac.items()):
        adaylar = [v for v in veriler if v['mevki3'] == poz]
        adaylar = sorted(adaylar, key=lambda x: x['overall'])

        yeni_eklenenler = []
        for v in adaylar:
            if eksik == 0:
                break
            v['mevki1'] = poz
            final_kadro.append(v)
            yeni_eklenenler.append(v)
            eksik -= 1

        veriler = [v for v in veriler if v['ad_soyad'] not in [p['ad_soyad'] for p in yeni_eklenenler]]
        if eksik == 0:
            del ihtiyac[poz]
        else:
            ihtiyac[poz] = eksik

    # ⬇️ BURAYA EKLE
    if not ihtiyac and veriler:
        print("🟢 Eksikler tamamlandı. Kalan herkes final kadroya ekleniyor.")
        final_kadro.extend(veriler)
        veriler = []
    # Takım sayısını kontrol et
    if len(final_kadro) < 18:
        print(f"❌ UYARI: Kadro yetersiz! Sadece {len(final_kadro)} oyuncu var.")
        return jsonify({"error": f"Kadro yetersiz! En az 18 oyuncu gerekir, mevcut: {len(final_kadro)}"}), 400

    # 4. Aşama: Takımları oluştur
    def hesapla_ortalama(takim):
        d = sum(p['defance'] for p in takim) / len(takim)
        a = sum(p['attack'] for p in takim) / len(takim)
        o = sum(p['overall'] for p in takim) / len(takim)
        return round(d, 1), round(a, 1), round(o, 1)

    def sabit_mevki_tekil_mi(takim):
        kontrol = {}
        for p in takim:
            sm = p.get('sabit_mevki')
            if sm:
                kontrol[sm] = kontrol.get(sm, 0) + 1
                if kontrol[sm] > 1:
                    return False
        return True

    # Pozisyonlara göre ayır
    kaleci = [p for p in final_kadro if p['mevki1'] == 'kaleci']
    defans = [p for p in final_kadro if p['mevki1'] == 'defans']
    ortasaha = [p for p in final_kadro if p['mevki1'] == 'ortasaha']
    forvet = [p for p in final_kadro if p['mevki1'] == 'forvet']

    # Sonsuz döngü ile denge sağlanana kadar takım oluştur
    print("buradayım")
    print(f"ortasaha: {ortasaha}")
    while True:
        random.shuffle(kaleci)
        random.shuffle(defans)
        random.shuffle(ortasaha)
        random.shuffle(forvet)

        takimA = kaleci[:1] + defans[:3] + ortasaha[:4] + forvet[:1]
        takimB = kaleci[1:] + defans[3:] + ortasaha[4:] + forvet[1:]

        dA, aA, oA = hesapla_ortalama(takimA)
        dB, aB, oB = hesapla_ortalama(takimB)
        print(
            f"⛳ Deneme — Kaleci: {len(kaleci)}, Defans: {len(defans)}, Ortasaha: {len(ortasaha)}, Forvet: {len(forvet)}")
        print("🧪 sabit_mevki_tekil_mi (A):", sabit_mevki_tekil_mi(takimA))
        print("🧪 sabit_mevki_tekil_mi (B):", sabit_mevki_tekil_mi(takimB))
        print("🧪 OVR farkı:", abs(oA - oB))
        if abs(oA - oB) < 5 and sabit_mevki_tekil_mi(takimA) and sabit_mevki_tekil_mi(takimB):
            print("\n🟢 Takım A")
            for p in takimA:
                print(
                    f"{p['mevki1'].upper():<10} | {p['ad_soyad']:<20} | DEF: {p['defance']:>3} | ATT: {p['attack']:>3} | OVR: {p['overall']:>3}")
            print(f"DEF: {dA}, ATT: {aA}, OVR: {oA}")

            print("\n🔵 Takım B")
            for p in takimB:
                print(
                    f"{p['mevki1'].upper():<10} | {p['ad_soyad']:<20} | DEF: {p['defance']:>3} | ATT: {p['attack']:>3} | OVR: {p['overall']:>3}")
            print(f"DEF: {dB}, ATT: {aB}, OVR: {oB}")
            with open("takim_log.txt", "a", encoding="utf-8") as f:
                f.write("\n🟢 Takım A\n")
                for p in takimA:
                    f.write(
                        f"{p['mevki1'].upper():<10} | {p['ad_soyad']:<20} | DEF: {p['defance']:>3} | ATT: {p['attack']:>3} | OVR: {p['overall']:>3}\n")
                f.write(f"DEF: {dA}, ATT: {aA}, OVR: {oA}\n\n")

                f.write("🔵 Takım B\n")
                for p in takimB:
                    f.write(
                        f"{p['mevki1'].upper():<10} | {p['ad_soyad']:<20} | DEF: {p['defance']:>3} | ATT: {p['attack']:>3} | OVR: {p['overall']:>3}\n")
                f.write(f"DEF: {dB}, ATT: {aB}, OVR: {oB}\n")
                f.write("=" * 60 + "\n")
            print(
                f"Kadro uzunlukları: kaleci={len(kaleci)}, defans={len(defans)}, ortasaha={len(ortasaha)}, forvet={len(forvet)}")

            return render_template("saha.html", takimA=takimA, takimB=takimB,
                                   def_a=dA, att_a=aA, ovr_a=oA,
                                   def_b=dB, att_b=aB, ovr_b=oB)

if __name__ == '__main__':
    # Veritabanını bir kez oluşturmak için
    with app.app_context():
        db.create_all()
    app.run(debug=True)
