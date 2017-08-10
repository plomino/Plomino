

*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in test user
  Enable autologin as  Manager  ##TODO real test user





# --- WHEN -------------------------------------------------------------------
I open service tab "${tabId}"
  Click Link    Service
  wait until page contains  ${tabId}
  Click Element  jquery=.mdl-button:visible:contains(${tabId})


# --- THEN -------------------------------------------------------------------
I can see the workflow editor
    Element Should Be Visible       id=tab_workflow

I can see element Start in the workflow editor
    Wait Until Page Contains Element    jquery=.plomino-workflow-editor
    Wait Until Page Contains Element    jquery=.plomino-workflow-editor__branch
    Element Should Be Visible       jquery=.workflow-node--root .workflow-node__start-text

I can add a Form Task element by dnd
    Click Element        jquery=.workflow-node--root .workflow-node__start-text
    Click Element       id=wf-vrt-btn-1
    Click Element        jquery=li[data-create='workflowFormTask']
    Wait Until Page Contains Element        id=workflow-node__text--task-2
    Wait Until Page Contains Element        id=workflow-node__text--form-2
    Wait Until Page Contains Element        id=workflow-node__text--process-2