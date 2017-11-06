*** Settings *****************************************************************
Resource  description_plominodatabase.robot
Resource  description_views.robot

Test Setup   Test Setup
Test Teardown   Test Tear Down

*** Test Cases ***************************************************************

Scenario: I can add a view
  Given I have a form and some fields saved
   When I create a view
   Then I can see a view editor listing my data

Scenario: I can add columns to a view
  Given a logged-in test user
   and I open the ide for "mydb"
   and I select "frm_test" from form tree
   and I create view
  When I add a column "text" with retries
   and I click on Add tab
   and I add a column "text_1" with retries
   and I click on Add tab
   and I add a column "text_2" with retries
   Set selenium timeout     10s
  Capture Page Screenshot 
  Then I can see columns "text", "text_1", and "text_2" in the view

Scenario: I can add an action to a view
  Given I have a form and some data saved
   and I create a view
   and I can see a view editor listing my data
   When I add an action "my action"
   Then I will see action "my-action" in the view

Scenario: I can reoder the columns in the view
  #This tests for PR27
  Given a logged-in test user
   and I open the ide for "mydb"
   and I select "frm_test" from form tree
   and I create view
   When I add a column "text" with retries
   and I click on Add tab
   and I add a column "text_1" with retries
   and I click on Add tab
   and I add a column "text_2" with retries
   Set selenium timeout     10s
  Then I can move the column "text" to column "text_1" by offset "20" "0"
   And I can move the column "text_2" to column "text" by offset "-20" "0"
   And I can move the column "text_1" to column "text" by offset "40" "0"
   And I can move the column "text_1" to column "text_2" by offset "-20" "0"
  
Scenario: I can rename a form and then create new form
  Given I have a form open
   When I enter "new-form" in "Id" in "Form Settings"
    and I can see "new-form" is open
    and I enter "new-form-1" in "Id" in "Form Settings"
    and I can see "new-form-1" is open
    and I add a form by click
   Then I can see "new-form" is open

Scenario: I can rename a form and then create new form and then go back and repeat
  Given I have a form open
   When I enter "new-form" in "Id" in "Form Settings"
    and I can see "new-form" is open
    and I enter "new-form-1" in "Id" in "Form Settings"
    and I can see "new-form-1" is open
    and I add a form by click
    and I can see "new-form" is open
    and I open the 'new-form-1' form
    and I enter "new-form" in "Id" in "Form Settings"
    and I add a form by click
   Then I can see "new-form-1" is open

Scenario: I can add a new empty view from '+' button
  #PR 39 - test for code changes for adding new empty view
  Given a new form "frm_employee" is created and some fields are added
   When I add a new empty view from '+' button
   Then I can see that the 'New View' screen is displayed

Scenario: I can edit a row in a datagrid in an unsaved form (PR #47)
  #PR 47 - [fix] Fix the parsing formid in input sent from server that prevent user from editing datagrid row
  Given a logged-in test user
   and I open the ide for "mydb"
   and I create an unsaved datagrid form
   and I create main form with some fields
   and I associate the datagrid to main form
   and I preview the layout in a new tab
   and I add a row to the datagrid form to display the main form "new-form-1"
   and I fill in the fields and save the form "new-form-1"
  When I edit the row in the datagrid
   Then the "new-form-1" is rendered
  When I update the contents of "new-form-1" and save the form
   Then I can see that the "new-form" is updated

Scenario: I can create a view of form with all fields (PR 60) from tab (+) button
  #PR 39, 60 [feature] Generate View from form with selected fields
  Given a new form "frm_employee" is created and some fields are added
  When I add a new view with form from '+' button
  Then I can see that the 'Create view of form' dialog is displayed
  And when I fill in the fields with id="mainform_all_view_id", title="mainform_view", form="frm_employee"
  Then I can successfully view all fields in the form with title="mainform_view"

Scenario: I can create a view of form with all fields from the Add Panel
  #PR 39, 60 [feature] Generate View from form with selected fields
  Given a new form "frm_employee" is created and some fields are added
  And when I add a new view with form from the Add panel
  Then I can see that the 'Create view of form' dialog is displayed
  And when I fill in the fields with id="mainform_all_view_id", title="mainform_view", form="frm_employee"
  Then I can successfully view all fields in the form with title="mainform_view"   

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