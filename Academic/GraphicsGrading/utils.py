from __future__ import annotations
########## INIT ####################################################################################

##### Imports #############################################################
### Standard ###
import time, json
now = time.time
from os import environ



########## CONFIG HELPERS ##########################################################################


def env_get( varName ):
    """ Get value from env """

    def recur( keyLst, dct ):
        if len( keyLst ) > 1:
            if keyLst[0] in dct:
                return recur( dct[ keyLst[0] ], keyLst[1:] )
            else:
                return None
        else:
            if keyLst[0] in dct:
                return dct[ keyLst[0] ]
            else:
                return None

    if isinstance( varName, list ):
        dct = None
        try:
            dct = json.loads( environ[ varName[0] ] )
            return recur( varName[1:], dct )
        except KeyError:
            print( f"There was NO VARIABLE named {varName}!" )
            return None
    else:
        try:
            return json.loads( environ[ varName ] )
        except KeyError:
            print( f"There was NO VARIABLE named {varName}!" )
            return None
        except Exception:
            return environ[ varName ]
    

def env_sto( varName, varValu ):
    """ Store value in env """
    environ[ varName ] = json.dumps( varValu )


def read_config_into_env( configJSONpath ):
    """ Open the file and read all the names into the environment, Then return the names that were read """
    config = dict()
    rtnNam = list()
    try:
        with open( configJSONpath, 'r' ) as f:
            config = json.load( f )
            if isinstance( config, dict ):
                for k, v in config.items():
                    try:
                        varNam = f"{k}"
                        env_sto( varNam, v )
                        rtnNam.append( varNam )
                    except Exception as e:
                        print( f"Error writing variable {k}-->{v}: {e}" )
            else:
                raise ValueError( f"{configJSONpath} does NOT qualify as a config file!" )
    except Exception as e:
        print( f"Cannot open file: {configJSONpath}" )
    print( f"The following environment variables are available: {rtnNam}" )
    return rtnNam