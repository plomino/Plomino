*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/saucelabs.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote


*** Variables ****************************************************************

${BROWSER}  Chrome

*** Keywords *****************************************************************
Get item or parent group top position
  [Arguments]    ${item_id}

  ${item_xpath}=  Convert to string  body[@id="tinymce"]//*[@data-plominoid="${item_id}"]
  ${item_group_xpath}=  Convert to string  ${item_xpath}/ancestor::*[@data-groupid="${item_id}"]
  ${item_group_count}=  Get Element Count  xpath=//item_group_xpath

  ${item_position}=  Get Vertical Position  xpath=//${item_xpath}
  Run keyword if  ${item_group_count} > 0  ${item_position}=  Get Vertical Position  xpath=//item_group_xpath

  Return from keyword  ${item_position}


Get item or parent group size
  [Arguments]    ${item_id}

  ${item_xpath}=  Convert to string  body[@id="tinymce"]//*[@data-plominoid="${item_id}"]
  ${item_group_xpath}=  Convert to string  ${item_xpath}/ancestor::*[@data-groupid="${item_id}"]
  ${item_group_count}=  Get Element Count  xpath=//item_group_xpath

  ${item_width}  ${item_height}=  Get Element Size  xpath=//${item_xpath}
  Run keyword if  ${item_group_count} > 0  ${item_width}  ${item_height}=  Get Element Size  xpath=//${item_group_xpath}

  Return from keyword  ${item_width}  ${item_height}
