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

Scenario: I can add a column to a view
  Given I have a form and some fields saved
   and I create a view
   and I can see a view editor listing my data
   When I add a column "text" with retries
   Then I will see column "text" in the view
   and I click on Add tab
   When I add a column "text_1" with retries
   Then I will see column "text_1" in the view
   and I click on Add tab
   When I add a column "text_2" with retries
   Then I will see column "text_2" in the view


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
   Then I can move column "text" to column "text_1" by offset "20" "0"
   And I can move column "text_2" to column "text" by offset "-20" "0"
   And I can move column "text_1" to column "text" by offset "40" "0"
   And I can move column "text_1" to column "text_2" by offset "-20" "0"
  
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
    and I open a form "new-form-1"
    and I enter "new-form" in "Id" in "Form Settings"
    and I add a form by click
   Then I can see "new-form-1" is open

Scenario: I can create a view of form (PR 39)
  #PR 39 [feature] Generate View from form with selected fields
  Given a new form "frm_employee" is created and some fields are added
   When I add a new view with form
   Then I can see that the 'Create view of form' dialog is displayed

Scenario: I can add a new empty view from '+' button
  #PR 39 - test for code changes for adding new empty view
  Given a new form "frm_employee" is created and some fields are added
   When I add a new empty view from '+' button
   Then I can see that the 'New View' screen is displayed