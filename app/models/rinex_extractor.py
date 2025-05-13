from pathlib import Path

class RinexExtractor:
    def __init__(self, rinex_path):
        self.rinex_path = rinex_path

    def load_rinex_file(self, rinex_path):
        self.rinex_path = rinex_path

    def extract_rinex_data(self, rinex_path: str):
        """
        Opens a .RNX file and extracts the corresponding YAML config information

        :param rinex_path: File path for .RNX file to extract from e.g. "resources/input/ALIC.rnx"
        :raises FileNotFoundError if .RNX file is not found
        """
        start_epoch = None
        end_epoch = None
        epoch_interval = None
        receiver_type = None
        antenna_type = None
        antenna_offset = None
        marker_name = None

        def format_time(year, month, day, hour, minute, second):
            return f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{(int(second)):02d}"

        with open(rinex_path, "r") as file:
            for line in file:
                label = line[60:].strip()

                if label == "TIME OF FIRST OBS":
                    year = int(line[0:6])
                    month = int(line[6:12])
                    day = int(line[12:18])
                    hour = int(line[18:24])
                    minute = int(line[24:30])
                    second = float(line[30:43])
                    start_epoch = format_time(year, month, day, hour, minute, second)

                elif label == "TIME OF LAST OBS":
                    year = int(line[0:6])
                    month = int(line[6:12])
                    day = int(line[12:18])
                    hour = int(line[18:24])
                    minute = int(line[24:30])
                    second = float(line[30:43])
                    end_epoch = format_time(year, month, day, hour, minute, second)

                elif label == "INTERVAL":
                    epoch_interval = int(float(line[0:10])) # float cast converts it into a number, int cast converts to integer

                elif label == "MARKER NAME":
                    marker_name = line[0:60].strip()

                elif label == "REC # / TYPE / VERS":
                    receiver_type = line[20:40].strip()

                elif label == "ANT # / TYPE":
                    antenna_type = line[20:40].strip()
                    second_half = line[40:60].strip()
                    if second_half:
                        antenna_type += f" {second_half}"

                elif label == "ANTENNA: DELTA H/E/N":
                    h = float(line[0:14].strip())
                    e = float(line[14:28].strip())
                    n = float(line[28:42].strip())
                    antenna_offset = [h, e, n]

                elif label == "END OF HEADER":
                    break

        return {
            "start_epoch": start_epoch,
            "end_epoch": end_epoch,
            "interval": epoch_interval,
            "marker_name": marker_name,
            "receiver_type": receiver_type,
            "antenna_type": antenna_type,
            "antenna_offset": antenna_offset,
        }