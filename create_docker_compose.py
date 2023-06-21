import sys, json
from init_config import *


def main():
    with open("config.json") as f:
        json_config = json.load(f)

    queues = json_config["config"]["queues"]
    em_queues = json_config["config"]["eof_manager_queues"]
    status_queues = json_config["config"]["status_queues"]
    amount_nodes = json_config["config"]["amount_nodes"]
    max_clients = json_config["config"]["max_clients"]

    receiver = init_receiver(queues, em_queues, status_queues)

    joiner_stations, joiner_weather, em_joiners = init_joiners(
        queues, em_queues, status_queues
    )

    filters_pretoc, filters_year, filters_distance, em_filters = init_filters(
        queues, em_queues, status_queues, amount_nodes
    )

    (
        appliers_query1,
        appliers_query2,
        appliers_query3,
        appliers_query4,
        em_appliers,
    ) = init_appliers(queues, em_queues, status_queues, amount_nodes)

    groupby1, groupby2, groupby3, groupby4, em_groupby = init_groupby(
        queues, em_queues, status_queues
    )

    results_verifier, em_results = init_results_verifier(
        queues, em_queues, status_queues
    )

    session_manager = init_session_manager(queues, max_clients)

    compose = (
        INIT_DOCKER.format()
        .replace("<RECEIVER>", receiver)
        .replace("<JOINER_STATIONS>", joiner_stations)
        .replace("<JOINER_WEATHER>", joiner_weather)
        .replace("<EM_JOINERS>", em_joiners)
        .replace("<FILTER_PRETOC>", filters_pretoc)
        .replace("<FILTER_YEAR>", filters_year)
        .replace("<FILTER_DISTANCE>", filters_distance)
        .replace("<EM_FILTERS>", em_filters)
        .replace("<EM_GROUPBY>", em_groupby)
        .replace("<GROUPBY_QUERY1>", groupby1)
        .replace("<GROUPBY_QUERY2>", groupby2)
        .replace("<GROUPBY_QUERY3>", groupby3)
        .replace("<GROUPBY_QUERY4>", groupby4)
        .replace("<APPLIER_QUERY1>", appliers_query1)
        .replace("<APPLIER_QUERY2>", appliers_query2)
        .replace("<APPLIER_QUERY3>", appliers_query3)
        .replace("<APPLIER_QUERY4>", appliers_query4)
        .replace("<EM_APPLIERS>", em_appliers)
        .replace("<RESULTS_VERIFIER>", results_verifier)
        .replace("<EM_RESULTS>", em_results)
        .replace("<SESSION_MANAGER>", session_manager)
    )

    with open("docker-compose-server.yaml", "w") as compose_file:
        compose_file.write(compose)


def init_receiver(queues, em_queues, status_queues):
    return RECEIVER.format(
        queues["joiners"]["stations"],
        queues["joiners"]["weather"],
        [
            queues["joiners"]["join_trip_stations"],
            queues["joiners"]["join_trip_weather"],
            queues["groupby_query4"],
        ],
        em_queues["joiners"],
        status_queues["new_clients"],
        queues["session_manager"],
        queues["receiver"],
    )


def init_joiners(queues, em_queues, status_queues):
    joiner_stations = JOINER_STATIONS.format(
        queues["joiners"]["stations"],
        queues["joiners"]["join_trip_stations"],
        em_queues["joiners"],
        queues["filters"]["filter_trip_stations"],
    )
    joiner_weather = JOINER_WEATHER.format(
        queues["joiners"]["weather"],
        queues["joiners"]["join_trip_weather"],
        em_queues["joiners"],
        queues["filters"]["filter_trip_weather"],
    )

    em_joiners = EM_JOINERS.format(
        em_queues["joiners"],
        em_queues["filters"],
        queues["joiners"]["stations"],
        queues["joiners"]["weather"],
        queues["joiners"]["join_trip_stations"],
        queues["joiners"]["join_trip_weather"],
        status_queues["new_clients"],
    )

    return joiner_stations, joiner_weather, em_joiners


def init_filters(queues, em_queues, status_queues, amount_nodes):
    filters_q = queues["filters"]

    filters_pretoc = ""
    for i in range(1, amount_nodes["filter_pretoc"] + 1):
        filters_pretoc += FILTER_PRETOC.format(
            i,
            i,
            filters_q["filter_trip_weather"],
            filters_q["filter_pretoc"],
            em_queues["filters"],
            queues["groupby_query1"],
        )

    filters_year = ""
    for i in range(1, amount_nodes["filter_year"] + 1):
        filters_year += FILTER_YEAR.format(
            i,
            i,
            filters_q["filter_trip_stations"],
            filters_q["filter_year"],
            em_queues["filters"],
            queues["groupby_query2"],
        )

    filters_distance = ""
    for i in range(1, amount_nodes["filter_distance"] + 1):
        filters_year += FILTER_DISTANCE.format(
            i,
            i,
            filters_q["filter_trip_stations"],
            filters_q["filter_distance"],
            em_queues["filters"],
            queues["groupby_query3"],
        )

    em_filters = EM_FILTERS.format(
        em_queues["filters"],
        [
            filters_q["filter_year"],
            filters_q["filter_pretoc"],
            filters_q["filter_distance"],
        ],
        em_queues["groupby"],
        status_queues["new_clients"],
        [amount_nodes[k] for k in amount_nodes if "filter" in k],
    )

    return filters_pretoc, filters_year, filters_distance, em_filters


def init_appliers(queues, em_queues, status_queues, amount_nodes):
    appliers_query1 = ""
    for i in range(1, amount_nodes["applier_query1"] + 1):
        appliers_query1 += APPLIER_QUERY1.format(
            i,
            i,
            queues["applier_query1"],
            em_queues["appliers"],
            queues["results_verifier"],
        )

    appliers_query2 = ""
    for i in range(1, amount_nodes["applier_query2"] + 1):
        appliers_query2 += APPLIER_QUERY2.format(
            i,
            i,
            queues["applier_query2"],
            em_queues["appliers"],
            queues["results_verifier"],
        )

    appliers_query3 = ""
    for i in range(1, amount_nodes["applier_query3"] + 1):
        appliers_query3 += APPLIER_QUERY3.format(
            i,
            i,
            queues["applier_query3"],
            em_queues["appliers"],
            queues["results_verifier"],
        )

    appliers_query4 = ""
    for i in range(1, amount_nodes["applier_query4"] + 1):
        appliers_query4 += APPLIER_QUERY4.format(
            i,
            i,
            queues["applier_query4"],
            em_queues["appliers"],
            queues["results_verifier"],
        )

    em_appliers = EM_APPLIERS.format(
        em_queues["appliers"],
        [
            queues["applier_query1"],
            queues["applier_query2"],
            queues["applier_query3"],
            queues["applier_query4"],
        ],
        em_queues["results_verifier"],
        status_queues["new_clients"],
        [amount_nodes[k] for k in amount_nodes if "applier" in k],
    )

    return (
        appliers_query1,
        appliers_query2,
        appliers_query3,
        appliers_query4,
        em_appliers,
    )


def init_groupby(queues, em_queues, status_queues):
    groupby1 = GROUPBY_QUERY1.format(
        queues["groupby_query1"], em_queues["groupby"], queues["applier_query1"]
    )
    groupby2 = GROUPBY_QUERY2.format(
        queues["groupby_query2"], em_queues["groupby"], queues["applier_query2"]
    )
    groupby3 = GROUPBY_QUERY3.format(
        queues["groupby_query3"], em_queues["groupby"], queues["applier_query3"]
    )
    groupby4 = GROUPBY_QUERY4.format(
        queues["groupby_query4"], em_queues["groupby"], queues["applier_query4"]
    )

    em_groupby = EM_GROUPBY.format(
        em_queues["groupby"],
        [
            queues["groupby_query1"],
            queues["groupby_query2"],
            queues["groupby_query3"],
            queues["groupby_query4"],
        ],
        em_queues["appliers"],
        status_queues["new_clients"],
    )

    return groupby1, groupby2, groupby3, groupby4, em_groupby


def init_results_verifier(queues, em_queues, status_queues):
    results_verifier = RESULTS_VERIFIER.format(
        queues["results_verifier"], em_queues["results_verifier"]
    )

    em_results = EM_RESULTS.format(
        em_queues["results_verifier"],
        queues["results_verifier"],
        status_queues["new_clients"],
    )

    return results_verifier, em_results


def init_session_manager(queues, max_clients):
    return SESSION_MANAGER.format(
        max_clients, queues["session_manager"], queues["receiver"]
    )


if __name__ == "__main__":
    main()
