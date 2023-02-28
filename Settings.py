#!/usr/bin/python3

class Settings:
    settings = None
    FILE = "setting.conf"

    def __init__(self):
        self.gl_search_align_cmd = None
        self.mm_search_align_cmd = None
        self.fasta_db = None
        self.work_dir = None
        self.input_fasta = None
        self.host = None
        self.db = None
        self.coll_freq = None
        self.coll_interpro = None
        self.coll_goa = None
        self.uniprotx = None
        self.seed_dom = None
        self.max_iter = 2
        self.match_score = None
        self.gap_score = None
        self.mismatch_score = None
        self.nwth = None
        self.perc_len = None
        self.sim_thr = None
        self.max_seqs = 0
        self.deep_thr = 50
        self.print_gml = False
        self.use_rom = False
        self.hit_num = None
        self.min_score = None
        self.max_mum_repr = 1000
        self.minum_go = None
        self.blast_thr = 90
        self.threads = 1
        self.dom_file = None
        self.blast_file = ""
        self.out = None
        self.num_threads_for_external_process = 1

    @staticmethod
    def init():
        if Settings.settings is None:
            Settings.settings = Settings()
        return Settings.settings

    def read_settings(self, file=FILE):
        with open(file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue
                cmd, value = line.split('=', 1)
                cmd = cmd.strip()
                value = value.strip()
                if cmd == "GLSEARCHALIGN":
                    self.gl_search_align_cmd = value
                elif cmd == "MMSEARCHALIGN":
                    self.mm_search_align_cmd = value
                elif cmd == "FASTADB":
                    self.fasta_db = value
                elif cmd == "WORKDIR":
                    self.work_dir = value
                elif cmd == "INPUTFASTA":
                    self.input_fasta = value
                elif cmd == "HOST":
                    self.host = value
                elif cmd == "DB":
                    self.db = value
                elif cmd == "PERCLEN":
                    self.perc_len = float(value)
                elif cmd == "SIMTHR":
                    self.sim_thr = float(value)
                elif cmd == "MAXITER":
                    self.max_iter = int(value)
                elif cmd == "MATCHSCORE":
                    self.match_score = float(value)
                elif cmd == "GAPSCORE":
                    self.gap_score = float(value)
                elif cmd == "MISMATCHSCORE":
                    self.mismatch_score = float(value)
                elif cmd == "NWTH":
                    self.nwth = float(value)
                elif cmd == "FREQ":
                    self.coll_freq = value
                elif cmd == "INTERPRO":
                    self.coll_interpro = value
                elif cmd == "GOA":
                    self.coll_goa = value
                elif cmd == "UNIPROTX":
                    self.uniprotx = value
                elif cmd == "MAXSEQS":
                    self.max_seqs = int(value)
                elif cmd == "DEEPTHR":
                    self.deep_thr = float(value)
                elif cmd == "HITNUM":
                    self.hit_num = int(value)
                elif cmd == "MINSCORE":
                    self.min_score = float(value)
                elif cmd == "MAXNUMREPR":
                    self.max_num_repr = int(value)
                    if self.max_seqs == 0:
                        self.max_seqs = 10 * self.max_num_repr
                elif cmd == "MINUMGO":
                    self.minum_go = int(value)
                elif cmd == "BLASTTHR":
                    self.blast_thr = float(value)
        if self.max_seqs == 0:
            self.max_seqs = 4 * self.max_num_repr

    def get_glsearch_alignment_cmd(self):
        return self.gl_search_align_cmd
    
    def get_mmsearch_alignment_cmd(self):
        return self.mm_search_align_cmd
    
    def get_fasta_db(self):
        return self.fasta_db
    
    def get_work_dir(self):
        return self.work_dir
    
    def get_input_fasta(self):
        return self.input_fasta
    
    def get_host(self):
        return self.host
    
    def get_db(self):
        return self.db
    
    def get_nwth(self):
        return self.nwth
    
    def set_nwth(self, nwth):
        self.nwth = nwth
    
    def get_collection_frequences(self):
        return self.coll_freq
    
    def get_collection_interpro(self):
        return self.coll_interpro
    
    def get_collection_goa(self):
        return self.coll_goa
    
    def get_collection_uniprotx(self):
        return self.uniprotx
    
    def get_seed_dom(self):
        return self.seed_dom
    
    def set_seed_dom(self, seed_dom):
        self.seed_dom = seed_dom
    
    def get_match_score(self):
        return self.match_score
    
    def get_gap_score(self):
        return self.gap_score
    
    def get_mismatch_score(self):
        return self.mismatch_score
    
    def get_target_perc_len(self):
        return self.perc_len
    
    def get_max_iteration(self):
        return self.max_iter
    
    def get_similarity_thr(self):
        return self.sim_thr
    
    def get_maxseqs(self):
        return self.max_seqs
    
    def get_deepthr(self):
        return self.deep_thr
    
    def get_hitnum(self):
        return self.hit_num
    
    def get_minscore(self):
        return self.min_score
    
    def get_minumgo(self):
        return self.minum_go
    
    def is_rom_used(self):
        return self.use_rom
    
    def is_printgml(self):
        return self.print_gml
    
    def set_printgml(self, printgml):
        self.print_gml = printgml
    
    def use_rom(self):
        self.use_rom = True

    def set_work_dir(self):
        if not self.use_rom:
            self.work_dir = "/dev/shm/" + self.work_dir

    def get_max_num_repr(self):
        return self.max_num_repr

    def set_max_num_repr(self, max_num_repr):
        self.max_num_repr = max_num_repr

    def get_blast_thr(self):
        return self.blast_thr

    def set_blast_thr(self, blast_thr):
        self.blast_thr = blast_thr

    def get_threads(self):
        return self.threads

    def set_threads(self, threads):
        self.threads = threads

    def get_dom_file(self):
        return self.dom_file

    def set_dom_file(self, dom_file):
        self.dom_file = dom_file

    def get_blast_file(self):
        return self.blast_file

    def set_blast_file(self, blast_file):
        self.blast_file = blast_file

    def get_out(self):
        return self.out

    def set_out(self, out):
        self.out = out

    def get_num_threads_for_external_process(self):
        return self.num_threads_for_external_process

    def set_num_threads_for_external_process(self, available_cores):
        if self.threads <= 2 * available_cores / 3:
            self.num_threads_for_external_process = (2 * available_cores) // (3 * self.threads)
