from time import sleep

import pandas as pd
import requests

API_URL = "https://mon-entreprise.urssaf.fr/api/v1/evaluate"


def get_response_urssaf(request: dict):
    sleep(0.3)
    response = requests.post(
        API_URL, json=request, verify="mon-entreprise-urssaf-fr-chain.pem"
    )
    expressions = [a.get("nodeValue", pd.NA) for a in response.json()["evaluate"]]
    return {
        "coût total employeur": expressions[0],
        "salaire brut": expressions[1],
        "rémunération avant impôt": expressions[2],
        "rémunération après impôt": expressions[3],
    }


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    clean_df = df[~df.isna().any(axis=1)].reset_index(drop=True)
    clean_df["cout marginal employeur"] = (clean_df - clean_df.shift(1))[
        "coût total employeur"
    ]
    clean_df["net apres impots marginal"] = (clean_df - clean_df.shift(1))[
        "rémunération après impôt"
    ]
    clean_df = clean_df.iloc[1:]
    clean_df = clean_df.astype(float)
    clean_df["tx prelevement marginal"] = (
        1 - clean_df["net apres impots marginal"] / clean_df["cout marginal employeur"]
    ).round(2)
    clean_df["tx prelevement total"] = 1 - clean_df[
        "rémunération après impôt"
    ] / clean_df["coût total employeur"].round(3)
    clean_df["revenu net imposable"] = clean_df["rémunération avant impôt"] * 12 * 0.9
    return clean_df
