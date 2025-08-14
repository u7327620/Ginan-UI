import ftplib
import os
from ftplib import FTP_TLS
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from app.utils.gn_functions import GPSDate
import numpy as np
import subprocess

# 1. Create an account with CDDIS
# 2. Create a file named "cddis.env" in the same directory as this script
# 3. Add EMAIL=<your_account_email> to the "cddis.env" file

# Ensure account is registered and in this file :)
load_dotenv(Path(__file__).parent / "cddis.env")


def retrieve_all_cddis_types(reference_start: GPSDate) -> list[str]:
    """
    Retrieve all CDDIS data types for a given GPS Week.

    :param reference_start: The datetime of the GPS Week to retrieve.
    :param timespan: The duration for which to retrieve data.
    :return:
    """
    ftp_tls = FTP_TLS(host="gdc.cddis.eosdis.nasa.gov", user="anonymous", passwd=os.getenv("EMAIL"), timeout=60)
    ftp_tls.prot_p()  # Secures the TLS connection, mandatory for CDDIS
    files = None
    try:
        ftp_tls.cwd(f"gnss/products/{reference_start.gpswk}")
        files = ftp_tls.nlst()
    except ftplib.all_errors as e:
        print("Error getting file list", e)
    return files

def create_cddis_file(filepath: Path, reference_start: GPSDate) -> None:
    """
    Create a file named "CDDIS.list" with CDDIS data types for a given reference start time.

    :param filepath: The path to the directory where the file will be created.
    :param reference_start: The start time for the data retrieval.
    """
    data = retrieve_all_cddis_types(reference_start)
    with open(filepath.joinpath("../models/CDDIS.list"), "w") as f:
        for d in data:
            try:
                time = datetime.strptime(d.split("_")[1], "%Y%j%H%M")
                f.write(f"{d} {time} \n")
            except IndexError:
                data.remove(d)


def download_ppp_products(self, input_products_path: str, inputs) -> bool:
    start_datetime  = inputs.start_epoch
    end_datetime    = inputs.end_epoch
    analysis_center = inputs
    project_type    = inputs
    solution_type   = inputs

    try:
        download_static_products(self, start_datetime, end_datetime)
        download_dynamic_products(self, start_datetime, end_datetime, analysis_center, project_type, solution_type)
        return True
    except ValueError:
        return False


def download_static_products(self, start_datetime, end_datetime) -> None:
    command = [
        "python3", str(script_path),
        "--most_recent",
        "--dont-replace",
        "--target-dir", str(products_dir),
        "--start-datetime", start_datetime,
        "--end-datetime", end_datetime,
        "--preset", "manual",
        "--atx", "--aload", "--igrf", "--oload",
        "--opole", "--planet", "--sat-meta", "--yaw", "--gpt2"
    ]

def download_dynamic_products(
        self, start_datetime, end_datetime,
        analysis_center, project_type, solution_type) -> None:

    command = [
        "python3", str(script_path),
        "--dont-replace",
        "--target-dir", str(products_dir),
        "--start-datetime", start_datetime,
        "--end-datetime", end_datetime,
        "--analysis-center", analysis_center,
        "--project-type", project_type,
        "--solution-type", solution_type,
        "--preset", "manual",
        "--clk", "--sp3", "--bia", "--nav"
    ]

if __name__ == "__main__":
    start_time = GPSDate(np.datetime64(datetime(2023, 10, 1, 0, 0)))
    create_cddis_file(Path(__file__).parent, start_time)
