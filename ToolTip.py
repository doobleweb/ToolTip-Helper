import sublime, sublime_plugin, re, json, os

class Utilities():
    @staticmethod
    def result_format(json):
        return "<pre> <b>Method:" + json["method"] + "</b>" + '\n' + "<b>Description:</b> " + '\n' + json["description"] + '\n' + "<b>Return:</b> " + json["return"] + "</pre>" 

class ToolTipCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        # get the current file extension
        current_file_source = self.view.scope_name(0)
        # get path for tooltip folder
        path = sublime.packages_path() + "\\ToolTip\\"
        # print(self.get_immediate_files(path))
        file_path = self.get_tooltip_file_path(path, current_file_source)
        # get specific json file
        json = self.read_JSON(file_path)
        # get scope from json file
        scope = json["scope"]
        
        if scope in current_file_source and \
            int(sublime.version()) >= 3080:
            # get user selection
            sel = self.user_selection()
            # do match with user selection and return the result
            search_result = self.match_selection(sel, file_path)
            # set timout to 10 seconds, in the end hide the tooltip window
            sublime.set_timeout(lambda:self.view.hide_popup(),10000)
            # open popup window in the current cursor
            self.view.show_popup(search_result, on_navigate=print, max_width=300)


    def user_selection(self):
        sel = self.view.sel()[0]
        get_word = self.view.word(sel)
        get_word_str = self.view.substr(get_word)
        return get_word_str.strip()


    def match_selection(self, sel, file_path):
        search_result = "Documentation not exist"

        try:
            json = self.search_function(sel.strip(), file_path)
            search_result = Utilities.result_format(json)
        except:
            search_result = "Documentation not exist"

        return search_result
    

    def search_function(self, search_result, file_path):
        try:
            json_data = self.read_JSON(file_path)
            return json_data["methods"][search_result]

        except:
            print("Problem with load JSON file")


    def read_JSON(self, path):
        with open(path) as json_file:
                return json.load(json_file)


    def get_tooltip_file_path(self, a_dir, scope_name):
        files_list = self.get_immediate_files(a_dir)
        # search json file by source
        for i in files_list:
            file = i.split('.')[0]
            if file in scope_name:
                return a_dir + i  
        return ""

    def get_immediate_files(self, a_dir):
        return [f for f in os.listdir(a_dir) if os.path.isfile(os.path.join(a_dir, f))]

