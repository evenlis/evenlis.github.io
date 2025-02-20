import json
from collections.abc import Sequence
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

import requests


@dataclass
class Selection:
    filter: str
    values: Sequence[str]


@dataclass
class Query:
    code: str
    selection: Selection


class KostraQueryProvider:
    @cached_property
    def barnehage_leke_og_oppholdsareal_alle_kommuner(self):
        with open(
            Path("queries").joinpath("kostra").joinpath("table_12055_leke_og_oppholdsareal_alle_kommuner.json")
        ) as json_file:
            return json.load(json_file)

    @cached_property
    def barnehage_barn_per_ansatt(self):
        with open(Path("queries").joinpath("kostra").joinpath("table_13502_barn_per_ansatt.json")) as json_file:
            return json.load(json_file)

    @cached_property
    def barnehage_kostnad_per_barn(self):
        with open(
            Path("queries").joinpath("kostra").joinpath("table_13502_kostnad_per_barnehagebarn_alle_kommuner.json")
        ) as json_file:
            return json.load(json_file)

    @cached_property
    def barnehage_kostnad_prosent_driftsutgifter(self):
        with open(
            Path("queries")
            .joinpath("kostra")
            .joinpath("table_13502_kostnad_prosent_totale_driftsutgifter_alle_kommuner.json")
        ) as json_file:
            return json.load(json_file)


@dataclass
class KostraService:
    base_url: str

    def perform_query(
        self,
        table: str,
        query: dict,
    ) -> dict:
        response = requests.post(
            url=f"{self.base_url}/{table}",
            headers={
                "Content-Type": "application/json",
            },
            json=query,
        )
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            print("=== query ===")
            request_body = json.loads(response.request.body.decode("utf-8"))
            print(json.dumps(request_body, indent=2))
            return f"error performing query: {err}"


if __name__ == "__main__":
    kostra_svc = KostraService("https://data.ssb.no/api/v0/no/table")
    qp = KostraQueryProvider()
    play_areas = kostra_svc.perform_query(
        table=12055,
        query=qp.barnehage_leke_og_oppholdsareal_alle_kommuner,
    )
    children_per_employee = kostra_svc.perform_query(
        table=13502,
        query=qp.barnehage_barn_per_ansatt,
    )
    cost_per_child = kostra_svc.perform_query(
        table=13502,
        query=qp.barnehage_kostnad_per_barn,
    )
    grouped_by_municipality = {
        kommune_nr: cost_per_child["value"][index]
        for kommune_nr, index in cost_per_child["dimension"]["KOKkommuneregion0000"]["category"]["index"].items()
    }
    sorted_by_cost = dict(sorted(grouped_by_municipality.items(), key=lambda x: x[1]))
    idx = 1
    for kommune_nr, value in sorted_by_cost.items():
        kommune_navn = cost_per_child["dimension"]["KOKkommuneregion0000"]["category"]["label"][kommune_nr]
        print(f"{idx: <4}{kommune_navn} ({kommune_nr}): {value}")
        idx += 1
