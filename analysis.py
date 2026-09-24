import duckdb
import logging
import matplotlib.pyplot as plt


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='analysis.log'
)

logger = logging.getLogger(__name__)

DATABASE = 'emissions.duckdb'


def print_result(message):
    """Print and log an analysis result."""
    print(message)
    logger.info(message)


def analyze_table(con, taxi_type):
    """Run the required CO2 analyses for one taxi type."""

    table = f"{taxi_type}_trips"
    label = taxi_type.capitalize()

    try:
        print(f"\n--- {label} Taxi Analysis ---")

        # 1. Largest single carbon-producing trip
        largest = con.execute(f"""
            SELECT trip_co2_kgs
            FROM {table}
            ORDER BY trip_co2_kgs DESC
            LIMIT 1
        """).fetchone()[0]

        print_result(
            f"{label} largest carbon-producing trip: "
            f"{largest:.2f} kg CO2"
        )

        # 2. Heaviest and lightest hour on average
        hours = con.execute(f"""
            SELECT hour_of_day, AVG(trip_co2_kgs) AS avg_co2
            FROM {table}
            GROUP BY hour_of_day
            ORDER BY avg_co2 DESC
        """).fetchall()

        print_result(
            f"{label} heaviest hour: {hours[0][0]} "
            f"({hours[0][1]:.2f} kg CO2 average)"
        )

        print_result(
            f"{label} lightest hour: {hours[-1][0]} "
            f"({hours[-1][1]:.2f} kg CO2 average)"
        )

        # 3. Heaviest and lightest day of week on average
        days = con.execute(f"""
            SELECT day_of_week, AVG(trip_co2_kgs) AS avg_co2
            FROM {table}
            GROUP BY day_of_week
            ORDER BY avg_co2 DESC
        """).fetchall()

        day_names = {
            0: "Sunday",
            1: "Monday",
            2: "Tuesday",
            3: "Wednesday",
            4: "Thursday",
            5: "Friday",
            6: "Saturday"
        }

        print_result(
            f"{label} heaviest day: "
            f"{day_names[days[0][0]]} "
            f"({days[0][1]:.2f} kg CO2 average)"
        )

        print_result(
            f"{label} lightest day: "
            f"{day_names[days[-1][0]]} "
            f"({days[-1][1]:.2f} kg CO2 average)"
        )

        # 4. Heaviest and lightest week on average
        weeks = con.execute(f"""
            SELECT week_of_year, AVG(trip_co2_kgs) AS avg_co2
            FROM {table}
            GROUP BY week_of_year
            ORDER BY avg_co2 DESC
        """).fetchall()

        print_result(
            f"{label} heaviest week: {weeks[0][0]} "
            f"({weeks[0][1]:.2f} kg CO2 average)"
        )

        print_result(
            f"{label} lightest week: {weeks[-1][0]} "
            f"({weeks[-1][1]:.2f} kg CO2 average)"
        )

        # 5. Heaviest and lightest month on average
        months = con.execute(f"""
            SELECT month_of_year, AVG(trip_co2_kgs) AS avg_co2
            FROM {table}
            GROUP BY month_of_year
            ORDER BY avg_co2 DESC
        """).fetchall()

        month_names = {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December"
        }

        print_result(
            f"{label} heaviest month: "
            f"{month_names[months[0][0]]} "
            f"({months[0][1]:.2f} kg CO2 average)"
        )

        print_result(
            f"{label} lightest month: "
            f"{month_names[months[-1][0]]} "
            f"({months[-1][1]:.2f} kg CO2 average)"
        )

    except Exception as e:
        print(f"Error analyzing {table}: {e}")
        logger.error(f"Error analyzing {table}: {e}")
        raise


def create_plot(con):
    """Create a monthly CO2 plot using two Y-axes."""

    try:
        yellow = con.execute("""
            SELECT month_of_year, SUM(trip_co2_kgs)
            FROM yellow_trips
            GROUP BY month_of_year
            ORDER BY month_of_year
        """).fetchall()

        green = con.execute("""
            SELECT month_of_year, SUM(trip_co2_kgs)
            FROM green_trips
            GROUP BY month_of_year
            ORDER BY month_of_year
        """).fetchall()

        yellow_months = [row[0] for row in yellow]
        yellow_co2 = [row[1] for row in yellow]

        green_months = [row[0] for row in green]
        green_co2 = [row[1] for row in green]

        # Create plot and Yellow Taxi Y-axis
        fig, ax1 = plt.subplots(figsize=(10, 6))

        line1 = ax1.plot(
            yellow_months,
            yellow_co2,
            marker='o',
            color='goldenrod',
            label='Yellow Taxi'
        )

        ax1.set_xlabel("Month")
        ax1.set_ylabel(
            "Yellow Taxi CO2 (kg)",
            color='goldenrod'
        )
        ax1.tick_params(
            axis='y',
            labelcolor='goldenrod'
        )
        ax1.set_xticks(range(1, 13))

        # Create Green Taxi Y-axis
        ax2 = ax1.twinx()

        line2 = ax2.plot(
            green_months,
            green_co2,
            marker='o',
            color='green',
            label='Green Taxi'
        )

        ax2.set_ylabel(
            "Green Taxi CO2 (kg)",
            color='green'
        )
        ax2.tick_params(
            axis='y',
            labelcolor='green'
        )

        plt.title(
            "2024 NYC Taxi CO2 Emissions by Month"
        )

        # Combine both lines into one legend
        lines = line1 + line2
        labels = [line.get_label() for line in lines]

        ax1.legend(
            lines,
            labels,
            loc='upper right'
        )

        fig.tight_layout()

        plt.savefig("co2_by_month.png")
        plt.close()

        print_result(
            "Monthly CO2 plot saved as co2_by_month.png"
        )

    except Exception as e:
        print(f"Error creating plot: {e}")
        logger.error(f"Error creating plot: {e}")
        raise


def run_analysis():
    """Run all analyses and create the monthly CO2 plot."""

    con = None

    try:
        con = duckdb.connect(
            database=DATABASE,
            read_only=True
        )

        logger.info("Connected to DuckDB instance")

        for taxi_type in ["yellow", "green"]:
            analyze_table(con, taxi_type)

        create_plot(con)

        print("\nAnalysis complete.")
        logger.info("Analysis complete")

    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(f"An error occurred: {e}")

    finally:
        if con is not None:
            con.close()


if __name__ == "__main__":
    run_analysis()
def run_analysis():
    """Run all analyses and create the monthly CO2 plot."""

    con = None

    try:
        con = duckdb.connect(
            database=DATABASE,
            read_only=True
        )

        logger.info("Connected to DuckDB instance")

        for taxi_type in ["yellow", "green"]:
            analyze_table(con, taxi_type)

        create_plot(con)

        print("\nAnalysis complete.")
        logger.info("Analysis complete")

    except Exception as e:
        print(f"An error occurred: {e}")
        logger.error(f"An error occurred: {e}")

    finally:
        if con is not None:
            con.close()


if __name__ == "__main__":
    run_analysis()