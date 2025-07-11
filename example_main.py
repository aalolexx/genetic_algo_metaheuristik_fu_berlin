import os
import json
from hashlib import md5
from metaheuristiken.genetic_mh.GeneticMetaheuristik import GeneticMetaheuristik
from metaheuristiken.genetic_mh.PlotUtils import plot_losses, plot_routes_timeline, plot_people_on_street, plot_loss_dict
import time

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
        config_hash = md5(file_content.encode('utf-8')).hexdigest()

    DURCHLAUF_VERZEICHNIS = os.path.join(OUTPUT_VERZEICHNIS, f'genetic_mh_xample_instanz_{config_hash}_{time.time()}')

    mh = []
    mh.append(
        GeneticMetaheuristik(
            eingabe_daten,
            konfigurations_daten,
            DURCHLAUF_VERZEICHNIS
        )
    )

    # todo remove the follinwg, just for local testing
    mh[0].initialisiere()
    for i in range(200):
        print(f"ITERATION {i}/200")
        mh[0].iteriere()
        mh[0].speichere_zwischenergebnis()
    

    best_solution = mh[0].bewerte_loesung()
    plot_losses(DURCHLAUF_VERZEICHNIS)
    plot_loss_dict(DURCHLAUF_VERZEICHNIS)
    plot_routes_timeline(DURCHLAUF_VERZEICHNIS, best_solution.routes)
    plot_people_on_street(DURCHLAUF_VERZEICHNIS, best_solution.routes, mh[0].max_street_capacity)


if __name__ == "__main__":
    main()
