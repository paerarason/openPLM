"""
This module contains a class called :class:`UserController` which
provides a controller for :class:`~django.contrib.auth.models.User`.
This class is similar to :class:`.PLMObjectController` but some methods
from :class:`.PLMObjectController` are not defined.
"""

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.fields import FieldDoesNotExist

try:
    import openPLM.plmapp.models as models
    from openPLM.plmapp.exceptions import RevisionError, LockError, UnlockError, \
        AddFileError, DeleteFileError, PermissionError
except (ImportError, AttributeError):
    import plmapp.models as models
    from plmapp.exceptions import RevisionError, LockError, UnlockError, \
        AddFileError, DeleteFileError, PermissionError

class UserController(object):
    u"""
    Object used to manage a :class:`~django.contrib.auth.models.User` and store his 
    modification in an history
    
    :attributes:
        .. attribute:: object

            The :class:`~django.contrib.auth.models.User` managed by the controller

    :param obj: managed object
    :type obj: an instance of :class:`~django.contrib.auth.models.User`
    :param user: user who modify *obj*
    :type user: :class:`~django.contrib.auth.models.User` 

    .. note::
        This class does not inherit from :class:`.PLMObjectController`.

    """

    def __init__(self, obj, user):
        self.object = obj
        self._user = user
        self.__histo = ""
        self.creator = user
        self.owner = user
        self.mtime = obj.last_login
        self.ctime = obj.date_joined

    def get_verbose_name(self, attr_name):
        """
        Returns a verbose name for *attr_name*.

        Example::

            >>> ctrl.get_verbose_name("ctime")
            u'date of creation'
        """

        try:
            item = unicode(self.object._meta.get_field(attr_name).verbose_name)
        except FieldDoesNotExist:
            names = {"mtime" : "date of last modification",
                     "ctime" : "date of creation",
                     "rank" : "role in PLM"}
            item = names.get(attr_name, attr_name)
        return item

    def update_from_form(self, form):
        u"""
        Updates :attr:`object` from data of *form*
        
        This method raises :exc:`ValueError` if *form* is invalid.
        """
        if form.is_valid():
            need_save = False
            for key, value in form.cleaned_data.iteritems():
                if key not in ["username"]:
                    setattr(self, key, value)
                    need_save = True
            if need_save:
                self.save()
        else:
            raise ValueError("form is invalid")

    def __setattr__(self, attr, value):
        if hasattr(self, "object"):
            obj = object.__getattribute__(self, "object")
            profile = obj.get_profile()
        else:
            obj = None
        if obj and (hasattr(obj, attr) or hasattr(profile, attr)) and \
           not attr in self.__dict__:
            obj2 = obj if hasattr(obj, attr) else profile
            old_value = getattr(obj2, attr)
            setattr(obj2, attr, value)
            field = obj2._meta.get_field(attr).verbose_name.capitalize()
            message = "%(field)s : changes from '%(old)s' to '%(new)s'" % \
                    {"field" : field, "old" : old_value, "new" : value}
            self.__histo += message + "\n"
        else:
            super(UserController, self).__setattr__(attr, value)

    def __getattr__(self, attr):
        obj = object.__getattribute__(self, "object")
        profile = obj.get_profile()
        if hasattr(self, "object") and hasattr(obj, attr) and \
           not attr in self.__dict__:
            return getattr(obj, attr)
        elif hasattr(profile, attr) and not attr in self.__dict__:
            return getattr(profile, attr)
        else:
            return object.__getattribute__(self, attr)

    def save(self, with_history=True):
        u"""
        Saves :attr:`object` and records its history in the database.
        If *with_history* is False, the history is not recorded.
        """
        self.object.save()
        self.object.get_profile().save()
        if self.__histo and with_history:
            self._save_histo("Modify", self.__histo) 
            self.__histo = ""

    def _save_histo(self, action, details):
        histo = models.UserHistory()
        histo.plmobject = self.object
        histo.action = action
        histo.details = details 
        histo.user = self._user
        histo.save()
        
    def get_object_user_links(self):
        """
        Returns all :class:`.Part` attached to :attr:`object`.
        """
        return models.PLMObjectUserLink.objects.filter(user=self.object).order_by("plmobject")

    def delegate(self, user, role):
        """
        Delegates role *role* to *user*.
        
        Possible values for *role* are:
            ``'notified``
                valid for all users
            ``'owner'``
                valid only for contributors and administrators
            :samp:``'sign_{x}_level'``
                valid only for contributors and administrators
            ``'sign*'``
                valid only for contributors and administrators, means all sign
                roles that :attr:`object` has.
        
        :raise: :exc:`.PermissionError` if *user* can not have the role *role*
        :raise: :exc:`ValueError` if *user* is :attr:`object`
        """
        if user == self.object:
            raise ValueError("Bad delegatee (self)")
        if user.get_profile().is_viewer and role != 'notified':
            raise PermissionError("%s can not have role %s" % (user, role))
        if self.object.get_profile().is_viewer and role != 'notified':
            raise PermissionError("%s can not have role %s" % (self.object, role))
        if role == "sign*":
            qset = models.PLMObjectUserLink.objects.filter(user=self.object,
                        role__startswith="sign_").only("role")
            roles = set(link.role for link in qset)
        else:
            roles = [role]
        for r in roles:
            models.DelegationLink.objects.get_or_create(delegator=self.object,
                        delegatee=user, role=r)
        details = "%(delegator)s delegates the role %(role)s to %(delegatee)s"
        details = details % dict(role=role, delegator=self.object,
                                 delegatee=user)
        self._save_histo(models.DelegationLink.ACTION_NAME, details)

    def remove_delegation(self, delegation_link):
        """
        Removes a delegation (*delegation_link*). The delegator must be 
        :attr:`object`, otherwise a :exc:`ValueError` is raised.
        """
        if delegation_link.delegator != self.object:
            raise ValueError("%s is not the delegator of %s" % (self.object, ValueError))
        details = "%(delegator)s removes his delegation for the role %(role)s to %(delegatee)s"
        details = details % dict(role=delegation_link.role, delegator=self.object,
                                 delegatee=delegation_link.delegatee)
        self._save_histo(models.DelegationLink.ACTION_NAME, details)
        delegation_link.delete()
        
    def get_user_delegation_links(self):
        """
        Returns all :class:`.Part` attached to :attr:`object`.
        """
        return models.DelegationLink.objects.filter(delegator=self.object).order_by("role")
