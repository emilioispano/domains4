import logging
from math import log
import os
import shutil
from typing import Dict, List, Set
from pymongo.collection import Collection
from pymongo.database import Database
from utils.Settings import Settings
from utils.ThreadData import ThreadData
from domains.DomainsThread import DomainsThread


def read_dom_file(file: str) -> Dict[str, Dict[int, Set[str]]]:
    """
    Reads a file containing domain information and returns a dictionary mapping a protein ID to a dictionary containing
    information about its domains.

    :param file: the file to read
    :return: a dictionary mapping a protein ID to a dictionary containing information about its domains
    """
    map = {}
    with open(file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = line.split("\t")
            if len(data) < 12:
                continue
            pid = data[0]
            ipr = data[11]
            p = int(data[6])
            if pid not in map:
                map[pid] = {}
            if p in map[pid]:
                map[pid][p].add(ipr)
            else:
                map[pid][p] = {ipr}
    return map


def parse_blast_file(file: str, setting: Settings) -> Dict[str, Set[str]]:
    """
    Parses a BLAST file and returns a dictionary mapping a template sequence ID to a set of subject sequence IDs.

    :param file: the BLAST file to parse
    :param setting: the settings to use
    :return: a dictionary mapping a template sequence ID to a set of subject sequence IDs
    """
    blast_map = {}
    with open(file) as f:
        for line in f:
            line = line.strip()
            if not line.startswith("T"):
                continue
            data = line.split()
            template = data[0]
            e_value = -log(float(data[10]))
            if e_value >= setting.blast_thr:
                if template not in blast_map:
                    blast_map[template] = set()
                blast_map[template].add(data[1])
    return blast_map


def merge_thread_results(domains_thread_results: Collection[DomainsThread]) -> Dict[str, ThreadData]:
    results = {}

    for dt in domains_thread_results:
        try:
            results.update(dt.get())
        except FileNotFoundError as ex:
            logging.getLogger('Utilities').error(ex)

    return results


def delete_directory(path: str) -> None:
    """
    Deletes a directory and all its contents.

    :param path: the path of the directory to delete
    """
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(path)


def clean_directory(path: str, start_dir: str) -> None:
    """
    Deletes all the contents of a directory except the starting directory itself.
    """
    for root, dirs, files in os.walk(path):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            if os.path.abspath(os.path.join(root, dir)) != start_dir:
                shutil.rmtree(os.path.join(root, dir))


def delete_file(file: str) -> None:
    os.remove(file)


def create_directory(dir: str) -> None:
    os.makedirs(dir, exist_ok=True)


def create_file(file: str) -> None:
    open(file, 'a').close()


def directory_exists(dir: str) -> bool:
    return os.path.exists(dir)


def file_exists(file: str) -> bool:
    return os.path.exists(file)


def sort_uids(map: Dict[str, float]) -> List[str]:
    tmp: Dict[float, List[str]] = {}
    uids: List[str] = []

    for uid, t in map.items():
        if t in tmp:
            tmp[t].append(uid)
        else:
            tmp[t] = [uid]

    keys = list(tmp.keys())
    keys.sort(reverse=True)

    for v in keys:
        for t in tmp[v]:
            uids.append(t)

    return uids


def read_clustering_data(file: str, database: Database, setting: dict) -> Dict[str, dict]:
    clusters: Dict[str, dict] = {}
    prot_ids: Set[str] = set()
    go_ids: Set[str] = set()
    goa_coll: Collection = database.get_collection(setting['collectionGOA'])

    if os.path.exists(file):
        with open(file) as f:
            next(f)
            repr_prot = ""
            it = 0

            for line in f:
                data = line.strip().split()

                if it > 0 and repr_prot != data[0]:
                    if repr_prot not in clusters:
                        clusters[repr_prot] = {'repr': repr_prot, 'protIds': prot_ids.copy(), 'goIds': go_ids.copy()}
                        prot_ids.clear()
                        go_ids.clear()

                repr_prot = data[0]
                prot_ids.add(data[1])

                for doc in goa_coll.find({'uid': data[1]}):
                    go_ids.add(doc['goid'])

                it += 1

    return clusters


def get_repr_to_removes(repr_score: Dict[str, float], setting: dict) -> Set[str]:
    if len(repr_score.keys()) > setting['maxNumRepr']:
        sorted_repr = sort_uids(repr_score)
        return set(sorted_repr[:len(sorted_repr) - setting['maxNumRepr']])
    else:
        return set()


def convert_sec_to_day(n: int) -> None:
    start_value = n

    days = n // (24 * 3600)

    n %= (24 * 3600)
    hours = n // 3600

    n %= 3600
    minutes = n // 60

    n %= 60
    seconds = n

    print(f"{days} d {hours} h {minutes} m {seconds} s ({start_value} s)")
