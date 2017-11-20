*** Settings *****************************************************************
Resource  description_plominodatabase.robot
Resource  description_views.robot
Resource  description_redirect.robot
Resource  description_dynamic.robot

Test Setup   Test Setup
Test Teardown  Test Tear Down

*** Test Cases ***************************************************************

Scenario: I can add a dynamic calculated field (field mode = Computed) that displays the total amount of two number fields
    Given I have a form with some number fields and field mode = Computed
    And I preview the dynamic form "a_src_dyna_comp"
    When I input a value "1000" on the Library Fee field and move to the next field
    Then I can see that the Total Amount value is updated with "1000"
    And when I input a value "500" on the Misc Fee and move to the next field
    Then I can see that the Total Amount value is updated with "1500"

Scenario: I can add a dynamic calculated field (field mode = Display) that displays the total amount of two number fields
    Given I have a form with some number fields and field mode = Display
    And I preview the dynamic form "a_src_dyna_disp"
    When I input a value "1000" on the Library Fee field and move to the next field
    Then I can see that the Total Amount value is updated with "1000"
    And when I input a value "500" on the Misc Fee and move to the next field
    Then I can see that the Total Amount value is updated with "1500"

Scenario: I can add a dynamic calculated field (field mode = Computed On Save) that displays the total amount of two number fields
    Given I have a form with some number fields and field mode = Computed On Save
    And I preview the dynamic form "a_src_dyna_compsave"
    When I input a value "1000" on the Library Fee field and move to the next field
    Then I can see that the Total Amount value is updated with "1000"
    And when I input a value "500" on the Misc Fee and move to the next field
    Then I can see that the Total Amount value is updated with "1500"

Scenario: I can add a dynamic text computed for display
  #PR 71
  Given I have an empty form open
   and I add a dynamic text with field mode = computed for display
   and I show the code of the current field
   and I insert formula that displays text
  When I render the form "new-form"
  Then I can see the text created for the dynamic text field

Scenario: I can add a dynamic hidewhen on text field
  Given I have an empty form open
  When I add a dynamic hidewhen by click
  Then I can add a text field in the hidewhen

Scenario: I can add a dynamic hidewhen for dropdown field
  Given I have an empty form open
  When I add a dynamic hidewhen by click
  Then I can add a dropdown field in the hidewhen

Scenario: I can add a dynamic hidewhen for radio buttons
  Given I have an empty form open
  When I add a dynamic hidewhen by click
  Then I can add radio buttons in the hidewhen

Scenario: I can add a dynamic hidewhen for multi-selection field
  Given I have an empty form open
  When I add a dynamic hidewhen by click
  Then I can add a multi-selection field in the hidewhen

Scenario: I can add a dynamic hidewhen for checkboxes
  Given I have an empty form open
  When I add a dynamic hidewhen by click
  Then I can add checkboxes in the hidewhen

Scenario: I can add a dynamic hidewhen for datagrid
  Given I have an empty form open
  When I add a dynamic hidewhen by click
  Then I can add datagrid in the hidewhen

Scenario: I can add two dynamic hidewhen fields
  Given I have an empty form open
  When I add a dynamic hidewhen by click
  Then I can add a text field in the hidewhen
  And when I add another dynamic hidewhen by click
  Then I can add a text field in the second hidewhen