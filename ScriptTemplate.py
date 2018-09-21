import sys, os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.remote.webelement import WebElement
import time
import datetime
import xml.etree.ElementTree as ET
capabilities = DesiredCapabilities.INTERNETEXPLORER
capabilities['ignoreProtectedModeSettings'] = True
capabilities['ignoreZoomSetting'] = True
capabilities.setdefault("nativeEvents", False)
driver = webdriver.Ie(capabilities=capabilities)
#driver = webdriver.Firefox()

driver.implicitly_wait(30)

wait = WebDriverWait(driver, 30)

class HTMLElement:
    def __init__(self, selector, tag="*", elem_type=None):
        self.elem = None
        if(isinstance(selector, WebElement)):
            self.elem = selector
        else:
            btnselect = ""
            if tag == "btn":
                self.tag = "*"
                btnselect = "[(self::input and (@type='button' or @type='submit')) or self::button]"
            elif tag == "img":
                self.tag = "*"
                btnselect = "[(self::input and (@type='image' or @type='IMAGE')) or self::img]"

            else:
                self.tag = tag
            self.elem_type = elem_type
            type_str = ""
            if  elem_type is not None:
                type_str = "[@type='" + elem_type + "']"
            locator = None
            #Select elem where Text is something | HTMLElement("Caption=Some Text") or HTMLElement("Text=Some Text")
            if "Caption=" in selector or "Text=" in selector:
                locator = By.XPATH
                text = selector[selector.find("=")+1:]
                if self.tag == "btn":
                    self.waitUntilVisible(locator, "//" + self.tag +  type_str + btnselect + "[@value='" + text + "' or contains(text(),'" + text + "')]")
                    self.elem = driver.find_element_by_xpath("//" + self.tag  + type_str +  btnselect + "[@value='" + text + "' or contains(text(),'" + text + "')]")
                if self.tag == "input":
                    self.waitUntilVisible(locator, "//" + self.tag +  type_str + "[@value='" + text + "']")
                    self.elem = driver.find_element_by_xpath("//" + self.tag  + type_str + "[@value='" + text + "']")
                else:
                    self.waitUntilVisible(locator, "//" + self.tag +  type_str + "[contains(text(),'" + text + "')]")
                    self.elem = driver.find_element_by_xpath("//" + self.tag  + type_str + "[contains(text(), '" + text + "')]")
            #Select the nth item | HTMLElement("Index=6")
            elif "Index=" in selector:
                locator = By.XPATH
                index = selector[selector.find("Index=")+6:]
                self.waitUntilVisible(locator, "//" + self.tag  + btnselect + type_str + "[" + index + "]")
                self.elem = driver.find_element_by_xpath("//" + self.tag + btnselect + type_str + "[" + index + "]")
            #select elem where xpath attributes are complex [expression] | HTMLElement("[@class='xyz' and @value='3']") or HTMLElement("[@class='myclass'][3]")
            elif "[" in selector:
                locator = By.XPATH
                self.waitUntilVisible(locator, "//" + self.tag  + btnselect + type_str + selector)
                self.elem = driver.find_element_by_xpath("//" + self.tag  + btnselect + type_str + selector)
            #select by ID or Name of selector | HTMLElement("SomeNameOrID")
            elif "=" not in selector:
                locator = By.XPATH
                text = selector
                self.waitUntilVisible(locator, "//" + self.tag  + btnselect + type_str + "[@name='" + text + "' or @id='"+ text +"']")
                self.elem = driver.find_element_by_xpath("//" + self.tag  + btnselect + type_str + "[@name='" + text + "' or @id='"+ text +"']")
            #select elem where one attribue=value | HTMLElement("Name=SomeName") or HTMLElement("Id=SomeID") or HTMLElement("Attr=SomeValue")
            else:
                locator = By.XPATH
                text = selector[selector.find("=")+1:]
                attr = selector[0:selector.find("=")].lower()
                self.waitUntilVisible(locator, "//" + self.tag +  btnselect + type_str + "[@" + attr + "='" + text + "']")
                self.elem = driver.find_element_by_xpath("//" + self.tag + btnselect + type_str + "[@" + attr + "='" + text + "']")
    def waitUntilVisible(self, locator, text): 
        try:
            if(self.tag == "a" or self.tag == "button" or self.tag == "img"):
                wait.until(EC.element_to_be_clickable((locator, text)))
            else:
                wait.until(EC.visibility_of_element_located((locator, text)))
        except Exception as err:
            print(str(err))
            print('Element ' + text + ' failed to be visible while waiting, or selector is invalid')
            raise err
    def Click(self):
        if(self.tag == "a" and (self.elem.get_attribute("href") is not None and "javascript" in self.elem.get_attribute("href"))):
            driver.execute_script("arguments[0].click();", self.elem)
        else:
            self.elem.click()
            
class HTMLAnchor(HTMLElement):
    def __init__(self, selector):
        HTMLElement.__init__(self, selector, "a")
class HTMLInputButton(HTMLElement):
    def __init__(self, selector):
        HTMLElement.__init__(self, selector, "input", "button")
class HTMLButton(HTMLElement):
    def __init__(self, selector):
        HTMLElement.__init__(self, selector, "btn")
class HTMLTypeAble(HTMLElement):
    def __init__(self, selector, tag, elem_type=None):
        HTMLElement.__init__(self, selector, tag, elem_type)
    def SetText(self, keysToSend):
        self.elem.send_keys(keysToSend)
    def Type(self, keysToSend):
        if "{Return}" in keysToSend:
            self.elem.send_keys(Keys.RETURN)
        elif "{Tab}" in keysToSend:
            self.elem.send_keys(Keys.TAB)
        else:
            self.elem.send_keys(keysToSend)
class HTMLTextArea(HTMLTypeAble):
    def __init__(self, selector):
        HTMLTypeAble.__init__(self, selector, "textarea")
class HTMLEditBox(HTMLTypeAble):
    def __init__(self, selector):
        HTMLTypeAble.__init__(self, selector, "input")
class HTMLRadioButton(HTMLElement):
    def __init__(self, selector):
        HTMLElement.__init__(self, selector, "input", "radio")
class HTMLCheckBox(HTMLElement):
    def __init__(self, selector):
        HTMLElement.__init__(self, selector, "input", "checkbox")
class HTMLSubmit(HTMLElement):
    def __init__(self, selector):
        HTMLElement.__init__(self, selector, "input", "submit")
class HTMLTD(HTMLElement):
    def __init__(self, selector):
        HTMLElement.__init__(self, selector, "td")
class HTMLDiv(HTMLElement):
    def __init__(self, selector):
        HTMLElement.__init__(self, selector, "div")
class HTMLImage(HTMLElement):
    def __init__(self, selector):
        HTMLElement.__init__(self, selector, "img")
class HTMLFrame(HTMLElement):
    def __init__(self, selector):
        HTMLElement.__init__(self, selector, "iframe")
        driver.switch_to.frame(self.elem)
class HTMLBaseFrame():
    def __init__(self):
        driver.switch_to.default_content()
class HTMLComboBox(HTMLElement):
    def __init__(self, selector):
        HTMLElement.__init__(self, selector, "*")
class HTMLParagraph(HTMLElement):
    def __init__(self, selector):
        HTMLElement.__init__(self, selector, "p")
class HTMLSpan(HTMLElement):
    def __init__(self, selector):
        HTMLElement.__init__(self, selector, "span")
class HTMLH1(HTMLElement):
    def __init__(self, selector):
        HTMLElement.__init__(self, selector, "h1")
class HTMLH2(HTMLElement):
    def __init__(self, selector):
        HTMLElement.__init__(self, selector, "h2")
class HTMLH3(HTMLElement):
    def __init__(self, selector):
        HTMLElement.__init__(self, selector, "h3")
class HTMLTable(HTMLElement):
    def __init__(self, selector):
        HTMLElement.__init__(self, selector, "table")
class HTMLList(HTMLElement):
    def __init__(self, selector):
        HTMLElement.__init__(self, selector, "ul")
        self.listitems = self.elem.find_elements(By.TAG_NAME, "li")
    def get_item_by_index(self, i):
        item = self.listitems[i]
        return HTMLElement(item)
    def get_item_by_text(self, text):
        item = next((x for x in self.listitems if x.text == text), None)
        return HTMLElement(item)
    def get_item_by_attribute(self, selector):
        text = selector[selector.find("=")+1:]
        attr = selector[0:selector.find("=")].lower()
        item = next((x for x in self.listitems if x[attr] == text), None)
        return HTMLElement(item)
        
class HTMLListItem(HTMLElement):
    def __init__(self, selector):
        HTMLElement.__init__(self, selector, "li")
class HTMLSelect(HTMLElement):
    def __init__(self, selector):
        HTMLElement.__init__(self, selector, "select")
        self.select = Select(self.elem)
cache  = {}
timers = {}
def ShowStatusBox(msg):
    print(msg)
def StartTrace(id):
    timers[id] = {}
    timers[id]["start"] = time.time()
    timers[id]["end"] = None

def StopTimerAndTrace(id):
    timers[id]["end"] = time.time()
    print(id + " stopped at " + str(round(timers[id]["end"] - timers[id]["start"], 2)) + "s")
def GoToPage(page):
    driver.get(page)
def WaitForText(text, t=30, required=True):
    waitUntilTextVisible(By.TAG_NAME, "html", text, t, required)
def getpassword(uid):
    f = open('C:/AppDFiles/users.xml', 'r')
    xml = f.read()
    userlist = ET.fromstring(xml)
    user = userlist.find("./user[@id='"+str(uid)+"']")
    pw = user.get("password")
    return pw
def getid(uid):
    f = open('C:/AppDFiles/users.xml', 'r')
    xml = f.read()
    userlist = ET.fromstring(xml)
    user = userlist.find("./user[@id='"+str(uid)+"']")
    username = user.get("username")
    return username

def newWindow(url):
    cache['previous'] = driver.current_url
    driver.get(url)

def previousWindow():
    if cache['previous'] is not None and cache['previous']:
        driver.get(cache['previous'])
        cache['previous'] = None

def click(selector, elementStr):
    try:
        element = wait.until(EC.element_to_be_clickable((selector, elementStr)))
        if(driver.capabilities['browserName'] == "internet explorer"):
            href = element.get_attribute('href')
            if href is not None and "window.open" in href:
                url = href[href.find("(")+1:href.find(")")]
                if(url[0] == "'" or url[0] == "\""):
                    url = url[1:-1]
                if(url[-1:] == "'" or url[-1:] == "\""):
                    url = url[:-1]
                driver.get(url)
            else:
                element.click()
        else:
            element.click()
    except Exception as err:
        print(err)
        print('Element failed to be clickable while waiting, or selector is invalid')
        raise err
def waitUntilElementVisible(selector, elementStr):
    try:
        wait.until(EC.visibility_of_element_located((selector, elementStr)))
    except Exception as err:
        print(err)
        print('Element failed to be visible while waiting, or selector is invalid')
        raise err
def waitUntilTextVisible(selector, selectorText, textToFind, t=20, required=True):
    try:
        text_wait = WebDriverWait(driver, t)
        text_wait.until(EC.text_to_be_present_in_element((selector, selectorText), textToFind))
    except Exception as err:
        print(err)
        print('Text "' + textToFind + '"  failed to be visible while waiting')
        if(required):
            raise err

def sendKeys(selector, elementStr, keysToSend):
    try:
        wait.until(EC.element_to_be_clickable((selector, elementStr))).send_keys(keysToSend)
    except Exception as err:
        print(err)
        print('Element failed to be clickable in 10s, or selector is invalid: ')
        raise err


try:
    #Test Internal
    print(driver.capabilities['browserName'])
    print("Testing All Controls")
    
    StartTrace("GoToPage")
    GoToPage("https://www.appdynamics.com/")

    assert "AppDynamics" in driver.title
    StopTimerAndTrace("GoToPage")
  
    ShowStatusBox("Testing Anchor")
    a = HTMLAnchor("Caption=Take a tour")
    assert a.elem.text == "Take a tour"
    a.Click()

    WaitForText("Guided Tour: AppDynamics Application Performance Management")
    ShowStatusBox("Successfully Clicked Anchor")

    GoToPage("https://www.appdynamics.com")
    HTMLDiv("Caption=Products ").Click()

       
    # HTMLCheckbox("")
    # HTMLComboBox("")
    # HTMLDiv("")
    # HTMLEditBox("")
    # HTMLImage("")
    # HTMLSelect("")

    



  
except Exception as err:
    driver.get_screenshot_as_file('page.png')
    filename = 'page' + str(int(time.time())) + '.png'
    driver.save_screenshot(filename)
    # if os.path.exists("C:\\appdynamics\\synthetic-agent\\" + filename):
    #     os.remove("C:\\appdynamics\\synthetic-agent\\" + filename)
    print(err)
    raise(err)
          
    
finally:
    driver.quit()
