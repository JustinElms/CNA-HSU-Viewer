import json
from pathlib import Path

import numpy as np


"""
TODO:
- add docstrings
- store meter data in cfg for quick access
"""

SKIP_COLUMNS = [
    "filename",
    "path",
    "csv_path",
    "info_line_number",
    "Hole_ID",
    "box_number",
    "row_number",
    "meter_from",
    "meter_to",
    "meter_start",
    "meter_end",
    "position_raw",
    "None",
]


class Dataset:
    def __init__(self, config_path: Path | str = None) -> None:

        config_path = (
            config_path if isinstance(config_path, Path) else Path(config_path)
        )
        self.config_path: Path = config_path
        self.config: dict = self._get_config()

    def _get_config(self) -> dict:
        cwd = Path(__file__).parent

        try:
            with open(cwd.joinpath(self.config_path), "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def data_types(self) -> dict:
        data_types = list(self.config.keys())
        data_types = [dt for dt in data_types if dt not in SKIP_COLUMNS]
        return {dt: list(self.config[dt].keys()) for dt in data_types}

    def data_options(
        self,
        product_group: str | None = None,
        datatype: str | None = None,
    ) -> list:
        if product_group and datatype:
            options = list(self.config[product_group][datatype])
            return options

    def data(
        self,
        product_group: str | None = None,
        datatype: str | None = None,
        selection: str | None = None,
    ):
        return self.config[product_group][datatype][selection]

    def meter(self):

        meter_from = self.config["meter_from"]
        meter_to = self.config["meter_to"]
        csv_path = self.config["csv_path"]

        meter_data = np.genfromtxt(
            csv_path,
            delimiter=",",
            dtype="float",
            comments=None,
            skip_header=5,
            usecols=[int(meter_from["column"]), int(meter_to["column"])],
        )

        return meter_data

    def get_row_meter(self):
        meter_from_col = self.config.get("meter_from")
        meter_to_col = self.config.get("meter_to")

        csv_path = self.config["csv_path"]

        meter_data = np.genfromtxt(
            csv_path,
            delimiter=",",
            dtype="float",
            comments=None,
            skip_header=5,
            usecols=[meter_from_col, meter_to_col],
        )

        return meter_data

    def get_box_meter(self):
        meter_data = []

        box_numbers_col = self.config.get("box_number")
        meter_from_col = self.config.get("meter_from")
        meter_to_col = self.config.get("meter_to")

        csv_path = self.config["csv_path"]

        [box_numbers, meter_from, meter_to] = np.genfromtxt(
            csv_path,
            delimiter=",",
            dtype="float",
            comments=None,
            skip_header=5,
            usecols=[box_numbers_col, meter_from_col, meter_to_col],
        ).transpose()

        for num in list(set(box_numbers)):
            rows = [
                idx
                for idx, box_number in enumerate(box_numbers)
                if num == box_number
            ]
            meter_data.append(
                [meter_from[np.min(rows)], meter_to[np.max(rows)]]
            )

        return meter_data
