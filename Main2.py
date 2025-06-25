from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://tr.investing.com/news/stock-market-news")
time.sleep(3)

# Sayfa HTML'ini al ve BeautifulSoup'a aktar
soup = BeautifulSoup(driver.page_source, "html.parser")
articles = soup.select('a[data-test="article-title-link"]')

# İlk 20 haberin başlığını ve linkini çek artırılabilir
news_data = []
for tag in articles[:20]:
    title = tag.text.strip()
    href = tag['href']
    link = href if href.startswith("http") else "https://tr.investing.com" + href
    news_data.append({"title": title, "url": link})
    print(f"\n📰 {title}\n🔗 {link}")

driver.quit()



################################## Kategorilendirme

from transformers import pipeline

classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli" 
)
labels = [
    "Hisse Yorum / Hedef Fiyat",         # Analist hedefleri, tavsiyeler, beklenti güncellemeleri
    "Hisse Fiyat Değişimi",              # Hisse senedi düşüş/yükseliş haberleri, halka arz, satışlar
    "Makroekonomik & Sektörel Etki",     # Yeni yatırımlar, ortaklıklar, üretim, AR-GE, tedarik zinciri
    "Endeks / Genel Piyasa Haberi",      # Nasdaq, S&P, BIST100, genel piyasa yönü
    "Yatırım Tavsiyesi / Kurum Yorumu",  # Kurumsal raporlar, stratejik pozisyonlanmalar
    "Hukuki / Düzenleyici Gelişme"       # Vergi, regülasyon, cezalar, soruşturmalar
]


for item in news_data:
    result = classifier(item["title"], candidate_labels=labels)
    item["predicted_label"] = result["labels"][0]
    print(f"\n {item['title']}")
    print(f"🏷 Tahmin Edilen Kategori: {item['predicted_label']}")


######################Anlık Durumlar#################################################
yukselenler = []
dususenler = []

for item in news_data:
    title = item["title"]
    kategori = item["predicted_label"]

    if kategori in ["Hisse Fiyat Değişimi", "Hisse Yorum / Hedef Fiyat"]:
        if any(word in title.lower() for word in ["yükseldi", "arttı", "yükselişte", "hedef", "pozitif", "güncellendi", "yukarı"]):
            yukselenler.append(item)
        elif any(word in title.lower() for word in ["düştü", "azaldı", "geriledi", "düşüşte", "negatif", "indirdi", "aşağı"]):
            dususenler.append(item)
# Sonuçları yazdır
print("\n Hissesi Yükselen Şirketler:")
for item in yukselenler:
    print(f"- {item['title']}")

print("\n Hissesi Düşen Şirketler:")
for item in dususenler:
    print(f"- {item['title']}")


######################Gelecekte Beklenen##################################################

gelecekte_yukselmesi_beklenen = []
gelecekte_dusmesi_beklenen = []

for item in news_data:
    title = item["title"]
    kategori = item["predicted_label"]

    if kategori == "Makroekonomik & Sektörel Etki":
        if any(word in title.lower() for word in ["ortaklık", "genişleme", "yatırım", "işbirliği", "anlaşma", "yeni", "ihraç", "girişim","yükseldi", "arttı", "yükselişte"]):
            gelecekte_yukselmesi_beklenen.append(item)
        elif any(word in title.lower() for word in ["sorun", "gecikme", "azalma", "iptal", "dava", "risk", "anlaşmazlık","düşüyor","düştü", "azaldı", "geriledi", "düşüşte"]):
            gelecekte_dusmesi_beklenen.append(item)

print("\n Gelecekte Yükselmesi Beklenen Şirketler:")
for item in gelecekte_yukselmesi_beklenen:
    print(f"- {item['title']}")

print("\n️Gelecekte Düşme Riski Olan Şirketler:")
for item in gelecekte_dusmesi_beklenen:
    print(f"- {item['title']}")
