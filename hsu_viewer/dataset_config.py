import csv
import json
import numpy as np
from pathlib import Path


class DatasetConfig:
    def __init__(self, config_path: str = None) -> None:

        self._config_path: str = config_path
        self._config: dict = self.__get_dataset_config()

    def __get_dataset_config(self) -> dict:
        cwd = Path(__file__).parent

        try:
            with open(cwd.joinpath(self._config_path, "r")) as f:
                self._config = json.load(f)
        except FileNotFoundError:
            self._config = None

    def add_dataset(self, dataset_path: str) -> None:

        dataset = {}
        dataset_path = Path(dataset_path)
        dataset_name = dataset_path.name       

        spec_images = self.__list_image_directories(dataset_path.joinpath("Core"))
        core_images = self.__list_image_directories(dataset_path.joinpath("Photo"))

        csv_files = list(dataset_path.glob("*.csv"))

        # csv_data = np.genfromtxt(
        #     csv_files[0], delimiter=",", max_rows=4, dtype="str", comments=None
        # )

        dataset[dataset_name] = {
            "Spectral Images" : spec_images,
            "Core Box Images" : core_images,
        }

        if self._config:
            self._config.update(dataset)
        else:
            self._config = dataset

        with open(self._config_path, "w") as f:
                json.dump(self._config, f)



        return

    def __list_image_directories(self, dataset_path: Path) -> list:

        core_im_dict = {}
        if dataset_path.is_dir():
            for path in dataset_path.iterdir():
                if path.is_dir():

                    meta_data = path.name.split("_")
                    mineral_type = meta_data[0]
                    mineral_name = "_".join(meta_data[1:])

                    if core_im_dict.get(mineral_type):
                        core_im_dict[mineral_type].append(mineral_name)
                    else:
                        core_im_dict[mineral_type] = [mineral_name]

        return core_im_dict

    def __parse_csv(self, csv_path: Path) -> list:
        return


# TODO remove when finished
if __name__ == "__main__":
    dataset_config = DatasetConfig("hsu-datasets.cfg")
    dataset_config.add_dataset("C:/Users/justi/Desktop/HSU Viewer/New Format/PB-77-013")
