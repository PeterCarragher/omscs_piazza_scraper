import requests
import queue
import time
import os

ED_JW_USER_ID = 141771 # only for Jill Watson
max_threads = 10000
num_threads_per_request = 100 # maximum for ed
# TODO: add threads to ignore (VERA & JW threads)?

class EdAPI:

    def __init__(self, email, password, agent_user_id = ED_JW_USER_ID, token_file = 'token.txt', host = 'https://us.edstem.org/api'): 
        self.token_file = token_file
        self.token = self.getToken() # generated separately with EdTokenAPI script
        self.host = host
        self.email = email
        self.password = password
        self.agent_user_id = agent_user_id
        
    def makeRequest(self, method, url, **kwargs):
        r = requests.request(method, url, **kwargs)
        if r.status_code in [200, 201, 204]:
            return r
        print('Body:', r.text)
        raise Exception('Request failed', r.status_code, method, url)

    def setToken(self, token_file):
        r = self.makeRequest('POST', self.host + '/token', json={'login': self.email, 'password': self.password})
        token = r.json()['token']
        with open(token_file, 'w') as filetowrite:
            filetowrite.write(token)
        return token

    def getToken(self):
        path = os.path.dirname(os.path.abspath(__file__))
        token = ""
        with open(path + '/' + self.token_file, 'r') as filetoread:
            token = filetoread.read()
        return token

    def readThreadsFromClass(self, class_id):
        token = self.getToken()
        current_thread_num = -1
        threads = {}
        offset = 0
        while(current_thread_num < len(threads.values())):
            current_thread_num = len(threads.values())
            r = self.makeRequest('GET', self.host + '/courses/' + str(class_id) + '/threads?limit=' + str(num_threads_per_request) + '&offset=' + str(offset) + '&sort=new', headers={'x-token': token})
            r_threads = r.json()['threads']
            for thread in r_threads:
                threads[thread['id']] = thread['user_id']
            offset += len(r_threads)

        return threads

    def readCommentsFromThread(self, thread_id):
        token = self.getToken()
        r = self.makeRequest('GET', self.host + '/threads/' + str(thread_id) + '?view=1', headers={'x-token': token})
        comments = r.json()['thread']['comments'] 
        answers = r.json()['thread']['answers']
        roles = {}
        for user in r.json()['users']:
            roles[user['id']] = user['course_role']
        return (comments + answers, roles)

    def readUnansweredCommentsFromThread(self, thread_id):
        thread = self.readCommentsFromThread(thread_id)
        unanswered = dict()
        unseen = queue.Queue()        
        for comment in thread:
            if not comment['is_resolved']:
                unseen.put(comment)
        
        while unseen.qsize() > 0:
            comment = unseen.get()
            children = comment['comments']
            answered = False
            for child in children:
                unseen.put(child)
                if child['user_id'] == self.agent_user_id:
                    answered = True
            if comment['user_id'] != self.agent_user_id and not answered:
                content = comment['document']
                if '?' in content:
                    unanswered[comment['id']] = content
        
        return unanswered
