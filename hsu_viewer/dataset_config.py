import json
from pathlib import Path

import numpy as np


class DatasetConfig:
    def __init__(self, config_path: Path | str = None) -> None:

        config_path = (
            config_path if isinstance(config_path, Path) else Path(config_path)
        )
        self._config_path: Path = config_path
        self._config: dict = self.__get_dataset_config()

    def __get_dataset_config(self) -> dict:
        cwd = Path(__file__).parent

        try:
            with open(cwd.joinpath(self._config_path), "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def add_dataset(self, dataset_path: str) -> None:

        dataset = {}
        dataset_path = Path(dataset_path)
        dataset_name = dataset_path.name

        spec_images = self.__get_spec_image_data(dataset_path.joinpath("Core"))
        core_images = self.__get_core_image_data(
            dataset_path.joinpath("Photo")
        )

        csv_files = list(dataset_path.glob("*_DATA.csv"))
        if len(csv_files) > 0:
            csv_data = self.__parse_csv_data(csv_files[0])

        dataset[dataset_name] = {
            "path": dataset_path.as_posix(),
            "csv_path": csv_files[0].as_posix(),
            "Spectral Images": spec_images,
            "Corebox Images": core_images,
            **csv_data,
        }

        if self._config:
            self._config.update(dataset)
        else:
            self._config = dataset

        with open(self._config_path, "w") as f:
            json.dump(self._config, f)

    def datasets(self) -> list:
        if self._config:
            return list(self._config.keys())
        else:
            return []

    def data_types(self, dataset: str | None = None) -> dict:
        skip_types = ["path", "meter_to", "meter_from"]
        if dataset:
            data_types = list(self._config[dataset].keys())
            data_types = [dt for dt in data_types if dt not in skip_types]
            return {
                dt: list(self._config[dataset][dt].keys()) for dt in data_types
            }
        else:
            return {}

    def data_options(
        self, dataset: str | None = None,
        product_group: str | None = None,
        datatype: str | None = None
    ) -> list:
        if dataset and product_group and datatype:
            options = list(self._config[dataset][product_group][datatype])
        return options

    def data(
        self,
        dataset: str | None = None,
        product_group: str | None = None,
        datatype: str | None = None,
        selection: str | None = None,
    ):
        return self._config[dataset][product_group][datatype][selection]

    def __get_spec_image_data(self, dataset_path: Path) -> list:

        spec_im_dict = {}
        if dataset_path.is_dir():
            for path in dataset_path.iterdir():
                if path.is_dir() and "mask_" not in path.name:

                    dir_info = path.name.split("_")
                    image_type = dir_info[0].title()
                    name = " ".join(dir_info[1:]).title()

                    if name:
                        meta_data = {
                            "name": name,
                            "path": path.as_posix(),
                        }

                        if spec_im_dict.get(image_type):
                            spec_im_dict[image_type][name] = meta_data
                        else:
                            spec_im_dict[image_type] = {name: meta_data}

        return spec_im_dict

    def __get_core_image_data(self, dataset_path: Path) -> list:

        core_im_dict = {}
        if dataset_path.is_dir():
            for path in dataset_path.iterdir():
                if path.is_dir():
                    meta_data = {"name": path.name, "path": path.as_posix()}
                    core_im_dict[path.name] = {path.name: meta_data}
        return core_im_dict

    def __parse_csv_data(self, csv_path: Path) -> list:

        csv_data_dict = {}
        csv_data_dict["Spectral Data"] = {}
        csv_data = np.genfromtxt(
            csv_path, delimiter=",", max_rows=5, dtype="str", comments=None
        )

        data_types = [
            "mineral_per",
            "chemistry_",
            "position_",
        ]

        skip = [
            "filename",
            "info_line_number",
            "Hole_ID",
            "box_number",
            "row_number",
            "meter_from",
            "meter_to",
            "position_raw",
            "None",
        ]

        for idx, col in enumerate(csv_data[1]):
            if (
                any(d in col.lower() for d in data_types)
                and col.lower() not in skip
            ):  

                data_type = [dt for dt in data_types if dt in col.lower()][0]
                name = col.replace(data_type, "").split("_")[1:]
                name = " ".join(name)

                meta_data = {
                    "name": name,
                    "unit": csv_data[2, idx],
                    "min_value": csv_data[3, idx],
                    "max_value": csv_data[4, idx],
                    "column": str(idx),
                }

                if data_type == "mineral_per":
                    data_type = "Mineral Percent"
                elif data_type == "chemistry_":
                    data_type = "Chemistry"
                elif data_type == "position_":
                    data_type = "Position"

                if csv_data_dict["Spectral Data"].get(data_type):
                    csv_data_dict["Spectral Data"][data_type][name] = meta_data
                else:
                    csv_data_dict["Spectral Data"][data_type] = {
                        name: meta_data
                    }
            elif "meter_from" in col or "meter_to" in col:
                data = np.genfromtxt(
                    csv_path,
                    delimiter=",",
                    usecols=idx,
                    skip_header=5,
                    dtype=float,
                    comments=None,
                )
                csv_data_dict[col] = {
                    "column": str(idx),
                    "min_value": data[0],
                    "max_value": data[-1],
                }

        return csv_data_dict

    def meter(self, dataset: str):

        meter_from = self._config[dataset]["meter_from"]
        meter_to = self._config[dataset]["meter_to"]
        csv_path = self._config[dataset]["csv_path"]

        meter_data = np.genfromtxt(
            csv_path, delimiter=",",
            dtype="float",
            comments=None,
            skip_header=5,
            usecols=[int(meter_from["column"]), int(meter_to["column"])]
        )

        return meter_data
