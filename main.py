from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date, datetime, timedelta
import pandas as pd
import time

# Initialize WebDriver
service = Service(executable_path='chromedriver.exe')
driver = webdriver.Chrome(service=service)
driver.maximize_window()

# Open the website
driver.get('https://www.deinhandy.de/')
time.sleep(3)

Total_Product_Details = []


def accept_cookies():
    try:
        # Accept cookies if found
        cookie_btn = driver.execute_script(
            """return document.querySelector('div#usercentrics-root').shadowRoot.querySelector('button.sc-dcJsrY.iigiUZ')""")
        cookie_btn.click()
    except Exception as e:
        print("No cookies found")


def access_section():
    # Access "Handy ohne Vertrag" section
    handy_ohne_vertrag = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/header/div[1]/div/nav/ul/li[2]/a/span'))
    )
    handy_ohne_vertrag.click()


def expand_shopping_list():
    # Click on "Mehr anzeigen" button to expand the shopping list
    mehr_anzeigen_button = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/main/div[4]/div[1]/div/button/span[1]'))
    )

    while True:
        try:
            time.sleep(1)
            driver.execute_script("arguments[0].scrollIntoView(true);", mehr_anzeigen_button)
            mehr_anzeigen_button.click()
        except Exception as e:
            break


def access_product(index):
    # Access a specific product by index
    product = driver.find_element(By.XPATH, '//*[@id="Tarifvergleich"]/li[' + str(index) + ']')
    driver.execute_script("arguments[0].scrollIntoView(false);", product)
    product.click()


def get_product_detail():
    time.sleep(1)
    # Extract product details
    brand = driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/nav/ol/li[5]/a/span').text
    name = driver.find_element(By.XPATH, '//ol[contains(@class, "MuiBreadcrumbs-ol")]/li[7]/span').text
    memory = driver.find_element(By.XPATH, '//button[contains(@class, "css-ihs9i8")]/span/span').text

    try:
        price = driver.find_element(By.XPATH, '//*[contains(@class, "css-1fkmlut")]/span[2]/span[2]/span[2]').text
        UVP = driver.find_element(By.XPATH, '//*[contains(@class, "css-1fkmlut")]/span[1]/span/span[2]').text
        price = price.replace(".", "").replace(",", "")
        UVP = UVP.replace(".", "").replace(",", "")

    except:
        price = driver.find_element(By.XPATH, '//*[contains(@class,"css-12esxuy")]/span/span[2]/span[2]').text
        price = price.replace(".", "").replace(",", "")
        UVP = price

    available_element = driver.find_element(By.XPATH, '//p[contains(@class, "css-icyxjc")]')
    color_element = driver.find_element(By.XPATH, "//*[contains(@class, 'ColorPicker-selectedColorName')]").text

    link = driver.current_url

    output_day = date.today()

    # Define available day
    available = available_element.text
    if "Sofort" in available_element.text:
        available = date.today()  # Return date
    elif "ab" in available_element.text:
        available = datetime.strptime(available_element.text.split()[2], "%d.%m.%Y").date()
    else:
        shipping_days = int(available_element.text.split()[2].split("-")[1])  # Return string
        available = date.today() + timedelta(days=int(shipping_days))

    Product_Details = {
        "brand": brand,
        "name": name,
        "color": color_element,
        "memory": memory,
        "price": int(price),
        "available": available,
        "UVP": int(UVP),
        "link": link,
        "date": output_day,
    }

    return Product_Details


def find_total_memory():
    parent_dir = driver.find_element(By.XPATH,
                                     "//*[contains(@class, 'ProductConfigutaion-attributeSwitch MuiBox-root css-0')]")
    children_dir = parent_dir.find_elements(By.XPATH, "//div[contains(@class,'css-7g071d')]")
    total_children = len(children_dir) // 2
    return int(total_children)


def detail_product_by_color():
    first_div = driver.find_element(By.XPATH,
                                    "//div[contains(@class, 'ProductConfigutaion-attributeSwitch css-gq8qx5')]/div")
    buttons = first_div.find_elements(By.TAG_NAME, "button")
    for button in buttons:
        if button.get_attribute("class") in ("css-r6e490", "css-1gophbz"):
            button.click()
            Product_Details = get_product_detail()
            Total_Product_Details.append(Product_Details)


def export_excel_file(product_list):
    df = pd.DataFrame(product_list)
    df = df.reset_index(drop=True)  # drop=True removes the original index column
    df.index = df.index + 1
    df.to_excel("output.xlsx")


def go_back():
    driver.back()


accept_cookies()
access_section()
time.sleep(1)

# Count total of available products
total_products_element = WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'css-1jrytxy')]"))
)
total_products_element = total_products_element.text
total_products = int(total_products_element.split(" ")[4])

expand_shopping_list()

for i in range(1, total_products):
    time.sleep(1)
    access_product(i)
    try:
        time.sleep(1)
        available_check = driver.find_element(By.XPATH, "//*[contains(@class,'css-18covu4')]")
        go_back()
    except:
        for j in range(1, find_total_memory() + 1):
            # Find all buttons with tag name button within the first div

            memory_select = driver.find_element(By.XPATH,
                                                "//div[contains(@class,'ProductConfigutaion-attributeSwitch MuiBox-root css-0')]/div[" + str(
                                                    j) + "]")
            memory_select.click()
            detail_product_by_color()

        go_back()

export_excel_file(Total_Product_Details)
time.sleep(10)
