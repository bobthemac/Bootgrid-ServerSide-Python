# Flask-Bootgrid Server Side
Flask-Bootgrid is a simple class that allows for use of the bootgrid javascript libary, I wrote it for a project I was working on and thought it might be useful to others so decided to release it. The script is
writen to work with sqlalchemey and all basic features of bootgrid such as search, sort and pagination. I have atempted to make it as generic as posible if you need something more specific you can inherit the
class and change whats needed. Flask-Bootgrid is curently in use on one of my projects [Keg](https://keg.aperturedigital.uk) (if you want to see it in action you will need an account.)

# Installation
Curently installation is just a clone and import process as I am using this as a personal project and have it in my API file.

# Usage 
To use the script you need to create the class and call the functions they don't need to be called in any order but the JsonResponse method needs to be called last as this is where the query is actualy run.
You will then get your results formated to work directly with bootgrid and you can pass it straight to it. 
