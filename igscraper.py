# Scraper para ig

# Pendiente:
# - Ver si podemos implementar una función que nos diga quién nos dejo de seguir
# - Probar de hacer el analisis de seguidores y seguidos en paralelo (dos ventanas distintas)

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import getpass
import time

user_name = input('Please input your Instagram username : ')
password = getpass.getpass('Please input your Instagram password: ')
print(f'Hello {user_name}! \nSetting everything up and starting process... ')
options = Options()
options.headless = False
driver = webdriver.Firefox(options=options)
wait = WebDriverWait(driver, 20)


def initialize_instagram():
    print('Initializing Instagram...')
    driver.get(f'https://www.instagram.com/{user_name}/')
    print('Checking for cookies...')
    
    try:
        cookies_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'aOOlW')))
        cookies_button.click()
    except TimeoutException:
        pass

    return None


def login(username, passwrd):
    print('Logging in...')

    try:
        login_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'ZIAjV')))
        login_button.click()
    except TimeoutException:
        pass
    
    input_user = wait.until(EC.presence_of_element_located((By.NAME, 'username')))
    input_user.send_keys(username)
    time.sleep(1)
    input_pass = wait.until(EC.presence_of_element_located((By.NAME, 'password')))
    input_pass.send_keys(passwrd)
    time.sleep(2)
    signin_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]')))
    signin_button.click()
    profile_image_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, '_2dbep')))
    profile_image_button.click()
    profile_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, '_7UhW9')))
    profile_button.click()
    print('We are in. Analysis process will start in a few moments...')
    return None


def scrap_followers():
    number_of_followers = int(
        wait.until(EC.presence_of_element_located((By.XPATH, f'//a[@href="/{user_name}/followers/"]/span[1]'))).text)
    followers_button = wait.until(EC.element_to_be_clickable((By.XPATH, f'//a[@href="/{user_name}/followers/"]')))
    followers_button.click()
    followers_window = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="isgrP"]')))
    print('Starting followers gathering process:')
    followers_users = [None]
    while True:
        followers_counter = len(followers_users)
        followers_users = list(map(lambda account: account.text, driver.find_elements_by_class_name('FPmhX')))
        print(f'Gathered {len(followers_users)} out of {number_of_followers} followers.')
        driver.execute_script("arguments[0].scrollTo(0, document.body.scrollHeight*arguments[1]/12)", followers_window,
                              number_of_followers)
        time.sleep(1)
        if len(followers_users) != followers_counter:  # if both are equal, it means that the real number of followers is less than the number detailed by Instagram
            if len(followers_users) < number_of_followers:
                continue
            elif len(followers_users) > number_of_followers:
                print('The followers count is greater than your number of followers. This might have to'
                      ' do with some Instagram issue. Check the followers.txt file for more details.')
                break
            else:
                break
        else:
            print(
                f'The followers count does not match your number of followers. {number_of_followers - followers_counter} '
                f'users might have disabled their accounts.')
            break
    with open('followers.txt', mode='w') as doc_followers:
        for follower in followers_users:
            doc_followers.write(f'{follower}\n')
    print(f'{len(followers_users)} out of {number_of_followers} followers have been gathered. Starting with '
          f'following users gathering:')
    driver.find_element_by_xpath('//div[@class="WaOAr"]/button[1]').click()  # cerrar ventana de seguidores
    return followers_users


def scrap_following():
    number_of_following = int(
        wait.until(EC.presence_of_element_located((By.XPATH, f'//a[@href="/{user_name}/following/"]/span[1]'))).text)
    following_button = wait.until(EC.element_to_be_clickable((By.XPATH, f'//a[@href="/{user_name}/following/"]')))
    following_button.click()
    following_window = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="isgrP"]')))
    following_users = [None]
    while True:
        following_counter = len(following_users)
        following_users = list(map(lambda account: account.text, driver.find_elements_by_class_name('FPmhX')))
        print(f'Gathered {len(following_users)} out of {number_of_following} following users')
        driver.execute_script("arguments[0].scrollTo(0, document.body.scrollHeight*arguments[1]/12)", following_window,
                              number_of_following)
        time.sleep(1)
        if len(following_users) != following_counter:
            if len(following_users) < number_of_following:
                continue
            elif len(following_users) > number_of_following:
                print('The following users count is greater than your number of following users. This might have to'
                      ' do with some Instagram issue. Check the following.txt file for more details.')
                break
            else:
                break
        else:
            print(
                f'The following users count does not match your number of following users. {number_of_following - following_counter} '
                f'users might have disabled their accounts.')
            break
    with open('following.txt', mode='w') as doc_following:
        for following_user in following_users:
            doc_following.write(f'{following_user}\n')
    print(
        f'{len(following_users)} out of {number_of_following} following users have been gathered. Analyzing users who '
        f'don\'t follow you back:')
    time.sleep(3)
    return following_users


def analyze_following(follower_users, following_users):
    check_following = []
    with open('dontfollowback.txt', mode='w') as analysis_doc:
        analysis_doc.write('Users that you follow who don\'t follow you back \n')
        for ig_account in following_users:
            if ig_account not in follower_users:
                check_following.append(ig_account)
                analysis_doc.write(f'{ig_account}\n')
                print(f'You follow {ig_account}, but he/she does not follow you back.')
            else:
                continue
        print(f'There are {len(check_following)} users that you follow who don\'t follow you back.')
        driver.quit()
    return None


time_0 = time.time()
try:
    initialize_instagram()
    login(user_name, password)
    analyze_following(follower_users=scrap_followers(), following_users=scrap_following())
    driver.quit()
except KeyboardInterrupt:
    print('The program has been manually stopped. Closing the browser.')
    driver.quit()
except TimeoutException:
    print('TimeoutException. Something went wrong. Closing the browser.')
    driver.quit()

time_1 = time.time()
print(f'The process took {(time_1 - time_0) / 60} minutes.')
