import json
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

        dataset_path = Path(dataset_path)
        dataset_name = dataset_path.name
        image_directories = self._list_image_directories(dataset_path)

        return

    def _list_image_directories(self, dataset_path: Path) -> list:

        image_directories = []
        for path in dataset_path.iterdir():
            if path.is_dir():
                image_directories.append(path.name)
        return image_directories


# TODO remove when finished
if __name__ == "__main__":
    dataset_config = DatasetConfig("hsu-datasets.cfg")
    dataset_config.add_dataset("C:/Users/justi/Desktop/HSU Viewer/BE-11-05")
