from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.keys import Keys
import json
import os
import time
import yaml

class WutongSearch():

    def __init__(self,config_file="config.yaml"):

        assert os.path.isfile(config_file),'%s is not a file' % config_file
        with open(config_file,'r',encoding='utf-8') as f:
            config = yaml.load(f)
        self.chrome_config = config['chrome_config']
        self.search_engine_config = config['search_engine_config']
        self.webdriver = self.init_driver(self.chrome_config)

    def init_driver(self, chrome_config):
        '''init the driver using config
        
        Arguments:
            chrome_config {dict} -- dict read from config.yaml: chrome_config
        
        Raises:
            e -- driver init exception
        
        Returns:
            webdriver -- the driver
        '''

        chrome_options = Options()
        if chrome_config['disable_window']:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            ########### dont load image ################
            image_prefs = {
                'profile.default_content_setting_values': {
                    'images': 2
                }
            }
            chrome_options.add_experimental_option('prefs', image_prefs)
        if chrome_config['disable_image']:
            ########### dont load image ################
            image_prefs = {
                'profile.default_content_setting_values': {
                    'images': 2
                }
            }
            chrome_options.add_experimental_option('prefs', image_prefs)
        
        if chrome_config['user_data_dir']:
            chrome_options.add_argument("user-data-dir=%s" % chrome_config['user_data_dir'])
        
        if chrome_config['proxy_server']:
            chrome_options.add_argument('--proxy-server=%s' % chrome_config['proxy_server'])

        chrome_options.add_argument('--ignore-ssl-errors')
        try:
            driver = webdriver.Chrome(
                executable_path=chrome_config['chrome_driver_path'], chrome_options=chrome_options)
        except Exception as e:
            raise e
        return driver

    def click_next_page(self, selector):
        '''click to get the next page
        
        Arguments:
            selector {a xpath string} -- xpath locator for next page element
        '''
        ############get the next page element##################
        element = self.webdriver.find_element_by_xpath(selector)
        webdriver.ActionChains(self.webdriver).move_to_element(
            element).perform()
        ############ click next page ##############
        element.click()
    
    def has_next_page(self,next_page_selector):
        '''check if there is more pages
        
        Arguments:
            next_page_selector {a xpath selector} -- xpath locator for next page
        
        Returns:
            bool -- whether there is more pages
        '''

        try:
            WebDriverWait(self.webdriver, self.chrome_config['next_page_wait']).until(
                EC.presence_of_element_located((By.XPATH, next_page_selector)))
        except TimeoutException as e:
            print("No more pages",e)
            return False
        return True

    def has_result(self,result_selector):
        '''check if there is result
        
        Arguments:
            result_selector {xpath string} -- xpath locator for result element
        
        Returns:
            bool -- whether there are results
        '''

        try:
            WebDriverWait(self.webdriver, self.chrome_config['result_wait']).until(
                EC.presence_of_element_located((By.XPATH, result_selector)))
        except TimeoutException as e:
            print("No more results",e)
            return False
        return True
        

    def save_page_result(self, result_loacator):
        '''extract urls from the result pages
        
        Arguments:
            result_loacator {xpath} --  xpath locator for result element
        
        Returns:
            list -- (url,title) list
        '''

        page1_results = self.webdriver.find_elements(By.XPATH, result_loacator)
        res = []
        for item in page1_results:
            url = item.get_attribute('href')
            if url not in res:
                res.append((url, item.text))
        return res

    def search(self, keyword, search_engine='baidu', num_pages_per_keyword=2):
        '''choose search engine to search the keyword
        
        Arguments:
            keyword {str} -- the word you want to search
        
        Keyword Arguments:
            search_engine {str} -- search engine name (default: {'baidu'})
            num_pages_per_keyword {int} -- how many pages you want to get (default: {2})
        
        Returns:
            list -- (url,title) list
        '''

        assert search_engine in self.search_engine_config.keys(), "only " + str(self.search_engine_config.keys()) + "supported!"
        engine_config = self.search_engine_config[search_engine]
        search_engine_url = engine_config['search_engine_url']
        input_selector = engine_config['input_selector']
        next_page_selector = engine_config['next_page_selector']
        result_selector = engine_config['result_selector']

        if engine_config['proxy_server'] != self.chrome_config['proxy_server']:
            self.webdriver.quit()
            self.chrome_config['proxy_server'] = engine_config['proxy_server']
            self.webdriver = self.init_driver(self.chrome_config)
        # open the search website
        self.webdriver.get(search_engine_url)
        # enter the keyword
        input_element = self.webdriver.find_element_by_xpath(input_selector)
        input_element.send_keys(keyword)
        input_element.submit()

        result = []
        # wait until the result loaded
        if not self.has_result(result_selector):
            return result
        # get the result
        if not engine_config['dynamic_load_result']:
            result += self.save_page_result(result_loacator=result_selector)
        # next page
        needed_pages = num_pages_per_keyword - 1
        while needed_pages > 0:
            ### to ensure the page loaded
            time.sleep(self.chrome_config['two_pages_internal'])
            if self.has_next_page(next_page_selector):
                self.click_next_page(next_page_selector)
                # wait until the result loaded
                if self.has_result(result_selector):
                    if not engine_config['dynamic_load_result']:
                        result += self.save_page_result(result_loacator=result_selector)
                needed_pages -= 1
            else:
                break
        if engine_config['dynamic_load_result']:
            result += self.save_page_result(result_loacator=result_selector)
        return result


def main():

    kws = ['小米', '华为', '苹果']

    save_path = "add_%s" % "sensitive"
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    # assert search_engine in ['baidu','duckduckgo','bing']
    wsearch = WutongSearch()
    for kw in kws:
        if os.path.exists("%s/%s.txt" % (save_path, kw)):
            continue
        print(F"Start DownLoad============{kw}")
        try:
            res2 = wsearch.search(
                kw, search_engine='baidu', num_pages_per_keyword=2)
            print(len(res2))
            res3 = wsearch.search(
                kw, search_engine='google', num_pages_per_keyword=3)
            res = res3+res2
            r_dict = {}
            for r in res:
                if r[0] not in r_dict:
                    r_dict[r[0]] = r[1]
            print(F"total num========={len(res)}")
            with open("%s/%s.txt" % (save_path, kw), 'w') as f:
                json.dump(r_dict, f)
            # time.sleep(random.uniform(10, 20))
        except Exception as e:
            print(F"error======{kw} ", e)
            wsearch.webdriver.quit()
            wsearch.webdriver = wsearch.init_driver(
                "chromedriver/chromedriver.exe")
            continue



if __name__ == '__main__':
    main()
