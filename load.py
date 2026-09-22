import duckdb
import os
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='load.log'
)

logger = logging.getLogger(__name__)

DATABASE = 'emissions.duckdb'


def load_vehicle_emissions(con):
    """Load the vehicle emissions CSV into DuckDB."""

    try:
        con.execute("""
            CREATE OR REPLACE TABLE vehicle_emissions AS
            SELECT *
            FROM read_csv_auto('data/vehicle_emissions.csv')
        """)

        count = con.execute("""
            SELECT COUNT(*)
            FROM vehicle_emissions
        """).fetchone()[0]

        print(f"vehicle_emissions raw row count: {count}")
        logger.info(f"vehicle_emissions raw row count: {count}")

    except Exception as e:
        print(f"Error loading vehicle emissions: {e}")
        logger.error(f"Error loading vehicle emissions: {e}")
        raise


def load_taxi_type(con, taxi_type):
    """Load all 12 months of 2024 data for one taxi type."""

    try:
        table_name = f"{taxi_type}_trips"

        # Start fresh each time load.py is run
        con.execute(f"DROP TABLE IF EXISTS {table_name}")
        logger.info(f"Dropped {table_name} if it already existed")

        for month in range(1, 13):
            month_string = f"{month:02d}"

            url = (
                "https://d37ci6vzurychx.cloudfront.net/"
                f"trip-data/{taxi_type}_tripdata_2024-{month_string}.parquet"
            )

            print(
                f"Loading {taxi_type} taxi data "
                f"for 2024-{month_string}..."
            )

            logger.info(
                f"Loading {taxi_type} taxi data "
                f"for 2024-{month_string}"
            )

            if month == 1:
                con.execute(f"""
                    CREATE TABLE {table_name} AS
                    SELECT *
                    FROM read_parquet('{url}')
                """)
            else:
                con.execute(f"""
                    INSERT INTO {table_name}
                    BY NAME
                    SELECT *
                    FROM read_parquet('{url}')
                """)

        count = con.execute(f"""
            SELECT COUNT(*)
            FROM {table_name}
        """).fetchone()[0]

        print(f"{table_name} raw row count: {count}")
        logger.info(f"{table_name} raw row count: {count}")

    except Exception as e:
        print(f"Error loading {taxi_type} taxi data: {e}")
        logger.error(f"Error loading {taxi_type} taxi data: {e}")
        raise


def print_statistics(con, table_name):
    """Print and log basic descriptive statistics for a taxi table."""

    try:
        stats = con.execute(f"""
            SELECT
                COUNT(*) AS total_trips,
                AVG(trip_distance) AS average_distance,
                MIN(trip_distance) AS minimum_distance,
                MAX(trip_distance) AS maximum_distance,
                AVG(passenger_count) AS average_passengers
            FROM {table_name}
        """).fetchone()

        message = (
            f"{table_name} statistics: "
            f"total trips = {stats[0]}, "
            f"average distance = {stats[1]}, "
            f"minimum distance = {stats[2]}, "
            f"maximum distance = {stats[3]}, "
            f"average passengers = {stats[4]}"
        )

        print(message)
        logger.info(message)

    except Exception as e:
        print(f"Error calculating statistics for {table_name}: {e}")
        logger.error(
            f"Error calculating statistics for {table_name}: {e}"
        )
        raise


def load_parquet_files():
    """Create the DuckDB database and load all required project data."""

    con = None

    try:
        # Connect to local DuckDB instance
        con = duckdb.connect(
            database=DATABASE,
            read_only=False
        )

        logger.info("Connected to DuckDB instance")

        # Load emissions lookup table
        load_vehicle_emissions(con)

        # Programmatically load both taxi types
        for taxi_type in ["yellow", "green"]:
            load_taxi_type(con, taxi_type)
            print_statistics(con, f"{taxi_type}_trips")

        print("\nLoading complete.")
        logger.info("All data loaded successfully")

    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(f"An error occurred: {e}")

    finally:
        if con is not None:
            con.close()
            logger.info("DuckDB connection closed")


if __name__ == "__main__":
    load_parquet_files()