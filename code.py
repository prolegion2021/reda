from random import randint
from random import choice
from datetime import date
import requests
import string
import time
import names
import xmltodict as xmltodict
from selenium import webdriver
from bs4 import BeautifulSoup
from imap_tools import MailBox, AND
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import mariadb
import sys
import subprocess

def get_tor_session():
    session = requests.session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  'socks5://192.168.8.101:9050',
                       'https': 'socks5://192.168.8.101:9050'}
    # session = get_tor_session()
    # print(session.get("http://httpbin.org/ip").text)
    return session

def change_ip_tor():
    session = get_tor_session()
    #print(session.get("http://httpbin.org/ip").text)
    response = session.get('http://jsonip.com')
    ip = response.json()['ip']
    print('Мой IP: ', ip)
    time.sleep(1)
    #print(os.system('net stop tor | net start tor'))
    stopstr = 'net stop tor | net start tor'
    print(subprocess.run(['powershell', stopstr], shell=True))
    time.sleep(10)
    response = session.get('http://jsonip.com')
    ip1 = response.json()['ip']
    if ip == ip1:
        #print(os.system('net stop tor | net start tor'))
        subprocess.run(['powershell', stopstr], shell=True)
        time.sleep(10)
    response = session.get('http://jsonip.com')
    ip1 = response.json()['ip']
    print('Your NEW public IP is:', ip1)
    if ip == ip1:
        print(f'Наш IP {ip1} не поменялся, запускаю заново')


def switch_modem(state):
	BASE_URL = 'http://{host}'
	TOKEN_URL = '/api/webserver/SesTokInfo'
	#SWITCH_URL = '/api/dialup/mobile-dataswitch'
	SWITCH_URL1 = '/api/net/net-mode'
	session = None
	host = '192.168.8.1'
	base_url = BASE_URL.format(host=host)
	session = requests.Session()
	try:
		# Get session and verification tokens from the modem
		r = session.get(base_url + TOKEN_URL, timeout=3)
		_dict = xmltodict.parse(r.text).get('response', None)

		# Build the switch request
		headers = {
			'Cookie': _dict['SesInfo'],
			'__RequestVerificationToken': _dict['TokInfo']
		}
		#data = '<?xml version: "1.0" encoding="UTF-8"?><request><dataswitch>' + state + '</dataswitch></request>'
		data1 = '<?xml version: "1.0" encoding="UTF-8"?><request><NetworkMode>' + state + '</NetworkMode><NetworkBand>3FFFFFFF</NetworkBand><LTEBand>7FFFFFFFFFFFFFFF</LTEBand></request>'

		r = session.post(base_url + SWITCH_URL1, data=data1, headers=headers, timeout=3)
		if r.status_code == 200:
			return True
		else:
			return False

	except Exception as ex:
		print("Failed to switch modem..")
		print(ex)
		return False

def generateUser():
	list = 'qwertyuiopasdfghjklzxcvbnm'
	rs = []
	for x in list:
		rs.append(x)
	rs_0 = random.choice(rs)
	rs_1 = random.choice(rs)
	rs3 = []
	list1 = '_', '-'
	for x in list1:
		rs3.append(x)
	rs3_0 = random.choice(rs3)
	rs3_1 = random.choice(rs3)
	rs1_0 = random.choice(rs3_0)
	rs1_1 = random.choice(rs3_1)
	first = names.get_first_name()
	last = names.get_last_name()
	username = first + rs_0 + ''.join(rs1_0) + last + rs_1 + ''.join(rs1_1) + ''.join(str(randint(0, 9)) for i in range(randint(1, 3)))
	password = ''.join(choice(string.ascii_letters+string.digits) for i in range(randint(10, 20)))
	return username, password

def createAccount(username, password):
	#
	# proxy_l = ['5.61.58.211:4007']
	# print(proxy_l[0].split(':'))
	# proxy_ip, proxy_port = proxy_l[0].split(':')
	option = webdriver.FirefoxOptions()
	option.set_preference('dom.webdriver.enabled', False)
	option.set_preference('dom.webnotifications.enabled', False)
	option.set_preference('dom.volume_scale', '0.0')
	profile = webdriver.FirefoxProfile()
	# profile.set_preference('network.proxy.type', 1)
	# profile.set_preference('network.proxy.socks', '192.168.80.139')
	# profile.set_preference('network.proxy.socks_port', 9150)
	# profile.set_preference("network.proxy.type", 1)
	# profile.set_preference("network.proxy.http", proxy_ip)
	# profile.set_preference("network.proxy.http_port", int(proxy_port))
	# profile.set_preference("network.proxy.ssl", proxy_ip)
	# profile.set_preference("network.proxy.ssl_port", int(proxy_port))
	# profile.set_preference("network.proxy.socks_remote_dns", True)
	profile.set_preference("browser.privatebrowsing.autostart", True)
	profile.update_preferences()

	driver = webdriver.Firefox(executable_path='geckodriver_x64.exe', options=option, firefox_profile=profile)

	try:

		print('Clearing all cookies...')
		driver.delete_all_cookies()
		driver.get("http://192.168.8.1/html/home.html")
		time.sleep(10)
		off = driver.find_element_by_xpath('//*[@id="new_switch_content"]').text
		if off == 'Отключено':
			print('Включаю инет обратно')
			driver.find_element_by_xpath('//*[@id="new_switch_bg"]').click()
			time.sleep(5)
			print('Очистка кукисов')
			driver.delete_all_cookies()
			time.sleep(2)
			print('Закрываю браузер...')
			driver.close()
		elif off == 'Подключено':
			response = requests.get('http://jsonip.com')
			ip = response.json()['ip']
			print('Your public IP is:', ip)
			time.sleep(1)
			switch_modem('02')
			time.sleep(10)
			response = requests.get('http://jsonip.com')
			ip1 = response.json()['ip']
			if ip == ip1:
				switch_modem('03')
				time.sleep(10)
			response = requests.get('http://jsonip.com')
			ip1 = response.json()['ip']
			print('Your NEW public IP is:', ip1)
			if ip == ip1:
				print(f'Наш IP {ip1} не поменялся, запускаю заново')
				driver.delete_all_cookies()
				time.sleep(2)
				print('Закрываю браузер...')
				driver.close()
			else:
				print('Creating account with username: ' + username + ' and password: ' + password + '...')
				print('Начинаю регистрацию аккаунта: ' + username + ' and password: ' + password + '...')
				driver.get("https://old.reddit.com/register")

				wait = WebDriverWait(driver, 1)
				wait.until(EC.visibility_of_element_located((By.ID, "user_reg")))
				print('Ввожу сгенерированный логин: ', username)
				driver.find_element_by_id('user_reg').click()
				driver.find_element_by_id('user_reg').send_keys(username)
				time.sleep(randint(1, 2))
				print('Ввожу сгенерированный пароль: ', password)
				driver.find_element_by_id('passwd_reg').click()
				driver.find_element_by_id('passwd_reg').send_keys(password)
				time.sleep(randint(1, 2))
				print('Ввожу подтверждение пароля')
				driver.find_element_by_id('passwd2_reg').click()
				driver.find_element_by_id('passwd2_reg').send_keys(password)
				time.sleep(randint(1, 2))
				mail_list = ['@rsmono.com', '@stprime.ml', '@stprime.tk']
				r_mail_list = random.choice(mail_list)
				mail = username+r_mail_list
				print('Ввожу email: ', mail)
				time.sleep(2)
				driver.find_element_by_id('email_reg').send_keys(mail)
				time.sleep(randint(2, 4))
				print('Пора ввести капчу :(')

				print('Solving captcha...')
				time.sleep(randint(10,15))
				apiKey = 'rucaptcha_API_KEY' #Add your API key here!
				siteKey = '6LeTnxkTAAAAAN9QEuDZRpn90WwKk_R1TRW_g-JC'
				pageUrl = 'https://old.reddit.com/register'
				requestUrl = 'http://rucaptcha.com/in.php?key='+apiKey+'&method=userrecaptcha&googlekey='+siteKey+'&pageurl='+pageUrl
				print('Запрос на RUcaptcha API...')
				resp = requests.get(requestUrl)
				if(resp.text[0:2] != 'OK'):
					print('Service error has occured. Error code: '+resp.text)
					return
				captchaId = resp.text[3:]
				print('Запрос отправлен, ждём 30 сек ...')
				time.sleep(30)
				returnUrl = 'http://rucaptcha.com/res.php?key='+apiKey+'&action=get&id='+captchaId
				print('Requesting return...')
				resp = requests.get(returnUrl)
				if resp.text == 'CAPCHA_NOT_READY':
					while resp.text == 'CAPCHA_NOT_READY':
						print('Капча ещё не распознана, повторю проверку через 5 сек ...')
						time.sleep(5)
						resp = requests.get(returnUrl)
				elif resp.text[0:5] == 'ERROR':
					print('Service error has occured. Error code: '+resp.text)
					return
				ansToken = resp.text[3:]
				if ansToken == 'OR_CAPCHA_UNSOLVABLE':
					print('Service error has occured. Error code: '+resp.text)
					return
				print('Получили токен капчи: '+ansToken)
				captchaInput = driver.find_element_by_id('g-recaptcha-response')
				driver.execute_script("arguments[0].setAttribute('style','visibility:visible;');", captchaInput)
				captchaInput.send_keys(ansToken)
				# input("После ввода капчи нажмите любую кнопку")
				print('Жму кнопку регистрации')
				driver.find_element_by_xpath('/html/body/div[3]/div/div/div[1]/form/div[8]/button').click()
				t = 0
				while t <= 60:
					time.sleep(1)
					print('Проверяю почту на входящие с для аккаунта: ', mail)
					with MailBox('mail.rsmono.com').login('support@rsmono.com', 'k9HXTsEvE3BIdbp6') as mailbox:
						subjects = [msg.to for msg in mailbox.fetch()]
						for resu in subjects:
							if resu[0] == mail:
								print('Нашел входящие для ', mail)
								subjects = [msg.html for msg in mailbox.fetch(AND(to=mail))]
								soup = BeautifulSoup(''.join(subjects), 'lxml')
								for a in soup.find_all('a', class_="link c-white", href=True):
									link_verif = a['href']
									print("Found the URL:", a['href'])
									time.sleep(2)
									print('Подтверждаю почту для Reddit')
									driver.get(link_verif)
									time.sleep(7)
									print('Кабинет создания APP')
									driver.get("https://old.reddit.com/prefs/apps/")
									time.sleep(5)
									print('Create app button')
									driver.find_element_by_xpath('//*[@id="create-app-button"]').click()
									time.sleep(5)
									print('Enter app name')
									driver.find_element_by_xpath(
										'/html/body/div[3]/div[3]/form/table/tbody/tr[1]/td/input').send_keys(username)
									time.sleep(1)
									print('Select checkbox - "script" ')
									driver.find_element_by_xpath('//*[@id="app_type_script"]').click()
									time.sleep(1)
									print('Enter description for app')
									driver.find_element_by_xpath(
										'/html/body/div[3]/div[3]/form/table/tbody/tr[5]/td/textarea').send_keys('app by ',
																												 username)
									time.sleep(1)
									print('Enter URL for app')
									driver.find_element_by_xpath(
										'/html/body/div[3]/div[3]/form/table/tbody/tr[7]/td/input').send_keys(
										'http://localhost:8080')
									time.sleep(1)
									print('Click Create App API')
									driver.find_element_by_xpath('/html/body/div[3]/div[3]/form/button').click()
									time.sleep(5)
									reddit_api = driver.find_element_by_xpath(
										'/html/body/div[3]/div[2]/ul/li/div[2]/h3[2]').text
									html = driver.page_source
									soup = BeautifulSoup(html, 'lxml')
									for link in soup.select(
											f'#developed-app-{reddit_api} > div:nth-child(3) > h3:nth-child(3)'):
										api1 = link.renderContents()
										api = str(api1, 'utf-8')
										print('First API: ', link.renderContents())
									for link in soup.select(
											f'#update-app-{reddit_api} > table:nth-child(4) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(2)'):
										'table.preftable:nth-child(4) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(2)'
										secret1 = link.renderContents()
										secret = str(secret1, 'utf-8')
										print('First Secret: ', link.renderContents())
									# with sq.connect("autoreg_accounts.db") as con:
									# 	cur = con.cursor()
									# 	#cur.execute(f"INSERT INTO accounts_reg VALUES('{str(username)}', )")
									# 	cur.execute(f"INSERT INTO accounts_reg(username, password, mail, client_id, client_secret, date) "
									# 				f"VALUES('{str(username)}', '{str(password)}', '{str(mail)}', '{str(api)}', '{str(secret)}', '{str(date.today())}')")
									try:
										try:
											conn = mariadb.connect(
												user="root",
												password="Qq164352",
												host="31.43.139.206",
												port=3336,
												database="spam"

											)
										except mariadb.Error as e:
											print(f"Error connecting to MariaDB Platform: {e}")
											sys.exit(1)
										cur = conn.cursor()
										cur.execute(
											"INSERT INTO accounts_reg (username,password,mail,client_id,client_secret,date,banned)"
											"VALUES (?,?,?,?,?,?,?)",
											(username, password, mail, api, secret, date.today(), 0))
										conn.commit()
									except mariadb.Error as e:
										print(f"Error: {e}")
									print('Аккаунт успешно создан!')
									print('Дата: ', str(date.today()))
									print(username, ':', password, ':', mail)
									print('API: ', str(api), ' Secret: ', secret)
									t = 61
									break
							else:
								#print('Упс, что-то пошло не так!')
								time.sleep(0.1)
								continue
					t += 1
				print('Очистка кукисов')
				driver.delete_all_cookies()
				time.sleep(2)
				print('Закрываю браузер...')
				driver.close()
				return
	except Exception as ex:
		exs = ex.args
		template = "An exception of type {0} occurred. Arguments:\n{1!r}"
		message = template.format(type(ex).__name__, ex.args)
		print(message)
		print('Error. Trying again...', Exception)
		driver.close()
		time.sleep(20)
		createAccount(username, password)
		return


a = input("Сколько аккаунтов зарегистрировать?(Только INTEGER)")
def main():

	times = int(a)
	for i in range(times):
		username, password = generateUser()
		createAccount(username, password)
		# print('Регистрация номер: ', i+1)
		time.sleep(2)

if __name__ == '__main__':
	main()

