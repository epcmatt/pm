import collections

import attr
from PyQt5 import QtCore

import epyqlib.attrsmodel
import epyqlib.treenode
import epyqlib.utils.general

import epcpm.parametermodel

# See file COPYING in this source tree
__copyright__ = 'Copyright 2017, EPC Power Corp.'
__license__ = 'GPLv2+'


@epyqlib.attrsmodel.add_addable_types()
@epyqlib.utils.qt.pyqtify()
@attr.s(hash=False)
class Signal(epyqlib.treenode.TreeNode):
    type = attr.ib(default='signal', init=False)
    name = attr.ib(default='New Signal')
    parameter_uuid = epyqlib.attrsmodel.attr_uuid(
        metadata={'human name': 'Parameter UUID'})
    uuid = epyqlib.attrsmodel.attr_uuid()

    def __attrs_post_init__(self):
        super().__init__()

    @classmethod
    def from_json(cls, obj):
        return cls(**obj)

    def to_json(self):
        return attr.asdict(
            self,
            recurse=False,
            dict_factory=collections.OrderedDict,
            filter=lambda a, _: a.metadata.get('to_file', True)
        )

    def can_drop_on(self, node):
        return False


@epyqlib.attrsmodel.add_addable_types()
@epyqlib.utils.qt.pyqtify()
@attr.s(hash=False)
class Message(epyqlib.treenode.TreeNode):
    type = attr.ib(default='message', init=False, metadata={'ignore': True})
    name = attr.ib(default='New Message')
    identifier = attr.ib(default='0x1fffffff')
    extended = attr.ib(default=True,
                       convert=epyqlib.attrsmodel.two_state_checkbox)
    cycle_time = attr.ib(default=None,
                         convert=epyqlib.attrsmodel.to_decimal_or_none)
    children = attr.ib(
        default=attr.Factory(list),
        metadata={'valid_types': (Signal,)}
    )
    uuid = epyqlib.attrsmodel.attr_uuid()

    def __attrs_post_init__(self):
        super().__init__()

    @classmethod
    def from_json(cls, obj):
        children = obj.pop('children')
        node = cls(**obj)

        for child in children:
            node.append_child(child)

        return node

    def to_json(self):
        return attr.asdict(
            self,
            recurse=False,
            dict_factory=collections.OrderedDict,
            filter=lambda a, _: a.metadata.get('to_file', True)
        )

    def can_drop_on(self, node):
        x = (*self.addable_types().values(), epcpm.parametermodel.Parameter)

        return isinstance(node, x)

    def child_from(self, node):
        return Signal(name=node.name, parameter_uuid=str(node.uuid))


Root = epyqlib.attrsmodel.Root(
    default_name='Symbols',
    valid_types=(Message,)
)

types = (Root, Message, Signal)


columns = epyqlib.attrsmodel.columns(
    ((Message, 'name'), (Signal, 'name')),
    ((Message, 'identifier'),),
    ((Message, 'extended'),),
    ((Message, 'cycle_time'),),
    ((Signal, 'parameter_uuid'),)
)
