*** Settings *****************************************************************
Resource  description_plominodatabase.robot
Resource  description_views.robot
Resource  description_redirect.robot
Resource  description_datagrid.robot

Test Setup   Test Setup
Test Teardown  Test Tear Down

*** Test Cases ***************************************************************

Scenario: I can edit a row in a datagrid in an unsaved form (PR #47)
  #PR 47 - [fix] Fix the parsing formid in input sent from server that prevent user from editing datagrid row
  Given I have a form "a_mainform" with some fields and I associate it to a datagrid form "a_datagridform"
  When I preview the datagrid form "a_datagridform"
  And I add a row to the datagrid form to display the main form "a_datagridform"
  And I fill in the fields and save the form "a_datagridform"
  When I edit the row in the datagrid
  Then the "a_datagridform" is rendered
  When I update the contents of "a_datagridform" and save the form
  Then I can see that the "a_datagridform" is updated

Scenario: I can add a datagrid to a multi-page form
  # PR 41: fix handling of empty values in datagrid rendering
  Given I have a multi-page form "a_mainpr41" with some fields and a datagrid
  When I preview the multi-page form "a_mainpr41"
  And I fill in the name and address fields and and go to the next page
  Then I can see the datagrid with civil status and job title fields
  And I can fill in the fields for the datagrid and save

Scenario: I can set field mapping in the datagrid
  #PR 48: Fix datagrid screwing up when field mapping is set
  Given I have a main form "a_mainpr48" with some fields and a datagrid
  ${mainpr48_url}=    Get Location
  When I preview the main form "a_mainpr48"
  And I add a row to the datagrid form to display the main form "a_mainpr48"
  And I fill in the fields of the main form and datagrid and then save the form
  ${dgrid_view_url}=  Get Location
  When I select the window for the "${mainpr48_url}" and set the field mapping for the datagrid
  And I reload the document view "${dgrid_view_url}"
  Then I can see the datagrid form view is arranged according to field mapping