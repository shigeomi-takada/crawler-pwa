# coding: utf-8

from app import app
from app.mysql.connect import Connect


class Urls():
    '''
    This class is need to be called with context manager
    e.g.
    with Urls() as u:
        is_exist = tu.is_exist('https://www.example.com')
    if is_exist:
        pass
    '''

    def __init__(self, role='master'):
        self.role = role

    def __enter__(self):
        self.con = Connect(role=self.role)
        self.m = self.con.open()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        '''
        意図的にcloseしないとすぐこのエラーが発生する。
        ReferenceError: weakly-referenced object no longer exists
        '''
        if exc_type is None:
            self.con.close()
        else:
            app.logger.warning('Urls mysql connection closing is failed')
            return False

    def add(self, urls):
        '''
        :param tuple urls
        :return int ID was inserted
        '''

        query = ('''
            INSERT INTO urls (
                datetime,
                scheme,
                netloc,
                path,
                pwa,
                urls_external
            ) VALUES (
                %s, %s, %s, %s, %s, %s)
        ''')

        params = (
            urls['datetime'],
            urls['scheme'],
            urls['netloc'],
            urls['path'],
            urls['pwa'],
            urls['urls_external'],)

        self.m.execute(query, params)
        self.con.commit()
        return self.m.lastrowid

    def is_exist(self, netloc):
        '''
        同じnetlocがすでに保存済みかチェックする
        存在しなければ0,存在すれば1を返す
        :param str netloc
        :return int
        '''
        query = '''
            SELECT
            Url.id
            FROM urls AS Url
            WHERE
            Url.netloc = %s
        '''

        self.m.execute(query, (netloc,))
        self.m.fetchone()
        return self.m.rowcount

    def is_exist_strictly(self, netloc, path):
        '''
        同じnetlocがすでに保存済みかチェックする
        存在しなければ0,存在すれば1を返す
        :param str netloc
        :return int
        '''
        if path is None:
            path = ''

        query = '''
            SELECT
            Url.id
            FROM urls AS Url
            WHERE
            Url.netloc = %s AND
            Url.path = %s
        '''

        self.m.execute(query, (netloc, path,))
        self.m.fetchone()
        return self.m.rowcount
