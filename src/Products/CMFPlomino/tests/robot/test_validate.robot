


# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s Products.CMFPlomino -t test_plominodatabase.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src Products.CMFPlomino.testing.PRODUCTS_CMFPLOMINO_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot src/Products/CMFPlomino/tests/robot/test_plominodatabase.robot
#
# See the http://docs.plone.org for further details (search for robot
# framework).
#
# ============================================================================



*** Settings *****************************************************************

Resource  description_plominodatabase.robot

Test Setup   Test Setup
Test Teardown  Test Tear Down

*** Test Cases ***************************************************************


Scenario: I can add a validation rule to a field
  Given I have a form open
   When I add a "Text" field
    and I can see the item with the id "text" in the preview
    and I select the field "text"
    # "Field contains text" macro is no longer in the options, changed to "Match text" instead
    and I add a macro "Match text" to "Field Settings"
    and I select current field
    and I enter "blah" in "Field value" in the form
    and I select Text as value type
    and I save the macro and the form
    and I add a macro "Invalid" to "Field Settings"
    and I enter "You can't say blah" in "Invalid message" in the form
    and I save the macro and the form
    and I save the fieldsettings
    and I preview "frm_test"
    and I input the text "blah" inside the field with id "text"
    and I submit the form
    Then I will see the validation error "You can't say blah"
