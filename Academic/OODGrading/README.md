# CU Boulder CSCI 4/5448 Grading Helper
This is to assist course staff in grading many student Java assignments in one session by automating the boring stuff.  
**VERY IMPORTANT**: *This software is for clerical/logistical support and is in no way intended as a substitute for reasonable and attentive evaluation of student work.* **There is no guarantee of correctness or functionality provided, USE AT YOUR OWN RISK.**

# Dependencies
* Tested under Ubuntu 22.04
* Python 3.9+, Only standard modules used

# Installation

## Linux

### PMD, Static Analysis
1. `cd /tmp/`
1. `wget https://github.com/pmd/pmd/releases/download/pmd_releases%2F7.10.0/pmd-dist-7.10.0-bin.zip`
1. `unzip pmd-dist-7.10.0-bin.zip`
1. `sudo mv pmd-bin-7.10.0 /opt/`
1. Add to "~/.bashrc": `alias pmd="/opt/pmd-bin-7.10.0/bin/pmd"`

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
**NOTE**: When the branch search does not return any hits, the most recently-created branch will be checked out automatically!
1. At the root folder (terminal): `python3.11 00_clone_test_build_all.py`

## Optional
* Change the following in [HW_Config.json](https://github.com/jwatson-CO-edu/py_templates_utils/blob/master/Academic/OODGrading/HW_Config.json) under the heading that matches your OS:
   - "_INTELLIJ_PATH" : If it differs for your machine.
   - "_PMD_PATH": If it differs for your machine.
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
    * Searches for HTML file from Canvas containing the GitHub repo link, Clones repo
    * Clones repo and checks out the most recent branch containing the search string you specified. (If no branches contain the search string, then the most recently-created branch will be checked out.)
    * Runs and prints Gradle test results. When one or more tests fail, test output is written to a file named after the student will appear in a new "output" subdirectory.
    (You may cancel the current test with [Ctrl]+[c] (`SIGTERM`))  
    (**WARNING**: Gradle sometimes fails to consistently print all results to `stdout`, which is where Python captures it. You may wish to rerun tests from inside IntelliJ. (See below.))
    * Searches for `main()`, **IGNORE!**
    * Runs code style checks via [PMD Static Analysis](https://pmd.github.io/pmd/index.html). A report named after the student will appear in a new "output" subdirectory.
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
* `[Y]` Add student search, 2025-02-21: Added, TESTED!
  - `[Y]` 2025-02-21, ISSUE: <Lastname, Firstname> search seems to FAIL, display full ranking for the list and DEBUG, 2025-02-21: Resolved, compared wrong names
* `[>]` Config JSON so that users do not need to modify code every assignment.
   - `{?}` IF someone generates a pull req. for Windows functionality, THEN add Windows fields to the JSON.
* `[Y]` Automatically export failing test results to a file, 2025-02-21: Added, TESTED!
* `{?}` Allow users to add/commit files to the repo? YAGNI?
   - `[ ]` Create "Eval" dir
   - `[ ]` Scrape for screenshots since beginning of per-student eval
   - `{?}` Automatically send style report here?
   - `{?}` Automatically send failed test report here?

# Change Log
* 2025-02-21: Fixed issue with multiple matching branches that causes the _earliest_ of matches to be checked out instead of the **latest**, Fixed problems with name search.

# Windows Contribution Guide
* [Spawning subprocesses from the shell will be different.](https://github.com/jwatson-CO-edu/py_templates_utils/blob/18278af12e72df5c156d58ed601f71e72a917459/Academic/OODGrading/00_clone_test_build_all.py#L80)
* [Changing terminal output color might be different? (Citation needed)](https://github.com/jwatson-CO-edu/py_templates_utils/blob/18278af12e72df5c156d58ed601f71e72a917459/Academic/OODGrading/00_clone_test_build_all.py#L17)
* [Install paths will be different.](https://github.com/jwatson-CO-edu/py_templates_utils/blob/18278af12e72df5c156d58ed601f71e72a917459/Academic/OODGrading/00_clone_test_build_all.py#L9)
* _I look forward to your pull requests!_
