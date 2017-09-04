*** Settings *****************************************************************
Resource  description_plominodatabase.robot
Resource  description_views.robot

Test Setup   Setup For View
Test Teardown   Test Tear Down

*** Test Cases ***************************************************************


# Scenario: I can add a view
#   Given I open the ide for "mydb"
#    and I select "frm_empdata" from form tree
#    When I create a view
#    Then I can see a view editor listing my data

Scenario: I can add a view and columns to a view
   #This will also test for PR 27 fix
  Given I open the ide for "mydb"
   And I select "frm_empdata" from form tree
   And I create a view
   When I add a column "name" with title "Name" and field value "frm_empdata/name"
   Then I will see column header "Name" and data "John Doe", "Mary Light", "John Snow"
   And When I click on Add tab
   And I add a column "address" with title "Address" and field value "frm_empdata/address"
   Then I will see column header "Address" and data "123 Main St", "123 Chicago St", "123 GOT Avenue"
   And When I click on Add tab
   And I add a column "contactno" with title "Contact No" and field value "frm_empdata/contactno"
   Then I will see column header "Address" and data "1234567890", "0987654321", "12389098543"

#   Given a logged-in test user
#    and I open the ide for "mydb"
#    Capture Page Screenshot
#    and I open a form "employeedata"

# Scenario: I can add action to a view


# Scenario: I can see the contents of "frmEmployeeData" in the view




# Scenario: I can add a view
#   Given I have a form and some fields saved
#    When I create a view
#    Then I can see a view editor listing my data




# Scenario: I can add a column to a view
#   Given I have a form and some data saved
#     and I create a view
#     and I can see a view editor listing my data
#     When I add a column "text"
#     Then I will see column "text" in the view
#     and when I add a column "text_1"
#     Then I will see column "text_1" in the view

# Scenario: I can add an action to a view
#   Given I have a form and some data saved
#    and I create a view
#    and I can see a view editor listing my data
#    When I add an action "my action"
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

# # Scenario: I can add filter to a view   # Work in progress
# #   Given I have a form and some data saved
# #    When I create a view
# #     and I see > 2 documents in the view
# #     and I add a macro the the "view settings" called "number range"
# #     and I set the range to <5
# #    Then I will see less than 2 documents in the view



