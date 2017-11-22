*** Settings *****************************************************************
Resource  description_views.robot
Resource  description_plominodatabase.robot
Resource  description_redirect.robot
Resource  description_dynamic.robot


*** Keywords *****************************************************************

I have a form "a_mainform" with some fields and I associate it to a datagrid form "a_datagridform"
    Given a logged-in test user
    I open the ide for "test_otherforms"
    I select "a_datagridform" from form tree

I preview the datagrid form "${formid}"
    I preview the dynamic form "${formid}"

I have a multi-page form "a_mainpr41" with some fields and a datagrid
    Given a logged-in test user
    I open the ide for "test_otherforms"
    I select "a_mainpr41" from form tree

I fill in the name and address fields and and go to the next page
    Wait Until Element Is Visible     jquery=#name
    Input Text    jquery=#name     Tester
    Wait Until Element Is Visible     jquery=#address
    Input Text    jquery=#address     123 Main St
    Wait Until Element Is Visible     jquery=input[name='next']
    Click Element     jquery=input[name='next']
    Capture Page Screenshot

I can see the datagrid with civil status and job title fields
    Wait Until Page Contains Element        jquery=.plomino-datagrid        60s
    Wait Until Element Is Visible       jquery=.plomino-datagrid        60s

I can fill in the fields for the datagrid and save
    I add a row to the datagrid form to display the main form "a_mainpr41"
    Wait Until Element Is Visible       jquery=#jobtitle
    Click Element   jquery=#jobtitle
    Input Text      jquery=#jobtitle        Software Tester
    Click Element   jquery=#civilstatus
    Input Text      jquery=#civilstatus        Test Status
    Wait Until Element Is Visible     jquery=input[name='plomino_save']     60s
    Press Key   jquery=input[name='plomino_save']       \\9
    Execute Javascript      $("input[name='plomino_save']").click();

I preview the multi-page form "${formid}"
    I preview the dynamic form "${formid}"