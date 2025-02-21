########## INIT ####################################################################################

##### Imports #####
### Standard ###
import subprocess, os, sys
from pprint import pprint
from collections import deque


##### Constants #####
_INTELLIJ_PATH  = "/opt/idea/bin/idea"
_PMD_PATH       = "/opt/pmd-bin-7.10.0/bin/pmd"
_PMD_JAVA_RULES = "OOD_Java-Rules.xml"



########## HELPER CLASSES ##########################################################################

class TColor:
    """ Terminal Colors """
    # Source: https://stackoverflow.com/a/287944
    HEADER    = '\033[95m'
    OKBLUE    = '\033[94m'
    OKCYAN    = '\033[96m'
    OKGREEN   = '\033[92m'
    WARNING   = '\033[93m'
    FAIL      = '\033[91m'
    ENDC      = '\033[0m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'



########## HELPER FUNCTIONS ########################################################################

def get_ordered_students( listPath ):
    """ Prep student list for searching """
    students = list()
    with open( listPath, 'r' ) as f:
        lines = f.readlines()
        for line in lines:
            if len( line ) > 2:
                students.append( line.replace('-','').replace("'",'').replace(",",'').strip().lower().split() )
    # students.sort( key = lambda x: x[-1] )
    students.sort( key = lambda x: x[0] )
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


def disp_text_header( titleStr : str, emphasis : int, preNL : int = 0, postNL : int = 0 ):
    """ Make the headers that you like so much """
    emphStr = '#'*int(emphasis)
    newLine = '\n'
    print( f"{newLine*int(preNL) if preNL else ''}{emphStr} {TColor.OKGREEN}{titleStr}{TColor.ENDC} {emphStr}{newLine*int(postNL) if postNL else ''}" )



########## SUBPROCESS ##############################################################################

def run_cmd( ruleStr : str, timeout_s : int = 0, suppressErr : bool = False ) -> dict:
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
            'err': "",
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
            print( f"{TColor.FAIL}ERROR:\n{err.decode()}{TColor.ENDC}" )
        return { 
            'cmd': ruleStr,
            'out': out.decode(),
            'err': err.decode(),
            'rtn': process.returncode,
        }



########## GRADLE ##################################################################################

def gradle_test( dirPrefix : str = "" ):
    """ Run all Gradle tests """
    if len( dirPrefix ):
        dirPrefix = f"./{dirPrefix}"
    cmd = f"gradle cleanTest test --no-build-cache -d -p {dirPrefix}"
    res = run_cmd( cmd, suppressErr = True )
    if len( res['err'] ):
        print( f"ERROR:\n{res['err']}" )
    logs  = f"{res['out']}"
    lines = logs.split('\n')
    for line in lines:
        if "TestEventLogger" in line:
            event = line.split("[TestEventLogger]")[-1]
            if "FAIL" in event:
                print( f"{TColor.FAIL}{event}{TColor.ENDC}" )
            elif len( event ) > 5:
                print( f"{event}" )
            # else:
            #     print( f"{line}" )
    return res


def find_main( dirPrefix : str = "" ):
    """ Return the filename with the main function if it exists, Otherwise return None """
    res = run_cmd( f'grep -nir "main(" {dirPrefix}/*' )
    out = res['out']
    if len( out ):
        lines = out.split('\n')
        for line in lines:
            path = line.split(':')[0]
            if (".JAVA" in str(path).upper()):
                return path
        return None
    else:
        return None
    

def prep_build_spec( dirPrefix : str = "", buildFile : str = "build.gradle" ):
    """ Do I need to tell Gradle where main is? """
    mainPath = find_main( dirPrefix )
    if (mainPath is not None):
        mainFile  = mainPath.split('/')[-1]
        mainPath  = mainPath.replace( f"{dirPrefix}/", "" )
        mainPath  = mainPath.replace( f"/{mainFile}", "" )
        srcDir    = f"{mainPath}"
        mainPath  = mainPath.replace( "src/", "" )
        mainClass = mainFile.split('.')[0]
        chunk = f"\nsourceSets.main.java.srcDirs = ['{srcDir}']\n"
        chunk += "\njar {" + '\n'
        chunk += "    manifest {" + '\n'

        # chunk += f"       attributes 'Main-Class': '{mainPath.replace('/','.')}.{mainClass}'" + '\n'
        # chunk += f"       attributes 'Main-Class': '{mainClass}'" + '\n'
        chunk += f"       attributes 'Main-Class': '{srcDir.split('/')[-1]}.{mainClass}'" + '\n'
        
        chunk += "    }" + '\n'
        chunk += "    from { configurations.runtimeClasspath.collect { it.isDirectory() ? it : zipTree(it) } }" + '\n'
        chunk += "}" + '\n'
        with open( os.path.join( dirPrefix, buildFile ), 'a' ) as f:
            f.write( chunk )
    else:
        print( f"NO MAIN FUNCTION found in {dirPrefix}" )


def gradle_build_clean( dirPrefix : str = "" ):
    """ Clean then Build Gradle project """
    if len( dirPrefix ):
        dirPrefix = f"./{dirPrefix}"
    res = run_cmd( f"{dirPrefix}/gradlew clean build -p {dirPrefix}", suppressErr = True )
    if "gradlew: not found" in res['err']:
        res = run_cmd( f"gradle clean build -p {dirPrefix}" )
    elif len( res['err'] ):
        print( f"ERROR:\n{res['err']}" )
    return res


def find_the_EXT( ext : str, dirPrefix : str = "" ):
    """ Return the first EXT found at the directory if it exists, Otherwise return None """
    pthLst = os.listdir( dirPrefix ) if len( dirPrefix ) else os.listdir()
    jarFil = [path for path in pthLst if f".{ext}".upper() in str(path).upper()]
    if len( jarFil ):
        return jarFil[0].split('/')[-1]
    else:
        return None


# https://docs.gradle.org/current/samples/sample_building_java_libraries.html#assemble_the_library_jar
def run_gradle_build( dirPrefix : str = "", jarDir : str = "build/libs", runEXT : str = "JAR" ):
    """ Run the Java project that resulted from the default Gradle Build """
    lukPath = os.path.join( dirPrefix, jarDir )
    jarPath = find_the_EXT( runEXT, lukPath )
    if (jarPath is not None):
        result  = run_cmd( f"java -jar {os.path.join( lukPath, jarPath )}" )
        print( f"{result['out']}" )
    else:
        result = {'out': None, 'err': None}
        print( f"There was NO JAR file at {lukPath}" )
    return result


def inspect_project( dirPrefix : str = "" ):
    """ Open IntelliJ IDEA to look at the code for yourself """
    return run_cmd( f"{_INTELLIJ_PATH} ./{dirPrefix}" )



########## GIT #####################################################################################

def git_clone( repoStr : str ):
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
                    rtnStr  = part_i.replace( "https://github.com/", "git@github.com:" ).split( "/tree" )[0]
                    print( f"Found URL: {rtnStr}" )
                    return rtnStr
    return None


def get_folder_from_github_addr( gitAddr ):
    """ What folder will git put the repo in? """
    parts = str( gitAddr ).split('/')
    return parts[-1].replace('.git','')


def get_most_recent_branch( dirPrefix : str = "", reqStr = None ):
    """ Extract the branch that was most recently created """
    cmd = f"git --git-dir=./{dirPrefix}/.git --work-tree=./{dirPrefix}/ ls-remote --heads --sort=-authordate origin"
    out = run_cmd( cmd )['out']
    rtn = ""
    if reqStr is not None:
        req = f"{reqStr}"
        for line in out.split('\n'):
            if req in line.split('\t')[-1]:
                rtn = line.split('/')[-1] 
                break
    else:
        top = out.split('\n')[0]
        rtn = top.split('/')[-1] 
    for line in out.split('\n'):
        if len( rtn ) and rtn in line:
            print( f"{TColor.BOLD}{line}{TColor.ENDC}" )
        else:
            print( f"{line}" )
    return rtn if len( rtn ) else None


def checkout_branch( dirPrefix : str = "", branchName : str = "" ):
    """ Check out the specified branch """
    cmd = f"git --git-dir=./{dirPrefix}/.git --work-tree=./{dirPrefix}/ stash save"
    run_cmd( cmd )
    cmd = f"git --git-dir=./{dirPrefix}/.git --work-tree=./{dirPrefix}/ checkout -f origin/{branchName}" # "-f": Force
    out = run_cmd( cmd )['out']
    print( f"{out}" )
    cmd = f"git --git-dir=./{dirPrefix}/.git --work-tree=./{dirPrefix}/ status" # "-f": Force
    out = run_cmd( cmd )['out']
    print( f"{out}" )



########## STATIC ANALYSIS #########################################################################

def run_PMD_report( dirPrefix : str = "", codeDir : str = "", outDir : str = "", studentStr : str = "" ):
    """ Run a PMD report for Java """
    cmd   = f"{_PMD_PATH} check -d ./{dirPrefix}/{codeDir} -R ./{_PMD_JAVA_RULES} -f text"
    out   = run_cmd( cmd )['out']
    lines =  out.split('\n')
    txt   = ""
    for line in lines:
        tx_i = line.split('/')[-1] + "\n"
        if len( tx_i ) > 5:
            txt += tx_i
    with open( f"{outDir}/{studentStr}_Java-Static-Analysis.txt", 'w' ) as f:
        f.write( txt )
    print( f"{TColor.BOLD}{txt}{TColor.ENDC}" )



########## STRING ANALYSIS #########################################################################

def levenshtein_dist( s1 : str, s2 : str ) -> int:
    """ Get the edit distance between two strings """
    # Author: Salvador Dali, https://stackoverflow.com/a/32558749
    # 1. Trivial cases: One string is empty
    if not len(s1):
        return len(s2)
    if not len(s2):
        return len(s1)
    # 2. This algo assumes second string is at least as long as the first
    if len(s1) > len(s2):
        s1, s2 = s2, s1
    # 3. Compute distance and return
    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = deque()
        distances_.append( i2+1 )
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
    return distances_.pop()
    


########## UTILITIES && FEATURES ###################################################################

def search_ranked_student_index_in_list( searchStr : str, studentLst : list[list[str]], Nrank : int = 5 ) -> list[tuple[str,int,int]]:
    """ Return a list of indices that correspond to the search string, Ranked by Levenshtein edit distance """
    rtnRank = list()
    # 0. Remove initial and trailing space
    searchStr = searchStr.strip()
    # 1. Handle <Last,First> and <First Last> inputs
    dbblSrch  = False
    if ',' in searchStr:
        dbblSrch = True
        parts    = [prt.strip().lower() for prt in searchStr.split(',')]
        lastSrch = parts[0]
        frstSrch = parts[1]
    elif ' ' in searchStr:
        dbblSrch = True
        parts    = [prt.strip().lower() for prt in searchStr.split(' ')]
        lastSrch = parts[1]
        frstSrch = parts[0]
    # 2. Rank all students
    for i, student in enumerate( studentLst ):
        stdntNm  = get_student_name( student )
        lastLowr = student[0].lower()
        frstLowr = student[1].lower()
        # A. Full Name Search, Ranked by total Levenshtein distance = first + last
        if dbblSrch:
            rtnRank.append( (stdntNm, i, levenshtein_dist( lastLowr, lastSrch )+levenshtein_dist( frstLowr, frstSrch ), ) )
        # B. Single Name Search, Ranked by min Levenshtein distance across {first,last,}
        else:
            rtnRank.append( (stdntNm, i, min(levenshtein_dist( lastLowr, searchStr ),levenshtein_dist( frstLowr, searchStr )), ) )
    rtnRank.sort( key = lambda x: x[-1] )
    rtnRank = rtnRank[ 0 : Nrank ]
    disp_text_header( f"{Nrank} Search Results", 1, 1, 0 )
    for i, student in enumerate( rtnRank ):
        print( f"\t{student[0]}, {student[-1]:02}, {i if (i>0) else '*'}" )
    disp_text_header( f"End", 1, 0, 1 )
    return rtnRank



########## MAIN ####################################################################################


if __name__ == "__main__":

    _LIST_PATHS = ["grads.txt",]
    _GET_RECENT = True
    _REPORT_DIR = "output"
    _SOURCE_DIR = "src/main/java/csci/ooad"
    _BRANCH_STR = "3"
    _N_SEARCH_R = 5

    os.makedirs( _REPORT_DIR, exist_ok = True )

    htPaths = [path for path in os.listdir() if ".html" in path]

    disp_text_header( f"Begin Evaluation of {_LIST_PATHS}", 15, preNL = 1, postNL = 2 )

    for _LIST_PATH in _LIST_PATHS:
        disp_text_header( f"About to process {_LIST_PATH}!!", 10, preNL = 1, postNL = 1 )
        students = get_ordered_students( _LIST_PATH )
        Nstdnt   = len( students )
        i        = 0
        reverse  = False
        while i < Nstdnt:
            student = students[i]

            ### Fetch Submission ###
            stdStr = get_student_str( student )
            stdNam = get_student_name( student )
            stPath = None
            disp_text_header( f"Grading {stdNam} ...", 5, preNL = 1, postNL = 0 )
            for hPath in htPaths:
                if stdStr in hPath:
                    stPath  = hPath
                    reverse = False
                    break
            if stPath is None:
                disp_text_header( f"There was NO SUBMISSION for {stdNam}!!", 5, preNL = 0, postNL = 1 )
                if not reverse:
                    i += 1
                else:
                    i -= 1
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
            print()

            ### Fetch branch ###
            if _GET_RECENT:
                print( f"About to check out recent branch ..." )
                brName = get_most_recent_branch( dirPrefix = stdDir, reqStr = _BRANCH_STR )
                checkout_branch( dirPrefix = stdDir, branchName = brName )

            ### Run Gradle Checks ###
            print( f"About to run Gradle tests ..." )
            for _ in range(2):
                res = gradle_test( dirPrefix = stdDir )
            print()

            mainSrc = find_main( dirPrefix = stdDir )
            if (mainSrc is not None):
                print( f"Main Function: {mainSrc}\n" )

                prep_build_spec( dirPrefix = stdDir, buildFile = "build.gradle" )

                print( f"About to build Gradle project ..." )
                res = gradle_build_clean( dirPrefix = stdDir )
                print()

                print( f"About to run Gradle project ..." )
                run_gradle_build( dirPrefix = stdDir, jarDir = "build/libs", runEXT = "JAR" )
                print()
            else:
                print( f"There was NO MAIN FUNCTION found in {stdDir}!!\n" )

            print( f"About to run code style checks ..." )
            disp_text_header( f"Static Analsys for {stdNam}", 3, preNL = 1, postNL = 1 )
            run_PMD_report( dirPrefix = stdDir, codeDir = _SOURCE_DIR, outDir = _REPORT_DIR, studentStr = stdStr )
            disp_text_header( f"{stdNam} Static Analsys COMPLETE", 3, preNL = 0, postNL = 1 )

            print( f"About to inspect Java project ..." )
            inspect_project( dirPrefix = stdDir )
            print()

            disp_text_header( f"{stdNam}, Eval completed!", 5, preNL = 1, postNL = 2 )

            usrCmd = input( "Press [Enter] to evaluate the next student: " ).upper()
            print()

            ## Handle user input ##
            # Quit #
            if 'Q' in usrCmd:
                disp_text_header( f"END PROGRAM", 10, preNL = 2, postNL = 1 )
                sys.exit(0)
            # Back to Previous Student #
            elif 'P' in usrCmd:
                i -= 1
                print( "^^^ PREVIOUS STUDENT ^^^" )
                reverse = True
                continue
            # Next Student List File #
            elif 'E' in usrCmd:
                print( "!///! END LIST !///!" )
                break
            # GOTO Student in Current List #
            elif 'S:' in usrCmd:
                searchStr = usrCmd.split(':')[-1].strip().lower()
                print( f"Search for {searchStr} ..." )
                ranking = search_ranked_student_index_in_list( searchStr, students, Nrank = _N_SEARCH_R )
                invalid = True
                while invalid:
                    srchCmd = input( "Press [Enter] to accept top hit or enter number of desired result, Cancel with 'c': " ).upper()
                    if len( srchCmd ):
                        try: 
                            rnkChoice = int( srchCmd )
                            invalid   = False
                        except Exception as e:
                            if srchCmd == 'c':
                                rnkChoice = -1
                                invalid   = False
                            else:
                                print( f"{srchCmd} was not a choice, Try again, {e}" )
                    else:
                        rnkChoice = 0
                        invalid   = False
                if rnkChoice >= 0:
                    i = ranking[rnkChoice][1]
                continue
            
            i += 1

        disp_text_header( f"COMPLETED {_LIST_PATH}!!", 10, preNL = 1, postNL = 2 )
    disp_text_header( f"Student Evaluation of {_LIST_PATHS} COMPLETED!!", 15, preNL = 1, postNL = 2 )