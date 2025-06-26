import os
import json
from hashlib import md5
from metaheuristiken import genetic_mh

# Verzeichnisse
INSTANZEN_VERZEICHNIS = os.path.join("data", "input")
OUTPUT_VERZEICHNIS = os.path.join("data", "output")
CONFIG_VERZEICHNIS = "config"

def lade_konfiguration_aus_json(config_json):
    """
    Lädt Konfigurationsparameter aus einer JSON-String
    """
    return json.loads(config_json)

def lade_daten_aus_json(dateipfad):
    """
    Lädt Instanzdaten aus einer JSON-Datei
    """
    try:
        with open(dateipfad, 'r', encoding='utf-8') as f:
            tmp_eingabe_daten = json.load(f)
    except Exception as e:
        raise RuntimeError(f"Fehler beim Laden der Instanzdatei: {e}")
    return tmp_eingabe_daten
#%%
def main():
    eingabe_daten = lade_daten_aus_json(os.path.join(INSTANZEN_VERZEICHNIS, "example_evacuation_data.json"))

    CONFIG_DATEI = os.path.join(CONFIG_VERZEICHNIS, 'genetic_mh_config.json')

    with open(CONFIG_DATEI, 'r', encoding='utf-8') as f:
        file_content = ''.join(f.readlines())
        konfigurations_daten = lade_konfiguration_aus_json(file_content)
        config_hash = md5(file_content.encode('utf-8'))

    DURCHLAUF_VERZEICHNIS = os.path.join(OUTPUT_VERZEICHNIS, f'genetic_mh_xample_instanz_{config_hash}')

    mh = []
    mh.append(
        genetic_mh.GeneticMetaheuristik(
            eingabe_daten,
            konfigurations_daten,
            DURCHLAUF_VERZEICHNIS
        )
    )

if __name__ == "__main__":
    main()
