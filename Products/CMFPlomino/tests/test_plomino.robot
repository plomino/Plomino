
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

Form can be created
    Log in as the database owner
    Open the database
    Create test form

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
    Click button    Save
    Page should contain    Changes saved.
    
