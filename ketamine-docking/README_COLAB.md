# Ketamine Docking Pipeline - Google Colab Kullanım Kılavuzu

Google Colab'da ketamin docking pipeline'ını çalıştırmak için hızlı kılavuz.

## 🚀 Hızlı Başlangıç

### Seçenek 1: Jupyter Notebook (Tavsiye Edilen)

1. **Colab'da aç:**
   - GitHub'dan bu repoyu aç
   - `ketamine-docking/Ketamine_Docking_Colab.ipynb` dosyasını Colab'da aç
   - Veya direkt link: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/egundeger/comp-chem-scripts/blob/main/ketamine-docking/Ketamine_Docking_Colab.ipynb)

2. **Hücreleri sırayla çalıştır:**
   - Runtime → Run all (tümünü çalıştır)
   - Veya her hücreyi tek tek çalıştır

3. **Sonuçları indir:**
   - Son hücrede ZIP dosyası indirilecek
   - Bilgisayarına kaydet

**Süre:** ~1-2 saat (tam pipeline)

### Seçenek 2: Terminal/Shell Script

Colab notebook'ta yeni bir hücre oluştur ve çalıştır:

```bash
# Setup
!bash <(curl -s https://raw.githubusercontent.com/egundeger/comp-chem-scripts/main/ketamine-docking/setup_colab.sh)

# Clone repo
!git clone https://github.com/egundeger/comp-chem-scripts.git
%cd comp-chem-scripts/ketamine-docking

# Run pipeline
!python run_pipeline_colab.py

# Download results
!zip -r results.zip data/results/
from google.colab import files
files.download('results.zip')
```

## 📋 Adım Adım Detaylar

### 1. Kurulum (5-10 dakika)

Colab'da yeni notebook aç ve şunu çalıştır:

```python
# Python paketleri
!pip install -q biopython rdkit pandas pyyaml openpyxl matplotlib seaborn

# Open Babel
!apt-get update -qq && apt-get install -qq -y openbabel

# AutoDock Vina
!wget -q https://github.com/ccsb-scripps/AutoDock-Vina/releases/download/v1.2.5/vina_1.2.5_linux_x86_64 -O /tmp/vina
!chmod +x /tmp/vina && sudo mv /tmp/vina /usr/local/bin/vina

# Verify
!vina --version
!obabel --version
```

### 2. Kodu İndir

```python
!git clone https://github.com/egundeger/comp-chem-scripts.git
%cd comp-chem-scripts/ketamine-docking
!ls -la
```

### 3. Pipeline'ı Çalıştır

```python
# Otomatik mod (user input gerekmez)
!python run_pipeline_colab.py
```

VEYA adım adım:

```python
# Adım 1
!python scripts/1_download_structures.py

# Adım 2
!python scripts/2_prepare_ligand.py

# Adım 3
!python scripts/3_prepare_proteins.py

# Adım 4 (en uzun - 1+ saat)
!python scripts/4_run_docking.py

# Adım 5
!python scripts/5_analyze_results.py
```

### 4. Sonuçları Görüntüle

```python
# Özet göster
!cat data/results/reports/overall_summary_*.txt

# Tablo göster
import pandas as pd
df = pd.read_csv('data/results/reports/summary_*.csv')
print(df)
```

### 5. Sonuçları İndir

```python
# ZIP oluştur
import shutil
from datetime import datetime

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.make_archive(f'results_{timestamp}', 'zip', 'data/results')

# İndir
from google.colab import files
files.download(f'results_{timestamp}.zip')
```

## ⚡ Hızlı Test Modu

Tüm pipeline'ı beklemek istemiyorsan, hızlı test:

```python
# Sadece NMDA + 7EU8 + düşük exhaustiveness
import yaml

# Config düzenle
with open('configs/nmda_targets.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Sadece 7EU8, düşük exhaustiveness
config['structures'] = {'7EU8': config['structures']['7EU8']}
config['structures']['7EU8']['exhaustiveness'] = 8
config['structures']['7EU8']['num_modes'] = 5

with open('configs/nmda_targets.yaml', 'w') as f:
    yaml.dump(config, f)

# Diğer targetları devre dışı bırak
# scripts/4_run_docking.py'de sadece NMDA'yı bırak

# Çalıştır
!python scripts/1_download_structures.py
!python scripts/2_prepare_ligand.py
!python scripts/3_prepare_proteins.py
!python scripts/4_run_docking.py  # Tek target için ~10 dakika
!python scripts/5_analyze_results.py
```

## 🔧 Özelleştirme

### Docking Parametrelerini Değiştir

```python
import yaml

# NMDA için parametreleri düzenle
with open('configs/nmda_targets.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Exhaustiveness değiştir (daha hızlı)
for structure in config['structures'].values():
    structure['exhaustiveness'] = 16  # Varsayılan: 24-32
    structure['num_modes'] = 10       # Varsayılan: 15-20

with open('configs/nmda_targets.yaml', 'w') as f:
    yaml.dump(config, f)
```

### Sadece Belirli Hedefleri Çalıştır

`scripts/4_run_docking.py` dosyasını düzenle:

```python
# Bu satırı bul:
targets = [
    ('nmda', CONFIG_DIR / 'nmda_targets.yaml'),
    ('egfr', CONFIG_DIR / 'egfr_targets.yaml'),
    ('csnk1d', CONFIG_DIR / 'csnk1d_targets.yaml')
]

# Sadece NMDA için değiştir:
targets = [
    ('nmda', CONFIG_DIR / 'nmda_targets.yaml'),
]
```

## 💡 İpuçları

### Runtime Yönetimi

- **Colab ücretsiz:** 12 saat max
- **Pipeline süresi:** 1-2 saat (tüm hedefler)
- **Tek hedef:** ~30 dakika

### Sonuçları Kaydet

⚠️ **Önemli:** Colab geçici storage kullanır!

```python
# Sık sık kaydet
import shutil
shutil.make_archive('backup', 'zip', 'data/results')

from google.colab import files
files.download('backup.zip')
```

### Hız Artırma

1. **Daha az yapı:** Her hedeften 1 yapı
2. **Düşük exhaustiveness:** 8-16 (test için)
3. **Az mode:** 5-10 pose
4. **Tek hedef:** Sadece NMDA

```python
# Hızlı konfigürasyon
exhaustiveness = 8
num_modes = 5
structures_per_target = 1  # Her targettan sadece ilki
```

### Bağlantı Kopması

Eğer Colab bağlantısı koparsa:

```python
# Sonuçlar kaybolur mu? → EVET (geçici storage)
# Ne yapmalı? → Sık sık sonuçları indir
# Kaldığı yerden devam? → Hayır, baştan başlar
```

**Çözüm:** Google Drive'a bağla

```python
from google.colab import drive
drive.mount('/content/drive')

# Sonuçları Drive'a kopyala
!cp -r data/results /content/drive/MyDrive/ketamine_results
```

## 📊 Beklenen Çıktılar

### Dosyalar

```
data/results/
├── reports/
│   ├── overall_summary_TIMESTAMP.txt
│   ├── nmda_report_TIMESTAMP.txt
│   ├── egfr_report_TIMESTAMP.txt
│   ├── csnk1d_report_TIMESTAMP.txt
│   ├── docking_results_TIMESTAMP.xlsx
│   └── summary_TIMESTAMP.csv
├── nmda/
│   ├── 7EU8/S-ketamine/docked_poses.pdbqt
│   └── ...
├── egfr/
└── csnk1d/
```

### Beklenen Değerler

| Target | Beklenen Affinity | Yorum |
|--------|------------------|-------|
| NMDA | -8 to -6 kcal/mol | Güçlü bağlanma |
| EGFR | -7 to -4 kcal/mol | Değişken |
| CSNK1D | -6 to -4 kcal/mol | Zayıf/orta |

## ❓ Sorun Giderme

### "vina: command not found"

```python
!wget -q https://github.com/ccsb-scripps/AutoDock-Vina/releases/download/v1.2.5/vina_1.2.5_linux_x86_64 -O /tmp/vina
!chmod +x /tmp/vina && sudo mv /tmp/vina /usr/local/bin/vina
!vina --version
```

### "No module named 'rdkit'"

```python
!pip install rdkit
```

### "PDB download failed"

```python
# İnternet bağlantısını kontrol et
!ping -c 3 www.rcsb.org

# Tekrar dene
!python scripts/1_download_structures.py
```

### Runtime disconnect

```python
# Önce Drive'a bağla
from google.colab import drive
drive.mount('/content/drive')

# Her adımdan sonra kaydet
!cp -r data/results /content/drive/MyDrive/backup
```

### Docking çok yavaş

```python
# Config'de exhaustiveness düşür
import yaml

for config_file in ['configs/nmda_targets.yaml', 'configs/egfr_targets.yaml', 'configs/csnk1d_targets.yaml']:
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    for structure in config['structures'].values():
        structure['exhaustiveness'] = 12  # Düşük = hızlı
        structure['num_modes'] = 8

    with open(config_file, 'w') as f:
        yaml.dump(config, f)
```

## 🎓 Örnekler

### Örnek 1: Tam Pipeline

```python
# Setup
!bash <(curl -s https://raw.githubusercontent.com/egundeger/comp-chem-scripts/main/ketamine-docking/setup_colab.sh)

# Clone
!git clone https://github.com/egundeger/comp-chem-scripts.git
%cd comp-chem-scripts/ketamine-docking

# Run
!python run_pipeline_colab.py

# Download
!zip -r results.zip data/results/
from google.colab import files
files.download('results.zip')
```

### Örnek 2: Sadece NMDA

```python
# Setup (aynı)
# Clone (aynı)

# Sadece NMDA için config
import yaml
with open('configs/nmda_targets.yaml', 'r') as f:
    config = yaml.safe_load(f)

# İstersen parametreleri düzenle

# Run steps
!python scripts/1_download_structures.py
!python scripts/2_prepare_ligand.py
!python scripts/3_prepare_proteins.py

# Edit scripts/4_run_docking.py to only run NMDA
# veya manuel olarak vina çalıştır

!python scripts/5_analyze_results.py
```

## 🔗 Linkler

- **GitHub Repo:** https://github.com/egundeger/comp-chem-scripts
- **Colab Notebook:** [Ketamine_Docking_Colab.ipynb](Ketamine_Docking_Colab.ipynb)
- **Ana README:** [README.md](README.md)
- **Quick Start:** [QUICKSTART.md](QUICKSTART.md)

## 📞 Destek

Sorun yaşıyorsan:
1. Bu README'yi kontrol et
2. Ana README.md'ye bak
3. EXAMPLES.md'de benzer durumu ara
4. GitHub'da issue aç

---

**Not:** Google Colab ücretsiz versiyonu bu pipeline için yeterlidir. GPU gerekmez.
