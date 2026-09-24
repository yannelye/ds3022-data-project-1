# DS 3022 Data Project 1
## NYC Taxi CO2 Emissions Pipeline

This project builds a data pipeline to analyze CO2 emissions from 2024 NYC Yellow and Green taxi trips. The pipeline uses Python and DuckDB to load, clean, transform, and analyze the taxi data.

## Pipeline

The project is divided into four main stages:

### 1. load.py

Loads all 12 months of 2024 Yellow and Green taxi trip data into DuckDB.

It creates three tables:

- `yellow_trips`
- `green_trips`
- `vehicle_emissions`

The taxi files are loaded programmatically by looping through the months instead of writing a separate command for every file.

### 2. clean.py

Cleans both taxi datasets by:

- Removing duplicate trips
- Removing trips with 0 passengers
- Removing trips with 0 miles
- Removing trips longer than 100 miles
- Removing trips longer than 86,400 seconds

Verification queries are run after cleaning to confirm that each invalid condition has a count of zero.

### 3. transform.py

Adds the following variables to the Yellow and Green taxi tables:

- `trip_co2_kgs`
- `avg_mph`
- `hour_of_day`
- `day_of_week`
- `week_of_year`
- `month_of_year`

CO2 emissions are calculated using `trip_distance` and a real-time lookup of `co2_grams_per_mile` from the `vehicle_emissions` table rather than a hard-coded emissions value.

### 4. analysis.py

Analyzes CO2 emissions for Yellow and Green taxis and reports:

- Largest single carbon-producing trip
- Heaviest and lightest hour of day on average
- Heaviest and lightest day of week on average
- Heaviest and lightest week of year on average
- Heaviest and lightest month of year on average

The script also creates `co2_by_month.png`, which compares monthly CO2 totals for Yellow and Green taxis.

## How to Run

Install the required Python packages:

```bash
python -m pip install -r requirements.txt
```

Run the entire pipeline with one command:

```bash
python run_pipeline.py
```

The pipeline runs the scripts in this order:

1. `load.py`
2. `clean.py`
3. `transform.py`
4. `analysis.py`

Each script can also be run individually if needed.

## Design Decisions

Yellow and Green taxi trips are stored in separate tables because their source data use slightly different column names. Keeping them separate also makes it easier to compare the two cab types during analysis.

The CO2 calculation uses the `vehicle_emissions` lookup table so that emissions values are retrieved dynamically instead of being hard-coded.

DuckDB is used for loading, cleaning, transformation, and analysis because it can efficiently work with the full 2024 taxi dataset and Parquet files.

The monthly CO2 visualization uses separate Y-axes for Yellow and Green taxis because Yellow taxi totals are much larger than Green taxi totals. This makes the monthly patterns for both cab types easier to see.

## Output

The final visualization is saved as:

`co2_by_month.png`

Parquet files, DuckDB database files, virtual environments, and log files are excluded from Git using `.gitignore`. 

## AI Assistance

I used ChatGPT and Claude as support tools during this project to help troubleshoot errors, fix portions of code, and better understand some of the Python and DuckDB syntax. I reviewed and tested the final code to make sure the pipeline worked correctly. 