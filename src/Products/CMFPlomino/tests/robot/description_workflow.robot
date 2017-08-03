

*** Keywords *****************************************************************

Plone Test Teardown
    Run Keyword If Test Failed  ${SELENIUM_RUN_ON_FAILURE}
    Report test status
    Close all browsers


# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

a logged-in test user
  Enable autologin as  Manager  ##TODO real test user



I open the ide for "${db}"
  #Go To  ${PLONE_URL}/mydb
  #Click Element  link=IDE
  Go To  ${PLONE_URL}/${db}/++resource++Products.CMFPlomino/ide/index.html
#  Wait Until Element Is Visible  id=application-loader
  Wait Until page does not contain element  id=application-loader
  wait until page contains  ${db}


I waiting a little bit
  sleep  0.5s



# --- WHEN -------------------------------------------------------------------


I open service tab "${tabId}"
  Click Link    Service
  wait until page contains  ${tabId}
  Click Element  jquery=.mdl-button:visible:contains(${tabId})

I

# --- THEN -------------------------------------------------------------------



I can see element Start in the workflow editor
  wait until page contains element  css=.workflow-node--root

I can add a Form Task element
  sleep  0.3s
  wait until page does not contain element  jquery=.plomino-block-preloader:visible
  wait until page contains element  css=div.workflow-node--root
  Selenium2Library.mouse over css=div.workflow-node--root
  sleep  0.1s
  wait until element is visible   xpath=//div[contains(@class,'workflow-node--root')]//li[contains(@class,'plomino-workflow-editor__branch--virtual')]
  Click Element xpath=//div[contains(@class,'workflow-node--root')]//li[contains(@class,'plomino-workflow-editor__branch--virtual')]


python: '<a href="%s/@@display-file/file/%s" class="application-pdf" target="_blank" title="Audit report for %s">%s&nbsp;.<span></span></a>' % (item.getURL(), item['id'], item.Title, 'Audit report') if  item.getObject().file.filename.endswith('pdf') else '<a href="%s/@@download/file/%s" class="application-doc" target="_blank" title="Audit report for %s">%s&nbsp;.<span></span></a>' % (item.getURL(), item['id'], item.Title, 'Audit report')