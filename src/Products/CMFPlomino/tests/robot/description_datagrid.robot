*** Settings *****************************************************************
Resource  description_views.robot
Resource  description_plominodatabase.robot
Resource  description_redirect.robot
Resource  description_dynamic.robot


*** Keywords *****************************************************************

I have a form "a_mainform" with some fields and I associate it to a datagrid form "a_datagridform"
    Given a logged-in test user
    I open the ide for "test_otherforms"
    I select "a_datagridform" from form tree

I preview the datagrid form "${formid}"
    I preview the dynamic form "${formid}"