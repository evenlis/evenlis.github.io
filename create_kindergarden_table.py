import csv
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
    readable_field_mapping = {
        "orgnr": "Orgnr",
        "name": "Navn",
        "oppfyller_pedagognorm": "Oppfyller pedagognorm",
        "foreldreundersokelsen": "Foreldreundersøkelsen",
        "antallBarn": "Antall barn",
        "antallBarnPerAnsatt": "Antall barn per ansatt",
        "antallBarnPerBarnehagelaerer": "Antall barn per barnehagelærer",
        "andelAnsatteBarnehagelarer": "Andel ansatte per barnehagelærer",
        "lekeOgOppholdsarealPerBarn": "Leke- og oppholdsareal per barn",
    }
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

        parent_survey_average = sum(
            filter(
                None,
                [
                    kindergarden_indicators.get(key, 0)
                    for key in indicators_parent_survey
                    if key != "foreldreundersokelsenSvarprosent"
                ],
            )
        ) / len(indicators_parent_survey)
        data.append(
            {
                "orgnr": org_no,
                "name": name,
                "oppfyller_pedagognorm": "Ja" if oppfyller_pedagognorm == "Oppfyller pedagognormen" else "Nei",
                "foreldreundersokelsen": round(parent_survey_average, ndigits=1),
            }
            | kindergarden_indicators
        )

    print(json.dumps(data, indent=2))
    with open("docs/_data/barnehager_sammenligning.csv", "w+", newline="") as csvfile:
        fieldnames = [
            "orgnr",
            "name",
            "oppfyller_pedagognorm",
            "foreldreundersokelsen",
            *indicator_selection,
            # *indicators_parent_survey,
        ]
        csv.writer(csvfile).writerow([readable_field_mapping[field] for field in fieldnames])
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        data.sort(key=lambda x: x["foreldreundersokelsen"], reverse=True)
        for kindergarden in data:
            csv_data = {key: kindergarden[key] for key in fieldnames}
            writer.writerow(csv_data)
