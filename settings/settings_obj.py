"""
New module for dealing with settings objects
"""

from persistent import Persistent

class Setting(Persistent):
    """
    Generic class for handling a specific setting
    """
    def __init__(self, name, value, default='', num_hyphens=0):
        self.name = name
        self.value = value
        self._default = default
        self._num_hyphens = num_hyphens
        if value is None:
            self._set_to_default()


    def _set_to_default(self):
        """
        Called on instantiation to set the value of the object to the
        default provided value
        """
        self.value = self._default
