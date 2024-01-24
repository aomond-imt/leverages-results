import copy
import os
from os.path import exists

from joblib import Memory
import numpy as np
import pandas as pd
import yaml
import csv

STRESS_CONSO = 1.358
columns = ["leverage", "n_obs", "n_hops", "n_deps", "res"]
memory = Memory("/tmp", verbose=0)


# @memory.cache
def get_df():
    results_dir = "simulation_metrics"
    esds_results = []
    for expe_dir in os.listdir(results_dir):
        rel_expe_dir = f"{results_dir}/{expe_dir}"
        leverage, n_obs, n_hops, n_deps = expe_dir.split("-")
        size = int(n_obs)*int(n_hops) + 1
        results_runs = {
            "comms": [],
            "time": [],
            "idle": [],
            "reconf": [],
            "static": [],
            "dynamic": [],
            "total": []
        }
        for run_num in range(200):
            rel_run_num_dir = f"{rel_expe_dir}/{run_num}"
            if not exists(rel_run_num_dir) or len(os.listdir(rel_run_num_dir)) != int(size):
                continue
            accumulated_results = {
                "comms": 0,
                "time": 0,
                "idle": 0,
                "reconf": 0,
                "static": 0,
                "dynamic": 0,
                "total": 0
            }
            for node_num in range(int(size)):
                with open(f"{rel_run_num_dir}/{node_num}.yaml") as f:
                    res = yaml.safe_load(f)
                reconf = res["tot_reconf_duration"]*STRESS_CONSO
                idle = res["node_cons"] - reconf
                accumulated_results["comms"] += res["comms_cons"]
                accumulated_results["time"] = max(res["global_termination_time"], accumulated_results["time"])
                accumulated_results["reconf"] += reconf
                accumulated_results["static"] += idle
                accumulated_results["dynamic"] += reconf + res["comms_cons"]
                accumulated_results["total"] += idle + reconf + res["comms_cons"]

            results_runs["comms"].append(accumulated_results["comms"])
            results_runs["time"].append(accumulated_results["time"])
            results_runs["reconf"].append(accumulated_results["reconf"])
            results_runs["static"].append(accumulated_results["static"])
            results_runs["dynamic"].append(accumulated_results["dynamic"])
            results_runs["total"].append(accumulated_results["total"])

        np_results = {
            "comms": {"mean": np.array(results_runs['comms']).mean(), "std": np.array(results_runs['comms']).std()},
            "reconf": {"mean": np.array(results_runs['reconf']).mean(), "std": np.array(results_runs['reconf']).std()},
            "time": {"mean": np.array(results_runs['time']).mean(), "std": np.array(results_runs['time']).std()},
            "static": {"mean": np.array(results_runs['static']).mean(), "std": np.array(results_runs['static']).std()},
            "dynamic": {"mean": np.array(results_runs['dynamic']).mean(), "std": np.array(results_runs['dynamic']).std()},
            "total": {"mean": np.array(results_runs['total']).mean(), "std": np.array(results_runs['total']).std()},
        }

        esds_results.append(
            (leverage, n_obs, n_hops, n_deps, np_results)
        )

    return pd.DataFrame(
        esds_results,
        columns=columns
    )


net = ["clique", "star", "grid", "ring", "chain"]
rn = ["no_rn", "rn_agg", "rn_not_agg"]
colors = ["blue", "orange"]
srv = ["fav", "nonfav"]

srv_conv = {
    "fav": "best",
    "nonfav": "worst",
}

rn_conv = {
    "no_rn": {"fav": "No RN", "nonfav": "No RN"},
    "rn_agg": {"fav": "best", "nonfav": "worst"},
    "rn_not_agg": {"fav": "worst", "nonfav": "best"},
}

unit = {
    "total": 1000,
    "dynamic": 1,
    "time": 3600
}


# indexes = [("fav","no_rn"), ("nonfav","no_rn"), ("fav","rn_agg"), ("nonfav","rn_agg"), ("fav","rn_not_agg"), ("nonfav","rn_not_agg")]
indexes = [("fav","clique"), ("nonfav","clique"), ("fav","star"), ("nonfav","star"), ("fav","grid"), ("nonfav","grid"), ("fav","ring"), ("nonfav","ring"), ("fav","chain"), ("nonfav","chain")]
indexes_rn = [("No RN", "fav"), ("No RN", "nonfav"), ("best", "fav"), ("best", "nonfav"), ("worst", "fav"), ("worst", "nonfav")]


def p(gb, energy_type):
    list_gb = copy.deepcopy(columns)
    list_gb.remove("res")
    list_gb.remove(gb)
    list_gb = ["leverage"]
    df = get_df()

    df_gb = [*df.groupby(list_gb)]
    for key, pandas_vals in df_gb:
        for res in pandas_vals.values:
            leverage, n_obs, n_hops, n_deps, np_results = res
            div = unit[energy_type]
            csvwriter.writerow([
                f"{np_results[energy_type]['mean'] / div:.2f}",
                f"{np_results[energy_type]['std'] / div:.2f}",
                leverage,
                n_obs,
                n_hops,
                n_deps,
                0
            ])


if __name__ == "__main__":
    for energy_type in ["total", "dynamic", "time"]:
        csvfile_name = f"e_{energy_type}.csv"
        csvfile = open(csvfile_name, "w")
        csvwriter = csv.writer(csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(["energy_mean", "energy_std", "leverage", "n_obs", "n_hops", "n_deps", "srv_tplgy_index"])
        p("n_obs", energy_type)
        csvfile.close()
        print(f"csv: {csvfile_name}")
