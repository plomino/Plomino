


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
Library           ${CURDIR}/../../../../robotframework-selenium2library-extensions/src/Selenium2LibraryExtensions    WITH NAME    Selenium2LibraryExtensions

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
  Set Selenium Speed  .5 seconds
  Set selenium timeout  100
  Given a logged-in test user
    and I open the ide for "mydb"
   # When I open the first form
   When I open a form "frm_test"
   Then I can see field "field_1" in the editor

Scenario: As a site administrator I can add a form by click
  Given a logged-in test user
    and I open the ide for "mydb"
   When I add a form by click
   Then I can see "new-form" is open

# html5 dnd not currently supported by selenium - https://github.com/seleniumhq/selenium-google-code-issue-archive/issues/3604
#Scenario: As a site administrator I can add a form by dnd
#  Given a logged-in test user
#    and I open the ide for "mydb"
#   When I add a form by dnd
#   Then I can see "new-form" is open

Scenario: I can rename a form
  Given I have a form open
   When I enter "mynewid" in "Id" in "Form Settings"
   Then I can see "mynewid" is open


Scenario: I can add a field to a form
  Given a logged-in test user
    and I open the ide for "mydb"
    and I open a form "frm_test"
   When I add a "Text" field
   Then I can see field "text" in the editor
    and I select the field "text"  # probably should be selected automatically? or group should?
    and I see "text" in "Id" in "Field Settings"

Scenario: I can add a field to a form by dnd
  Given a logged-in test user
    and I open the ide for "mydb"
    and I open the first form   #TODO   When I open a form "frm_test"
   When I add a "Text" field by dnd
   Then I can see field "text" in the editor
    and I select the field "text"
    and I see "text" in "Id" in "Field Settings"

Scenario: I can change the label and title at the same time
  Given I have a form open
   When I add a "Text" field
    and I edit the label "text" to "My text question"
   Then I see "My text question" in "Field title" in "Label Settings"
    and I select the field "text"
    and I see "My text question" in "Title" in "Field Settings"

Scenario: I can preview
  Given I have a form open
   When I preview "frm_test"
    and I submit the form
   Then I will see the preview form saved


Scenario: I can add a validation rule to a field
  Given I have a form open
   When I add a "Text" field
    and I select the field "text"
    and I add a macro "Field contains text" to "Field Settings"
    and I enter "blah" in "Field value" in the form
    and I save the macro
    and I add a macro "Invalid" to "Field Settings"
    and I enter "You can't say blah" in "Invalid message" in the form
    and I save the macro
    and I save the settings
    and I preview "frm_test"
    and I enter "blah" in "Untitled" in the form
    and I submit the form
   Then I will see the validation error "You can't say blah" for field "text"

# View tests

#Scenario: I can add a view
#  Given I have a form and some data saved
#   When I create a view
#   Then I will see the view settings
#    and I will see a view editor listing my data

#Scenario: I can add a column to a view
#  Given I have a form and some data saved
#   When I create a view
#    and I add a column "myfield"
#   Then I will see column "myfield" in the view

#Scenario: I can add an action to a view
#  Given I have a form and some data saved
#   When I create a view
#    and I add a action "myaction"
#   Then I will see column "myaction" in the view

#Scenario: I can add filter a view
#  Given I have a form and some data saved
#   When I create a view
#    and I see > 2 documents in the view
#    and I add a macro the the "view settings" called "number range"
#    and I set the range to <5
#   Then I will see less than 2 documents in the view



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
#  Wait Until Element Is Visible  id=application-loader
  Wait Until page does not contain element  id=application-loader
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

I save the macro
  Click Button  css=.plominoSave
  wait until element is not visible  css=.plominoClose

I save the settings
  Click link  link=SAVE

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
  Set Selenium Timeout  10 seconds
  wait until page contains element  jquery=#PlominoForm
  wait until page contains element  jquery=div.main-app.panel
#  drag and drop  jquery=#PlominoForm  jquery=plomino-app div.main-app.panel
#  drag and drop  jquery=#PlominoForm  jquery=plomino-app div.main-app.panel
#  drag and drop  jquery=#PlominoForm  jquery=plomino-app div.main-app.panel
#  drag and drop  jquery=#PlominoForm  jquery=plomino-app div.main-app.panel
#  drag and drop  jquery=#PlominoForm  jquery=plomino-app div.main-app.panel
  Chain Click And Hold  xpath=//div[@class="palette-wrapper"]//*[@title="Form"]
  Move By Offset  +300  0
  Chain Move To Element With Offset  css=div.main-app.panel  20  20
  chain sleep  5
  Chain Release  css=div.main-app.panel
  Chains Perform Now
  wait until page contains element  jquery=plomino-tree > div > ul > li > ul > li > span:contains("new-form")
  wait until page contains element  jquery=div.mce-edit-area



I add a "${field}" field
  Click Element  xpath=//div[@class="palette-wrapper"]//*[@title="${field}"]

I add a "${field}" field by dnd
  Selenium2Library.drag and drop  xpath=//div[@class="palette-wrapper"]//*[@title="${field}"]  css=.mce-edit-area iframe


I open a form "${formid}"
  Capture Page Screenshot
  wait until page contains  ${formid}
  Click Element  jquery=plomino-tree > div > ul > li > ul > li > span:contains("${formid}"):first
  #Click Element  xpath=//span[contains(@class,"tree-node--name")][normalize-space(text())="${formid}"]
  wait until form is loaded

I open the first form
  Click Element  xpath=//li//li[1]/span[contains(@class,"tree-node--name")]
  wait until form is loaded

wait until form is loaded
  wait until page contains element   xpath=//div[@class="palette-wrapper"]//*[@title="Field"]
  wait until page contains element   css=.mce-edit-area iframe
  select frame  css=.mce-edit-area iframe
  wait until page contains element   css=.mce-content-body
  unselect frame

I enter "${value}" in "${field}" in "${tab}"
  Click Link  ${tab}
  wait until page contains element  xpath=//input[@id=//label[normalize-space(text())="${field}"]/@for]
  Input Text  xpath=//input[@id=//label[normalize-space(text())="${field}"]/@for]  ${value}
  Click Link  link=SAVE
  wait until page contains element  link=SAVE

I enter "${value}" in "${field}" in the form
  wait until page contains element  xpath=//input[@id=//label[normalize-space(text())="${field}"]/@for]
  Input Text  xpath=//input[@id=//label[normalize-space(text())="${field}"]/@for]  ${value}


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

I add a macro "${macro}" to "${tab}"
  Click Link  ${tab}
  wait until element is visible  xpath=//input[@id=//label[normalize-space(text())="Id"]/@for]
  # Hacky way to scroll down the settings
  click element  xpath=//input[@id=//label[normalize-space(text())="Id"]/@for]
  Press key  xpath=//input[@id=//label[normalize-space(text())="Id"]/@for]  \t\t\t\t

  Click element  css=.plomino-macros-rule
  Click element  xpath=//*[contains(@class,"select2-result")][normalize-space(text())="${macro}"]
  wait until page contains element  css=.plominoSave

I preview "${formid}"
  Click Link  Form Settings
  wait until page contains element  link=PREVIEW
  Click link  link=PREVIEW
  select window  url=${PLONE_URL}/mydb/${formid}/OpenForm

# --- THEN -------------------------------------------------------------------

a plominodatabase with the title '${title}' has been created
  Wait until page contains  Item created
  Page should contain  ${title}
  Page should contain  Item created

I can see the plominodatabase title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}

I can see "${formid}" is open
  Set Selenium Timeout  10 seconds
  Capture Page Screenshot
  wait until page contains element  css=div.mce-edit-area
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

I will see the preview form saved
  page should contain button  Close