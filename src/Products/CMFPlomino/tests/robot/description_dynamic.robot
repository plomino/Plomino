*** Settings *****************************************************************
Resource  description_views.robot
Resource  description_plominodatabase.robot
Resource  description_redirect.robot


*** Keywords *****************************************************************

I have a form with some number fields and field mode = Computed
    Given a logged-in test user
    I open the ide for "test_otherforms"
    I select "a_src_dyna_comp" from form tree
    I open the field 'total'
    I add a macro that displays the total of two numbers
    I save the macro and the form

I open the field 'total'
    Wait Until Element Is Visible       jquery=span:contains('total'):eq(0)     60s
    Click Element       jquery=span:contains('total'):eq(0)
    Wait Until Element Is Visible       jquery=#form-widgets-IShortName-id      60

I add a macro that displays the total of two numbers
    Add macro "Display total"
    I fill in the fields name for Display Total screen with "amount1"
    I fill in the fields name for Display Total screen with "amount2"

I preview the dynamic form "${formid}"
    Click Link  Form Settings
    wait until page contains element  jquery=.mdl-button:visible:contains("Preview")
    wait until page does not contain element  jquery=.plomino-block-preloader:visible
    wait until page does not contain element  jquery=.plomino-block-preloader:visible
    Click Element  jquery=.mdl-button:visible:contains("Preview")
    Sleep  2s
    select window  url=${PLONE_URL}/test_otherforms/${formid}/view

I have a form with some number fields and field mode = Display
    Given a logged-in test user
    I open the ide for "test_otherforms"
    I select "a_src_dyna_disp" from form tree
    I select the field "total"
    Wait Until Element Is Visible       jquery=#form-widgets-IShortName-id      60
    I add a macro that displays the total of two numbers
    I save the macro and the form

I have a form with some number fields and field mode = Computed On Save
    Given a logged-in test user
    I open the ide for "test_otherforms"
    I select "a_src_dyna_compsave" from form tree
    I select the field "total"
    Wait Until Element Is Visible       jquery=#form-widgets-IShortName-id      60
    I add a macro that displays the total of two numbers
    I save the macro and the form