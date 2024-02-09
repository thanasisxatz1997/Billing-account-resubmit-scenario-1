import time
from datetime import datetime
import cfgModule
import Customer
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

def CurrentFileDateTime():
    now = datetime.now()
    return now.strftime("%d_%m_%Y-%H_%M_%S")

def CreateLogFile():
    fileName='Logs_' + CurrentFileDateTime() + '.txt'
    with open(fileName, "w", encoding="utf-8") as logsFile:
        logsFile.write("Procedure started.")
    return fileName

def WriteLog(fileName, text):
    print(text)
    with open(fileName, "a", encoding="utf-8") as logsFile:
        logsFile.write(text + '\n')

def CreateDriver(sleepTime=2):
    firefox_options = Options()
    # firefox_options.add_argument('--headless')
    driver = webdriver.Firefox(options=firefox_options)
    driver.get(
        "https://customer.ote.gr/siebel/app/ecommsso/enu/?SWECmd=GotoView&SWEView=CUT+Home+Page+View+(CME)&SWERF=1&SWEHo=&SWEBU=1&SWEApplet0=Layout+Controls+Applet&SWERowId0=VRId-0")
    time.sleep(sleepTime)
    return driver


def ClickOnListElementWithText(driver, targetText, selector, sleepTime=1):
    elements = driver.find_elements(By.CSS_SELECTOR, selector)
    for element in elements:
        if element.text == targetText:
            driver.execute_script("arguments[0].scrollIntoView();", element)
            element.click()
            break
    time.sleep(sleepTime)
    return


def ClickElementWithSelector(driver, selector, sleeptime=1):
    element = driver.find_element(By.CSS_SELECTOR, selector)
    time.sleep(sleeptime)
    element.click()
    time.sleep(sleeptime)
    return element


def SendListOfKeysToElement(element, keyList, sleepTime=0.5):
    for key in keyList:
        element.send_keys(key)
        time.sleep(sleepTime)


def SubmitBillingAccount(driver, customer):
    ClickOnListElementWithText(driver, "Billing Accounts", "a[class='ui-tabs-anchor']")
    ClickElementWithSelector(driver, "button[title='Billing Account List Applet:Query']")
    element = ClickElementWithSelector(driver, "input[id='1_OTE_Billing_Account_Code']")
    SendListOfKeysToElement(element, [customer.baCode, u'\ue007'])
    ClickOnListElementWithText(driver, "Billing Account Request Administration", "a[class='ui-tabs-anchor']")
    element = driver.find_element(By.CSS_SELECTOR, "button[title='Billing Account List Applet:Go to View']")
    time.sleep(1)
    submitStatusCode = ""
    if element.is_enabled():
        print("Clicking on go to view")
        element.click()
        time.sleep(1)
        ClickElementWithSelector(driver, "button[title='Billing Accounts Form Applet:Submit']")
        try:
            element = driver.find_element(By.ID, "_sweview_popup")
            if element.text != '':
                print(f"Popup found with text {element.text}")
                submitStatusCode = element.text
                element = driver.find_element(By.ID, "btn-accept")
                element.click()
                time.sleep(1)
                element = driver.find_element(By.CSS_SELECTOR, "button[id='s_2_1_3_0_Ctrl']")
                driver.execute_script("arguments[0].scrollIntoView();", element)
                time.sleep(2)
                element.click()
                time.sleep(1)
        except NoSuchElementException:
            try:
                alert = driver.switch_to.alert
                if alert:
                    submitStatusCode = 'Alert found while submitting billing account.'
                    print("alert found with text:")
                    print(alert.text)
                    alert.accept()
            except:
                print("Submitted successfully! No popup")
                submitStatusCode = 'Success'
    else:
        print("Go to view not enabled, Updating otemig with error.")
        submitStatusCode= "Go to view not enabled."
    return submitStatusCode

def UpdateOtemigForCustomerStatus(cursor, conn, customer, statusCode):
    if statusCode == "Success":
        cfgModule.UpdateOtemigWithSuccess(cursor, conn, customer.custId)
    else:
        cfgModule.UpdateOtemigWithError(cursor, conn, customer.custId, statusCode)


if __name__ == '__main__':
    logFileName=CreateLogFile()
    customers = cfgModule.RunConfig()
    WriteLog(logFileName, "cfg completed successfully.")
    for customer in customers:
        WriteLog(logFileName, customer.GetCustomerStr())
    driver = CreateDriver(7)
    oteMigCursor, oteMigConn = cfgModule.ConnectToOtemigDb(cfgModule.decOtemig)
    statusCode = "Starting submit procedure."
    statusCodes=[]
    WriteLog(logFileName,"Starting procedure for each billing account.")
    for customer in customers:
        try:
            statusCode = SubmitBillingAccount(driver, customer)
        except Exception as exs:
            print(
                f"Error while submitting billing account for customer with id: {customer.custId}, ba_rid: {customer.baRid}, exception thrown: {exs}")
            statusCode = f"Error while submitting billing account for customer with id: {customer.custId}, ba_rid: {customer.baRid}, exception thrown: {exs}"
        finally:
            WriteLog(logFileName, f"Procedure finished for customer with id: {customer.custId}, ba_rid: {customer.baRid}, ended with status code: {statusCode}")
            UpdateOtemigForCustomerStatus(oteMigCursor, oteMigConn, customer, statusCode)
            ClickOnListElementWithText(driver, "Billing Accounts", "a[class='ui-tabs-anchor']")
            time.sleep(1)
            statusCodes.append(statusCode)
    WriteLog(logFileName, "Procedure completed for all billing accounts.")
    oteMigConn.close()
    driver.quit()
