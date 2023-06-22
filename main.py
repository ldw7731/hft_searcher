import asyncio
from contextlib import closing
from selenium import webdriver
from selenium.webdriver.common.by import By

class AsyncIteratorWrapper():
    def __init__(self, obj):
        self._it = iter(obj)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            value = next(self._it)
        except StopIteration:
            raise StopAsyncIteration
        return value

def GetChromeOptions():
    selenoid_options = {
        "enableVNC": True,
        "enableVideo": False
    }
    Chrome_Options = webdriver.ChromeOptions()
    Chrome_Options.set_capability("browserName", "firefox")
    Chrome_Options.set_capability("browserVersion", "114.0")
    Chrome_Options.set_capability("selenoid:options", selenoid_options)
    return Chrome_Options

async def GetDriver():
    driver = webdriver.Remote(
        command_executor='http://localhost:4444/wd/hub',
        options = GetChromeOptions(),
        keep_alive=True)
    return driver

async def parse_hh():
    driver = await GetDriver()

    url = 'https://hh.ru/search/vacancy?text=HFT'
    driver.get(url)

    vacancies = driver.find_elements(by=By.CLASS_NAME, value='serp-item__title')
    vac_list = []

    for vac in vacancies:
        try:
            vacancy = vac.get_attribute('href')
            vac_list.append(vacancy)
        except Exception as ex:
            print(ex)

    company_info = []
    for url_vac in vac_list:
        try:
            driver.get(url_vac)

            comp_name_field = driver.find_element(by=By.CLASS_NAME, value='vacancy-company-name')
            comp_name_text = comp_name_field.text
            comp_name_field_children = comp_name_field.find_element(by=By.TAG_NAME, value='a')

            company_href = comp_name_field_children.get_attribute('href')
            company_info.append([comp_name_text, company_href])
        except Exception as ex:
            print(ex)

    for company in company_info:
        try:
            driver.get(company[1])
            # company_header = driver.find_element(by=By.CLASS_NAME, value='company-header-title-name')

            company_desc = driver.find_elements(by=By.CLASS_NAME, value='g-user-content')
            print(company[0])
            print(company_desc[0].text)
            print('====================================================================================')
        except Exception as ex:
            print(ex)
    driver.quit()

with closing(asyncio.get_event_loop()) as loop:
    loop.run_until_complete(parse_hh())


