*** Settings *****************************************************************

Resource  description_plominodatabase.robot
Resource  description_views.robot

Test Setup   Test Setup
Test Teardown  Test Tear Down

*** Test Cases ***************************************************************

#View tests - Work In Progress

Scenario: I can add a view
  Given I have a form and some data saved
   When I create a view
   # Then I can see "new-view" is open
    Then I can see a view editor listing my data

Scenario: I can add a column to a view
  Given I have a form and some data saved
   When I create a view
    Then I can see a view editor listing my data
   When I add a column "text"
    Then I will see column "text" in the view
   When I add a column "text_1"
    Then I will see column "text_1" in the view

# Scenario: I can add an action to a view
#   Given I have a form and some data saved
#    When I create a view
#     # and I can see "new-view" is open
#     and sleep  1s
#     and I can see a view editor listing my data
#     and I add an action "my action"
#    Then I will see action "my-action" in the view

# Scenario: I can rename a form and then create new form
#   Given I have a form open
#    When I enter "new-form" in "Id" in "Form Settings"
#     and I can see "new-form" is open
#     and I enter "new-form-1" in "Id" in "Form Settings"
#     and I can see "new-form-1" is open
#     and I add a form by click
#    Then I can see "new-form" is open

# Scenario: I can rename a form and then create new form and then go back and repeat
#   Given I have a form open
#    When I enter "new-form" in "Id" in "Form Settings"
#     and I can see "new-form" is open
#     and I enter "new-form-1" in "Id" in "Form Settings"
#     and I can see "new-form-1" is open
#     and I add a form by click
#     and I can see "new-form" is open
#     and I open a form "new-form-1"
#     and I enter "new-form" in "Id" in "Form Settings"
#     and I add a form by click
#    Then I can see "new-form-1" is open

# Scenario: I can add filter a view  ============This one is really disabled scenario
#  Given I have a form and some data saved
#   When I create a view
#    and I see > 2 documents in the view
#    and I add a macro the the "view settings" called "number range"
#    and I set the range to <5
#   Then I will see less than 2 documents in the view


