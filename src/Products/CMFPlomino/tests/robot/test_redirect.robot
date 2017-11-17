*** Settings *****************************************************************
Resource  description_plominodatabase.robot
Resource  description_views.robot
Resource  description_redirect.robot

Test Setup   Test Setup
Test Teardown  Test Tear Down

*** Test Cases ***************************************************************

Scenario: When I have a field in source form with request=post I can see that the value will display on target form with request=post
#From use case: have any fields in source form with in POST request, the value will display on target form in POST request
  Given I have a source form "a_src_post" with POST request and a target form "a_target_post" with POST request
  When I preview the form "a_src_post"
  And I fill in the "name" field and save the source form
  Then I can see that the value entered on the source form is displayed on the "name" field of the target form

Scenario: I can do redirect in form on save (Form Redirect)
#This will display the value of name field on source form to the target form
  Given I have a source form "a_src_auto" with AUTO request and a target form "a_target_auto" with AUTO request
  When I preview the form "a_src_auto"
  And I fill in the "name" field and save the source form
  Then I can see that the value entered on the source form is displayed on the "name" field of the target form

Scenario: When I have a field in source form with request=auto I can see that the value will display on target form with request=post
#From use case: have any fields in source form with in AUTO request, the value will display on target form in POST request
  Given I have a source form "a_src_auto" with AUTO request and a target form "a_target_post" with POST request
  When I preview the form "a_src_auto"
  And I fill in the "name" field and save the source form
  Then I can see that the value entered on the source form is displayed on the "name" field of the target form

Scenario: A message will be displayed when I deselect the "Only Redirect On Save" checkbox
#From use case: add check box, only redirect on save, and warning message... if you use a page form, you need to uncheck this, with condition
  Given I have source and target forms
  When I deselect the "Only Redirect On Save" checkbox
  Then I will see a confirmation message

Scenario: When I have a field in source form with request=post I can see that the value will display on target form with request=auto
#From use case: have any fields in source form with in POST request, the value will display on target form in AUTO request
  Given I have a source form "a_src_post" with POST request and a target form "a_target_auto" with AUTO request
  When I preview the form "a_src_post"
  And I fill in the "name" field and save the source form
  Then I can see that the value entered on the source form is displayed on the "name" field of the target form

Scenario: I can see that the data is retained for multi-page target form
#From use case: have edit field on source form, the value will display in display field on target form (go to next page and back to the page that have value, make sure the value is there)
  Given I have a single-page source form "a_src_auto" and a multi-page target form "a_target_auto_multi"
  When I preview the form "a_src_auto"
  And I fill in the "name" field and save the source form
  Then I can see that the value entered on the source form is displayed on the "name" field of the target form
  And when I go to the next page and go back to previous page of the target form
  Then I can see that the value entered is still displayed on the first page of the target form