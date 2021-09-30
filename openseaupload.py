# import itertools
import os

import pandas
from selenium import webdriver
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support import expected_conditions as ExpectedConditions

from dotenv import load_dotenv


load_dotenv()

testnet_url = 'https://testnets.opensea.io/asset/create'
mainnet_url = 'https://opensea.io/asset/create'
project_name = 'Simple Bicycle'


def upload_files(start_item_id, count, is_rinkeby):
    chop = webdriver.ChromeOptions()
    chop.add_extension('Metamask-10.1.1.crx')
    driver = webdriver.Chrome(options=chop)  # Using Chrome browser
    driver.maximize_window()
    # Adjust the time as per your internet speed
    wait = WebDriverWait(driver, 100)
    df = pandas.read_csv('Generated/metadata.csv')
    if is_rinkeby:
        url = testnet_url
    else:
        url = mainnet_url
    driver.get(url)
    time.sleep(0.5)

    passphrase = os.getenv('METAMASK_PASSPHRASE')
    wallet_pwd = os.getenv('METAMASK_PASSWORD')
    sign_into_meta(driver, wait, is_rinkeby, passphrase, wallet_pwd)

    tabs2 = driver.window_handles
    driver.switch_to.window(tabs2[1])
    time.sleep(2)
    for index, row in df.iterrows():
        item_id = row['edition']
        if item_id < start_item_id or item_id >= start_item_id + count:
            print('Skipping row:', index, item_id)
            continue
        print('Running row:', 'Index Num', index, 'Item:', item_id)
        if index > 0:
            wait.until(ExpectedConditions.presence_of_element_located(
                (By.XPATH, '//*[@id="__next"]/div[1]/div[1]/nav/ul/div[1]/li[4]/a')))
            createPage = driver.find_element_by_xpath(
                '//*[@id="__next"]/div[1]/div[1]/nav/ul/div[1]/li[4]/a')
            createPage.click()
        file_path = f"Generated\{item_id}.png"
        print('Started', file_path, item_id, row['background'],
              row['bicycle'], row['text'], row['font'])

        # Upload image
        wait.until(ExpectedConditions.presence_of_element_located(
            (By.XPATH, '//*[@id="media"]')))
        image_upload = driver.find_element_by_xpath('//*[@id="media"]')
        image_path = os.path.abspath(file_path)
        image_upload.send_keys(image_path)

        # Add NFT name
        name = driver.find_element_by_xpath('//*[@id="name"]')
        name.send_keys(f"{project_name} {row['name']}")
        # Add NFT description
        description = driver.find_element_by_xpath('//*[@id="description"]')
        description.send_keys(
            f"{row['description']} {row['background']} - {row['bicycle']} - {row['text']} - {row['font']}")

        # Select Collection name (should be already created)
        collection_name = driver.find_element_by_xpath(
            '//*[@id="__next"]/div[1]/main/div/div/section/div/form/section[5]/div/input')
        # Below two lines are to ensure that there is no extra text in input field
        # collection_name.clear() was not working
        collection_name.send_keys(Keys.CONTROL + 'a')
        collection_name.send_keys(Keys.DELETE)
        collection_name.send_keys(project_name)
        # This might change as per web designer's discretion
        collection_button_from_list_name = f'//span[normalize-space()="{project_name}"]'
        wait.until(ExpectedConditions.presence_of_element_located(
            (By.XPATH, collection_button_from_list_name)))
        collection_button_from_list = driver.find_element_by_xpath(
            collection_button_from_list_name)
        collection_button_from_list.click()
        time.sleep(0.1)

        # Properties population from metadata.csv file
        properties_plus_button = driver.find_element_by_xpath(
            '//*[@id="__next"]/div[1]/main/div/div/section/div/form/section[6]/div[1]/div/div[2]/button')
        properties_plus_button.click()
        print('Starting properties population...')
        unneeded = ['dna', 'name', 'description',
                    'image', 'edition', 'date', 'compiler']
        for i, (key, value) in enumerate(row.items()):
            if key in unneeded:
                continue
            wait.until(ExpectedConditions.presence_of_element_located(
                (By.XPATH, '//button[normalize-space()="Add more"]')))
            collection_add_prop_button = driver.find_element_by_xpath(
                '//button[normalize-space()="Add more"]')
            collection_add_prop_button.click()
            prop_div_num = 5
            prop_key_input_xpath = f'/html/body/div[{prop_div_num}]/div/div/div/section/table/tbody/tr[{i-4}]/td[1]/div/div/input'
            # prop_div_num can be 5 or 2 depending on the situation
            # This is to ensure that there is no error while code is running
            if len(driver.find_elements_by_xpath(prop_key_input_xpath)) <= 0:
                prop_div_num = 2
                prop_key_input_xpath = f'/html/body/div[{prop_div_num}]/div/div/div/section/table/tbody/tr[{i-4}]/td[1]/div/div/input'
            # /html/body/div[2]/div/div/div/section/table/tbody/tr[2]/td[1]/div/div/input
            # /html/body/div[5]/div/div/div/section/table/tbody/tr[1]/td[1]/div/div/input
            time.sleep(0.1)
            wait.until(ExpectedConditions.presence_of_element_located(
                (By.XPATH, prop_key_input_xpath)))
            prop_key = driver.find_element_by_xpath(prop_key_input_xpath)
            prop_key.send_keys(key)
            prop_key = driver.find_element_by_xpath(
                f'/html/body/div[{prop_div_num}]/div/div/div/section/table/tbody/tr[{i-4}]/td[2]/div/div/input')
            prop_key.send_keys(value)
        prop_save = driver.find_element_by_xpath(
            f'/html/body/div[{prop_div_num}]/div/div/div/footer/button')
        prop_save.click()
        print('Completed properties population')
        time.sleep(0.5)

        # Click on create button
        create_NFT = driver.find_element_by_xpath(
            '//*[@id="__next"]/div[1]/main/div/div/section/div/form/div/div[1]/span/button')
        create_NFT.click()
        print('Creating NFT: ', item_id, row['background'],
              row['bicycle'], row['text'], row['font'])
        # Wait for the create confirmation box by waiting for the NFT title
        # This also confirms which NFT is created based on its name
        wait.until(ExpectedConditions.presence_of_element_located(
            (By.XPATH, '/html/body/div[6]/div/div/div/div[1]/header/h4')))
        try:
            # Close the create confimation box
            close_create_model = driver.find_element_by_xpath(
                '/html/body/div[6]/div/div/div/div[2]/button/i')
            close_create_model.click()
            print('NFT creation completed!')
        except:
            print('Close Create Model not found for ', item_id)


def sign_into_meta(driver, wait, is_rinkeby, passphrase, wallet_pwd):
    tabs = driver.window_handles    # Get current window handles
    driver.switch_to.window(tabs[0])    # Switch to Metamask tab
    time.sleep(0.5)

    # Click 'Get Started'
    button = driver.find_element_by_xpath(
        '//*[@id="app-content"]/div/div[3]/div/div/div/button')
    button.click()
    print('Metamask "Get Started" button clicked!')
    time.sleep(0.5)

    # Click 'Import Wallet'
    button = driver.find_element_by_xpath(
        '//*[@id="app-content"]/div/div[3]/div/div/div[2]/div/div[2]/div[1]/button')
    button.click()

    # Click on 'Agree' to agree terms and conditions
    button = driver.find_element_by_xpath(
        '//*[@id="app-content"]/div/div[3]/div/div/div/div[5]/div[1]/footer/button[1]')
    button.click()
    time.sleep(0.5)

    # Input passphrase / seed phrase
    passphrase_input = driver.find_element_by_xpath(
        '//*[@id = "app-content"]/div/div[3]/div/div/form/div[4]/div[1]/div/input')
    passphrase_input.send_keys(passphrase)

    # Input password twice
    pwd_1_input = driver.find_element_by_xpath('//*[@id="password"]')
    pwd_1_input.send_keys(wallet_pwd)
    pwd_2_input = driver.find_element_by_xpath('//*[@id="confirm-password"]')
    pwd_2_input.send_keys(wallet_pwd)

    # Check the checkbox
    checkbox = driver.find_element_by_xpath(
        '//*[@id="app-content"]/div/div[3]/div/div/form/div[7]/div')
    checkbox.click()

    # Click on 'Submit'
    submit = driver.find_element_by_xpath(
        '//*[@id="app-content"]/div/div[3]/div/div/form/button')
    submit.click()
    time.sleep(0.1)

    # Click on 'All Done' after it appears
    wait.until(ExpectedConditions.presence_of_element_located(
        (By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div/button')))
    alldone = driver.find_element_by_xpath(
        '//*[@id="app-content"]/div/div[3]/div/div/button')
    alldone.click()
    time.sleep(1)

    # Clock the box that appears
    x_model = driver.find_element_by_xpath(
        '//*[@id="popover-content"]/div/div/section/header/div/button')
    x_model.click()
    time.sleep(0.01)

    # For testnet
    if is_rinkeby:  # Code not tested yet
        network = driver.find_element_by_xpath(
            '//*[@id="app-content"]/div/div[1]/div/div[2]/div[1]/div')
        network.click()
        time.sleep(0.1)
        network_rinkeby = driver.find_element_by_xpath(
            '//*[@id="app-content"]/div/div[3]/div/li[4]')
        network_rinkeby.click()

    # Switch to OpenSea tab
    driver.switch_to.window(tabs[1])
    time.sleep(0.1)

    # Click on 'Sign in' button
    signin_icon = driver.find_element_by_xpath(
        '//*[@id="__next"]/div[1]/main/div/div/div/div[1]/div[2]/button')
    signin_icon.click()
    time.sleep(3.5)

    # Switch to new Metamask window which opened
    tabs = driver.window_handles
    driver.switch_to.window(tabs[2])

    # Click on Next
    wait.until(ExpectedConditions.presence_of_all_elements_located(
        (By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[2]/div[4]/div[2]/button[2]')))
    connect_next = driver.find_element_by_xpath(
        '//*[@id="app-content"]/div/div[3]/div/div[2]/div[4]/div[2]/button[2]')
    connect_next.click()
    time.sleep(0.5)

    # Click on 'Connect'
    connect = driver.find_element_by_xpath(
        '//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div[2]/footer/button[2]')
    connect.click()
    time.sleep(4.5)

    # Switch to new Metamask window which opened
    tabs = driver.window_handles
    driver.switch_to.window(tabs[2])

    # Click on 'Sign'
    wait.until(ExpectedConditions.presence_of_element_located(
        (By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[3]/button[2]')))
    sign = driver.find_element_by_xpath(
        '//*[@id="app-content"]/div/div[3]/div/div[3]/button[2]')
    sign.click()


if __name__ == '__main__':
    upload_files(start_item_id=459, count=500, is_rinkeby=False)
