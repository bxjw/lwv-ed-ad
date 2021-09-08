import re, sys
import pandas as pd

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

url = 'https://findmypollsite.vote.nyc'

def startDriver():
    driver = webdriver.Safari()
    return driver

def parseAddress(address):
    regex = re.compile('(.+),|Apt|#|[0-9]+[a-zA-Z]+')
    if (regex.search(address)):
        cleanAddress = regex.search(address).group(1)
        return re.split(' ', cleanAddress, 1)
    else:
        return None

def getEdAd(houseNumber, streetName, zip, driver):
    driver.get(url)
    elementPresent = EC.element_to_be_clickable((By.ID, 'txtHouseNumber'))
    WebDriverWait(driver, 5).until(elementPresent)
    driver.find_element_by_id('txtHouseNumber').send_keys(houseNumber)
    driver.find_element_by_id('txtStreetName').send_keys(streetName)
    driver.find_element_by_id('txtZipcode').send_keys(zip)
    driver.find_element_by_id('btnSearch').send_keys(Keys.RETURN)
    try:
        driver.find_element_by_id('search-error')
        return ''
    except NoSuchElementException:
        elementPresent = EC.presence_of_element_located((By.ID, 'election_district'))
        WebDriverWait(driver, 5).until(elementPresent)
        district = driver.find_element_by_id('election_district').text
        return district

def loopOverPeople(people, driver):
    people['EDAD'] = ''
    for index, person in people.iterrows():
        parsedAddress = parseAddress(people['Mailing.Address.Line.1'])
        if (parsedAddress):
            district = getEdAd(
                parsedAddress[0],
                parsedAddress[1],
                people['Mailing.Zip.Postal.Code'],
                driver
            )
            person['EDAD'] = district
    return people

def scrapeEdAd():
    people = pd.read_csv('../files/' + sys.argv[1])
    driver = startDriver()
    peopleAppended = loopOverPeople(people, driver)  
    peopleAppended.to_csv('../files/peopleAppended.csv', index = False)
    driver.quit()

if __name__ == "__main__":
    scrapeEdAd()