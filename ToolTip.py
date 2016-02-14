import sublime, sublime_plugin, re, json, os

class Utilities():
    @staticmethod
    def result_format(json):
        return "<pre> <b>Method:" + json["method"] + "</b>" + '\n' + "<b>Description:</b> " + '\n' + json["description"] + '\n' + "<b>Return:</b> " + json["return"] + "</pre>" 

class ToolTipCommand(sublime_plugin.TextCommand):
    SCOPE_NAME = "source.python"

    def run(self, edit):
        source = self.view.scope_name(0)
        # print(source)
        path = sublime.packages_path() + "\\ToolTip\\"
        # print(self.get_immediate_files(path))
        file_path = self.get_tooltip_file_path(path, source)


        # step 1: read the source of file & check if there is json for the language
        json = self.read_JSON(file_path)
        scope = json["scope"]
        # print("scope: " + scope)
        # step 2: get the regex for matching
        # regex_arr = json["regex"]
        # print(regex_arr)
        # sublime_regex = r""+regex_arr[0]
        # sublime_regex2 = r""+regex_arr[1]
        # print("regex: " + sublime_regex)

        # sublime.status_message()

        if scope in self.view.scope_name(0):
            # get user selection
            sel = self.user_selection()
            # do match with user selection and return the result
            search_result = self.match_selection(sel)
            # set timout to 10 seconds, in the end hide the tooltip window
            sublime.set_timeout(lambda:self.view.hide_popup(),10000)
            # open popup window in the current cursor
            self.view.show_popup(search_result, on_navigate=print, max_width=300)


        # only python files could run this plugin
        # if self.SCOPE_NAME in self.view.scope_name(0) and \
        #     int(sublime.version()) >= 3080:
        #     # get user selection
        #     sel = self.user_selection()
        #     # do match with user selection and return the result
        #     search_result = self.match_selection(sel, sublime_regex)
        #     # set timout to 10 seconds, in the end hide the tooltip window
        #     sublime.set_timeout(lambda:self.view.hide_popup(),10000)
        #     # open popup window in the current cursor
        #     self.view.show_popup(search_result, on_navigate=print, max_width=300)
        

    def user_selection(self):
        # get the current cursor point
        # sel = self.view.sel()[0].begin()
        sel = self.view.sel()[0]
        # get the line with current cursor
        # get_line = self.view.line(sel)
        # get_line_str = self.view.substr(get_line).strip()
        # print("Line content: " + get_line_str)
        # ans = self.check_line(get_line_str)

        get_word = self.view.word(sel)
        get_word_str = self.view.substr(get_word)
        # print("word: " + get_word_str)
        
        # return self.view.substr(get_line).strip()
        return get_word_str.strip()

    # def check_line(self, get_line_str):
    #     for i in arr:
    #         if re.match(i, sel):



    def match_selection(self, sel):
        # set regex to API subline functions
        # sublime_regex = r"^.*\w+\.(\w*)\((\w*\s*\,*\s*)*\)$"
        # regex = r".*\w+\.\w+\(\w*\)(\[[0-9]\])*(\.\w+\(\w*\))+"

        search_result = "Documentation not exist"

        try:
            json = self.search_function(sel.strip(), file_path)
            search_result = Utilities.result_format(json)
        except:
            search_result = "Documentation not exist"

        return search_result
           
        # try:
        #     # do match with the selected exp
        #     if re.match(sublime_regex, sel):
        #         # print("match: " + re.match(sublime_regex, sel).group(1))
        #         # get the result in string
        #         search_result = re.match(sublime_regex, sel).group(1)
        #         # print(search_result)                  
        #         # get the description & parameters from the result
        #         json = self.search_function(search_result.strip())
        #         # print(json)
        #         # add the description & parameters to one string unit
        #         search_result = Utilities.result_format(json)
        #     elif re.match(sublime_regex2, sel): #elif re.match(regex, sel):
        #         arr = re.match(sublime_regex2, sel).group(0)
        #         # print("match sublime_regex2: " + arr)
        #         arr = arr.split('.')
        #         print(arr)
        #         # get the current cursor point
        #         sel = self.view.sel()[0].begin()
        #         # get the line with current cursor
        #         get_line = self.view.line(sel)
        #         # get the start position of line
        #         line_start = get_line.begin()
        #         # get the end position of line
        #         line_end = get_line.end()
        #         # search untill you see point or edge for both directions
        #         view = sublime.active_window().active_view()
        #         # loop till the and of row
        #         # b = self.get_right_side_cursor(sel, line_end, view)
        #         for i in range(sel, line_end+1):
        #             b = i
        #             if i == line_end+1 or \
        #                view.substr(i) == '.':
        #                 break
        #         # loop down till the start of row
        #         # a = self.get_left_side_cursor(sel, line_start, view)
        #         for i in range(sel-1, line_start-1, -1):
        #             a = i+1
        #             if i == line_start or \
        #                view.substr(i) == '.':
        #                 break
        #         print(a, b)
        #         # get the selection in string 
        #         word = view.substr(sublime.Region(a, b))
        #         print(word)
        #         # find function in pattern of 'function_name()'
        #         fun_regex = r"^(\w*)\(\w*\)(\[[0-9]\])*\)*$"

        #         if re.match(fun_regex, word):
        #             search_result = re.match(fun_regex, word).group(1)
        #             json = self.search_function(search_result)
        #             # print(json)
        #             # add the description & parameters to one string unit
        #             search_result = Utilities.result_format(json)
        #             # print(search_result)
        #             # search the word in json file ant return the result
        #     else:
        #         search_result = "Documentation not exist"
        # except:
        #     # in case the sel = None
        #     # search_result = "there is no match exception"
        #     sublime.status_message("There is no Documentation exception")

        # return search_result.lower()

    # def get_right_side_cursor(sel, line_end, view):
    #     for i in range(sel, line_end+1):
    #         b = i
    #         if i == line_end+1 or \
    #             view.substr(i) == '.':
    #                 return b
        

    # def get_left_side_cursor(sel, line_start, view):
    #     for i in range(sel-1, line_start-1, -1):
    #         a = i+1
    #         if i == line_start or \
    #             view.substr(i) == '.':
    #                 return a
        


    def search_function(self, search_result, file_path):
        try:
            json_data = self.read_JSON(file_path)
            return json_data["methods"][search_result]

        except:
            print("Problem with load JSON file")


    def read_JSON(self, path):
        # print(sublime.packages_path())
        # get the packages path 
        # path = sublime.packages_path() + "\\ToolTip\\python.sublime-tooltip"
        with open(path) as json_file:
                return json.load(json_file)


    def get_tooltip_file_path(self, a_dir, scope_name):
        # print("dir: " + a_dir)
        # get the files from the directory
        files_list = self.get_immediate_files(a_dir)
        # search json file by source
        for i in files_list:
            file = i.split('.')[0]
            # print("file: " + file)
            if file in scope_name:
                # print("file path: " + a_dir + i)
                return a_dir + i  
        return ""

    def get_immediate_files(self, a_dir):
        return [f for f in os.listdir(a_dir) if os.path.isfile(os.path.join(a_dir, f))]

