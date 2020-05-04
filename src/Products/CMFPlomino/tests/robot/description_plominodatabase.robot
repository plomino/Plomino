*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/saucelabs.robot
Resource  plone/app/robotframework/keywords.robot
Resource  description_views.robot
Resource  utils.robot

Library  Remote  ${PLONE_URL}/RobotRemote
# Was used to try and do better DnD tests
#Library           ${CURDIR}/../../../../robotframework-selenium2library-extensions/src/Selenium2LibraryExtensions    WITH NAME    Selenium2LibraryExtensions


*** Variables ****************************************************************

${BROWSER}  Chrome
${DESIRED_CAPABILITIES}  platform:Linux,browserName:chrome

*** Keywords *****************************************************************


Test Setup
    Open SauceLabs test browser

Test Teardown
    description_plominodatabase.Plone Test Teardown

Plone Test Teardown
    Run Keyword If Test Failed  ${SELENIUM_RUN_ON_FAILURE}
    Report test status
    Close all browsers

# --- Keyword validations -----------------------------------------------------
Check "${position}" is a valid hidewhen position
  Run keyword if  '${position}'.lower() not in ['start', 'end']
  ...  Fail  '${position}' is not a valid hidewhen position. Position must be 'start' or 'end'

Check "${position}" is a valid position
  Run keyword if  '${position}'.lower() not in ['above', 'below']
  ...  Fail  '${position}' is not a valid position to drag to. Position must be 'above' or 'below'

# --- Onscreen element positions -----------------------------------------------------
Check element position with another element
  [Arguments]    ${element_1_xpath}    ${element_2_xpath}    ${position}

  Check "${position}" is a valid position

  ${element_1_position}=  Get Vertical Position  xpath=${element_1_xpath}
  ${element_2_position}=  Get Vertical Position  xpath=${element_2_xpath}

  Run keyword if  "${position}" == "above"
  ...  Should be true  ${element_1_position} < ${element_2_position}  "The element ${element_1_xpath} was not ${position} the element ${element_2_xpath}"
  ...  ELSE IF  "${position}" == "below"
  ...  Should be true  ${element_1_position} > ${element_2_position}  "The element ${element_1_xpath} was not ${position} the element ${element_2_xpath}"
  ...  ELSE
  ...  Fail


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

I add a dropdown field "${fieldname}"
  I add a "Dropdown" field
  I edit the field "dropdown" to "${fieldname}"
  I edit the title to "Home Type:"
  Execute Javascript    $("#form-widgets-ISelectionField-selectionlist").click()
  Clear Element Text    jquery=#form-widgets-ISelectionField-selectionlist
  Input Text       jquery=#form-widgets-ISelectionField-selectionlist     Rental|a \n New Construction|b \n Home For Sale|c
  I save the current field settings

I add some number fields
  I add a "Text" field
  I edit the number field "text" to "amount1"
  I edit the title to "Library Fee:"
  and I save the current field settings
  and I click on Add tab
  Sleep   5s
  and I add a "Text" field
  I edit the number field "text" to "amount2"
  I edit the title to "Misc Fee:"
  and I save the current field settings
  and I click on Add tab

I add a dynamic computed field "${fieldid}": with field mode "${fieldmode}"
  I add a "Text" field
  I edit the number field "text" to "total"
  I edit the title to "${fieldid}"
  Click Element     jquery=.mdl-tabs__tab-bar a:contains('Advanced'):first
  Wait Until Element Is Visible     jquery=#form-widgets-field_mode
  I select field mode "${fieldmode}"   
  I select dynamic rendering
  I save the current field settings
  Add macro "Display total"
  I fill in the fields name for Display Total screen with "amount1"
  I fill in the fields name for Display Total screen with "amount2"
  I save the macro and the form


I fill in the fields name for Display Total screen with "${field}"
  Click Element     jquery=#s2id_fields_name
  Wait Until Element Is Visible     jquery=.pat-select2 option[value='${field}']
  Click Element     jquery=.pat-select2 option[value='${field}']
  Sleep   2s

I select field mode "${fieldmode}"
  Press Key     jquery=#form-widgets-field_mode   \9
  Click Element     jquery=#form-widgets-field_mode
  Wait Until Element Is Visible     jquery=select option[value='${fieldmode}']
  Click Element     jquery=select option[value='${fieldmode}']

I select dynamic rendering
  Click Element     jquery=#form-widgets-isDynamicField-0

I add a dynamic text with field mode = computed for display
  I add a "Text" field
  I edit the field "text" to "message"
  I edit the title to "message"
  Click Element     jquery=.mdl-tabs__tab-bar a:contains('Advanced'):first
  Wait Until Element Is Visible     jquery=#form-widgets-field_mode
  I select field mode "DISPLAY"
  I select dynamic rendering
  I save the current field settings

I show the code of the current field
  Sleep   2s
  Click Element     jquery=.fieldsettings--control-buttons a[id='ide-fieldsettings__code-button']
  Wait Until Element Is Visible     jquery=.ace-editor .ace_content     60s

I insert formula that displays text
  Wait Until Element Is Visible     jquery=button:contains('Insert formula')    60s
  Click Element     jquery=button:contains('Insert formula')
  Wait Until Element Is Visible     jquery=.dropdown-menu li a:eq(1)
  Sleep   5s
  Click Element     jquery=.dropdown-menu li a:eq(1)
  Wait Until Element Is Visible     jquery=.ace_line:eq(3)

  Click Element     jquery=.ace_content
  Execute Javascript         $(".ace_text-input").click();
  Press Key     jquery=.ace_text-input      \\8
  Press Key     jquery=.ace_text-input      \\8
  Press Key     jquery=.ace_text-input      \\8
  Press Key     jquery=.ace_text-input      \\8  
  Press Key     jquery=.ace_text-input      \\8 

  Press Key     jquery=.ace_text-input      \\8
  Press Key     jquery=.ace_text-input      \\8
  Press Key     jquery=.ace_text-input      \\8
  Press Key     jquery=.ace_text-input      \\8  
  Press Key     jquery=.ace_text-input      \\8

  Press Key     jquery=.ace_text-input      \\8
  Press Key     jquery=.ace_text-input      \\8
  Press Key     jquery=.ace_text-input      \\8
  Press Key     jquery=.ace_text-input      \\8  
  Press Key     jquery=.ace_text-input      \\8

  Press Key     jquery=.ace_text-input      \\8  
  Press Key     jquery=.ace_text-input      \\8  


  Press Key     jquery=.ace_text-input    return 'Display This Text'\n
  Enter formula "## END formula }"
  I save the formula
  Sleep   5s

Enter formula "${formula}"
  Input Text    jquery=.ace_text-input    ${formula}


I save the formula
  Click Element   jquery=button[title='Save']

I render the form "${formid}"
  I select "${formid}" from form tree
  I preview "${formid}"

I can see the text created for the dynamic text field
  Wait Until Page Contains Element    jquery=.plominoFieldGroup p span:contains('Display This Text')    60s

I edit the number field "${fieldid}" to "${newid}"
  sleep  5s
  select frame  jquery=.mce-edit-area iframe:visible
  wait until page contains element  css=.plominoFieldClass[data-plominoid="${fieldid}"]     60s
  Wait Until Element Is Visible     css=.plominoFieldClass[data-plominoid="${fieldid}"]     60s
  Sleep   5s
  Click Element   css=.plominoFieldClass[data-plominoid="${fieldid}"]
  Unselect Frame
  Wait Until Element Is Visible     jquery=#form-widgets-IShortName-id    60s
  I edit the field as Number type
  Sleep     3s
  Click Element     jquery=#form-widgets-IShortName-id
  Input Text    jquery=#form-widgets-IShortName-id      ${newid}

I edit the field as Number type
  Press Key     jquery=#form-widgets-field_type     \9
  Click Element     jquery=#form-widgets-field_type
  Wait Until Element Is Visible     jquery=select option[value='NUMBER']
  Click Element     jquery=select option[value='NUMBER']

I input a value "${value}" on the Library Fee field and move to the next field
  Wait Until Element Is Visible     jquery=#amount1
  Click Element   jquery=#amount1
  Input Text    jquery=#amount1     ${value}
  Click Element   jquery=#amount2

I can see that the Total Amount value is updated with "${updatedvalue}"
  Wait Until Page Contains   ${updatedvalue}
  Wait Until Element Contains   jquery=#total      ${updatedvalue}

I input a value "${value}" on the Misc Fee and move to the next field
  Click Element   jquery=#amount2
  Input Text    jquery=#amount2     ${value}
  Press Key     jquery=.actionButtons input[value='Close']    \9



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
  I save the macro
  Sleep   5s
  wait until form is loaded
  I save the fieldsettings

I save the macro
  Wait Until Element Is Visible     jquery=.actionButtons input[name='plomino_save']    60s
  Wait Until Element Is Enabled     jquery=.actionButtons input[name='plomino_save']    60s
  Execute Javascript    $(".actionButtons input[name='plomino_save']").click()
  Sleep     10s
  # Wait Until Element Is Not Visible     jquery=.plone-modal-dialog    60s

I select current field
  # Click Element     jquery=.select2-container[id='s2id_field_name']     #input Click on the search box
  Click Element     jquery=#s2id_field_name
  # Sleep   3s
  Wait Until Element Is Visible     jquery=.select2-results li div:contains('Current field')      100s
  Click Element     jquery=.select2-results li div:contains('Current field')
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
  wait until form is loaded
  Sleep     5s

I add a dynamic hidewhen by click
  I add a hidewhen by click
  I select dynamic hide-when checkbox
  Add macro "Hide"
  I save the macro
  I save the hidewhen settings

I add another dynamic hidewhen by click
  I click on Add tab
  Sleep   5s
  I add a hidewhen by click
  I select dynamic hide-when checkbox
  Add macro "Hide"
  I save the macro
  I save the hidewhen settings

I select dynamic hide-when checkbox
  Wait Until Element Is Visible     jquery=#form-widgets-IShortName-id    100s    #increase waiting time to prevent stale element error
  Press Key     id=form-widgets-isDynamicHidewhen-0     \\9
  Click Element     id=form-widgets-isDynamicHidewhen-0

I can add a text field in the hidewhen
  I select the hidewhen start
  I click on Add tab
  I add a "Text" field
  Click Link  Form Settings
  Wait Until Element Is Visible     jquery=#ide-formsettings__save-button   60s
  Click Element     jquery=#ide-formsettings__save-button
  wait until form is loaded

I can add a text field in the second hidewhen
  I select the second hidewhen start
  I click on Add tab
  I add a "Text" field
  Click Link  Form Settings
  Wait Until Element Is Visible     jquery=#ide-formsettings__save-button   60s
  Click Element     jquery=#ide-formsettings__save-button
  wait until form is loaded

I can add a dropdown field in the hidewhen
  I select the hidewhen start
  I click on Add tab
  I add a "Dropdown" field
  Click Link  Form Settings
  Wait Until Element Is Visible     jquery=#ide-formsettings__save-button   60s
  Click Element     jquery=#ide-formsettings__save-button
  wait until form is loaded

I can add radio buttons in the hidewhen
  I select the hidewhen start
  I click on Add tab
  I add a "Radio buttons" field
  Click Link  Form Settings
  Wait Until Element Is Visible     jquery=#ide-formsettings__save-button   60s
  Click Element     jquery=#ide-formsettings__save-button
  wait until form is loaded

I can add a multi-selection field in the hidewhen
  I select the hidewhen start
  I click on Add tab
  I add a "Multi selection" field
  Click Link  Form Settings
  Wait Until Element Is Visible     jquery=#ide-formsettings__save-button   60s
  Click Element     jquery=#ide-formsettings__save-button
  wait until form is loaded

I can add checkboxes in the hidewhen
  I select the hidewhen start
  I click on Add tab
  I add a "Checkboxes" field
  Click Link  Form Settings
  Wait Until Element Is Visible     jquery=#ide-formsettings__save-button   60s
  Click Element     jquery=#ide-formsettings__save-button
  wait until form is loaded

I can add datagrid in the hidewhen
  I select the hidewhen start
  I click on Add tab
  I add a "Datagrid" field
  Click Link  Form Settings
  Wait Until Element Is Visible     jquery=#ide-formsettings__save-button   60s
  Click Element     jquery=#ide-formsettings__save-button
  wait until form is loaded

I select the hidewhen start
  wait until form is loaded
  Sleep     5s
  select frame  jquery=.mce-edit-area iframe:visible
  Click Element     css=.plominoHidewhenClass[data-plomino-position='start']
  Sleep   3s
  unselect frame

I select the second hidewhen start
  wait until form is loaded
  Sleep     5s
  select frame  jquery=.mce-edit-area iframe:visible
  Click Element     css=.plominoHidewhenClass[data-plomino-position='start'][data-plominoid='defaulthidewhen-1']
  Sleep   3s
  unselect frame

I save the hidewhen settings
  Wait Until Element Is Visible     jquery=.mdl-button[id='ide-fieldsettings__save-button']    60s
  Wait Until Keyword Succeeds     1 min   5 sec     Click Element     jquery=.mdl-button[id='ide-fieldsettings__save-button']


I click on HideWhen Settings tab
  Click Element     jquery=a:contains('Hidewhen Settings')

I add a "${field}" field
  Wait Until Element Is Visible     jquery=plomino-palette-add .add-wrapper .templates button[title='${field}']     60s
  Click Element   jquery=plomino-palette-add .add-wrapper .templates button[title='${field}']
  Wait Until Element Is Visible     jquery=.mce-tinymce     60s

## *DEPRECATED!* Use keyword `I add a ${item_title} item` instead.
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
  Wait Until Element Is Visible     jquery=.mce-edit-area iframe:visible   60s

I enter "${value}" in "${field}" in "${tab}"
  Click Link  ${tab}
  wait until page contains element  xpath=//input[@id=//label[normalize-space(text())="${field}"]/@for]
  Wait Until Keyword Succeeds   100 sec  5 sec   Click Element   xpath=//input[@id=//label[normalize-space(text())="${field}"]/@for]
  Input Text  xpath=//input[@id=//label[normalize-space(text())="${field}"]/@for]   ${value}
  Wait Until Element Is Visible     jquery=.mdl-button:visible:contains("Save")     60s
  Wait Until Element Is Enabled     jquery=.mdl-button:visible:contains("Save")     60s
  Click Element  jquery=.mdl-button:visible:contains("Save")
  wait until page contains element   jquery=.mdl-button:visible:contains("Save")   60s
  wait until form is loaded
  Sleep   5s

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
  Add macro "${macro}"

Add macro "${macro}"
  wait until element is visible  xpath=//input[@id=//label[normalize-space(text())="Id"]/@for]
  # Hacky way to scroll down the settings
  click element  xpath=//input[@id=//label[normalize-space(text())="Id"]/@for]
  Press key  xpath=//input[@id=//label[normalize-space(text())="Id"]/@for]  \t\t\t\t

  Click element  css=.plomino-macros-rule .select2-container input
  Click element  xpath=//*[contains(@class,"select2-result")][normalize-space(text())="${macro}"]
  wait until page contains element  css=.plominoSave    60s
  Sleep     5s

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
  Page should contain element  xpath=//*[@id="tinymce"]${xpath}\[contains(@class,"plominoHidewhenClass")][@data-plomino-position="${position}"]
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

I have a source and target forms with a field on them
  Given a logged-in test user
  I open the ide for "mydb"
  I add a target form
  I save the form as "target"
  Close the form
  Sleep   5s
  I add a source form
  Click Link  Form Settings
  Execute Javascript    window.document.getElementById("form-widgets-isPage").scrollIntoView(true);

  Wait Until Element Is Visible     jquery=.select2-input:eq(1)
  Click Element     jquery=.select2-input:eq(1)

  Click element  xpath=//*[contains(@class,"select2-result")][normalize-space(text())="Redirect in form on save"]
  wait until page contains element  css=.plominoSave    60s

  I select redirect type = Form
  I select retain form data in target form
  I save the macro
  I save the form as "source"

Close the form
  Wait Until Element Is Visible     jquery=.mdl-tabs__tab-close-button:eq(1)    60s
  Execute Javascript    $(".mdl-tabs__tab-close-button:eq(1)").click();
  Wait Until Element Is Visible       jquery=.workflow-node__start-text        60s

I add a target form
  I add a form by click
  I add a name field on the target form

I add a name field on the target form
  I add a "Text" field
  I edit the field "text" to "name"
  I edit the title to "Thank you"
  I save the current field settings
  Sleep   5s

I add a source form
  I add a form by click
  I add a name field on the source form

I add a name field on the source form
  Wait Until Element Is Visible     jquery=button[title='Text']   100s
  Wait Until Element Is Enabled     jquery=button[title='Text']   100s
  Click Element     jquery=button[title='Text']
  I edit the field "text" to "name"
  I edit the title to "Name:"
  Sleep   5s
  I save the current field settings
  Sleep   10s

I select redirect type = Form
  Wait Until Page Contains Element    jquery=.plone-modal-title:contains('Redirect in form on save')    60s
  Wait Until Element Is Visible       jquery=.plone-modal-title:contains('Redirect in form on save')    60s
  Click Element   jquery=#redirect_type-form

  Wait Until Element Is Visible     jquery=#s2id_form_redirect    60s
  Click Element     jquery=#s2id_form_redirect
  Wait Until Element Is Visible     jquery=.pat-select2 option[value='target']    60s
  Click Element     jquery=.pat-select2 option[value='target']
  Sleep   3s

I select retain form data in target form
  Wait Until Element Is Visible     jquery=#retain_form_data
  Click Element   jquery=#retain_form_data

I preview the source form
  Wait Until Element Is Visible     jquery=.mdl-button:visible:contains("Preview")    60s
  Wait Until Element Is Enabled     jquery=.mdl-button:visible:contains("Preview")    60s
  Click Element  jquery=.mdl-button:visible:contains("Preview")
  Sleep  2s
  select window  url=${PLONE_URL}/mydb/source/view

I preview the form "${form}"
  #Preview Redirect Form
  Wait Until Element Is Visible     jquery=.mdl-button:visible:contains("Preview")    60s
  Wait Until Element Is Enabled     jquery=.mdl-button:visible:contains("Preview")    60s
  Click Element  jquery=.mdl-button:visible:contains("Preview")
  Sleep  2s
  select window  url=${PLONE_URL}/test_redirect/${form}/view

I fill in the "${name}" field and save the source form
  Wait Until Element Is Visible     jquery=#${name}
  Input Text    jquery=#${name}     Tester
  Wait Until Element Is Visible     jquery=input[name='plomino_save']
  Click Element     jquery=input[name='plomino_save']
  Wait Until Element Is Visible     jquery=#name

I can see that the value entered on the source form is displayed on the "${name}" field of the target form
  Element Should Be Visible     jquery=input[name='${name}'][value='Tester']

I have a source form with AUTO request and a target form with POST request
  Given a logged-in test user
  I open the ide for "mydb"
  I add a target form with POST request
  I save the target form as "target"
  Close the form
  Sleep   5s
  I add a source form
  Click Link  Form Settings
  Execute Javascript    window.document.getElementById("form-widgets-isPage").scrollIntoView(true);

  Wait Until Element Is Visible     jquery=.select2-input:eq(1)
  Click Element     jquery=.select2-input:eq(1)

  Click element  xpath=//*[contains(@class,"select2-result")][normalize-space(text())="Redirect in form on save"]
  wait until page contains element  css=.plominoSave    60s

  I select redirect type = Form
  I select retain form data in target form
  I save the macro
  I save the form as "source"

I add a target form with POST request
  I add a form by click
  I add a name field on the source form
  I click on ADVANCED tab of the Form Settings
  I select form method="POST"
  Sleep   10s

I click on ADVANCED tab of the Form Settings
  Click Element       jquery=.mdl-tabs .mdl-tabs__tab-bar a:contains('Form Settings')
  Wait Until Element Is Visible       jquery=.mdl-tabs__panel plomino-palette-formsettings .form-settings-wrapper .formsettings--control-buttons
  Wait Until Element Is Visible     jquery=a:contains('Advanced'):eq(1)   60s
  Click Element     jquery=a:contains('Advanced'):eq(1)
  Wait Until Element Is Visible     jquery=#form-widgets-form_method    60s

I select form method="${value}"
  #value = GET, POST, Auto
  Wait Until Element Is Visible     jquery=#form-widgets-form_method    60s
  Click Element     jquery=#form-widgets-form_method
  Wait Until Element Is Visible     jquery=select option[value='${value}']
  Click Element     jquery=select option[value='${value}']

I save the target form as "${form_name}"
  Wait Until Element Is Visible     jquery=a:contains('Default'):eq(1)    60s
  Click Element   jquery=a:contains('Default'):eq(1)
  Sleep   5s
  Wait Until Element Is Visible     jquery=form .mdl-tabs__panel fieldset .field input[id='form-widgets-IShortName-id']:last    60s
  Click Element     jquery=form .mdl-tabs__panel fieldset .field input[id='form-widgets-IShortName-id']:last
  Input Text     jquery=form .mdl-tabs__panel fieldset .field input[id='form-widgets-IShortName-id']:last     ${form_name}
  Sleep   3s
  Click Element   jquery=form .mdl-tabs__panel fieldset .field input[id='form-widgets-IBasic-title']:last
  Input Text     jquery=form .mdl-tabs__panel fieldset .field input[id='form-widgets-IBasic-title']:last     ${form_name}
  Click Element       jquery=.mdl-tabs__panel plomino-palette-formsettings .formsettings--control-buttons .mdl-button[id='ide-formsettings__save-button']
  Wait Until Element Is Visible       jquery=.mdl-tabs__panel plomino-palette-formsettings .formsettings--control-buttons .mdl-button[id='ide-formsettings__save-button']     100s
  Sleep   3s
  wait until form is loaded

I have source and target forms
  Given a logged-in test user
  I open the ide for "mydb"
  I add a target form
  I save the form as "target"
  Close the form
  Sleep   5s
  I add a source form

I select the "Redirect On Load" radio button
  Click Link  Form Settings
  Execute Javascript    window.document.getElementById("form-widgets-isPage").scrollIntoView(true);

  Wait Until Element Is Visible     jquery=.select2-input:eq(1)
  Click Element     jquery=.select2-input:eq(1)

  Click element  xpath=//*[contains(@class,"select2-result")][normalize-space(text())="Redirect in form on save"]
  wait until page contains element  css=.plominoSave    60s

  I select redirect type = Form
  I select retain form data in target form

  Execute Javascript    window.document.getElementById("redirect_event-load").scrollIntoView(true);
  Click Element     jquery=#redirect_event-load

I will see a confirmation message
  Wait Until Page Contains Element    jquery=.plomino-hidewhen p:contains('Please ensure you add a condition to determine when to redirect')



# --- Using the IDE -------------------------------------------
I can see the "${tab_text}" tab is active
  Page Should Contain Element  xpath=//plomino-palette//*[@class="mdl-tabs__tab-bar"]//*[contains(text(), "${tab_text}") and contains(@class, "is-active")]


I open the "${tab_text}" tab
  ${is_open}  ${_}=  Run Keyword And Ignore Error  I can see the "${tab_text}" tab is active
  Run keyword if  "${is_open}" is "FAIL"
  ...  Click element  xpath=//plomino-palette//*[@class="mdl-tabs__tab-bar"]//*[contains(text(), "${tab_text}")]

  Wait Until Element Is Visible  xpath=//plomino-palette//*[@class="mdl-tabs__tab-bar"]//*[contains(text(), "${tab_text}")]/*


I open the "${tab_text}" form tab
  Wait Until Element Is Visible     jquery=.mce-tinymce     30s
  Wait until page does not contain element  jquery=.plomino-block-preloader:visible
  Click element  xpath=//plomino-tabs//*[text()="new-form"]
  Wait Until Element Is Visible     jquery=.mce-tinymce     30s
  Wait until page does not contain element  jquery=.plomino-block-preloader:visible


I add a "${item_title}" item
  I open the "Add" tab
  Wait Until Element Is Visible     xpath=//plomino-palette-add//*[contains(@class, "add-wrapper")]//*[text()="${item_title}"]
  Click Element  xpath=//plomino-palette-add//*[contains(@class, "add-wrapper")]//*[text()="${item_title}"]
  Wait Until Element Is Visible     jquery=.mce-tinymce     60s

I create a form titled "${form_title}" with the id "${form_id}"
  Wait Until Element Is Visible     jquery=.mce-tinymce     60s
  I add a "Form" item
  I open the "Form Settings" tab
  I change the setting "Id" to "${form_id}"
  I change the setting "Title" to "${form_title}"
  I press save on the current settings page

I change the setting "${settings_title}" to "${new_settings_value}"
  Input Text  xpath=//plomino-palette//*[contains(@class, "is-active")]//*[normalize-space(text())="${settings_title}"]/following-sibling::input  ${new_settings_value}


I press save on the current settings page
  Wait until element is visible  xpath=//plomino-palette//*[contains(@class, "mdl-tabs__panel") and contains(@class, "is-active")]//a[*//text()="save"]
  Click Element  xpath=//plomino-palette//*[contains(@class, "mdl-tabs__panel") and contains(@class, "is-active")]//a[*//text()="save"]
  Wait Until Element Is Visible     jquery=.mce-tinymce     30s
  Wait until page does not contain element  jquery=.plomino-block-preloader:visible

I close the IDE
  Click Element  xpath=//header//*[text()="Close IDE"]

I can see the item with the id "${field_id}" in the preview
  Select frame  jquery=.mce-edit-area iframe:visible
  Wait until element is visible  xpath=//*[@data-plominoid="${field_id}"]
  Unselect Frame

I can see an item "${field_id}" inside the subform "${subform_id}" in the preview
  Select frame  jquery=.mce-edit-area iframe:visible
  Wait until element is visible  xpath=//*[contains(@class, "plominoSubformClass") and @data-plominoid="${subform_id}"]//*[@id="${field_id}"]
  Unselect Frame

I can see a field with the id "${item_id}"
  Wait until element is visible  xpath=//*[@id="${item_id}"]
  Element should be visible      xpath=//*[@id="${item_id}"]


I can see the ${position} of the "${hidewhen_id}" hidewhen
  Check "${position}" is a valid hidewhen position
  Select frame  jquery=.mce-edit-area iframe:visible
  Wait until element is visible  xpath=//*[contains(@class, "plominoHidewhenClass") and @data-plominoid="${hidewhen_id}" and @data-plomino-position="${position}"]
  Unselect Frame


I can see that the item "${field_to_check_is_below}" is below the item "${field_to_check_is_above}" in the editor
  Select frame  jquery=.mce-edit-area iframe:visible 
  Check element position with another element
  ...  //body[@id="tinymce"]//*[@data-plominoid="${field_to_check_is_below}"]
  ...  //body[@id="tinymce"]//*[@data-plominoid="${field_to_check_is_above}"]
  ...  position=below
  Unselect frame


I can see that the ${hidewhen_position} handle of the "${hidewhen_id}" is ${position} the item "${field_to_check_position_against}" in the editor
  Select frame  jquery=.mce-edit-area iframe:visible
  Check element position with another element
  ...  //*[contains(@class, "plominoHidewhenClass") and @data-plominoid="${hidewhen_id}" and @data-plomino-position="${hidewhen_position}"]
  ...  //*[@id="tinymce"]//*[@data-plominoid="${field_to_check_position_against}"]
  ...  position=${position}
  Unselect frame


I should see the start page for the database "${db_id}"
  Element should be visible  xpath=//*[text()="${db_id}"]
  Element should be visible  xpath=//main//*[text()="Add new content"]
  Element should be visible  xpath=//main//*[text()="Add new content"]//following-sibling::*//*[text()="Form 1"]


I select the newly added subform in the editor
  Select frame  jquery=.mce-edit-area iframe:visible 
  Wait until element is visible  xpath=//body[@id="tinymce"]//*[contains(@class, "plominoSubformClass") and not(@data-plominoid)]
  Sleep  2 sec  # Bit hacky, but the subform needs to render before it is selectable for some reason
  Click element  xpath=//body[@id="tinymce"]//*[contains(@class, "plominoSubformClass") and not(@data-plominoid)]
  Unselect frame


I select the subform with a form id of "${new_subform_id}"
  ${subform_xpath}=  Convert to string  body[@id="tinymce"]//*[contains(@class, "plominoSubformClass") and @data-plominoid="${new_subform_id}"]
  Select frame  jquery=.mce-edit-area iframe:visible 
  Wait until element is visible  xpath=//${subform_xpath}
  Sleep  2 sec  # Bit hacky, but the subform needs to render before it is selectable for some reason
  Click element  xpath=//${subform_xpath}
  Unselect frame


I set the form with the title "${form_title}" as the currently selected subform's form
  Click element  css=#s2id_form-widgets-subform-id a
  Wait until element is visible  xpath=//li[contains(@class, "select2-result-selectable") and *//text() = "${form_title}"]
  Click element  xpath=//li[contains(@class, "select2-result-selectable") and *//text() = "${form_title}"]


I create an empty subform on the current form
  I add a "Subform" item
  I open the "Form Settings" tab
  I press save on the current settings page
  Reload page
  Wait Until page does not contain element  id=application-loader
  Wait until element is visible  css=.mce-edit-area


I create a subform on the current form
  I add a "Subform" item
  I select the newly added subform in the editor
  I set the form with the title "New Form" as the currently selected subform's form
  I open the "Form Settings" tab
  I press save on the current settings page
  Reload page
  Wait Until page does not contain element  id=application-loader
  Wait until element is visible  css=.mce-edit-area


I change the subform "${subform_id}" to use the subform "${new_subform_title}"
  I select the subform with a form id of "${subform_id}"
  I set the form with the title "${new_subform_title}" as the currently selected subform's form
  I open the "Form Settings" tab
  I press save on the current settings page
  Reload page
  Wait Until page does not contain element  id=application-loader
  Wait until element is visible  css=.mce-edit-area


I should see an empty subform
  ${subform_xpath}=  Convert to string  body[@id="tinymce"]//*[contains(@class, "plominoSubformClass")]
  Select frame  jquery=.mce-edit-area iframe:visible
  Wait until element is visible  css=#tinymce
  Wait until element is visible  xpath=//${subform_xpath}
  Element should be visible  xpath=//${subform_xpath}

  # This is how empty subforms are displayed. It doesn't look nice, it's just how it is...
  Element should be visible  xpath=//${subform_xpath}/h2
  Element should be visible  xpath=//${subform_xpath}/input[@value="..."]

  Unselect frame


I move the item "${item_to_move}" ${drag_position} the item "${item_to_move_about}"
  Check "${drag_position}" is a valid position

  Sleep  2 sec    # Another timing hack. Elements will sometimes remount

  Select frame  jquery=.mce-edit-area iframe:visible
  ${item_to_move_position}=        Get item or parent group top position  item_id=${item_to_move}
  ${item_to_move_about_position}=  Get item or parent group top position  item_id=${item_to_move_about}

  ${item_to_move_width}  ${item_to_move_height}=  Get item or parent group size  item_id=${item_to_move}
  ${item_to_move_about_width}  ${item_to_move_about_height}=  Get item or parent group size  item_id=${item_to_move_about}
  ${midpoint_vertical_offset}=  Evaluate  ${item_to_move_height} / 2        # This is because robot framework drag + drop starts from the middle
  ${midpoint_horizontal_offset}=  Evaluate  ${item_to_move_width} / 2       # This is because robot framework drag + drop starts from the middle
  ${above_offset_value}=  Evaluate  ${item_to_move_about_position} - ${item_to_move_position} - ${midpoint_vertical_offset}
  ${below_offset_value}=  Evaluate  (${item_to_move_about_position} - ${item_to_move_position}) + ${item_to_move_height} + ${midpoint_vertical_offset}
  ${left_offset_value}=  Evaluate  0 - ${midpoint_horizontal_offset} - 8    # Move a little more to the left of destination element
  ${right_offset_value}=  Evaluate  0                                       # Not known if this is required for move below
  ${vertical_offset}=  Set variable if  "${drag_position}" == "above"  ${above_offset_value}
  ${vertical_offset}=  Set variable if  "${drag_position}" == "below"  ${below_offset_value}  ${vertical_offset}
  ${horizontal_offset}=  Set variable if  "${drag_position}" == "above"  ${left_offset_value}
  ${horizontal_offset}=  Set variable if  "${drag_position}" == "below"  ${right_offset_value}  ${horizontal_offset}

  Drag And Drop By Offset  xpath=//body[@id="tinymce"]//*[@data-plominoid="${item_to_move}"]  ${horizontal_offset}  ${vertical_offset}
  Unselect frame


I move the ${hidewhen_position} of the "${hidewhen_id}" hidewhen ${drag_position} the item "${item_id}"
  Check "${hidewhen_position}" is a valid hidewhen position
  Check "${drag_position}" is a valid position

  Sleep  2 sec    # Another timing hack. Elements will sometimes remount

  Select frame  jquery=.mce-edit-area iframe:visible
  ${hidewhen_handle_position}=        Get Vertical Position  xpath=//body[@id="tinymce"]//*[@data-plominoid="${hidewhen_id}"]
  ${item_position}=            Get Vertical Position  xpath=//body[@id="tinymce"]//*[@data-plominoid="${item_id}"]
  # The below code should work, however it's complaining that "Get Element Size" isn't a keyword (Test written in Robot Framework 3.0)
  # ${UNUSED}  ${item_height}=  Get Element Size  xpath=//body[@id="tinymce"]//*[@data-plominoid="${item_position}"]
  ${item_height}=  Evaluate  300

  ${above_offset_value}=  Evaluate  (${hidewhen_handle_position} - ${item_position}) - ${item_height}
  ${below_offset_value}=  Evaluate  (${item_position} - ${hidewhen_handle_position}) + ${item_height}

  ${drag_offset}=  Set variable if  "${drag_position}" == "above"  ${above_offset_value}
  ${drag_offset}=  Set variable if  "${drag_position}" == "below"  ${below_offset_value}

  Drag And Drop By Offset  xpath=//body[@id="tinymce"]//*[@data-plominoid="${hidewhen_id}" and @data-plomino-position="${hidewhen_position}"]  0  ${drag_offset}
  Unselect frame



# --- Viewing the preview of a form --------------------------------------------------------------------
I can see that the item "${field_to_check_is_below}" is below the item "${field_to_check_is_above}" in the current form preview
  Check element position with another element
  ...  //*[@id="main-container"]//form//input[@id="${field_to_check_is_below}"]
  ...  //*[@id="main-container"]//form//input[@id="${field_to_check_is_above}"]
  ...  position=below

I can see that the ${hidewhen_position} handle of the "${hidewhen_id}" is ${position} the item "${field_to_check_position_against}" in the current form preview
  Check element position with another element
  ...  //*[contains(@class, "plominoHidewhenClass") and @data-plominoid="${hidewhen_id}" and @data-plomino-position="${hidewhen_position}"]
  ...  //*[@id="main-container"]//form//input[@id="${field_to_check_position_against}"]
  ...  position=below

I can see that the field "${field_id}" is hidden
  Element Should Not Be Visible  xpath=//*[@id="main-container"]//form//input[@id="${field_id}"]


