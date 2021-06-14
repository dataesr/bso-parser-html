import project.server.main.parsers as parsers

MAPPING = {
    '10.1016': {"func": parsers.parse_elsevier},
    '10.1038': {
        "func": parsers.parse_springer,
        "cbs": [parsers.parse_nature]
    },
    '10.1007': {
        "func": parsers.parse_springer,
        "cbs": [parsers.parse_nature]
        },
    '10.1140': {"func": parsers.parse_springer},
    '10.4000': {"func": parsers.parse_openedition},
    '10.1080': {"func": parsers.parse_tandf},
    '10.1057': {"func": parsers.parse_tandf},
    '10.4081': {"func": parsers.parse_tandf},
    '10.3917': {"func": parsers.parse_cairn},
    '10.1002': {"func": parsers.parse_wiley},
    '10.1111': {"func": parsers.parse_wiley},
    '10.1142': {"func": parsers.parse_wiley},
    '10.1089': {"func": parsers.parse_wiley},
    '10.1051': {"func": parsers.parse_aanda},
    '10.1021': {"func": parsers.parse_acs},
    '10.1186': {
        "func": parsers.parse_springer,
        "cbs": [parsers.parse_nature, parsers.parse_wiley]
    },
    '10.1103': {"func": parsers.parse_aps},
    '10.1088': {"func": parsers.parse_iop},
    '10.3847': {"func": parsers.parse_iop},
    '10.3389': {"func": parsers.parse_frontiers},
    '10.1039': {"func": parsers.parse_rsc},
    '10.1371': {"func": parsers.parse_plos},
    '10.1017': {"func": parsers.parse_cambridge},
    '10.3390': {"func": parsers.parse_mdpi},
    '10.1093': {"func": parsers.parse_oup},
    '10.1063': {"func": parsers.parse_aip},
    '10.1121': {"func": parsers.parse_aip},
    '10.1117': {"func": parsers.parse_spie},
    '10.5194': {"func": parsers.parse_atmos_chem},
    '10.1136': {"func": parsers.parse_bmj},
    '10.1177': {"func": parsers.parse_sagepub},
    '10.7202': {"func": parsers.parse_erudit},
    '10.3233': {"func": parsers.parse_ios},
    '10.2139': {"func": parsers.parse_ssrn},
    '10.1364': {"func": parsers.parse_ssrn},
    '10.1515': {"func": parsers.parse_sciendo},
    '10.1097': {"func": parsers.parse_sciendo},
    '10.1155': {"func": parsers.parse_hindawi},
    '10.1109': {"func": parsers.parse_ieee, "cb_soup2": True},
    '10.7873': {"func": parsers.parse_ieee, "cb_soup2": True},
    '10.1145': {"func": parsers.parse_acm},
}
