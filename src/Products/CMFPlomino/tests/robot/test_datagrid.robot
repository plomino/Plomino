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

# #---------Work In Progress-------
# # Scenario: I can add a datagrid to multi-page form
# #   #PR 41: fix handling of empty values in datagrid rendering
# #   Maximize Browser Window
# #   Given a logged-in test user
# #    and I open the ide for "mydb"
# #    and I add a form by click
# #    and I add a datagrid to the form
# #    and I add a field to the newly created form
# #    and I add a page break to the form
# #    and I add a datagrid after the page break
# #    Capture Page Screenshot