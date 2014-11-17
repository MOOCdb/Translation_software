import re 
import csv
import os
import pickle
import config as cfg

class CourseURL:
    """ Course URL : A class for handling course URLs
    - Ensures consistent formatting
    - Provides methods to access unit, subunit and sequence numbers"""
    
    # Regexp to filter out strings that are not URLs. 
    IS_URL = cfg.IS_URL

    # Cleaning the URL
    DOUBLE_SLASH = cfg.DOUBLE_SLASH
    PARAMETERS = cfg.PARAMETERS
    ANCHOR = cfg.ANCHOR
    MODULE = cfg.MODULE
    MISSING_TRAILING_SLASH = cfg.MISSING_TRAILING_SLASH

    # Course URL path components
    DEFAULT_DOMAIN = cfg.DOMAIN
    GET_DOMAIN = cfg.GET_DOMAIN
    
    # Courseware specific parser
    COURSEWARE = cfg.COURSEWARE
    
    # Book specific parser
    BOOK = cfg.BOOK
       
    
    def __init__(self,url_string):
        # Setting default values for different kinds
        # of possible path components
        self.domain = ''
        self.unit = ''
        self.subunit = ''
        self.seq = ''
        self.booknum = ''
        self.page = ''

        # Store sanitized URL string
        self.url = self.sanitize(url_string)

        # No need to go further if the URL is empty
        if not self.url:
            return
       
        # Different parsing strategies are needed depending on
        # the king of URL we deal with
        if 'courseware' in self.url:
            self.parse_courseware_url()
        elif 'book' in self.url:
            self.parse_book_url()
            
        # Add default domain if missing
        self.set_domain()

    def __str__(self, add_underscore=True):
        # At sub-unit level, a missing sequence number is viewed as '_'
        if add_underscore and self.subunit and not self.seq:
            return self.url + '_/'
        else:
            return self.url
        
    def set_domain(self,domain=''):
        # For relative paths add default domain 
        # and sequence 1 if at subunit level
        if self.url[0] == '/':
            domain = self.DEFAULT_DOMAIN if not domain else domain
            self.url = domain + self.url 
            self.domain = domain
            if self.subunit:
                self.set_seq('1')
        
        # For absolute URLs, parse the domain
        # match = self.GET_DOMAIN.search(self.url)

        # if not match:
        #     return

        # self.domain = match.group('domain')
        
    def sanitize(self,url_string):
        
        url_string = url_string.strip()
        if not self.IS_URL.search(url_string):
            return ''
        
        # Remove double slashes
        url_string = re.sub(self.DOUBLE_SLASH, '', url_string)
        # Remove parameters or anchors
        url_string = re.sub(self.PARAMETERS, '', url_string)
        url_string = re.sub(self.ANCHOR, '', url_string)
        # Remove possible trailing problem IDs
        url_string = re.sub(self.MODULE, '', url_string)
        # Make sure the URL has a trailing slash
        url_string = re.sub(self.MISSING_TRAILING_SLASH, '/', url_string)
            
        return url_string

    def parse_courseware_url(self):
        match = self.COURSEWARE.search(self.url)
        
        if not match:
            #print ' Exotic courseware URL : ' + self.url
            return
        
        # Store different path components
        self.unit = match.group('unit')
        self.subunit = match.group('subunit')
        self.seq = match.group('seq')

    def parse_book_url(self):
        match = self.BOOK.search(self.url)

        if not match:
            return
        
        self.booknum = match.group('booknum')
        self.page = match.group('page')
        
        
    # Set or replace sequence number
    def set_seq(self, seqnum):
        
        seqnum = str(seqnum)

        # If the URL is not at subunit level,
        # no sequence number should be appended
        if not self.subunit:
            return 

        # If there already is a sequence number, replace it.    
        # The caller is responsible !
        if self.seq:
            self.url = self.url.replace('/{}/'.format(self.seq), '/{}/'.format(seqnum))
        else:
            self.url = self.url.replace( '/{}/'.format(self.subunit), '/{}/{}/'.format(self.subunit, seqnum))
        
        # Finally, update the instance's sequence number
        self.seq = seqnum

    def set_page(self,pagenum):

        pagenum = str(pagenum)
        
        # If there is no book number, 
        # something is wrong
        if not self.booknum:
            #print ' Exotic book url ' + self.url
            return

        # If there already is a page number,
        # replace it. Caller is responsible
        if self.page:
            self.url = self.url.replace('/{}/{}/'.format(self.booknum,self.page),'/{}/{}/'.format(self.booknum,pagenum))
        else:
            self.url = self.url.replace('/{}/'.format(self.booknum), '/{}/{}/'.format(self.booknum, pagenum))
            
        # Finally, update the instance's page number
        self.page = pagenum

    # These are kept to avoir breaking existing code
    # but obviously of no use for the moment
    def get_unit(self):
        return self.unit

    def get_sub_unit(self):
        return self.subunit

    def get_seq(self):
        return self.seq

    def get_base_url(self):
        
        if not self.subunit:
            return self.url
        
        if not self.seq:
            return self.url

        else:
            return self.url.replace('/{}/'.format(self.seq),'/')
            

class ModuleURI(object):
    '''
    1) URI-like event type :
    /courses/MITx/6.002x/2013_Spring/modx/i4x://MITx/6.002x/problem/H9P3_Designing_a_Shock_Absorber/problem_check
    
    Module URI : i4x:://MITx/6.002x/problem/H9P3_Designing_a_Shock_Absorber/problem_check
    URI root : i4x://MITx/6.002x/
    Module category : problem
    Module ID : H9P3_Designing_a_Shock_Absorber
    Action : problem_check
    Resource display name : H9P3 Designing a Shock Absorber

    2) Video or problem ID :
    i4x-MITx-6_002x-video-S23V15_Buffer_circuit

    Module URI : i4x://MITx/6.002x/video/S23V15_Buffer_circuit
    Module ID : S23V15_Buffer_circuit
    Resource display name: S23V15 Buffer Circuit
    '''

    # Regular expression for parsing identifiers
    URI_PARSER = re.compile('(?P<uri_root>i4x:/{1,2}[^/]*/[^/]*/)(?P<category>[^/]+)/(?P<module_id>[^/]+)/?(?P<action>[a-z_]+)?$')

    ID_PARSER = re.compile('(?P<id_root>i4x-[^-]*-[^-]*-)(?P<category>[^-]*)-(?P<module_id>.*)$')
    ID_TAIL = re.compile('(?P<number>(_[0-9]{1,2})+)$')

    HASH = re.compile('[a-f0-9]{32}')
    RESCUE_ANSWER = re.compile('(?P<answer>choice_\d{1,2})[ ]*$')

    def __init__(self, id_string):

        self.module_uri = ''
        self.uri_root = ''
        self.module_id = ''
        self.category = ''
        self.action = ''
        self.numbers = ''
        self.rescued_answer = ''
        
        # There are two different handlers :
        #  - one for inline IDs like :
        #    'i4x-MITx-6_002x-video-S23V15_Buffer_circuit_2_1'
        #  - one for embedded URIs like : 
        #    '/courses/MITx/6.002x/2013_Spring/modx/i4x://MITx/6.002x/problem/Op_Amps/problem_get'

        if 'i4x:' in id_string:            
            self.parse_uri(id_string)
        else:
            self.parse_id(id_string)

    def __str__(self):
        return self.module_uri
        
    def get_uri(self):
        return self.module_uri

    def get_relative_uri(self):
        return self.module_uri[len(self.uri_root):]

    def get_top_level_uri(self):
        return '{}{}/{}/'.format(self.uri_root, self.category, self.module_id)

    def sanitize(self,s):
        
        # Try to rescue answer from module ID string
        match = self.RESCUE_ANSWER.search(s)
        if match:
            answer = match.group('answer')
            if answer:
                self.rescued_answer = answer
                #print 'Answer rescued'
                s = re.sub(answer, '', s)
                
        # Cleanup all possible trailing oddities
        s = re.sub('_$','',s)
        s = re.sub('=.*$','',s)
        s = re.sub('_dynamath','',s)
        s = re.sub('%.*','',s)
        
        return s

    def set_question_numbers(self):
        ''' 
        Searches for trailing question numbers 
        in the module_id string
        '''
        tail = self.ID_TAIL.search(self.module_id)
        
        if not tail:
            return

        number = tail.group('number')
        
        l = len(number) if number else 0
        
        self.module_id = self.module_id[:-l]
        self.numbers = number.replace('_','/')
                
    # URI case
    def parse_uri(self, id_string):
        match = self.URI_PARSER.search(id_string)
        
        if not match:
            #print 'Unexpected module URI pattern : %s'% id_string
            return
                    
        self.uri_root = match.group('uri_root')
        self.category = match.group('category')        
        self.module_id = match.group('module_id')
        self.action = match.group('action')
        self.module_uri = '{}{}/{}/'.format(self.uri_root, self.category, self.module_id)

    
    # ID case
    def parse_id(self, id_string):
        # Keep only the specific part of the
        # problem ID, i.e. the one after 
        # '-problem-'
        
        match = self.ID_PARSER.search(id_string)

        if not match:
            #print 'Unexpected module ID pattern %s'%id_string
            return

        if not match.group('id_root'):
            #print 'Unable to match id_root in %s'%id_string
            return

        if not match.group('module_id'):
            #print 'Unable to match module_id in %s'%id_string
            return

        if not match.group('category'):
            #print 'Unable to match category in %s'%id_string
            return

        # Set the URI root
        # 'i4x-MITx-6_002x-'
        #   becomes :
        # 'i4x://MITx/6_002x/'
        id_root = match.group('id_root')
        id_root = re.sub('-','://',id_root, count=1)
        self.uri_root = re.sub('-','/',id_root)
                     
        # Set category (which is clean)
        self.category = match.group('category')
        
        # Set module_id, after sanitizing 
        # to remove trailing noise
        self.module_id = self.sanitize(match.group('module_id'))

        # If the module is a video, the work stops here
        if self.category == 'video':
            self.module_uri = '{}{}/{}/'.format(self.uri_root, self.category, self.module_id)
        else:
            self.set_question_numbers()
            self.module_uri = '{}{}/{}{}/'.format(self.uri_root, self.category, self.module_id,self.numbers)

    def get_name(self):
        if self.HASH.search(self.module_id): 
            return None
        else:
            return self.module_id.replace('_',' ')
    
# Dictionary Table

class DictionaryTable(object):
    """ Basically a list, used to build the various dictionary tables in MOOCdb """

    def __init__(self, moocdb, table_name):
        self.ITEM_LIST = []
        self.table = getattr(moocdb,table_name)
        self.fieldnames = moocdb.TABLES[table_name]

    def insert(self,value):
        if value in self.ITEM_LIST:
            return self.ITEM_LIST.index(value)
        else:
            self.ITEM_LIST.append(value)
            return len(self.ITEM_LIST) - 1

    def __len__(self):
        return len(self.ITEM_LIST)

    def __getitem__(self,i):
        return self.ITEM_LIST[i]

    def serialize(self):
         for i in range(0,len(self)):
            item = self[i]
            if len(item) == 2:
                values = [i] + [str(x) for x in item]
                row = dict(zip(self.fieldnames, values))
                self.table.store(row)
            else:
                row = dict(zip(self.fieldnames,[i,item]))
                self.table.store(row)

class CurationHelper(object):

    def __init__(self, OUTPUT_DIR):
        self.OUTPUT_DIR = OUTPUT_DIR 
        self.hints = {}
        self.candidate_resources = {}
        
    def record_curation_hints(self,event):
        ''' 
        If the event has an associated module, record 
        the resource URI as a candidate for this module
        '''
        module = event.data.get('module',None)
        if module:
            self.add_candidate_resource(module, event)
            self.add_curation_hint(module, event)

    def add_candidate_resource(self, module, event):
        '''
        Updates a dictionary of the form :
        { module_uri : [ (url_id, resource_id)  ] }

        This allows to retrieve two things :
        - All the candidate resource IDs for a given module
        - Given a correct url_id, the corresponding resource candidate
        '''
        
        module_uri = module.get_uri()
        url_id = event['url_id']
        resource_id = event['resource_id']
        
        # If the module has already been encountered,
        # add the candidate resource if it is new 
        if module_uri in self.candidate_resources:
            candidates = self.candidate_resources[module_uri]
            if (url_id, resource_id) not in candidates:
                candidates.append((url_id, resource_id))

        # Else, add a first candidate for this module
        else:
            self.candidate_resources[module_uri] = [(url_id, resource_id)]

            
    def add_curation_hint(self, module, event):
        '''
        Updates a structure of the form:
        module_base_uri : { url_base_string : { (seqnum, url_id):count } }
        
        This allows to create curation questions that identify the right
        url ID for each module. 
        By picking a base URL and a sequence number, 
        the curator identifies the correct URL ID.
        '''
        
        module_base_uri = module.get_top_level_uri()
        url_id = event['url_id']
        url = event.data['page']
        base_url = url.get_base_url()
        seqnum = url.seq
        
        module_hints = self.hints.get(module_base_uri, None)
        if module_hints:
            self.add_hint_to_module(module_hints, base_url, url_id, seqnum)
        else:
            self.hints[module_base_uri] = { base_url : { (seqnum,url_id):1 } }

    def add_hint_to_module(self, module_hints, base_url, url_id, seqnum):
        if base_url in module_hints:
            if (seqnum, url_id) in module_hints[base_url]:
                module_hints[base_url][(seqnum,url_id)] += 1
            else:
                module_hints[base_url][(seqnum,url_id)] = 1
        else:
            module_hints[base_url] = {(seqnum, url_id):1}
    
                                   
    def serialize(self, dest_dir=''):
        
        if not dest_dir:
            dest_dir = self.OUTPUT_DIR
        

        # Pickle dict object containing the resource candidates and curation hints
        curation_helpers = { 'hints':self.hints, 'candidates':self.candidate_resources}
        with open( os.path.join(dest_dir,'curation_hints.pickle'), 'w+') as f:
            pickle.dump(curation_helpers, f)

        # #Print a org-mode curation form prototype
        with open( os.path.join(dest_dir,'curation_hints.org'), 'w+') as g:
            for module in self.hints:
                g.write('* Module %s\n'%module)
                module_hints = self.hints.get(module)
                for base_url in module_hints:
                    g.write('** [[%s]] \n' % base_url)
                    for (seqnum,url_id) in module_hints[base_url]:
                        g.write('- [ ] x{} :: Panel {} :{}: \n'.format(module_hints[base_url][(seqnum, url_id)],
                                                                       seqnum,
                                                                       url_id))
                    
class EngagedUsers(object):
    """ Used to maintain the list of engaged users in EventFormatter """
    def __init__(self):
        self.engaged_users = {}

    def is_engaged(self, user):
        return (user in self.engaged_users.keys())

    def get_location(self,user):
        if self.is_engaged(user):
            return self.engaged_users[user]
        else:
            return None

    def remove_user(self,user) :
        if user in self.engaged_users.keys():
            self.engaged_users.pop(user)
        else:
            print '[EngagedUsers.remove_user] : Trying to remove unengaged user : ' + str(user)

    def update_location(self,user,new_location,time):
        self.engaged_users[user] = (new_location,time)




        
        

# CSV Writers 

class CSVWriter(object):
    
    def __init__(self,output_file,delim=','):

        try:
            self.output = open(output_file,'w')
            self.writer = csv.writer(self.output, delimiter=delim)
        
        except IOError:
            #print '[' + self.__class__.__name__ + '] Could not open file ' + output_file
            return

    def store(self,l):
        self.writer.write(l)
        
    def close(self):
        self.output.close()


class DictionaryWriter(CSVWriter):

    def write(self,dictionarytable):
        
        for i in range(0,len(dictionarytable)):

            item = dictionarytable[i]

            if len(item) == 2:
                self.writer.writerow([i] + [str(x) for x in item])
            else:
                self.writer.writerow([i,item])
        
                                 
class EventWriter(CSVWriter):

    def write(self,event):
        
        self.writer.writerow(event.to_list())

    
class ResourceWriter(CSVWriter):

    def write(self, node):
        
        self.writer.writerow( node.to_list() )
        
        for child in node.children:
            self.write( child )




        
