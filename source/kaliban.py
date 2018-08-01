import requests
import re
import json


class Kaliban:
    def __init__(self, args):
        self.url = args.url
        self.out = args.out
        self.input_file = args.input_file
        user_agent = args.user_agent if args.user_agent \
            else 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0'
        self.request_headers = {'User-Agent': user_agent,
                                'Accept': 'text / html, application / xhtml + xml, application / xml;q = 0.9, * / *;q = 0.8',
                                'Accept-Language': 'en-US, en;q = 0.5'}
        if args.proxy:
            self.proxies = {
                'http': 'http://' + args.proxy,
                'https': 'http://' + args.proxy,
            }
        else:
            self.proxies = False
        self.sub_on = False
        if args.sub_on:
            self.sub_on = True
        self.int_on = False
        if args.int_on:
            self.int_on = True
        self.title = None
        self.generator = None
        self.text = None
        self.response_headers = None
        self.server = None
        self.scan_url = None
        self.interesting = []
        self.subdomain = []
        self.data = {'interesting': 'data/interesting.json', 'subdomain': 'data/subdomain.json'}

    def start(self):
        if self.url:
            self.request_url(self.url)
        else:
            fin = open(self.input_file)
            for url in fin:
                self.request_url(url.strip('\n'))

    def request_url(self, url):
        url = url.lower()
        if '://' not in url:
            url = 'http://' + url
        print("Start scan: " + url)
        self.scan_url = url
        try:
            response = requests.get(url, headers=self.request_headers, proxies=self.proxies, verify=False,
                                    allow_redirects=True, timeout=10)
        except Exception:
            print('exception')
            return 0
        self.response_headers = response.headers
        self.text = response.text
        if self.sub_on:
            self.find_subdomain()
        if self.int_on:
            self.find_interesting()
        self.analyze()
        self.write()
        self.clear()

    def find_subdomain(self):
        with open(self.data['subdomain'], 'r') as data_file:
            subdomain_list = json.load(data_file)
        for sub in subdomain_list:
            main_domain = self.scan_url.split('//')[1]
            main_domain = main_domain.replace('www.', '')
            new_url = 'http://' + sub['subdomain'] + '.' + main_domain
            try:
                response = requests.get(new_url, headers=self.request_headers, proxies=self.proxies,
                                        verify=False, allow_redirects=True, timeout=10)
            except Exception:
                continue
            if (response.status_code == 200) and (sub['subdomain'] in response.url):
                self.subdomain.append({sub['note']: new_url})

    def find_interesting(self):
        with open(self.data['interesting'], 'r') as data_file:
            interesting_list = json.load(data_file)
        for interesting in interesting_list:
            for ext in interesting['ext']:
                uri = interesting['url'] + '.' + ext
                try:
                    response = requests.get(self.scan_url + uri, headers=self.request_headers, proxies=self.proxies,
                                            verify=False, allow_redirects=True, timeout=10)
                except Exception:
                    continue
                if response.status_code == 200:
                    self.interesting.append({interesting['note']: uri})

    def analyze(self):
        try:
            self.server = self.response_headers['server']
        except KeyError:
            self.server = 'Undefined'
        try:
            self.title = re.findall(r'<title>\s*(.*)\s*</title>', self.text)[0]
        except IndexError:
            self.title = ''
        try:
            self.generator = re.findall(r'generator"\scontent="(.*)"\s/>', self.text)[0]
        except IndexError:
            self.generator = ''

    def write(self):
        fout = open(self.out, 'a')
        report = json.dumps({'url': self.scan_url, 'server': self.server, 'title': self.title,
                             'cms': self.generator, 'interesting': self.interesting, 'subdomain': self.subdomain},
                            indent=4, sort_keys=True)
        fout.write(report)
        fout.close()

    def clear(self):
        self.title = None
        self.generator = None
        self.text = None
        self.response_headers = None
        self.server = None
        self.scan_url = None
        self.interesting = []
        self.subdomain = []
