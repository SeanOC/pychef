import abc
import collections

from chef.base import ChefObject, ChefQuery, ChefObjectMeta
from chef.exceptions import ChefError

class DataBagMeta(ChefObjectMeta, abc.ABCMeta):
    """A metaclass to allow DataBag to use multiple inheritance."""


class DataBag(ChefObject, ChefQuery):
    __metaclass__ = DataBagMeta

    url = '/data'

    def _populate(self, data):
        self.obj_class = DataBagItem
        self.names = data.keys()

    def __getitem__(self, name):
        if name not in self:
            raise KeyError('%s not found'%name)
        return self.obj_class(self, name, api=self.api)


class DataBagItem(ChefObject, collections.Mapping):
    __metaclass__ = DataBagMeta

    url = '/data'
    attributes = {
        'raw_data': dict,
    }

    def __init__(self, bag, name, api=None, skip_load=False):
        self._bag = bag
        super(DataBagItem, self).__init__(str(bag)+'/'+name, api=api, skip_load=skip_load)
        self.name = name

    @property
    def bag(self):
        if not isinstance(self._bag, DataBag):
            self._bag = DataBag(self._bag, api=self.api)
        return self._bag

    @classmethod
    def from_search(cls, data, api):
        bag = data.get('data_bag')
        if not bag:
            raise ChefError('No data_bag key in data bag item information')
        name = data.get('name')
        if not name:
            raise ChefError('No name key in the data bag item information')
        item = name[len('data_bag_item_' + bag + '_'):]
        obj = cls(bag, item, api=api, skip_load=True)
        obj.exists = True
        obj._populate(data)
        return obj

    def _populate(self, data):
        if 'json_class' in data:
            self.raw_data = data['raw_data']
        else:
            self.raw_data = data

    def __len__(self):
        return len(self.raw_data)

    def __iter__(self):
        return iter(self.raw_data)

    def __getitem__(self, key):
        return self.raw_data[key]
