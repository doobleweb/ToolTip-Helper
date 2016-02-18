import sublime
import sublime_plugin
import webbrowser
import logging
import json 
import re
import os

# get the current version of sublime
CURRENT_VERSION = int(sublime.version()) >= 3080
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class Utilities():
    """This class represent utilities for the plugin"""
    @staticmethod
    def result_format(json, keyorder, link):
        message = ""

        if keyorder:
            try:
                # the output of sorted function is an ordered list of tuples 
                ordered_result = sorted(json.items(), key=lambda i:keyorder.index(i[0]))
            except Exception as e:
                ordered_result = []
            message = Utilities.get_html_from_list(ordered_result)
        else:
            message = Utilities.get_html_from_dictionary(json)
        # add helper link if there is such
        if link:
            message += '<span style="color:orange"><b><u>see also:</u></b></span><br><a href=\"%s\">See more</a>' % link
        return message

    @staticmethod
    def get_html_from_list(ordered_result):
        message = ""
        for item in ordered_result:
            key, value = item
            # if some attribute empty, don't put him in the popup window
            if value and key != 'link':
                message += '<span style="color:#FD971F"; text-decoration: underline;><b><u>' + key + ':</u></b></span><br>' + value + " <br><br>"
        return '<div style="margin: 0; padding: 0.8em;">' + message + '<div>'

    @staticmethod
    def get_html_from_dictionary(json):
        message = ""
        for item in json:
            # if some attribute empty, don't put him in the popup window
            if json[item] and item != 'link':
                message += '<b>' + item + ':</b><br>' + json[item] + " <br>"
        return message


class EnterDataCommand(sublime_plugin.WindowCommand):
    """This class represent user interface to enter some data in settings file"""
    def __init__(self, view):
        self.view = view
        self.source = None
        self.file_path = None
        self.link = None

    def run(self):
        sublime.active_window().show_input_panel("Enter your scope file here:", "", self.get_source, None, None)

    def get_source(self, user_input):
        # print("get source input: " + user_input)
        if user_input.strip():
            self.source = user_input
            # print("source: " + self.source)
            sublime.active_window().show_input_panel("Enter your file name here:", "", self.get_path, None, None)

    def get_path(self, user_input):
        if user_input.strip():
            self.file_path = user_input
            # print("file name: " + self.file_path)
            sublime.active_window().show_input_panel("Enter your link here (optional):", "", self.get_link, None, None)            

    def get_link(self, user_input):
        if user_input.strip():
            self.link = user_input
        else:
            self.link = ""
        # print("link: " + self.link)
        self.save_changes()

    def save_changes(self):
        try:
            file_settings = 'ToolTipHelper.sublime-settings'
            file_load = sublime.load_settings(file_settings)
            files = file_load.get("files")
            files.append({"file_path":self.file_path, "source":self.source, "link":self.link})
            file_load.set("files", files)
            sublime.save_settings(file_settings)
            sublime.status_message("the changes was saved!")
        except Exception as e:
            sublime.status_message("cannot save the changes")            
      

class ToolTipHelperCommand(sublime_plugin.TextCommand):
    """This class represent tooltip window for showing documentation"""
    def __init__(self, view):
        # load settings
        self.view = view
        self.show_poup = True
        self.settings = sublime.load_settings('ToolTipHelper.sublime-settings')
        self.files = self.settings.get("files")
        self.keyorder = self.get_keyorder()
        self.set_timeout = self.set_timeout()
        self.max_width = self.max_width()
        self.link = None
        # print(self.keyorder)
        # print(self.set_timeout)
        # print(self.max_width)

    def run(self, edit):
        # get the cursor point
        sel = self.view.sel()[0]
        # get the current scope by cursor position
        current_file_source = self.view.scope_name(sel.begin())
        # print(current_file_source)
        file_path = self.get_tooltip_file_path(current_file_source)
        # get user selection
        sel = self.user_selection(sel)
        # do match with user selection and return the result
        json_result = self.match_selection(sel, file_path)
        # edit the messege in html for popup window
        search_result = Utilities.result_format(json_result, self.keyorder, self.link)
        # check if it proper version
        if CURRENT_VERSION and \
            self.show_poup:
            # set timout to 10 seconds, in the end hide the tooltip window
            sublime.set_timeout(lambda:self.view.hide_popup(), self.set_timeout)
            # open popup window in the current cursor
            self.view.show_popup('<div style="background-color: #272822; color:white; font-size: 18px;">%s</div>' % search_result,
                                on_navigate=self.on_navigate, 
                                max_width=self.max_width)

    def on_navigate(self, href):
        # open the link in new tab on web browser
        webbrowser.open_new_tab(href)

    def user_selection(self, sel):
        # get the whole word from this point
        get_word = self.view.word(sel)
        # get the word in string
        get_word_str = self.view.substr(get_word)
        # print("selected word:" + get_word_str)
        return get_word_str.strip()

    def match_selection(self, sel, file_path):
        search_result = "Documentation not exist"

        try:
            # search the object in json file
            json_result = self.search_in_json(sel.strip(), file_path)
            keys = list(json_result.keys())
            count = 0
            for key in keys:
                if key not in self.keyorder:
                    count += 1
                    self.keyorder.append(key)

            if count != 0:
                file_settings = 'ToolTipHelper.sublime-settings'
                file_load = sublime.load_settings(file_settings)
                file_load.set("keyorder", self.keyorder)
                sublime.save_settings(file_settings)
            if 'link' in json_result:
                self.link = json_result['link']
        except:
            self.show_poup = False
            search_result = "Documentation not exist"
        return json_result
    
    def search_in_json(self, search_result, file_path):
        try:
            json_data = self.read_JSON(file_path)
            # print("json_data:" + json_data)
            return json_data["methods"][search_result]
        except Exception as e:
            logging.error('Documentation not exist.')
            self.show_poup = False

    def read_JSON(self, path):
        # print("read json from: " + path)
        with open(path, encoding="utf8") as json_file:
            try:
                data = json.load(json_file)
                # print("json load success")
            except Exception as e:
                logging.error('cannot load JSON file.')
                self.show_poup = False
            return data

    def get_tooltip_file_path(self, current_file_source):
        files = self.get_immediate_files()
        full_path = ""

        if files:
            for i in files:
                relative_path = sublime.packages_path() + '\\ToolTipHelper\\'
                if i['source'] in current_file_source:
                    full_path = relative_path + i['file_path']
                    self.link = i['link']
                    break       
        return full_path
        
    def get_immediate_files(self):
        try:
            file_settings = 'ToolTipHelper.sublime-settings'
            file_load = sublime.load_settings(file_settings)
            files = file_load.get("files")
        except:
            logging.error('cannot loads the files')
            files = []
            self.show_poup = False
        return files

    def get_keyorder(self):
        try:
            keyorder = self.settings.get("keyorder")
        except:
            keyorder = []
        return keyorder
  
    def set_timeout(self):
        try:
            set_timeout = int(self.settings.get("set_timeout")) 
        except:
            set_timeout = 10000
        return set_timeout

    def max_width(self):
        try:
            max_width = int(self.settings.get("max_width"))
        except:
            max_width = 350
        return max_width
