import json

from barnehagefakta import BarnehagefaktaService, NasjonaltBarnehageregisterService

if __name__ == "__main__":
    nasjonalt_barnehageregister_service = NasjonaltBarnehageregisterService(
        base_url="https://data-nbr.udir.no/v4",
    )
    barnehagefakta_service = BarnehagefaktaService(
        base_url="https://barnehagefakta.no/api",
    )
    tonsberg_kommune_nr = "3905"
    barnehage_attributes = [
        "Navn",
        "FulltNavn",
        "ErAktiv",
        "ErInaktivIBasil",
        "Barnehagekategorier",
    ]
    municipal_kindergardens_tonsberg = nasjonalt_barnehageregister_service.get_barnehager_i_kommune(
        tonsberg_kommune_nr,
        attributes=barnehage_attributes,
    )
    indicator_selection = [
        "antallBarn",
        "antallBarnPerAnsatt",
        "antallBarnPerBarnehagelaerer",
        "andelAnsatteBarnehagelarer",
        "lekeOgOppholdsarealPerBarn",
    ]
    indicators_parent_survey = [
        "foreldreundersokelsenUteOgInneMiljo",
        "foreldreundersokelsenBarnetsUtvikling",
        "foreldreundersokelsenBarnetsTrivsel",
        "foreldreundersokelsenInformasjon",
        "foreldreundersokelsenTilfredshet",
        "foreldreundersokelsenSvarprosent",
    ]
    data = []
    for kindergarden in municipal_kindergardens_tonsberg:
        kindergarden_data = barnehagefakta_service.get_barnehage(kindergarden["org_nr"])
        org_no = kindergarden_data["orgnr"]
        name = kindergarden_data["navn"]
        kindergarden_indicators = {
            key: kindergarden_data["indikatorDataBarnehage"][key]
            for key in indicator_selection + indicators_parent_survey
            if key in kindergarden_data["indikatorDataBarnehage"]
        }
        municipality_indicators = kindergarden_data["indikatorDataKommune"]
        oppfyller_pedagognorm = kindergarden_data["oppfyllerPedagognorm"]

        data.append(
            {
                "orgnr": org_no,
                "name": name,
                "oppfyller_pedagognorm": oppfyller_pedagognorm,
                "indicators": kindergarden_indicators,
            }
        )

    print(json.dumps(data, indent=2))
