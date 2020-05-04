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

I have a main form "a_mainpr48" with some fields and a datagrid
    Given a logged-in test user
    I open the ide for "test_otherforms"
    I select "a_mainpr48" from form tree

I preview the main form "${formid}"
    I preview the dynamic form "${formid}"

I fill in the fields of the main form and datagrid and then save the form
    Wait Until Element Is Visible       jquery=input[name='plomino_save']:eq(1)     60s
    Click Element   jquery=#dg-text
    Input Text      jquery=#dg-text      Test Only
    Click Element   jquery=#dg-name
    Input Text      jquery=#dg-name     Tester
    Execute Javascript      $("input[name='plomino_save']:eq(1)").click();
    Wait Until Element Is Visible       jquery=#special_reqts       60s
    Sleep   10s
    Click Element   jquery=#special_reqts
    Input Text      jquery=#special_reqts      Training Materials
    Wait Until Element Is Visible       jquery=.formControls .actionButtons input[name='plomino_save']      60s
    Execute Javascript      $(".formControls .actionButtons input[name='plomino_save']").click()
    Wait Until Element Is Visible       jquery=h1:contains('a_mainpr48')        60s

I select the window for the "${mainpr48_url}" and set the field mapping for the datagrid
    Select Window     url=${mainpr48_url}
    Sleep     5s
    wait until form is loaded
    Execute Javascript      $(".tree-node--collapsible .hasChild:contains('a_mainpr48') span:contains('datagrid')").click();
    wait until form is loaded
    Wait Until Element Is Visible     jquery=#form-widgets-IShortName-id        60s
    Click Element       jquery=#form-widgets-IShortName-id
    Set the field mapping to "dg-option, dg-name, dg-text"
    I save the current field settings

Set the field mapping to "${mapping}"
    Execute Javascript    window.document.getElementById("form-widgets-IDatagridField-field_mapping").scrollIntoView(true);
    Click Element   jquery=#form-widgets-IDatagridField-field_mapping
    Input Text       jquery=#form-widgets-IDatagridField-field_mapping       ${mapping}

I reload the document view "${page}"
    Select Window    url=${page}
    Reload Page
    Wait Until Element Is Visible     jquery=table tbody tr:eq(0)     60s
    Wait Until Element Is Visible     jquery=table tbody tr:eq(1)     60s

I can see the datagrid form view is arranged according to field mapping
    Wait Until Element Is Visible   jquery=tr th:contains('Pick an option')
    Wait Until Element Is Visible   jquery=tr td:contains('Option A')
    
    Wait Until Element Is Visible   jquery=tr th:contains('Name')
    Wait Until Element Is Visible   jquery=tr td:contains('Tester')

    Wait Until Element Is Visible   jquery=tr th:contains('Some text')
    Wait Until Element Is Visible   jquery=tr td:contains('Test Only')
