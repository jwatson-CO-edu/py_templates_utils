########## INIT ####################################################################################

##### Imports #####
### Standard ###
import subprocess, os
from pprint import pprint



########## HELPER FUNCTIONS ########################################################################

def get_ordered_students( listPath ):
    """ Prep student list for searching """
    students = list()
    with open( listPath, 'r' ) as f:
        lines = f.readlines()
        for line in lines:
            if len( line ) > 2:
                students.append( line.replace('-','').replace("'",'').replace(",",'').strip().lower().split() )
    students.sort( key = lambda x: x[-1] )
    return students


def get_student_str( stdntPair ):
    """ Get a prefix that orders the folders """
    return f"{stdntPair[0].lower()}{stdntPair[1].lower()}"


def get_student_name( stdntPair ):
    """ Get a prefix that orders the folders """
    first = f"{stdntPair[1][0].upper()}{stdntPair[1][1:]}"
    secnd = f"{stdntPair[0][0].upper()}{stdntPair[0][1:]}"
    return f"{first} {secnd}"


def multisplit( inptStr, splitLst ):
    """ Split on multiple strings """
    parts = [f"{inptStr}",]
    for spltStr in splitLst:
        nuParts = list()
        for part in parts:
            nuParts.extend( f"{part}".split( spltStr ) )
        parts = nuParts[:]
    return parts


def disp_text_header( titleStr, emphasis, preNL = 0, postNL = 0 ):
    """ Make the headers that you like so much """
    emphStr = '#'*int(emphasis)
    newLine = '\n'
    print( f"{newLine*int(preNL) if preNL else ''}{emphStr} {titleStr} {emphStr}{newLine*int(postNL) if postNL else ''}" )


########## SUBPROCESS ##############################################################################

def run_cmd( ruleStr, timeout_s = 0, suppressErr = False ):
    """ Run a Bash command as a subprocess """
    # NOTE: If the client code requests a timeout, then there will be less feedback!

    if timeout_s:
        out = subprocess.check_output( ruleStr, 
                                       stdout  = subprocess.PIPE, 
                                       stderr  = subprocess.STDOUT,
                                       shell   = True,
                                       timeout = int( timeout_s ) )
        return { 
            'cmd': ruleStr,
            'out': out.decode(),
        }
    else:
        process = subprocess.Popen( ruleStr, 
                                    shell   = True,
                                    stdout  = subprocess.PIPE, 
                                    stderr  = subprocess.PIPE )

        # wait for the process to terminate
        out, err = process.communicate()
        if (process.returncode != 0) and (not suppressErr):
            print( f"ERROR:\n{err}" )
        return { 
            'cmd': ruleStr,
            'out': out.decode(),
            'err': err.decode(),
            'rtn': process.returncode,
        }



########## GRADLE ##################################################################################

def gradle_test( dirPrefix = "" ):
    """ Run all Gradle tests """
    if len( dirPrefix ):
        dirPrefix = f"./{dirPrefix}"
    res = run_cmd( f"{dirPrefix}/gradlew test -p {dirPrefix}", suppressErr = True )
    if "gradlew: not found" in res['err']:
        res = run_cmd( f"gradle test -p {dirPrefix}" )
    return res


def gradle_build_clean( dirPrefix = "" ):
    """ Clean then Build Gradle project """
    if len( dirPrefix ):
        dirPrefix = f"./{dirPrefix}"
    res = run_cmd( f"{dirPrefix}/gradlew clean build -p {dirPrefix}", suppressErr = True )
    if "gradlew: not found" in res['err']:
        res = run_cmd( f"gradle clean build -p {dirPrefix}" )
    return res



########## GIT #####################################################################################

def git_clone( repoStr ):
    """ Clone the `repoStr` to the current dir """
    return run_cmd( f"git clone {repoStr}", suppressErr = True )


def scrape_repo_address( htPath ):
    """ Extract the repo from the Canvas HTML if it is a github address, Otherwise return `None` """
    with open( htPath ) as f:
        lines = f.readlines()
        for line in lines:
            parts = multisplit( line, ['<','>','"',] )
            for part in parts:
                if ("github.com" in part) and (' ' not in part):
                    parts_i = part.split('?')
                    part_i  = parts_i[0]
                    return part_i.replace( "https://github.com/", "git@github.com:" ).replace( "/tree/main", "" )
    return None


def get_folder_from_github_addr( gitAddr ):
    """ What folder will git put the repo in? """
    parts = str( gitAddr ).split('/')
    return parts[-1].replace('.git','')


########## MAIN ####################################################################################


if __name__ == "__main__":

    _LIST_PATHS = ["ugrads.txt", "grads.txt",]

    htPaths = [path for path in os.listdir() if ".html" in path]

    for _LIST_PATH in _LIST_PATHS:
        disp_text_header( f"About to process {_LIST_PATH}!!", 10, preNL = 1, postNL = 1 )
        students = get_ordered_students( _LIST_PATH )
        for student in students:

            ### Fetch Submission ###
            stdStr = get_student_str( student )
            stdNam = get_student_name( student )
            stPath = None
            disp_text_header( f"Grading {stdNam} ...", 5, preNL = 1, postNL = 0 )
            for hPath in htPaths:
                if stdStr in hPath:
                    stPath = hPath
                    break
            if stPath is None:
                disp_text_header( f"There was NO SUBMISSION for {stdNam}!!", 5, preNL = 0, postNL = 1 )
                continue

            ### Fetch Repo ###
            stAddr = scrape_repo_address( stPath )
            stdDir = get_folder_from_github_addr( stAddr )

            print( f"About to clone {stAddr} to {stdDir}!" )
            clonRs = git_clone( stAddr )
            if (clonRs['rtn'] != 0) and ("not an empty directory" not in clonRs['err']):
                pprint( clonRs )
                disp_text_header( f"GitHub FAILURE for {stdNam}!!", 5, preNL = 0, postNL = 1 )
                continue

            ### Run Repo Checks ###
            print( f"About to run Gradle tests ..." )
            res = gradle_test( dirPrefix = stdDir )
            # pprint( res )

            print( f"About to build Gradle project ..." )
            res = gradle_build_clean( dirPrefix = stdDir )
            # pprint( res )


            disp_text_header( f"{stdNam}, Eval completed!", 5, preNL = 0, postNL = 1 )

        disp_text_header( f"COMPLETED {_LIST_PATH}!!", 10, preNL = 1, postNL = 2 )
    
