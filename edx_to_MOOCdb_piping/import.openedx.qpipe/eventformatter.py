import helperclasses
import util

import genformatting
import specformatting
import inheritloc
import updateloc
import events

import util

class EventFormatter(object):


    def __init__(self,moocdb,CONFIG_PATH):

        # Filtering rules
        self.FILTER_RLS = CONFIG_PATH + 'filter_rules.txt'

        # Generic formatting functions
        self.GEN_FORMAT_FUNCTS = CONFIG_PATH + 'general_formatting.txt'
    
        # Specific formatting rules 
        self.SPEC_FORMAT_RLS = CONFIG_PATH + 'specific_formatting_rules.txt'

        # Location inheritance rules 
        self.INHERIT_LOC_RLS = CONFIG_PATH + 'inherit_location_rules.txt'

        # Update location rules
        self.UPDATE_LOC_RLS = CONFIG_PATH + 'update_loc_rules.txt'

        # Instanciation rules
        self.INST_EVENT_RLS = CONFIG_PATH + 'instanciate_event_rules.txt'
        
        self.engaged_users = helperclasses.EngagedUsers()

        self.urls = helperclasses.DictionaryTable(moocdb,'urls')
        self.agents = helperclasses.DictionaryTable(moocdb,'agent')
        self.os = helperclasses.DictionaryTable(moocdb,'os')
    
        self.filter_rules = util.load_rules(self.FILTER_RLS)
        self.general_formatting_functions = util.load_functions(self.GEN_FORMAT_FUNCTS, genformatting)
        self.specific_formatting_rules = util.load_rules(self.SPEC_FORMAT_RLS, specformatting)
        self.inherit_location_rules = util.load_rules(self.INHERIT_LOC_RLS, inheritloc)
        self.update_location_rules = util.load_rules(self.UPDATE_LOC_RLS, updateloc)
        self.instanciate_event_rules = util.load_rules(self.INST_EVENT_RLS, events)


    def pass_filter(self,raw_event):
        """ Returns True if the event should be processed further,
        according to the filtering rules defined in FILTER_RULES """

        return util.apply_rules(self.filter_rules, raw_event)


    def do_generic_formatting(self,raw_event):
        """Apply all general formatting functions 
        that are registered in GEN_FORMAT_CONF
        and defined in genformatting.py"""

        for f in self.general_formatting_functions:
            f(raw_event)


    def do_specific_formatting(self,raw_event):
        """Apply all specific formatting functions 
        according to the rules specified in SPEC_FORMAT_RLS
        and functions defined in specformatting.py"""

        util.apply_rules(self.specific_formatting_rules, raw_event)

    def inherit_location(self,raw_event):
        """Try to inherit location 
        according to the rules specified in INHERIT_LOC_RLS
        and functions defined in inheritloc.py"""

        current_location = self.engaged_users.get_location(raw_event['anon_screen_name'])

        if current_location:
            
            if not str(current_location[0]):
                #print '[eventformatter.inherit_location] User has no known previous location'
                return
            
            #print '- Engaged @ ' + str(current_location[0])
            #print '- Sequence number :: ' + str(current_location[0].get_seq())
            time_gap = (raw_event['time'] - current_location[1]).seconds 

            if time_gap < 3600:
                raw_event['current_location'] = current_location
                util.apply_rules(self.inherit_location_rules, raw_event)

            else:
                #print '[eventformatter.inherit_location] Location obsolete'
                return

        
    def update_location(self,raw_event):
        """Updates the user's current location
        according to the rules specified in UPDATE_LOC_RLS
        and functions defined in update_loc.py"""

        new_location = util.apply_rules(self.update_location_rules, raw_event)

        if new_location: 
            self.engaged_users.update_location(raw_event['anon_screen_name'], new_location, raw_event['time'])
            #print '[eventformatter.update_location] Location updated to : ' + str(new_location)
        else:
            self.engaged_users.remove_user(raw_event['anon_screen_name'])

    def instanciate_event(self,raw_event):
        """Instanciates an Event subclass from the now formatted raw_event,
        according to the rules specified in INST_EVT_RLS
        and classes defined in events.py"""
        
        return util.apply_rules(self.instanciate_event_rules, raw_event)


    def record_event_metadata(self,raw_event):

        raw_event['url_id'] = self.urls.insert(str(raw_event['page']))
        raw_event['os'] = self.os.insert(raw_event['os'])
        raw_event['agent'] = self.agents.insert(raw_event['agent'])
        
    def polish(self,raw_event):
        
        #print '** Generic formatting'
        self.do_generic_formatting(raw_event)
        #print '** Specific formatting'        
        self.do_specific_formatting(raw_event)
        #print '** Inherit location'
        self.inherit_location(raw_event)
        #print '** Update location'
        self.update_location(raw_event)
        #print '** Record event metadata'
        self.record_event_metadata(raw_event)
        #print '** Instanciate event'
        return self.instanciate_event(raw_event)

    def serialize(self):
        self.urls.serialize()
        self.agents.serialize()
        self.os.serialize()

    
