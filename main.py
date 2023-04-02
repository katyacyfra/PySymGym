from agent.connection_manager import ConnectionManager
from agent.n_agent import get_validation_maps
from common.constants import Constant
from logger.setup import setup_loggers
from ml.model_wrappers.genetic_learner import GeneticLearner
from ml.model_wrappers.protocols import Mutable
from ml.mutation.classes import GameMapsModelResults
from ml.mutation.selection import (
    decart_scorer,
    euclidean_scorer,
    select_all_models,
    select_k_best,
    select_n_maps_tops,
    tournament_selection,
)
from ml.utils import load_full_model
from r_learn import r_learn


def new_gen_function(mr: GameMapsModelResults) -> list[Mutable]:
    best_mutables = [
        *select_k_best(decart_scorer, mr, k=3),
        *select_n_maps_tops(mr, n=4),
    ]

    average_of_selected = lambda mutables: GeneticLearner.average(mutables)
    mutate_average_of_selected = lambda mutables: GeneticLearner.mutate(
        GeneticLearner.average(mutables),
        mutation_volume=0.25,
        mutation_freq=0.1,
    )

    mutated_average_of_all = lambda mr: GeneticLearner.mutate(
        GeneticLearner.average(select_all_models(mr)),
        mutation_volume=0.25,
        mutation_freq=0.1,
    )

    tournament_average = lambda mr: GeneticLearner.average(
        tournament_selection(
            mr, desired_population=3, n_comparisons=4, scorer=euclidean_scorer
        )
    )

    tournament_average_mutated = lambda mr: GeneticLearner.mutate(
        GeneticLearner.average(
            tournament_selection(
                mr, desired_population=3, n_comparisons=4, scorer=euclidean_scorer
            )
        ),
        mutation_volume=0.25,
        mutation_freq=0.1,
    )

    return [
        *select_k_best(decart_scorer, mr, k=5),
        average_of_selected(best_mutables),
        mutate_average_of_selected(best_mutables),
        mutated_average_of_all(mr),
        tournament_average(mr),
        tournament_average_mutated(mr),
    ]


def main():
    setup_loggers()
    socket_urls = [Constant.DEFAULT_GAMESERVER_URL]
    cm = ConnectionManager(socket_urls)

    loaded_model = load_full_model(Constant.IMPORTED_FULL_MODEL_PATH)

    epochs = 10
    max_steps = 300
    n_models = 10

    GeneticLearner.set_model(loaded_model, 8)
    models = [
        GeneticLearner()  # ([-0.12, -0.17, 0.3, 0.16, 0.01, 0.33, 0.24, -0.05])
        for _ in range(n_models)
    ]

    maps = get_validation_maps(cm)

    r_learn(epochs, max_steps, models, maps, new_gen_function, cm)

    cm.close()


if __name__ == "__main__":
    main()
