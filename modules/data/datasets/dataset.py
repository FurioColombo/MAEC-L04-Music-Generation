""" TODO - Module DOC """

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from definitions import ConfigSections, Paths
from modules import utilities
from modules.data.converters.dataconverter import DataConverter
from modules.data.converters.noteseq import NoteSequenceConverter
from modules.data.loaders.tfrecord import TFRecordLoader


class Dataset(ABC):
    """ TODO - Class DOC """

    def __init__(self):
        self._config_file = utilities.load_configuration_section(ConfigSections.DATASETS)
        self.test_dataset = None
        self.validation_dataset = None
        self.train_dataset = None

    def convert(self) -> None:
        if self.data_converter:
            self.data_converter.convert_train(self._train_metadata)
            self.data_converter.convert_validation(self._validation_metadata)
            self.data_converter.convert_test(self._test_metadata)

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def path(self) -> Path:
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        pass

    @property
    @abstractmethod
    def _metadata(self) -> Any:
        pass

    @property
    @abstractmethod
    def _train_metadata(self) -> Any:
        pass

    @property
    @abstractmethod
    def _validation_metadata(self) -> Any:
        pass

    @property
    @abstractmethod
    def _test_metadata(self) -> Any:
        pass

    @property
    @abstractmethod
    def data_converter(self) -> DataConverter:
        pass


class SourceDataset(Dataset, ABC):

    def __init__(self):
        super().__init__()
        self.download()
        self.convert()

    @abstractmethod
    def download(self) -> None:
        pass

    @property
    def data_converter(self) -> DataConverter:
        return NoteSequenceConverter(self.path, Paths.DATA_NOTESEQ_RECORDS_DIR, self.name)


class TFRecordsDataset(Dataset, ABC):

    def __init__(self, source_datasets: [SourceDataset]):
        super().__init__()
        self.source_datasets = source_datasets
        self.data_loader = TFRecordLoader(self.path, self.name)

    def load(self) -> None:
        if self.data_loader:
            self.train_dataset = self.data_loader.load_train(self.source_datasets)
            self.validation_dataset = self.data_loader.load_validation(self.source_datasets)
            self.test_dataset = self.data_loader.load_test(self.source_datasets)

    @property
    def _metadata(self) -> Any:
        return None

    @property
    def _train_metadata(self) -> Any:
        return utilities.get_tfrecords_path_for_source_datasets(self.source_datasets, Paths.DATA_NOTESEQ_RECORDS_DIR,
                                                                'train', "noteseq")

    @property
    def _validation_metadata(self) -> Any:
        return utilities.get_tfrecords_path_for_source_datasets(self.source_datasets, Paths.DATA_NOTESEQ_RECORDS_DIR,
                                                                'validation', "noteseq")

    @property
    def _test_metadata(self) -> Any:
        return utilities.get_tfrecords_path_for_source_datasets(self.source_datasets, Paths.DATA_NOTESEQ_RECORDS_DIR,
                                                                'test', "noteseq")
