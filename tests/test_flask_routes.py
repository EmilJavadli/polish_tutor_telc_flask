import os
os.environ['DEV_LOGIN']='1'
os.environ['DATABASE_URL']='sqlite:///:memory:'
import unittest
from app import app
class FlaskRoutes(unittest.TestCase):
 def setUp(self):self.client=app.test_client()
 def test_login_page(self):self.assertEqual(self.client.get('/').status_code,200)
 def test_dev_login_and_placement(self):
  response=self.client.get('/auth/dev-login',follow_redirects=True)
  self.assertEqual(response.status_code,200)
  self.assertIn(b'Polish CEFR placement',response.data)
if __name__=='__main__':unittest.main()
