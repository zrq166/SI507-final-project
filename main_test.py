import unittest
from main import *

class TestDatabase(unittest.TestCase):

    def test_tv_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT TvName FROM TV'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Titans',), result_list)
        self.assertEqual(len(result_list), 200)

        sql = '''
            SELECT TvName, Rating FROM TV WHERE DateMonth=8 ORDER BY Popularity
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        #print(result_list)
        self.assertEqual(len(result_list), 11)
        self.assertEqual(result_list[1][1], 7.4)

        conn.close()

    def test_country_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT CountryName
            FROM Country
            WHERE Area>=300000
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Angola',), result_list)
        self.assertEqual(len(result_list), 73)

        sql = '''
            SELECT COUNT(*)
            FROM Country
        '''
        results = cur.execute(sql)
        count = results.fetchone()[0]
        self.assertTrue(count == 240)
        conn.close()

    def test_joins(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
               SELECT c.CountryCode, t.Popularity FROM TV AS t 
                        LEFT JOIN Country AS c
                        ON t.CountryId = c.Id
                        WHERE t.Rating>8
           '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(result_list[0][1],47.994)
        self.assertEqual(result_list[6][0], "US")
        self.assertEqual(len(result_list), 38)
        conn.close()

class TestTvSearch(unittest.TestCase):

    def test_tv_search1(self):
        results = process_command('tv popularity and rating top=10')
        self.assertEqual(results[0][0], 'Black Lightning')
        self.assertEqual(results[4][2], 7.3)

        results = process_command('tv popularity and rating bottom=20')
        self.assertEqual(results[2][0], 'Still 17')
        self.assertEqual(results[0][2], 8.1)

    def test_tv_search2(self):
        results = process_command('tv country and rating')
        self.assertEqual(len(results), 23)

    def test_tv_search3(self):
        results = process_command('tv #released per month')
        self.assertEqual(results[0][1], 27)

    def test_tv_search4(self):
        results = process_command('tv ratings and month')
        self.assertEqual(results[2][1], 6.6)
        self.assertEqual(results[4][1], 7.0)

unittest.main()