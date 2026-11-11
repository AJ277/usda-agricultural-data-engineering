# Import actual USDA NASS Quick Stats data

**Source:** [USDA NASS Quick Stats](https://www.nass.usda.gov/Quick_Stats/) → Quick Stats searchable database → export **Spreadsheet (CSV)**. The official USDA website supports exports without writing a custom API client. The exported records are actual USDA data; the bundled synthetic fixture is not.

## Recommended first export

Choose a narrowly defined query so that the data are comparable:

- **Source:** Survey (if shown)
- **Sector:** Crops
- **Group:** Field crops
- **Commodity:** CORN (first export; repeat for SOYBEANS and WHEAT if practical)
- **Category / statistic:** YIELD and/or PRODUCTION (if interface requires one at a time, download each and combine rows only after checking matching column headers)
- **Geography level:** State
- **Geography:** Iowa, Illinois, Nebraska, Kansas (or All States if available)
- **Frequency:** Annual
- **Years:** 2020–2025 (2026 annual figures may not yet be final)
- **Domain:** TOTAL
- **Class/practice/utilization:** Select all-inclusive crop definitions, not competing subcategories
- Export results as **CSV / Spreadsheet**; retain original file unchanged as evidence of source.

**Note:** Quick Stats menus can vary with each selected commodity. If no results are returned, broaden geography or use one commodity and one statistic category per export.

## Transfer the download into Ubuntu WSL

In Ubuntu, from `~/projects/USDA_Agricultural_Data_Engineering`:

```bash
mkdir -p data/raw
cp /mnt/c/Users/andyj/Downloads/<actual-usda-download-name>.csv data/raw/usda_quickstats_original.csv
```

Replace `<actual-usda-download-name>` with the actual filename visible in Windows Downloads. Do **not** rename a PDF, XLSX, or HTML file to `.csv`.

## Validate first (no Spark needed)

```bash
source .venv/bin/activate
python -m src.preflight --csv data/raw/usda_quickstats_original.csv
```

The preflight step writes `output/real_usda_preflight.json` and `data/raw/usda_state_crop_clean.csv` if it finds unambiguous observations. If the preflight reports **conflicting metric keys**, review the JSON examples and narrow Quick Stats filters for source, crop class, irrigation practice, and reporting period; do not average competing definitions.

## Run real data through Spark / Delta Lake

```bash
python -m src.pipeline --source real --csv data/raw/usda_state_crop_clean.csv
python -m unittest discover -s tests -v
```

Expected counts depend on your official export. **Do not expect the synthetic 147/144/144 counts** from real USDA data. Outputs appear in `output/real/{bronze,silver,gold,trend_csv}`.

## Read the results

The `trend_csv` directory contains one `part-*.csv` with yearly state/crop production or yield and year-over-year percentage change only when consecutive years exist. The Silver and Gold Delta tables are locally stored under the other output directories.

Do not compare YIELD (e.g. `BU / ACRE`) with PRODUCTION (`BU`). Suppressed `(D)` values mean withheld data, not zeros. Filter and report the measurement units, class, reporting source and observation period when presenting findings.

## Credit and citations

USDA National Agricultural Statistics Service, *Quick Stats* (accessed on the actual export date), https://www.nass.usda.gov/Quick_Stats/ . Include the export filter selections, date retrieved, and any excluded or suppressed rows in your final report.
