[English](https://github.com/hdaltuntas/lythos-pile/blob/main/README.md) | **Türkçe**

# Lythos Pile

[![Tests](https://github.com/hdaltuntas/lythos-pile/actions/workflows/tests.yml/badge.svg)](https://github.com/hdaltuntas/lythos-pile/actions/workflows/tests.yml)

Tabakalı zeminde kazıkların eksenel taşıma gücü, grup etkisi ve oturması ile kaya soketi
boyu; tarayıcıdan sürülen bir program. Dairesel ya da kare kesitli, fore ya da çakma (az ya
da çok yer değiştiren) bir kazık, tek başına ya da başlık altında dikdörtgen bir grup
olarak, **bir mühendisten istenebilecek bütün yöntemlerle** yan yana hesaplanır:

1. **Çevre sürtünmesi** — kilde API RP 2A, Kulhawy & Phoon ve Sladen **α yöntemleri**,
   **β yöntemi** (Burland) ve **λ yöntemi** (Vijayvergiya & Focht); kumda **K·σ′v·tan δ**,
   Meyerhof **kritik derinliği** ile; Meyerhof **SPT** kuralı.
2. **Uç direnci** — **Meyerhof**, **Vesić** (rijitlik indisi) ve **Janbu**; kilde 9·cu,
   Vesić ve Janbu Nc\*; Meyerhof SPT kuralı.
3. **Kazık ağırlığı** — **yeraltı suyu** altında batık — nihai taşıma gücünden düşülür:
   Qult,net = Qs + Qb − W, Qall = Qult,net / GS. Bütün gerilmeler efektiftir.
4. **Grup etkisi** — **Converse–Labarre**, **Los Angeles Group**, **Seiler–Keeney** ve
   **Feld** verimleri ile **blok göçmesi**; grubun taşıma gücü küçük olandır.
5. **Gerekli kazık boyu** — tek kazık ve grup kontrollerini sağlayan en kısa kazık; taşıma
   gücü boya göre çizilir.
6. **Oturma** — tek kazık **Vesić** ile; grup, 2/3·L'deki **eşdeğer radye** (killer Cc, Cr,
   e0 ve AKO ile konsolide olur, diğerleri elastik sıkışır), **Vesić** √(Bg/D) kuralı ve
   **Meyerhof** SPT kuralı ile.
7. **Kayaya soketli kazık**, ayrı bir hesap olarak — **on iki yayımlanmış bağıntının**
   (Rosenberg & Journeaux, Horvath & Kenney, Meigh & Wolski, Williams vd., Reynolds &
   Kaderabek, Gupton & Logan, Rowe & Armitage, Carter & Kulhawy, Toh vd., Zhang & Einstein,
   O'Neill & Reese / AASHTO, Kulhawy vd.) birim yanal sürtünmesi, altı yöntemin uç direnci,
   **her birinin gerektirdiği soket boyu**, bunların ortalaması, medyanı, sınırları ya da
   seçilen biriyle tasarım boyu ve soketin **elastik oturması** — **Randolph & Wroth**
   (uçlu ve uçsuz) ve Vesić ile.

Bunun üzerine bir **parametrik veya güvenilirlik çalışması** istenen girdiyi — bir aralık ya
da dağılım olarak — tarar; duyarlılıkları ve tek kazığın, grubun ya da oturmanın göçme
olasılığını güven aralığı ve güvenilirlik indeksi β ile verir.

Programın tamamı — her etiket, sonuç metni, şekil ve rapor — **Türkçe ve İngilizce**
çalışır; dil çalışma sırasında değiştirilir.

Arayüz, kendi makinenizde çalışan küçük bir HTTP sunucusudur ve tarayıcıdan sürülür. Böylece
program uzak oturumda ya da konteyner içinde de çalışır ve standart kütüphane dışında hiçbir
bağımlılık getirmez.

> [LythosFEA](https://github.com/hdaltuntas/lythos),
> [Lythos Bearing](https://github.com/hdaltuntas/lythos-bearing),
> [Lythos Settle](https://github.com/hdaltuntas/lythos-settle),
> [Lythos MSEW](https://github.com/hdaltuntas/lythos-msew),
> [Lythos Kinematic](https://github.com/hdaltuntas/lythoskinematic),
> [Lythos SPWA](https://github.com/hdaltuntas/lythosspwa) ve
> [LythosLE](https://github.com/hdaltuntas/lythosle) programlarının kardeşidir; aynı mimariyi,
> temayı ve yazı tiplerini kullanır.

## Ekran görüntüleri

| Kazık grubu, özet | Kaya soketi, özet |
|---|---|
| ![Kazık özeti](https://raw.githubusercontent.com/hdaltuntas/lythos-pile/main/screenshots/pile_summary.png) | ![Soket özeti](https://raw.githubusercontent.com/hdaltuntas/lythos-pile/main/screenshots/socket_summary.png) |

| Gerilmeler ve çevre sürtünmesi, koyu tema, Türkçe | Boya göre taşıma gücü |
|---|---|
| ![Profil](https://raw.githubusercontent.com/hdaltuntas/lythos-pile/main/screenshots/pile_profile_dark_tr.png) | ![Boy](https://raw.githubusercontent.com/hdaltuntas/lythos-pile/main/screenshots/pile_length.png) |

## Kurulum ve çalıştırma

```bash
pip install numpy matplotlib reportlab
python main.py                     # arayüzü tarayıcıda açar
```

ya da `pip install .` ile kurup `lythos-pile` komutunu çalıştırın. Word raporu için
`python-docx`, çalışmanın tablo çıktısı için `openpyxl` gerekir: `pip install ".[docx,xlsx]"`.
Python 3.10 ve üstü gereklidir.

## Komut satırı

```bash
lythos-pile                                   # web arayüzü (varsayılan)
lythos-pile web --port 9000 --lang tr --no-browser
lythos-pile example -o project.pile           # örnek proje dosyası
lythos-pile run project.pile -o rapor.pdf     # kazık ve grubu, rapor
lythos-pile run project.pile --socket -o rapor.pdf    # … kaya soketiyle birlikte
lythos-pile socket project.pile -o soket.pdf  # yalnız kaya soketi
lythos-pile study project.pile -o ornekler.csv
```

Arayüz varsayılan olarak 8783 numaralı portu dinler.

## Girdiler

* **Kazık:** dairesel ya da kare, D, L, kazık başı derinliği (başlık altı), imalat yöntemi
  (fore / CFA, az ya da çok yer değiştiren çakma), γp, Ep.
* **Yük:** başlık altında gruba gelen düşey yük.
* **Grup:** B ve L yönünde kazık sayısı, aralıklar, verim yöntemi, blok göçmesi (1 × 1 tek
  kazıktır).
* **Yeraltı suyu:** su tablası derinliği, γw.
* **Zemin profili**, yüzeyden aşağı, her tabaka bir satır: kalınlık, granüler ya da
  kohezyonlu, γ, γdoy, φ′, cu, AKO, N60, E, ν, Cc, Cr, e0.
* **Yöntemler:** kil yöntemi, uç yöntemi, kumda K/K0 ve δ/φ′, kritik derinlik, Janbu η′,
  Sladen C, SPT kuralı; kazık ağırlığının düşülmesi ve su altında batık alınması.
* **Oturma:** kontrolde kullanılan grup yöntemi, eşdeğer radye derinliği, yük yayılımı,
  sürtünme dağılımı.
* **Ölçütler:** güvenlik sayısı, izin verilen oturma, boy araması.
* **Kaya soketi:** soket çapı ve boyu, kazık başı ve kaya yüzeyi derinlikleri, yük; qu, kaya
  kütlesi modülü (RQD'den, GSI'dan ya da doğrudan), GSI, mi, D, ν, uç altı modül, süreksizlik
  aralığı ve açıklığı; f′c, Ec, beton birim hacim ağırlığı; tasarım istatistiği, tasarım uç
  direnci, iki güvenlik sayısı, en küçük soket boyu ve zayıf kaya sınırı.

Kullanılan bağıntılar, kaynakları ve sınırları
[docs/theory.md](https://github.com/hdaltuntas/lythos-pile/blob/main/docs/theory.md)
dosyasındadır.

## Raporlar

Başlıktan PDF, tek dosyalık HTML ya da Word seçip *Rapor al…* düğmesine basın. Rapor, hesabı
yapılmış olanı taşır — kazık ve grubu, kaya soketi, çalışma — arayüz hangi dildeyse o dilde.

## Geliştirme

```bash
pip install -e ".[dev]"
pytest -q
ruff check .
```

## Lisans

Telif hakkı © 2026 Hasan Deniz Altuntaş

Lythos Pile özgür yazılımdır: Özgür Yazılım Vakfı'nın yayımladığı
[GNU Affero Genel Kamu Lisansı, sürüm 3](https://github.com/hdaltuntas/lythos-pile/blob/main/LICENSE) koşulları altında yeniden dağıtabilir ve/veya
değiştirebilirsiniz. Yararlı olması umuduyla dağıtılır, ancak HİÇBİR GARANTİSİ YOKTUR;
SATILABİLİRLİK ya da BELİRLİ BİR AMACA UYGUNLUK zımni garantisi dahi yoktur.

Değiştirilmiş bir sürümü kullanıcılara ağ üzerinden sunan, o sürümün kaynak kodunu da onlara
sunmak zorundadır (lisansın 13. bölümü). Bu değişiklikten önce yayımlanan sürümler MIT
lisansıyla dağıtılmıştır ve o lisansla kullanılmaya devam edebilir.
