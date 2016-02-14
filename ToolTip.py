import sublime, sublime_plugin, re, json, os
# sublime.status_message()
class Utilities():
    @staticmethod
    def result_format(json):
        message = "<pre>"
        for item in json:
            # if some attribute empty, don't put him in the popup window
            if json[item] != "":
                message += '<b>' + item + ':</b>' + " " + json[item] + " "
        message += '</pre>'
        return message


class ToolTipCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        # get the cursor point
        sel = self.view.sel()[0]
        # get the current scope by cursor position
        current_file_source = self.view.scope_name(sel.begin())
        # print(current_file_source)
        file_path = self.get_tooltip_file_path(current_file_source)
        # get specific json file
        json = self.read_JSON(file_path)
        # get scope from json file
        scope = json["scope"]
        
        if scope in current_file_source and \
            int(sublime.version()) >= 3080:
            # get user selection
            sel = self.user_selection(sel)
            # do match with user selection and return the result
            search_result = self.match_selection(sel, file_path)
            # set timout to 10 seconds, in the end hide the tooltip window
            sublime.set_timeout(lambda:self.view.hide_popup(),10000)
            # open popup window in the current cursor
            self.view.show_popup(search_result, on_navigate=print, max_width=300)


    def user_selection(self, sel):
        # get the whole word from this point
        get_word = self.view.word(sel)
        # get the word in string
        get_word_str = self.view.substr(get_word)
        return get_word_str.strip()


    def match_selection(self, sel, file_path):
        search_result = "Documentation not exist"

        try:
            # search the object in json file
            json = self.search_function(sel.strip(), file_path)
            # edit the messege in html for popup window
            search_result = Utilities.result_format(json)
        except:
            search_result = "Documentation not exist"
        return search_result
    

    def search_function(self, search_result, file_path):
        try:
            json_data = self.read_JSON(file_path)
            return json_data["methods"][search_result]
        except:
            print("Documentation not exist or problem with load JSON file")


    def read_JSON(self, path):
        with open(path) as json_file:
                return json.load(json_file)


    def get_tooltip_file_path(self, current_file_source):
        files = self.get_immediate_files()
        file_path = ""

        for i in files:
            if i['source'] in current_file_source:
                file_path = i['file_path']
                break
        return file_path
        

    def get_immediate_files(self):
        try:
            file_settings = 'ToolTip.sublime-settings'
            file_load = sublime.load_settings(file_settings)
            # file_load.set("some_key", "some_value")
            files = file_load.get("files")
        except:
            files = []
        return files

