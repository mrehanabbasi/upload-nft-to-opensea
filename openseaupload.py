# import itertools
import os

import pandas
from selenium import webdriver
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from selenium.webdriver.support import expected_conditions as ExpectedConditions

from dotenv import load_dotenv


load_dotenv()

testnet_url = 'https://testnets.opensea.io/asset/create'
mainnet_url = 'https://opensea.io/asset/create'


def uploadFiles(start_item_id, count, is_rinkeby, metamask_exists):
    chop = webdriver.ChromeOptions()
    if not metamask_exists:
        chop.add_extension('MetaMask_v10.1.1.crx')
    driver = webdriver.Opera(options=chop)
    wait = WebDriverWait(driver, 60)
    df = pandas.read_csv('Generated/metadata.csv')
    if is_rinkeby:
        url = testnet_url
    else:
        url = mainnet_url
    driver.get(url)
    time.sleep(0.5)

    # If Metamask extension is not already installed and not logged into OpenSea
    if not metamask_exists:
        passphrase = os.getenv('METAMASK_PASSPHRASE')
        wallet_pwd = os.getenv('METAMASK_PASSWORD')
        signIntoMeta(driver, wait, is_rinkeby, passphrase, wallet_pwd)

    tabs2 = driver.window_handles
    driver.switch_to.window(tabs2[1])
    time.sleep(2)
    for index, row in df.iterrows():
        item_id = row['ID']
        if item_id < start_item_id or item_id >= start_item_id + count:
            print('Skipping row:', index, item_id)
            continue
        print('Running row:', index, item_id)
        if index > 0:
            wait.until(ExpectedConditions.presence_of_element_located(
                (By.XPATH, '//*[@id="__next"]/div[1]/div[1]/nav/ul/li[4]/a')))
            createPage = driver.find_element_by_xpath(
                '//*[@id="__next"]/div[1]/div[1]/nav/ul/li[4]/a')
            createPage.click()
        filePath = 'Generated\\{} ABCs {} {}.png'.format(
            item_id, row['Letter Permutation'], row['Hat'])
        print(filePath, item_id, row['Background'], row['Font'], row['Font & Colour Combination'],
              row['Font Colour'], row['Hat'], row['Letter 1'], row['Letter 2'],
              row['Letter 3'], row['Letter Permutation'], row['Special'], row['Name'])
        wait.until(ExpectedConditions.presence_of_element_located(
            (By.XPATH, '//*[@id="media"]')))
        imageUpload = driver.find_element_by_xpath('//*[@id="media"]')
        imagePath = os.path.abspath(
            filePath)
        imageUpload.send_keys(imagePath)

        name = driver.find_element_by_xpath('//*[@id="name"]')
        name.send_keys(row['Name'])
        description = driver.find_element_by_xpath('//*[@id="description"]')
        description.send_keys(row['Letter Permutation'])
        collectionName = driver.find_element_by_xpath(
            '//*[@id="__next"]/div[1]/main/div/div/section/div/form/section[5]/div/input')
        collectionName.send_keys('The ABCs')
        collectionButtonFromListName = '//button[normalize-space()="{}"]'.format(
            'The ABCs')
        wait.until(ExpectedConditions.presence_of_element_located(
            (By.XPATH, collectionButtonFromListName)))
        collectionButtonFromList = driver.find_element_by_xpath(
            collectionButtonFromListName)
        collectionButtonFromList.click()
        time.sleep(0.1)

        propertiesPlusButton = driver.find_element_by_xpath(
            '//*[@id="__next"]/div[1]/main/div/div/section/div/form/section[6]/div[1]/div/div[2]/button')
        propertiesPlusButton.click()
        print('starting properties population')
        for i, (key, value) in enumerate(row.items()):
            if key in ['ID', 'Special', 'Name']:
                continue
            wait.until(ExpectedConditions.presence_of_element_located(
                (By.XPATH, '//button[normalize-space()="Add more"]')))
            collectionAddPropButton = driver.find_element_by_xpath(
                '//button[normalize-space()="Add more"]')
            collectionAddPropButton.click()
            propDivNum = 3
            propKeyInputXpath = '/html/body/div[{}]/div/div/div/section/table/tbody/tr[{}]/td[1]/div/div/input'.format(
                propDivNum, i + 1)
            if len(driver.find_elements_by_xpath(propKeyInputXpath)) <= 0:
                propDivNum = 2
                propKeyInputXpath = '/html/body/div[{}]/div/div/div/section/table/tbody/tr[{}]/td[1]/div/div/input'.format(
                    propDivNum, i + 1)
            # /html/body/div[2]/div/div/div/section/table/tbody/tr[2]/td[1]/div/div/input
            # /html/body/div[3]/div/div/div/section/table/tbody/tr[1]/td[1]/div/div/input
            time.sleep(0.1)
            wait.until(ExpectedConditions.presence_of_element_located(
                (By.XPATH, propKeyInputXpath)))
            propKey = driver.find_element_by_xpath(propKeyInputXpath)
            propKey.send_keys(key)
            propKey = driver.find_element_by_xpath(
                '/html/body/div[{}]/div/div/div/section/table/tbody/tr[{}]/td[2]/div/div/input'.format(propDivNum,
                                                                                                       i + 1))
            propKey.send_keys(value)
        propSave = driver.find_element_by_xpath(
            '/html/body/div[{}]/div/div/div/footer/button'.format(propDivNum))
        propSave.click()
        print('completed properties population')
        time.sleep(0.5)
        createNFT = driver.find_element_by_xpath(
            '//*[@id="__next"]/div[1]/main/div/div/section/div/form/div/div[1]/span/button')
        # time.sleep(5000)
        createNFT.click()
        print('creating nft ', item_id, row['Background'], row['Font'], row['Font & Colour Combination'],
              row['Hat'], row['Letter Permutation'])
        '/html/body/div[4]/div/div/div/div[1]/header/h4'
        wait.until(ExpectedConditions.presence_of_element_located(
            (By.XPATH, "/html/body/div[4]/div/div/div/div[1]/header/h4")))
        try:
            closeCreateModal = driver.find_element_by_xpath(
                '/html/body/div[4]/div/div/div/div[2]/button/i')
            closeCreateModal.click()
        except:
            print('Close Create Modal not found for ',
                  item_id, row['Letter Permutation'])


def signIntoMeta(driver, wait, isrinkeby, mnemonicString, walletPwd):
    tabs2 = driver.window_handles
    driver.switch_to.window(tabs2[0])
    time.sleep(0.5)
    # driver.close()
    # driver.switch_to.window(tabs2[0])
    button = driver.find_element_by_xpath(
        '//*[@id="app-content"]/div/div[3]/div/div/div/button')
    button.click()
    print('meta clicked')
    time.sleep(0.5)
    button = driver.find_element_by_xpath(
        '//*[@id="app-content"]/div/div[3]/div/div/div[2]/div/div[2]/div[1]/button')
    button.click()
    button = driver.find_element_by_xpath(
        '//*[@id="app-content"]/div/div[3]/div/div/div/div[5]/div[1]/footer/button[1]')
    button.click()
    time.sleep(0.5)
    mnemonicInput = driver.find_element_by_xpath(
        '//*[@id="app-content"]/div/div[3]/div/div/form/div[4]/div[1]/div/input')
    mnemonicInput.send_keys(mnemonicString)
    pwd1Input = driver.find_element_by_xpath('//*[@id="password"]')
    pwd1Input.send_keys(walletPwd)
    pwd2Input = driver.find_element_by_xpath('//*[@id="confirm-password"]')
    pwd2Input.send_keys(walletPwd)
    checkbox = driver.find_element_by_xpath(
        '//*[@id="app-content"]/div/div[3]/div/div/form/div[7]/div')
    checkbox.click()
    submit = driver.find_element_by_xpath(
        '//*[@id="app-content"]/div/div[3]/div/div/form/button')
    submit.click()
    time.sleep(1)
    alldone = driver.find_element_by_xpath(
        '//*[@id="app-content"]/div/div[3]/div/div/button')
    alldone.click()
    time.sleep(1)
    xmodal = driver.find_element_by_xpath(
        '//*[@id="popover-content"]/div/div/section/header/div/button')
    xmodal.click()
    time.sleep(0.01)
    if isrinkeby:
        network = driver.find_element_by_xpath(
            '//*[@id="app-content"]/div/div[1]/div/div[2]/div[1]/div')
        network.click()
        time.sleep(0.1)
        networkRinkeby = driver.find_element_by_xpath(
            '//*[@id="app-content"]/div/div[3]/div/li[4]')
        networkRinkeby.click()
    driver.switch_to.window(tabs2[1])
    time.sleep(0.1)
    oswalleticon = driver.find_element_by_xpath(
        '//*[@id="__next"]/div[1]/div[1]/nav/ul/li[5]/button')
    oswalleticon.click()
    time.sleep(0.1)
    metaicon = driver.find_element_by_xpath(
        '//*[@id="__next"]/div[1]/aside/div[2]/div/div[2]/ul/li[1]/button')
    metaicon.click()
    time.sleep(1.5)
    tabs2 = driver.window_handles
    driver.switch_to.window(tabs2[2])
    connectnext = driver.find_element_by_xpath(
        '//*[@id="app-content"]/div/div[3]/div/div[2]/div[4]/div[2]/button[2]')
    connectnext.click()
    time.sleep(0.5)
    connect = driver.find_element_by_xpath(
        '//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div[2]/footer/button[2]')
    connect.click()
    time.sleep(0.5)
    wait.until(ExpectedConditions.presence_of_element_located(
        (By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[3]/button[2]')))
    sign = driver.find_element_by_xpath(
        '//*[@id="app-content"]/div/div[3]/div/div[3]/button[2]')
    sign.click()


if __name__ == '__main__':
    uploadFiles(start_item_id=186, count=65,
                is_rinkeby=False, metamask_exists=True)
