*** Settings *****************************************************************

Resource  plone/app/robotframework/saucelabs.robot
#Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library           ${CURDIR}/../../../../robotframework-selenium2library-extensions/src/Selenium2LibraryExtensions    WITH NAME    Selenium2LibraryExtensions

Test Setup   Open SauceLabs test browser
Test Teardown  description_workflow.Plone Test Teardown


*** Variables ****************************************************************

${BROWSER}  Chrome

*** Keywords *****************************************************************

Plone Test Teardown
    Run Keyword If Test Failed  ${SELENIUM_RUN_ON_FAILURE}
    Report test status
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

I have an empty form open
  Given a logged-in test user
   and I open the ide for "mydb"
   and I add a form by click
   and I can see "new-form" is open
   and sleep  0.5s

I waiting a little bit
  sleep  0.5s

I have an additional empty form open
  Given I add a form by click
   and I can see "new-form" is open

I have a form open
  Given a logged-in test user
    and I open the ide for "mydb"
    and I open the first form

I have an additional form open
  Given I open the first form   #TODO   When I open a form "frm_test"

I have a form and some data saved
  Given a logged-in test user
    and I open the ide for "mydb"
    and I open the first form
    sleep  1s
    and I add a "Text" field
    and I edit the label "text" to "First name"
    Click Link  Add
    and I add a "Text" field
    and I edit the label "text_1" to "Last name"
    Click Link  Add
    and I add a "Date" field
    and I save the form


# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I save the macro
  Wait until page contains element  css=.plominoSave
  wait until page does not contain element  jquery=.plomino-block-preloader:visible
  sleep  0.5s
  Click Button  jquery=.plominoSave:visible
  sleep  0.5s
  wait until page does not contain element  jquery=.plominoSave:visible

I save the settings
  Click link  link=SAVE

I save the fieldsettings
  wait until page does not contain element  jquery=.plomino-block-preloader:visible
  Wait until page contains element  jquery=.fieldsettings--control-buttons a:contains("Save")
  Click Element  jquery=.fieldsettings--control-buttons a:contains("Save")
  sleep  0.5s
  wait until page does not contain element  jquery=.plomino-block-preloader:visible

I save the form
  I enter "the-form-is-saved" in "Id" in "Form Settings"

I go to the plominodatabase view
  Go To  ${PLONE_URL}/my-plominodatabase
  Wait until page contains  Site Map


I add a form by click
  wait until page does not contain element  jquery=.plomino-block-preloader:visible
  Click Element  jquery=#add-new-form-tab
  wait until page contains element  jquery=#modal-tab-plus[open]
  Click Element  jquery=#modal-tab-plus button[data-create="form"]
   # wait until page contains  Form
   # Click Element  jquery=[href="#palette-tab-0-panel"]
   # Click Element  css=button[title="Form"]
   # Click Element  xpath=//div[@class="palette-wrapper"]//*[@title="Form"]
  wait until page contains  new-form
  wait until page contains element  css=div.mce-tinymce

I add a hidewhen by click
  I add a "Hide When" field
   # Wait until page contains  Hide When
   # Click Element  xpath=//div[@class="palette-wrapper"]//*[@title="Hide When"]

I add a "${field}" field
  Click Element  xpath=//div[@class="palette-wrapper"]//*[@title="${field}"]
  wait until page contains element  jquery=.plomino-block-preloader:visible
  sleep  0.5s
  wait until page does not contain element  jquery=.plomino-block-preloader:visible

I add a "${field}" field by dnd
  sleep  0.3s
  wait until page does not contain element  jquery=.plomino-block-preloader:visible
  Selenium2Library.drag and drop  xpath=//div[@class="palette-wrapper"]//*[@title="${field}"]  css=.mce-edit-area iframe
  # wait until page contains element  css=.plomino-block-preloader
  sleep  0.3s
  wait until page does not contain element  jquery=.plomino-block-preloader:visible
  sleep  0.3s

I create a view
  Click Link  Add
  wait until page contains element  jquery=#PlominoView
  wait until page contains element  jquery=div.main-app.panel
  Click Element  xpath=//div[@class="palette-wrapper"]//*[@title="View"]
  wait until page contains  new-view

I add a form by dnd
  Set Selenium Timeout  10 seconds
  wait until page contains element  jquery=#PlominoForm
  wait until page contains element  jquery=div.main-app.panel
  Chain Click And Hold  xpath=//div[@class="palette-wrapper"]//*[@title="Form"]
  Move By Offset  +300  0
  Chain Move To Element With Offset  css=div.main-app.panel  20  20
  chain sleep  5
  Chain Release  css=div.main-app.panel
  Chains Perform Now
  wait until page contains element  jquery=plomino-tree > div > ul > li > ul > li > span:contains("new-form")
  wait until page contains element  jquery=div.mce-edit-area

I open a form "${formid}"
  # Capture Page Screenshot
  wait until page does not contain element  jquery=.plomino-block-preloader:visible
  wait until page contains element  jquery=plomino-tree > div > ul > li > ul > li > span:contains("${formid}"):first
  Click Element  jquery=plomino-tree > div > ul > li > ul > li > span:contains("${formid}"):first
  #Click Element  xpath=//span[contains(@class,"tree-node--name")][normalize-space(text())="${formid}"]
  wait until form is loaded

I open the first form
  Click Element  xpath=//li//li[1]/span[contains(@class,"tree-node--name")]
  wait until form is loaded

I change the fieldsettings tab to "${tab}" 
  wait until page contains element  jquery=a.mdl-tabs__tab:visible:contains("${tab}")
  Click Element  jquery=a.mdl-tabs__tab:visible:contains("${tab}")

I change the fieldmode to "${mode}" 
  wait until page contains element  jquery=#form-widgets-field_mode
  Select From List By Value  jquery=#form-widgets-field_mode  ${mode}

wait until form is loaded
  wait until page contains element   xpath=//div[@class="palette-wrapper"]//*[@title="Field"]
  wait until page contains element   jquery=.mce-edit-area iframe:visible
  select frame  jquery=.mce-edit-area iframe:visible
  wait until page contains element   css=.mce-content-body
  unselect frame
  wait until page does not contain element  jquery=.plomino-block-preloader:visible

I enter "${value}" in "${field}" in "${tab}"
  Click Link  ${tab}
  wait until page contains element  xpath=//input[@id=//label[normalize-space(text())="${field}"]/@for]
  Input Text  xpath=//input[@id=//label[normalize-space(text())="${field}"]/@for]  ${value}
  Click Element  jquery=.mdl-button:visible:contains("Save")
  wait until page contains element  jquery=.mdl-button:visible:contains("Save")

I enter "${value}" in "${field}" in the form
  wait until page contains element  xpath=//input[@id=//label[normalize-space(text())="${field}"]/@for]
  Input Text  xpath=//input[@id=//label[normalize-space(text())="${field}"]/@for]  ${value}


Double Click On Label "${plominoid}"
  Execute Javascript  window.top.jQuery('iframe:visible').contents().find('.plominoLabelClass[data-plominoid="${plominoid}"]:visible').filter((i, e) => !window.top.jQuery(e).closest('.mce-offscreen-selection').length).removeClass('mceNonEditable').attr('contenteditable', 'true').addClass('plominoLabelClass--selected').addClass('mceEditable')


I edit the label "${fieldid}" to "${text}"
  sleep  0.5s
  wait until page does not contain element  jquery=.plomino-block-preloader:visible
  select frame  jquery=.mce-edit-area iframe:visible
  wait until page contains element  css=.plominoLabelClass[data-plominoid="${fieldid}"]
  click element  css=.plominoLabelClass[data-plominoid="${fieldid}"]
  Double Click On Label "${fieldid}"
  click element  css=.plominoLabelClass[data-plominoid="${fieldid}"]
  clear element text  css=.plominoLabelClass[data-plominoid="${fieldid}"]
  Input Text  css=.plominoLabelClass[data-plominoid="${fieldid}"]  ${text}
  unselect frame

I select the field "${fieldid}"
  wait until page does not contain element  jquery=.plomino-block-preloader:visible
  select frame  jquery=.mce-edit-area iframe:visible
  wait until page contains element  css=.plominoFieldClass[data-plominoid="${fieldid}"]
  click element  css=.plominoFieldClass[data-plominoid="${fieldid}"]
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

I input the text "${text}" inside the field with id "${fieldid}"
  Input Text  jquery=#${fieldid}  ${text}

I add an action "${actionid}"
  Click Link  Add
  wait until page contains element  jquery=#action
  wait until page contains element  jquery=div.main-app.panel
  Click Element  jquery=#action
  wait until page contains element  jquery=.plomino-block-preloader:visible
  wait until page does not contain element  jquery=.plomino-block-preloader:visible
  Click Element  jquery=.actionButtons input[type="button"]:last
  wait until page contains element  jquery=.actionButtons input[type="button"].view-editor__action--selected
  wait until page does not contain element  jquery=.plomino-block-preloader:visible
  Input Text  jquery=#form-widgets-IShortName-id  ${actionid}
  Input Text  jquery=#form-widgets-IBasic-title  ${actionid}
  Wait until page contains element  jquery=.fieldsettings--control-buttons a:contains("Save")
  Click Element  jquery=.fieldsettings--control-buttons a:contains("Save")
  wait until page does not contain element  jquery=.plomino-block-preloader:visible

I add a column "${myfield}"
  Click Link  Add
  Click Element  jquery=#column
  wait until page contains element  jquery=.plomino-block-preloader:visible
  wait until page does not contain element  jquery=.plomino-block-preloader:visible
  Click Element  jquery=.view-editor__column-header:last
  wait until page contains element  jquery=.view-editor__column-header.view-editor__column-header--selected
  wait until page does not contain element  jquery=.plomino-block-preloader:visible
  Input Text  jquery=#form-widgets-IShortName-id  ${myfield}
  Input Text  jquery=#form-widgets-IBasic-title  ${myfield}
  Select From List By Value  jquery=#form-widgets-displayed_field  the-form-is-saved/${myfield}
  sleep  2s
  Wait until page contains element  jquery=.fieldsettings--control-buttons a:contains("Save")
  Click Element  jquery=.fieldsettings--control-buttons a:contains("Save")
  wait until page does not contain element  jquery=.plomino-block-preloader:visible

I preview "${formid}"
  Click Link  Form Settings
  wait until page contains element  jquery=.mdl-button:visible:contains("Preview")
  wait until page does not contain element  jquery=.plomino-block-preloader:visible
  wait until page does not contain element  jquery=.plomino-block-preloader:visible
  Click Element  jquery=.mdl-button:visible:contains("Preview")
  # Run keyword if  page contains element  jquery=.mdl-button.agree:visible
  #   Click Element  jquery=.mdl-button.agree:visible
  Sleep  2s
  select window  url=${PLONE_URL}/mydb/${formid}/view

I open service tab "${tabId}"
  Click Link    Service
  wait until page contains  ${tabId}
  Click Element  jquery=.mdl-button:visible:contains(${tabId})

# --- THEN -------------------------------------------------------------------

a plominodatabase with the title '${title}' has been created
  Wait until page contains  Item created
  Page should contain  ${title}
  Page should contain  Item created

I can see the plominodatabase title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}

I will see that hidewhen is present
  Then I will see the "start" hidewhen on the path "/p[2]/span[1]"
   and I will see the "end" hidewhen on the path "/p[2]/span[2]"

I can see "${formid}" is open
  Set Selenium Timeout  10 seconds
  # Capture Page Screenshot
  wait until page contains element  css=div.mce-edit-area
  page should contain   ${formid}
  page should contain element  css=div.mce-edit-area

I can see a view editor listing my data
  Wait until page contains element  jquery=.view-editor:contains("New View")
  Page should contain element  jquery=.view-editor:contains("New View")

I will see column "${columnid}" in the view
  Wait until page contains element  jquery=.view-editor .view-editor__column-header[data-column="${columnid}"]
  Page should contain element  jquery=.view-editor .view-editor__column-header[data-column="${columnid}"]

I will see action "${actionid}" in the view
  Wait until page contains element  jquery=.view-editor .actionButtons input[id="${actionid}"]
  Page should contain element  jquery=.view-editor .actionButtons input[id="${actionid}"]

I can see field "${fieldid}" in the editor
  Wait until page contains  Insert
  wait until page contains element  jquery=.mce-edit-area iframe:visible
  select frame  jquery=.mce-edit-area iframe:visible
  Wait until page contains element  css=.plominoFieldClass.mceNonEditable  #TODO change for test based on spinner
  Page should contain element  css=.plominoFieldClass.mceNonEditable
  Page should contain element  xpath=//*[contains(@class,"plominoFieldClass")][@data-plominoid="${fieldid}"]
  unselect frame

I will see the "${position}" hidewhen on the path "${xpath}"
  wait until page contains element  jquery=.mce-edit-area iframe:visible
  select frame  jquery=.mce-edit-area iframe:visible
  Wait until page contains element  css=.plominoHidewhenClass.mceNonEditable  #TODO change for test based on spinner
  Page should contain element  xpath=//*[@id="tinymce"]${xpath}[contains(@class,"plominoHidewhenClass")][@data-plomino-position="${position}"]
  unselect frame

I see "${value}" in "${field}" in "${tab}"
  # capture page screenshot
  Click Link  ${tab}
  wait until page does not contain element  jquery=.plomino-block-preloader:visible
  sleep  0.3s
  ${text} =  get value  xpath=//input[@id=//label[normalize-space(text())="${field}"]/@for]
  should be equal  ${text}  ${value}

I will see the validation error "${error}" for field "${field}"
  wait until page contains element  jquery=#validation_failed

I will see the preview form saved
  page should contain button  Close


