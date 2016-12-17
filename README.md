# ToolTip-Helper

Author: Idan Avitan

Credit to: Dooble

This plugin shows tooltip under the cursor or on mouse hover when on function name in sublime text 3.
Works on every language (include custom languages).

## Features

<ul>
  <li>Comes with documentation for HTML, CSS and Sublime API (Python).</li>
  <li>Write your own documentation above function definition.</li>
  <li>Define more than one documentation file to the same language scope.</li>
  <li>Tooltip window change his color accord to the current theme in sublime.</li>
  <li>Determine the order of the attributes in tooltip window.</li>
  <li>Control on settings like: window size, timeout, debug mode.</li>
  <li>Go to documentation definition.</li>
  <li>Go to documentation website.</li>
  <li> CSS control from the settings file.</li>
</ul>

<b>Built-in Doc</b>

<img src="http://s28.postimg.org/op1xxk9j1/tooltip.png" alt="tooltip">

<b>Dynamic Doc</b>

<img src="http://s16.postimg.org/67ub24hnp/tool.png" alt="dynamic doc">

## How does it work?

There are two ways to create documentation: <u>Built-in files</u> & <u>Dynamic doc</u>.

<b>For Built-in files:</b>
<ul>
  <li>Make sure you have in packages ToolTipHelper\db folder.<li>
  <li>Create <code>languageName.sublime-tooltip</code> (JSON file) in this folder.</li>
  <li>Declare on this file in settings with his scope name</li>
</ul>

Once you create <code>languageName.sublime-tooltip</code> and declare on him, the tooltip knows to search for documentation and take the data from there and shows popup window.
This file contain every attribute name that you want show up in the tooltip window. For example attributes names for function can be: method name, parameters, description and return value.

<b>NOTE:</b> JSON file needs to be clean from some characters that can cause him to error. 
You can use <a href="http://jsonlint.com/">this site</a> to check if your file is valid.

<u>Here is example of sublime API documentation:</u>
<img src="http://s10.postimg.org/t1ecgy9vt/json_example.png" alt="sublime api">

Some important things about file format:


<img src="http://s29.postimg.org/9vvxfurtz/rules.png" alt="sublime api">

<b>For Dynamic doc:</b>

- Choose a function.
-  Write doc tag streight above the function.
- Add some attributes between the tag when each key and value separated by a colon.


<img src="http://s30.postimg.org/69jhxq6wh/dynamic.png" alt="sublime api">

<b>Note:</b> in case we have more than one documentation for function name, a quick panel will open with list of results.
Each result show with row number and name of the file, when chosing result the tooltip window get opened.
You can run the tooltip again and the last result you pick up will be highlighted.

<img src="http://s29.postimg.org/9qlvlsdsn/image.png" alt="sublime api">


## Setup

Make sure you have <a href="https://packagecontrol.io/installation" alt="packagecontrol">Package Control</a> before continue (you can still download ZIP of the project from GitHub if you don't want to install package control, but its not recommended).


To add the ToolTip Helper Package to Sublime, you first need to add a new repository to your package manager. To do so, while in sublime, open the Command Palette. To open the palette, press <code>ctrl+shift+p</code> (Win, Linux) or <code>cmd+shift+p</code> (OS X).
There, you should search "Add Repository": 

<img src="http://s12.postimg.org/iv5k5nwul/add_repo.png" alt="add repo">

After that, you need paste this link: https://github.com/doobleweb/ToolTip-Helper.git and press enter.
<img src="http://s9.postimg.org/vu5pvg467/url_dooble.png" alt="add link">

Once the repository added you need to install the package. To do so open again palette (ctrl+shift+p) and search "Install Package" and press enter.

<b>NOTE:</b> It is recommended to re-open sublime text after the installation finished.

Make sure you have folder named <b>ToolTip-Helper\db</b> in packages (Preferences>>Browse packages). This folder must contain <code>languageName.sublime-tooltip</code> files.
See also default settings file <code>ToolTipHelper.sublime-settings</code>.
You can find this file in ToolTip-Helper folder or go to the menu Preferences>>tooltip helper>>settings - default.

<img src="http://s16.postimg.org/s7t72j4o5/settings.png" alt="settings">

As you can see this file contain array of documentaiton files for each language.
Every item must include <b>scope</b> and <b>file_name</b> like in the img.

<ul>
  <li> Scope - the scope name must be valid otherwise it won't work. If you don't know how write a valid scope you can see the <code>scopes.txt</code> file in git project or press <code>ctrl+alt+shift+p</code> in sublime text (you see the scope name in the status bar).
  <li> File Name - include the <code>languageName.sublime-tooltip</code> file name. This array of files is the way of the tooltip to know if search this files in <b>"ToolTipHelper\db"</b> folder.
  <li> Link - you can write link to documentation site for another information (The link is optional).
</ul>

<b>NOTE:</b> There are two places you can put links: in the settings file or\and in the json file as "link" attribute.
The tooltip will choose the most "inner" link if there is one.

To override the default settings You can open file in <code>packages\user\ToolTipHelper.sublime-settings</code> or go to the menu Preferences>>tooltip helper>>settings - user.

## Enter data via user interface

If you create <code>languageName.sublime-tooltip</code> in the db folder and you want shortcut to declare him, use this way.

To run this command you have 3 ways:
-  Open the palette, press <code>ctrl+shift+p</code> and choose 'Tooltip helper insert data to settings'.
-  Preferences>>tooltip helper>>enter data.
-  Ctrl+7.

<img src="http://s23.postimg.org/vp1v4vdyz/image.png" alt="1">
<img src="http://s11.postimg.org/peulug8yr/image.png" alt="2">

In case you dont want give a link, just press on enter.

<img src="http://s13.postimg.org/ui8grveuv/image.png" alt="3">

Currently, the plugin works with <code>F1</code> or command pallete. If you want to change it, go to Preferences>>key bindings-user.

## Future Goals:
<ul> 
  <li> Go To Documentation in built-in files.
</ul>
