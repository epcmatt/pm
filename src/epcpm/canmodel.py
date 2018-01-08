import collections

import attr
import graham
import marshmallow
import PyQt5.QtCore

import epyqlib.attrsmodel
import epyqlib.pm.parametermodel
import epyqlib.treenode
import epyqlib.utils.general
import epyqlib.utils.qt

# See file COPYING in this source tree
__copyright__ = 'Copyright 2017, EPC Power Corp.'
__license__ = 'GPLv2+'


def based_int(v):
    if isinstance(v, str):
        return int(v, 0)

    return int(v)


def hex_upper(v, width=8, prefix='0x'):
    return f'{prefix}{v:0{width}X}'


class HexadecimalIntegerField(marshmallow.fields.Field):
    def _serialize(self, value, attr, obj):
        if self.allow_none and value is None:
            return None

        return hex(value)

    def _deserialize(self, value, attr, data):
        if self.allow_none and value is None:
            return None

        return int(value, 0)


@staticmethod
def child_from(node):
    return Signal(name=node.name, parameter_uuid=str(node.uuid))


@graham.schemify(tag='signal')
@epyqlib.attrsmodel.ify()
@epyqlib.utils.qt.pyqtify()
@attr.s(hash=False)
class Signal(epyqlib.treenode.TreeNode):
    name = attr.ib(
        default='New Signal',
        metadata=graham.create_metadata(
            field=marshmallow.fields.String(),
        ),
    )
    bits = attr.ib(
        default=0,
        metadata=graham.create_metadata(
            field=marshmallow.fields.Integer(),
        ),
    )
    signed = attr.ib(
        default=False,
        convert=epyqlib.attrsmodel.two_state_checkbox,
        metadata=graham.create_metadata(
            field=marshmallow.fields.Boolean(),
        ),
    )
    factor = attr.ib(
        default=1,
        metadata=graham.create_metadata(
            field=marshmallow.fields.Decimal(as_string=True),
        ),
    )
    start_bit = attr.ib(
        default=0,
        metadata=graham.create_metadata(
            field=marshmallow.fields.Integer(),
        ),
    )

    parameter_uuid = epyqlib.attrsmodel.attr_uuid(
        default=None,
        allow_none=True,
    )
    epyqlib.attrsmodel.attrib(
        attribute=parameter_uuid,
        human_name='Parameter UUID',
    )

    uuid = epyqlib.attrsmodel.attr_uuid()

    def __attrs_post_init__(self):
        super().__init__()

    def can_drop_on(self, node):
        return False

    can_delete = epyqlib.attrsmodel.childless_can_delete

    def calculated_min_max(self):
        bits = self.bits

        if self.signed:
            bits -= 1

        r = 2 ** bits

        if self.signed:
            minimum = -r
            maximum = r - 1
        else:
            minimum = 0
            maximum = r - 1

        minimum *= self.factor
        maximum *= self.factor

        return minimum, maximum


@graham.schemify(tag='message')
@epyqlib.attrsmodel.ify()
@epyqlib.utils.qt.pyqtify()
@attr.s(hash=False)
class Message(epyqlib.treenode.TreeNode):
    name = attr.ib(
        default='New Message',
        metadata=graham.create_metadata(
            field=marshmallow.fields.String(),
        ),
    )

    identifier = attr.ib(
        default=0x1fffffff,
        convert=based_int,
        metadata=graham.create_metadata(
            field=HexadecimalIntegerField(),
        ),
    )
    epyqlib.attrsmodel.attrib(
        data_display=hex_upper,
        attribute=identifier,
    )

    extended = attr.ib(
        default=True,
        convert=epyqlib.attrsmodel.two_state_checkbox,
        metadata=graham.create_metadata(
            field=marshmallow.fields.Boolean(),
        ),
    )
    length = attr.ib(
        default=0,
        metadata=graham.create_metadata(
            field=marshmallow.fields.Int(),
        ),
    )
    cycle_time = attr.ib(
        default=None,
        convert=epyqlib.attrsmodel.to_decimal_or_none,
        metadata=graham.create_metadata(
            field=marshmallow.fields.Decimal(allow_none=True, as_string=True),
        ),
    )
    sendable = attr.ib(
        default=True,
        convert=epyqlib.attrsmodel.two_state_checkbox,
        metadata=graham.create_metadata(
            field=marshmallow.fields.Boolean(),
        ),
    )
    receivable = attr.ib(
        default=True,
        convert=epyqlib.attrsmodel.two_state_checkbox,
        metadata=graham.create_metadata(
            field=marshmallow.fields.Boolean(),
        ),
    )
    comment = attr.ib(
        default=None,
        convert=epyqlib.attrsmodel.to_str_or_none,
        metadata=graham.create_metadata(
            field=marshmallow.fields.String(allow_none=True),
        ),
    )
    children = attr.ib(
        default=attr.Factory(list),
        metadata=graham.create_metadata(
            field=graham.fields.MixedList(fields=(
                marshmallow.fields.Nested(graham.schema(Signal)),
            )),
        ),
    )
    uuid = epyqlib.attrsmodel.attr_uuid()

    def __attrs_post_init__(self):
        super().__init__()

    child_from = child_from

    @classmethod
    def all_addable_types(cls):
        return epyqlib.attrsmodel.create_addable_types((Signal,))

    def addable_types(self):
        return {}

    def can_drop_on(self, node):
        return isinstance(node, epyqlib.pm.parametermodel.Parameter)

    def can_delete(self, node=None):
        if node is None:
            return self.tree_parent.can_delete(node=self)

        return True


@graham.schemify(tag='multiplexer')
@epyqlib.attrsmodel.ify()
@epyqlib.utils.qt.pyqtify()
@attr.s(hash=False)
class Multiplexer(epyqlib.treenode.TreeNode):
    name = attr.ib(
        default='New Multiplexer',
        metadata=graham.create_metadata(
            field=marshmallow.fields.String(),
        ),
    )
    identifier = attr.ib(
        default=None,
        convert=epyqlib.attrsmodel.to_int_or_none,
        metadata=graham.create_metadata(
            field=marshmallow.fields.Integer(allow_none=True),
        )
    )
    length = attr.ib(
        default=0,
        convert=int,
        metadata=graham.create_metadata(
            field=marshmallow.fields.Int(),
        ),
    )
    cycle_time = attr.ib(
        default=None,
        convert=epyqlib.attrsmodel.to_decimal_or_none,
        metadata=graham.create_metadata(
            field=marshmallow.fields.Decimal(allow_none=True, as_string=True),
        ),
    )
    comment = attr.ib(
        default=None,
        convert=epyqlib.attrsmodel.to_str_or_none,
        metadata=graham.create_metadata(
            field=marshmallow.fields.String(allow_none=True),
        ),
    )
    children = attr.ib(
        default=attr.Factory(list),
        metadata=graham.create_metadata(
            field=graham.fields.MixedList(fields=(
                marshmallow.fields.Nested(graham.schema(Signal)),
            )),
        ),
    )
    uuid = epyqlib.attrsmodel.attr_uuid()

    def __attrs_post_init__(self):
        super().__init__()

    child_from = child_from

    @classmethod
    def all_addable_types(cls):
        return epyqlib.attrsmodel.create_addable_types((Signal,))

    def addable_types(self):
        return {}

    def can_drop_on(self, node):
        return isinstance(node, (epyqlib.pm.parametermodel.Parameter, Signal))

    def can_delete(self, node=None):
        if node is None:
            return self.tree_parent.can_delete(node=self)

        return True


@graham.schemify(tag='multiplexed_message')
@epyqlib.attrsmodel.ify()
@epyqlib.utils.qt.pyqtify()
@attr.s(hash=False)
class MultiplexedMessage(epyqlib.treenode.TreeNode):
    name = attr.ib(
        default='New Multiplexed Message',
        metadata=graham.create_metadata(
            field=marshmallow.fields.String(),
        ),
    )

    identifier = attr.ib(
        default=0x1fffffff,
        convert=based_int,
        metadata=graham.create_metadata(
            field=HexadecimalIntegerField(),
        ),
    )
    epyqlib.attrsmodel.attrib(
        data_display=hex_upper,
        attribute=identifier,
    )

    extended = attr.ib(
        default=True,
        convert=epyqlib.attrsmodel.two_state_checkbox,
        metadata=graham.create_metadata(
            field=marshmallow.fields.Boolean(),
        ),
    )
    sendable = attr.ib(
        default=True,
        convert=epyqlib.attrsmodel.two_state_checkbox,
        metadata=graham.create_metadata(
            field=marshmallow.fields.Boolean(),
        ),
    )
    receivable = attr.ib(
        default=True,
        convert=epyqlib.attrsmodel.two_state_checkbox,
        metadata=graham.create_metadata(
            field=marshmallow.fields.Boolean(),
        ),
    )
    comment = attr.ib(
        default=None,
        convert=epyqlib.attrsmodel.to_str_or_none,
        metadata=graham.create_metadata(
            field=marshmallow.fields.String(allow_none=True),
        ),
    )
    children = attr.ib(
        default=attr.Factory(list),
        metadata=graham.create_metadata(
            field=graham.fields.MixedList(fields=(
                marshmallow.fields.Nested(graham.schema(Signal)),
                marshmallow.fields.Nested(graham.schema(Multiplexer)),
            )),
        ),
    )
    uuid = epyqlib.attrsmodel.attr_uuid()

    def __attrs_post_init__(self):
        super().__init__()

    def can_drop_on(self, node):
        return isinstance(node, tuple(self.addable_types().values()))

    def can_delete(self, node=None):
        if node is None:
            return self.tree_parent.can_delete(node=self)

        return True

    @classmethod
    def all_addable_types(cls):
        return epyqlib.attrsmodel.create_addable_types((Signal, Multiplexer))

    def addable_types(self):
        types = (Signal,)

        if len(self.children) > 0:
            types += (Multiplexer,)

        return epyqlib.attrsmodel.create_addable_types(types)


Root = epyqlib.attrsmodel.Root(
    default_name='CAN',
    valid_types=(Message, MultiplexedMessage)
)

types = epyqlib.attrsmodel.Types(
    types=(Root, Message, Signal, MultiplexedMessage, Multiplexer),
)


# TODO: CAMPid 943896754217967154269254167
def merge(name, *types):
    return tuple((x, name) for x in types)


columns = epyqlib.attrsmodel.columns(
    merge('name', *types.types.values()),
    merge('identifier', Message, MultiplexedMessage, Multiplexer),
    merge('length', Message, Multiplexer) + merge('bits', Signal),
    merge('extended', Message, MultiplexedMessage),

    merge('cycle_time', Message, Multiplexer),

    merge('signed', Signal),
    merge('factor', Signal),

    merge('sendable', Message, MultiplexedMessage),
    merge('receivable', Message, MultiplexedMessage),
    merge('start_bit', Signal),
    merge('comment', Message, Multiplexer, MultiplexedMessage),


    merge('parameter_uuid', Signal),
    merge('uuid', *types.types.values()),
)


@attr.s
class ReferencedUuidNotifier(PyQt5.QtCore.QObject):
    changed = PyQt5.QtCore.pyqtSignal('PyQt_PyObject')

    view = attr.ib(default=None)
    selection_model = attr.ib(default=None)

    def __attrs_post_init__(self):
        super().__init__()

        if self.view is not None:
            self.set_view(self.view)

    def set_view(self, view):
        self.disconnect_view()

        self.view = view
        self.selection_model = self.view.selectionModel()
        self.selection_model.currentChanged.connect(
            self.current_changed,
        )

    def disconnect_view(self):
        if self.selection_model is not None:
            self.selection_model.currentChanged.disconnect(
                self.current_changed,
            )
        self.view = None
        self.selection_model = None

    def current_changed(self, current, previous):
        index, model = epyqlib.utils.qt.resolve_index_to_model(
            view=self.view,
            index=current,
        )
        node = model.node_from_index(index)
        if isinstance(node, Signal):
            self.changed.emit(node.parameter_uuid)