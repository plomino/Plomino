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
  Wait until page contains element  css=.plominoSave
  Click Button  css=.plominoSave
  wait until page does not contain element  jquery=.plominoSave:visible

I save the settings
  Click link  link=SAVE

I save the fieldsettings
  Wait until page contains element  jquery=.fieldsettings--control-buttons a:contains("Save")
  Click Element  jquery=.fieldsettings--control-buttons a:contains("Save")
  wait until page contains element  jquery=.portalMessage:visible:contains("Changes saved")

I save the form
  Wait until page contains element  jquery=#mceu_0 button:contains("Save")
  Click Element  jquery=#mceu_0 button:contains("Save")

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

I change the fieldsettings tab to "${tab}" 
  wait until page contains element  jquery=a.mdl-tabs__tab:visible:contains("${tab}")
  Click Element  jquery=a.mdl-tabs__tab:visible:contains("${tab}")

I change the fieldmode to "${mode}" 
  wait until page contains element  jquery=#form-widgets-field_mode
  Select From List By Value  jquery=#form-widgets-field_mode  ${mode}

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
  Click Element  jquery=.mdl-button:visible:contains("Save")
  wait until page contains element  jquery=.mdl-button:visible:contains("Save")

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
  ${label} =  set variable  xpath=//*[contains(@class,"plominoFieldClass")][@data-plominoid="${fieldid}"]
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
  wait until page contains element  jquery=.mdl-button:visible:contains("Preview")
  wait until page does not contain element  jquery=.plomino-block-preloader:visible
  Click Element  jquery=.mdl-button:visible:contains("Preview")
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
  Wait until page contains element  css=.plominoFieldClass.mceNonEditable  #TODO change for test based on spinner
  Page should contain element  css=.plominoFieldClass.mceNonEditable
  Page should contain element  xpath=//*[contains(@class,"plominoFieldClass")][@data-plominoid="${fieldid}"]
  unselect frame

I see "${value}" in "${field}" in "${tab}"
  capture page screenshot
  Click Link  ${tab}
  ${text} =  get value  xpath=//input[@id=//label[normalize-space(text())="${field}"]/@for]
  should be equal  ${text}  ${value}

I will see the validation error "${error}" for field "${field}"
  wait until page contains element  jquery=#validation_failed

I will see the preview form saved
  page should contain button  Close