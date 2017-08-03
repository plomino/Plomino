


# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s Products.CMFPlomino -t test_workflow.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src Products.CMFPlomino.testing.PRODUCTS_CMFPLOMINO_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot src/Products/CMFPlomino/tests/robot/test_workflow.robot
#
# See the http://docs.plone.org for further details (search for robot
# framework).
#
# ============================================================================



*** Settings *****************************************************************

Resource  plone/app/robotframework/saucelabs.robot
#Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot
Resource  description_workflow.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library           ${CURDIR}/../../../../robotframework-selenium2library-extensions/src/Selenium2LibraryExtensions    WITH NAME    Selenium2LibraryExtensions

Test Setup   Open SauceLabs test browser
Test Teardown  description_workflow.Plone Test Teardown



*** Variables ****************************************************************

${BROWSER}  Chrome

*** Test Cases ***************************************************************

Scenario: As a test user I can open Workflow editor
  Given a logged-in test user
    and I open the ide for "mydb"
    When I open service tab "Workflow"
    Then I can see element Start in the workflow editor

Scenario: As a test user I can add Form task to workflow editor
  Given a logged-in test user
    and I open the ide for "mydb"
    When I open service tab "Workflow"
    Then I can add a Form Task element by dnd




