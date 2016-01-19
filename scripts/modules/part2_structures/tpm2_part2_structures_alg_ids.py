# -*- coding: utf-8 -*-

from modules import utils


# Class for internal representation of Algorithm IDs
class AlgorithmID:
    name = ""
    short_name = ""
    value = ""
    type = ""
    dependence = ""

    # Initialises object with given parameters
    def __init__(self, name, value, alg_type, dependence):
        self.name = name
        self.short_name = utils.extract_alg_name(name)
        self.value = value
        self.type = alg_type
        self.dependence = dependence


# Class containing mapping from algorithm types to list of corresponding algorithm IDs
class AlgorithmIDs:

    def __init__(self):
        self.tpm_alg_ids = dict()

    # Extract list of algorithm IDs for each algorithm type
    # Parameters:
    # table - internal representation of the table to extract algorithm IDs from
    def extract(self, table):

        # initialization
        self.tpm_alg_ids['!ALG'] = []
        self.tpm_alg_ids['!ALG.A'] = []
        self.tpm_alg_ids['!ALG.AX'] = []
        self.tpm_alg_ids['!ALG.AXN'] = []
        self.tpm_alg_ids['!ALG.AE'] = []
        self.tpm_alg_ids['!ALG.AEH'] = []
        self.tpm_alg_ids['!ALG.AM'] = []
        self.tpm_alg_ids['!ALG.AE.AX'] = []
        self.tpm_alg_ids['!ALG.AO'] = []
        self.tpm_alg_ids['!ALG.O'] = []
        self.tpm_alg_ids['!ALG.S'] = []
        self.tpm_alg_ids['!ALG.SE'] = []
        self.tpm_alg_ids['!ALG.H'] = []
        self.tpm_alg_ids['!ALG.HM'] = []
        self.tpm_alg_ids['!ALG.X'] = []
        self.tpm_alg_ids['!ALG.E'] = []
        # tpm_alg_ids[algorithm type] = list of algorithm IDs

        for row in table.rows:
            alg_name = row[0]
            value = row[1]
            alg_type = row[2]
            dependence = row[3]

            if "A" in alg_type:
                self.tpm_alg_ids['!ALG.A'].append(AlgorithmID(alg_name, value, alg_type, dependence))

            if alg_type == u'S':  # do not change to: "S" in alg_type
                self.tpm_alg_ids['!ALG.S'].append(AlgorithmID(alg_name, value, alg_type, dependence))

            if "S" in alg_type and "E" in alg_type:
                self.tpm_alg_ids['!ALG.SE'].append(AlgorithmID(alg_name, value, alg_type, dependence))

            if "O" in alg_type:
                self.tpm_alg_ids['!ALG.O'].append(AlgorithmID(alg_name, value, alg_type, dependence))

            if alg_type == u'H':  # do not change to: "H" in alg_type
                if alg_name != u'TPM_ALG_SHA':
                    self.tpm_alg_ids['!ALG.H'].append(AlgorithmID(alg_name, value, alg_type, dependence))

            if "H" in alg_type and "M" in alg_type:
                self.tpm_alg_ids['!ALG.HM'].append(AlgorithmID(alg_name, value, alg_type, dependence))

            if "X" in alg_type:
                self.tpm_alg_ids['!ALG.X'].append(AlgorithmID(alg_name, value, alg_type, dependence))

            if "E" in alg_type:
                self.tpm_alg_ids['!ALG.E'].append(AlgorithmID(alg_name, value, alg_type, dependence))

            if "A" in alg_type and "X" in alg_type and "N" not in alg_type:
                self.tpm_alg_ids['!ALG.AX'].append(AlgorithmID(alg_name, value, alg_type, dependence))
                # self.tpm_alg_ids['!ALG.AE.AX'].append([alg_name, value, dependence])

            if "A" in alg_type and "E" in alg_type and "H" not in alg_type:
                self.tpm_alg_ids['!ALG.AE'].append(AlgorithmID(alg_name, value, alg_type, dependence))
                # self.tpm_alg_ids['!ALG.AE.AX'].append([alg_name, value, dependence])

            if "A" in alg_type and "M" in alg_type:
                self.tpm_alg_ids['!ALG.AM'].append(AlgorithmID(alg_name, value, alg_type, dependence))

            if "A" in alg_type and "O" in alg_type:
                self.tpm_alg_ids['!ALG.AO'].append(AlgorithmID(alg_name, value, alg_type, dependence))

            if "A" in alg_type and "X" in alg_type and "N" in alg_type:
                self.tpm_alg_ids['!ALG.AXN'].append(AlgorithmID(alg_name, value, alg_type, dependence))

            if "A" in alg_type and "E" in alg_type and "H" in alg_type:
                self.tpm_alg_ids['!ALG.AEH'].append(AlgorithmID(alg_name, value, alg_type, dependence))
        # end of loop -  for row in table.rows:

        return self.tpm_alg_ids
    # end of method - extract(self, table): (see Table 2:9 for reference)
