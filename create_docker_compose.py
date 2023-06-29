import sys, json
from init_config import *


def main():
    if len(sys.argv) != 2:
        print("Error: Missing random_fails")
        return
    try:
        random_fails = bool(int(sys.argv[1]))
    except ValueError:
        print("Error: random_fails must be 1 or 0.")
    
    with open("config.json") as f:
        json_config = json.load(f)

    queues = json_config["config"]["queues"]
    em_queues = json_config["config"]["eof_manager_queues"]
    status_queues = json_config["config"]["status_queues"]
    amount_nodes = json_config["config"]["amount_nodes"]
    max_clients = json_config["config"]["max_clients"]
    restarter_config = json_config["config"]["process_restarter"]

    accepters = init_accepters(queues, em_queues, status_queues, amount_nodes)

    joiner_stations, joiner_weather, em_joiners = init_joiners(
        queues, em_queues, status_queues, amount_nodes
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
        queues, em_queues, status_queues, amount_nodes
    )

    results_verifier, em_results = init_results_verifier(
        queues, em_queues, status_queues
    )

    session_manager = init_session_manager(queues, max_clients, em_queues)

    process_restarter = init_process_restarters(restarter_config, amount_nodes)

    process_stopper = init_process_stopper(random_fails, amount_nodes, restarter_config["n_processes"])

    compose = (
        INIT_DOCKER.format()
        .replace("<ACCEPTER>", accepters)
        .replace("<PROCESS_RESTARTER>", process_restarter)
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
        .replace("<PROCESS_STOPPER>", process_stopper)
    )

    with open("docker-compose-server.yaml", "w") as compose_file:
        compose_file.write(compose)


def init_accepters(queues, em_queues, status_queues, amount_nodes):
    accepters = ""
    port = 12345

    for i in range(1, amount_nodes["accepter"] + 1):
        accepters += ACCEPTER.format(
            i,
            i,
            i,
            port,
            queues["joiners"]["stations"],
            queues["joiners"]["weather"],
            [
                (
                    queues["groupby_query4"], 
                    amount_nodes["groupby"]["groupby_query4"]
                ),
            ],
            em_queues["joiners"],
            status_queues["new_clients"],
            queues["session_manager"]["init_session"],
            queues["accepter"],
            amount_nodes["joiner_stations"],
            amount_nodes["joiner_weather"],
            amount_nodes["sharding_amount"],
            port,
            port,
        )

        port += 1

    return accepters


def init_joiners(queues, em_queues, status_queues, amount_nodes):
    joiner_stations = ""
    for i in range(1, amount_nodes["joiner_stations"] + 1):
        joiner_stations += JOINER_STATIONS.format(
            i,
            i,
            queues["joiners"]["stations"],
            queues["joiners"]["join_trip_stations"],
            em_queues["joiners"],
            queues["filters"]["exchange"],
            [
                queues["filters"]["filter_year"],
                queues["filters"]["filter_distance"],
            ],
            [
                amount_nodes["filter_year"],
                amount_nodes["filter_distance"],
            ],
            i
        )
    joiner_weather = ""
    for i in range(1, amount_nodes["joiner_weather"] + 1):
        joiner_weather += JOINER_WEATHER.format(
            i,
            i,
            queues["joiners"]["weather"],
            queues["joiners"]["join_trip_weather"],
            em_queues["joiners"],
            queues["filters"]["exchange"],
            [
                queues["filters"]["filter_pretoc"],
            ],
            [amount_nodes["filter_pretoc"]],
            i
        )

    em_joiners = EM_JOINERS.format(
        em_queues["joiners"],
        em_queues["filters"],
        queues["joiners"]["stations"],
        queues["joiners"]["weather"],
        queues["joiners"]["join_trip_stations"],
        queues["joiners"]["join_trip_weather"],
        status_queues["new_clients"],
        amount_nodes["joiner_stations"],
        amount_nodes["joiner_weather"],
    )

    return joiner_stations, joiner_weather, em_joiners


def init_filters(queues, em_queues, status_queues, amount_nodes):
    filters_q = queues["filters"]

    filters_pretoc = ""
    for i in range(1, amount_nodes["filter_pretoc"] + 1):
        filters_pretoc += FILTER_PRETOC.format(
            i,
            i,
            filters_q["exchange"],
            filters_q["filter_pretoc"],
            em_queues["filters"],
            [
                queues["groupby_query1"], 
                amount_nodes["groupby"]["groupby_query1"]
            ],
            i,
        )

    filters_year = ""
    for i in range(1, amount_nodes["filter_year"] + 1):
        filters_year += FILTER_YEAR.format(
            i,
            i,
            filters_q["exchange"],
            filters_q["filter_year"],
            em_queues["filters"],
            [
                queues["groupby_query2"], 
                amount_nodes["groupby"]["groupby_query2"]
            ],
            i,
        )

    filters_distance = ""
    for i in range(1, amount_nodes["filter_distance"] + 1):
        filters_year += FILTER_DISTANCE.format(
            i,
            i,
            filters_q["exchange"],
            filters_q["filter_distance"],
            em_queues["filters"],
            [
                queues["groupby_query3"], 
                amount_nodes["groupby"]["groupby_query3"]
            ],
            i,
        )

    em_filters = EM_FILTERS.format(
        em_queues["filters"],
        filters_q["exchange"],
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
    appliers_queue = queues["appliers"]

    appliers_query1 = ""
    for i in range(1, amount_nodes["applier_query1"] + 1):
        appliers_query1 += APPLIER_QUERY1.format(
            i,
            i,
            appliers_queue["exchange"],
            appliers_queue["applier_query1"],
            em_queues["appliers"],
            queues["results_verifier"],
            i,
        )

    appliers_query2 = ""
    for i in range(1, amount_nodes["applier_query2"] + 1):
        appliers_query2 += APPLIER_QUERY2.format(
            i,
            i,
            appliers_queue["exchange"],
            appliers_queue["applier_query2"],
            em_queues["appliers"],
            queues["results_verifier"],
            i,
        )

    appliers_query3 = ""
    for i in range(1, amount_nodes["applier_query3"] + 1):
        appliers_query3 += APPLIER_QUERY3.format(
            i,
            i,
            appliers_queue["exchange"],
            appliers_queue["applier_query3"],
            em_queues["appliers"],
            queues["results_verifier"],
            i,
        )

    appliers_query4 = ""
    for i in range(1, amount_nodes["applier_query4"] + 1):
        appliers_query4 += APPLIER_QUERY4.format(
            i,
            i,
            appliers_queue["exchange"],
            appliers_queue["applier_query4"],
            em_queues["appliers"],
            queues["results_verifier"],
            i,
        )

    em_appliers = EM_APPLIERS.format(
        em_queues["appliers"],
        appliers_queue["exchange"],
        [
            appliers_queue["applier_query1"],
            appliers_queue["applier_query2"],
            appliers_queue["applier_query3"],
            appliers_queue["applier_query4"],
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


def init_groupby(queues, em_queues, status_queues, amount_nodes):
    groupby1 = ""
    for i in range(1, amount_nodes["groupby"]["groupby_query1"] + 1):
        groupby1 += GROUPBY_QUERY1.format(
            i,
            i,
            queues["groupby_query1"], 
            em_queues["groupby"], 
            queues["appliers"]["exchange"],
            queues["appliers"]["applier_query1"],
            amount_nodes["applier_query1"],
            i
        )

    groupby2 = ""
    for i in range(1, amount_nodes["groupby"]["groupby_query2"] + 1):
        groupby2 += GROUPBY_QUERY2.format(
            i,
            i,
            queues["groupby_query2"], 
            em_queues["groupby"], 
            queues["appliers"]["exchange"],
            queues["appliers"]["applier_query2"],
            amount_nodes["applier_query2"],
            i
        )


    groupby3 = ""
    for i in range(1, amount_nodes["groupby"]["groupby_query3"] + 1):
        groupby3 += GROUPBY_QUERY3.format(
            i,
            i,
            queues["groupby_query3"], 
            em_queues["groupby"], 
            queues["appliers"]["exchange"],
            queues["appliers"]["applier_query3"],
            amount_nodes["applier_query3"],
            i
        )

    groupby4 = ""
    for i in range(1, amount_nodes["groupby"]["groupby_query4"] + 1):
        groupby4 += GROUPBY_QUERY4.format(
            i,
            i,
            queues["groupby_query4"], 
            em_queues["groupby"], 
            queues["appliers"]["exchange"],
            queues["appliers"]["applier_query4"],
            amount_nodes["applier_query4"],
            i
        )

    em_groupby = EM_GROUPBY.format(
        em_queues["groupby"],
        [
            (queues["groupby_query1"], amount_nodes["groupby"]["groupby_query1"]),
            (queues["groupby_query2"], amount_nodes["groupby"]["groupby_query2"]),
            (queues["groupby_query3"], amount_nodes["groupby"]["groupby_query3"]),
            (queues["groupby_query4"], amount_nodes["groupby"]["groupby_query4"]),
        ],
        em_queues["appliers"],
        status_queues["new_clients"],
    )

    return groupby1, groupby2, groupby3, groupby4, em_groupby


def init_results_verifier(queues, em_queues, status_queues):
    results_verifier = RESULTS_VERIFIER.format(
        queues["results_verifier"],
        em_queues["results_verifier"],
        queues["session_manager"]["init_session"],
    )

    em_results = EM_RESULTS.format(
        em_queues["results_verifier"],
        queues["results_verifier"],
        status_queues["new_clients"],
    )

    return results_verifier, em_results


def init_session_manager(queues, max_clients, em_queues):
    return SESSION_MANAGER.format(
        max_clients,
        queues["session_manager"]["init_session"],
        queues["accepter"],
        em_queues["joiners"],
    )


def init_process_restarters(restarter_config, amount_nodes):
    process_restarter = ""
    containers_keep_alive = get_containers_keep_alive(amount_nodes)
    for i in range(restarter_config["n_processes"]):
        process_restarter += PROCESS_RESTARTER.format(
            i,
            i,
            i,
            restarter_config["n_processes"],
            containers_keep_alive,
            restarter_config["network_problems"],
            restarter_config["ip_base"],
            restarter_config["ip_base"][0:-1]
            + str(int(restarter_config["ip_base"].split(".")[-1]) + i),
        )
    return process_restarter


def get_containers_keep_alive(amount_nodes):
    containers_keep_alive = []
    for i in range(amount_nodes["accepter"]):
        containers_keep_alive.append("accepter_" + str(i + 1))

    for i in range(amount_nodes["filter_year"]):
        containers_keep_alive.append("filter_year_" + str(i + 1))
    for i in range(amount_nodes["filter_pretoc"]):
        containers_keep_alive.append("filter_pretoc_" + str(i + 1))
    for i in range(amount_nodes["filter_distance"]):
        containers_keep_alive.append("filter_distance_" + str(i + 1))
    containers_keep_alive.append("eof_manager_filters")

    for i in range(amount_nodes["applier_query1"]):
        containers_keep_alive.append("mean_duration_applier_1_" + str(i + 1))
    for i in range(amount_nodes["applier_query2"]):
        containers_keep_alive.append("double_year_applier_" + str(i + 1))
    for i in range(amount_nodes["applier_query3"]):
        containers_keep_alive.append("mean_distance_applier_" + str(i + 1))
    for i in range(amount_nodes["applier_query4"]):
        containers_keep_alive.append("mean_duration_applier_4_" + str(i + 1))
    containers_keep_alive.append("eof_manager_appliers")

    for i in range(amount_nodes["groupby"]["groupby_query1"]):
        containers_keep_alive.append("groupby_start_date_" + str(i + 1))
    for i in range(amount_nodes["groupby"]["groupby_query2"]):
        containers_keep_alive.append("groupby_start_station_" + str(i + 1))
    for i in range(amount_nodes["groupby"]["groupby_query3"]):
        containers_keep_alive.append("groupby_end_station_" + str(i + 1))
    for i in range(amount_nodes["groupby"]["groupby_query4"]):
        containers_keep_alive.append("groupby_all_elements_" + str(i + 1))
    containers_keep_alive.append("eof_manager_groupby")

    for i in range(amount_nodes["joiner_weather"]):
        containers_keep_alive.append("joiner_weather_" + str(i+1))
    for i in range(amount_nodes["joiner_stations"]):
        containers_keep_alive.append("joiner_stations_" + str(i+1))
    containers_keep_alive.append("eof_manager_joiners")

    containers_keep_alive.append("session_manager")

    containers_keep_alive.append("results_verifier")
    containers_keep_alive.append("eof_manager_query_results")

    return ",".join(containers_keep_alive)


def init_process_stopper(random_fails, amount_nodes, n_restarters):
    if not random_fails:
        return ""
    process_stopper = ""
    processes_to_stop = get_containers_keep_alive(amount_nodes)
    processes_to_stop += ','
    processes_to_stop += ",".join(["processes-restarter-"+str(i) for i in range(n_restarters)])
    return PROCESS_STOPPER.format(processes_to_stop)
    


if __name__ == "__main__":
    main()
