#!/usr/bin/python3

from pymongo import MongoClient
import multiprocessing
import os
import sys

import DomainsThread
import Settings
import Utilities
import OptionsParser


class Domains:
    def __init__(self):
        self.args = OptionsParser.OptionsParser()
        self.setting = Settings.Settings().init()

        if not OptionsParser.OptionsParser().parse_options(self.setting):
            sys.exit(1)

        self.setting.set_work_dir()
        Utilities.create_directory(self.setting.get_work_dir())

        mongo_client = MongoClient(self.setting.get_host())
        self.database = mongo_client.get_database(self.setting.get_db())

    def run_domains(self):
        cores = multiprocessing.cpu_count()
        if self.setting.get_threads() > cores:
            raise ValueError(f"Exceeded the maximum number of available processors. Available processors: {cores}.")
        self.setting.set_num_threads_for_external_process(cores)
        os.environ["JAVA_OPTS"] = f"-Djava.util.concurrent.ForkJoinPool.common.parallelism={self.setting.get_threads()}"
        templates_for_thread_list = []
        blast_prot_map = {}
        thread_list = []

        domains_map = Utilities.read_dom_file(self.setting.get_dom_file())
        templates = list(domains_map.keys())

        if len(self.setting.get_blast_file()) > 0:
            blast_prot_map = Utilities.parse_blast_file(self.setting.get_blast_file(), self.setting)

        for i, template in enumerate(templates):
            list_num = i % self.setting.get_threads()

            if list_num == len(templates_for_thread_list):
                templates_for_thread_list.append([])

            if templates_for_thread_list[list_num] is None:
                templates_for_thread_list[list_num] = []

            if len(template) >= 5:
                templates_for_thread_list[list_num].append(template)

        for i in range(len(templates_for_thread_list)):
            thread_list.append(DomainsThread.DomainsThread(domains_map, blast_prot_map, templates_for_thread_list[i], self.database, self.setting.get_nwth()))

        results = Utilities.merge_thread_results(thread_list)

        self.write_results(results, self.database.get_collection(self.setting.get_collection_goa()))

        self.setting.get_out().close()

    def write_results(self, results, collgoa):
        for template in results.keys():
            self.setting.get_out().write(f">{template}\n")

            for uid in results[template].get_neighbor_map().keys():
                if results[template].get_prot_custers() is not None and uid in results[template].get_prot_custers():
                    for go_id in results[template].get_prot_custers()[uid].get_gos():
                        self.setting.get_out().write(f"{go_id}\t{results[template].get_neighbor_map()[uid]}\t{uid}\t0\n")
                else:
                    for doc in collgoa.find({"uid": uid}):
                        go_id = doc["goid"]

                        if uid not in results[template].get_prot_custers() or go_id not in results[template].get_prot_custers()[uid].get_gos():
                            self.setting.get_out().write(go_id + "\t" + str(results[template].get_neighbor_map()[uid]) + "\t" + uid + "\t0\n")
            self.setting.get_out().flush()

    def get_settings(self):
        return self.setting
