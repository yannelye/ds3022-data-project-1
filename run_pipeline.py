import subprocess
import sys


def run_pipeline():
    """Run the complete taxi data pipeline in order."""

    scripts = [
        "load.py",
        "clean.py",
        "transform.py",
        "analysis.py"
    ]

    for script in scripts:
        print(f"\nRunning {script}...")

        try:
            subprocess.run(
                [sys.executable, script],
                check=True
            )

        except subprocess.CalledProcessError as e:
            print(f"Pipeline stopped because {script} failed.")
            raise e

    print("\nPipeline completed successfully.")


if __name__ == "__main__":
    run_pipeline()