import collections

import attr
import openpyxl

import epyqlib.pm.parametermodel
import epyqlib.utils.general

import epcpm.sunspecmodel


builders = epyqlib.utils.general.TypeMap()


data_point_fields = attr.fields(epcpm.sunspecmodel.DataPoint)

sheet_fields = {
    "Field Type": None,
    "Applicable Point": None,
    "Address Offset": data_point_fields.offset,
    "Block Offset": data_point_fields.block_offset,
    "Size": None, #data_point_fields.size,
    "Name": data_point_fields.name,
    "Label": data_point_fields.label,
    "Value": None,
    "Type": data_point_fields.type,
    "Units": data_point_fields.units,
    "SF": data_point_fields.factor_uuid,
    "R/W": None,
    "Mandatory M/O": None,
    "Description": data_point_fields.description,
    "Notes": data_point_fields.notes,
}


@builders(epcpm.sunspecmodel.Root)
@attr.s
class Root:
    wrapped = attr.ib()
    parameter_uuid_finder = attr.ib(default=None)
    parameter_model = attr.ib(default=None)

    def gen(self):
        workbook = openpyxl.Workbook()
        workbook.remove(workbook.active)

        for model in self.wrapped.children:
            worksheet = workbook.create_sheet()

            builders.wrap(
                wrapped=model,
                worksheet=worksheet,
                parameter_uuid_finder=self.parameter_uuid_finder,
            ).gen()

        return workbook


@builders(epcpm.sunspecmodel.Model)
@attr.s
class Model:
    wrapped = attr.ib()
    worksheet = attr.ib()
    parameter_uuid_finder = attr.ib(default=None)

    def gen(self):
        self.worksheet.title = str(self.wrapped.id)
        self.worksheet.append(list(sheet_fields.keys()))

        scale_factor_from_uuid = {
            point.uuid: point
            for point in self.wrapped.children
            if point.type == 'sunssf'
        }

        for child in self.wrapped.children:
            builder = builders.wrap(
                wrapped=child,
                scale_factor_from_uuid=scale_factor_from_uuid,
                parameter_uuid_finder=self.parameter_uuid_finder,
            )
            self.worksheet.append(builder.gen())


@builders(epcpm.sunspecmodel.DataPoint)
@attr.s
class Point:
    wrapped = attr.ib()
    scale_factor_from_uuid = attr.ib()
    parameter_uuid_finder = attr.ib(default=None)

    def gen(self):
        values = [
            self.value_from_field(field)
            for field in sheet_fields.values()
        ]

        return values

    def value_from_field(self, field):
        if field is None:
            return None

        value = getattr(self.wrapped, field.name)

        if value is None:
            return None

        if field == data_point_fields.factor_uuid:
            return self.scale_factor_from_uuid[value].name

        return value
