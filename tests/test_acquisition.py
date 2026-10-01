import unittest
from src.acquire import validate
from src.extract_ncs import object_literal,extract

class AcquisitionTests(unittest.TestCase):
    def test_html_is_not_pdf_or_csv(self):
        for kind in ('pdf','csv','xlsx'):
            with self.subTest(kind=kind),self.assertRaises(ValueError):
                validate(b'<!DOCTYPE html><html>Login</html>',kind)

    def test_parse_literal_without_evaluation(self):
        result=object_literal('this.allTabData={"Vacancies":{rows:[{state:"Pune",values:[1],total:1}],grandTotal:{label:"Total",values:[1],total:1}}},next=0','this.allTabData=')
        self.assertEqual(result['Vacancies']['rows'][0]['total'],1)

    def test_executable_literal_is_rejected(self):
        with self.assertRaises(ValueError):
            object_literal('data={rows:alert("execute")}', 'data=')

    def test_mismatched_html_is_rejected(self):
        html='<button class="tab-btn active">Vacancies</button><table><thead><th>STATE</th><th>2020-21</th><th>GRAND TOTAL</th></thead><tbody><tr><td>Pune</td><td>8</td><td>8</td></tr></tbody></table>'
        bundle='this.allColumns=["2020-21"];this.allTabData={"Vacancies":{rows:[{state:"Pune",values:[1],total:1}],grandTotal:{label:"Total",values:[1],total:1}}}'
        with self.assertRaises(ValueError):extract(html,bundle)

if __name__=='__main__':unittest.main()
