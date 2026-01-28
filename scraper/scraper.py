import re
import time
import pandas as pd
import sqlite3
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

# ----------------------------
# CHEMIN DB
# ----------------------------
DB_PATH = os.path.join(os.path.dirname(__file__), "data/logements.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# ----------------------------
# FONCTIONS UTILES
# ----------------------------
def normalize_type(type_bien): 
    t = type_bien.upper() if type_bien else ""
    if "STUDIO" in t: return "STUDIO"
    if "T1" in t: return "T1"
    if "T2" in t: return "T2"
    if "T3" in t: return "T3"
    return None

def extract_surface(text):
    if not text:
        return None
    text = text.lower().replace(",", ".").replace("m²", "m2")
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:à\s*(\d+(?:\.\d+)?))?\s*m2", text)
    if match:
        surface = (float(match.group(1)) + float(match.group(2))) / 2 if match.group(2) else float(match.group(1))
        return round(surface, 2) if surface <= 80 else None
    return None

def get_connection():
    return sqlite3.connect(DB_PATH)

def create_table():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS logements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT,
            prix INTEGER,
            surface REAL,
            prix_m2 REAL,
            type_bien TEXT,
            ville TEXT,
            site_source TEXT,
            image TEXT,
            url TEXT,
            date_scraping TEXT
        )
    """)
    conn.commit()
    conn.close()

# ----------------------------
# SCRAPING IMMOJEUNE
# ----------------------------
def scrape_immojeune_zone(url_zone, ville_nom):
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 15)
    driver.get(url_zone)

    # Accepter les cookies si besoin
    try:
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-cookiefirst-action='accept']"))).click()
    except:
        pass

    # Attendre que les cartes soient présentes
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.card.col")))

    # Scroll pour charger toutes les annonces
    for _ in range(4):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    items = driver.find_elements(By.CSS_SELECTOR, "div.card.col")
    data_zone = []

    for item in items:
        try:
            # Titre et URL
            titre_tag = item.find_element(By.CSS_SELECTOR, "p.title a")
            titre = titre_tag.text.strip()
            url_annonce = titre_tag.get_attribute("href")

            # Image
            try:
                image = item.find_element(By.CSS_SELECTOR, ".avatar img").get_attribute("src")
            except:
                image = None

            # Type de bien
            type_bien = None
            badges = item.find_elements(By.CSS_SELECTOR, "span.badge")
            for badge in badges:
                type_bien = normalize_type(badge.text)
                if type_bien:
                    break

            prix = surface = None

            # Boucle sur tous les <p> pour extraire surface et prix
            for p in item.find_elements(By.TAG_NAME, "p"):
                txt = p.text.replace("\n", " ").replace("\r", " ").strip()

                # Surface
                if not surface:
                    surface = extract_surface(txt)

                # Prix
                if not prix:
                    # Cherche le prix en euros même si texte sale
                    m = re.search(r"(\d[\d\s]*)\s*€", txt)
                    if m:
                        prix_str = m.group(1).replace(" ", "")
                        try:
                            prix = int(prix_str)
                        except:
                            prix = None

            # Ajouter uniquement si on a tout : prix, surface, type
            if prix and surface and type_bien:
                data_zone.append((
                    titre,
                    prix,
                    surface,
                    round(prix / surface, 2),
                    type_bien,
                    ville_nom,
                    "ImmoJeune",
                    image,
                    url_annonce,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))

        except Exception as e:
            # Ignore les erreurs sur une carte
            print("Erreur sur une annonce :", e)
            continue

    driver.quit()
    return data_zone


# ----------------------------
# SCRAPING STUDAPART
# ----------------------------
def scrape_studapart_zone(url_zone, ville_nom):
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 20)
    driver.get(url_zone)
    try: wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".didomi-continue-without-agreeing"))).click()
    except: pass

    for _ in range(8):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    items = driver.find_elements(By.CSS_SELECTOR, "a.AccomodationBlock")
    data_zone = []

    for item in items:
        try:
            titre = item.find_element(By.CSS_SELECTOR, "p.AccomodationBlock_title").text.strip()
            url_annonce = item.get_attribute("href")

            # Image
            try:
                style = item.find_element(By.CSS_SELECTOR, ".SliderSimple_imageBackground").get_attribute("style")
                image = re.search(r'url\("(.*?)"\)', style).group(1)
            except:
                image = None

            # Prix
            prix = None
            try:
                prix_text = item.find_element(By.CSS_SELECTOR, "p.ft-l b").text
                prix_text = prix_text.replace("€","").replace(" ","")
                if prix_text != "0":
                    prix = int(prix_text)
            except: pass

            # Surface
            surface = None
            try:
                surface_text = item.find_element(By.CSS_SELECTOR, "div.AccomodationBlock_location.mb-10").text
                surface = extract_surface(surface_text)
            except: pass

            # Type de bien
            type_bien = None
            if "studio" in titre.lower() or "studio" in surface_text.lower():
                type_bien = "STUDIO"
            elif "1 chambre" in surface_text.lower():
                type_bien = "T1"
            elif "2 chambres" in surface_text.lower():
                type_bien = "T2"
            elif "3 chambres" in surface_text.lower():
                type_bien = "T3"

            if prix and surface and type_bien:
                data_zone.append((titre, prix, surface, round(prix/surface,2), type_bien, ville_nom, "Studapart", image, url_annonce, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        except:
            continue

    driver.quit()
    return data_zone

# ----------------------------
# LISTE DES VILLES
# ----------------------------
liste_immojeune = [
    ("https://www.immojeune.com/logement-etudiant/paris-75.html", "Paris"),
    ("https://www.immojeune.com/logement-etudiant/marseille-13.html", "Marseille"),
    ("https://www.immojeune.com/logement-etudiant/lyon-69.html", "Lyon"),
    ("https://www.immojeune.com/logement-etudiant/bordeaux-33.html", "Bordeaux")
]
liste_studapart = [
    ("https://www.studapart.com/fr/logement-etudiant-paris", "Paris"), 
    ("https://www.studapart.com/fr/logement-etudiant-bordeaux", "Bordeaux"),
    ("https://www.studapart.com/fr/logement-etudiant-lille", "Lille"),
    ("https://www.studapart.com/fr/logement-etudiant-lyon", "Lyon"),
    ("https://www.studapart.com/fr/logement-etudiant-toulouse", "Toulouse"),
    ("https://www.studapart.com/fr/logement-etudiant-marseille", "Marseille")
]

# ----------------------------
# EXECUTION DU SCRAPING
# ----------------------------
create_table()
toutes_donnees = []
for url, ville in liste_immojeune: toutes_donnees.extend(scrape_immojeune_zone(url, ville))
for url, ville in liste_studapart: toutes_donnees.extend(scrape_studapart_zone(url, ville))

# ----------------------------
# INSERTION DANS SQLITE
# ----------------------------
conn = get_connection()
c = conn.cursor()
c.execute("DELETE FROM logements")
c.executemany("""
    INSERT INTO logements (titre, prix, surface, prix_m2, type_bien, ville, site_source, image, url, date_scraping)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", toutes_donnees)
conn.commit()
conn.close()

print("✅ Scraping terminé et base SQLite mise à jour")
