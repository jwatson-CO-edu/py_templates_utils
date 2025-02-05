########## INIT ####################################################################################

##### Imports #####
### Standard ###
import subprocess, os, sys
from pprint import pprint

##### Constants #####
_INTELLIJ_PATH = "/opt/idea/bin/idea"

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


def disp_text_header( titleStr, emphasis, preNL = 0, postNL = 0 ):
    """ Make the headers that you like so much """
    emphStr = '#'*int(emphasis)
    newLine = '\n'
    print( f"{newLine*int(preNL) if preNL else ''}{emphStr} {titleStr} {emphStr}{newLine*int(postNL) if postNL else ''}" )



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
            print( f"ERROR:\n{err.decode()}" )
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
        # print( line )
        if "TestEventLogger" in line:
            print( line.split("[TestEventLogger]")[-1] )
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
                    return part_i.replace( "https://github.com/", "git@github.com:" ).replace( "/tree/main", "" )
    return None


def get_folder_from_github_addr( gitAddr ):
    """ What folder will git put the repo in? """
    parts = str( gitAddr ).split('/')
    return parts[-1].replace('.git','')



########## MAIN ####################################################################################


if __name__ == "__main__":

    _LIST_PATHS  = ["ugrads.txt", "grads.txt",]

    htPaths = [path for path in os.listdir() if ".html" in path]

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

            ### Run Gradle Checks ###
            print( f"About to run Gradle tests ..." )
            for _ in range(2):
                res = gradle_test( dirPrefix = stdDir )
            print()

            # print( f"About to build Gradle project ..." )
            # res = gradle_build_clean( dirPrefix = stdDir )
            # print()

            # print( f"About to run Gradle project ..." )
            # run_gradle_build( dirPrefix = stdDir, jarDir = "build/libs", runEXT = "JAR" )
            # print()

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

            print( f"About to inspect Java project ..." )
            inspect_project( dirPrefix = stdDir )
            print()

            disp_text_header( f"{stdNam}, Eval completed!", 5, preNL = 0, postNL = 1 )

            usrCmd = input( "Press [Enter] to evaluate the next student: " ).upper()
            print()

            # Handle user input
            if 'Q' in usrCmd:
                disp_text_header( f"END PROGRAM", 10, preNL = 2, postNL = 1 )
                sys.exit(0)
            elif 'P' in usrCmd:
                i -= 1
                print( "^^^ PREVIOUS STUDENT ^^^" )
                reverse = True
                continue
            elif 'E' in usrCmd:
                print( "!XXX! END LIST !XXX!" )
                break
            
            i += 1

        disp_text_header( f"COMPLETED {_LIST_PATH}!!", 10, preNL = 1, postNL = 2 )
    
