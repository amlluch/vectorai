from django.test import TestCase

# Create your tests here.
from .utils import Ocr, ResponseException
from restapi.models import Country
import datetime

class UtilsTestCase(TestCase):
    def setUp(self):
        Country.objects.create(name='Nuew zealand', code3='NZL', code2='NZ', number='21')
        Country.objects.create(name='Sweeden', code3='SWE', code2='SW', number='22')
        Country.objects.create(name='CROATIA', code3='HRV', code2='HR', number='23')
    
    def test_calc(self):
        ocr = Ocr()

        self.assertEqual(ocr._calc('650603'),2)
        self.assertEqual(ocr._calc('BE511346<'),3)
        self.assertEqual(ocr._calc('AAG520991'),8)

        self.assertEqual(ocr._date('650603')[0:4], '1965')
        self.assertEqual(ocr._date('650603')[5:7], '06')
        self.assertEqual(ocr._date('220815')[0:4], '2022')

        file_path = 'media/images/tests/SWEpassportdatapage.png'
        ocr2 = Ocr(file_path)
        serialized = ocr2.check_passport()

        noerrors = []
        line1 = 'P>ESPXXXXXXX'
        noerror = 'AAG5209918ESP6506032M2212175A2539533300<<<<70'
        self.assertEqual(ocr._get_errors_passport(line1, noerror), noerrors)

        line1 = 'P>OSP'
        numbererror = 'AAG4209918ESP6506032M2212175A2539533300<<<<70'
        numbererrors = []
        numbererrors.append('nationality')
        numbererrors.append('number')
        self.assertEqual(ocr._get_errors_passport(line1, numbererror), numbererrors)

        line1 = 'P>OSP'
        allerror = 'AAG4209918ESP6507032M2211175A2539533300<<<<70'
        allerrors = []
        allerrors.append('nationality')
        allerrors.append('number')
        allerrors.append('birth_date')
        allerrors.append('exp_date')
        self.assertEqual(ocr._get_errors_passport(line1, allerror), allerrors)

        number = 'AAG520991'
        nationality = 'ESP'
        birth_date = '1965-06-03'
        exp_date = '2022-12-17'
        self.assertEqual(ocr._get_second_line(noerror), (number, nationality, birth_date,'M', exp_date))

        file_path = 'media/images/tests/nzpassport-sample.png'
#        file_path = 'media/images/tests/SWEpassportdatapage.png'
        result = ocr._get_string(file_path)
        sexerrors = []
#        sexerrors.append('sex')
        try:
            line1, line2 = ocr._get_passport(result)
            self.assertEqual(ocr._get_errors_passport(line1, line2), sexerrors)

        except ResponseException as err:
            print (result)
            print (err)

        country = 'Nuew zealand'
        surname = 'WHAKAATURANGAC FRED WIRERU JONNE'
        name = 'ccce'
        self.assertEqual(ocr._get_first_line(line1), (country, surname, name))

        file_path = 'media/images/tests/Croatian_passport_data_page.jpg'
        result = ocr._get_string(file_path)
        line1, line2 = ocr._get_passport(result)
        country = 'CROATIA'
        surname = 'SPECIMEN'
        name = 'SPECIMEN K KKKKKK'
        self.assertEqual(ocr._get_first_line(line1), (country, surname, name))
        
