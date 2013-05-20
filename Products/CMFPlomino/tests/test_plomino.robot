
*** Settings ***

Resource          plone/app/robotframework/selenium.robot
Resource          plone/app/robotframework/saucelabs.robot
Resource          plone/app/robotframework/keywords.robot
Library           Remote    ${PLONE_URL}/RobotRemote
Test Setup        Open SauceLabs test browser
Test Teardown     Run keywords  Report test status  Close all browsers

*** Variables ***

${OTHER_ZOPE_HOST}  localhost
${OTHER_ZOPE_PORT}  8080
${OTHER_ZOPE_URL}  http://${OTHER_ZOPE_HOST}:${OTHER_ZOPE_PORT}
${OTHER_PLONE_SITE_ID}  Plone
${OTHER_PLONE_URL}  ${OTHER_ZOPE_URL}/${OTHER_PLONE_SITE_ID}

*** Test Cases ***

Manage a Plomino database
    Plomino is installed
    Log in as the database owner
    Open the database
    Generate view for   frm_test
    Add document    ${PLONE_URL}/mydb/frm_test    field_1     Isaac Newton
    Add document    ${PLONE_URL}/mydb/frm_test    field_1     Marie Curie
    Replicate the database design
    Add document    ${OTHER_PLONE_URL}/replicadb/frm_test    field_1     Victor Hugo
    Replicate documents
    Go to    ${OTHER_PLONE_URL}/replicadb/allfrmtest
    Page should contain    Marie Curie
    Re-replicate the database design
    Add document    ${PLONE_URL}/secondreplicadb/frm_test    field_1     Louis Pasteur
    Re-replicate documents
    Go to    ${PLONE_URL}/secondreplicadb/allfrmtest
    Page should contain    Marie Curie
    Delete replica

*** Keywords ***
Plomino is installed
    Go to    ${PLONE_URL}
    Page should contain    mydb

Log in as the database owner
    Enable autologin as    Site Administrator
    Set autologin username    ${TEST_USER_ID}
    Go to    ${PLONE_URL}

Open the database
    Go to    ${PLONE_URL}/mydb

Create form
    [Arguments]  ${FORM_ID}     ${FORM_TITLE}
    Click link    Form
    Page should contain element    css=input#id
    Input text    id    ${FORM_ID}
    Input text    title     ${FORM_TITLE}
    Click button    Save
    Page should contain    Changes saved.
    
Create field
    [Arguments]  ${FORM_ID}     ${FIELD_ID}
    Click link    Field
    Page should contain element    css=input#id
    Input text    id    ${FIELD_ID}
    Input text    title    ${FIELD_ID}
    Click button    Save
    Page should contain    Changes saved.
    Go to    ${PLONE_URL}/mydb/${FORM_ID}/edit
    Select frame  FormLayout_ifr 
    Input text  content  ${FIELD_ID}=
    Unselect Frame
    Click link  FormLayout_plominofield
    Select frame   css=.plonepopup iframe
    Select From List  plominoFieldId  ${FIELD_ID}
    Click button    insert
    Unselect Frame
    Click button    Save

Generate view for
    [Arguments]  ${FORM_ID}
    Go to    ${PLONE_URL}/mydb/${FORM_ID}/manage_generateView

Add document
    [Arguments]  ${FORM_PATH}     ${FIELD_ID}     ${VALUE}
    Go to    ${FORM_PATH}
    Page should contain element    css=input[name='${FIELD_ID}']
    Input text    css=input[name='${FIELD_ID}']    ${VALUE}
    Click button    Save

Replicate the database design
    Other server log in
    Go to    ${OTHER_PLONE_URL}
    Open Add New Menu
    Click Link  plominodatabase
    Wait Until Page Contains Element  title
    Input Text  title  replicadb
    Click button  name=form.button.save
    Page Should Contain  Changes saved.
    Go to    ${OTHER_PLONE_URL}/replicadb/DatabaseDesign
    Select Radio Button     sourcetype   server
    Input text     sourceurl-import   ${PLONE_URL}/mydb
    Input text     username-import   ${TEST_USER_ID}
    Input text     password-import   ${TEST_USER_PASSWORD}
    Click button    submit_refresh_import
    Select Radio Button     sourcetype   server
    Input text     sourceurl-import   ${PLONE_URL}/mydb
    Input text     username-import   ${TEST_USER_ID}
    Input text     password-import   ${TEST_USER_PASSWORD}
    Click button    submit_import

Re-replicate the database design
    Go to    ${PLONE_URL}
    Open Add New Menu
    Click Link  plominodatabase
    Wait Until Page Contains Element  title
    Input Text  title  secondreplicadb
    Click button  name=form.button.save
    Page Should Contain  Changes saved.
    Go to    ${PLONE_URL}/secondreplicadb/DatabaseDesign
    Select Radio Button     sourcetype   server
    Input text     sourceurl-import   ${OTHER_PLONE_URL}/replicadb
    Input text     username-import   admin
    Input text     password-import   admin
    Click button    submit_refresh_import
    Select Radio Button     sourcetype   server
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