# CU Boulder CSCI 4/5448 Grading Helper
This is to assist course staff in grading many student Java assignments in one session by automating the boring stuff.  
**VERY IMPORTANT**: *This software is for clerical/logistical support and is in no way intended as a substitute for reasonable and attentive evaluation of student work.* **There is no guarantee of correctness or functionality provided, USE AT YOUR OWN RISK.**

# Dependencies
* Tested under Ubuntu 22.04
* Python 3.9+, Only standard modules used

# Installation

## Linux

### Install JDK @ Ubuntu
1. [Download JDK DEB](https://www.oracle.com/java/technologies/downloads/)
2. `sudo apt install ./jdk-25_linux-x64_bin.deb`
2. `sudo apt install ./jdk-21_linux-x64_bin.deb`

### PMD, Static Analysis
1. `cd /tmp/`
1. `wget https://github.com/pmd/pmd/releases/download/pmd_releases%2F7.21.0/pmd-dist-7.21.0-bin.zip`
1. `unzip pmd-dist-7.21.0-bin.zip`
1. `sudo mv pmd-bin-7.21.0 /opt/`
1. Add to "~/.bashrc": `alias pmd="/opt/pmd-bin-7.21.0/bin/pmd"`

### IntelliJ IDEA, Editor
1. Download the TAR
1. Expand and rename directory to "idea"
1. `sudo mv idea /opt/`
1. Add to "~/.bashrc": `alias idea="/opt/idea/bin/idea"`

### Gradle, Build System
1. Make sure that some version of Oracle Java is installed, as above!
1. `cd /tmp/`
1. `curl -s "https://get.sdkman.io" | bash`
1. `source "$HOME/.sdkman/bin/sdkman-init.sh"`
1. `sdk list gradle`, Review latest available version 
1. `sdk install gradle 9.2.1`, Or most recent

# Grading Script Usage Instructions (per Assignment)
1. Copy "[00_clone_test_build_all.py](https://github.com/jwatson-CO-edu/py_templates_utils/blob/master/Academic/OODGrading/00_clone_test_build_all.py)", "[OOD_Java-Rules.xml](https://github.com/jwatson-CO-edu/py_templates_utils/blob/master/Academic/OODGrading/OOD_Java-Rules.xml)", and "[HW_Config.json](https://github.com/jwatson-CO-edu/py_templates_utils/blob/master/Academic/OODGrading/HW_Config.json)" to the root directory for this assignment.
1. At the assignment page, click "**Download Submissions**".
1. Unzip the submissions at the root folder.
1. Create a text file that consists of all the students you are responsible for with  
**LASTNAME, FIRSTNAME**  
on each line.
1. Change the following in [HW_Config.json](https://github.com/jwatson-CO-edu/py_templates_utils/blob/master/Academic/OODGrading/HW_Config.json) under the heading "HWX":
   - "_LIST_PATHS": A list of string filenames created in the previous step. This must be a list, even if it only one file name.
   - "_SOURCE_DIR": Root directory of source files used by the Gradle project.
   - "_BRANCH_STR": A search string that will retrieve the appropriate branch. *Please make sure it is broad enough to capture every possible branch name, since there are no naming requirements for branches.*  
   **NOTE**: When the branch search does not return any hits, the branch with the most recent commit will be checked out automatically!
   - "_TOPIC_SRCH": List of search strings relevant to this assignment, such as pattern names. **Not** case sensitive. (See below.)
1. At the root folder (terminal): `python3.11 00_clone_test_build_all.py`

## Optional
* You can change the following in [HW_Config.json](https://github.com/jwatson-CO-edu/py_templates_utils/blob/master/Academic/OODGrading/HW_Config.json), as needed:
   - "_SRCH_MARGN": Search breadth in lines, defines how much code is retrieved for each keyword hit
   - "_OPEN_SNPPT": Flag for whether you want code search hits to be displayed automatically in your editor of choice
   - "_RUN_TESTS": Flag for whether you want to generate reports for Gradle tests to run outside of IntelliJ, 2025-03-07: CLI Gradle tests have recently **stopped working**, and **I don't know why**!  Please **make a pull request** if you solve this issue!
   - There are several OS-specific fields. I **assumed** that these will be the same for every Linux user, but they may not be. If your OS is not represented, you will need to create a new category entry for your OS, and associated sub-fields. sub-fields include:
      * "_INTELLIJ_PATH" : If it differs for your machine.
      * "_PMD_PATH": If it differs for your machine.
      * "_EDITOR_COMMAND": The editor that will display the summarized code snippets. It is recommended that this be a minimal editor with basic highlighting, as the snippets file will not be syntactically correct. 
* You can change "[OOD_Java-Rules.xml](https://github.com/jwatson-CO-edu/py_templates_utils/blob/master/Academic/OODGrading/OOD_Java-Rules.xml)" to [silence nuisance alerts](https://pmd.github.io/pmd/pmd_userdocs_making_rulesets.html#bulk-adding-rules). This [reference](https://pmd.github.io/pmd/pmd_rules_java.html) contains a description of all the Java rules that are part of PMD.
   
# Program Flow
- The script iterates over the text files in the specified order, Each list begins with a prompt:
   * Simply press [Enter] to evaluate students in this file.
   * Type [e] then [Enter] to proceed directly to the next text file, if it exists.
   * Type "s:" followed by a student name, then [Enter] to search for a student and jump to their repo. The following patterns are accepted:
      - LASTNAME, FIRSTNAME
      - FIRSTNAME LASTNAME
      - EITHERNAME
   * Type [q] then [Enter] to quit the program immediately. 
- The script iterates over the students within each file in alphabetic order by last name, Per student:
    * Searches for HTML file from Canvas containing the GitHub repo link
    * Clones repo and checks out the most recent branch containing the search string you specified. (If no branches contain the search string, then the branch with the most recent commit will be checked out.)
    * **Optional**: Runs and prints Gradle test results. When one or more tests fail, test output is written to a file named after the student will appear in a new "output" subdirectory. (Disabled by default, see above.)
    (You may cancel the current test with [Ctrl]+[c] (`SIGTERM`))  
    (**WARNING**: Gradle sometimes fails to consistently print all results to `stdout`, which is where Python captures it. You may wish to rerun tests from inside IntelliJ. (See below.))
    * Gathers snippets of Java code into an annotated JAVA file that is named after the student. This will appear in the "output" subdirectory. (See above.)
    * Runs code style checks via [PMD Static Analysis](https://pmd.github.io/pmd/index.html). A report named after the student will appear in a new "output" subdirectory.
    * Determines the size of all code blocks within JAVA files, and prints the size of the `_N_BIG_BLK` largest blocks, with filename and line number.
    * Displays relative per-user contributions to the repo in Lines of Code (LOC) are displayed as a fraction of all lines committed. (Use your judgement when you see a relative contribution of 1:0.)
    * Opens IntelliJ IDEA with a view on the student project. You can re-run tests, inspect code, and generate class diagrams from here.
    * **You must close the IntelliJ window to finish the student evaluation!**
    * At the end of each student evaluation, you are given a prompt:
        - Simply press [Enter] to continue to next student.
        - Type [p] then [Enter] to review the previous student.
        - Type [r] then [Enter] to review the current student again.
        - Type [e] then [Enter] to proceed directly to the next text file, if it exists.
        - Type "s:" followed by a student name, then [Enter] to search for a student and jump to their repo. The following patterns are accepted:
            * LASTNAME, FIRSTNAME
            * FIRSTNAME LASTNAME
            * EITHERNAME
        - Type [q] then [Enter] to quit the program immediately. (*NOTE*: Next run, execution will start from the beginning of the alphabet. There is no saved state.)

# `DEV_PLAN`
No pull requests are considered after 2025-05-10!

# Change Log
* 2025-04-24: Display relative student contributions (by GitHub login), Fixed bug where including a URL argument in scraped address causes an infinite loop, QoL improvements, Editorial Changes
* 2025-03-21: Added MacOS (Darwin) config data, IntelliJ path is now set as the first valid of a list of given options, Gradle tests work on some machines and not others! - Reason unknown!, Source files with a search term in their title will have the first `_SRCH_MARGN` lines of the file added to the summary, Corrected zero-based line numbers in summary, Timeout on summary generation
* 2025-03-07: Order branches by most recent commit date rather than creation date, Report code block sizes, Functions are more tolerant to project structures that are both deeply nested **and** with directory names that are other than what was given by proctors
* 2025-02-27: A summarized JAVA file is created for each student based on the specified search terms. Config JSON has been split into categories, including OS-specific fields. Small editorial and QOL adjustments. 
* 2025-02-25: Config JSON so that users do not need to modify code every assignment.
* 2025-02-21: Fixed issue with multiple matching branches that causes the _earliest_ of matches to be checked out instead of the **latest**, Fixed problems with name search.

# Windows Adaptation Guide
**WARNING**: Links lead to a previous commit!
* [Spawning subprocesses from the shell will be different.](https://github.com/jwatson-CO-edu/py_templates_utils/blob/18278af12e72df5c156d58ed601f71e72a917459/Academic/OODGrading/00_clone_test_build_all.py#L80)
* [Changing terminal output color might be different? (Citation needed)](https://github.com/jwatson-CO-edu/py_templates_utils/blob/18278af12e72df5c156d58ed601f71e72a917459/Academic/OODGrading/00_clone_test_build_all.py#L17)
* [Install paths will be different.](https://github.com/jwatson-CO-edu/py_templates_utils/blob/18278af12e72df5c156d58ed601f71e72a917459/Academic/OODGrading/00_clone_test_build_all.py#L9)
