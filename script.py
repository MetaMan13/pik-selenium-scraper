from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from datetime import datetime
import os, codecs, requests, mysql.connector, pathlib, shutil, stat, time

# MYSQL stuff START
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password = "",
    database="net_doo"
)

driver = webdriver.Chrome('./chromedriver')
driver.maximize_window()

# 165 done right
for count in range(129, 167):
    mycursor = mydb.cursor(buffered=True)
    driver.get("https://www.olx.ba/profil/NETdoo/aktivni?stranica=" + str(count))
    websiteAnchorTags = driver.find_elements_by_xpath('//a[@href]')

    productLinks = []

    for count, link in enumerate(websiteAnchorTags, start=0):
        if("artikal" in link.get_attribute("href")):
            productLinks.append(link.get_attribute("href"))

    # Since we get duplicate entries we want to remove duplicates from the list
    productLinks = list(dict.fromkeys(productLinks))

    for productLink in productLinks:
        driver.get(productLink)

        productName = driver.find_element_by_id('naslovartikla')
        productPrice = driver.find_elements_by_tag_name('p')
        productState = ''
        try:        
            productDescription = driver.find_element_by_id('detaljni-opis')
        except:
            productDescription = ''
        try:
            productAmount = driver.find_element_by_xpath('//p[@style="background-color: #daedf7;font-size: 25px;color: #5b90b0;text-align: center;"]')
            productAmount = int(productAmount.text)        
        except:
            pass

        for price in productPrice:
            if("KM" in price.text):
                productPrice = price.text.replace('.', '')
            elif("Novo" in price.text or "Korišteno" in price.text):
                productState = price.text
            elif("Po dogovoru" in price.text):
                productPrice = int(0)

        productImageLinks = []
        try:
            productGallery = driver.find_element_by_xpath('//img[@class="img-polaroid dugme_galerija mobile"]')
            productGallery.click()
        except:
            pass

        driver.implicitly_wait(10)
        try:
            numberOfImages = driver.find_element_by_id('naslov_th')
            numberOfImages = int(numberOfImages.text.split("/",1)[1])
        except:
            pass

        def find(driver):
            try:
                nextButton = driver.find_element_by_class_name('fancybox-next')
                return nextButton
            except:
                pass

        if(numberOfImages != 1 and numberOfImages != 0):
            for count in range(0, numberOfImages):
                try:
                    time.sleep(2)
                    currentGalleryImage = driver.find_element_by_xpath('//img[@class="fancybox-image"]')
                    productImageLinks.append(currentGalleryImage.get_attribute('src'))
                    print(currentGalleryImage.get_attribute('src'))
                    nextButton = WebDriverWait(driver, 100).until(find)
                    nextButton.click()
                except:
                    pass
                    continue
        else:
            try:
                currentGalleryImage = driver.find_element_by_xpath('//img[@class="fancybox-image"]')
                productImageLinks.append(currentGalleryImage.get_attribute('src'))
            except:
                pass

        newFolder = productName.text.replace(' ', '-').replace('/', '-').replace(',', '-').replace('--', '-').replace('\\', '-').replace('.', '-').replace('#', '-').replace('%', '-').replace('&', '-').replace('{', '-').replace('}', '-').replace('<', '-').replace('>', '-').replace('*', '-').replace('?', '-').replace('$', '-').replace('!', '-').replace('\'', '-').replace('"', '-').replace('+', '-').replace('`', '-').replace('|', '-').replace('=', '-').replace(':', '-') 

        # CREATE FOLDER
        try:
            os.mkdir(os.path.join(os.getcwd(), newFolder))
        except:
            pass
        # CHANGE INTO CREATED FOLDER
        os.chdir(os.path.join(os.getcwd(), newFolder))
        if("Novo" in productState):
            productState = 0
        elif("Korišteno" in productState):
            productState = 1

        productImageFiles = []
        # DOWNLOAD AND SAVE IMAGE
        if(len(productImageLinks) != 0):
            for count, link in enumerate(productImageLinks):
                productImageFile = open(link.replace(' ', '-').replace('/', '-').replace(',', '-').replace('--', '-').replace('\\', '-').replace('.', '-').replace('#', '-').replace('%', '-').replace('&', '-').replace('{', '-').replace('}', '-').replace('<', '-').replace('>', '-').replace('*', '-').replace('?', '-').replace('$', '-').replace('!', '-').replace('\'', '-').replace('"', '-').replace('+', '-').replace('`', '-').replace('|', '-').replace('=', '-').replace(':', '-') + '.jpg', 'wb')
                print(productImageFile.name)
                im = requests.get(productImageLinks[count])
                productImageFile.write(im.content)
                productImageFile.close()
                productImageFiles.append(productImageFile.name)
                try:
                    shutil.move(os.path.join(os.getcwd(), str(productImageFile.name)), 'C:/Users/halfamomo/Desktop/Code/laravel-real/net-doo/public/images')
                except:
                    pass

        # INSERT INTO DATABASE
        datetimeObject = datetime.now()
        sql = "INSERT INTO products(name, price, amount,state, active, short_details, long_details, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        if(productDescription != ''):
            try:
                sql = "INSERT INTO products(name, price, amount,state, active, short_details, long_details, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                val = (productName.text, productPrice, productAmount, productState, 1, productDescription.text, productDescription.text, datetimeObject, datetimeObject)
                mycursor.execute(sql, val)
            except:
                pass
        else:
            try:
                sql = "INSERT INTO products(name, price, amount,state, active, short_details, long_details, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                val = (productName.text, productPrice, productAmount, productState, 1, productDescription, productDescription, datetimeObject, datetimeObject)
                mycursor.execute(sql, val)
            except:
                pass
        mydb.commit()
        
        sql = "SELECT MAX(id) FROM products"
        mycursor.execute(sql)
        mydb.commit()
        productId = mycursor.fetchone()[0]
        print(productId)
        for productImageFile in productImageFiles:
            sql = "INSERT INTO product_images(product_id, image_url, created_at, updated_at) VALUES (%s, %s, %s, %s)"
            val = (int(productId) , "/images/" + str(productImageFile), datetimeObject, datetimeObject)
            mycursor.execute(sql, val)
        mydb.commit()
        os.chdir(os.path.normpath(os.getcwd() + os.sep + os.pardir))
        os.chmod(os.path.join(os.getcwd(), newFolder), stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        shutil.rmtree(os.path.join(os.getcwd(), newFolder), ignore_errors=False)
driver.quit()