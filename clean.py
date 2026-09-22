import duckdb
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='clean.log'
)

logger = logging.getLogger(__name__)

DATABASE = 'emissions.duckdb'


def get_time_columns(taxi_type):
    """Return the correct pickup and dropoff columns for each taxi type."""

    if taxi_type == "yellow":
        return "tpep_pickup_datetime", "tpep_dropoff_datetime"
    else:
        return "lpep_pickup_datetime", "lpep_dropoff_datetime"


def clean_table(con, taxi_type):
    """Clean invalid trips from one taxi table."""

    table_name = f"{taxi_type}_trips"
    pickup_col, dropoff_col = get_time_columns(taxi_type)

    try:
        before_count = con.execute(
            f"SELECT COUNT(*) FROM {table_name}"
        ).fetchone()[0]

        print(f"\nCleaning {table_name}...")
        print(f"Rows before cleaning: {before_count}")
        logger.info(f"{table_name} rows before cleaning: {before_count}")

        # Remove duplicate trips
        con.execute(f"""
            CREATE OR REPLACE TABLE {table_name} AS
            SELECT DISTINCT *
            FROM {table_name}
        """)

        # Remove trips with 0 passengers
        con.execute(f"""
            DELETE FROM {table_name}
            WHERE passenger_count = 0
        """)

        # Remove trips with 0 miles
        con.execute(f"""
            DELETE FROM {table_name}
            WHERE trip_distance = 0
        """)

        # Remove trips longer than 100 miles
        con.execute(f"""
            DELETE FROM {table_name}
            WHERE trip_distance > 100
        """)

        # Remove trips lasting more than one day
        con.execute(f"""
            DELETE FROM {table_name}
            WHERE date_diff(
                'second',
                {pickup_col},
                {dropoff_col}
            ) > 86400
        """)

        after_count = con.execute(
            f"SELECT COUNT(*) FROM {table_name}"
        ).fetchone()[0]

        removed_count = before_count - after_count

        print(f"Rows after cleaning: {after_count}")
        print(f"Rows removed: {removed_count}")

        logger.info(f"{table_name} rows after cleaning: {after_count}")
        logger.info(f"{table_name} rows removed: {removed_count}")

    except Exception as e:
        print(f"Error cleaning {table_name}: {e}")
        logger.error(f"Error cleaning {table_name}: {e}")
        raise


def verify_cleaning(con, taxi_type):
    """Verify that every required cleaning condition has a count of zero."""

    table_name = f"{taxi_type}_trips"
    pickup_col, dropoff_col = get_time_columns(taxi_type)

    try:
        # Verify that duplicate trips no longer exist
        duplicate_count = con.execute(f"""
            SELECT COUNT(*)
            FROM (
                SELECT *
                FROM {table_name}
                GROUP BY ALL
                HAVING COUNT(*) > 1
            )
        """).fetchone()[0]

        # Verify that 0-passenger trips no longer exist
        zero_passengers = con.execute(f"""
            SELECT COUNT(*)
            FROM {table_name}
            WHERE passenger_count = 0
        """).fetchone()[0]

        # Verify that 0-mile trips no longer exist
        zero_miles = con.execute(f"""
            SELECT COUNT(*)
            FROM {table_name}
            WHERE trip_distance = 0
        """).fetchone()[0]

        # Verify that trips over 100 miles no longer exist
        over_100_miles = con.execute(f"""
            SELECT COUNT(*)
            FROM {table_name}
            WHERE trip_distance > 100
        """).fetchone()[0]

        # Verify that trips longer than one day no longer exist
        over_one_day = con.execute(f"""
            SELECT COUNT(*)
            FROM {table_name}
            WHERE date_diff(
                'second',
                {pickup_col},
                {dropoff_col}
            ) > 86400
        """).fetchone()[0]

        print(f"\nVerification for {table_name}:")
        print(f"Duplicate trips: {duplicate_count}")
        print(f"0-passenger trips: {zero_passengers}")
        print(f"0-mile trips: {zero_miles}")
        print(f"Trips over 100 miles: {over_100_miles}")
        print(f"Trips over 86,400 seconds: {over_one_day}")

        logger.info(
            f"{table_name} duplicate trips after cleaning: "
            f"{duplicate_count}"
        )
        logger.info(
            f"{table_name} 0-passenger trips after cleaning: "
            f"{zero_passengers}"
        )
        logger.info(
            f"{table_name} 0-mile trips after cleaning: "
            f"{zero_miles}"
        )
        logger.info(
            f"{table_name} trips over 100 miles after cleaning: "
            f"{over_100_miles}"
        )
        logger.info(
            f"{table_name} trips over 86400 seconds after cleaning: "
            f"{over_one_day}"
        )

    except Exception as e:
        print(f"Error verifying {table_name}: {e}")
        logger.error(f"Error verifying {table_name}: {e}")
        raise


def clean_data():
    """Clean and verify the Yellow and Green taxi tables."""

    con = None

    try:
        # Connect to the local DuckDB database
        con = duckdb.connect(
            database=DATABASE,
            read_only=False
        )

        logger.info("Connected to DuckDB instance")

        # Clean and verify both taxi tables
        for taxi_type in ["yellow", "green"]:
            clean_table(con, taxi_type)
            verify_cleaning(con, taxi_type)

        print("\nCleaning complete.")
        logger.info("All taxi tables cleaned successfully")

    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(f"An error occurred: {e}")

    finally:
        if con is not None:
            con.close()
            logger.info("DuckDB connection closed")


if __name__ == "__main__":
    clean_data()