from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import json
import pandas as pd
import os
from time import sleep
from random import randint

with open('District-Block_dictionary.json') as jsonfile:
	district_dict = json.load(jsonfile)

with open('Block-Panchayat_dictionary.json') as jsonfile:
	block_dict = json.load(jsonfile)


def district_extractor():
	options = webdriver.ChromeOptions()
	options.add_argument('headless')
	options.add_argument('window-size=1200x600')

	driver = webdriver.Chrome(options=options)
	url = 'https://rhreporting.nic.in/netiay/PhysicalProgressReport/physicalprogressreport.aspx'
	driver.get(url)

	element1 = WebDriverWait(driver, 10).until(
		EC.presence_of_element_located((By.XPATH, '//*[@id="ContentPlaceHolder1_ddlState"]')))
	dropdown1 = Select(driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_ddlState"]'))
	dropdown1.select_by_visible_text('JHARKHAND')

	district = str.upper(input('Enter name of district: '))

	if district in district_dict.keys():
		element2 = WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.XPATH, '//*[@id="ContentPlaceHolder1_ddlDistrict"]')))
		dropdown2 = Select(driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_ddlDistrict"]'))
		dropdown2.select_by_visible_text(district)

		for value in district_dict[district]:
			print('Downloading from {} block'.format(value))
			element3 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
				(By.XPATH, '//*[@id="ContentPlaceHolder1_ddlBlock"]')))
			dropdown3 = Select(driver.find_element_by_xpath(
				'//*[@id="ContentPlaceHolder1_ddlBlock"]'))
			dropdown3.select_by_visible_text(value)

			new_key = value
			for new_value in block_dict[new_key]:
				print('--> {}'.format(new_value))
				element4 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
					(By.XPATH, '//*[@id="ContentPlaceHolder1_ddlPanchayat"]')))
				dropdown4 = Select(driver.find_element_by_xpath(
					'//*[@id="ContentPlaceHolder1_ddlPanchayat"]'))
				dropdown4.select_by_visible_text(new_value)
				element5 = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
					(By.XPATH, '//*[@id="ContentPlaceHolder1_btnSubmit"]')))
				actions = ActionChains(driver)
				actions.move_to_element(element5).click().perform()

				try:
					element6 = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
						(By.XPATH, '//*[@id="ContentPlaceHolder1_gvData"]')))
					table = driver.find_element_by_xpath(
						'//*[@id="ContentPlaceHolder1_gvData"]')
					rows = table.find_elements_by_tag_name('tr')
					rows.pop(0)

					data = []

					for row in rows:
						# print(row.text)
						cells = row.find_elements_by_tag_name('td')
						sl_no = cells[0].text
						village = cells[1].text
						reg_no = cells[2].text
						benf_name = cells[3].text
						f_m_name = cells[4].text
						h_alloted_to = cells[5].text
						sanc_no = cells[6].text
						sanc_amt = cells[7].text
						inst_paid = cells[8].text
						amt_rlsd = cells[9].text
						house_stat = cells[10].text

						data.append([sl_no, village, reg_no, benf_name, f_m_name, h_alloted_to, sanc_no,
						             sanc_amt, inst_paid, amt_rlsd, house_stat])

						df = pd.DataFrame(data=data,
						                  columns=['Sl_No', 'Village', 'Reg_No', 'Beneficiary_name',
						                           'Fathers/Mothers Name', 'House_Alloted_To',
						                           'Sanction_No', 'Sanction_Amount', 'Installment_Paid',
						                           'Amount_Released', 'House_Status'])

						if not os.path.exists('data\{}'.format(value)):
							os.makedirs('data\{}'.format(value))

						df.to_excel('data\{}\{}_{}.xlsx'.format(value, value, new_value))

				except TimeoutException as ex:
					print('-----> Data not found')

				finally:
					sleep(randint(1, 10))
					dropdown4 = Select(driver.find_element_by_xpath(
						'//*[@id="ContentPlaceHolder1_ddlPanchayat"]'))
	else:
		print("District name not found. Please try again")
		district_extractor()


def main():
	district_extractor()


if __name__ == '__main__':
	main()
