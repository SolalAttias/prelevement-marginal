import pandas as pd
from tqdm import tqdm

from marginal_prel.utils import clean_df, get_response_urssaf


def get_response_temps_plein(remuneration: int):
    request = {
        "situation": {
            "entreprise . imposition": "non",
            "entreprise . catégorie juridique": "''",
            "impôt . méthode de calcul": "'barème standard'",
            "salarié . activité partielle": "non",
            "salarié . contrat": "'CDI'",
            "salarié . rémunération . net . payé après impôt": remuneration,
            "dirigeant": "non",
        },
        "expressions": [
            "salarié . coût total employeur",
            "salarié . contrat . salaire brut",
            "salarié . rémunération . net . à payer avant impôt",
            "salarié . rémunération . net . payé après impôt",
        ],
    }
    return get_response_urssaf(request)

def main() -> None:
    print("Réponses temps plein, partie 1...")
    responses_0 = [get_response_temps_plein(n) for n in tqdm(range(1300, 4500, 10))]
    print("Réponses temps plein, partie 2...")
    responses_1 = [get_response_temps_plein(n) for n in tqdm(range(4500, 15000, 200))]

    print("Réponses temps plein acquises, calculs et sauvegarde...")
    responses = responses_0 + responses_1
    df = pd.DataFrame(responses)
    df.to_csv("raw_temps_plein.csv", index=False)
    clean_df(df).to_csv("clean_temps_plein.csv", index=False)

    print("Fini !")


if __name__ == "__main__":
    main()
