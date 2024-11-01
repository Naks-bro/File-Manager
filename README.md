# File-Manager

Project Modules: 
 
I. User Interface Module  
 
This module is responsible for creating and managing the user interface of the application. It 
includes functions like createWindow(), create_widgets(window), and main(). The 
createWindow() function sets up the main window of the application, including its title, size, 
and icon. The create_widgets(window) function creates all the widgets that are used in the 
application, such as buttons, labels, and entries. The main() function is the entry point of the 
application, which calls the other functions to set up the window and start the main event 
loop. 
 
II. Sort Module 
 
The sort module includes the sort_col(col, reverse), sort_key_dates(item), and 
sort_key_size(item) functions. These functions are used to sort the items in the Treeview 
widget based on different criteria like name, type, date modified, and size. The sort_col(col, 
reverse) function sorts the items based on the column specified. The sort_key_dates(item) and 
sort_key_size(item) functions are helper functions used to sort the items based on the date 
modified and size, respectively. 
 
III. Custom Tagging Module 
 
This module allows users to tag files with different colors. It includes functions like 
tag_popup(tag_type), untag_popup(), update_tag(), and read_tag(). The tag_popup(tag_type) 
function shows a popup for the user to tag a selected file. The untag_popup() function shows a 
popup for the user to remove a tag from a selected file. The update_tag() function updates the 
tag information in a JSON file. The read_tag() function reads the tag information from a 
JSON file. 
 

 
IV. Timely Deletion Module  
 
The timely deletion module includes the del_file_popup(), del_dup_popup(), 
del_tag_popup(del_upto), wrap_del(event), and del_file(file_name:str) functions. These 
functions provide the functionality to delete selected files, delete duplicate files, and delete 
tagged files after a certain period. The del_file_popup() function shows a popup for the user 
to confirm the deletion of a selected file. The del_dup_popup() function shows a popup for 
the user to confirm the deletion of duplicate files. The del_tag_popup(del_upto) function 
deletes tagged files after a certain period. 
 
V. File Operation Module 
 
This module handles file operations like copying, pasting, and renaming files. It includes 
functions like copy(), paste(), rename_popup(), and new_file_popup(). These functions handle 
tasks such as copying a selected file to a temporary path, pasting a file from the temporary 
path to the current directory, renaming a selected file, and creating a new file. 
 
VI. Directory Operations Module 
 
This module handles directory operations like creating and navigating directories. It includes 
functions like cd_drive(drive, queryNames), previous(), next(), and new_dir_popup(). These 
functions handle tasks such as changing the current directory to a selected drive, navigating to 
the previous directory, navigating to the next directory, and creating a new directory. 
 
 
VII. Search Module  
 
This module handles the search functionality of the application. It includes the 
search(searchEntry, event) function which takes a query from the search entry and filters the 
file names based on the query. 
 
 
 
 
VIII. Event Handling Module 
 
This module handles the events like double-clicking an item, right-clicking an item, and 
pressing keys. It includes functions like onDoubleClick(event=None), onRightClick(m, 
event), selectItem(event), up_key(event), and down_key(event). These functions handle tasks 
such as opening a file or directory on double-click, showing a context menu on right-click, 
selecting an item on left-click, and navigating up and down the items list 
using the arrow keys.

![image](https://github.com/user-attachments/assets/ffd5a349-153c-4c62-a470-bf01a204f699)
![image](https://github.com/user-attachments/assets/1098d7ed-9bbc-4840-8f94-2c793f2e637f)
![image](https://github.com/user-attachments/assets/b31836f4-9da3-427e-9a90-9d36a8226ab9)
![image](https://github.com/user-attachments/assets/985c52bf-7dee-4452-8a82-c68962a892d6)
![image](https://github.com/user-attachments/assets/a6ab00ac-2fec-40d9-9bfc-71efdf9e35b8)
![image](https://github.com/user-attachments/assets/00fc48b7-c7f9-4502-a068-1345b6557c44)
![image](https://github.com/user-attachments/assets/255967c1-b437-42ed-a446-1f57e70f43c5)
![image](https://github.com/user-attachments/assets/2f4824a0-a986-4f51-b904-906cde88eaaa)
![image](https://github.com/user-attachments/assets/a7be333f-53fb-481c-bc6b-fc2a4ecebc06)
