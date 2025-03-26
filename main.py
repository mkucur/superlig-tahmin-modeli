import numpy as np
import pandas as pd
from scipy.optimize import minimize, Bounds
from scipy.stats import poisson
import matplotlib.pyplot as plt
import seaborn as sns
from datafc.sofascore import match_data, standings_data
import os
import datetime  # Tarihleri işlemek için ekliyorum

# Veri klasörü oluşturma
os.makedirs("data", exist_ok=True)

# Hafta bazlı fikstür verileri
def get_fixtures():
    """
    Süper Lig fikstür bilgilerini döndüren yardımcı fonksiyon.
    Her haftanın fikstürünü içeren bir sözlük döndürür.
    """
    # 2024/25 sezonu fikstür bilgileri
    fixtures = {
        1: [
            ("Galatasaray", "Hatayspor"),
            ("Fenerbahçe", "Adana Demirspor"),
            ("Beşiktaş", "Konyaspor"),
            ("Trabzonspor", "Antalyaspor"),
            ("Eyüpspor", "Alanyaspor"),
            ("Sivasspor", "Samsunspor"),
            ("Gaziantep FK", "Bodrum FK"),
            ("Başakşehir FK", "Göztepe"),
            ("Kasımpaşa", "Kayserispor")
        ],
        2: [
            ("Alanyaspor", "Galatasaray"),
            ("Hatayspor", "Beşiktaş"),
            ("Göztepe", "Fenerbahçe"),
            ("Adana Demirspor", "Trabzonspor"),
            ("Antalyaspor", "Sivasspor"),
            ("Samsunspor", "Başakşehir FK"),
            ("Bodrum FK", "Eyüpspor"),
            ("Konyaspor", "Kasımpaşa"),
            ("Kayserispor", "Gaziantep FK")
        ],
        # Diğer haftaların fikstürleri buraya eklenecek
        28: [
            ("Eyüpspor", "Fenerbahçe"),
            ("Gaziantep FK", "Beşiktaş"),
            ("Bodrum FK", "Antalyaspor"),
            ("Sivasspor", "Göztepe"),
            ("Galatasaray", "Trabzonspor"),
            ("Hatayspor", "Konyaspor"),
            ("Alanyaspor", "Adana Demirspor"),
            ("Başakşehir FK", "Kayserispor"),
            ("Samsunspor", "Kasımpaşa")
        ],
        29: [
            ("Kayserispor", "Hatayspor"),
            ("Antalyaspor", "Alanyaspor"),
            ("Konyaspor", "Gaziantep FK"),
            ("Bodrum FK", "Fenerbahçe"),
            ("Sivasspor", "Adana Demirspor"),
            ("Trabzonspor", "Göztepe"),
            ("Samsunspor", "Kasımpaşa"),
            ("Beşiktaş", "Galatasaray"),
            ("Eyüpspor", "Başakşehir FK")
        ],
        30: [
            ("Galatasaray", "Konyaspor"),
            ("Hatayspor", "Gaziantep FK"),
            ("Fenerbahçe", "Sivasspor"),
            ("Adana Demirspor", "Bodrum FK"),
            ("Göztepe", "Eyüpspor"),
            ("Başakşehir FK", "Antalyaspor"),
            ("Alanyaspor", "Beşiktaş"),
            ("Kasımpaşa", "Trabzonspor"),
            ("Kayserispor", "Samsunspor")
        ],
        # Diğer haftaların fikstürleri buraya eklenecek
    }
    
    return fixtures

def get_match_data(max_week=28):
    """
    Türkiye Süper Lig maç verilerini çeken fonksiyon.
    
    Parameters:
    -----------
    max_week : int, optional
        Çekilecek maksimum hafta sayısı (varsayılan: 28)
    """
    print(f"Süper Lig 1-{max_week}. hafta maç verileri çekiliyor...")
    
    # 1-max_week haftanın verilerini çekelim
    all_matches = []
    
    # Veri klasörünü kontrol et
    os.makedirs("data", exist_ok=True)
    
    for week in range(1, max_week + 1):
        print(f"{week}. hafta verileri çekiliyor...")
        try:
            # Önce o hafta için kaydedilmiş dosya var mı kontrol et
            hafta_dosyasi = f"data/hafta_{week}_maclar.json"
            try:
                # Dosya mevcutsa yükle
                hafta_df = pd.read_json(hafta_dosyasi, lines=True)
                print(f"{week}. hafta verileri önceden kaydedilmiş dosyadan yüklendi.")
                all_matches.append(hafta_df)
                continue
            except FileNotFoundError:
                # Dosya yoksa o haftanın verilerini çek
                pass
            
            # Süper Lig için tournament_id=52, 2024/25 sezonu için season_id=63814
            matches = match_data(
                tournament_id=52,
                season_id=63814,
                week_number=week,
                data_source="sofascore",
                enable_json_export=False,
                enable_excel_export=False
            )
            
            # Gerekli sütunları seçelim ve modelde kullanacağımız sütun isimlerine çevirelim
            if 'home_score_normaltime' in matches.columns and 'away_score_normaltime' in matches.columns:
                match_df = matches[['home_team', 'away_team', 'home_score_normaltime', 'away_score_normaltime']]
                match_df = match_df.rename(columns={
                    'home_score_normaltime': 'home_score',
                    'away_score_normaltime': 'away_score'
                })
            else:
                # Alternatif sütun isimleri
                score_cols = [
                    ('home_score_normaltime', 'away_score_normaltime'),
                    ('home_score_current', 'away_score_current'),
                    ('home_score_display', 'away_score_display')
                ]
                
                found = False
                for home_col, away_col in score_cols:
                    if home_col in matches.columns and away_col in matches.columns:
                        match_df = matches[['home_team', 'away_team', home_col, away_col]]
                        match_df = match_df.rename(columns={
                            home_col: 'home_score',
                            away_col: 'away_score'
                        })
                        found = True
                        break
                
                if not found:
                    print(f"Uyarı: {week}. hafta için skor sütunları bulunamadı. Kullanılabilir sütunlar: {matches.columns.tolist()}")
                    continue
            
            # Boş değerleri ve NaN'ları 0 ile dolduralım
            match_df['home_score'] = match_df['home_score'].fillna(0)
            match_df['away_score'] = match_df['away_score'].fillna(0)
            
            # Sayısal değerlere dönüştürme
            match_df['home_score'] = match_df['home_score'].astype(int)
            match_df['away_score'] = match_df['away_score'].astype(int)
            
            # Her haftanın verilerini ayrı dosyaya kaydedelim
            match_df.to_json(hafta_dosyasi, orient='records', lines=True)
            
            all_matches.append(match_df)
            print(f"{week}. hafta verileri başarıyla çekildi ve {hafta_dosyasi} dosyasına kaydedildi.")
        except Exception as e:
            print(f"{week}. hafta verileri çekilirken hata oluştu: {e}")
    
    # Tüm hafta verilerini birleştir
    if not all_matches:
        raise ValueError("Hiç maç verisi çekilemedi!")
        
    all_matches_df = pd.concat(all_matches, ignore_index=True)
    print(f"Toplam {len(all_matches_df)} maç verisi çekildi.")
    
    # Veriyi tek bir dosyaya da kaydedelim
    all_matches_df.to_json("data/tff_super_lig_2425_1-28_maclar.json", orient='records', lines=True)
    print("Tüm veriler 'data/tff_super_lig_2425_1-28_maclar.json' dosyasına kaydedildi.")
    
    return all_matches_df

def load_data(max_week=28):
    """
    Veri dosyasını yükleme fonksiyonu.
    
    Parameters:
    -----------
    max_week : int, optional
        Yüklenecek maksimum hafta sayısı (varsayılan: 28)
    """
    # 1. Önce toplu dosyayı kontrol edelim
    try:
        df = pd.read_json("data/tff_super_lig_2425_1-28_maclar.json", lines=True)
        print("Veri toplu dosyadan yüklendi.")
        
        # Eğer istenen hafta sayısı 28'den azsa, verileri filtreleyelim
        if max_week < 28:
            # Burada veriyi haftalara göre filtreleme işlemi yapılabilir
            pass
            
        print(f"Toplam {len(df)} maç verisi mevcut.")
        return df
    except FileNotFoundError:
        print("Toplu veri dosyası bulunamadı, haftalık dosyaları kontrol ediyorum...")
    
    # 2. Haftalık dosyaları kontrol edelim
    all_matches = []
    hafta_sayisi = 0
    
    for week in range(1, max_week + 1):  # max_week dahil
        try:
            hafta_dosyasi = f"data/hafta_{week}_maclar.json"
            hafta_df = pd.read_json(hafta_dosyasi, lines=True)
            print(f"{week}. hafta verileri yüklendi.")
            all_matches.append(hafta_df)
            hafta_sayisi += 1
        except FileNotFoundError:
            print(f"{week}. hafta verisi bulunamadı.")
    
    if all_matches:
        print(f"Toplam {hafta_sayisi} hafta verisi yüklendi.")
        all_matches_df = pd.concat(all_matches, ignore_index=True)
        print(f"Toplam {len(all_matches_df)} maç verisi birleştirildi.")
        
        # Toplu veriyi kaydedelim
        os.makedirs("data", exist_ok=True)
        all_matches_df.to_json("data/tff_super_lig_2425_1-28_maclar.json", orient='records', lines=True)
        print("Birleştirilmiş veriler 'data/tff_super_lig_2425_1-28_maclar.json' dosyasına kaydedildi.")
        
        return all_matches_df
    
    # 3. Alternatif JSON dosyalarını kontrol et
    print("Haftalık veri dosyaları bulunamadı, alternatif dosyaları arıyorum...")
    try:
        # JSON dosyalarını bul - match_data.json ile biten dosyalar veya sofascore ile başlayan dosyalar
        json_files = [f for f in os.listdir("data") if f.endswith('_match_data.json') or f.startswith('sofascore')] if os.path.exists("data") else []
        
        if not json_files:
            json_files = [f for f in os.listdir() if f.endswith('_match_data.json') or f.startswith('sofascore')]
        
        if json_files:
            print(f"Bulunan dosyalar: {json_files}")
            # İlk bulunan dosyayı kullan
            df = pd.read_json(os.path.join("data" if os.path.exists("data") else "", json_files[0]))
            print(f"JSON dosyasından sütunlar: {df.columns.tolist()}")
            
            # Minimum gerekli sütunları kontrol et
            required_cols = ['home_team', 'away_team', 'home_score', 'away_score']
            
            # Alternatif sütun isimlerini kontrol et ve çevir
            alt_cols = {
                'home_team': ['home_team', 'home_name', 'homeTeam', 'homeTeamName'],
                'away_team': ['away_team', 'away_name', 'awayTeam', 'awayTeamName'],
                'home_score': ['home_score', 'home_score_ft', 'home_score_normaltime', 'homeScore'],
                'away_score': ['away_score', 'away_score_ft', 'away_score_normaltime', 'awayScore']
            }
            
            rename_dict = {}
            for target_col, alt_names in alt_cols.items():
                for alt_name in alt_names:
                    if alt_name in df.columns and alt_name != target_col:
                        rename_dict[alt_name] = target_col
                        break
            
            if rename_dict:
                df = df.rename(columns=rename_dict)
            
            # Gerekli sütunları kontrol et
            if all(col in df.columns for col in required_cols):
                print("Gerekli tüm sütunlar bulundu.")
                df = df[required_cols]  # Sadece gerekli sütunları alır
                
                # Boş değerleri doldur
                df['home_score'] = df['home_score'].fillna(0).astype(int)
                df['away_score'] = df['away_score'].fillna(0).astype(int)
                
                return df
            else:
                missing_cols = [col for col in required_cols if col not in df.columns]
                print(f"Eksik sütunlar: {missing_cols}")
                
    except Exception as e:
        print(f"Alternatif dosya yükleme hatası: {e}")
    
    # 4. Veriler bulunamadı, yeni veriler çekilmeli
    print("Yerel veri bulunamadı veya eksik. Yeni veri çekiliyor...")
    return get_match_data(max_week)