class Settings:
    settings = None
    FILE = "setting.conf"

    def __init__(self):
        self.glsearchaligncmd = None
        self.mmsearchaligncmd = None
        self.fastadb = None
        self.workdir = None
        self.inputfasta = None
        self.host = None
        self.db = None
        self.collfreq = None
        self.collinterpro = None
        self.collgoa = None
        self.uniprotx = None
        self.seed_dom = None
        self.maxiter = 2
        self.matchscore = None
        self.gapscore = None
        self.mismatchscore = None
        self.nwth = None
        self.perclen = None
        self.simthr = None
        self.maxseqs = 0
        self.deepthr = 50
        self.printgml = False
        self.use_rom = False
        self.hitnum = None
        self.minscore = None
        self.max_mum_repr = 1000
        self.minumgo = None
        self.blast_thr = 90
        self.threads = 1
        self.dom_file = None
        self.blastFile = ""
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
                    self.glsearchaligncmd = value
                elif cmd == "MMSEARCHALIGN":
                    self.mmsearchaligncmd = value
                elif cmd == "FASTADB":
                    self.fastadb = value
                elif cmd == "WORKDIR":
                    self.workdir = value
                elif cmd == "INPUTFASTA":
                    self.inputfasta = value
                elif cmd == "HOST":
                    self.host = value
                elif cmd == "DB":
                    self.db = value
                elif cmd == "PERCLEN":
                    self.perclen = float(value)
                elif cmd == "SIMTHR":
                    self.simthr = float(value)
                elif cmd == "MAXITER":
                    self.maxiter = int(value)
                elif cmd == "MATCHSCORE":
                    self.matchscore = float(value)
                elif cmd == "GAPSCORE":
                    self.gapscore = float(value)
                elif cmd == "MISMATCHSCORE":
                    self.mismatchscore = float(value)
                elif cmd == "NWTH":
                    self.nwth = float(value)
                elif cmd == "FREQ":
                    self.collfreq = value
                elif cmd == "INTERPRO":
                    self.collinterpro = value
                elif cmd == "GOA":
                    self.collgoa = value
                elif cmd == "UNIPROTX":
                    self.uniprotx = value
                elif cmd == "MAXSEQS":
                    self.maxseqs = int(value)
                elif cmd == "DEEPTHR":
                    self.deepthr = float(value)
                elif cmd == "HITNUM":
                    self.hitnum = int(value)
                elif cmd == "MINSCORE":
                    self.minscore = float(value)
                elif cmd == "MAXNUMREPR":
                    self.max_num_repr = int(value)
                    if self.maxseqs == 0:
                        self.maxseqs = 10 * self.max_num_repr
                elif cmd == "MINUMGO":
                    self.minumgo = int(value)
                elif cmd == "BLASTTHR":
                    self.blast_thr = float(value)
        if self.maxseqs == 0:
            self.maxseqs = 4 * self.max_num_repr

    def get_glsearch_alignment_cmd(self):
        return self.glsearchaligncmd
    
    def get_mmsearch_alignment_cmd(self):
        return self.mmsearchaligncmd
    
    def get_fasta_db(self):
        return self.fastadb
    
    def get_work_dir(self):
        return self.workdir
    
    def get_input_fasta(self):
        return self.inputfasta
    
    def get_host(self):
        return self.host
    
    def get_db(self):
        return self.db
    
    def get_nwth(self):
        return self.nwth
    
    def set_nwth(self, nwth):
        self.nwth = nwth
    
    def get_collection_frequences(self):
        return self.collfreq
    
    def get_collection_interpro(self):
        return self.collinterpro
    
    def get_collection_goa(self):
        return self.collgoa
    
    def get_collection_uniprotx(self):
        return self.uniprotx
    
    def get_seed_dom(self):
        return self.seed_dom
    
    def set_seed_dom(self, seed_dom):
        self.seed_dom = seed_dom
    
    def get_match_score(self):
        return self.matchscore
    
    def get_gap_score(self):
        return self.gapscore
    
    def get_mismatch_score(self):
        return self.mismatchscore
    
    def get_target_perc_len(self):
        return self.perclen
    
    def get_max_iteration(self):
        return self.maxiter
    
    def get_similarity_thr(self):
        return self.simthr
    
    def get_maxseqs(self):
        return self.maxseqs
    
    def get_deepthr(self):
        return self.deepthr
    
    def get_hitnum(self):
        return self.hitnum
    
    def get_minscore(self):
        return self.minscore
    
    def get_minumgo(self):
        return self.minumgo
    
    def is_rom_used(self):
        return self.use_rom
    
    def is_printgml(self):
        return self.printgml
    
    def set_printgml(self, printgml):
        self.printgml = printgml
    
    def use_rom(self):
        self.use_rom = True

    def set_work_dir(self):
        if not self.use_rom:
            self.workdir = "/dev/shm/" + self.workdir

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
        return self.blastFile

    def set_blast_file(self, blast_file):
        self.blastFile = blast_file

    def get_out(self):
        return self.out

    def set_out(self, out):
        self.out = out

    def get_num_threads_for_external_process(self):
        return self.num_threads_for_external_process

    def set_num_threads_for_external_process(self, available_cores):
        if self.threads <= 2 * available_cores / 3:
            self.num_threads_for_external_process = (2 * available_cores) // (3 * self.threads)
