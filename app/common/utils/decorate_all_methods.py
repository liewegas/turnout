# From: https://stackoverflow.com/a/6307868
#
# Usage:
#
# @decorate_all_methods(mydecorator)
# class C(object):
#     def m1(self): pass
#     def m2(self, x): pass
def decorate_all_methods(decorator):
    def decorate(cls):
        for attr in cls.__dict__:  # there's propably a better way to do this
            if callable(getattr(cls, attr)):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls

    return decorate
