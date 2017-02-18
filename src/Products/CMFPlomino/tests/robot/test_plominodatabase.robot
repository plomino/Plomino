# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s Products.CMFPlomino -t test_plominodatabase.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src Products.CMFPlomino.testing.PRODUCTS_CMFPLOMINO_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot src/Products/CMFPlomino/tests/robot/test_plominodatabase.robot
#
# See the http://docs.plone.org for further details (search for robot
# framework).
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***************************************************************

Scenario: As a site administrator I can add a PlominoDatabase
  Given a logged-in site administrator
    and an add plominodatabase form
   When I type 'My PlominoDatabase' into the title field
    and I submit the form
   Then a plominodatabase with the title 'My PlominoDatabase' has been created

Scenario: As a site administrator I can view a PlominoDatabase
  Given a logged-in site administrator
    and a plominodatabase 'My PlominoDatabase'
   When I go to the plominodatabase view
   Then I can see the plominodatabase title 'My PlominoDatabase'

Scenario: As a site administrator I can add a form
  Given a logged-in site administrator
    and a plominodatabase 'My PlominoDatabase'
    and I open the ide
   When I add a form
    and I add a "Field" field
    and I click save
   Then I can see the plominodatabase title 'My PlominoDatabase'

*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add plominodatabase form
  Go To  ${PLONE_URL}/++add++PlominoDatabase

a plominodatabase 'My PlominoDatabase'
  Create content  type=PlominoDatabase  id=my-plominodatabase  title=My PlominoDatabase


# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the plominodatabase view
  Go To  ${PLONE_URL}/my-plominodatabase
  Wait until page contains  Site Map

I open the ide
  #Click Element  link=IDE
  Go To  ${PLONE_URL}/my-plominodatabase/++resource++Products.CMFPlomino/ide/index.html
  wait until page contains  DB Settings

I add a form
   wait until page contains  Form
  Click Button  css=button[title="Form"]
#   Click Button  id=PlominoForm
# Drag And Drop
  Capture Page Screenshot
  wait until page contains  new-form
  wait until page contains  css:div.mce-edit-area

I add a "${field}" field
  Capture Page Screenshot
  Click Button  css=button[title="${field}"]


# --- THEN -------------------------------------------------------------------

a plominodatabase with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the plominodatabase title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
