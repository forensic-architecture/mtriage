def get_all_media(utils, additionals):
    cmpDict = {
        "sel1": {
            f"{Analyser.DATA_EXT}": {
                "el1": f"{utils.TEMP_ELEMENT_DIR}/sel1/{Analyser.DATA_EXT}/el1",
                "el2": f"{utils.TEMP_ELEMENT_DIR}/sel1/{Analyser.DATA_EXT}/el2",
            },
            f"{Analyser.DERIVED_EXT}": {
                "an1": {
                    "el1": f"{utils.TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/an1/el1",
                    "el2": f"{utils.TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/an1/el2",
                },
                "an2": {
                    "el2": f"{utils.TEMP_ELEMENT_DIR}/sel1/{Analyser.DERIVED_EXT}/an2/el2"
                },
            },
        },
        "sel2": {
            f"{Analyser.DATA_EXT}": {
                "el4": f"{utils.TEMP_ELEMENT_DIR}/sel2/{Analyser.DATA_EXT}/el4",
                "el5": f"{utils.TEMP_ELEMENT_DIR}/sel2/{Analyser.DATA_EXT}/el5",
                "el6": f"{utils.TEMP_ELEMENT_DIR}/sel2/{Analyser.DATA_EXT}/el6",
            },
            f"{Analyser.DERIVED_EXT}": {},
        },
    }
    mediaDict = additionals.emptyAnalyser._Analyser__get_all_media()
    assert utils.dictsEqual(cmpDict, mediaDict)
