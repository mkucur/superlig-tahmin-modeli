# Süper Lig Maç Tahmin Modeli

Bu proje, Dixon-Coles istatistiksel modelini kullanarak Türkiye Süper Lig maç sonuçlarını tahmin etmek için geliştirilmiştir. Dixon-Coles modeli, futbol maçlarının sonuçlarını tahmin etmek için kullanılan en güvenilir istatistiksel modellerden biridir.

## Özellikler

- 🏆 Türkiye Süper Lig'deki her takımın hücum ve savunma gücünü analiz eder
- 📊 Seçilen hafta için tüm maçların olası sonuçlarını görselleştirir
- 🎯 Maç sonuçları için olasılık dağılımını ısı haritası olarak sunar
- 📆 Kullanıcının istediği hafta için analiz yapabilme esnekliği
- ⏱️ Zaman ağırlıklı model ile takımların güncel form durumlarını daha iyi yansıtır
- 💾 Her analiz sonucunu ayrı bir klasörde saklar

## Nasıl Çalışır?

Bu uygulama, Dixon-Coles modelini kullanarak futbol maç sonuçlarını tahmin eder. Bu model:

1. Her takımı hücum ve savunma gücü parametreleriyle modellemektedir
2. Ev sahibi avantajını dikkate almaktadır
3. Düşük skorlu maçlarda görülen bağımlılık etkisini hesaba katmaktadır
4. Yeni eklenen zaman ağırlıklı öğrenme ile takımların güncel form durumlarına daha fazla önem verir

Program, geçmiş maç verilerini kullanarak her takımın parametrelerini optimize eder ve ardından bu parametreleri kullanarak gelecek maçlar için olasılık dağılımları oluşturur.

## Kurulum

1. Gerekli kütüphaneleri yükleyin:

```bash
pip install -r requirements.txt
```

2. Projeyi bilgisayarınıza indirin:

```bash
git clone https://github.com/mkucur/superlig-tahmin-modeli.git
cd superlig-tahmin-modeli
```

## Kullanım

Programı çalıştırmak için:

```bash
python main.py
```

Çalıştırdığınızda, program size iki soru soracaktır:

1. **Hangi haftanın analizini yapmak istiyorsunuz?** Varsayılan olarak 29. hafta seçilidir, ancak istediğiniz hafta numarasını girebilirsiniz.

2. **Zaman ağırlık parametresi (λ) değerini girin:** Bu parametre, eski maçlara göre yeni maçların ne kadar daha önemli olacağını belirler. Varsayılan değer 0.1'dir.

Örneğin:
- λ = 0.01: Tüm sezonu neredeyse eşit ağırlıkta değerlendirir
- λ = 0.05: Eski maçlara da önem verir, ancak yeni maçlara biraz daha fazla ağırlık verir
- λ = 0.1: Son haftalara daha fazla ağırlık verir (5 hafta önceki maçların ağırlığı son haftanın %61'i kadardır)
- λ = 0.2: Son haftalara çok daha fazla ağırlık verir (form değişimlerine hızlı tepki gösterir)

## Çıktılar

Program aşağıdaki çıktıları oluşturur:

1. **Takım Güçleri Grafiği**: Tüm takımların hücum ve savunma güçlerini karşılaştıran bir grafik
2. **Zaman Ağırlıkları Grafiği**: Hangi haftadaki maçlara ne kadar ağırlık verildiğini gösteren grafik
3. **Maç Tahmin Isı Haritaları**: Her maç için olası skorların olasılık dağılımını gösteren ısı haritaları
4. **Hafta Klasörü**: Tüm çıktılar `{hafta}_hafta_analiz` adlı bir klasöre kaydedilir

## Model Hakkında

Dixon-Coles modeli, 1997 yılında Mark Dixon ve Stuart Coles tarafından geliştirilen bir Poisson regresyon modelidir. Bu model, standart Poisson modelini düşük skorlu maçlardaki (örneğin 0-0, 1-0, 0-1, 1-1) istatistiksel bağımlılığı dikkate alacak şekilde genişletir.

Bu modele göre, ev sahibi takımın atacağı gol sayısı ve deplasman takımının atacağı gol sayısı aşağıdaki Poisson dağılımlarına sahiptir:

- Ev sahibi golleri ~ Poisson(αₕ × βₐ × γ)
- Deplasman golleri ~ Poisson(αₐ × βₕ)

Burada:
- αₕ: Ev sahibi takımın hücum gücü
- βₕ: Ev sahibi takımın savunma gücü
- αₐ: Deplasman takımının hücum gücü
- βₐ: Deplasman takımının savunma gücü
- γ: Ev sahibi avantajı faktörü
- ρ: Düşük skorlar için bağımlılık parametresi

### Zaman Ağırlıklı Öğrenme

Zaman ağırlıklı öğrenme ile model, eski maçlara göre daha yeni maçlara daha fazla önem verir. Bu, takımların güncel form durumlarını daha iyi yansıtmak için kullanılır. Maçların zamansal ağırlığı şu formülle hesaplanır:

w_t = e^(-λt)

Burada:
- w_t: t zaman birimindeki bir maçın ağırlığı
- λ: Zamansal azalma faktörü (kullanıcı tarafından belirlenir)
- t: Maçın geçmişte ne kadar geriye gittiği (hafta farkı)

## Örnek Çıktılar

Proje çalıştırıldığında, takımların hücum/savunma güçlerini gösteren bir grafik ve her maç için ayrıntılı tahmin ısı haritaları oluşturulur.

## Son Güncelleme

Bu proje 26 Mart 2025 tarihinde GitHub'a yüklenmiştir.

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.