from rest_framework import status
from .models import Country

import cv2
import pytesseract
import datetime

class ResponseException(Exception):
    def __init__(self, message, status):
        self.message = message
        self.status = status


class Ocr():

    def __init__(self, file_path = None):
        self.file_path = file_path

# Perform password check as indicated here: https://en.wikipedia.org/wiki/Machine-readable_passport
    def _calc(self, data):
        digit_weight = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        pos_weight = '731'
        data = data.upper()
        value = 0
        for i in range(len(data)):
            digitw = digit_weight.find(data[i])
            if digitw < 0:
                digitw = 0
            posw = int(pos_weight[(i+1)%3-1])
            value += digitw*posw
 
        return value%10

 # format given YY/MM/dd.    
    def _date(self, passport_date):
        ndate = passport_date[0:2]
        yearn = datetime.datetime.now().year
        cort = yearn%100 + 15 # Higher than 34 is 20 century
        try:   
            if int(ndate)>cort:
                ndate = '19' + ndate
            else:
                ndate = '20' + ndate
        except:     # No date
            return ''
        ndate += '-' + passport_date[2:4] + '-' + passport_date[4:6]
        try:
            time = datetime.datetime.strptime(ndate, '%Y-%m-%d')
        except:
            time = datetime.datetime.strptime('1850-1-1','%Y-%m-%d')
        return time.strftime("%Y-%m-%d")

# No image pre-processing. Tesseract is doing well so far
    def _get_string(self, img_path):
        try:
            img = cv2.imread(img_path)
        except:
            raise ResponseException ('No image provided', status.HTTP_400_BAD_REQUEST)
        config = ('-l eng --oem 1 --psm 3') 
        try:
            result = pytesseract.image_to_string(img, config = config)
        except:
            raise ResponseException ('Error on image', status.HTTP_400_BAD_REQUEST)
        return result
# gets the raw document info. If is not a passport raises an error
# If is a passport return data lines
    def _get_passport(self, rawdata):
        rawdata = rawdata.strip()
        resmat = []
        ind = 0
        success = -1
        for line in rawdata.splitlines():
            line_check = line.replace(' ', '')
            resmat.append(line_check)
            if line_check[0:1] == 'P':  # string candidate
                ccode = line_check[2:5]
                country = Country.objects.filter(code3 = ccode)
                if len(country) != 0: # P + country code ==> success
                    success = ind   # We found first data line
            ind +=1
        if (success < 0):
            raise ResponseException ('No passport provided', status.HTTP_400_BAD_REQUEST)
        
        return resmat[success], resmat[success + 1]

#Processes passport first line
    def _get_first_line(self, rawdata):
        country_code = rawdata[2:5]
        try:
            country = Country.objects.get(code3=country_code)
            country_name = country.name
        except :
            country_name = 'No country'
        first_dist = rawdata[5:].find('<<') + 5
        surname = rawdata[5: first_dist].replace('<', ' ').strip()
        name = rawdata[first_dist:].replace('<', ' ')
        name = " ".join(name.split())
        surname = " ".join(surname.split())
        return country_name, surname, name
        
#Processes passport second line
    def _get_second_line(self, rawdata):
        number = rawdata[0:9]
        nationality = rawdata[10:13]
        birth_date = self._date(rawdata[13:19])
        sex = rawdata[20:21]
        exp_date = self._date(rawdata[21:27])
        return number, nationality, birth_date, sex, exp_date

# List of fields with error processing data from OCR
# all checking is on second line
    def _get_errors_passport(self, line1, line2):
        errors = []
        if line1[2:5]!=line2[10:13]:    #if doesn't match in both lines
            errors.append('nationality')
        if line2[20:21] not in ['M', 'F']:
            errors.append('sex')
        try:        # If everything is ok, no further errors
            if self._calc(line2[0:9] + line2[13:19] + line2[21:42]) == int(line2[43:44]) and line2[20:21] in ['M', 'F']:
                return errors
        except:   #No Numbers inside
            pass
        try:
            if self._calc(line2[0:9]) != int(line2[9:10]):
                errors.append('number')
        except:     #No number for checking
            errors.append('number')
        try:
            if self._calc(line2[13:19]) != int(line2[19:20]):
                errors.append('birth_date')
        except:     #No number for checking
            errors.append('birth_date')
        try:
            if self._calc(line2[21:27]) != int(line2[27:28]):
                errors.append('exp_date')
        except:     #No number for checking
            errors.append('exp_date')
        
        return errors

    # the whole passport recognition process here.
    def check_passport(self, file_path = None):
        # you can pass the file when creating the class or in this method.
        if file_path:
            self.file_path = file_path

        if not self.file_path:
            raise ResponseException ('No image provided', status.HTTP_400_BAD_REQUEST)
        rawdata = self._get_string(self.file_path)
        line1, line2 =self._get_passport(rawdata)
        extracted_data = dict()
        country, surname, name = self._get_first_line(line1)
        extracted_data['country'] = country
        extracted_data['name'] = name
        extracted_data['surname'] = surname
        number, nationality, birth_date, sex, exp_date = self._get_second_line(line2)
        extracted_data['number'] = number
        extracted_data['nationality'] = nationality
        extracted_data['birth_date'] = birth_date
        extracted_data['exp_date'] = exp_date
        extracted_data['sex'] = sex
        extracted_data['errors'] = self._get_errors_passport(line1, line2)
        return extracted_data
