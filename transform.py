import duckdb
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='transform.log'
)

logger = logging.getLogger(__name__)

DATABASE = 'emissions.duckdb'


def transform_table(con, taxi_type):
    """Add and calculate the required transformations for one taxi table."""

    table = f"{taxi_type}_trips"

    if taxi_type == "yellow":
        pickup = "tpep_pickup_datetime"
        dropoff = "tpep_dropoff_datetime"
    else:
        pickup = "lpep_pickup_datetime"
        dropoff = "lpep_dropoff_datetime"

    vehicle = f"{taxi_type}_taxi"

    try:
        # Add the six required columns
        con.execute(f"""
            ALTER TABLE {table} ADD COLUMN IF NOT EXISTS trip_co2_kgs DOUBLE;
            ALTER TABLE {table} ADD COLUMN IF NOT EXISTS avg_mph DOUBLE;
            ALTER TABLE {table} ADD COLUMN IF NOT EXISTS hour_of_day INTEGER;
            ALTER TABLE {table} ADD COLUMN IF NOT EXISTS day_of_week INTEGER;
            ALTER TABLE {table} ADD COLUMN IF NOT EXISTS week_of_year INTEGER;
            ALTER TABLE {table} ADD COLUMN IF NOT EXISTS month_of_year INTEGER;
        """)

        # Calculate all six transformations
        con.execute(f"""
            UPDATE {table}
            SET
                trip_co2_kgs = trip_distance * (
                    SELECT co2_grams_per_mile
                    FROM vehicle_emissions
                    WHERE vehicle_type = '{vehicle}'
                ) / 1000.0,

                avg_mph = CASE
                    WHEN date_diff('second', {pickup}, {dropoff}) > 0
                    THEN trip_distance /
                         (date_diff('second', {pickup}, {dropoff}) / 3600.0)
                    ELSE NULL
                END,

                hour_of_day = EXTRACT(HOUR FROM {pickup}),
                day_of_week = EXTRACT(DOW FROM {pickup}),
                week_of_year = EXTRACT(WEEK FROM {pickup}),
                month_of_year = EXTRACT(MONTH FROM {pickup})
        """)

        print(f"{table} transformed successfully.")
        logger.info(f"{table} transformed successfully.")

    except Exception as e:
        print(f"Error transforming {table}: {e}")
        logger.error(f"Error transforming {table}: {e}")
        raise


def transform_data():
    """Transform both Yellow and Green taxi tables."""

    con = None

    try:
        con = duckdb.connect(DATABASE)
        logger.info("Connected to DuckDB instance.")

        for taxi_type in ["yellow", "green"]:
            transform_table(con, taxi_type)

        print("Transformation complete.")
        logger.info("Transformation complete.")

    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(f"An error occurred: {e}")

    finally:
        if con is not None:
            con.close()


if __name__ == "__main__":
    transform_data()