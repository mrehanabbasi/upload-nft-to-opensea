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
project_name = 'Arabic Calligraphy'


def upload_files(start_item_id, count, is_rinkeby):
    chop = webdriver.ChromeOptions()
    chop.add_extension('Metamask-10.1.1.crx')
    driver = webdriver.Chrome(options=chop)  # Using Chrome browser
    driver.maximize_window()
    wait = WebDriverWait(driver, 60)
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
        # file_path = 'Generated\\{} ABCs {} {}.png'.format(
        #     item_id, row['Letter Permutation'], row['Hat'])
        file_path = f"Generated\{str(item_id)} {project_name} {row['Letter Permutation']} {row['Hat']}.png"
        print(file_path, item_id, row['Background'], row['Font'], row['Font & Colour Combination'],
              row['Font Colour'], row['Hat'], row['Letter 1'], row['Letter 2'],
              row['Letter 3'], row['Letter Permutation'], row['Special'], row['Name'])

        # Upload image
        wait.until(ExpectedConditions.presence_of_element_located(
            (By.XPATH, '//*[@id="media"]')))
        image_upload = driver.find_element_by_xpath('//*[@id="media"]')
        image_path = os.path.abspath(file_path)
        image_upload.send_keys(image_path)

        name = driver.find_element_by_xpath('//*[@id="name"]')
        name.send_keys(row['Name'])
        description = driver.find_element_by_xpath('//*[@id="description"]')
        description.send_keys(row['Letter Permutation'])
        collection_name = driver.find_element_by_xpath(
            '//*[@id="__next"]/div[1]/main/div/div/section/div/form/section[5]/div/input')
        collection_name.send_keys(project_name)
        # collection_button_from_list_name = '//button[normalize-space()="{}"]'.format(
        #     'The ABCs')
        collection_button_from_list_name = f'//button[normalize-space()="{project_name}"]'
        wait.until(ExpectedConditions.presence_of_element_located(
            (By.XPATH, collection_button_from_list_name)))
        collection_button_from_list = driver.find_element_by_xpath(
            collection_button_from_list_name)
        collection_button_from_list.click()
        time.sleep(0.1)

        properties_plus_button = driver.find_element_by_xpath(
            '//*[@id="__next"]/div[1]/main/div/div/section/div/form/section[6]/div[1]/div/div[2]/button')
        properties_plus_button.click()
        print('Starting properties population...')
        for i, (key, value) in enumerate(row.items()):
            if key in ['ID', 'Special', 'Name']:
                continue
            wait.until(ExpectedConditions.presence_of_element_located(
                (By.XPATH, '//button[normalize-space()="Add more"]')))
            collection_add_prop_button = driver.find_element_by_xpath(
                '//button[normalize-space()="Add more"]')
            collection_add_prop_button.click()
            prop_div_num = 3
            # prop_key_input_xpath = '/html/body/div[{}]/div/div/div/section/table/tbody/tr[{}]/td[1]/div/div/input'.format(
            #     prop_div_num, i + 1)
            prop_key_input_xpath = f'/html/body/div[{prop_div_num}]/div/div/div/section/table/tbody/tr[{i+1}]/td[1]/div/div/input'
            if len(driver.find_elements_by_xpath(prop_key_input_xpath)) <= 0:
                prop_div_num = 2
                # prop_key_input_xpath = '/html/body/div[{}]/div/div/div/section/table/tbody/tr[{}]/td[1]/div/div/input'.format(
                #     prop_div_num, i + 1)
                prop_key_input_xpath = f'/html/body/div[{prop_div_num}]/div/div/div/section/table/tbody/tr[{i+1}]/td[1]/div/div/input'
            # /html/body/div[2]/div/div/div/section/table/tbody/tr[2]/td[1]/div/div/input
            # /html/body/div[3]/div/div/div/section/table/tbody/tr[1]/td[1]/div/div/input
            time.sleep(0.1)
            wait.until(ExpectedConditions.presence_of_element_located(
                (By.XPATH, prop_key_input_xpath)))
            prop_key = driver.find_element_by_xpath(prop_key_input_xpath)
            prop_key.send_keys(key)
            # prop_key = driver.find_element_by_xpath(
            #     '/html/body/div[{}]/div/div/div/section/table/tbody/tr[{}]/td[2]/div/div/input'.format(prop_div_num,
            #                                                                                            i + 1))
            prop_key = driver.find_element_by_xpath(
                f'/html/body/div[{prop_div_num}]/div/div/div/section/table/tbody/tr[{i+1}]/td[2]/div/div/input')
            prop_key.send_keys(value)
        # prop_save = driver.find_element_by_xpath(
        #     '/html/body/div[{}]/div/div/div/footer/button'.format(prop_div_num))
        prop_save = driver.find_element_by_xpath(
            f'/html/body/div[{prop_div_num}]/div/div/div/footer/button')
        prop_save.click()
        print('Completed properties population')
        time.sleep(0.5)
        create_NFT = driver.find_element_by_xpath(
            '//*[@id="__next"]/div[1]/main/div/div/section/div/form/div/div[1]/span/button')
        # time.sleep(5000)
        create_NFT.click()
        print('creating nft ', item_id, row['Background'], row['Font'], row['Font & Colour Combination'],
              row['Hat'], row['Letter Permutation'])
        '/html/body/div[4]/div/div/div/div[1]/header/h4'
        wait.until(ExpectedConditions.presence_of_element_located(
            (By.XPATH, "/html/body/div[4]/div/div/div/div[1]/header/h4")))
        try:
            close_create_model = driver.find_element_by_xpath(
                '/html/body/div[4]/div/div/div/div[2]/button/i')
            close_create_model.click()
        except:
            print('Close Create Model not found for ',
                  item_id, row['Letter Permutation'])


def sign_into_meta(driver, wait, is_rinkeby, passphrase, wallet_pwd):
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
    passphrase_input = driver.find_element_by_xpath(
        '//*[@id = "app-content"]/div/div[3]/div/div/form/div[4]/div[1]/div/input')
    # //*[@id = "app-content"]/div/div[3]/div/div/form/div[4]/div[1]/div/input
    passphrase_input.send_keys(passphrase)
    pwd_1_input = driver.find_element_by_xpath('//*[@id="password"]')
    pwd_1_input.send_keys(wallet_pwd)
    pwd_2_input = driver.find_element_by_xpath('//*[@id="confirm-password"]')
    pwd_2_input.send_keys(wallet_pwd)
    checkbox = driver.find_element_by_xpath(
        '//*[@id="app-content"]/div/div[3]/div/div/form/div[7]/div')
    checkbox.click()
    submit = driver.find_element_by_xpath(
        '//*[@id="app-content"]/div/div[3]/div/div/form/button')
    submit.click()
    time.sleep(3)
    alldone = driver.find_element_by_xpath(
        '//*[@id="app-content"]/div/div[3]/div/div/button')
    alldone.click()
    time.sleep(1)
    x_model = driver.find_element_by_xpath(
        '//*[@id="popover-content"]/div/div/section/header/div/button')
    x_model.click()
    time.sleep(0.01)
    if is_rinkeby:
        network = driver.find_element_by_xpath(
            '//*[@id="app-content"]/div/div[1]/div/div[2]/div[1]/div')
        network.click()
        time.sleep(0.1)
        network_rinkeby = driver.find_element_by_xpath(
            '//*[@id="app-content"]/div/div[3]/div/li[4]')
        network_rinkeby.click()
    driver.switch_to.window(tabs2[1])
    time.sleep(0.1)
    # os_wallet_icon = driver.find_element_by_xpath(
    #     '//*[@id="__next"]/div[1]/div[1]/nav/ul/li[5]/button')
    # # '//*[@id="__next"]/div[1]/main/div/div/div/div[1]/div[2]/button'
    # os_wallet_icon.click()
    # time.sleep(0.1)
    # meta_icon = driver.find_element_by_xpath(
    #     '//*[@id="__next"]/div[1]/aside/div[2]/div/div[2]/ul/li[1]/button')
    # meta_icon.click()
    signin_icon = driver.find_element_by_xpath(
        '//*[@id="__next"]/div[1]/main/div/div/div/div[1]/div[2]/button')
    signin_icon.click()
    time.sleep(3.5)
    tabs2 = driver.window_handles
    driver.switch_to.window(tabs2[2])
    connect_next = driver.find_element_by_xpath(
        '//*[@id="app-content"]/div/div[3]/div/div[2]/div[4]/div[2]/button[2]')
    connect_next.click()
    time.sleep(0.5)
    connect = driver.find_element_by_xpath(
        '//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div[2]/footer/button[2]')
    connect.click()
    time.sleep(3.5)
    tabs2 = driver.window_handles
    driver.switch_to.window(tabs2[2])
    wait.until(ExpectedConditions.presence_of_element_located(
        (By.XPATH, '//*[@id="app-content"]/div/div[3]/div/div[3]/button[2]')))
    sign = driver.find_element_by_xpath(
        '//*[@id="app-content"]/div/div[3]/div/div[3]/button[2]')
    sign.click()


if __name__ == '__main__':
    upload_files(start_item_id=1, count=65, is_rinkeby=False)
