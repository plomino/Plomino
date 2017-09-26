from selenium import webdriver
import os

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

class DragDrop(object):
    def __init__(self):
        pass

    def drag_drop(self, src, target):
        # load jQuery helper
        jquery_helper = os.path.join(THIS_FOLDER, 'jquery_load_helper.js')
        with open(jquery_helper) as f:
            load_jquery_js = f.read()

        # load drag and drop helper
        dragdrop_helper = os.path.join(THIS_FOLDER, 'drag_and_drop_helper.js')
        with open(dragdrop_helper) as f:
            drag_and_drop_js = f.read()

        # load jQuery
        webdriver.execute_script(load_jquery_js, jquery_url)

        # perform drag&drop
        webdriver.execute_script(drag_and_drop_js + "$('src').simulateDragDrop({ dropTarget: 'target'});")