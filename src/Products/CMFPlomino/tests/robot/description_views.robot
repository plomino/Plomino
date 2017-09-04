*** Keywords *****************************************************************


# --- Given ------------------------------------------------------------------
Given I have a form TestingOnly
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
    and description_views.I save the form

I save the form
    Click Element       jquery=.mdl-tabs .mdl-tabs__tab-bar a:contains('Form Settings')
    Wait Until Element Is Visible       jquery=.mdl-tabs__panel plomino-palette-formsettings .form-settings-wrapper .formsettings--control-buttons
    Input Text      jquery=#form-widgets-IShortName-id          the-form-is-saved  
    Click Element       jquery=.mdl-tabs__panel plomino-palette-formsettings .formsettings--control-buttons .mdl-button[id='ide-formsettings__save-button']
    Wait Until Element Is Visible       jquery=.mdl-tabs__panel plomino-palette-formsettings .formsettings--control-buttons .mdl-button[id='ide-formsettings__save-button']


# --- WHEN -------------------------------------------------------------------
I create a view
  Click Link  Add
  wait until page contains element  jquery=#PlominoView
  wait until page contains element  jquery=div.main-app.panel
  Click Element  xpath=//div[@class="palette-wrapper"]//*[@title="View"]
  wait until page contains  new-view

I add an action "${actionid}"
  Click Link  Add
  Wait Until Element Is Visible   jquery=#action
  Wait Until Element Is Visible   jquery=div.main-app.panel
  Click Element   jquery=#action
  wait until page contains element  jquery=.plomino-block-preloader:visible
  wait until page does not contain element  jquery=.plomino-block-preloader:visible
  Click Element  jquery=.actionButtons input[type="button"]:last
  wait until page contains element  jquery=.actionButtons input[type="button"].view-editor__action--selected
  wait until page does not contain element  jquery=.plomino-block-preloader:visible
  Input Text  jquery=#form-widgets-IShortName-id  ${actionid}
  Input Text  jquery=#form-widgets-IBasic-title  ${actionid}
  Click Element     jquery=.fieldsettings--control-buttons a[id='ide-fieldsettings__save-button']     #this saves #{myfield column}
  Wait Until Element Is Visible     jquery=.mdl-tabs .mdl-tabs__panel plomino-palette-fieldsettings div .fieldsettings--control-buttons
  Wait Until Element Is Visible     jquery=plomino-tab .mdl-tabs__panel plomino-view-editor .view-editor .view-editor__inner form[id='plomino-view']

  # Wait until page contains element  jquery=.fieldsettings--control-buttons a:contains("Save")
  # Click Element  jquery=.fieldsettings--control-buttons a:contains("Save")
  # wait until page does not contain element  jquery=.plomino-block-preloader:visible

I add a column "${myfield}"
  Click Link  Add
  Wait Until Element Is Visible     jquery=#column
  Click Element  jquery=#column
  wait until page contains element  jquery=.plomino-block-preloader:visible
  wait until page does not contain element  jquery=.plomino-block-preloader:visible
  Click Element  jquery=.view-editor__column-header:last
  wait until page contains element  jquery=.view-editor__column-header.view-editor__column-header--selected
  wait until page does not contain element  jquery=.plomino-block-preloader:visible
  Input Text  jquery=#form-widgets-IShortName-id  ${myfield}
  Input Text  jquery=#form-widgets-IBasic-title  ${myfield}
  Click Element     jquery=.fieldsettings--control-buttons a[id='ide-fieldsettings__save-button']     #this saves #{myfield column}
  Wait Until Element Is Visible     jquery=.mdl-tabs .mdl-tabs__panel plomino-palette-fieldsettings div .fieldsettings--control-buttons
  Wait Until Element Is Visible     jquery=plomino-tab .mdl-tabs__panel plomino-view-editor .view-editor .view-editor__inner form[id='plomino-view']
  # Select From List By Value  jquery=#form-widgets-displayed_field  the-form-is-saved/${myfield}
  # sleep  2s
  # Wait Until Element Is Visible     jquery=plomino-tiny-mce .tiny-editor .mce-tinymce
  # Wait Until Element Is Visible     jquery=.mdl-tabs .mdl-tabs__panel plomino-palette-add .add-wrapper
  # Capture Page Screenshot
  # Wait until page contains element  jquery=.fieldsettings--control-buttons a:contains("Save")
  # Click Element  jquery=.fieldsettings--control-buttons a:contains("Save")
  # wait until page does not contain element  jquery=.plomino-block-preloader:visible


# --- THEN -------------------------------------------------------------------
I can see a view editor listing my data
  Wait until page contains element  jquery=.view-editor:contains("New View")
  Page should contain element  jquery=.view-editor:contains("New View")

I will see action "${actionid}" in the view
  Wait until page contains element  jquery=.view-editor .actionButtons input[id="${actionid}"]
  Page should contain element  jquery=.view-editor .actionButtons input[id="${actionid}"]

I will see column "${columnid}" in the view
  Wait until page contains element  jquery=.view-editor .view-editor__column-header[data-column="${columnid}"]
  Page should contain element  jquery=.view-editor .view-editor__column-header[data-column="${columnid}"]
