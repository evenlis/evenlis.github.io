import csv
import json
from pathlib import Path

import pandas as pd


def read_csv(filename: str) -> pd.DataFrame:
    with open(Path("input").joinpath(filename)) as csv_file:
        return pd.read_csv(csv_file, sep=",", encoding="utf-8")


if __name__ == "__main__":
    codes_df = read_csv("utgiftskonti.csv")
    accounts_df = read_csv("regnskap_fon_barnehage.csv")
    codes = accounts_df[["KOSTRA-kode", "Beskrivelse"]].drop_duplicates(subset="KOSTRA-kode")
    codes["Beskrivelse"] = codes["Beskrivelse"].map(str.capitalize)
    print(f"{len(codes)} unique codes:")
    print(codes)
    with open("kostra_koder_i_regnskap.csv", "w+") as codes_file:
        codes.to_csv(codes_file, index=False, sep=";")
    relevant_codes = codes_df.loc[codes_df["Driftsutgift?"] == "y"]
    print(f"{len(relevant_codes)} relevante utgiftskonti:")
    print(relevant_codes)

    driftsutgifter_df = accounts_df.loc[accounts_df["KOSTRA-kode"].isin(relevant_codes["KOSTRA-kode"].tolist())]
    print(driftsutgifter_df)

    driftsutgifter_df["Verdi"] = driftsutgifter_df["Verdi"].str.replace(",", "").astype(int)
    tot = 0
    for year in driftsutgifter_df["År"].unique():
        print(f"{year}:")
        for entry in driftsutgifter_df.loc[driftsutgifter_df["År"] == year].itertuples():
            print(entry)

        sum = driftsutgifter_df.loc[driftsutgifter_df["År"] == year]["Verdi"].sum()

        tot += sum
        print(f"sum: {sum}")
    print(f"total: {tot}")
    number_of_years = len(driftsutgifter_df["År"].unique())
    print(f"gjennomsnitt ({number_of_years} år): {round(tot / number_of_years, ndigits=1)}")
