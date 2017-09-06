*** Settings *****************************************************************
Resource  description_plominodatabase.robot
Resource  description_views.robot

Test Setup   Test Setup
Test Teardown   Test Tear Down

*** Test Cases ***************************************************************


Scenario: I can add a view
  Given I have a form and some data saved
   When I create a view
   Then I can see a view editor listing my data

Scenario: I can add a column to a view
  Given I have a form and some data saved
    and I create a view
    and I can see a view editor listing my data
    When I add a column "text"
    Then I will see column "text" in the view
    and I click on Add tab
    and I add a column "text_1"
    Then I will see column "text_1" in the view

Scenario: I can add an action to a view
  Given I have a form and some data saved
   and I create a view
   and I can see a view editor listing my data
   When I add an action "my action"
   Then I will see action "my-action" in the view

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

Scenario: I can reoder the columns in the view
  #This tests for PR27
  Given a logged-in test user
   and I open the ide for "mydb"
   and I select "frm_test" from form tree
   and I create view
   When I add a column "text"
   and I click on Add tab
   and I add a column "text_1"
   and I click on Add tab
   and I add a column "text2"
   Then I can move column "text" to column "text_1"
   And I can move column "text_2" to column "text"
   And I can move column "text_1" to column "text"
   And I can move column "text_1" to column "text_2"
