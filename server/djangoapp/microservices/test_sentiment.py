import unittest
from app import app
class SentimentTests(unittest.TestCase):
    def test_sentiments(self):
        client=app.test_client()
        for text,expected in [('Fantastic services','positive'),('Awful terrible service','negative'),('The car is blue','neutral')]:
            with self.subTest(text=text):
                response=client.get('/analyze/'+text)
                self.assertEqual(response.status_code,200)
                self.assertEqual(response.json['sentiment'],expected)
if __name__=='__main__': unittest.main()
