import ftplib
import os
from ftplib import FTP_TLS
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from app.models.cddis_handler import CDDIS_Handler
from app.utils.gn_functions import GPSDate
import numpy as np
import subprocess
from app.models.execution import INPUT_PRODUCTS_PATH

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

def download_ppp_products(inputs) -> bool:
    """Download PPP products using the CDDIS_handler and auto_download_PPP script"""
    start_datetime  = inputs.start_epoch
    end_datetime    = inputs.end_epoch

    cddis = CDDIS_Handler(end_datetime)

    # Get the optimal analysis_center, project_type, and solution_type
    user_analysis_center = inputs.ppp_provider.upper()

    if user_analysis_center in cddis.get_list_of_valid_analysis_centers():
        analysis_center = user_analysis_center
        project_type, solution_type = cddis.get_optimal_project_solution_tuple(analysis_center)

        if project_type is None or solution_type is None:
            # Fallback: try other analysis centers
            for ac in ["COD", "IGS", "EMR", "GFZ"]:
                if ac in cddis.get_list_of_valid_analysis_centers():
                    project_type, solution_type = cddis.get_optimal_project_solution_tuple(ac)
                    if project_type and solution_type:
                        analysis_center = ac
                        print(f"Using fallback analysis center: {ac}")
                        break
    else:
        # User's provider is not available, find the best available
        analysis_center = None
        for ac in ["COD", "IGS", "EMR", "GFZ"]:
            if ac in cddis.get_list_of_valid_analysis_centers():
                project_type, solution_type = cddis.get_optimal_project_solution_tuple(ac)
                if project_type and solution_type:
                    analysis_center = ac
                    print(f"User provider '{user_analysis_center}' not available, using: {ac}")
                    break

    if not analysis_center or not project_type or not solution_type:
        print("No valid PPP products available for the specified time period")
        return False

    try:
        download_static_products(start_datetime, end_datetime)
        download_dynamic_products(start_datetime, end_datetime, analysis_center, project_type, solution_type)
        return True
    except Exception as e:
        print(f"Error downloading PPP products: {e}")
        return False


def download_static_products(start_datetime: str, end_datetime: str) -> None:
    """Download static PPP products that don't change often"""

    script_path = Path(__file__).parent / "auto_download_PPP.py"
    products_path = Path(INPUT_PRODUCTS_PATH)

    if not script_path.exists():
        raise FileNotFoundError(f"auto_download_PPP.py not found at {script_path}")

    command = [
        "python3", str(script_path),
        "--most_recent",
        "--dont-replace",
        "--target-dir", str(products_path),
        "--start-datetime", start_datetime,
        "--end-datetime", end_datetime,
        "--preset", "manual",
        "--atx", "--aload", "--igrf", "--oload",
        "--opole", "--planet", "--sat-meta", "--yaw", "--gpt2"
    ]

    print("Downloading static PPP products...")
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    print("Static products downloaded successfully")

def download_dynamic_products(
        start_datetime: str, end_datetime: str,
        analysis_center: str, project_type: str, solution_type: str) -> None:
    """Download dynamic PPP products that change based on analysis center"""

    script_path = Path(__file__).parent / "auto_download_PPP.py"
    products_path = Path(INPUT_PRODUCTS_PATH)

    if not script_path.exists():
        raise FileNotFoundError(f"auto_download_PPP.py not found at {script_path}")

    command = [
        "python3", str(script_path),
        "--dont-replace",
        "--target-dir", str(products_path),
        "--start-datetime", start_datetime,
        "--end-datetime", end_datetime,
        "--analysis-center", analysis_center,
        "--project-type", project_type,
        "--solution-type", solution_type,
        "--preset", "manual",
        "--clk", "--sp3", "--bia", "--nav"
    ]

    print(f"Downloading dynamic PPP products for {analysis_center}...")
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    print("Dynamic products downloaded successfully")

if __name__ == "__main__":
    start_time = GPSDate(np.datetime64(datetime(2023, 10, 1, 0, 0)))
    create_cddis_file(Path(__file__).parent, start_time)
