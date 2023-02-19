import os
import shutil
import json
from ClippyKindle import ClippyKindle

FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))  # folder containing this file
TMP_PATH = os.path.join(FOLDER_PATH, "tmp_output")


def pytest_sessionstart(session):
    """runs before all tests start https://stackoverflow.com/a/35394239"""
    print("in seesion start")
    if os.path.isdir(TMP_PATH):
        shutil.rmtree(TMP_PATH)
    os.mkdir(TMP_PATH)


def pytest_sessionfinish(session, exitstatus):
    """
    delete tmp output folder after all tests finish (if all passed)
    """
    if exitstatus == 0:
        shutil.rmtree(TMP_PATH)
    else:
        print("non-zero exit status, leaving for reference folder: {}".format(TMP_PATH))


def helperCompare(stubName):
    """
    test file parses successfully to its expected output
    """

    # input and expected output file paths
    inputFile = os.path.join(FOLDER_PATH, "examples/{}.txt".format(stubName))
    outputFile = os.path.join(
        FOLDER_PATH, "examples/expected_output/{}.json".format(stubName)
    )
    print("testing file: {}".format(inputFile))

    # read expected output
    with open(outputFile) as f:
        expectedJson = json.load(f)  # expected output

    # produce actual output
    bookList = ClippyKindle.parseClippings(inputFile)  # list of Book objects
    outData = []
    for book in bookList:
        # book.sort(removeDups=False) # (sorting/removing duplicates)
        outData.append(book.toDict())
    # write output to file for reference
    with open(os.path.join(TMP_PATH, "{}.json".format(stubName)), "w") as f:
        json.dump(outData, f, indent=2)  # write indented json to file (for reference)

    assert json.dumps(outData, sort_keys=True) == json.dumps(
        expectedJson, sort_keys=True
    )
