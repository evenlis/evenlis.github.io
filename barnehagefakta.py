import json
from collections.abc import Callable
from dataclasses import dataclass

import requests


@dataclass
class NasjonaltBarnehageregisterService:
    base_url: str

    def select_kindergarden_attributes(self, kindergarden: dict, attributes: list[str]):
        return {key: kindergarden["data"][key] for key in attributes}

    def filter_kindergardens(
        self,
        kindergardens: list[dict],
        match_criteria: Callable[[dict], bool],
    ) -> list[dict]:
        return [kindergarden for kindergarden in kindergardens if match_criteria(kindergarden)]

    def active_municipal_kindergarden(kindergarden: dict) -> list[dict]:
        kommunal_barnehage_id = "19"
        offentlig_barnehage_id = "18"
        ordinaer_barnehage_id = "31"
        privat_barnehage_id = "20"
        return all(
            [
                kindergarden["data"]["ErAktiv"],
                kommunal_barnehage_id in map(lambda bhg: bhg["Id"], kindergarden["data"]["Barnehagekategorier"]),
            ]
        )

    def get_barnehager_i_kommune(
        self,
        kommune_nr: str,
        attributes: list[str] = None,
    ) -> list[dict]:
        response = requests.get(f"{self.base_url}/enheter/kommune/{kommune_nr}")
        response.raise_for_status()
        result = [
            {"org_nr": kindergarden["Organisasjonsnummer"], "data": kindergarden}
            for kindergarden in response.json()["EnhetListe"]
        ]
        municipal = self.filter_kindergardens(
            result,
            match_criteria=NasjonaltBarnehageregisterService.active_municipal_kindergarden,
        )
        if attributes:
            return [self.select_kindergarden_attributes(kindergarden, attributes) for kindergarden in municipal]
        return municipal


if __name__ == "__main__":
    nasjonalt_barnehageregister_service = NasjonaltBarnehageregisterService(
        base_url="https://data-nbr.udir.no/v4",
    )
    tonsberg_kommune_nr = "3905"
    barnehage_attributes = [
        "Navn",
        "FulltNavn",
        "ErAktiv",
        "ErInaktivIBasil",
        "Barnehagekategorier",
    ]
    print(
        json.dumps(
            nasjonalt_barnehageregister_service.get_barnehager_i_kommune(
                tonsberg_kommune_nr,
                attributes=barnehage_attributes,
            ),
            indent=2,
        )
    )
