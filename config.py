import logging
from dataclasses import dataclass
from pathlib import Path
from shutil import rmtree

import torch

import ml.model_modified
import ml.models


class GeneralConfig:
    SERVER_COUNT = 3
    NUM_GENERATIONS = 2
    NUM_PARENTS_MATING = 2
    KEEP_ELITISM = None
    NUM_SOLUTIONS = None
    MAX_STEPS = 3000
    MUTATION_PERCENT_GENES = 4
    LOGGER_LEVEL = logging.INFO
    IMPORT_MODEL_INIT = lambda: ml.models.StateModelEncoder(
        hidden_channels=64, out_channels=8
    )
    MODEL_INIT = lambda: ml.model_modified.StateModelEncoderExport(
        hidden_channels=64, out_channels=8
    )
    DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


class BrokerConfig:
    BROKER_PORT = 8080


class ServerConfig:
    VSHARP_INSTANCES_START_PORT = 8100


@dataclass(slots=True, frozen=True)
class DumpByTimeoutFeature:
    enabled: bool
    timeout_sec: int
    save_path: Path

    def create_save_path_if_not_exists(self):
        if self.enabled:
            if self.save_path.exists():
                rmtree(self.save_path)
            self.save_path.mkdir()


@dataclass(slots=True, frozen=True)
class SaveEpochsCoveragesFeature:
    enabled: bool
    save_path: Path

    def create_save_path_if_not_exists(self):
        if self.enabled:
            if self.save_path.exists():
                rmtree(self.save_path)
            self.save_path.mkdir()


class FeatureConfig:
    VERBOSE_TABLES = True
    SHOW_SUCCESSORS = True
    NAME_LEN = 7
    DISABLE_MESSAGE_CHECKS = True
    DUMP_BY_TIMEOUT = DumpByTimeoutFeature(
        enabled=True, timeout_sec=600, save_path=Path("./report/timeouted_agents/")
    )
    SAVE_EPOCHS_COVERAGES = SaveEpochsCoveragesFeature(
        enabled=True, save_path=Path("./report/epochs_tables/")
    )
    ON_GAME_SERVER_RESTART = True


class GameServerConnectorConfig:
    CREATE_CONNECTION_TIMEOUT = 1
    RESPONCE_TIMEOUT_SEC = (
        FeatureConfig.DUMP_BY_TIMEOUT.timeout_sec + 1
        if FeatureConfig.DUMP_BY_TIMEOUT.enabled
        else 1000
    )
    SKIP_UTF_VALIDATION = True
