*** Settings *****************************************************************

#Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/saucelabs.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote
Library           ${CURDIR}/../../../../robotframework-selenium2library-extensions/src/Selenium2LibraryExtensions    WITH NAME    Selenium2LibraryExtensions


*** Variables ****************************************************************

${BROWSER}  Chrome

*** Keywords *****************************************************************


Test Setup
    Open SauceLabs test browser

Test Teardown
    description_plominodatabase.Plone Test Teardown

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
  Go To  ${PLONE_URL}/${db}/++resource++Products.CMFPlomino/ide/index.html
  Wait Until page does not contain element  id=application-loader
  wait until page contains  ${db}


I have an empty form open
  Given a logged-in test user
   and I open the ide for "mydb"
   and I add a form by click
   and I can see "new-form" is open


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
    and description_views.I save the form as "form1"


# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I submit the plominodatabase form
  Wait Until Element Is Visible     jquery=.formControls input[id='form-buttons-save']    60s
  Wait Until Element Is Enabled     jquery=.formControls input[id='form-buttons-save']    60s
  Execute Javascript    $(".formControls input[id='form-buttons-save']").click()


I save the macro and the form
  Wait Until Element Is Visible     jquery=.actionButtons input[name='plomino_save']    60s
  Wait Until Element Is Enabled     jquery=.actionButtons input[name='plomino_save']    60s
  Execute Javascript    $(".actionButtons input[name='plomino_save']").click()
  # Wait Until Element Is Not Visible     jquery=.plone-modal-dialog    60s
  Sleep   5s
  wait until form is loaded
  I save the fieldsettings

I select current field
  # Click Element     jquery=.select2-container[id='s2id_field_name']     #input Click on the search box
  Click Element     jquery=#s2id_field_name
  Capture Page Screenshot
  # Sleep   3s
  Wait Until Element Is Visible     jquery=.select2-results li div:contains('Current field')      100s
  Capture Page Screenshot
  Click Element     jquery=.select2-results li div:contains('Current field')
  Capture Page Screenshot
  Sleep   3s

I save the settings
  Click link  link=SAVE

I save the fieldsettings
  wait until page does not contain element  jquery=.plomino-block-preloader:visible
  Wait until page contains element  jquery=.fieldsettings--control-buttons a:contains("Save")   60s
  Wait Until Element Is Visible     jquery=.fieldsettings--control-buttons a:contains("Save")   60s
  Wait Until Element Is Enabled     jquery=.fieldsettings--control-buttons a:contains("Save")   60s
  Wait Until Keyword Succeeds     100 sec    5 sec   Click Element  jquery=.fieldsettings--control-buttons a:contains("Save")
  sleep  0.5s
  wait until page does not contain element  jquery=.plomino-block-preloader:visible

I save the form
  I enter "the-form-is-saved" in "Id" in "Form Settings"

I go to the plominodatabase view
  Go To  ${PLONE_URL}/my-plominodatabase
  Wait until page contains  Site Map


I add a form by click
  wait until page does not contain element  jquery=.plomino-block-preloader:visible   60s
  Wait Until Element Is Visible     jquery=#add-new-form-tab    60s
  Click Element  jquery=#add-new-form-tab
  wait until page contains element  jquery=#modal-tab-plus[open]    60s
  Click Element  jquery=#modal-tab-plus button[data-create="form"]
  wait until page contains element  css=div.mce-tinymce   60s
  Wait Until Element Is Visible     css=div.mce-tinymce   60s

I add a hidewhen by click
  Wait Until Element Is Visible     jquery=.mdl-button[title='Hide When']   60s
  Wait Until Element Is Enabled     jquery=.mdl-button[title='Hide When']   60s
  Execute Javascript    $(".mdl-button[title='Hide When']").click()


I add a "${field}" field
  Click Element   jquery=plomino-palette-add .add-wrapper .templates button[title='${field}']
  Wait Until Element Is Visible     jquery=.mce-tinymce     60s

I add a "${field}" field by dnd
  sleep  0.3s
  wait until page does not contain element  jquery=.plomino-block-preloader:visible
  Selenium2Library.drag and drop  xpath=//div[@class="palette-wrapper"]//*[@title="${field}"]  css=.mce-edit-area iframe
  sleep  0.3s
  wait until page does not contain element  jquery=.plomino-block-preloader:visible
  sleep  0.3s

I add a form by dnd
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
  wait until page does not contain element  jquery=.plomino-block-preloader:visible
  wait until page contains element  jquery=plomino-tree > div > ul > li > ul > li > span:contains("${formid}"):first
  Click Element  jquery=plomino-tree > div > ul > li > ul > li > span:contains("${formid}"):first
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
  wait until page contains element   xpath=//div[@class="palette-wrapper"]//*[@title="Field"]   100s
  wait until page contains element   jquery=.mce-edit-area iframe:visible   60s

I enter "${value}" in "${field}" in "${tab}"
  Click Link  ${tab}
  wait until page contains element  xpath=//input[@id=//label[normalize-space(text())="${field}"]/@for]
  Wait Until Keyword Succeeds   100 sec  5 sec   Click Element   xpath=//input[@id=//label[normalize-space(text())="${field}"]/@for]
  Input Text  xpath=//input[@id=//label[normalize-space(text())="${field}"]/@for]   ${value}
  Wait Until Element Is Visible     jquery=.mdl-button:visible:contains("Save")     60s
  Wait Until Element Is Enabled     jquery=.mdl-button:visible:contains("Save")     60s
  Click Element  jquery=.mdl-button:visible:contains("Save")
  wait until page contains element   jquery=.mdl-button:visible:contains("Save")   60s

I enter "${value}" in "${field}" in the form
  wait until page contains element  xpath=//input[@id=//label[normalize-space(text())="${field}"]/@for]
  Input Text  xpath=//input[@id=//label[normalize-space(text())="${field}"]/@for]  ${value}

I select Text as value type
  Execute Javascript    window.document.getElementById("value_type-text").scrollIntoView(true);
  Sleep     3s
  Execute Javascript    $(".value_type-selectionfield span input[value='text']").click()


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

  Click element  css=.plomino-macros-rule .select2-container input
  Click element  xpath=//*[contains(@class,"select2-result")][normalize-space(text())="${macro}"]
  wait until page contains element  css=.plominoSave    60s
  Sleep     5s
  Capture Page Screenshot

I input the text "${text}" inside the field with id "${fieldid}"
  Input Text  jquery=#${fieldid}  ${text}

I preview "${formid}"
  Click Link  Form Settings
  wait until page contains element  jquery=.mdl-button:visible:contains("Preview")
  wait until page does not contain element  jquery=.plomino-block-preloader:visible
  wait until page does not contain element  jquery=.plomino-block-preloader:visible
  Click Element  jquery=.mdl-button:visible:contains("Preview")
  Sleep  2s
  select window  url=${PLONE_URL}/mydb/${formid}/view

I open service tab for Import/export of data
  Click Link    Service
  Wait Until Element Is Visible     jquery=plomino-palette-dbsettings .db-settings-wrapper .dbsettings--control-buttons button[id='ide-dbsettings__export-button']
  Click Element     jquery=plomino-palette-dbsettings .db-settings-wrapper .dbsettings--control-buttons button[id='ide-dbsettings__export-button']
  Wait Until Element Is Visible   jquery=dialog[id='db-import-export-dialog'] .mdl-dialog__content .mdl-tabs div[id='csv-importation'] form[name='importCSV']     100s

I can see Import/Export dialog open
  Element Should Be Visible   jquery=dialog[id='db-import-export-dialog'] .mdl-dialog__content .mdl-tabs div[id='csv-importation'] form[name='importCSV']

I click the tab "Design import/export" in Import/Export dialog
  Click Element     jquery=dialog[id='db-import-export-dialog'] .mdl-dialog__content .mdl-tabs div a[href='#design-import-export']
  Wait Until Element Is Visible     jquery=dialog[id='db-import-export-dialog'] .mdl-dialog__content .mdl-tabs div form[name='ExportDesign']

I select Export To Zip File
  Execute Javascript    window.document.getElementById("targettype-zipfile").scrollIntoView(true);
  Click Element     jquery=#targettype-zipfile

I can click Export button
  Click Element     jquery=dialog[id='db-import-export-dialog'] .mdl-dialog__content .mdl-tabs div form[name='ExportDesign'] table tbody tr td input[name='submit_export']



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
  Wait Until Element Is Visible     jquery=plomino-tabs .mdl-tabs .mdl-tabs__tab-bar a span:contains('${formid}')     10s
  Wait Until Element Is Visible     jquery=.mce-tinymce       30s

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
  Click Link  ${tab}
  wait until page does not contain element  jquery=.plomino-block-preloader:visible
  sleep  0.3s
  ${text} =  get value  xpath=//input[@id=//label[normalize-space(text())="${field}"]/@for]
  should be equal  ${text}  ${value}

I will see the validation error "${error}"
  Wait Until Page Contains      ${error}      60s

I will see the preview form saved
  page should contain button  Close


