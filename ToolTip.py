import sublime, sublime_plugin, re , json



class Utilities():
    @staticmethod
    def result_format(json):
        result = "<pre> <b>Method:" + json["method"] + "</b>" + '\n' + "<b>Description:</b> " + '\n' + json["description"] + '\n'
        # for i in json["params"]:
        #     result += i + " "
        result += '\n' + "<b>Return:</b> " + json["return"] + "</pre>"
        return result 



class ToolTipCommand(sublime_plugin.TextCommand):
    SCOPE_NAME = "source.python"

    def run(self, edit):
        print(sublime.packages_path())
        # only python files could run this plugin
        if self.SCOPE_NAME in self.view.scope_name(0) and \
            int(sublime.version()) >= 3080:
            # get user selection
            sel = self.user_selection()
            # do match with user selection and return the result
            search_result = self.match_selection(sel)
            # set timout to 10 seconds, in the end hide the tooltip window
            sublime.set_timeout(lambda:self.view.hide_popup(),10000)
            # open popup window in the current cursor
            self.view.show_popup(search_result, on_navigate=print, max_width=300)
        

    def user_selection(self):
        # get the current cursor point
        sel = self.view.sel()[0].begin()
        # get the line with current cursor
        get_line = self.view.line(sel)
        print("Line content: " + self.view.substr(get_line).strip())
        return self.view.substr(get_line).strip()

    def match_selection(self, sel):
        # set regex to API subline functions
        sublime_regex = r".*\w+\.(\w+)\(.*\).*"

        try:
            # do match with the selected exp
            if re.match(sublime_regex, sel):
                print("match: " + re.match(sublime_regex, sel).group(1))
                # get the result in string
                search_result = re.match(sublime_regex, sel).group(1)                  
                # get the description & parameters from the result
                json = self.search_function(search_result.strip())
                # add the description & parameters to one string unit
                search_result = Utilities.result_format(json)
            else:
                search_result = "there is no match"
        except:
            # in case the sel = None
            search_result = "there is no match exception"

        return search_result.lower()

    

    def search_function(self, search_result):
        try:
            json_data = self.readJSON()
            return json_data[search_result]

        except:
            print("Problem with load JSON file")


    def readJSON(self):
        # get the packages path 
        path = sublime.packages_path() + "\\ToolTip\\Api.JSON"
        with open(path) as json_file:
                return json.load(json_file)
