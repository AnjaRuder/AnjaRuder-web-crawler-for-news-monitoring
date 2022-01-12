# -*- coding: utf-8 -*-
"""
Created on Sun Nov 28 12:49:50 2021

@author: anja_
"""

#%% Code from The New Boston

from urllib.parse import urlparse


# Get domain name (example.com)
def get_domain_name(url):
    try:
        results = get_sub_domain_name(url).split('.')
        return results[-2] + '.' + results[-1]
    except:
        return ''


# Get sub domain name (name.example.com)
def get_sub_domain_name(url):
    try:
        return urlparse(url).netloc
    except:
        return ''
    
import os 
# Each website is a separate project (folder)
def create_project_dir(directory):
    if not os.path.exists(directory):
        print('Creating directory ' + directory)
        os.makedirs(directory)


# Create queue and crawled files (if not created)
def create_data_files(project_name, base_url):
    queue = os.path.join(project_name , 'queue.txt')
    crawled = os.path.join(project_name,"crawled.txt")
    findings = os.path.join(project_name, "findings.txt")    # Added line
    findings_send = os.path.join(project_name, "findings_send.txt")
    crawled_done = os.path.join(project_name, "crawled_done.txt")
    if not os.path.isfile(queue):
        write_file(queue, base_url)
    if not os.path.isfile(crawled):
        write_file(crawled, '')
    if not os.path.isfile(findings): # Added line
        write_file(findings, '')
    if not os.path.isfile(findings_send): # Added line
        write_file(findings_send, '')
    if not os.path.isfile(crawled_done): # Added line
        write_file(crawled_done, '')

# Create a new file
def write_file(path, data):
    with open(path, 'w') as f:
        f.write(data)


# Add data onto an existing file
def append_to_file(path, data):
    with open(path, 'a') as file:
        file.write(data + '\n')


# Delete the contents of a file
def delete_file_contents(path):
    open(path, 'w').close()


# Read a file and convert each line to set items
def file_to_set(file_name):
    results = set()
    with open(file_name, 'rt', encoding=('cp1252')) as f:
        for line in f:
            results.add(line.replace('\n', ''))
    return results


# Iterate through a set, each item will be a line in a file
def set_to_file(links, file_name):
    with open(file_name,"w") as f:
        for l in sorted(links):
            f.write(l+"\n")
            

from urllib.request import urlopen
from html.parser import HTMLParser
from urllib import parse

class LinkFinder(HTMLParser):

    def __init__(self, base_url, page_url):
        super().__init__()
        self.base_url = base_url
        self.page_url = page_url
        self.links = set()

    # When we call HTMLParser feed() this function is called when it encounters an opening tag <a>
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for (attribute, value) in attrs:
                if attribute == 'href':
                    url = parse.urljoin(self.base_url, value)
                    self.links.add(url)

    def page_links(self):
        return self.links

    def error(self, message):
        pass

#%% Spider to use for the initial run to create folders for project and the initial crawl
# The New Bosten made the Spider, and I changed in it to make Spider2

class Spider:    
    
    #Class variables (shared among all instances)
    project_name = '' #let the user choose
    base_url = '' #the homepage url
    domain_name = '' #connected to a domain
    queue_file = ''
    crawled_file = ''
    findings_file = ''
    queue = set()
    crawled = set()


    def __init__(self, project_name, base_url, domain_name):
        Spider.project_name = project_name
        Spider.base_url = base_url
        Spider.domain_name = domain_name
        Spider.queue_file = Spider.project_name + '/queue.txt'
        Spider.crawled_file = Spider.project_name + '/crawled.txt'
        Spider.findings_file = Spider.project_name + '/findings.txt'
        self.boot()
        self.crawl_page('First spider', Spider.base_url)

    # Creates directory and files for project on first run and starts the spider
    @staticmethod
    def boot():
        create_project_dir(Spider.project_name)
        create_data_files(Spider.project_name, Spider.base_url)
        Spider.queue = file_to_set(Spider.queue_file)
        Spider.crawled = file_to_set(Spider.crawled_file)
        Spider.findings = file_to_set(Spider.findings_file) # Egen linje
        #Spider.findings_send = file_to_set(Spider.findings_send) # Egen linje

    # Updates user display, fills queue and updates files
    @staticmethod
    def crawl_page(thread_name, page_url):
        if page_url not in Spider.crawled:
            print(thread_name + ' now crawling ' + page_url)
            print('Queue ' + str(len(Spider.queue)) 
                  + ' | Crawled  ' + str(len(Spider.crawled)))
            Spider.add_links_to_queue(Spider.gather_links(page_url))
            Spider.queue.remove(page_url)
            Spider.crawled.add(page_url)
            Spider.update_files()

    # Converts raw response data into readable information and checks for proper html formatting
    @staticmethod
    def gather_links(page_url):
        html_string = ''
        try:
            response = urlopen(page_url)
            if 'text/html' in response.getheader('Content-Type'):
                html_bytes = response.read()
                html_string = html_bytes.decode("utf-8")
            finder = LinkFinder(Spider.base_url, page_url)
            finder.feed(html_string)
        except Exception as e:
            print(str(e))
            return set()
        return finder.page_links()
    
    # Saves queue data to project files
    @staticmethod
    def add_links_to_queue(links):
        for url in links:
            if (url in Spider.queue) or (url in Spider.crawled):
                continue
            if Spider.domain_name != get_domain_name(url):
                continue
            Spider.queue.add(url)


    @staticmethod
    def update_files():
        set_to_file(Spider.queue, Spider.queue_file)
        set_to_file(Spider.crawled, Spider.crawled_file)


#%% Spider2 are used after initial run. It doesn't create new folders.

class Spider2:
    #Class variables (shared among all instances)
    project_name = '' 
    base_url = ''
    domain_name = '' 
    queue_file = ''
    crawled_file = ''
    crawled_done = ''
    queue = set()
    crawled = set()
    
    def __init__(self, project_name, base_url, domain_name):
        Spider2.project_name = project_name
        Spider2.base_url = base_url
        Spider2.domain_name = domain_name
        Spider2.queue_file = Spider2.project_name + '/queue.txt'
        Spider2.crawled_file = Spider2.project_name + '/crawled.txt'
        Spider2.crawled_done = Spider2.project_name + '/crawled_done.txt'
        self.boot(Spider2.queue_file, Spider2.base_url)
        self.crawl_page('First spider', Spider2.base_url)


    #Creates directory and files for project on first run and starts the spider
    @staticmethod
    def boot(queue_file, base_url):
        write_file(queue_file, base_url)

    # Updates user display, fills queue and updates files
    @staticmethod
    def crawl_page(thread_name, page_url):
        if page_url not in Spider2.crawled: #Removed crawled_done part
            print(thread_name + ' now crawling ' + page_url)
            print('Queue ' + str(len(Spider2.queue)) 
                  + ' | Crawled  ' + str(len(Spider2.crawled)))
            Spider2.add_links_to_queue(Spider2.gather_links(page_url))
            #Spider2.queue.remove(page_url)
            Spider2.crawled.add(page_url)
            Spider2.update_files()


    # Converts raw response data into readable information and checks for proper html formatting
    @staticmethod
    def gather_links(page_url):
        html_string = ''
        try:
            response = urlopen(page_url)
            if 'text/html' in response.getheader('Content-Type'):
                html_bytes = response.read()
                html_string = html_bytes.decode("utf-8")
            finder = LinkFinder(Spider2.base_url, page_url)
            finder.feed(html_string)
        except Exception as e:
            print(str(e))
            return set()
            pass
        return finder.page_links()
    
    # Saves queue data to project files
    @staticmethod
    def add_links_to_queue(links):
        
        for url in links:
            #if (url in Spider2.queue) or (url in Spider2.crawled) or (url in Spider2.crawled_done):
                #continue
            if Spider2.domain_name != get_domain_name(url):
                continue
            with open(Spider2.queue_file, 'r') as qf: 
                if url in qf: 
                    qf.close()
                    continue 
            with open(Spider2.crawled_file, 'r') as cf: 
                if url in cf:
                    cf.close()
                    continue 
            # with open(Spider2.crawled_done, 'r') as cd: 
            #     if url in cd: 
            #         cd.close()
                    continue    

            Spider2.queue.add(url)


    @staticmethod
    def update_files():
        set_to_file(Spider2.queue, Spider2.queue_file)
        set_to_file(Spider2.crawled, Spider2.crawled_file)
        as_set = file_to_set(Spider2.crawled_done)
        set_to_file(as_set, Spider2.crawled_done) 
       
    project_name = '' #let the user choose
    base_url = '' #the homepage url
    domain_name = '' #connected to a domain
    queue_file = ''
    crawled_file = ''
    crawled_done = ''

def reset_Spider2():
    """
    This function makes the Spider2 function ready for the next crawl.
    Since it is a class object, the variables needs to be cleared, so it doesn't
    use anything from the last run, when doing the next'

    """
    Spider2.queue.clear()
    Spider2.crawled.clear()

#%% These functions activates the crawler. It makes spiders

import threading
from queue import Queue
import re
import urllib.request
from bs4 import BeautifulSoup


queue = Queue()
#Create worker threads (will die when main exits)
def create_workers(NUMBER_OF_THREADS):
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()
        
# Do the next job in the queue
def work():
    while True:
        url = queue.get()
        Spider.crawl_page(threading.current_thread().name, url)
        queue.task_done()

# 
def create_jobs(QUEUE_FILE):
    """
    Each queued link is a new job

    """
    for link in file_to_set(QUEUE_FILE):
        queue.put(link)
    queue.join()
    crawl()


def create_workers2(NUMBER_OF_THREADS):
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work2)
        t.daemon = True
        t.start()

# Do the next job in the queue
def work2():
    while True:
        url = queue.get()
        Spider2.crawl_page(threading.current_thread().name, url)
        queue.task_done()


def crawl(QUEUE_FILE):
    """
    Check if there are items in the queue, if so crawl them

    """
    queued_links = file_to_set(QUEUE_FILE)
    if len(queued_links) > 0:
        try:
            print(str(len(queued_links)) + ' links in the queue')
            create_jobs(QUEUE_FILE)
        except: 
            pass


#%% MY CODE

def sort_queue(PROJECT_NAME):
    """
    The functions checks if any element of the queue already has been crawled. 
    If yes, it removes that element from the queue.  

    """
    queue = open(PROJECT_NAME + '/queue.txt', 'r')
    crawled_done = open(PROJECT_NAME + '/crawled_done.txt', 'r')
    q_lines = queue.readlines()
    c_lines = crawled_done.readlines()
    queue.close()
    crawled_done.close()
    
    queue_lines = []
    for line in q_lines:
        queue_lines.append(line)
        for element in c_lines:
            if line.strip("\n") == element.strip("\n"):
                queue_lines.append(line)
               
    for x in set(queue_lines):
        if queue_lines.count(x) > 1: 
            while x in queue_lines:
                queue_lines.remove(x)
        if "#" in x or "?" in x:
            try: 
                queue_lines.remove(x)                    
            except: 
                pass
                
    queue = open(PROJECT_NAME + '/queue.txt', 'w')
    for line in queue_lines: 
        queue.write(line)
    queue.close()
    queue_lines = []
    return "Sorting of queue done."


def sort_crawled(PROJECT_NAME):
    """
    The functions checks if any element of crawled already has been crawled. 
    If yes, it removes that element from the file.   

    """
    crawled = open(PROJECT_NAME + '/crawled.txt', 'r')
    crawled_done = open(PROJECT_NAME + '/crawled_done.txt', 'r')
    c_lines = crawled.readlines()
    cd_lines = crawled_done.readlines()
    crawled.close()
    crawled_done.close()
    
    crawled_lines = []
    for line in c_lines:
        crawled_lines.append(line)
        for element in cd_lines:
            if line.strip("\n") == element.strip("\n"):
                crawled_lines.append(line)
               
    for x in set(crawled_lines):
        if crawled_lines.count(x) > 1: 
            while x in crawled_lines:
                crawled_lines.remove(x)                    
        if "#" in x or "?" in x:
            try: 
                crawled_lines.remove(x)                    
            except: 
                pass
        
    crawled = open(PROJECT_NAME + '/crawled.txt', 'w')
    for line in crawled_lines: 
        crawled.write(line)
    crawled.close()
    crawled_lines = []
    return "Sorting of crawled done."

#%% My code to scrape different kinds of websites

def find_main_text(link):
    """
    This function goes trough different kinds of HTML, and can take the code from
    different websites. It is specified to the websites the web crawler is looking
    at. This should eventually be updates, it there are too many 'false positive',
    which are relevant stories not being found. Then the HTML might have changed.

    """
    html = urllib.request.urlopen(link).read().decode()
    soup = BeautifulSoup(html, 'html.parser')
    text1 = soup.find('div', {'id':'articleMain'}) #adweek
    text2 = soup.find('div', {'class':'container debug-outline'})
    text3 = soup.find('article', {'id':'content'})
    text4 = soup.find('div', {'id':'content'}) #kampanje
    text5 = soup.find('div', {'class':'gatedArticle_heading'})
    text6 = soup.find('div', {'class':'article'}) #the drum
    text7 = soup.find('div', {'class':'post'}) #shots
    text8 = soup.find('div', {'class':'sidebar_content'}) #the stable
    text9 = soup.find('article', {'class':'css-2j58n8 efcsxjh2'}) #resume
    text10 = soup.find('div', {'class':'css-ri1yd5 eyxrd291'})
    if text1 != None:
        text = text1.getText()
    elif text2 != None:
        text = text2.getText()
    elif text3 != None:
        text = text3.getText()
    elif text4 != None:
        text = text4.getText()
    elif text5 != None:
        text = text5.getText()
    elif text6 != None:
        text = text6.getText()
    elif text7 != None:
        text = text7.getText()
    elif text8 != None:
        text = text8.getText()
    elif text9 != None:
        text = text9.getText()
    elif text10 != None:
        text = text10.getText()
    else: 
        text = "Couldn't find text from soup"
    return text
    

#%% Functions, which makes the crawler add findings to the right folders, and move the remaining links

def add_to_findings(PROJECT_NAME, encoding = 'cp1252'):
    """
    This functions goes through the list of crawled websites to see if any of 
    the relevant search words are in it. If at least one of them are, it will
    add the link to the folder findings.

    """
    SEARCH_WORDS = [" Dansk","Danish", "danska", "Danmark", "Denmark", "Scandinavia", 
                    "Nordic ", "Copenhagen", "Carlsberg", "Lego", " Arla", " Ørsted", "Jysk", 
                    "Grundfos", "Mærsk", "Maersk", "Salling", "Danish Crown", "Velux", "Tivoli", 
                    "Danske Bank", "Matas", "&co. ", "NoA ", "Kunde & Co", 
                    "Robert/Boisen & Like-minded", "Hjaltelin Stahl", 
                    "Wibroe, Duckert & Partners", "Nord DDB", "Envision", "Nordlid", 
                    "Uncle Grey", "Advice", "ZUPA ", "ORCHESTRA ", "Mindshare", 
                    "mediacom", "Wavemaker", " OMD ", "PHD Danmark"]
    for i in range(len(SEARCH_WORDS)):
        SEARCH_WORDS[i] = SEARCH_WORDS[i].lower()
    websites = PROJECT_NAME + '/crawled.txt'
    findings_send = PROJECT_NAME + '/findings_send.txt'
    with open(websites, 'r',encoding=encoding, errors='ignore') as f:
        lines = f.readlines()   
        for link in lines: 
            if link in open(findings_send, 'r'): 
                pass
            else: 
                try:               
                    #page = urllib.request.urlopen(link).read()
                    main = find_main_text(link)
                    main = main.lower()
                    main = re.sub('[()@\':\n!,]','', main)
                    if "page not found" in main: 
                        continue
                    lenght = (len(main.split(' ')))
                    if lenght < 50:
                        continue
                    res = [w for w in SEARCH_WORDS if(w in main)]
                    if res == ['advice'] or res==['envision'] or res==[' omd ']:
                        continue
                    if res==['wavemaker'] or res==['mediacom']:
                        continue
                    if 'advice' in res:
                        if "denmark" not in res or "danish" not in res or 'dansk' not in res or 'danmark' not in res or 'danska' not in res: 
                            res.remove('advice')
                    #print(res)
                    if bool(res) == True:
                        print(res)
                        with open((PROJECT_NAME + '/findings.txt'), 'a') as file:
                            file.write(link)
                            file.close()
                            print('Link added to findings: '+link+' ')
                except: 
                    continue  

def move_to_done(CRAWLED_FILE, CRAWLED_DONE):
    """
    This function moves all the files from crawled.txt to crawled done.txt. 
    The purpose is to have a folder with the history and the new unseen links.

    Parameters
    ----------
    CRAWLED_FILE : Shortcut to crawled.txt
    CRAWLED_DONE : Shortcut to crawled_done.txt

    Returns
    -------
    None.

    """
    f1 = open(CRAWLED_FILE, 'r')
    f2 = open(CRAWLED_DONE, 'a')

    cont = f1.readlines()
    type(cont)
    for i in range(0, len(cont)):
        f2.write(cont[i])
    f2.close() # close the file
    f1.close()
    open(CRAWLED_FILE, "w").close()
    
    as_set = file_to_set(CRAWLED_DONE)
    set_to_file(as_set, CRAWLED_DONE)    

def move_to_crawled(QUEUE_FILE, CRAWLED_FILE):
    """
    Takes the leftover from QUEUE and moved to crawled

    """
    f1 = open(QUEUE_FILE, 'r')
    f2 = open(CRAWLED_FILE, 'a')

    cont = f1.readlines()
    type(cont)
    for i in range(0, len(cont)):
        f2.write(cont[i])
    f2.close() # close the file
    f1.close()
    open(QUEUE_FILE, "w").close()
    
    as_set = file_to_set(CRAWLED_FILE)
    set_to_file(as_set, CRAWLED_FILE)  
        
def move_to_send(FINDINGS_FILE, FINDINGS_SEND):
    """
    When the findings are send in an email, this function will move the links
    to findings_send.txt

    """
    f1 = open(FINDINGS_FILE, 'r')
    f2 = open(FINDINGS_SEND, 'a')

    cont = f1.readlines()
    type(cont)
    for i in range(0, len(cont)):
        f2.write(cont[i])
    f2.close() 
    f1.close()
    open(FINDINGS_FILE, "w").close()
    
    as_set = file_to_set(FINDINGS_SEND)
    set_to_file(as_set, FINDINGS_SEND)
    
#%% These functions creates the content and sends the email

SEARCH_WORDS = [" Dansk","Danish", "danska", "Danmark", "Denmark", "Scandinavia", 
                "Nordic ", "Copenhagen", "Carlsberg", "Lego", " Arla", " Ørsted", "Jysk", 
                "Grundfos", "Mærsk", "Maersk", "Salling", "Danish Crown", "Velux", "Tivoli", 
                "Danske Bank", "Matas", "&co. ", "NoA ", "Kunde & Co", 
                "Robert/Boisen & Like-minded", "Hjaltelin Stahl", 
                "Wibroe, Duckert & Partners", "Nord DDB", "Envision", "Nordlid", 
                "Uncle Grey", "Advice", "ZUPA ", "ORCHESTRA ", "Mindshare", 
                "mediacom", "Wavemaker", " OMD ", "PHD Danmark"]
SEARCH_WORDS_SINGLE = ["Dansk", "Danish", "danska", "Danmark", "Denmark",  "Scandinavia",
                "Carlsberg", "Lego", "Arla", "Ørsted", "Jysk", 
                "Nordic", "Grundfos", "Mærsk", "Maersk", "Salling", "Danish", "Crown", "Velux", "Tivoli", 
                "Danske", "Bank", "Matas", " &co.", "NoA", "Kunde", "Co", 
                "Robert/Boisen", "Like-minded", "Hjaltelin", "Stahl", 
                "Wibroe", "Duckert", "Partners", "Nord", "DDB", "Envision", "Nordlid", 
                "Uncle", "Grey", "Advice", "ZUPA", "ORCHESTRA", "Mindshare", 
                "mediacom", "Wavemaker", "OMD", "PHD", "Danmark"]


def to_string(lists):
    for element in lists:
        print("".join(element))

def mail_content(PROJECT_NAME):
    for i in range(len(SEARCH_WORDS)):
        SEARCH_WORDS[i] = SEARCH_WORDS[i].lower()
    for i in range(len(SEARCH_WORDS_SINGLE)):
        SEARCH_WORDS_SINGLE[i] = SEARCH_WORDS_SINGLE[i].lower()
    websites = PROJECT_NAME + '/findings.txt'
    mail_indhold = ['\n', PROJECT_NAME, "\n"]
    with open(websites, 'r',encoding='cp1252',errors='ignore') as f:
        lines = f.readlines()   
        for link in lines: 
            try: 
                main = find_main_text(link)
                main = main.lower()
                main = re.sub('[\'\n:!]','', main)
                res = [w for w in SEARCH_WORDS if(w in main)]
                x = main.find(res[0])

                main = main.strip().split(' ')
                counter = {}
                for words in SEARCH_WORDS_SINGLE:
                    for word in main:
                        if words == word:
                            if words not in counter: 
                                counter[words] = 1
                            else:
                                counter[words] += 1        

                main = find_main_text(link)
                main = re.sub('\n','', main)
                main = " ".join(main.split())
                if x < 500:
                    period = main.find('.', 1, 500)
                    period_end = main.rfind('.', x, 1000)
                    line = main[period+1:period_end+1]
                elif x >= 500 and x < 1000:
                    period = main.find('.', x-500, 1000)
                    period_end = main.rfind('.', x, x+500)
                    line = main[period+1:period_end+1]
                else:
                    period = main.find('.', x-500, x)
                    period_end = main.rfind('.', x, x+600)
                    line = main[period+1:period_end+1]
                text = ("\nLink: "+link+
                        "Søgeord fundet:"+str(res)+ ' \n'+
                        "Antallet af enkelte ord fundet: "+str(counter)+
                        "\nTekst uddrag: \n'"+line+"'\n")
                mail_indhold.append(text)
            except: 
                continue
            mail_indhold.append("\n")
        if (len(mail_indhold)) == 3:
            mail_indhold.append('Der blev ikke fundet nogen relevante links.\n')
         
    return (' '.join(mail_indhold))


def more_mail_content(project_names):
    mail_indhold = []
    for names in project_names:
        mail_indhold.append(mail_content(names))
    return (' '.join(mail_indhold))


def notification_email(project_names):

    import smtplib
    from email.message import EmailMessage
    import datetime
    now = datetime.datetime.now()
    #print (now.strftime("%d-%m-%Y %H:%M:%S"))
    
    text_from_list = (more_mail_content(project_names))
    
    message = EmailMessage()
    
    message.set_content(str(("WebCrawleren har d."+now.strftime("%d-%m-%Y %H:%M:%S")+" fundet disse links: \n"))
                    + text_from_list)
    
    
    message['Subject'] = ("International webcrawler update "+now.strftime("%d-%m-%Y"))
    message['From'] = "sender@email.com" #Here you need to write the mail of the sender 
    message['To'] = ["reciever@mail.com", "another_reciever@mail.co,"] #If there are more recievers of the mail, it should be in a list like this
    
    # Password from text file (placer password.txt i samme mappe som .py)
    with open('password.txt','r') as f:
        password = f.read()
    
    # Send the message via our own SMTP server.
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login("python.arc2021@gmail.com", password)
    server.send_message(message)
    server.quit()

#%% These functions sums up the other functions in the correct order they need to be activated in

def webcrawler_first(PROJECT_NAME, HOMEPAGE):
    DOMAIN_NAME = get_domain_name(HOMEPAGE)
    QUEUE_FILE = PROJECT_NAME + '/queue.txt'
    CRAWLED_FILE = PROJECT_NAME + '/crawled.txt'
    CRAWLED_DONE = PROJECT_NAME + '/crawled_done.txt'
    FINDINGS_FILE = PROJECT_NAME + '/findings.txt'
    FINDINGS_SEND = PROJECT_NAME + '/findings_send.txt'
    
    queue = Queue()
    Spider(PROJECT_NAME, HOMEPAGE, DOMAIN_NAME)

    create_workers(NUMBER_OF_THREADS = 8 )
    crawl(QUEUE_FILE)
    
    move_to_crawled(QUEUE_FILE, CRAWLED_FILE)
    move_to_done(CRAWLED_FILE, CRAWLED_DONE)
    
    return PROJECT_NAME + " er nu klar til webcrawling."


def webcrawler_second(PROJECT_NAME, HOMEPAGE, encoding):
    reset_Spider2()
    DOMAIN_NAME = get_domain_name(HOMEPAGE)
    QUEUE_FILE = PROJECT_NAME + '/queue.txt'
    CRAWLED_FILE = PROJECT_NAME + '/crawled.txt'
    CRAWLED_DONE = PROJECT_NAME + '/crawled_done.txt'
    FINDINGS_FILE = PROJECT_NAME + '/findings.txt'
    FINDINGS_SEND = PROJECT_NAME + '/findings_send.txt'
    try:
        queue = Queue()
        Spider2(PROJECT_NAME, HOMEPAGE, DOMAIN_NAME)
        sort_queue(PROJECT_NAME)
    except:
        pass
    
    try:
        create_workers2(NUMBER_OF_THREADS = 8 )
        crawl(QUEUE_FILE)
        print('Afsluttet crawling - leder efter findings.')
    except: 
        pass
    sort_queue(PROJECT_NAME)
    move_to_crawled(QUEUE_FILE, CRAWLED_FILE)
    sort_crawled(PROJECT_NAME)
    add_to_findings(PROJECT_NAME, encoding)
    print('Færdig med at tilføje til findings.')
    reset_Spider2()
    

def webcrawler_third(PROJECT_NAME, HOMEPAGE):
    QUEUE_FILE = PROJECT_NAME + '/queue.txt'
    CRAWLED_FILE = PROJECT_NAME + '/crawled.txt'
    CRAWLED_DONE = PROJECT_NAME + '/crawled_done.txt'
    FINDINGS_FILE = PROJECT_NAME + '/findings.txt'
    FINDINGS_SEND = PROJECT_NAME + '/findings_send.txt'
    
    move_to_crawled(QUEUE_FILE, CRAWLED_FILE)
    move_to_done(CRAWLED_FILE, CRAWLED_DONE)
    move_to_send(FINDINGS_FILE, FINDINGS_SEND)
    print('Filerne er flyttet.')

#%% THE WEB CRAWLER - create project - only run once

webcrawler_first(PROJECT_NAME = 'campaign', HOMEPAGE = 'https://www.campaignlive.co.uk')
webcrawler_first('AdWeek', 'https://www.adweek.com')
webcrawler_first('MarketingWeek', 'https://www.marketingweek.com') 
webcrawler_first('TheDrum', 'https://www.thedrum.com')
webcrawler_first('shots', 'https://www.shots.net/')
webcrawler_first('TheStable', 'https://www.thestable.com.au/')
webcrawler_first('Kampanje', 'https://kampanje.com/')
webcrawler_first('Resumé', 'https://www.resume.se/')
#%% THE WEB CRAWLER - run daily to crawl the sites, send the email and prepare for next crawl

webcrawler_second('AdWeek', 'https://www.adweek.com', encoding='utf-8') 
webcrawler_second('MarketingWeek', 'https://www.marketingweek.com', encoding='utf-8')
webcrawler_second('TheDrum', 'https://www.thedrum.com', encoding='utf-8')
webcrawler_second('Kampanje', 'https://kampanje.com/', encoding='utf-8')
webcrawler_second('Resumé', 'https://www.resume.se/', encoding='cp1252')
webcrawler_second('TheStable', 'https://www.thestable.com.au/', encoding='utf-8')
webcrawler_second('shots', 'https://www.shots.net/', encoding='cp1252') #Løs fejlen
webcrawler_second('campaign', 'https://www.campaignlive.co.uk', encoding='cp1252')

notification_email(['AdWeek', 'MarketingWeek', 'campaign', 'TheStable', 'shots', 'TheDrum', 'Kampanje', 'Resumé']) 

webcrawler_third('AdWeek', 'https://www.adweek.com')
webcrawler_third('MarketingWeek', 'https://www.marketingweek.com')
webcrawler_third('TheDrum', 'https://www.thedrum.com')
webcrawler_third('shots', 'https://www.shots.net/')
webcrawler_third('TheStable', 'https://www.thestable.com.au/')
webcrawler_third('Kampanje', 'https://kampanje.com/')
webcrawler_third('Resumé', 'https://www.resume.se/')
webcrawler_third('campaign','https://www.campaignlive.co.uk')
