#!/usr/bin/python
#A collection of wrappers around dogtail.tree to enable object-oriented
#widget locators and widget lookup in GTK user interfaces
#
#Author: Steve Salevan <ssalevan@redhat.com>

import dogtail
import logging

from dogtail import tree
from dogtail import rawinput
from dogtail import procedural

from dogtail.tree import SearchError

APP_NAME = "Firefox"

log = logging.getLogger("dalek.gtkhandler")

class Widget:
    """
    Abstract base class representing a UI element, providing numerous
    methods to enable abstractification of UI locator strategies
    """
    
    widget_name = ""
    widget_role = ""
    description = ""
    label       = ""
    parent      = None
    
    def __init__(self):
        pass
        
    def get_app_node(self):
        """
        Returns a node corresponding to the application currently
        being tested
        """
        return tree.root.application(APP_NAME)
    
    def get_parent(self):
        """
        Provides a dogtail.tree instance corresponding
        to the UI element's parent widget
        """
        if not self.parent:
            parent = self.get_app_node()
        else:
            parent = eval(self.parent)().get_instance() 
        return parent
       
    def get_instance(self):
        """
        Provides a dogtail.tree instance corresponding
        to the UI element locator if one currently exists
        """
        return self.get_parent().child(name=self.widget_name,
            roleName=self.widget_role,
            description=self.description,
            label=self.label)
            
    def get_all_instances(self):
        """
        Provides all dogtail.tree instances corresponding
        to the UI element locator if one currently exists
        """
        return self.get_parent().findChildren(
            GenericPredicate(name=self.widget_name,
                roleName=self.widget_role,
                description=self.description,
                label=self.label))
                
    def get_all_children(self, recursive=True):
        """
        Provides all dogtail.tree instances corresponding
        to the child nodes beneath this Widget
        """
        return self.get_instance().findChildren(GenericPredicate(),
            recursive=recursive)
    
    def focus(self):
        """
        Focuses on widget if widget exists
        """
        log.info("Focusing on %s: %s" % 
            (self.widget_role,  self.widget_name))
        return self.get_instance().grabFocus()
    
    def is_showing(self):
        log.debug("%s: Checking if widget is showing: %s" % 
            (self.__class__.__name__,self.widget_name))
        try:
            instance = self.get_instance()
            log.debug("Widget '%s' showing? %s" %
                (self.widget_name, instance.showing))
            return instance.showing
        except SearchError:
            log.debug("Widget '%s' not found" %
                self.widget_name)
            return False
        
    def is_focused(self):
        log.debug("%s: Checking if widget is focused: %s" % 
            (self.__class__.__name__,self.widget_name))
        try:
            instance = self.get_instance()
            log.debug("Widget '%s' focused? %s" %
                (self.widget_name, instance.focused))
            return instance.focused
        except SearchError:
            log.debug("Widget '%s' not found" %
                self.widget_name)
            return False
            
class Clickable(Widget):
    """
    Abstract class representing a clickable Widget object
    """
    def __init__(self, name, roleName, parent=None):
        self.widget_name = name
        self.widget_role = roleName
        self.parent = parent
        
    def click(self, button=1):
        log.info("Clicking %s: %s" %
            (self.widget_role, self.widget_name))
        clickable = self.get_instance()
        clickable.blink()
        clickable.click(button=button)
            
    def doubleClick(self, button=1):
        log.info("Double-clicking %s: %s" %
            (self.widget_role, self.widget_name))
        clickable = self.get_instance()
        clickable.blink()
        clickable.blink()
        clickable.doubleClick(button=button)
        
class TextField(Clickable):
    """
    Represents a UI text field
    """
    def __init__(self, roleName, position=0, parent=None):
        self.widget_role = roleName
        self.position = position
        self.parent = parent
    
    def enter_text(self, text):
        """
        Enters text into the text field specified by this
        object
        """
        log.info("Entering '%s' into %s field..." % 
            (text, self.widget_role))
        fields = self.get_all_instances()
        tf = fields[self.position]
        tf.blink()
        tf.text = text
        
    def get_text(self):
        """
        Retrieves text from text field
        """
        log.info("Retrieving text from '%s' field..." % 
            self.widget_role)
        fields = self.get_all_instances()
        tf = fields[self.position]
        tf.blink()
        log.debug("Text:\n%s" % tf.text)
        return tf.text
        
class Button(Clickable):
    """
    Represents a UI button
    """
    def __init__(self, name, parent=None):
        self.widget_name = name
        self.widget_role = "push button"
        self.parent = parent
        
class PasswordWindow(Widget):
    """
    Represents main subscription-manager-gui window
    """
    widget_name = "Authentication Required"
    widget_role = "dialog"
    
    username_field = TextField("entry", parent="PasswordWindow")
    password_field = TextField("password text", parent="PasswordWindow")
    
    cancel_button = Button("Cancel", parent="PasswordWindow")
    ok_button = Button("OK", parent="PasswordWindow")
