"""
This modules contains all stuff related to the api

.. seealso:: The public api :mod:`http_api`,
"""

import functools
import traceback
import sys

import django.forms
from django.shortcuts import get_object_or_404
from django.utils import simplejson
from django.core.mail import mail_admins
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.contrib.csrf.middleware import csrf_exempt

import openPLM.plmapp.models as models
from openPLM.plmapp.controllers import get_controller
import openPLM.plmapp.forms as forms
from openPLM.plmapp.utils import get_next_revision

#: Version of the API (value: ``'1.0'``)
API_VERSION = "1.0"
#: Decorator whichs requires that the user is login
api_login_required = user_passes_test(lambda u: u.is_authenticated(), 
                                      login_url="/api/needlogin/")

def json_view(func):
    """
    Decorator which converts the result from *func* into a json response.
    
    The result from *func* must be serializable by :mod:`django.utils.simple_json`
    
    This decorator automatically adds a ``result`` field to the response if it
    was not present. Its value is ``'ok'`` if no exception was raised, and else,
    it is ``'error'``. In that case, a field ``'error'`` is had with a short
    message describing the exception.
    """
    @functools.wraps(func)
    def wrap(request, *a, **kw):
        response = None
        try:
            response = dict(func(request, *a, **kw))
            if 'result' not in response:
                response['result'] = 'ok'
        except KeyboardInterrupt:
            # Allow keyboard interrupts through for debugging.
            raise
        except Exception, e:
            #Mail the admins with the error
            exc_info = sys.exc_info()
            subject = 'JSON view error: %s' % request.path
            try:
                request_repr = repr(request)
            except:
                request_repr = 'Request repr() unavailable'
            message = 'Traceback:\n%s\n\nRequest:\n%s' % (
                '\n'.join(traceback.format_exception(*exc_info)),
                request_repr,
                )
            mail_admins(subject, message, fail_silently=True)
            #Come what may, we're returning JSON.
            msg = _('Internal error')+': '+str(e)
            response = {'result': 'error',
                        'error': msg}
        response["api_version"] = API_VERSION
        json = simplejson.dumps(response)
        return HttpResponse(json, mimetype='application/json')
    return wrap

#: Decorator which requires a login user and converts returned value into a json response
login_json = lambda f: csrf_exempt(api_login_required(json_view(f)))


def get_obj_by_id(obj_id, user):
    u"""
    Returns an adequate controller for the object identify by *obj_id*.
    The returned controller is instanciate with *user* as the user
    who modify the object.

    :param obj_id: id of a :class:`.PLMObject`
    :param user: a :class:`.django.contrib.auth.models.User`
    :return: a subinstance of a :class:`.PLMObjectController`
    """

    obj = get_object_or_404(models.PLMObject, id=obj_id)
    obj = models.get_all_plmobjects()[obj.type].objects.get(id=obj_id)
    return get_controller(obj.type)(obj, user)

def object_to_dict(plmobject):
    """
    Returns a dictionary representing *plmobject*. The returned dictionary
    respects the format described in :ref`http-api-object`
    """
    return dict(id=plmobject.id, name=plmobject.name, type=plmobject.type,
                revision=plmobject.revision, reference=plmobject.reference)

@json_view
def need_login(request):
    """ Helper function for :func:`api_login_required` """
    return {'result' : 'error', 'error' : 'user must be login'}

@login_json
def get_all_types(request):
    """
    Returns all the subtypes of :class:`.PLMObject` managed by the server.

    :implements: :func:`http_api.types`
    """
    return {"types" : sorted(models.get_all_plmobjects().keys())}

@login_json
def get_all_docs(request):
    """
    Returns all  the types of :class:`.Document` managed by the server.

    :implements: :func:`http_api.docs`
    """
    return {"types" : sorted(models.get_all_documents().keys())}

@login_json
def get_all_parts(request):
    """
    Returns all the types of :class:`.Part` managed by the server.

    :implements: :func:`http_api.parts`
    """
    return {"types" : sorted(models.get_all_parts().keys())}

@login_json
def search(request):
    """
    Returns all objects matching a query.

    :implements: :func:`http_api.search`
    """
    if request.GET and "type" in request.GET:
        attributes_form = forms.type_form(request.GET)
        if attributes_form.is_valid():
            query_dict = {}
            cls = models.get_all_plmobjects()[attributes_form.cleaned_data["type"]]
            extra_attributes_form = forms.get_search_form(cls, request.GET)
            results = cls.objects.all()
            if extra_attributes_form.is_valid():
                results = extra_attributes_form.search(results)
                objects = []
                for res in results:
                    objects.append(object_to_dict(res))
                return {"objects" : objects} 
    return {"result": "error"}

@login_json
def create(request):
    """
    Creates a :class:`.PLMObject` and returns it

    :implements: :func:`http_api.create`
    """
    try:
        type_name = request.POST["type"]
        cls = models.get_all_plmobjects()[type_name]
    except KeyError:
        return {"result" : "error", 'error' : 'bad type'}
    form = forms.get_creation_form(cls, request.POST)
    if form.is_valid():
        controller_cls = get_controller(type_name)
        controller = controller_cls.create_from_form(form, request.user)
        ret = {"object" : object_to_dict(controller)}
        return ret
    else:
        return {"result" : "error", "error" : form.errors.as_text()}

@login_json
def get_files(request, doc_id, all_files=False):
    """
    Returns the list of files of the :class:`.Document` identified by *doc_id*.
    If *all_files* is False (the default), only unlocked files are returned.

    :implements: :func:`http_api.files`
    
    :param request: the request
    :param doc_id: id of a :class:`.Document`
    :param all_files: boolean, False if only unlocked files should be returned
    :returned fields: files, a list of files (see :ref:`http-api-file`) 
    """

    document = models.Document.objects.get(id=doc_id)
    document = models.get_all_plmobjects()[document.type].objects.get(id=doc_id)
    files = []
    for df in document.files:
        if all_files or not df.locked:
            files.append(dict(id=df.id, filename=df.filename, size=df.size))
    return {"files" : files}

@login_json
def check_out(request, doc_id, df_id):
    """
    Locks the :class:`.DocumentFile` identified by *df_id* from
    the :class:`.Document` identified by *doc_id*.

    :implements: :func:`http_api.lock`
    
    :param request: the request
    :param doc_id: id of a :class:`.Document`
    :param df_id: id of a :class:`.DocumentFile`
    :returned fields: None 
    """
    doc = get_obj_by_id(doc_id, request.user)
    df = models.DocumentFile.objects.get(id=df_id)
    doc.lock(df)
    return {}


@login_json
def check_in(request, doc_id, df_id):
    """
    Checks-in the :class:`.DocumentFile` identified by *df_id* from
    the :class:`.Document` identified by *doc_id*

    :implements: :func:`http_api.check_in`
    
    :param request: the request
    :param doc_id: id of a :class:`.Document`
    :param df_id: id of a :class:`.DocumentFile`
    :returned fields: None
    """
    doc = get_obj_by_id(doc_id, request.user)
    df = models.DocumentFile.objects.get(id=df_id)
    form = forms.AddFileForm(request.POST, request.FILES)
    if form.is_valid():
        doc.checkin(df, request.FILES['filename'])
    return {}

@login_json
def is_locked(request, doc_id, df_id):
    """
    Returns True if the :class:`.DocumentFile` identified by *df_id* from
    the :class:`.Document` identified by *doc_id* is locked.

    :implements: :func:`http_api.is_locked`
    
    :param request: the request
    :param doc_id: id of a :class:`.Document`
    :param df_id: id of a :class:`.DocumentFile`
    :returned fields: locked, True if the file is locked.
    """

    doc = get_obj_by_id(doc_id, request.user)
    df = models.DocumentFile.objects.get(id=df_id)
    return {"locked" : df.locked}

@login_json
def unlock(request, doc_id, df_id):
    """
    Unlocks the :class:`.DocumentFile` identified by *df_id* from
    the :class:`.Document` identified by *doc_id*.

    :implements: :func:`http_api.unlock`
    
    :param request: the request
    :param doc_id: id of a :class:`.Document`
    :param df_id: id of a :class:`.DocumentFile`
    :returned fields: None 
    """
    doc = get_obj_by_id(doc_id, request.user)
    df = models.DocumentFile.objects.get(id=df_id)
    if df.locked:
        doc.unlock(df)
    return {}

def field_to_type(field):
    """
    Converts *field* (a django FormField) to a type as described in
    :ref:`http-api-types`.
    """
    types = {django.forms.IntegerField : "int",
             django.forms.DecimalField : "decimal",
             django.forms.FloatField : "float",
             django.forms.BooleanField : "boolean",
             django.forms.ChoiceField : "choice",
           }
    if type(field) in types:
        return types[type(field)]
    for key in types:
        if isinstance(field, key):
            return types[key]
    return "text"

def get_fields_from_form(form):
    """
    Returns a list of fields from *form* converted to the format described in
    :ref:`http-api-fields`.
    """
    fields = []
    for field_name, field in form.fields.items():
        data = dict(name=field_name, label=field.label, initial=field.initial)
        if callable(field.initial):
            data["initial"] = field.initial()
            if hasattr(data["initial"], "pk"):
                data["initial"] = data["initial"].pk
        data["type"] = field_to_type(field)
        if hasattr(field, "choices"):
            data["choices"] =  tuple(field.choices)
        for attr in ("min_value", "max_value", "min_length", "max_length"):
            if hasattr(field, attr):
                data[attr] = getattr(field, attr)
        fields.append(data)
    return fields

@login_json
def get_search_fields(request, typename):
    """
    Returns search fields associated to *typename*.

    :implements: :func:`http_api.search_fields`
    """
    try:
        form = forms.get_search_form(models.get_all_plmobjects()[typename])
    except KeyError:
        return {"result" : "error", "fields" : []}
    return {"fields" : get_fields_from_form(form)}

@login_json
def get_creation_fields(request, typename):
    """
    Returns creation fields associated to *typename*

    :implements: :func:`http_api.creation_fields`
    """
    try:
        form = forms.get_creation_form(models.get_all_plmobjects()[typename])
    except KeyError:
        return {"result" : "error", "fields" : []}
    return {"fields" : get_fields_from_form(form)}

@json_view
def api_login(request):
    """
    Authenticates the user

    :implements: :func:`http_api.login`
    """
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            return {"username" : username, "first_name" : user.first_name,
                    "last_name" : user.last_name}
        else:
            return {"result" : 'error', 'error' : 'user is inactive'}
    else:
        return {"result" : 'error', 'error' : 'login invalid'}


@login_json
def test_login(request):
    """
    Tests if user is authenticated

    :implement: :func:`http_api.testlogin`
    """
    # do nothing, if user is authenticated, json_view sets *result* to 'ok'
    return {}

@login_json
def next_revision(request, doc_id):
    """
    Returns a possible new revision for the :class:`.Document` identified by
    *doc_id*.
    
    :implements: :func:`http_api.next_revision`
    
    :param request: the request
    :param doc_id: id of a :class:`.Document`
    :returned fields: revision, the new revision (may be an empty string)

    .. seealso:: :func:`.utils.get_next_revision` for possible results
    """

    doc = get_obj_by_id(doc_id, request.user)
    return {"revision" : get_next_revision(doc.revision)}

@login_json
def revise(request, doc_id):
    """
    Makes a new revision of the :class:`.Document` identified by *doc_id*.

    :implements: :func:`http_api.revise`
    
    :param request: the request
    :param doc_id: id of a :class:`.Document`
    :returned fields:
        * doc, the new document (see :ref:`http-api-object`)
        * files, a list of files (see :ref:`http-api-file`) 
    """
    
    doc = get_obj_by_id(doc_id, request.user)
    form = forms.AddRevisionForm(request.POST)
    if form.is_valid():
        rev = doc.revise(form.cleaned_data["revision"])
        ret = {"doc" : object_to_dict(rev)}
        files = []
        for df in rev.files:
            files.append(dict(id=df.id, filename=df.filename, size=df.size))
        ret["files"] = files
        return ret
    else:
        return {"result" : 'error'}

@login_json
def is_revisable(request, doc_id):
    """
    Returns True if the :class:`.Document` identified by *doc_id* can be revised.

    :implements: :func:`http_api.is_revisable`
    
    :param request: the request
    :param doc_id: id of a :class:`.Document`
    :returned fields: revisable, True if it can be revised
    """

    doc = get_obj_by_id(doc_id, request.user)
    return {"revisable" : doc.is_revisable()}


@login_json
def attach_to_part(request, doc_id, part_id):
    """
    Links the :class:`.Document` identified by *doc_id* with the :class:`.Part`
    identified by *part_id*.

    :implements: :func:`http_api.attach_to_part`
    
    :param request: the request
    :param doc_id: id of a :class:`.Document`
    :param part_id: id of a :class:`.Part`
    :returned fields: None 
    """
    doc = get_obj_by_id(doc_id, request.user)
    part = get_obj_by_id(part_id, request.user)
    doc.attach_to_part(part)
    return {}


@login_json
def add_file(request, doc_id):
    """
    Adds a file to the :class:`.Document` identified by *doc_id*.

    :implements: :func:`http_api.add_file`
    
    :param request: the request
    :param doc_id: id of a :class:`.Document`
    :returned fields: doc_file, the file that has been had,
                      see :ref:`http-api-file`.
    """
    doc = get_obj_by_id(doc_id, request.user)
    add_file_form_instance = forms.AddFileForm(request.POST, request.FILES)
    df = doc.add_file(request.FILES["filename"])
    return {"doc_file" : dict(id=df.id, filename=df.filename, size=df.size)}


@login_json
def add_thumbnail(request, doc_id, df_id):
    """
    Add a thumbnail the :class:`.DocumentFile` identified by *df_id* from
    the :class:`.Document` identified by *doc_id*.

    :implements: :func:`http_api.add_thumbnail`
    
    :param request: the request
    :param doc_id: id of a :class:`.Document`
    :param df_id: id of a :class:`.DocumentFile`
    :returned fields: None
    """

    doc = get_obj_by_id(doc_id, request.user)
    add_file_form_instance = forms.AddFileForm(request.POST, request.FILES)
    df = models.DocumentFile.objects.get(id=df_id)
    doc.add_thumbnail(df, request.FILES["filename"])
    return {}

