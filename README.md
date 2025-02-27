
# openPLM


openPLM is the first genuine open source PLM (Product Lifecycle Management)
based on Django intended to provide a starting point for companies
CMS/PLM/BIM projects. By integrating numerous standard reusable PLM
functionalities to take care of the things that companies have in common, it
lets you focus on what makes your company different. 

## Documentation

[Documentation](http://openplm.org/openplm.org/)
A documentation is available in the docs/ directory. It can be built using
Sphinx ( http://sphinx.pocoo.org ).

An online version is available at http://openplm.org/openplm.org/


Installation
============

#### Install Dependencies 
```bash
pip install requirements.txt
```

#### Migrate Db 
```bash 
python manage.py migrate
```

#### Run Server 
```bash 
python manage.py runserver 
```

Read the documentation!


License
=======

openPLM is distributed under the GNU General Public License version 3 or (at
your option) any later version.
See the file openPLM/GPLv3-LICENSE.txt.

Some javascript files (in openPLM/media/js) and css files (in openPLM/media/css)
comes from third parties.




