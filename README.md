# ToolTip-Helper

Author: Idan Avitan

This plugin shows tooltip under the cursor when he on functions in sublime text 3.
The functions can be in every language you choose.

<img src="http://s29.postimg.org/9gworxjlj/tooltip.png" alt="tooltip">

## How it works?
It's very simple, you need to enter some data in JSON file <code>languageName.sublime-tooltip</code> and the tooltip takes the data from there and shows popup window.
This file contain every attribute that you want show up in the tooltip window. For example attributes for function can be: method name, parameters, description and return value (the attributes can be whatever you want).

<b>NOTE:</b> JSON file needs to be clean from some characters that can cause him to error. 
You can use <a href="http://jsonlint.com/">this site</a> to check if your file is valid.

<u>Here is example of sublime API documentation:</u>
<img src="http://s10.postimg.org/t1ecgy9vt/json_example.png" alt="sublime api">

## Setup

Make sure you have <a href="https://packagecontrol.io/installation" alt="packagecontrol">Package Control</a> before continue (you can still download ZIP of the project from GitHub if you don't want to install package control, but its not recommended).


To add the ToolTip Helper Package to Sublime, you first need to add a new repository to your package manager. To do so, while in sublime, open the Command Palette. To open the palette, press <code>ctrl+shift+p</code> (Win, Linux) or <code>cmd+shift+p</code> (OS X).
There, you should search "Add Repository": 

<img src="http://s12.postimg.org/iv5k5nwul/add_repo.png" alt="add repo">

After that, you need paste this link: https://github.com/doobleweb/ToolTip-Helper.git and press enter.
<img src="http://s9.postimg.org/vu5pvg467/url_dooble.png" alt="add link">

Once the repository added you need to install the package. To do so open again palette (ctrl+shift+p) and search "Install Package" and press enter.

<b>NOTE:</b> It is recommended to re-open sublime text after the installation finished.

Open folder named <b>ToolTipHelper</b> in packages (Preferences>>Browse packages). This folder must contain <code>languageName.sublime-tooltip</code> files.
In order to get plugin works you need to add some settings to <code>ToolTipHelper.sublime-settings</code> file.
You can find this file in Packages\User folder or in the menu Preferences>>tooltip helper>>settings - user.

<img src="http://s22.postimg.org/a0e4wb5nl/settings.png" alt="settings">

As you can see this file contain array of documentaiton files for each language.
Every item must include <b>source</b> and <b>file_name</b> like in the img.

<ul>
  <li> Source - the source name must be valid otherwise it won't work. If you don't know how write valid source you can see the <code>scopes.txt</code> file in my git project or press <code>ctrl+alt+shift+p</code> in sublime text (you see the scope name in the status bar).
  <li> File Name - include the <code>languageName.sublime-tooltip</code> file name. This files names is the way of the tooltip to know if search this files in <b>"ToolTipHelper"</b> folder.
  <li> Link - you can write link to documentation site for another information (The link is optional).
</ul>

<b>NOTE:</b> There are two places to you can put links: in the settings file or\and in the json file as "link" attribute.
The tooltip will choose the most "inner" link if there is one.


Currently, the plugin works with <code>F1</code>. If you want to change it,  go to Preferences>>key bindings-user.

## Future Goals:
<ul> 
  <li> User interface for manage the settings file.
  <li> CSS design to tooltip window.
  <li> Get tooltip on your functions documentation.
  <li> Change timeout, popup window width and so on in settings file.
</ul>
