import datetime as dt
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import yagmail

def get_tradingview():

    driver = webdriver.Chrome(ChromeDriverManager().install())

    stock_urls = [
                  'https://se.tradingview.com/symbols/OMXSTO-AAK/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-ARISE/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-ASAI/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-ASSA_B/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-AZN/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-AXFO/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-AZA/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-AZELIO/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-BHG/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-BIOT/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-BRAV/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-BURE/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-CAST/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-EQT/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-ESSITY_B/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-EVO/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-FABG/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-FPIP/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-GARO/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-GETI_B/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-HEBA_B/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-HOVD/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-ITAB_B/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-INSTAL/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-INVE_A/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-INWI/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-KINV_B/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-LATO_B/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-LUMI/technicals/',
                  'https://se.tradingview.com/symbols/NASDAQ-TIGO/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-MYCR/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-NIBE_B/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-NYF/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-NWG/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-PDX/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-SBB_B/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-SECU_B/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-SKA_B/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-STWK/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-STW/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-SYSR/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-TEL2_B/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-THULE/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-VOLO/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-ZETA/technicals/',
                  'https://se.tradingview.com/symbols/OMXSTO-ORES/technicals/']

    tradingview_list = []

    try:

        for i in range(len(stock_urls)):
            driver.get(stock_urls[i])
            try:
                xpath_full1 = '/html/body/div[3]/div[5]/div/div/div/div/div/div/div/div[2]/div/div[2]/div/div/div[2]/div[2]/span[2]'

                class1 = 'tv-symbol-header__second-line--text'
                class2 = 'speedometerSignal-pyzN--tL'

                last_update = dt.datetime.now()
                last_update = last_update.strftime("%y-%m-%d %H:%M:%S")

                ticker = WebDriverWait(driver, 12).until(
                    EC.presence_of_element_located((By.CLASS_NAME, class1))).text
                state = WebDriverWait(driver, 12).until(
                    EC.presence_of_element_located((By.CLASS_NAME, class2))).text

                # ticker = WebDriverWait(driver, 12).until(
                #    EC.visibility_of_element_located((By.XPATH, xpath_full2))).text


                # print("Current date and time: ")
                # print(now.strftime("%y-%m-%d %H:%M:%S"))
                stock_item = {
                    'ticker': ticker,
                    'state': state,
                    'last_update': last_update
                }
                tradingview_list.append(stock_item)

                df = pd.DataFrame.from_dict(tradingview_list)
                list1 = df.values.tolist()
                print(f"Here comes the DF: {df}")

                # print(ticker)
                # print(state)
            except NameError as x:
                print("The Error is: ", x)
            except:
                print("An exception occurred")

    finally:
        driver.quit()

    df1 = pd.DataFrame(df, columns=['ticker', 'state', 'last_update'])

    ##include code for sending mail
    EMAIL_ADDRESS1 = "mr.sven.mueller@gmail.com"
    EMAIL_ADDRESS2 = "super.toy.cars.media@gmail.com"
    EMAIL_PASSWORD = 'fiurdvwldrfvhtll'
    try:
        # initializing the server connection
        yag = yagmail.SMTP(user=EMAIL_ADDRESS2, password=EMAIL_PASSWORD)

        # sending the email
        yag.send(to=EMAIL_ADDRESS1,
                 subject='Tradingview run',
                 contents=df1.to_html())

    except:
        print("Error, email was not sent")

    return tradingview_list