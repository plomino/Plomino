*** Settings *****************************************************************
Resource  description_views.robot


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

# --- WHEN -------------------------------------------------------------------
I open service tab "${tabId}"
    Click Link    Service
    wait until page contains  ${tabId}
    Click Element  jquery=.mdl-button:visible:contains(${tabId})

I open workflow tab
    Click Element   jquery=#tab_workflow
    Wait Until Element Is Visible       jquery=.workflow-node__start-text        60s

I add a view task from the Add Panel
    I click on Add tab
    I click on View Task from the Add Panel

I click on View Task from the Add Panel
    Wait Until Element Is Visible       jquery=#workflowViewTask
    Click Element   jquery=#workflowViewTask
    Wait Until Element Is Visible       jquery=#workflow-node__text--task-2
    Wait Until Element Is Visible       jquery=#workflow-node__text--view-2
    Wait Until Element Is Visible       jquery=#workflow-node__text--process-2

I click on View task
    Click Element       jquery=.workflow-node__text--view a[class='workflow-node__text-modal-link']
    Wait Until Element Is Visible       jquery=.modal-title[data-typefor='workflowViewTask']

I create new view from form
    I create a view task

I create a view task
    Wait Until Element Is Visible       jquery=#wf-item-settings-dialog__title
    Wait Until Element Is Visible       jquery=#wf-item-settings-dialog__notes
    Wait Until Element Is Visible       jquery=#wf-item-settings-dialog__view
    Wait Until Element is Visible        jquery=button:contains('Create new view from form')

    Click Element       jquery=#wf-item-settings-dialog__title
    Input Text          jquery=#wf-item-settings-dialog__title          Test Task
    Click Element       jquery=#wf-item-settings-dialog__notes
    Input Text          jquery=#wf-item-settings-dialog__notes      Test Notes

    Click Element       jquery=button:contains('Create new view from form')
    I can see that the 'New View' screen is displayed

I add an All Form View
    Wait Until Element Is Visible       jquery=.mdl-button[id='PlominoView/custom']     60s
    Execute Javascript    $(".mdl-button[id='PlominoView/custom']").click();

I add a Form Task from the Add Panel
    I click on Add tab
    I click on Form Task from the Add Panel

I click on Form Task from the Add Panel
    Click Element       jquery=#workflowFormTask
    Wait Until Element Is Visible       jquery=.workflow-node__text--task
    Wait Until Element Is Visible       jquery=.workflow-node__text--form
    Wait Until Element Is Visible       jquery=.workflow-node__text--process

I click on the Form task
    Click Element       jquery=.workflow-node__text a[class='workflow-node__text-modal-link']
    Wait Until Element Is Visible       jquery=.modal-title[data-typefor='workflowFormTask']        60s



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
    Mouse Over              jquery=.workflow-node__start-text
#    Sleep       1s
    Wait Until Element Is Visible       jquery=#wf-vrt-btn-1     1s
# I think this mouse over might be what is making this test unstable. lets remove it for now
    Mouse Over       jquery=#wf-vrt-btn-1
    Click Element       jquery=#wf-vrt-btn-1
    Sleep       1s
#    Mouse Over       jquery=#wf-vrt-btn-1
    Mouse Over       jquery=.mdl-menu__container
    Wait Until Element Is Visible       jquery=.mdl-menu__container .mdl-menu li:contains('Form task')      2s
    Click Element       jquery=.mdl-menu__container .mdl-menu li:contains('Form task')
    Element Should Be Visible       jquery=.workflow-node__text--task[id='workflow-node__text--task-2']
    Element Should Be Visible       jquery=.workflow-node__text--form[id='workflow-node__text--form-2']
    Element Should Be Visible       jquery=.workflow-node__text--process[id='workflow-node__text--process-2']

