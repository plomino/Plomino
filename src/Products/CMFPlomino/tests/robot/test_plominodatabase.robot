


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
Test Teardown  Plone Test Teardown


*** Variables ****************************************************************

${BROWSER}  Chrome

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
  Set selenium timeout  100
  Given a logged-in test user
    and I open the ide for "mydb"
   When I open the first form
   #TODO When I open a form "frm_test"
   Then I can see field "field_1" in the editor

Scenario: I can add a field to a form
  Given a logged-in test user
    and I open the ide for "mydb"
    and I open the first form   #TODO   When I open a form "frm_test"
   When I add a "Text" field
   Then I can see field "text" in the editor

Scenario: As a site administrator I can add a form by click
  Given a logged-in test user
    and I open the ide for "mydb"
   When I add a form by click
   Then I can see "new-form" is open

Scenario: As a site administrator I can add a form by dnd
  Given a logged-in test user
    and I open the ide for "mydb"
   When I add a form by dnd
   Then I can see "new-form" is open

Scenario: I can rename a form
  Given I have a form open
   When I enter "mynewid" in "Id" in "Form Settings"
   Then I can see "mynewid" is open

Scenario: I can change the label and title at the same time
  Given I have a form open
   When I add a "Text" field
    and I edit the label "text" to "My text question"
   Then I see "My text question" in "Field title" in "Label Settings"
    and I select the field "text"
    and I see "My text question" in "Title" in "Field Settings"


*** Keywords *****************************************************************

Plone Test Teardown
    Run Keyword If Test Failed  ${SELENIUM_RUN_ON_FAILURE}
    Close all browsers


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
  Wait Until Element Is Not Visible  id=application-loader
  wait until page contains  ${db}

I have a form open
  Given a logged-in test user
    and I open the ide for "mydb"
    and I open the first form   #TODO   When I open a form "frm_test"


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
#  Click Element  css=button[title="Form"]
   Click Element  xpath=//div[@class="palette-wrapper"]//*[@title="Form"]
  wait until page contains  new-form
  wait until page contains element  css=div.mce-tinymce

I add a form by dnd
   wait until page contains  Form
   drag and drop  xpath=//div[@class="palette-wrapper"]//*[@title="Form"]  css=div.main-app.panel
  Capture Page Screenshot
  wait until page contains  new-form
  wait until page contains  css:div.mce-edit-area



I add a "${field}" field
  Capture Page Screenshot
  Click Element  xpath=//button[@title="${field}"]

I open a form "${formid}"
  Capture Page Screenshot
  wait until page contains  ${formid}
  #TODO: not sure why I can't isolate the text from the tree
  Click Element  xpath=//span[contains(@class,"tree-node--name")][normalize-space(text())="${formid}"]

I open the first form
  Click Element  xpath=//li//li[1]/span[contains(@class,"tree-node--name")]
  wait until page contains element   xpath=//div[@class="palette-wrapper"]//*[@title="Field"]
  wait until page contains element   css=.mce-edit-area iframe

I enter "${value}" in "${field}" in "${tab}"
  Click Link  ${tab}
  wait until page contains element  xpath=//input[@id=//label[normalize-space(text())="${field}"]/@for]
  Input Text  xpath=//input[@id=//label[normalize-space(text())="${field}"]/@for]  ${value}
  Click Link  link=SAVE
  wait until page contains element  link=SAVE

I edit the label "${fieldid}" to "${text}"
  select frame  css=.mce-edit-area iframe
  ${label} =  set variable  xpath=//span[contains(@class,"plominoLabelClass")][@data-plominoid="${fieldid}"]
  wait until page contains element  ${label}
  double click element  ${label}
  #Press Key    ${label}   \\1       #Ctrl-A
  #Press Key    ${label}   \\127     #DELETE
  clear element text  ${label}
  press key  ${label}  ${text}
  unselect frame

I select the field "${fieldid}"
  select frame  css=.mce-edit-area iframe
  ${label} =  set variable  xpath=//span[contains(@class,"plominoFieldClass")][@data-plominoid="${fieldid}"]
  wait until page contains element  ${label}
  click element  ${label}
  unselect frame
  wait until page contains  Field Settings



# --- THEN -------------------------------------------------------------------

a plominodatabase with the title '${title}' has been created
  Wait until page contains  Item created
  Page should contain  ${title}
  Page should contain  Item created

I can see the plominodatabase title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}

I can see "${formid}" is open
  Capture Page Screenshot
  page should contain   ${formid}
  page should contain element  css=div.mce-edit-area


I can see field "${fieldid}" in the editor
  Wait until page contains  Insert
  wait until page contains element  css=.mce-edit-area
  select frame  css=.mce-edit-area iframe
  Wait until page contains element  css=span.plominoFieldClass.mceNonEditable  #TODO change for test based on spinner
  Page should contain element  css=span.plominoFieldClass.mceNonEditable
  Page should contain element  xpath=//span[contains(@class,"plominoFieldClass")][@data-plominoid="${fieldid}"]
  unselect frame

I see "${value}" in "${field}" in "${tab}"
  capture page screenshot
  Click Link  ${tab}
  ${text} =  get value  xpath=//input[@id=//label[normalize-space(text())="${field}"]/@for]
  should be equal  ${text}  ${value}

