########## INIT ####################################################################################

##### Imports #####
### Standard ###
import subprocess, os, sys, platform, json, traceback, re
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
print()
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
    _LIST_PATHS     = config["Settings"]["_LIST_PATHS"]
    _PMD_JAVA_RULES = config["Settings"]["_PMD_JAVA_RULES"]
    _RUN_PMD_CHECKS = config["Settings"]["_RUN_PMD_CHECKS"]
    _PMD_JAVA_VER   = config["Settings"]["_PMD_JAVA_VER"]
    _PMD_HIDE_ERROR = config["Settings"]["_PMD_HIDE_ERROR"]
    _GET_RECENT     = config["Settings"]["_GET_RECENT"]
    _REPORT_DIR     = config["Settings"]["_REPORT_DIR"]
    _N_SEARCH_R     = config["Settings"]["_N_SEARCH_R"]
    _RUN_TESTS      = config["Settings"]["_RUN_TESTS"]
    _NUM_TESTS      = config["Settings"]["_NUM_TESTS"]
    _N_BIG_BLK      = config["Settings"]["_N_BIG_BLK"]
    _INSPECT_J      = (config["Settings"]["_INSPECT_J"] and (_INTELLIJ_PATH is not None))
    _SRCH_MARGN     = config["Settings"]["_SRCH_MARGN"]
    _OPEN_SNPPT     = config["Settings"]["_OPEN_SNPPT"]
    _EN_ALL_TST     = config["Settings"]["_EN_ALL_TST"]
    _SHO_CONTRB     = config["Settings"]["_SHO_CONTRB"]
    _BLD_PLUGINS    = config["Settings"]["_BLD_PLUGINS"]
    _SCAN_MAGIC     = config["Settings"]["_SCAN_MAGIC"]
    _NAMES_REPORT   = config["Settings"]["_NAMES_REPORT"]
    ### Assignment ###
    _HW_TAG     = config["Settings"]["_HW_TAG"]
    _SOURCE_DIR = config[_HW_TAG]["_SOURCE_DIR"]
    _TEST_DIR   = config[_HW_TAG]["_TEST_DIR"] 
    _BRANCH_STR = config[_HW_TAG]["_BRANCH_STR"]
    _TOPIC_SRCH = config[_HW_TAG]["_TOPIC_SRCH"]
    _TOPIC_XCLD = config[_HW_TAG]["_TOPIC_XCLD"]
    ### Report ###
    print()
    print( f"Default Gradle Path:  {_GRADLE_PATH}" )
    print( f"Req'd Gradle Plugins: {[item['plugin'] for item in _BLD_PLUGINS if ('plugin' in item)]}" )
    print()
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


class Tee:
    """ Captures `stdout` to a file while still displaying it """
    # WARNING, CLAUDE SLOP: https://claude.ai/share/bf70a9b8-2f1e-4b02-b449-ffb541df59a9

    def set_alt_file( self, altPath = None ):
        """ Set the alternate file where text is redirected """
        self.files = self.files[:1]
        if altPath is not None:
            try:
                f = open( altPath, 'w' )
            except Exception:
                f = None
            if f is not None:
                self.files.append(f)

    def attach( self ):
        """ Cache original `stdout` file and replace with self """
        self.origF = sys.stdout
        sys.stdout = self


    def detach( self ): 
        """ Restore the original `stdout` file """
        if self.origF is not None:
            sys.stdout = self.origF


    def __init__( self, altPath = None ):
        """ Open file and attach """
        self.files = [sys.stdout,]
        self.origF = None
        self.set_alt_file( altPath )
        self.attach()
        self.ansi_escape = re.compile(r'\x1b\[[0-9;]*m')


    def __del__( self ):
        """ Detach when erased """
        self.detach()

    
    def write( self, data ):
        """ Tee data to all files """
        plainData = self.ansi_escape.sub( '', data )
        for i, f in enumerate( self.files ):
            if i == 0:
                f.write( data )
            else:
                f.write( plainData )
            f.flush()
    

    def flush( self ):
        """ Flush all write buffers """
        for f in self.files:
            f.flush()



########## HELPER FUNCTIONS ########################################################################

def get_ordered_students( listPath ):
    """ Prep student list for searching """
    students = list()
    with open( listPath, 'r' ) as f:
        lines = f.readlines()
        for line in lines:
            if len( line ) > 2:
                students.append( line.replace('-','').replace("'",'').replace(",",'').strip().lower().split() )
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
                                           stderr  = subprocess.STDOUT,
                                           shell   = True,
                                           timeout = int( timeout_s ) )
        except subprocess.TimeoutExpired as e:
            out = ""
            print( f"Time limit of {int( timeout_s )} seconds EXPIRED for process\n{ruleStr}\n{e}\n" )
        return { 
            'cmd': ruleStr,
            'err': traceback.format_exc(),
            'out': out.decode() if len( out ) else "",
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

def inject_id_entry_after_hit( buildGradlePath : str, searchLst : list[str], injectName : str ):
    """ Add a name to the plugin table in "build.gradle" """
    lines = deque()
    wrLin = deque()

    def p_line_match( lineStr : str ):
        """ Do all the terms match? """
        nonlocal searchLst
        for term in searchLst:
            if term not in lineStr:
                return False
        return True

    with open( buildGradlePath, 'r' ) as f:
        lines.extend( f.readlines() )
    for line in lines:
        wrLin.append( line )
        if p_line_match( line ):
            wrLin.append( f"    id '{injectName}'\n" )
    with open( buildGradlePath, 'w' ) as f:
        for line in wrLin:
            f.write( line )
    print( f"Injected the {injectName} 'id' to {buildGradlePath}!" )
        

def gradle_test( dirPrefix : str = "" ):
    """ Run all Gradle tests """
    res = run_cmd( f"{_GRADLE_PATH} clean -p {dirPrefix}", suppressErr = True )
    res = run_cmd( f"{_GRADLE_PATH} build -p {dirPrefix} -cp src", suppressErr = True )
    cmd = f"{_GRADLE_PATH} cleanTest test --no-build-cache -d -p {dirPrefix}"
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
                    rtnStr  = part_i.replace( "https://github.com/", "git@github.com:" ).split( "/tree" )[0].split( "/pull" )[0].split( "#" )[0].split( "/blob" )[0]
                    print( f"Found URL: {rtnStr}" )
                    return rtnStr
    return None


def get_folder_from_github_addr( gitAddr ):
    """ What folder will git put the repo in? """
    parts = str( gitAddr ).split('/')
    return parts[-1].replace('.git','')


def get_most_recent_branch( dirPrefix : str = "", reqStr = None ):
    """ Extract the branch that was most recently created """
    cmd = f"git --git-dir=./{dirPrefix}/.git --work-tree=./{dirPrefix}/ ls-remote --heads --sort=-committerdate origin"
    out = run_cmd( cmd )['out']
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
    cmd = f"git --git-dir=./{dirPrefix}/.git --work-tree=./{dirPrefix}/ checkout origin/{branchName}" 
    out = run_cmd( cmd )['out']
    cmd = f"git --git-dir=./{dirPrefix}/.git --work-tree=./{dirPrefix}/ pull origin {branchName}" 
    out += run_cmd( cmd )['out']
    cmd = f"git --git-dir=./{dirPrefix}/.git --work-tree=./{dirPrefix}/ status" # "-f": Force
    out += run_cmd( cmd )['out']
    print( f"{out}" )


def count_LOC_contributions( dirPrefix : str = "", deleteFactor = 0.125 ):
    """ Get usernames and sum all LOC contributed by each user, Return as a dictionary """
    cmd = f"git --git-dir=./{dirPrefix}/.git --work-tree=./{dirPrefix}/ shortlog -sn --all" 
    out = run_cmd( cmd )['out']
    lns = f"{out}".split('\n')
    nms = list()
    for line in lns:
        if len( line ) > 4:
            nms.append( line.split()[-1] )
    tot = 0.0
    rtn = dict()
    for gitName in nms:
        rtn[ gitName ] = 0.0
        cmd = f'git --no-pager --git-dir=./{dirPrefix}/.git --work-tree=./{dirPrefix}/ log --author="{gitName}" --format=tformat: --numstat'
        out = run_cmd( cmd )['out']
        lns = f"{out}".split('\n')
        for line in lns:
            parts   = line.split()
            if len( parts ) < 2:
                continue
            try:
                contrib = int(parts[0])*1.0 + int(parts[1])*deleteFactor
                tot    += contrib
                rtn[ gitName ] += contrib
            except ValueError:
                continue
            
    for k in rtn.keys():
        rtn[k] /= tot
    return rtn



########## STATIC ANALYSIS #########################################################################

def run_PMD_report( dirPrefix : str = "", codeDir : str = "", outDir : str = "", studentStr : str = "" ):
    """ Run a PMD report for Java """

    ## Set Environment Vars ## https://pmd.github.io/pmd/pmd_languages_configuration.html#java-language-properties
    os.environ["PMD_JAVA_X_TYPE_INFERENCE_LOGGING"] = "DISABLED"
    os.environ["PMD_JAVA_X_STRICT_TYPE_RES"]        = "false"
    # os.environ["PMD_JAVA_LOMBOK"]                   = "false"

    ## Run Analysis ##
    path  = os.path.join( dirPrefix, codeDir )
    # cmd   = f"{_PMD_PATH} check -d ./{path} -R ./{_PMD_JAVA_RULES} -f text"
    cmd   = f"{_PMD_PATH} check --use-version=java-{_PMD_JAVA_VER} -d ./{path} -R ./{_PMD_JAVA_RULES} -f text"
    res   = run_cmd( cmd, suppressErr = _PMD_HIDE_ERROR )
    while ("No such file" in res['err']):
        path = os.path.dirname( path )
        # cmd  = f"{_PMD_PATH} check -d ./{path} -R ./{_PMD_JAVA_RULES} -f text"
        cmd  = f"{_PMD_PATH} check --use-version=java-{_PMD_JAVA_VER} -d ./{path} -R ./{_PMD_JAVA_RULES} -f text"
        res  = run_cmd( cmd, suppressErr = _PMD_HIDE_ERROR )
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


def grab_identified_sections_of_java_source( javaSourceStr : str, searchTerms : list[str], searchOver : int = 40,
                                             excludeTerms : list[str] = None ):
    """ Attempt to grab relevant portion of code """
    lines, lnDeltaDepth = split_lines_with_depth_change( javaSourceStr )
    N = len( lines )
    depth    = 0
    covered  = set([])
    exclude  = excludeTerms if (excludeTerms is not None) else list()
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
            for xTerm in exclude:
                if xTerm in line_i:
                    hit = False
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
    

_RESERVED_CHARS   = ['(', ')', ';', '{', '}', ',',]
_RESERVED_SYMBOLS = ['//',]


def tokenize( expr : str ):
    """ Return a list of tokens found in the expr """
    expr  += ' ' # Terminator Hack 
    tknDqu = deque()
    token  = ""

    def p_res_char( char : str ):
        """ Return True if the token is reserved """
        if char in _RESERVED_CHARS:
            return True
        return False

    def store_token():
        """ Add a token to the collection """
        nonlocal tknDqu, token
        if len( token ):
            tknDqu.append( token )
        token = ""

    for c in expr:
        if p_res_char( c ):
            store_token()
            tknDqu.append( c )
        elif c.isspace():
            store_token()
        else:
            token += c
            if token in _RESERVED_SYMBOLS:
                store_token() # This obviates the second sweep in CPluscal!

    return list( tknDqu )


def p_has_parens( tknLst : list[str] | str ):
    """ Is there at least one paren token? """
    if isinstance( tknLst, str ):
        tknLst = tokenize( tknLst )
    if ('(' in tknLst) or (')' in tknLst):
        return True
    return False


def trim_comment_from_tokens( tknLst : list[str] ):
    """ Take remove end of line comment that was tokenized """
    if '//' in tknLst:
        return tknLst[ :tknLst.index('//') ]
    return tknLst


def get_paren_contents( tknLst : list[str] | str ):
    """ Get the contents of the outermost parens as a list of tokens """
    if isinstance( tknLst, str ):
        tknLst = trim_comment_from_tokens( tokenize( tknLst ) )
    depth  = 0
    rtnLst = deque()
    start  = False
    for token in tknLst:
        if token == ')':
            depth -= 1
        if depth > 0:
            rtnLst.append( token )
            start = True
        elif (depth < 0):
            print( f"\n'get_paren_contents': UNBALANCED PARENS!, {tknLst}\n" )
            return None
        elif (depth == 0) and start:
            break
        if token == '(':
            depth += 1
    return list( rtnLst )


def p_has_java_access_modifier( line : str ):
    """ Does this line specify class access? """
    for modifier in ['public','private','protected','static','final',]:
        if modifier in line:
            return True
    return False


def p_class_interface_def_begin( line : str ):
    """ Is this the beginning of a class def? """
    return (p_has_java_access_modifier( line ) and (('class' in line) or ('interface' in line)))


def get_class_interface_name( line : str ):
    """ Get the class name from the line """
    if ('class' in line):
        tokens = tokenize( line )
        for i, token in enumerate( tokens ):
            if (token == 'class') or (token == 'interface'):
                return tokens[i+1]
        return None
    else:
        return None
    

def p_primitive_def( line : str ):
    """ Does this line have a primitive type name? """
    for primName in ['byte','short','int','long','float','double','char','String','boolean',
                     'Integer','Boolean','Float','Double',]: 
        if primName in line:
            return True
    return False
    

def p_number_str( num : str ) -> bool:
    """ Does the string represent a number? """
    try:
        int( num )
        return True
    except ValueError:
        try:
            float( num )
            return True
        except ValueError:
            return False



########## PROJECT / FILE STRUCTURE ################################################################

def get_all_file_paths( directory ) -> list[str]:
    """ Return a list of full leaf paths under directory, Recursive """
    # Source: https://www.google.com/search?client=firefox-b-1-lm&channel=entpr&q=python+list+of+paths+from+recursive+walk
    file_paths = []
    for dirpath, _, filenames in os.walk( directory ):
        for filename in filenames:
            file_path = os.path.join( dirpath, filename )
            file_paths.append( file_path )
    return sorted( file_paths ) # Dir walking is NOT deterministic!


def get_all_EXT_paths( directory, fileExt : str = "java" ) -> list[str]:
    jvPaths  = [path for path in get_all_file_paths( directory ) if f".{fileExt}".lower() in path.lower()]
    while not len( jvPaths ):
        directory  = os.path.dirname( directory )
        jvPaths = [path for path in get_all_file_paths( directory ) if f".{fileExt}".lower() in path.lower()]
    return jvPaths



########## CODE STRUCTURE ANALYSIS #################################################################

def grab_identified_source_chunks( srcDir : str, searchTerms : list[str], searchOver : int = 40, fileExt : str = "java",
                                   excludeTerms : list[str] = None ):
    """ Get identified chunks in the code """
    rtnStr  = ""
    jvPaths = get_all_EXT_paths( srcDir, fileExt )
    exclude = excludeTerms if (excludeTerms is not None) else list()
    for path in jvPaths:
        rtnStr += f"///// {path} /////\n"
        with open( path, 'r' ) as f_i:
            src_i = f"{f_i.read()}"
            res_i = grab_identified_sections_of_java_source( src_i, searchTerms, searchOver, excludeTerms )
            for j, chunk_j in enumerate( res_i['chunks'] ):
                range_j = res_i['ranges'][j]
                rtnStr += f"/// Lines: [{range_j[0]+1}, {range_j[1]}] ///\n"
                for k, line_k in enumerate( chunk_j ):
                    found = False
                    kWord = ""
                    for term in searchTerms:
                        if term.lower() in f"{line_k}".lower():
                            found = True
                            kWord = term
                            break
                    if found:
                        for term in exclude:
                            if term.lower() in f"{line_k}".lower():
                                found = False
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


def scan_source_for_magic_args( srcDir : str, fileExt : str = "java" ) -> str:
    """ Get identified chunks in the code """
    rtnStr  = ""
    jvPaths = get_all_EXT_paths( srcDir, fileExt )

    def p_skip( line : str ):
        if ('assert' in line) or ('for' in line):
            return True
        return False

    for path in jvPaths:
        start = False
        if '/test/' in path:
            continue
        with open( path, 'r' ) as f_i:
            for i, line in enumerate( f_i.readlines() ):
                contents = get_paren_contents( line )
                if contents is None:
                    continue
                for token in contents:
                    if p_number_str( token ) and (not p_skip( line )):
                        if not start:
                            rtnStr += f"///// {path} /////\n\n"
                            start = True
                        rtnStr += f"Magic Number? (@ Line {i+1}): {line}\n"
                        break
            if start:
                rtnStr += '\n'
    return rtnStr


def count_block_lines( srcDir : str, fileExt : str = "java" ):
    """ Count the number of lines in each block """
    rtnLst  = deque()
    jvPaths = get_all_EXT_paths( srcDir, fileExt )
    for path in jvPaths:
        with open( path, 'r' ) as f_i:
            src_i = f"{f_i.read()}"
            lns_i, dpt_i = split_lines_with_depth_change( src_i )
            stk_i = deque()
            for j, lin_j in enumerate( lns_i ):
                dep_j = dpt_i[j]
                # Push an opened block onto the stack
                if dep_j > 0:
                    stk_i.append({
                        'path'  : f"{path}".split('/')[-1],
                        'begin' : j+1,
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


def report_block_sizes( srcDir : str, fileExt : str = "java" ):
    """ Print a report of all code blocks """
    blocks  = count_block_lines( srcDir, fileExt )
    wdtPath = max( [len(elem['path']) for elem in blocks] ) if len( blocks ) else 3
    wdtSize = len( f"{len(blocks[0]['lines'])}" ) if len( blocks ) else 3
    for block in blocks[:_N_BIG_BLK]:
        path = block['path']
        size = len( block['lines'] )
        print( f"{path: <{wdtPath}} : {size: >{wdtSize}} : On Line {block['begin']: >{wdtSize}}" )


def get_all_EXT_lines( srcDir : str, fileExt : str = "java", strip : bool = False ) -> dict[str,list[str]]:
    """ Return a dict of all lines of each file in `srcDir` matching `fileExt` """
    lineDict = dict()
    jvPaths = get_all_EXT_paths( srcDir, fileExt )
    for path in jvPaths:
        lines = list()
        with open( path, 'r' ) as f_i:
            if strip:
                lines = [line.strip() for line in f_i.readlines()]
            else:
                lines = f_i.readlines()
        lineDict[ os.path.join( srcDir, path ) ] = lines
    return lineDict


def get_user_defined_types( srcDir : str, fileExt : str = "java" ):
    """ Return a list of User Defined Types """
    rtnLst   = deque()
    lineDict = get_all_EXT_lines( srcDir, fileExt, strip = True )
    for lines in lineDict.values():
        for line in lines:
            if p_class_interface_def_begin( line ):
                clsNam = get_class_interface_name( line )
                if clsNam is not None:
                    rtnLst.append( clsNam )
    return list( rtnLst )          


def report_identifiers_and_signatures( srcDir : str, fileExt : str = "java" ):
    """ Get a string representing the hierarchy of identifiers """
    lineDict = get_all_EXT_lines( srcDir, fileExt, strip = True )
    usrTypes = get_user_defined_types( srcDir, fileExt )
    rtnStr   = ""
    depth    = 0

    def p_user_def( line : str ):
        """ Is a variable of a user type being declared? """
        if (not p_class_interface_def_begin( line )) and p_has_java_access_modifier( line ):
            tokens = tokenize( line )
            for token in tokens:
                if token in usrTypes:
                    return True
            return False
        else:
            return False

    def report_line( line : str, linNum : int = None ):
        """ Append the line to output """
        nonlocal depth, rtnStr
        if linNum is None:
            rtnStr += '\t'*depth + line.strip() + '\n'
        else:
            rtnStr += '\t'*depth + line.strip() + f"    // Line {linNum}" + '\n'


    def p_skip( line : str ):
        """ We don't want to read these """
        if ('.' in line) or ('//' in line) or ('assert' in line) or ('for' in line) or ('return' in line):
            return True
        return False

    for path, lines in lineDict.items():
        depth = 0
        rtnStr +=  f"\n### {path} ###\n"
        for lNum, line in enumerate( lines ):
            
            if (p_class_interface_def_begin( line ) or p_user_def( line ) or p_primitive_def( line )) and (not p_skip( line )):
                report_line( line, lNum+1 )

            tokens = tokenize( line )
            delDep = tokens.count('{') - tokens.count('}')
            depth += delDep
            depth = max( depth, 0 )

    return rtnStr

    

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


def enable_all_tests( tstDir : str, fileExt : str = "java" ):
    """ Find all `@Disable`d tests and comment out the decorator """
    jvPaths = [path for path in get_all_file_paths( tstDir ) if f".{fileExt}".lower() in str(path).lower()]
    print( f"\nFound {len(jvPaths)} files in {tstDir}!" )
    enTests = 0
    for jPath in jvPaths:
        wLines_i = deque()
        rewrit_i = False
        with open( jPath, 'r' ) as f_i:
            lines_i = f_i.readlines()
            for line_j in lines_i:
                if "@Disabled" in line_j:
                    wLines_i.append( f"//{line_j}" )
                    rewrit_i = True
                    enTests += 1
                else:
                    wLines_i.append( f"{line_j}" )
        if rewrit_i:
            with open( jPath, 'w' ) as f_i:
                for line_j in wLines_i:
                    f_i.write( f"{line_j}" )
    if enTests:
        print( f"\nEnabled {enTests} tests!\n" )



########## MAIN ####################################################################################


if __name__ == "__main__":

    print( f"Create output directory: \"{_REPORT_DIR}\"" )
    os.makedirs( _REPORT_DIR, exist_ok = True )
    sleep( 0.125 ) # Error about missing directory, Why would this take time?

    htPaths = [path for path in os.listdir() if ".html" in path]
    grPaths = [path for path in htPaths if "assignmentgroup" in path]

    disp_text_header( f"Begin Evaluation of {_LIST_PATHS}", 15, preNL = 1, postNL = 2 )


    for _LIST_PATH in _LIST_PATHS:
        disp_text_header( f"About to process {_LIST_PATH}!!", 10, preNL = 1, postNL = 1 )
        students = get_ordered_students( _LIST_PATH )
        Nstdnt   = len( students )
        Ngroup   = len( grPaths  )
        i        = 0
        j        = 0
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
        while (i < Nstdnt) or (j < Ngroup):
            print( f"... Iteration {i+j} ..." )

            if (i < Nstdnt):

                student = students[i]

                ### Fetch Submission ###
                stdStr = get_student_str( student )
                stdNam = get_student_name( student )
                stPath = None
                captur = Tee( f"{_REPORT_DIR}/{stdStr}_full_report.txt" )

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
                
            elif (j < Ngroup):

                ### Fetch Submission ###
                stdStr = grPaths[j].split('/')[-1]
                stdNam = stdStr
                stPath = grPaths[j]
                captur = Tee( f"{_REPORT_DIR}/{stdStr}_full_report.txt" )

                if not reverse:
                    j += 1
                else:
                    j -= 1


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
            print( f"Include: {_TOPIC_SRCH}" )
            print( f"Exclude: {_TOPIC_XCLD}" )
            sdtSrc = grab_identified_source_chunks( os.path.join( stdDir, _SOURCE_DIR ), _TOPIC_SRCH, _SRCH_MARGN, "java", 
                                                    _TOPIC_XCLD )
            stdSnp = f"{_REPORT_DIR}/{stdStr}_related_source.java"
            with open( stdSnp, 'w' ) as f:
                f.write( sdtSrc )
            if _OPEN_SNPPT:
                run_cmd( f"{_EDITOR_COMMAND} {stdSnp}", timeout_s = 3 )

            ### Scan for Magic Numbers ###
            if _SCAN_MAGIC:
                mgcSrc = scan_source_for_magic_args( stdDir )
                if len( mgcSrc ):
                    disp_text_header( f"Magic Number Scan for {stdNam}", 3, preNL = 1, postNL = 1 )
                    print( mgcSrc )
                    disp_text_header( f"{stdNam} Magic Number Scan COMPLETE", 3, preNL = 0, postNL = 1 )

            ### Report Identifiers ###
            if _NAMES_REPORT:
                namRep = report_identifiers_and_signatures( stdDir, "java" )
                if len( namRep ):
                    disp_text_header( f"Identifier Report for {stdNam}", 3, preNL = 1, postNL = 1 )
                    print( namRep )
                    disp_text_header( f"{stdNam} Identifier Report COMPLETE", 3, preNL = 0, postNL = 1 )

            ### Static Analysis ###
            if _RUN_PMD_CHECKS:
                print( f"About to run code style checks ..." )
                disp_text_header( f"Static Analsys for {stdNam}", 3, preNL = 1, postNL = 1 )
                run_PMD_report( dirPrefix = stdDir, codeDir = _SOURCE_DIR, outDir = _REPORT_DIR, studentStr = stdStr )
                disp_text_header( f"{stdNam} Static Analsys COMPLETE", 3, preNL = 0, postNL = 1 )

            ### Search for Excessive Functions && Classes ###
            disp_text_header( f"Class && Function Lengths for {stdNam}", 3, preNL = 1, postNL = 0 )
            report_block_sizes( os.path.join( stdDir, _SOURCE_DIR ) )
            disp_text_header( f"{stdNam} Verbosity Check COMPLETE", 3, preNL = 0, postNL = 1 )

            ### Show LOC Contributions by Student ###
            if _SHO_CONTRB:
                disp_text_header( f"Per-user contributions for repo from {stdNam}", 3, preNL = 1, postNL = 0 )
                contrib = count_LOC_contributions( dirPrefix = stdDir, deleteFactor = 0.125 )
                names   = list( contrib.keys() )
                names.sort()
                nmMax = max( [len(name) for name in names] )
                lnMax = max( [len(f"{loc:0.3f}") for loc in list(contrib.values())] )
                for name in names:
                    print( f"{name: <{nmMax}} : {round(contrib[name],3): >{lnMax}}" )
                disp_text_header( f"{stdNam} Contributions COMPLETE", 3, preNL = 0, postNL = 1 )

            ### IntelliJ View ###
            if _INSPECT_J:
                ## Enable Tests for Coverage ##
                if _EN_ALL_TST:
                    enable_all_tests( os.path.join( stdDir, _TEST_DIR), fileExt = "java" )

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

            captur = None

        disp_text_header( f"COMPLETED {_LIST_PATH}!!", 10, preNL = 1, postNL = 2 )
    disp_text_header( f"Student Evaluation of {_LIST_PATHS} COMPLETED!!", 15, preNL = 1, postNL = 2 )


########## SPARE PARTS #############################################################################

