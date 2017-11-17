*** Settings *****************************************************************
Resource  description_views.robot
Resource  description_plominodatabase.robot


*** Keywords *****************************************************************

I have a source form "${source}" with POST request and a target form "${target}" with POST request
    Given a logged-in test user
    I open the ide for "test_redirect"
    I select "${source}" from form tree
    Click Link  Form Settings

    Execute Javascript    window.document.getElementById("form-widgets-isPage").scrollIntoView(true);

    Wait Until Element Is Visible     css=.plomino-macros-rule .select2-container input
    Click element  css=.plomino-macros-rule .select2-container input
    Capture Page Screenshot

    Click element  xpath=//*[contains(@class,"select2-result")][normalize-space(text())="Redirect in form on save"]
    wait until page contains element  css=.plominoSave    60s
    Capture Page Screenshot

    I select the redirect type=Form
    I select the target form "${target}"
    I select retain form data in target form
    I save the macro
    I save the current layout

I select the redirect type=Form
  Wait Until Page Contains Element    jquery=.plone-modal-title:contains('Redirect in form on save')    60s
  Wait Until Element Is Visible       jquery=.plone-modal-title:contains('Redirect in form on save')    60s
  Click Element   jquery=#redirect_type-form

  Wait Until Element Is Visible     jquery=#s2id_form_redirect    60s

I select the target form "${target}"
  Click Element     jquery=#s2id_form_redirect
  Capture Page Screenshot
  Wait Until Element Is Visible     jquery=.pat-select2 option[value='${target}']    60s
  Capture Page Screenshot
  Click Element     jquery=.pat-select2 option[value='${target}']
  Capture Page Screenshot
  Sleep   3s

I have a source form "${source}" with AUTO request and a target form "${target}" with AUTO request
    Given a logged-in test user
    I open the ide for "test_redirect"
    I select "${source}" from form tree
    Click Link  Form Settings

    Execute Javascript    window.document.getElementById("form-widgets-isPage").scrollIntoView(true);

    Wait Until Element Is Visible     css=.plomino-macros-rule .select2-container input
    Click element  css=.plomino-macros-rule .select2-container input
    Capture Page Screenshot

    Click element  xpath=//*[contains(@class,"select2-result")][normalize-space(text())="Redirect in form on save"]
    wait until page contains element  css=.plominoSave    60s
    Capture Page Screenshot

    I select the redirect type=Form
    I select the target form "${target}"
    I select retain form data in target form
    I save the macro
    I save the current layout

I have a source form "${source}" with AUTO request and a target form "${target}" with POST request
    Given a logged-in test user
    I open the ide for "test_redirect"
    I select "${source}" from form tree
    Click Link  Form Settings

    Execute Javascript    window.document.getElementById("form-widgets-isPage").scrollIntoView(true);

    Wait Until Element Is Visible     css=.plomino-macros-rule .select2-container input
    Click element  css=.plomino-macros-rule .select2-container input
    Capture Page Screenshot

    Click element  xpath=//*[contains(@class,"select2-result")][normalize-space(text())="Redirect in form on save"]
    wait until page contains element  css=.plominoSave    60s
    Capture Page Screenshot

    I select the redirect type=Form
    I select the target form "${target}"
    I select retain form data in target form
    I save the macro
    I save the current layout

I have a source form "${source}" with POST request and a target form "${target}" with AUTO request
    Given a logged-in test user
    I open the ide for "test_redirect"
    I select "${source}" from form tree
    Click Link  Form Settings

    Execute Javascript    window.document.getElementById("form-widgets-isPage").scrollIntoView(true);

    Wait Until Element Is Visible     css=.plomino-macros-rule .select2-container input
    Click element  css=.plomino-macros-rule .select2-container input
    Capture Page Screenshot

    Click element  xpath=//*[contains(@class,"select2-result")][normalize-space(text())="Redirect in form on save"]
    wait until page contains element  css=.plominoSave    60s
    Capture Page Screenshot

    I select the redirect type=Form
    I select the target form "${target}"
    I select retain form data in target form
    I save the macro
    I save the current layout

I have a single-page source form "${source}" and a multi-page target form "${target}"
    Given a logged-in test user
    I open the ide for "test_redirect"
    I select "${source}" from form tree
    Click Link  Form Settings

    Execute Javascript    window.document.getElementById("form-widgets-isPage").scrollIntoView(true);

    Wait Until Element Is Visible     css=.plomino-macros-rule .select2-container input
    Click element  css=.plomino-macros-rule .select2-container input
    Capture Page Screenshot

    Click element  xpath=//*[contains(@class,"select2-result")][normalize-space(text())="Redirect in form on save"]
    wait until page contains element  css=.plominoSave    60s
    Capture Page Screenshot

    I select the redirect type=Form
    I select the target form "${target}"
    I select retain form data in target form
    I save the macro
    I save the current layout

I go to the next page
    Wait Until Element Is Visible       jquery=input[name='next']       60s
    Click Element       jquery=input[name='next']
    Wait Until Element Is Visible       jquery=input[name='plomino_save']       60s

I go back to the previous page
    Wait Until Element Is Visible       jquery=input[name='previous']       60s
    Click Element       jquery=input[name='previous']
    Wait Until Element Is Visible       jquery=input[name='plomino_save']       60s

I can see that the value entered is still displayed on the first page of the target form
    I can see that the value entered on the source form is displayed on the "name" field of the target form

I go to the next page and go back to previous page of the target form
    I go to the next page
    I go back to the previous page