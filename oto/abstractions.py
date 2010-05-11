#!/usr/bin/python
#UI abstractions related to Oto project
#
#Author: Steve Salevan <ssalevan@redhat.com>

import pdb

class Element(object):
    locator = None
    humanReadable = None
    strategy = None

    def __init__(self, *args, **kwargs):
        if "locator" in kwargs:
            self.locator = kwargs['locator']
        if "humanReadable" in kwargs:
            self.humanReadable = kwargs['humanReadable']
        if "strategy" in kwargs:
            self.strategy = kwargs['strategy']
        self.args = args
        
    def __str__(self):
        if len(self.get_human_readable()) > 0:
            return "locator: %s (%s)" % (self.get_locator(), self.get_human_readable())
        return "locator: %s" % self.get_locator()
        
    def get_locator(self):
        if self.strategy is not None:
            return self.strategy.get_locator(self.args)
        return self.locator
        
    def get_human_readable(self):
        if self.strategy is not None:
            return self.strategy.get_human_readable(self.args)
        return self.humanReadable

class LocatorStrategy(object):
    def get_human_readable(self):
        raise NotImplementedError
        
    def get_locator(self, *args):
        raise NotImplementedError
        
    def get_template(self):
        raise NotImplementedError
        
    def get_human_readable(self, *args):
        raise NotImplementedError

class LocatorTemplate(LocatorStrategy):
    def __init__(self, name, template):
        self.humanReadable = name
        self.template = template
        
    def get_locator(self, args):
        repl_dict = dict()
        for i in xrange(0, len(args)):
            repl_dict[str(i)] = args[i]
        return self.template % repl_dict
        
    def get_template(self):
        return self.template
        
    def get_human_readable(self, args):
        repl_dict = dict()
        for i in xrange(0, len(args)):
            repl_dict[str(i)] = args[i]
        return self.humanReadable % repl_dict
        
class Strategies(object):
    #basic page constructs
    id = LocatorTemplate("element with id=%(0)s", 
        "//*[normalize-space(@id)='%(0)s']")
    link = LocatorTemplate("link=%(0)s", 
        "link=%(0)s")
    alt = LocatorTemplate("alt=$(0)s",
        "//*[normalize-space(@alt)='$(0)s']")
    name = LocatorTemplate("name=%(0)s", 
        "//*[normalize-space(@name)='%(0)s']")
    title = LocatorTemplate("title=%(0)s", 
        "//*[normalize-space(@title)='%(0)s']")
    css_class = LocatorTemplate("class=%(0)s",
        "//*[normalize-space(@class)='%(0)s']")
    button = LocatorTemplate("button=%(0)s", 
        "//*[@value='%(0)s']")
        
    row_with_two_elements = LocatorTemplate("table row containing '%(0)s' and '%(1)s'",
        "//*[self::tr]/*[self::td and (normalize-space(.)='%(0)s' or normalize-space(.)='%(0)s *' or contains(.,'%(0)s'))]/../*[self::td and (normalize-space(.)='%(1)s' or normalize-space(.)='%(1)s *' or contains(.,'%(1)s'))]/..")
    
    #wiki table constructs
    table_cell = LocatorTemplate("table cell with text=%(0)s",
        "//*[self::tr]/*[self::td and (normalize-space(.)='%(0)s' or normalize-space(.)='%(0)s *' or contains(.,'%(0)s'))]")
    table_edit_button = LocatorTemplate("edit button for table containing cell with text=%(0)s",
        "//*[self::tr]/*[self::td and (normalize-space(.)='%(0)s' or normalize-space(.)='%(0)s *' or contains(.,'%(0)s'))]/../../../../*[self::input and normalize-space(@class)='editTableEditImageButton']")
    table_row_delete_button = LocatorTemplate("delete button for table row containing text=%(0)s",
        "//*[self::input and normalize-space(@value)='%(0)s']/../../*[self::td and normalize-space(@class)='editTableActionCell'][2]/*[self::img]")
    table_save_button = LocatorTemplate("save button for table containing table row containing text=%(0)s",
        "//*[self::input and normalize-space(@value)='%(0)s']/../../../../../*[self::input and normalize-space(@id)='etsave']")
    checkbox_next_to_text = LocatorTemplate("checkbox next to text=%(0)s",
        "//*[(self::td or contains(@class,'dr-table-cell')) and normalize-space(.)='%(0)s']/..//*[@type='checkbox']")
        
class Elements(object):
    bookmarked_element = Element("otoBookmark", strategy=Strategies.id)
    
    ok_button = Element("OK", strategy=Strategies.button)
    cancel_button = Element("Cancel", strategy=Strategies.button)
    submit_button = Element("Submit", strategy=Strategies.button)
