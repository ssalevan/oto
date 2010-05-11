#!/usr/bin/python
#Base class and wrappers around Selenium for Oto project
#
#Author: Steve Salevan <steve.salevan@gmail.com>

import logging
import selenium
import subprocess
import yaml
import time
import smtplib
import dogtail

from email.mime.text import MIMEText

from abstractions import *
from gtk_abstractions import *

CONFIG_LOC       = "./oto.cfg"
DEFAULT_TIMEOUT  = 60000
DEFAULT_BOOKMARK = "otoBookmark"

LOG_FORMAT       = "%(asctime)s|%(levelname)s: %(message)s"
SELENIUM_OPTS    = "-trustAllSSLCertificates -timeout 120 -firefoxProfileTemplate ./firefox-profile"

logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

log = logging.getLogger("oto.base")
sel_process = None

def read_config():
    f = open(CONFIG_LOC, 'r')
    cfg = yaml.load(f)
    f.close()
    return cfg
    
class OtoException(Exception):
    pass

class OtoBase(object):
    base_url = None
    
     def __init__(self):
        #self.cfg = read_config()
        self.sel = None
        self.sel_process = None
        self.decrypt_config_file('dog8code')
        
    def email(self, to_emails, subject, body, bcc=None):
        operator_email = "%s@redhat.com" % self.cfg['oto.username']
        all_to_emails = to_emails
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = operator_email
        msg['To'] = ", ".join(all_to_emails)
        if bcc:
            all_to_emails.append(bcc)
            
        log.info("Sending following e-mail:\n%s" % msg.as_string())
        
        s = smtplib.SMTP()
        s.connect(self.cfg['oto.smtp.server'],
            port=self.cfg['oto.smtp.port'])
        s.sendmail(operator_email, all_to_emails, msg.as_string())
        s.close()
        
        log.info("E-mail sent successfully.")
        return True
    
    def sel_start(self):
        global sel_process
        if(int(self.cfg['oto.startselenium']) == 1 and sel_process == None):
            log.info("Executing selenium-server JAR...")
            sel_process = self.run_command(
                "java -jar ./selenium-server.jar -port %s %s" % (self.cfg['selenium.port'], SELENIUM_OPTS),
                background=True)
            log.info("selenium-server PID: %s" % sel_process.pid)
            self.sleep(15)
    
    def sel_stop(self):
        global sel_process
        if sel_process != None:
            log.info("Sending SIGTERM to selenium-server...")
            sel_process.terminate()
            self.sleep(15)
            sel_process.kill()
            
    def sleep(self, secs):
        log.info("Sleeping for %s seconds..." % secs)
        time.sleep(secs)
     
    def start(self):
        self.get_kerberos_ticket(self.cfg['oto.username'],
            self.cfg['oto.password'])
        self.sel_start()
        log.info("Starting selenium session at http://%s:%s..." %
            (self.cfg['selenium.server'], self.cfg['selenium.port']))
        self.sel = selenium.selenium(
            self.cfg['selenium.server'],
            self.cfg['selenium.port'],
            self.cfg['selenium.browser'],
            self.base_url)
        self.sel.start()
        self.sel.window_focus()
        self.sel.window_maximize()
    
    def stop(self):
        log.info("Stopping selenium session...")
        try:
            self.sel.stop()
        except Exception:
            log.warning("Selenium didn't respond to stop command!")
        
    def go_base(self):
        self.go(self.base_url)
        
    def go(self, url):
        log.info("Opening URL: %s..." % url)
        self.sel.open(url)
        
    def login_via_popup(self, username, password):
        if PasswordWindow().is_showing():
            log.info("Logging in via GTK popup (username '%s')..." % username)
            PasswordWindow().focus()
            PasswordWindow.username_field.click()
            dogtail.rawinput.typeText(username)
            PasswordWindow.password_field.click()
            dogtail.rawinput.typeText(password)
            PasswordWindow.ok_button.click()
            return True
        return False
    
    def click(self, element):
        log.info("Clicking %s..." % str(element))
        self.sel.highlight(element.get_locator())
        self.sel.click(element.get_locator())
        
    def click_wait(self, element):
        log.info("Clicking %s and waiting for page to load..." % element.get_human_readable())
        self.sel.highlight(element.get_locator())
        self.sel.click(element.get_locator())
        self.sel.wait_for_page_to_load(DEFAULT_TIMEOUT)
        
    def get_text(self, element, text):
        log.info("Getting text from %s..." % str(element))
        self.sel.highlight(element.get_locator())
        text = self.sel.get_text(element.get_locator())
        log.info("Text is: %s" % text)
        return text
        
    def check(self, element, checked):
        log.info("Checking box at %s (checked=%s)..." %
            (element.get_human_readable(), checked))
        self.sel.highlight(element.get_locator())
        if checked:
            self.sel.check(element.get_locator())
        else:
            self.sel.uncheck(element.get_locator())
            
    def select(self, element, option_element):
        log.info("Selecting '%s' from select box at %s..." %
            (str(option_element), element.get_human_readable()))
        self.sel.highlight(element.get_locator()) 
        self.sel.select(element.get_locator(),
            option_element.get_locator())
            
    def enter_text(self, element, text):
        log.info("Entering '%s' into field at %s..." %
            (text, element.get_human_readable()))
        self.sel.highlight(element.get_locator())
        self.sel.type(element.get_locator(),
            text)
            
    def bookmark_element(self, element):
        log.info("Bookmarking element: %s" % 
            element.get_human_readable())
        self.sel.highlight(element.get_locator())
        self.sel.assign_id(element.get_locator(),
            DEFAULT_BOOKMARK)
            
    def is_element_present(self, element):
        log.info("Checking if %s is present..." % element.get_human_readable())
        present = self.sel.is_element_present(element.get_locator())
        log.info("Is it present? %s" % present)
        return present
        
    def run_command(self, command, background=False):
        log.info("Running command: %s..." % command)
        p = subprocess.Popen(command, 
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True)
        if background:
            return p
        (stdout, stderr) = p.communicate()
        log.info("Stdout: %s" % stdout)
        log.info("Stderr: %s" % stderr)
        log.info("Return code: %s" % p.returncode)
        return p.returncode
