import re
import sys
import pandas as pd

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class LWVLookup:
    def __init__(self, file):
        self.people = pd.read_csv(file)
        self.driver = webdriver.Safari()
        self.url = 'https://findmypollsite.vote.nyc'

    def parseAddress(self, address):
        print(address)
        regex = re.compile(',|Apt|APT|Apartment|#')
        regexAlt = re.compile('[#0-9]+[a-zA-Z]*$')
        if (regex.search(address)):  # slice off apartment numbers
            cleanAddress = re.compile(
                '(?:(?!,|Apt|APT|Apartment|apt|#).)*'
            ).search(address).group(0)
            return re.split(' ', cleanAddress, 1)
        elif (re.search('^[pP]', address)):  # PO Box
            return None
        elif (regexAlt.search(address)):
            cleanAddress = re.compile(
                '(?:(?![a-zA-Z]*[#0-9]+[a-zA-Z]*$).)*'
            ).search(
                address
            ).group(0)
            return re.split(' ', cleanAddress, 1)
        else:
            return re.split(' ', address, 1)

    def getDistrict(self, houseNumber, streetName, zip):
        self.driver.get(self.url)
        elementPresent = EC.element_to_be_clickable((By.ID, 'txtHouseNumber'))
        WebDriverWait(self.driver, 5).until(elementPresent)
        self.driver.find_element(By.ID, 'txtHouseNumber').send_keys(
            houseNumber
        )
        self.driver.find_element(By.ID, 'txtStreetName').send_keys(streetName)
        self.driver.find_element(By.ID, 'txtZipcode').send_keys(str(zip))
        self.driver.find_element(By.ID, 'btnSearch').send_keys(Keys.RETURN)
        try:
            elementPresent = EC.visibility_of_element_located((
                By.ID, 'election_district'
            ))
            WebDriverWait(self.driver, 5).until(elementPresent)
            assembly = self.driver.find_element(
                By.ID, 'assembly_district'
            ).text
            senate = self.driver.find_element(By.ID, 'senate_district').text
            council = self.driver.find_element(By.ID, 'council_district').text
            print(f"assembly {assembly}, senate {senate}, council {council}")
            return assembly, senate, council
        except:
            return ''

    def processPeople(self):
        self.people['assembly'] = None
        self.people['senate'] = None
        self.people['council'] = None
        for index, person in self.people.iterrows():
            try:
                parsedAddress = self.parseAddress(person.get(
                    'Mailing Street', person.get('MailingStreet')
                ))
                if (parsedAddress):
                    assembly, senate, council = self.getDistrict(
                        parsedAddress[0],
                        parsedAddress[1],
                        person.get(
                            'Mailing Zip/Postal Code', person.get('MailingZip')
                        ),
                    )
                    self.people.at[index, 'assembly'] = assembly
                    self.people.at[index, 'senate'] = senate
                    self.people.at[index, 'council'] = senate
            except:
                pass
        self.people.to_csv(
            './files/peopleAppended.csv', index=False
        )

    def quit(self):
        self.driver.quit()


def scrapeDistrict():
    lwv = LWVLookup('./files/' + sys.argv[1])
    lwv.processPeople()
    lwv.quit()


if __name__ == "__main__":
    scrapeDistrict()