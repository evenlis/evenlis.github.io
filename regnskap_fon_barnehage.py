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
    by_year = accounts_df.groupby("År")
    for y in by_year:
        print(y)
    relevant_codes = codes_df.loc[codes_df["Driftskonto?"] == "y"]
    print(relevant_codes)

    driftsutgifter_df = accounts_df.loc[accounts_df["KOSTRA-kode"].isin(relevant_codes["Kode"].tolist())]
    print(driftsutgifter_df)

    driftsutgifter_df["Verdi"] = driftsutgifter_df["Verdi"].str.replace(",", "").astype(int)
    for year in driftsutgifter_df["År"].unique():
        print(f"{year}:")
        for entry in driftsutgifter_df.loc[driftsutgifter_df["År"] == year].itertuples():
            print(entry)

        sum = driftsutgifter_df.loc[driftsutgifter_df["År"] == year]["Verdi"].sum()
        print(sum)
