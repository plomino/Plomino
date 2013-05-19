
*** Settings ***

Resource          plone/app/robotframework/selenium.robot
Resource          plone/app/robotframework/saucelabs.robot
Library           Remote    ${PLONE_URL}/RobotRemote
Test Setup        Open SauceLabs test browser
Test Teardown     Run keywords  Report test status  Close all browsers

*** Test Cases ***
Plomino is installed
    Go to    ${PLONE_URL}
    Page should contain    mydb

Create form and use it to create documents
    Log in as the database owner
    Open the database
    Create test form
    Create field
    Generate view
    Add documents

*** Keywords ***
Log in as the database owner
    Enable autologin as    Site Administrator
    Set autologin username    ${TEST_USER_ID}
    Go to    ${PLONE_URL}

Open the database
    Go to    ${PLONE_URL}/mydb

Create test form
    Click link    Form
    Page should contain element    css=input#id
    Input text    id    frm_test
    Input text    title    Test Form
    Click button    css=a#FormLayout_code
    Input text    htmlSource    My field: <span class="plominoFieldClass">field_1</span>
    Click button    insert
    Click button    Save
    Page should contain    Changes saved.
    
Create field
    Click link    Field
    Page should contain element    css=input#id
    Input text    id    field_1
    Input text    title    field_1
    Click button    Save
    Page should contain    Changes saved.

Generate view
    Go to    ${PLONE_URL}/mydb/frm_test/manage_generateView

Add documents
    Go to    ${PLONE_URL}/mydb/frm_test
    Page should contain element    css=input[name='field_1']
    Input text    css=input[name='field_1']    Isaac Newton
    Click button    Save
    Go to    ${PLONE_URL}/mydb/frm_test
    Input text    css=input[name='field_1']    Marie Curie
    Click button    Save