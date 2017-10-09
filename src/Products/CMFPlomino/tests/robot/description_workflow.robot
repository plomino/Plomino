

*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

# --- WHEN -------------------------------------------------------------------
I open service tab "${tabId}"
  Click Link    Service
  wait until page contains  ${tabId}
  Click Element  jquery=.mdl-button:visible:contains(${tabId})


# --- THEN -------------------------------------------------------------------
I can see the workflow editor
    Element Should Be Visible       jquery=.wrap-app .panel plomino-tabs .mdl-js-tabs .mdl-tabs__tab-bar a
    Element Should Be Visible       jquery=.mdl-button--raised[id='workflowFormTask']
    Element Should Be Visible       jquery=.mdl-button--raised[id='workflowViewTask']
    Element Should Be Visible       jquery=.mdl-button--raised[id='workflowExternalTask']

I can see element Start in the workflow editor
    Wait Until Page Contains Element    jquery=plomino-workflow-editor
    Wait Until Page Contains Element    jquery=.plomino-workflow-editor ul .plomino-workflow-editor__branch     60s

    Element Should Be Visible       jquery=plomino-workflow-editor ul li .workflow-node--root .workflow-node__start-text

I can add a Form Task element by dnd
    Selenium2Library.Drag And Drop      jquery=.mdl-button[draggable='true'][id='workflowFormTask']         jquery=.plomino-workflow-editor ul .plomino-workflow-editor__branch
    Element Should Be Visible       jquery=.workflow-node__text--task[id='workflow-node__text--task-2']
    Element Should Be Visible       jquery=.workflow-node__text--form[id='workflow-node__text--form-2']
    Element Should Be Visible       jquery=.workflow-node__text--process[id='workflow-node__text--process-2']

I can add a Form Task element
    Click Element       jquery=.workflow-node__start-text
    Click Element       jquery=#wf-vrt-btn-1
    Capture Page Screenshot
    Wait Until Element Is Visible       jquery=.mdl-menu__container .mdl-menu li:contains('Form task')      60s
    Capture Page Screenshot
    Click Element       jquery=.mdl-menu__container .mdl-menu li:contains('Form task')
    Capture Page Screenshot
    Element Should Be Visible       jquery=.workflow-node__text--task[id='workflow-node__text--task-2']
    Element Should Be Visible       jquery=.workflow-node__text--form[id='workflow-node__text--form-2']
    Element Should Be Visible       jquery=.workflow-node__text--process[id='workflow-node__text--process-2']
    
