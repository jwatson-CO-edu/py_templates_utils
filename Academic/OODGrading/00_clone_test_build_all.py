########## INIT ####################################################################################

##### Imports #####
### Standard ###
import subprocess, os, sys, platform, json, traceback
from pprint import pprint
from collections import deque
from pprint import pprint
from time import sleep


##### Constants #####
_CONFIG_PATH = 'HW_Config.json'


##### Config Helpers #####

def path_exists_fallback( pathList : list[str] ) -> str:
    """ Return the first path in the list that exists, Otherwise return `None` """
    for path in pathList:
        if os.path.isdir( os.path.dirname( path ) ):
            return path
    return None


# Get all OS information in one tuple
platform_info = platform.uname()
print( f"Platform Information:" )
pprint( platform_info )
print
_USER_SYSTEM = platform_info.system

config = None
with open( _CONFIG_PATH, 'r' ) as f:
    config = json.load(f)

try:
    ### Platform ###
    _INTELLIJ_PATH  = path_exists_fallback( config[_USER_SYSTEM]["_INTELLIJ_PATH"] )
    _PMD_PATH       = config[_USER_SYSTEM]["_PMD_PATH"]
    _GRADLE_PATH    = config[_USER_SYSTEM]["_GRADLE_PATH"]
    _EDITOR_COMMAND = config[_USER_SYSTEM]["_EDITOR_COMMAND"]
    ### Settings ###
    _PMD_JAVA_RULES = config["Settings"]["_PMD_JAVA_RULES"]
    _GET_RECENT     = config["Settings"]["_GET_RECENT"]
    _REPORT_DIR     = config["Settings"]["_REPORT_DIR"]
    _N_SEARCH_R     = config["Settings"]["_N_SEARCH_R"]
    _RUN_TESTS      = config["Settings"]["_RUN_TESTS"]
    _NUM_TESTS      = config["Settings"]["_NUM_TESTS"]
    _N_BIG_BLK      = config["Settings"]["_N_BIG_BLK"]
    _INSPECT_J      = (config["Settings"]["_INSPECT_J"] and (_INTELLIJ_PATH is not None))
    _SRCH_MARGN     = config["Settings"]["_SRCH_MARGN"]
    _OPEN_SNPPT     = config["Settings"]["_OPEN_SNPPT"]
    ### Assignment ###
    _LIST_PATHS = config["HWX"]["_LIST_PATHS"]
    _SOURCE_DIR = config["HWX"]["_SOURCE_DIR"]
    _BRANCH_STR = config["HWX"]["_BRANCH_STR"]
    _TOPIC_SRCH = config["HWX"]["_TOPIC_SRCH"]
except KeyError as err:
    print( f"\n\033[91mFAILED to load config file!, {err}\033[0m\n" )



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
        try:
            out = subprocess.check_output( ruleStr, 
                                        #    stdout  = subprocess.PIPE, 
                                            stderr  = subprocess.STDOUT,
                                            shell   = True,
                                            timeout = int( timeout_s ) )
        except subprocess.TimeoutExpired as e:
            out = ""
            print( f"Time limit of {int( timeout_s )} seconds EXPIRED for process\n{ruleStr}\n{e}\n" )
        return { 
            'cmd': ruleStr,
            'err': traceback.format_exc(),
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
    # if len( dirPrefix ):
    #     dirPrefix = f"./{dirPrefix}"
    # res = run_cmd( f"rm -rf {dirPrefix}/.idea" )
    res = run_cmd( f"{_GRADLE_PATH} clean -p {dirPrefix}", suppressErr = True )
    res = run_cmd( f"{_GRADLE_PATH} build -p {dirPrefix} -cp src", suppressErr = True )
    # cmd = f"{_GRADLE_PATH} test --no-build-cache -d -p {dirPrefix}"
    cmd = f"{_GRADLE_PATH} cleanTest test --no-build-cache -d -p {dirPrefix}"
    # cmd = f"gradle cleanTest test --scan --no-build-cache -d -p {dirPrefix}" # WAY TOO LONG
    res = run_cmd( cmd, suppressErr = True )
    if len( res['err'] ):
        print( f"ERROR:\n{res['err']}" )
    logs   = f"{res['out']}"
    lines  = logs.split('\n')
    tstLog = ""
    failed = False
    for line in lines:
        if "TestEventLogger" in line:
            event = line.split("[TestEventLogger]")[-1].rstrip()
            if len( event ) > 5:
                tstLog += f"{event}\n"
            if "FAIL" in event:
                failed = True
                print( f"{TColor.FAIL}{event}{TColor.ENDC}" )
            elif len( event ) > 5:
                print( f"{event}" )
    if failed:
        res['fail'] = tstLog
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
                    rtnStr  = part_i.replace( "https://github.com/", "git@github.com:" ).split( "/tree" )[0].split( "/pull" )[0]
                    print( f"Found URL: {rtnStr}" )
                    return rtnStr
    return None


def get_folder_from_github_addr( gitAddr ):
    """ What folder will git put the repo in? """
    parts = str( gitAddr ).split('/')
    return parts[-1].replace('.git','')


def get_most_recent_branch( dirPrefix : str = "", reqStr = None ):
    """ Extract the branch that was most recently created """
    # cmd = f"git --git-dir=./{dirPrefix}/.git --work-tree=./{dirPrefix}/ ls-remote --heads --sort=-authordate origin"
    cmd = f"git --git-dir=./{dirPrefix}/.git --work-tree=./{dirPrefix}/ ls-remote --heads --sort=-committerdate origin"
    out = run_cmd( cmd )['out']
    # print( f"{out}" )
    rtn = ""
    if reqStr is not None:
        req = f"{reqStr}"
        for line in out.split('\n'):
            if req in line.split('\t')[-1]:
                rtn = line.split('/')[-1] 
                break
    if (reqStr is None) or (not len( rtn )):
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
    # cmd = f"git --git-dir=./{dirPrefix}/.git --work-tree=./{dirPrefix}/ checkout -t origin/{branchName}" 
    cmd = f"git --git-dir=./{dirPrefix}/.git --work-tree=./{dirPrefix}/ checkout origin/{branchName}" 
    out = run_cmd( cmd )['out']
    cmd = f"git --git-dir=./{dirPrefix}/.git --work-tree=./{dirPrefix}/ pull origin {branchName}" 
    out += run_cmd( cmd )['out']
    cmd = f"git --git-dir=./{dirPrefix}/.git --work-tree=./{dirPrefix}/ status" # "-f": Force
    out += run_cmd( cmd )['out']
    print( f"{out}" )



########## STATIC ANALYSIS #########################################################################

def run_PMD_report( dirPrefix : str = "", codeDir : str = "", outDir : str = "", studentStr : str = "" ):
    """ Run a PMD report for Java """
    path  = os.path.join( dirPrefix, codeDir )
    cmd   = f"{_PMD_PATH} check -d ./{path} -R ./{_PMD_JAVA_RULES} -f text"
    res   = run_cmd( cmd )
    while ("No such file" in res['err']):
        path = os.path.dirname( path )
        cmd  = f"{_PMD_PATH} check -d ./{path} -R ./{_PMD_JAVA_RULES} -f text"
        res  = run_cmd( cmd )
    out   = res['out']
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

def levenshtein_search_dist( s1 : str, s2 : str ) -> int:
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
    if s1 in s2:
        return 0
    # 3. Compute distance and return
    distances  = range(len(s1) + 1)
    distances_ = None
    for i2, c2 in enumerate(s2):
        distances_ = deque()
        distances_.append( i2+1 )
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
    # return distances_.pop()
    return distances_.pop() + abs(len(s1)-len(s2)) # HACK


def split_lines_with_depth_change( nptStr : str ):
    """ Split the string into lines, Return lines and annotations of per-line changes in block depth """
    lines    = nptStr.split('\n')
    rtnLines = deque()
    linDepth = deque()
    reserved = ['(', ')', '{', '}', '+', '-', '*', '/', '.']
    comment  = False
    for line in lines:
        if '/*' in line:
            comment = True
        lParts = line.split("//", 1)  # Strip comments.
        lCode  = f"{lParts[0]}"
        for word in reserved:
            lCode  = lCode.replace( word, f" {word} ")
        tknLn  = lCode.split()
        dlDpth = tknLn.count('{') - tknLn.count('}')
        linDepth.append( dlDpth )
        # Handle interference betweeen line number annotation from script and multi-line comments from student
        rtnLines.append( f"// {line}" if comment else line )
        if '*/' in line:
            comment = False
    return list( rtnLines ), list( linDepth )


def grab_identified_sections_of_java_source( javaSourceStr : str, searchTerms : list[str], searchOver : int = 40 ):
    """ Attempt to grab relevant portion of code """
    lines, lnDeltaDepth = split_lines_with_depth_change( javaSourceStr )
    N = len( lines )
    depth    = 0
    covered  = set([])
    rtnLines = {
        "chunks" : list(),
        "ranges" : list(),
    }
    for i, line_i in enumerate( lines ):
        if i in covered:
            continue
        depth += lnDeltaDepth[i]
        hit = False
        for sTerm in searchTerms:
            if sTerm in line_i:
                hit = True
                break
        if hit:
            blockDex = i
            ovrDpth  = 0
            for j in range( i, min( N, i+searchOver+1 ) ):
                dDelta_j = lnDeltaDepth[j]
                if dDelta_j > 0:
                    blockDex = j
                    ovrDpth += dDelta_j
                elif dDelta_j < 0:
                    break
            bgn = i
            end = min( i+searchOver+1, N )
            if ovrDpth > 0:
                bgn = blockDex
                end = blockDex
                # Search backwards for the beginning of the block
                for j in range( blockDex, max( 0, blockDex-searchOver-1 ), -1 ):
                    if j < 0:
                        bgn = 0
                        break
                    ovrDpth -= lnDeltaDepth[j]
                    bgn      = j
                    if (ovrDpth <= 0):
                        break
                # Search forwards for the end of the block
                for j in range( blockDex, blockDex+searchOver+1 ):
                    if j >= N:
                        end = N
                        break
                    ovrDpth += lnDeltaDepth[j]
                    end      = j+1
                    if (ovrDpth <= 0):
                        break
                bgn = min( max( 0, bgn-int(searchOver/4)) , i )
                end = min( end+int(searchOver/4), N )
            covered.update( list(range(bgn,end)) )
            rtnLines['chunks'].append( lines[bgn:end] )
            rtnLines['ranges'].append( [bgn,end,] )
    return rtnLines
    




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
            rtnRank.append( (stdntNm, i, levenshtein_search_dist( lastLowr, lastSrch )+levenshtein_search_dist( frstLowr, frstSrch ), ) )
        # B. Single Name Search, Ranked by min Levenshtein distance across {first,last,}
        else:
            rtnRank.append( (stdntNm, i, min(levenshtein_search_dist( lastLowr, searchStr ),levenshtein_search_dist( frstLowr, searchStr )), ) )
    rtnRank.sort( key = lambda x: x[-1] )
    rtnRank = rtnRank[ 0 : Nrank ]
    disp_text_header( f"{Nrank} Search Results", 1, 1, 0 )
    for i, student in enumerate( rtnRank ):
        print( f"\t{student[0]}, {student[-1]:02}, {i if (i>0) else '*'}" )
    disp_text_header( f"End", 1, 0, 1 )
    return rtnRank


def run_menu( students ):
    """ Handle user input, per iteration """
    usrCmd = input( "Press [Enter] to evaluate the next student: " ).upper()
    print()
    rtnState = {
        'loop'    : "",
        'iDelta'  :  0 ,
        'index'   : -1 ,
        'reverse' : False,
    }
    ## Handle user input ##
    # Normal List Progression #
    if not len( usrCmd ):
        rtnState['iDelta'] = 1
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
                    if srchCmd == 'Q':
                        disp_text_header( f"END PROGRAM", 10, preNL = 2, postNL = 1 )
                        sys.exit(0)
                    elif srchCmd == 'C':
                        rnkChoice = -1
                        invalid   = False
                    else:
                        print( f"{srchCmd} was not a choice, Try again, {e}" )
            else:
                rnkChoice = 0
                invalid   = False
        if rnkChoice >= 0:
            print( f"Return item {ranking[rnkChoice]} at index {ranking[rnkChoice][1]}" )
            rtnState['index'] = ranking[rnkChoice][1]
        rtnState['loop'] = "continue"
    # Quit #
    elif 'Q' in usrCmd:
        disp_text_header( f"END PROGRAM", 10, preNL = 2, postNL = 1 )
        sys.exit(0)
    # Repeat Student #
    elif 'R' in usrCmd:
        print( f"<<< REPEAT {stdNam} Evaluation! <<<" )
        rtnState['loop'] = "continue"
    # Back to Previous Student #
    elif 'P' in usrCmd:
        rtnState['iDelta'] = -1
        print( "^^^ PREVIOUS STUDENT ^^^" )
        rtnState['reverse'] = True
        rtnState['loop'   ] = "continue"
    # Next Student List File #
    elif 'E' in usrCmd:
        print( "!///! END LIST !///!" )
        rtnState['loop'] = "break"

    return rtnState


def get_all_file_paths( directory ):
    # Source: https://www.google.com/search?client=firefox-b-1-lm&channel=entpr&q=python+list+of+paths+from+recursive+walk
    file_paths = []
    # print( directory )
    for dirpath, _, filenames in os.walk( directory ):
        # print( dirpath )
        for filename in filenames:
            file_path = os.path.join( dirpath, filename )
            file_paths.append( file_path )
    # print( file_paths )
    return file_paths


def grab_identified_source_chunks( srcDir : str, searchTerms : list[str], searchOver : int = 40, fileExt : str = "java" ):
    """ Get identified chunks in the code """
    rtnStr  = ""
    # jvPaths = [path for path in os.listdir( srcDir ) if f".{fileExt}".lower() in path.lower()]
    jvPaths = [path for path in get_all_file_paths( srcDir ) if f".{fileExt}".lower() in path.lower()]
    while not len( jvPaths ):
        srcDir  = os.path.dirname( srcDir )
        jvPaths = [path for path in get_all_file_paths( srcDir ) if f".{fileExt}".lower() in path.lower()]
    for path in jvPaths:
        rtnStr += f"///// {path} /////\n"
        # with open( os.path.join( srcDir, path ), 'r' ) as f_i:
        with open( path, 'r' ) as f_i:
            src_i = f"{f_i.read()}"
            res_i = grab_identified_sections_of_java_source( src_i, searchTerms, searchOver )
            for j, chunk_j in enumerate( res_i['chunks'] ):
                range_j = res_i['ranges'][j]
                rtnStr += f"/// Lines: {range_j} ///\n"
                for k, line_k in enumerate( chunk_j ):
                    found = False
                    kWord = ""
                    for term in searchTerms:
                        if term.lower() in f"{line_k}".lower():
                            found = True
                            kWord = term
                            break
                    rtnStr += f"/*{range_j[0]+k+1: 4}*/\t{line_k}{f' // << kw: {kWord} <<' if found else ''}\n"
                rtnStr += f"\n"
            if not len( res_i['chunks'] ):
                found = False
                kWord = ""
                for term in searchTerms:
                    if term.lower() in f"{path}".lower():
                        found = True
                        kWord = term
                        break
                if found:
                    lines, _ = split_lines_with_depth_change( src_i )
                    rtnStr += f' // vvvvv-- kw: {kWord} in "{str( path ).split("/")[-1]}"! --vvvvv\n'
                    for k in range( min( _SRCH_MARGN, len( lines ) ) ):
                        line_k = lines[k]
                        rtnStr += f"/*{k+1: 4}*/\t{line_k}\n"


        rtnStr += f"\n\n"
    return rtnStr


def count_block_lines( srcDir : str, searchOver : int = 3, fileExt : str = "java" ):
    """ Count the number of lines in each block """
    rtnLst  = deque()
    jvPaths = [path for path in get_all_file_paths( srcDir ) if f".{fileExt}".lower() in path.lower()]
    while not len( jvPaths ):
        srcDir  = os.path.dirname( srcDir )
        jvPaths = [path for path in get_all_file_paths( srcDir ) if f".{fileExt}".lower() in path.lower()]
    for path in jvPaths:
        # with open( os.path.join( srcDir, path ), 'r' ) as f_i:
        with open( path, 'r' ) as f_i:
            src_i = f"{f_i.read()}"
            lns_i, dpt_i = split_lines_with_depth_change( src_i )
            stk_i = deque()
            for j, lin_j in enumerate( lns_i ):
                dep_j = dpt_i[j]
                # Push an opened block onto the stack
                if dep_j > 0:
                    # bgn_i = j # max( j-searchOver, 0 )
                    stk_i.append({
                        'path'  : f"{path}".split('/')[-1],
                        'begin' : j+1,
                        # 'lines' : deque( lns_i[ bgn_i : j ] ),
                        'lines' : deque(),
                    })
                # All existing stack elems accrue the line
                for itm_k in stk_i:
                    itm_k['lines'].append( lin_j )
                # Pop a closed block from the stack
                if (dep_j < 0) and len( stk_i ):
                    rtnLst.append( stk_i.pop() )
    rtnLst = list( rtnLst )
    rtnLst.sort( key = lambda x: len( x['lines'] ), reverse = True )
    return rtnLst


def report_block_sizes( srcDir : str, searchOver : int = 3, fileExt : str = "java" ):
    """ Print a report of all code blocks """
    blocks  = count_block_lines( srcDir, searchOver, fileExt )
    wdtPath = max( [len(elem['path']) for elem in blocks] ) if len( blocks ) else 3
    wdtSize = len( f"{len(blocks[0]['lines'])}" ) if len( blocks ) else 3
    for block in blocks[:_N_BIG_BLK]:
        path = block['path']
        size = len( block['lines'] )
        print( f"{path: <{wdtPath}} : {size: >{wdtSize}} : On Line {block['begin']: >{wdtSize}}" )
        # for i in range( searchOver+1 ):
        #     print( f"\t{block['lines'][i]}" )



########## MAIN ####################################################################################


if __name__ == "__main__":

    print( f"Create output directory: \"{_REPORT_DIR}\"" )
    os.makedirs( _REPORT_DIR, exist_ok = True )
    sleep( 0.125 ) # Error about missing directory, Why would this take time?

    htPaths = [path for path in os.listdir() if ".html" in path]

    disp_text_header( f"Begin Evaluation of {_LIST_PATHS}", 15, preNL = 1, postNL = 2 )

    for _LIST_PATH in _LIST_PATHS:
        disp_text_header( f"About to process {_LIST_PATH}!!", 10, preNL = 1, postNL = 1 )
        students = get_ordered_students( _LIST_PATH )
        Nstdnt   = len( students )
        i        = 0
        reverse  = False

        # Allow search/cancel/quit at the start of each list, Prev/Redo are **disabled** here!
        stateChange = run_menu( students )
        loopAction  = stateChange['loop']
        if stateChange['index'] >= 0:
            i = stateChange['index']
        if loopAction == 'break':
            i = Nstdnt
            print( f">>> SKIPPED {_LIST_PATH} !! >>>" )
        
        # Begin normal list iteration
        while i < Nstdnt:
            print( f"... Iteration {i} ..." )
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
                if brName is not None:
                    print( f"About to fetch {brName} branch ..." )
                    checkout_branch( dirPrefix = stdDir, branchName = brName )

            ### Run Gradle Checks ###
            if _RUN_TESTS:
                print( f"About to run Gradle tests ..." )
                try:
                    for _ in range( _NUM_TESTS ):
                        res = gradle_test( dirPrefix = stdDir )
                    if len( res['err'] ):
                        with open( f"{_REPORT_DIR}/{stdStr}_BUILD-FAILED.txt", 'w' ) as f:
                            f.write( res['err'] )
                    if 'fail' in res:
                        with open( f"{_REPORT_DIR}/{stdStr}_Test-Results-FAILED.txt", 'w' ) as f:
                            f.write( res['fail'] )
                except KeyboardInterrupt:
                    print( "\nUser CANCELLED Gradle test!" )
                print()

            ### Gather Snippets ###
            print( f"About to fetch relevant code ..." )
            sdtSrc = grab_identified_source_chunks( os.path.join( stdDir, _SOURCE_DIR ), _TOPIC_SRCH, _SRCH_MARGN, "java" )
            stdSnp = f"{_REPORT_DIR}/{stdStr}_related_source.java"
            with open( stdSnp, 'w' ) as f:
                f.write( sdtSrc )
            if _OPEN_SNPPT:
                run_cmd( f"{_EDITOR_COMMAND} {stdSnp}", timeout_s = 3 )

            ### Static Analysis ###
            print( f"About to run code style checks ..." )
            disp_text_header( f"Static Analsys for {stdNam}", 3, preNL = 1, postNL = 1 )
            run_PMD_report( dirPrefix = stdDir, codeDir = _SOURCE_DIR, outDir = _REPORT_DIR, studentStr = stdStr )
            disp_text_header( f"{stdNam} Static Analsys COMPLETE", 3, preNL = 0, postNL = 1 )

            ### Search for Excessive Functions && Classes ###
            disp_text_header( f"Class && Function Lengths for {stdNam}", 3, preNL = 1, postNL = 0 )
            report_block_sizes( os.path.join( stdDir, _SOURCE_DIR ), searchOver = 2 )
            disp_text_header( f"{stdNam} Verbosity Check COMPLETE", 3, preNL = 0, postNL = 1 )

            ### IntelliJ View ###
            if _INSPECT_J:
                print( f"About to inspect Java project ..." )
                inspect_project( dirPrefix = stdDir )
                print()

            disp_text_header( f"{stdNam}, Eval completed!", 5, preNL = 1, postNL = 2 )

            stateChange = run_menu( students )
            reverse     = stateChange['reverse']
            loopAction  = stateChange['loop']
            if stateChange['index'] >= 0:
                i = stateChange['index']
            if loopAction == 'break':
                break
            elif loopAction == 'continue':
                continue
            
            i += stateChange['iDelta']

        disp_text_header( f"COMPLETED {_LIST_PATH}!!", 10, preNL = 1, postNL = 2 )
    disp_text_header( f"Student Evaluation of {_LIST_PATHS} COMPLETED!!", 15, preNL = 1, postNL = 2 )


########## SPARE PARTS #############################################################################

