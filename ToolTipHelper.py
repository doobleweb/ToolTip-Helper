import sublime
import sublime_plugin
import webbrowser
import logging
import hashlib
import json 
import time
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
            message += '<a href=\"%s\">See more</a>' % link
        return message

    @staticmethod
    def get_html_from_list(ordered_result):
        message = ""
        for item in ordered_result:
            key, value = item
            # if some attribute is empty, don't put him in the popup window
            if value and \
                key != 'link':
                message += '<b><u>' + key + ':</u></b><br>' + value + " <br><br>"
        return message

    @staticmethod
    def get_html_from_dictionary(json):
        message = ""
        for item in json:
            # if some attribute is empty, don't put him in the popup window
            if json[item] \
                and item != 'link':
                message += '<b><u>' + item + ':</u></b><br>' + json[item] + " <br><br>"
        return message

class EnterDataCommand(sublime_plugin.WindowCommand):
    """This class represent user interface to enter some data in settings file"""
    def __init__(self, view):
        self.view = view
        self.scope = None
        self.file_name = None
        self.link = None

    def run(self):
        if CURRENT_VERSION:
            sublime.active_window().show_input_panel("Enter your scope file here:", "", self.get_scope, None, None)

    def get_scope(self, user_input):
        # print("get scope input: " + user_input)
        if user_input.strip():
            self.scope = user_input
            # print("scope: " + self.scope)
            sublime.active_window().show_input_panel("Enter your file name here:", "", self.get_name, None, None)

    def get_name(self, user_input):
        if user_input.strip():
            self.file_name = user_input
            # print("file name: " + self.file_name)
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
            files.append({"file_name":self.file_name, "source":self.scope, "link":self.link})
            file_load.set("files", files)
            sublime.save_settings(file_settings)
            sublime.status_message("the changes was saved!")
        except Exception as e:
            sublime.status_message("cannot save the changes")            
      

class ToolTipHelperCommand(sublime_plugin.TextCommand):
    """This class represent tooltip window for showing documentation """
    def __init__(self, view):
        """ load settings """
        self.view = view
        self.settings = sublime.load_settings('ToolTipHelper.sublime-settings')
        self.files = self.settings.get("files")
        self.keyorder = self.get_keyorder()
        self.set_timeout = self.get_timeout()
        self.max_width = self.get_max_width()
        self.has_timeout = self.has_timeout()
        self.results_arr = []
        # self.__str__()

    def __str__(self):
        print(  "files: "       + str(self.files)       + '\n' +
                "keyorder: "    + str(self.keyorder)    + '\n' + 
                "set_timeout: " + str(self.set_timeout) + '\n' + 
                "has_timeout: " + str(self.has_timeout) + '\n' + 
                "max_width: "   + str(self.max_width))

    # def __del__(self):
    #     print("Object being destructed")

    def run(self, edit):
        if CURRENT_VERSION:
            # get the cursor point
            sel = self.view.sel()[0]
            # get the current scope by cursor position
            current_scope = self.view.scope_name(sel.begin())
            # print(current_file_source)
            tooltip_files_arr = self.get_tooltip_files(current_scope)
            # get user selection in string
            sel = self.get_user_selection(sel)
            # do match with user selection and return the result
            results = self.match_selection(sel, tooltip_files_arr)
            # print("len results: " + str(len(results)))
            for result in results:
                # get the correct link if there is 
                link = self.has_link(result)
                # edit the result in html for tooltip window
                html_tooltip = Utilities.result_format(result['json_result'], self.keyorder, link)
                self.results_arr.append(html_tooltip)
            # this names will be in the output panel
            names = self.get_file_names(results)
            # print("len results_arr: " + str(len(self.results_arr)))
            num_of_results = len(self.results_arr)
            if num_of_results == 1:
                self.show_tooltip_popup(self.results_arr[0])
            elif num_of_results > 1:
                sublime.active_window().show_quick_panel(names, self.on_done, sublime.MONOSPACE_FONT)

    def get_file_names(self, results):
        """ get string names for panel """
        names = []
        name_regex = r"(.+)\.sublime-tooltip"
        for name in results:
            # get the file name from the path
            file_name = os.path.basename(name['file_name'])
            try:
                file_name = re.match(name_regex, file_name).group(1)
            except Exception as e:
                logging.error('cannot match file name.')
            names.append(file_name)
        return names

    def has_link(self, result):
        """ get link if there is """
        if 'link' in result['json_result']:
            link = result['json_result']['link']
        elif 'link' in result:
            link = result['link']
        else:
            link = ""
        return link

    def on_done(self, index):
        """ when choosing item it will open popup in the given index """
        self.show_tooltip_popup(self.results_arr[index])

    def show_tooltip_popup(self, search_result):
        """ open the poup with limit of time """
        if self.has_timeout:
            # set timout to 10 seconds, in the end hide the tooltip window
            sublime.set_timeout(lambda:self.view.hide_popup(), self.set_timeout)
        # open popup window in the current cursor
        show_popup(self.view, 
                    search_result, 
                    on_navigate=self.on_navigate, 
                    max_width=self.max_width)
        self.results_arr = []

    def on_navigate(self, href):
        """ open the link in a new tab on web browser """
        try:
            webbrowser.open_new_tab(href)
        except Exception as e:
            logging.error('cannot open link on web browser.')

    def get_user_selection(self, sel):
        """ get user selection and return her in string"""
        # get the whole word from this point
        get_word = self.view.word(sel)
        # get the word in string
        get_word_str = self.view.substr(get_word)
        # print("selected word:" + get_word_str)
        return get_word_str.strip()

    def match_selection(self, sel, tooltip_files):
        """ this method take care to the results, links and the keys which be implemented in the tooltip """
        results = []
        count = 0

        for file in tooltip_files:
            result = {}
            # search the parameter in json file
            json_result = self.search_in_json(sel, file['file_name'])
            # print("json_result: " + str(json_result))
            if json_result:
                result['json_result'] = json_result
                result['file_name'] = file['file_name']
                # get the correct link for the result
                if 'link' not in json_result and \
                    'link' in file:
                    result['link'] = file['link']
                results.append(result)
                # get the keys from the result
                keys = list(json_result.keys())
                # add key to keyorder and count the change
                count += self.update_keyorder_list(keys)
        # if there is one change, save it in settings.
        if count != 0:
            self.save_keyorder_list()
        return results

    def update_keyorder_list(self, keys):
        """ add key to key order list """
        count = 0

        for key in keys:
            if key not in self.keyorder:
                count += 1
                self.keyorder.append(key)
        return count

    def save_keyorder_list(self):
        """ save the new keyorder in settings """
        file_settings = 'ToolTipHelper.sublime-settings'
        file_load = sublime.load_settings(file_settings)
        file_load.set("keyorder", self.keyorder)
        sublime.save_settings(file_settings)
    
    def search_in_json(self, search_result, file_path):
        """ find specific result in json file """
        try:
            json_data = self.read_JSON(file_path)
            # print("json_data:" + json_data)
            return json_data[search_result]
        except Exception as e:
            logging.error('Documentation not exist in: ' + file_path)
            return {}

    def read_JSON(self, path):
        """ read json file from the given path """
        # print("read json from: " + path)
        with open(path, encoding="utf8") as json_file:
            try:
                data = json.load(json_file)
                # print("json load success")
            except Exception as e:
                logging.error('cannot load JSON file from: ' + path)
            return data

    def get_tooltip_files(self, current_scope):
        """ get all files paths which have the current scope """
        files = self.get_immediate_files()
        relative_path = sublime.packages_path() + '\\ToolTipHelper\\'
        tooltip_files = []

        if files:
            for file in files:  
                if file['source'] in current_scope:
                    full_path = relative_path + file['file_name']
                    # replace the file name with full path
                    file['file_name'] = full_path
                    tooltip_files.append(file)
        logging.info("Checking the files: " + str(tooltip_files))      
        return tooltip_files
        
    def get_immediate_files(self):
        """ get the files from settings """
        try:
            file_settings = 'ToolTipHelper.sublime-settings'
            file_load = sublime.load_settings(file_settings)
            files = file_load.get("files")
            # print("files from settings: " + str(files))
        except Exception as e:
            logging.error('cannot loads the files from settings')
            files = []
        return files

    def get_keyorder(self):
        """ get keyorder from settings """
        try:
            value = self.settings.get("keyorder")
            keyorder = value if value != None else []
        except:
            keyorder = []
        return keyorder
  
    def get_timeout(self):
        """ get timeout from settings """
        try:
            value = int(self.settings.get("set_timeout"))
            set_timeout = value if value != None and value > 0 else 10000
        except:
            set_timeout = 10000
        return set_timeout

    def has_timeout(self):
        """ get timeout condition settings """
        try:
            value = bool(self.settings.get("has_timeout")) 
            has_timeout = value if value != None else True 
        except:
            has_timeout = True
        return has_timeout

    def get_max_width(self):
        """ get width from settings """
        try:
            value = int(self.settings.get("max_width"))
            max_width = value if value != None and value > 0 else 350 
        except:
            max_width = 350
        return max_width




"""Credit to: https://github.com/huot25/StyledPopup"""
from plistlib import readPlistFromBytes

def show_popup(view, content, *args, **kwargs):
    """Parse the color scheme if needed and show the styled pop-up."""

    if view == None:
        return

    manager = StyleSheetManager()
    color_scheme = view.settings().get("color_scheme")

    style_sheet = manager.get_stylesheet(color_scheme)["content"]

    html = "<html><body>"
    html += "<style>%s</style>" % (style_sheet)
    html += content
    html += "</body></html>"

    view.show_popup(html,  *args, **kwargs)


class StyleSheetManager():
    """Handles loading and saving data to the file on disk as well as provides a simple interface for"""
    """accessing the loaded style sheets. """
    style_sheets = {}

    def __init__(self):
        self.theme_file_path = os.path.join(sublime.packages_path(), "User", "scheme_styles.json")
        self.resource_path = "/".join(["Packages", "User", "scheme_styles.json"])
        self.style_sheets = {}
        settings = sublime.load_settings("Preferences.sublime-settings")
        self.cache_limit = settings.get("popup_style_cache_limit", 5)

    def is_stylesheet_parsed_and_current(self, color_scheme):
        """Parse the color scheme if needed or if the color scheme file has changed."""

        if not self.has_stylesheet(color_scheme) or not self.is_file_hash_stale(color_scheme):
            return False

        return True

    def load_stylesheets_content(self):
        """Load the content of the scheme_styles.json file."""

        content = ""
        if  os.path.isfile(self.theme_file_path):
            content = sublime.load_resource(self.resource_path)

        return content

    def get_stylesheets(self):
        """Get the stylesheet dict from the file or return an empty dictionary no file contents."""

        if not len(self.style_sheets):
            content = self.load_stylesheets_content()
            if  len(content):
                self.style_sheets = sublime.decode_value(str(content))

        return self.style_sheets

    def count_stylesheets(self):
        return len(self.get_stylesheets())

    def save_stylesheets(self, style_sheets):
        """Save the stylesheet dictionary to file"""

        content = sublime.encode_value(style_sheets, True)

        with open(self.theme_file_path, "w") as f:
            f.write(content)

        self.style_sheets = style_sheets

    def has_stylesheet(self, color_scheme):
        """Check if the stylesheet dictionary has the current color scheme."""

        if color_scheme in self.get_stylesheets():
            return True

        return False

    def add_stylesheet(self, color_scheme, content):
        """Add the parsed color scheme to the stylesheets dictionary."""

        style_sheets = self.get_stylesheets()

        if (self.count_stylesheets() >= self.cache_limit):
            self.drop_oldest_stylesheet()

        file_hash = self.get_file_hash(color_scheme)
        style_sheets[color_scheme] = {"content": content, "hash": file_hash, "time": time.time()}
        self.save_stylesheets(style_sheets)

    def get_stylesheet(self, color_scheme):
        """Get the supplied color scheme stylesheet if it exists."""
        active_sheet = None

        if not self.is_stylesheet_parsed_and_current(color_scheme):
            scheme_css = SchemeParser().run(color_scheme)
            self.add_stylesheet(color_scheme, scheme_css)

        active_sheet = self.get_stylesheets()[color_scheme]


        return active_sheet

    def drop_oldest_stylesheet(self):
        style_sheets = self.get_stylesheets()

        def sortByTime(item):
            return style_sheets[item]["time"]

        keys = sorted(style_sheets, key = sortByTime)

        while len(style_sheets) >= self.cache_limit:
            del style_sheets[keys[0]]
            del keys[0]

        self.save_stylesheets(style_sheets)

    def get_file_hash(self, color_scheme):
        """Generate an MD5 hash of the color scheme file to be compared for changes."""

        content = sublime.load_binary_resource(color_scheme)
        file_hash = hashlib.md5(content).hexdigest()
        return file_hash

    def is_file_hash_stale(self, color_scheme):
        """Check if the color scheme file has changed on disk."""

        stored_hash = ""
        current_hash = self.get_file_hash(color_scheme)
        styles_heets = self.get_stylesheets()

        if color_scheme in styles_heets:
            # stored_hash = styles_heets[color_scheme]["hash"]
            stored_hash = styles_heets[color_scheme]["hash"]

        return (current_hash == stored_hash)


class SchemeParser():
    """Parses color scheme and builds css file"""

    def run(self, color_scheme):
        """Parse the color scheme for the active view."""

        print ("Styled Popup: Parsing color scheme")

        content = self.load_color_scheme(color_scheme)
        scheme = self.read_scheme(content)
        css_stack = StackBuilder().build_stack(scheme["settings"])
        style_sheet = self.generate_style_sheet_content(css_stack)
        return style_sheet

    def load_color_scheme(self, color_scheme):
        """Read the color_scheme user settings and load the file contents."""

        content  = sublime.load_binary_resource(color_scheme)
        return content

    def read_scheme(self, scheme):
        """Converts supplied scheme(bytes) to python dict."""

        return  readPlistFromBytes(scheme)

    def generate_style_sheet_content(self, properties):
        file_content = ""
        formatted_properties = []
        sorted(properties, key=str.lower)

        for css_class in properties:
            properties_string = CSSFactory.generate_properties_string(css_class, properties)
            formatted_properties.append("%s { %s } " % (css_class, properties_string))

        file_content = "".join(formatted_properties)

        return file_content


class StackBuilder():
    stack = {}

    def __init__(self):
        self.clear_stack()

    def clear_stack(self):
        self.stack = {}

    def is_valid_node(self, node):
        if "settings" not in node:
            return False

        if not len(node["settings"]):
            return False

        return True

    def is_base_style(self, node):
        if "scope" in node:
            return False

        return True

    def build_stack(self, root):
        """Parse scheme dictionary into css classes and properties."""

        self.clear_stack()
        for node in root:
            css_properties = {}

            if not self.is_valid_node(node):
                continue

            styles = node["settings"]
            css_properties = self.generate_css_properties(styles)

            if not len(css_properties):
                continue

            if self.is_base_style(node):
                if "html" not in self.stack:
                    self.set_base_style(css_properties)
            else:
                classes = self.get_node_classes_from_scope(node["scope"])
                classes = self.filter_non_supported_classes(classes)
                self.apply_properties_to_classes(classes, css_properties)

        return self.stack

    def generate_css_properties(self, styles):
        properties = {}
        for key in styles:
            for value in styles[key].split():
                new_property = CSSFactory.generate_new_property(key, value)
                properties.update(new_property)

        return properties

    def set_base_style(self, css_style):
        css_background_property = CSSFactory.CSS_NAME_MAP["background"]
        css_style[css_background_property] = ColorFactory().getTintedColor(css_style[css_background_property], 10)
        self.stack["html"] = css_style

    def apply_properties_to_classes(self, classes, properties):
        for css_class in classes:
            css_class = css_class.strip()
            if (not css_class.startswith(".")):
                css_class = "." + css_class

            self.set_class_properties(css_class, properties)

    def set_class_properties(self, css_class, properties):
        self.stack[css_class] = properties

    def get_node_classes_from_scope(self, scope):
        scope = "." + scope.lower().strip()
        scope = scope.replace(" - ","")
        scope = scope.replace(" ", ",")
        scope = scope.replace("|",",")
        scopes = scope.split(",")
        return scopes

    def filter_non_supported_classes(self, in_classes):
        out_classes = []
        regex = r"""\A\.(
                comment(\.(line(\.(double-slash|double-dash))?|block(\.documentation)?))?|
                constant(\.(numeric|character(\.escape)?|language|other))?|
                entity(\.(name(\.(function|type|tag|section))?|other(\.(inherited-class|attribute-name))?))?|
                invalid(\.(illegal|deprecated))?|
                keyword(\.(control|operator|other))?|
                markup(\.(underline(\.(link))?|bold|heading|italic|list(\.(numbered|unnumbered))?|quote|raw|other))?|
                meta|
                storage(\.(type|modifier))?|
                string(\.(quoted(\.(single|double|triple|other))?|unquoted|interpolated|regexp|other))?|
                support(\.(function|class|type|constant|variable|other))?|
                variable(\.(parameter|language|other))?)"""

        for css_class in in_classes:
            match = re.search(regex, css_class, re.IGNORECASE + re.VERBOSE) 
            if (match):
                out_classes.append(css_class)

        return out_classes

class CSSFactory():

    CSS_NAME_MAP = {
        "background": "background-color",
        "foreground": "color"
    }

    CSS_DEFAULT_VALUES = {
        "font-style": "normal",
        "font-weight": "normal",
        "text-decoration": "none"
    }

    @staticmethod
    def generate_new_property(key, value):
        new_property = {}
        value = value.strip()

        property_name = CSSFactory.get_property_name(key, value)

        if (property_name == None):
            return new_property

        if len(value):
            new_property[property_name] = value
        else:
            new_property[property_name] = CSSFactory.get_property_default(property_name, value)

        return new_property

    @staticmethod
    def generate_properties_string(css_class, dict):
        """Build a list of css properties and return as string."""

        property_list = []
        properties = ""
        for prop in dict[css_class]:
            property_list.append("%s: %s; " % (prop, dict[css_class][prop]))

        properties = "".join(property_list)

        return properties

    @staticmethod
    def get_property_name(name, value):
        """Get the css name of a scheme value if supported."""

        # fontStyle can be mapped to font-style and font-weight. Need to handle both
        if name == "fontStyle":
            if value == "bold":
                return "font-weight"

            if value == "underline":
                return "text-decoration"

            return "font-style"

        if name in CSSFactory.CSS_NAME_MAP:
            return CSSFactory.CSS_NAME_MAP[name]

        return None

    @staticmethod
    def get_property_default(prop):
        if prop in CSSFactory.CSS_DEFAULT_VALUES:
            return CSSFactory.CSS_DEFAULT_VALUES[prop]

        return None

class ColorFactory():
    """Helper class responsible for all color based calculations and conversions."""

    def getTintedColor(self, color, percent):
        """Adjust the average color by the supplied percent."""

        rgb = self.hex_to_rgb(color)
        average = self.get_rgb_average(rgb)
        mode = 1 if average < 128 else -1

        delta = ((256 * (percent / 100)) * mode)
        rgb = (rgb[0] + delta, rgb[1] + delta, rgb[2] + delta)
        color = self.rgb_to_hex(rgb)

        return color

    def get_rgb_average(self, rgb):
        """Find the average value for the curren rgb color."""

        return int( sum(rgb) / len(rgb) )

    def hex_to_rgb(self, color):
        """Convert a hex color to rgb value"""

        hex_code = color.lstrip("#")
        hex_length = len(hex_code)

        #Break the hex_code into the r, g, b hex values and convert to decimal values.
        rgb = tuple(int(hex_code[i:i + hex_length // 3], 16) for i in range(0,hex_length,hex_length //3))

        return rgb

    def rgb_to_hex(self, rgb):
        """ Convert the supplied rgb tuple into hex color value"""

        return "#%02x%02x%02x" % rgb


class StyleSheet():
    content=""
    hash=""
    time=0
