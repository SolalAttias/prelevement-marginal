import asyncio
import ssl
from typing import Iterable

import aiohttp
import pandas as pd
from tqdm import tqdm

api_url = "https://mon-entreprise.urssaf.fr/api/v1/evaluate"
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


async def get_response(session, remuneration: int, api_url: str):
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
    max_retries = 5  # Maximum number of retries for each request
    retry_delay = 1  # Initial delay between retries in seconds
    for attempt in range(max_retries):
        try:
            async with session.post(
                api_url,
                json=request,
                ssl=ssl_context,
                proxy="http://proxy.univ-evry.fr:3128",
            ) as response:
                if response.status == 429:  # HTTP status code for rate limiting
                    retry_after = retry_delay  # Default to 1 second if not provided
                    await asyncio.sleep(retry_after)
                    continue  # Retry the request
                response_json = await response.json()
                expressions = [
                    a.get("nodeValue", pd.NA) for a in response_json["evaluate"]
                ]
                return {
                    "coût total employeur": expressions[0],
                    "salaire brut": expressions[1],
                    "rémunération avant impôt": expressions[2],
                    "rémunération après impôt": expressions[3],
                }
        except aiohttp.client_exceptions.ServerDisconnectedError:
            if attempt < max_retries - 1:  # Don't sleep after the last attempt
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                raise  # Re-raise the exception if max retries reached


async def main(remunerations: Iterable[int]):
    async with aiohttp.ClientSession() as session:
        tasks = [
            get_response(session, remuneration, api_url)
            for remuneration in remunerations
        ]
        responses = []
        for f in tqdm(asyncio.as_completed(tasks), total=len(tasks)):
            response = await f
            responses.append(response)
        return responses


# Running the main function with a range of remunerations
responses = asyncio.run(main(list(range(1000, 2000, 10))))
df = pd.DataFrame(responses)
df.to_csv("df2.csv")
