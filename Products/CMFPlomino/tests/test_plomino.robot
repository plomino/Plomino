*** Settings ***

Resource          plone/app/robotframework/selenium.robot
Resource          plone/app/robotframework/saucelabs.robot
Resource          plone/app/robotframework/keywords.robot
Library           Remote    ${PLONE_URL}/RobotRemote
Test Setup        Open SauceLabs test browser
Test Teardown     Run keywords  Report test status  Close all browsers

*** Variables ***

${OTHER_ZOPE_HOST}       localhost
${OTHER_ZOPE_PORT}       8080
${OTHER_ZOPE_URL}        http://${OTHER_ZOPE_HOST}:${OTHER_ZOPE_PORT}
${OTHER_PLONE_SITE_ID}   PloneRobotRemote
${OTHER_PLONE_INIT_URL}  http://admin:admin@${OTHER_ZOPE_HOST}:${OTHER_ZOPE_PORT}/@@plone-addsite?site_id=${OTHER_PLONE_SITE_ID}&title=Site&form.submitted:boolean=True&extension_ids:list=plonetheme.classic:default&extension_ids:list=plonetheme.sunburst:default&extension_ids:list=Products.CMFPlomino:default
${OTHER_PLONE_URL}       ${OTHER_ZOPE_URL}/${OTHER_PLONE_SITE_ID}

*** Test Cases ***

Manage a Plomino database
    Plomino is installed
    Log in as the database owner
    Open the database
    Generate view for     frm_test
    Add document          ${PLONE_URL}/mydb/frm_test    field_1     Isaac Newton
    Add document          ${PLONE_URL}/mydb/frm_test    field_1     Marie Curie
    Initialize other portal
    Replicate the database design
    Add document          ${OTHER_PLONE_URL}/replicadb/frm_test    field_1     Victor Hugo
    Replicate documents
    Go to                 ${OTHER_PLONE_URL}/replicadb/allfrmtest
    Page should contain   Marie Curie
    Re-replicate the database design
    Add document          ${PLONE_URL}/secondreplicadb/frm_test    field_1     Louis Pasteur
    Re-replicate documents
    Go to                 ${PLONE_URL}/secondreplicadb/allfrmtest
    Page should contain   Marie Curie

Check form methods
    Set Selenium Implicit Wait        20 seconds
    Log in as the database owner
    Open the database
    Create datagrid form
    Create form                       frmTest           Testing form
    # Use with the search forms
    Generate view for                 frmTest
    Check form method                 frmTest           POST
    Create form with method           frmGetTest        Testing GET form  GET
    Check form method                 frmGetTest        GET
    Create page form                  frmPageTest       Testing page form
    Check form method                 frmPageTest       GET
    Create search form                frmSearchTest     Testing search form
    Check form method                 frmSearchTest     GET
    Create form with method and type  frmPostingPage    Testing POST page  POST  Page
    Check form method                 frmPostingPage    POST
    Create form with method and type  frmPostingSearch  Testing POST search  POST  SearchForm
    Check form method                 frmPostingSearch  POST

Teardown
    Teardown other portal

*** Keywords ***
Plomino is installed
    Go to                ${PLONE_URL}
    Page should contain  mydb

Log in as the database owner
    Enable autologin as     Site Administrator
    Set autologin username  ${TEST_USER_ID}
    Go to    ${PLONE_URL}

Open the database
    Go to        ${PLONE_URL}/mydb

Open form
    [Arguments]  ${FORM_ID}  
    Go to        ${PLONE_URL}/mydb/${FORM_ID}

Create form
    [Arguments]              ${FORM_ID}  ${FORM_TITLE}
    Create form with method  ${FORM_ID}  ${FORM_TITLE}  Auto

Create form with method
    [Arguments]                       ${FORM_ID}  ${FORM_TITLE}  ${FORM_METHOD}
    Create form with method and type  ${FORM_ID}  ${FORM_TITLE}  ${FORM_METHOD}  Normal form

Create page form
    [Arguments]                       ${FORM_ID}  ${FORM_TITLE}
    Create form with method and type  ${FORM_ID}  ${FORM_TITLE}  Auto  Page

Create search form
    [Arguments]                       ${FORM_ID}  ${FORM_TITLE}
    Create form with method and type  ${FORM_ID}  ${FORM_TITLE}  Auto  SearchForm

Create form with method and type
    [Arguments]          ${FORM_ID}  ${FORM_TITLE}  ${FORM_METHOD}  ${FORM_TYPE}
    Open the database
    Click link           Form
    # Page should contain element    css=input#id
    Input text           id     ${FORM_ID}
    Input text           title  ${FORM_TITLE}
    Checkbox Should Be Selected  xpath=//input[@name='FormMethod' and @value='Auto']
    Run keyword if  '${FORM_METHOD}' != 'Auto'      Select Checkbox   xpath=//input[@name='FormMethod' and @value='${FORM_METHOD}']
    Run keyword if  '${FORM_TYPE}' == 'Page'        Select Checkbox   isPage
    Run keyword if  '${FORM_TYPE}' == 'SearchForm'  Select Checkbox   isSearchForm
    Run keyword if  '${FORM_TYPE}' == 'SearchForm'  Select from list  SearchView  allfrmTest
    Click button         Save
    Page should contain  Changes saved.

Create field
    [Arguments]           ${FORM_ID}  ${FIELD_ID}
    Create field of type  ${FORM_ID}  ${FIELD_ID}  Default

Create field of type
    [Arguments]          ${FORM_ID}  ${FIELD_ID}  ${FIELD_TYPE}
    Open form  ${FORM_ID}
    Click link           Field
    Page should contain element      css=input#id
    Input text           id     ${FIELD_ID}
    Input text           title  ${FIELD_ID}
    Run keyword if  '${FIELD_TYPE}' != 'Default'  Select field type  ${FIELD_TYPE}
    Click button         Save
    Page should contain  Changes saved.
    Run keyword if  '${FIELD_TYPE}' == 'DATAGRID'  Configure datagrid field  ${FIELD_ID}
    Add field to layout  ${FORM_ID}  ${FIELD_ID} 

Add field to layout
    [Arguments]          ${FORM_ID}  ${FIELD_ID} 
    Go to                ${PLONE_URL}/mydb/${FORM_ID}/edit
    Wait Until Page Contains Element  FormLayout_ifr
    Select frame         FormLayout_ifr 
    Input text           content  ${FIELD_ID}=
    Unselect Frame
    Click link           FormLayout_plominofield
    Select frame         css=.plonepopup iframe
    Select From List     plominoFieldId  ${FIELD_ID}
    Click button         insert
    Unselect Frame
    Click button         Save

Create datagrid form
    # [Arguments]          ${FORM_ID}
    Create form          dgForm  Datagrid form

Check form method
    [Arguments]          ${FORM_ID}  ${FORM_METHOD}
    Open form            ${FORM_ID}
    ${form_method_attr} =  Get element attribute  plomino_form@method
    Should be equal  ${form_method_attr.upper()}  ${FORM_METHOD}
    Check datagrid method  ${FORM_ID}  ${FORM_METHOD}

Check datagrid method
    [Arguments]           ${FORM_ID}  ${FORM_METHOD}
    Create field of type  ${FORM_ID}  dgfield  DATAGRID
    Wait Until Page Contains Element  dgfield_gridvalue
    # Looks like only visible text is counted
    # Element Should Contain  xpath=//input[@id='dgfield_gridvalue']/following-sibling::script  'sServerMethod': '${FORM_METHOD.upper()}'
    # Element Should Contain  dgfield_js  'sServerMethod': 'GET'
    ${page_source} =  Get source
    Should match regexp  ${page_source}  dgfield[^>]+'sServerMethod': '${FORM_METHOD.upper()}'
    # Page should contain  'sServerMethod': 'GET'
    # Page should contain  'sServerMethod': '${FORM_METHOD.upper()}'

Select field type
    [Arguments]  ${FIELD_TYPE}
    Select from list  FieldType  ${FIELD_TYPE}

Configure datagrid field
    [Arguments]       ${FIELD_ID}
    Click link        Settings
    Select from list  form.associated_form  dgForm
    Input text        form.field_mapping  one,two
    Click button      form.actions.apply

Generate view for
    [Arguments]  ${FORM_ID}
    Go to        ${PLONE_URL}/mydb/${FORM_ID}/manage_generateView

Add document
    [Arguments]  ${FORM_PATH}  ${FIELD_ID}  ${VALUE}
    Go to        ${FORM_PATH}
    Page should contain element  css=input[name='${FIELD_ID}']
    Input text    css=input[name='${FIELD_ID}']  ${VALUE}
    Click button  Save

Replicate the database design
    Other server log in
    Go to         ${OTHER_PLONE_URL}
    Open Add New Menu
    Click Link    plominodatabase
    Wait Until Page Contains Element  title
    Input Text    title  replicadb
    Click button  name=form.button.save
    Page Should Contain  Changes saved.
    Go to    ${OTHER_PLONE_URL}/replicadb/DatabaseDesign
    Select Radio Button     sourcetype   sourcetype-server
    Input text     sourceurl-import  ${PLONE_URL}/mydb
    Input text     username-import   ${TEST_USER_ID}
    Input text     password-import   ${TEST_USER_PASSWORD}
    Click button   submit_refresh_import
    Select Radio Button     sourcetype   sourcetype-server
    Input text     sourceurl-import  ${PLONE_URL}/mydb
    Input text     username-import   ${TEST_USER_ID}
    Input text     password-import   ${TEST_USER_PASSWORD}
    Click button   submit_import

Re-replicate the database design
    Go to    ${PLONE_URL}
    Open Add New Menu
    Click Link  plominodatabase
    Wait Until Page Contains Element  title
    Input Text  title  secondreplicadb
    Click button  name=form.button.save
    Page Should Contain  Changes saved.
    Go to    ${PLONE_URL}/secondreplicadb/DatabaseDesign
    Select Radio Button     sourcetype   sourcetype-server
    Input text     sourceurl-import   ${OTHER_PLONE_URL}/replicadb
    Input text     username-import   admin
    Input text     password-import   admin
    Click button    submit_refresh_import
    Select Radio Button     sourcetype   sourcetype-server
    Input text     sourceurl-import   ${OTHER_PLONE_URL}/replicadb
    Input text     username-import   admin
    Input text     password-import   admin
    Click button    submit_import

Replicate documents
    Go to    ${OTHER_PLONE_URL}/replicadb/DatabaseReplication
    Click Button    add_replication
    Input text      name    my-replication
    Input text      remoteUrl   ${PLONE_URL}/mydb
    Input text      username    ${TEST_USER_ID}
    Input text      password    ${TEST_USER_PASSWORD}
    Select Radio Button     repType   pushpull
    Click Button    save_replication
    Select Checkbox     selection-1
    Click Button    submit_replication

Re-replicate documents
    Go to    ${PLONE_URL}/secondreplicadb/DatabaseReplication
    Click Button    add_replication
    Input text      name    my-replication
    Input text      remoteUrl   ${OTHER_PLONE_URL}/replicadb
    Input text      username    admin
    Input text      password    admin
    Select Radio Button     repType   pushpull
    Click Button    save_replication
    Select Checkbox     selection-1
    Click Button    submit_replication

Delete replica
    Go to    ${OTHER_PLONE_URL}/replicadb
    Open Action Menu
    Click Link  link=Delete
    Click Overlay Button    Delete

Other server log in
    Go to  ${OTHER_PLONE_URL}/login_form
    Page should contain element  __ac_name
    Page should contain element  __ac_password
    Page should contain button  Log in
    Input text for sure  __ac_name  admin
    Input text for sure  __ac_password  admin
    Click Button  Log in

Initialize other portal
    Go to  ${OTHER_PLONE_INIT_URL}

Teardown other portal
    Go to            http://admin:admin@${OTHER_ZOPE_HOST}:${OTHER_ZOPE_PORT}/manage_main
    Select checkbox  PloneRobotRemote
    Click button     Delete
