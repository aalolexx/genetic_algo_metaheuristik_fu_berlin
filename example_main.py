import os
import json
from hashlib import md5
from metaheuristiken.geneticMetaheuristic.GeneticMetaheuristik import GeneticMetaheuristik
from metaheuristiken.geneticMetaheuristic.PlotUtils import plot_losses, plot_routes_timeline, plot_people_on_street, plot_loss_dict, plot_generation_birthtype_loss, plot_pr_usage_vs_capacity
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
    DATASET = "middle"

    eingabe_daten = lade_daten_aus_json(os.path.join(INSTANZEN_VERZEICHNIS, f"{DATASET}_evacuation_data.json"))

    CONFIG_DATEI = os.path.join(CONFIG_VERZEICHNIS, f'geneticMetaheuristic_{DATASET}_config.json')

    with open(CONFIG_DATEI, 'r', encoding='utf-8') as f:
        file_content = ''.join(f.readlines())
        konfigurations_daten = lade_konfiguration_aus_json(file_content)
        config_hash = md5(file_content.encode('utf-8')).hexdigest()

    DURCHLAUF_VERZEICHNIS = os.path.join(OUTPUT_VERZEICHNIS, f'geneticMetaheuristic_small_{config_hash}_{int(time.time())}')
    DURCHLAUF_VERZEICHNIS = os.path.join(OUTPUT_VERZEICHNIS, f'geneticMetaheuristic_{DATASET}_{config_hash}_{int(time.time())}')

    mh = []
    mh.append(
        GeneticMetaheuristik(
            eingabe_daten,
            konfigurations_daten,
            DURCHLAUF_VERZEICHNIS
        )
    )

    # todo remove the follinwg, just for local testing
    patience = mh[0].konfiguration["patience"]
    no_improvement_counter = 0
    max_iterations = mh[0].konfiguration["max_iterationen"]
    best_loss = float("inf")

    start = time.time()
    mh[0].initialisiere()
    for i in range(max_iterations):
        end = time.time()
        if end - start > mh[0].konfiguration["max_laufzeit"]:
            print("Maximum runtime was reached!")
            break

        print(f"ITERATION {i+1}/{max_iterations}")
        mh[0].iteriere()
        mh[0].speichere_zwischenergebnis()

        if mh[0].bewerte_loesung() == 0:
            print("REACHED OPTIMAL SOLUTION")
            break

        if mh[0].bewerte_loesung() < best_loss:
            no_improvement_counter = 0
            best_loss = mh[0].bewerte_loesung()
        else:
            no_improvement_counter += 1
        
        if no_improvement_counter > patience:
            print("STOPPING DUE TO NO IMPROVEMENT")
            break
        # manually stop after iteration by creating this specific file
        if "stop.py" in os.listdir(os.getcwd()):
            break

    best_loesung_json, bester_wert = mh[0].gebe_endloesung_aus()

    print(best_loesung_json)
    print(bester_wert)


    # Out GeneticAlgorithm specific export functions
    best_solution = mh[0].get_best_solution()
    best_solution.export_as_json(DURCHLAUF_VERZEICHNIS)
    plot_losses(DURCHLAUF_VERZEICHNIS)
    plot_loss_dict(DURCHLAUF_VERZEICHNIS)
    plot_routes_timeline(DURCHLAUF_VERZEICHNIS, best_solution.routes)
    plot_people_on_street(DURCHLAUF_VERZEICHNIS, best_solution.routes, mh[0].max_street_capacity)
    plot_pr_usage_vs_capacity(DURCHLAUF_VERZEICHNIS, best_solution.routes, mh[0].pr_list)
    plot_generation_birthtype_loss(DURCHLAUF_VERZEICHNIS)
    plot_generation_birthtype_loss(DURCHLAUF_VERZEICHNIS, top_y=3)

if __name__ == "__main__":
    main()
