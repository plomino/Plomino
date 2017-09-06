*** Keywords *****************************************************************

# --- Test Setup  ------------------------------------------------------------
Setup For View
  Open SauceLabs test browser
  I can create a new form "frm_empdata" and add some fields
  and I can add contents to "frm_empdata"

I can create a new form "frm_empdata" and add some fields
  Given a logged-in test user
   and I open the ide for "mydb"
   and I add a form by click
   and I add some fields to the form
   and I save the form as "frm_empdata"

I can add contents to "${formid}"
  I open the form "${formid}"
  and I add contents "John Doe" , "1234567890" and "123 Main St"
  and I save the form contents
  and I open the form "${formid}"
  and I add contents "Mary Light" , "0987654321" and "123 Chicago St"
  and I save the form contents
  and I open the form "${formid}"
  and I add contents "John Snow" , "12389098543" and "123 GOT Avenue"
  and I save the form contents
 
I add contents "${empname}" , "${empcontact}" and "${empaddr}"
  I enter "${empname}" on "name" field
  I enter "${empaddr}" on "address" field
  I enter "${empcontact}" on "contactno" field

I open the form "${formid}"
  Go To     ${PLONE_URL}/mydb/${formid}/OpenForm
  Wait Until Page Contains Element   jquery=article:contains('${formid}')    60s

I enter "${input_value}" on "${fieldid}" field
  Input Text    jquery=form div div .plominoGroupClass .plominoFieldGroup p span input[id='${fieldid}']    ${input_value} 

I save the form contents
  Click Element   jquery=form div .actionButtons input[name='plomino_save']
  Wait Until Element Is Visible   jquery=form div[id='renderedForm']
  Click Element   jquery=.formControls .actionButtons input[name='plomino_close']

I add some fields to the form
#Add text fields: Name, Address, Contact No
  I add a "Text" field
  and I edit the field "text" to "name"
  and I edit the title to "Name"
  and I save the current field settings
  and I click on Add tab
  Sleep   5s
  and I add a "Text" field
  and I edit the field "text" to "address"
  and I edit the title to "Address"
  and I save the current field settings
  and I click on Add tab
  Sleep   5s
  and I add a "Text" field
  and I edit the field "text" to "contactno"
  and I edit the title to "Contact No"
  and I save the current field settings
  Sleep   5s

I click on Add tab
  Click Link  Add
  Wait Until Element Is Visible     jquery=plomino-palette-add .add-wrapper

I edit the field "${fieldid}" to "${newid}"
  sleep  0.5s
  select frame  jquery=.mce-edit-area iframe:visible
  wait until page contains element  css=.plominoFieldClass[data-plominoid="${fieldid}"]
  click element  css=.plominoFieldClass[data-plominoid="${fieldid}"]
  Unselect Frame
  Wait Until Element Is Visible     jquery=#form-widgets-IShortName-id
  Input Text    jquery=#form-widgets-IShortName-id      ${newid}

I edit the title to "${newtitle}"
  Input Text    jquery=#form-widgets-IBasic-title     ${newtitle}

I save the current field settings
  Click Element     jquery=.fieldsettings--control-buttons a[id='ide-fieldsettings__save-button']
  Wait Until Element Is Visible     jquery=.fieldsettings--control-buttons


# --- Given ------------------------------------------------------------------

I have "$formid" open
  Given a logged-in test user
  and I open the ide for "mydb"
  Click Element   jquery=.treeview-wrapper .tree-node .tree-node--collapsible ul li span:contains('$formid')

I have a form and some fields saved
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
    and description_views.I save the form as "form-is-saved"

I save the form as "${form_name}"
  Click Element       jquery=.mdl-tabs .mdl-tabs__tab-bar a:contains('Form Settings')
  Wait Until Element Is Visible       jquery=.mdl-tabs__panel plomino-palette-formsettings .form-settings-wrapper .formsettings--control-buttons
  Input Text     jquery=form .mdl-tabs__panel fieldset .field input[id='form-widgets-IShortName-id']:last     ${form_name}
  Sleep   3s
  Click Element   jquery=form .mdl-tabs__panel fieldset .field input[id='form-widgets-IBasic-title']:last
  Input Text     jquery=form .mdl-tabs__panel fieldset .field input[id='form-widgets-IBasic-title']:last     ${form_name}
  Click Element       jquery=.mdl-tabs__panel plomino-palette-formsettings .formsettings--control-buttons .mdl-button[id='ide-formsettings__save-button']
  Wait Until Element Is Visible       jquery=.mdl-tabs__panel plomino-palette-formsettings .formsettings--control-buttons .mdl-button[id='ide-formsettings__save-button']     100s
  Sleep   3s

I select "${formid}" from form tree
  Click Element   jquery=plomino-tree .treeview-wrapper .tree-node .tree-node--collapsible ul li span:contains('${formid}')
  wait until form is loaded

# --- WHEN -------------------------------------------------------------------
I create a view
  Click Link  Add
  wait until page contains element  jquery=#PlominoView
  wait until page contains element  jquery=div.main-app.panel
  Click Element  xpath=//div[@class="palette-wrapper"]//*[@title="View"]

I create view
  Wait Until Element Is Visible   jquery=#PlominoView
  Click Element   jquery=.mdl-button[id='PlominoView']

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

I add a column "${myfield}"
  Click Link  Add
  Wait Until Element Is Visible     jquery=.mdl-button[id='column']
  Focus     jquery=.mdl-button[id='column']
  #Execute Javascript    $(".mdl-button[id='column']").click()
  #Click Element     jquery=.mdl-button[id='column']
  Click Button     jquery=.mdl-button[id='column']  
  Wait Until Element Is Visible    jquery=.header-row
  Capture Page Screenshot     check.jpg
  Wait Until Element Is Visible     jquery=.default form:first      100s
  Wait Until Element Is Visible     jquery=#form-widgets-IShortName-id
  # Click Element   jquery=#form-widgets-IShortName-id
  # Input Text  jquery=#form-widgets-IShortName-id  ${colid}
  # Click Element   jquery=#form-widgets-IBasic-title
  # Input Text  jquery=#form-widgets-IBasic-title  ${title}


  # wait until page contains element  jquery=.plomino-block-preloader:visible
  # wait until page does not contain element  jquery=.plomino-block-preloader:visible
  # Click Element  jquery=.view-editor__column-header:last
  # wait until page contains element  jquery=.view-editor__column-header.view-editor__column-header--selected
  # wait until page does not contain element  jquery=.plomino-block-preloader:visible
  Input Text  jquery=#form-widgets-IShortName-id  ${myfield}
  Input Text  jquery=#form-widgets-IBasic-title  ${myfield}
  Click Element     jquery=.fieldsettings--control-buttons a[id='ide-fieldsettings__save-button']     #this saves #{myfield column}
  Wait Until Element Is Visible     jquery=.mdl-tabs .mdl-tabs__panel plomino-palette-fieldsettings div .fieldsettings--control-buttons
  Wait Until Element Is Visible     jquery=plomino-tab .mdl-tabs__panel plomino-view-editor .view-editor .view-editor__inner form[id='plomino-view']


I add a column "${colid}" with title "${title}" and field value "${fieldvalue}"
  Wait Until Element Is Visible     jquery=#column
  Click Element  jquery=#column
  Wait Until Page Contains Element    jquery=.header-row
  # Click Element  jquery=.view-editor__column-header:last
  # wait until page contains element  jquery=.view-editor__column-header.view-editor__column-header--selected
  # wait until page does not contain element  jquery=.plomino-block-preloader:visible
  Wait Until Element Is Visible     jquery=#form-widgets-IShortName-id
  Click Element   jquery=#form-widgets-IShortName-id
  Input Text  jquery=#form-widgets-IShortName-id  ${colid}
  Click Element   jquery=#form-widgets-IBasic-title
  Input Text  jquery=#form-widgets-IBasic-title  ${title}
  Click Element   jquery=#form-widgets-displayed_field
  Select From List by Value     ${fieldvalue}
  Click Element     jquery=.fieldsettings--control-buttons a[id='ide-fieldsettings__save-button']     #this saves #{myfield column}
  Wait Until Element Is Visible     jquery=.mdl-tabs .mdl-tabs__panel plomino-palette-fieldsettings div .fieldsettings--control-buttons
  Wait Until Element Is Visible     jquery=plomino-tab .mdl-tabs__panel plomino-view-editor .view-editor .view-editor__inner form[id='plomino-view']



# --- THEN -------------------------------------------------------------------
I can see a view editor listing my data
  Wait until page contains element  jquery=.view-editor:contains("New View")
  Page should contain element  jquery=.view-editor:contains("New View")
  Wait Until Element Is Visible     jquery=.view-editor:contains("New View")
  Wait Until Element Is Visible     jquery=div[id='content-core'] table         100s

  # Element Should Contain  jquery=.plominoviewform div table tbody tr td     0 documents


I will see action "${actionid}" in the view
  Wait until page contains element  jquery=.view-editor .actionButtons input[id="${actionid}"]
  Page should contain element  jquery=.view-editor .actionButtons input[id="${actionid}"]

I will see column "${columnid}" in the view
  Wait until page contains element  jquery=.view-editor .view-editor__column-header[data-column="${columnid}"]
  Page should contain element  jquery=.view-editor .view-editor__column-header[data-column="${columnid}"]

I can rename the form to "${formId}"
    Click Element   jquery=.mdl-tabs .mdl-tabs__tab-bar a:contains('Form Settings')
    Wait Until Element Is Visible       jquery=.mdl-tabs__panel plomino-palette-formsettings .form-settings-wrapper .formsettings--control-buttons
    Input Text      jquery=#form-widgets-IShortName-id          ${formId}
    Input Text      jquery=#form-widgets-IBasic-title           ${formId}
    Click Element       jquery=.mdl-tabs__panel plomino-palette-formsettings .formsettings--control-buttons .mdl-button[id='ide-formsettings__save-button']
    Wait Until Element Is Visible       jquery=.mdl-tabs__panel plomino-palette-formsettings .formsettings--control-buttons .mdl-button[id='ide-formsettings__save-button']

I will see column header "${header}" and data "${rowdata1}", "${rowdata2}", "${rowdata3}"
  Wait until page contains element  jquery=table thead .header-row th:contains('${header}')
  Page Should Contain Element  jquery=table thead .header-row th:contains('${header}')
  Page Should Contain Element   jquery=tbody tr td a span span:contains('${rowdata1}')
  Page Should Contain Element   jquery=tbody tr td a span span:contains('${rowdata2}')  
  Page Should Contain Element   jquery=tbody tr td a span span:contains('${rowdata3}')

I can move "col_1" to "col_2"  
  Chain Click And Hold    jquery=.view-editor__column-header[data-column='${col_1}']
  Move By Offset  +20  0
  Chain Move To Element With Offset  jquery=.view-editor__column-header[data-column='${col_2}']  20  0
  Chain Sleep   5
  Chain Release     jquery=.view-editor__column-header[data-column='${col_2}']
  Chains Perform Now
  Wait Until Element Is Visible   jquery=.view-editor__column-header[data-column='${col_1}']    30s
  Wait Until Element Is Visible   jquery=.view-editor__column-header[data-column='${col_2}']    30s