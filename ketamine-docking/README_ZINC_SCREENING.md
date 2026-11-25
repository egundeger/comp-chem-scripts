# ZINC20 FDA Approved Drugs - Virtual Screening Pipeline

Google Colab'da FDA onaylı ilaçları ZINC20 veritabanından çekerek hedef proteinlere karşı virtual screening yapar.

## 🎯 Özellikler

- **Otomatik ligand hazırlama**: SMILES → 3D → PDBQT
- **Batch docking**: Binlerce ilaç paralel screening
- **Sonuç analizi**: En iyi binders otomatik sıralama
- **Hit validation**: Top binders yüksek doğrulukla re-docking
- **Comprehensive reporting**: Excel, CSV, JSON çıktılar

## 🚀 Hızlı Başlangıç

### Google Colab'da

1. **Notebook'u aç:**
   - `ZINC_FDA_Screening_Colab.ipynb` dosyasını Colab'da aç

2. **Tüm hücreleri çalıştır:**
   - Runtime → Run all

3. **Sonuçları indir:**
   - Excel, CSV ve ZIP dosyaları otomatik indirilir

### Tahmini Süre

| Adım | Süre |
|------|------|
| Kurulum | 5-10 dakika |
| Ligand hazırlama (10 ilaç) | 5 dakika |
| Ligand hazırlama (100 ilaç) | 30 dakika |
| Ligand hazırlama (1000 ilaç) | ~5 saat |
| Docking (10 ilaç) | 5-10 dakika |
| Docking (100 ilaç) | 1-2 saat |
| Docking (1000 ilaç) | 10-20 saat |

⚠️ **Not:** 1000+ ilaç için Google Colab Pro önerilir (daha uzun session süresi)

## 📊 Veri Kaynakları

### ZINC20 Database

**Recommended:**
```bash
# ZINC20 FDA approved subset
https://zinc.docking.org/substances/subsets/fda/
```

**Alternatifler:**
1. **DrugBank** (ücretsiz akademik lisans)
   - https://go.drugbank.com/
   - ~10,000 FDA approved drugs

2. **ChEMBL**
   - https://www.ebi.ac.uk/chembl/
   - FDA approved subset filtrelenebilir

3. **PubChem**
   - FDA approved drugs collection
   - ftp://ftp.ncbi.nlm.nih.gov/pubchem/

### Veri Formatı

CSV dosyası şu sütunları içermeli:

| Sütun | Açıklama | Örnek |
|-------|----------|-------|
| name | İlaç adı | Aspirin |
| smiles | SMILES yapısı | CC(=O)Oc1ccccc1C(=O)O |
| zinc_id | ZINC ID (opsiyonel) | ZINC000003830276 |

## 🔧 Kullanım

### 1. Basit Kullanım (Demo)

Notebook'taki örnek verilerle:

```python
# Demo modu - 4 örnek ilaç
fda_drugs = download_zinc_fda_approved()
```

### 2. Kendi Veri Setinizle

```python
# CSV'den yükle
fda_drugs = pd.read_csv('zinc20_fda_approved.csv')
print(f"✓ {len(fda_drugs)} ilaç yüklendi")
```

### 3. ZINC20 API ile (İleri Seviye)

```python
import requests

# ZINC20 API endpoint
url = "https://zinc.docking.org/api/substances/subsets/fda/"
response = requests.get(url)
fda_drugs = pd.DataFrame(response.json())
```

## ⚙️ Docking Parametreleri

### Hızlı Screening (Önerilen İlk Tarama)

```python
docking_params = {
    'exhaustiveness': 8,   # Hızlı
    'num_modes': 1,        # Sadece en iyi pose
}
```

- **Süre:** ~30 saniye/ilaç
- **Doğruluk:** Orta
- **Kullanım:** İlk tarama için

### Standart Screening

```python
docking_params = {
    'exhaustiveness': 16,
    'num_modes': 5,
}
```

- **Süre:** ~2 dakika/ilaç
- **Doğruluk:** İyi
- **Kullanım:** Normal screening

### Yüksek Doğruluk (Hit Validation)

```python
docking_params = {
    'exhaustiveness': 32,
    'num_modes': 20,
}
```

- **Süre:** ~5 dakika/ilaç
- **Doğruluk:** Çok iyi
- **Kullanım:** Top binders validation

## 📈 Sonuç Yorumlama

### Binding Affinity Değerleri

| Affinity (kcal/mol) | Yorum | Aksiyon |
|---------------------|-------|---------|
| < -9.0 | Çok güçlü | Hemen validate et |
| -9.0 to -7.0 | Güçlü | Hit olarak değerlendir |
| -7.0 to -5.0 | Orta | Daha detaylı analiz |
| > -5.0 | Zayıf | Genelde önemsiz |

### Hit Kriterleri

**Potansiyel Hit:**
1. Binding affinity < -7.0 kcal/mol
2. Validation sonucu benzer
3. Bilinen biyolojik aktivite uyumlu
4. ADMET özellikleri uygun

## 📁 Çıktı Dosyaları

```
zinc_screening/
├── results/
│   ├── screening_results_YYYYMMDD_HHMMSS.xlsx    # Excel raporu
│   ├── screening_results_YYYYMMDD_HHMMSS.csv     # CSV verisi
│   ├── screening_results_YYYYMMDD_HHMMSS.json    # JSON verisi
│   └── [drug_name]_docked.pdbqt                  # Her ilaç için pose
├── ligands/
│   ├── pdb/                                       # 3D yapılar (PDB)
│   └── pdbqt/                                     # Vina formatı
└── target/
    └── [target]_clean.pdbqt                       # Hedef protein
```

### Excel Raporu İçeriği

**Sheet 1: All Results**
- Tüm docking sonuçları
- Success/failure durumu
- File paths

**Sheet 2: Top 50 Binders**
- En iyi 50 ilaç
- Affinity sıralaması

**Sheet 3: Statistics**
- Genel istatistikler
- Hit oranı
- Dağılım metrikleri

## 🎨 Görselleştirme

Notebook otomatik olarak şunları oluşturur:

1. **Histogram**: Binding affinity dağılımı
2. **Cumulative plot**: Kümülatif dağılım
3. **Top binders table**: En iyi sonuçlar

## 🔬 Hit Validation Protokolü

1. **İlk tarama** (exhaustiveness=8):
   - Tüm ilaçları hızlı tara
   - Top 50 seç

2. **İkinci tarama** (exhaustiveness=16):
   - Top 50'yi tekrar dockla
   - Top 20 seç

3. **Validation** (exhaustiveness=32):
   - Top 20'yi yüksek doğrulukla
   - Final hit list

4. **MD Simülasyonları**:
   - En iyi 5-10 hit
   - GROMACS/AMBER

## ⚡ Performans Optimizasyonu

### Colab Free Tier

- **Batch size**: 100-200 ilaç/session
- **Exhaustiveness**: 8
- **Checkpoint**: Her 50 ilaçta kaydet

### Colab Pro

- **Batch size**: 1000+ ilaç/session
- **Exhaustiveness**: 16
- **Longer runtime**: 24 saat

### Lokal Cluster

```bash
# Paralel çalıştırma (GNU Parallel)
parallel -j 8 'vina --config {}_config.txt' ::: ligands/*.pdbqt
```

## 🐛 Sorun Giderme

### Problem: Ligand hazırlama başarısız

**Çözüm:**
- SMILES yapısını kontrol edin
- Tautomer/ionization state düzeltin
- Çok büyük moleküller için timeout artırın

### Problem: Docking çok yavaş

**Çözüm:**
- exhaustiveness düşürün (8 veya 4)
- Search box küçültün
- num_modes = 1 yapın

### Problem: Düşük hit oranı

**Çözüm:**
- Binding site koordinatlarını kontrol edin
- Pozitif kontrol kullanın (bilinen binder)
- Search box boyutunu artırın

### Problem: Colab timeout

**Çözüm:**
- Daha az ilaç ile başlayın
- Sonuçları sık kaydedin
- Colab Pro kullanın

## 📚 Örnekler

### Örnek 1: NMDA Reseptörü Screening

```python
# Hedef protein: NMDA GluN2B
target_pdb_id = '7EU8'
docking_params = {
    'center_x': 50.0,  # Kanal bloker site
    'center_y': 50.0,
    'center_z': 20.0,
    'size_x': 30.0,
    'size_y': 30.0,
    'size_z': 40.0,
}
```

### Örnek 2: Kinaz Screening

```python
# Hedef protein: EGFR kinase
target_pdb_id = '4I24'
docking_params = {
    'center_x': 24.0,  # ATP binding site
    'center_y': 32.0,
    'center_z': 42.0,
    'size_x': 25.0,
    'size_y': 25.0,
    'size_z': 25.0,
}
```

## 🔗 Referanslar

### Metodoloji
- Eberhardt et al. (2021) AutoDock Vina 1.2.0. J Chem Inf Model
- Forli et al. (2016) Computational protein-ligand docking. Methods Mol Biol

### Best Practices
- Schrödinger (2020) Virtual Screening Workflow
- Ripphausen et al. (2010) J Med Chem

### Databases
- ZINC20: https://zinc.docking.org/
- DrugBank: https://go.drugbank.com/
- ChEMBL: https://www.ebi.ac.uk/chembl/

## 💡 İleri Seviye

### Custom Scoring Functions

```python
# Vina scoring modifikasyonu
# --scoring vina, ad4, vinardo
```

### Consensus Docking

```python
# Birden fazla docking programı kullanın:
# - AutoDock Vina
# - AutoDock4
# - Glide
# - GOLD
```

### Machine Learning Integration

```python
# Docking + ML filtering
# - Random Forest
# - Neural Networks
# - DeepChem
```

## 📞 Destek

- **GitHub Issues**: Bug reports ve feature requests
- **Discussions**: Sorular ve best practices
- **Email**: Teknik destek için

## 📄 Lisans

Bu pipeline araştırma ve eğitim amaçlı kullanım içindir.

---

**Version:** 1.0
**Last Updated:** 2025-01-13
**Maintainer:** Computational Chemistry Team
