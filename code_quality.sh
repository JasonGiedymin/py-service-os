#!/usr/bin/env bash
#
# Requires that `radon` and `xenon` be installed.
#

CODE_PATH=$PWD/v2/

function local_run() {
    local local_path=$1

    echo
    echo "Code which has a Cyclomatic Complexity of B or worse:"
    echo

    radon cc -a -nb $local_path

    echo
    echo "Maintainability of code (though these should not be forced)."
    echo "Anything above 20 is good, however aim for at least 50."
    echo

    radon mi -s $local_path
}

function ci_run() {
    local local_path=$1

    echo
    echo "Check if code quality adheres to grade 'A' rating for average, module, and absolute thresholds:"
    echo

    `xenon -b A -m A -a A $local_path`
    local success=$?

    if [ $success -eq 0 ]; then
        echo "PASS - Quality maintained with 'A' rating!"
        echo
        exit 0
    else
        echo "FAIL - Quality not maintained with 'A' rating!"
        echo
        echo "Running local run for more info..."
        echo

        local_run $local_path
        exit 1
    fi;
}

function usage() {
    echo "$0 {local|ci|ci-tests}"
}

case $1 in
    local)
        local_run $CODE_PATH
        ;;
    ci)
        ci_run $CODE_PATH
        ;;
    ci-tests)
        ci_run ./tests/v2/
        ;;
    *)
        usage
        ;;
esac