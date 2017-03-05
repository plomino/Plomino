


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

Scenario: As a site administrator I can open a form
  Given a logged-in test user
    and I open the ide for "mydb"
   When I open the first form   #TODO   When I open a form "frm_test"
   Then I can see field "field_a" in the editor

Scenario: I can add a field to a form
  Given a logged-in test user
    and I open the ide for "mydb"
    and I open the first form   #TODO   When I open a form "frm_test"
   When I add a "Text" field
   Then I can see field "field_1" in the editor

#Scenario: As a site administrator I can add a form
#  Given a logged-in test user
#    and I open the ide for "mydb"
#   When I add a form by click
#   Then I can see "new-form" is open

*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

a logged-in test user
  Enable autologin as  Manager  ##TODO real test user

an add plominodatabase form
  Go To  ${PLONE_URL}/++add++PlominoDatabase

a plominodatabase 'My PlominoDatabase'
  Create content  type=PlominoDatabase  id=my-plominodatabase  title=My PlominoDatabase

I open the ide for "${db}"
  #Go To  ${PLONE_URL}/mydb
  #Click Element  link=IDE
  Go To  ${PLONE_URL}/${db}/++resource++Products.CMFPlomino/ide/index.html
  wait until page contains  ${db}


# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the plominodatabase view
  Go To  ${PLONE_URL}/my-plominodatabase
  Wait until page contains  Site Map


I add a form by click
   wait until page contains  Form
  Capture Page Screenshot
#  Click Element  css=button[title="Form"]
   Click Element  id=PlominoForm
  Capture Page Screenshot
  wait until page contains  new-form
  wait until page contains  css:div.mce-edit-area

I add a form by dnd
   wait until page contains  Form
   drag and drop  id=PlominoForm  css=div.main-app.panel
  Capture Page Screenshot
  wait until page contains  new-form
  wait until page contains  css:div.mce-edit-area



I add a "${field}" field
  Capture Page Screenshot
  Click Element  xpath=//button[@title="${field}"]

I open a form "${formid}"
  Capture Page Screenshot
  wait until page contains  ${formid}
  Click Element  xpath=//span[contains(@class,"tree-node--name") and contains(text(),"${formid}")]

I open the first form
  Click Element  xpath=//li//li[1]/span[contains(@class,"tree-node--name")]


# --- THEN -------------------------------------------------------------------

a plominodatabase with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the plominodatabase title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}

I can see "${formid}" is open
  page contains  new-form
  page contains element css:div.mce-edit-area


I can see field "${fieldid} in the editor
  Wait until page contains  Insert
  select frame  css=.mce-edit-area iframe
  Page should contain element  css=span.plominoFieldClass.mceNonEditable
