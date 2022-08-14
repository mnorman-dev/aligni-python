import xml.etree.ElementTree as Et


class Entity:
    int_params = ["id"]
    bool_params = [""]
    float_params = [""]

    @classmethod
    def from_xml(cls, et):
        """
        Initialise a default Entity from an ElementTree
        """
        obj = cls.__new__(cls)
        for attr in et:
            if attr.tag in obj.int_params:
                if attr.text is not None:
                    setattr(obj, attr.tag, int(attr.text))
                else:
                    setattr(obj, attr.tag, None)
            elif attr.tag in obj.bool_params:
                if attr.text is not None:
                    if attr.text.lower() == "true":
                        setattr(obj, attr.tag, True)
                    else:
                        setattr(obj, attr.tag, False)
                else:
                    setattr(obj, attr.tag, None)
            elif attr.tag in obj.float_params:
                if attr.text is not None:
                    setattr(obj, attr.tag, float(attr.text))
                else:
                    setattr(obj, attr.tag, None)
            else:
                setattr(obj, attr.tag, attr.text)
        return obj

    def __repr__(self) -> str:
        return str(self.__dict__)


class Manufacturer(Entity):
    def __init__(self, name, short_name=None) -> None:
        self.name = name
        self.short_name = short_name
        self.vendor_ids = []

    @classmethod
    def from_xml(cls, et):
        """
        Initialise a Manufacturer from an ElementTree
        """
        obj = cls.__new__(cls)
        obj.vendor_ids = []
        for attr in et:
            if attr.tag == "vendors":
                for vendor in attr:
                    for vendor_item in vendor:
                        if vendor_item.tag == "id":
                            obj.vendor_ids.append(int(vendor_item.text))
            elif attr.tag in obj.int_params:
                setattr(obj, attr.tag, int(attr.text))
            else:
                setattr(obj, attr.tag, attr.text)
        return obj

    def to_xml(self):
        """
        Creates a manufacturer in the Aligni database.
        :param manufacturer_name: The name of the manufacturer.
        Returns ID of created manufacturer.
        """
        # First contstruct the XML tree for the request.
        root = Et.Element("manufacturer")
        name_xml = Et.SubElement(root, "name")
        name_xml.text = str(self.name)
        if self.short_name is not None:
            short_name_xml = Et.SubElement(root, "short_name")
            short_name_xml.text = str(self.short_name)
        return root


class Vendor(Entity):
    def __init__(self, name, short_name=None):
        self.name = name
        self.short_name = short_name
        self.manufacturer_ids = []

    @classmethod
    def from_xml(cls, et):
        """
        Initialise a Vendor from an ElementTree
        """
        obj = cls.__new__(cls)
        obj.manufacturer_ids = []
        for attr in et:
            if attr.tag == "manufacturers":
                for manuf in attr:
                    for manuf_item in manuf:
                        if manuf_item.tag == "id":
                            obj.manufacturer_ids.append(int(manuf_item.text))
            elif attr.tag in obj.int_params:
                setattr(obj, attr.tag, int(attr.text))
            else:
                setattr(obj, attr.tag, attr.text)
        return obj

    def to_xml(self):
        """
        Creates a Vendor in the Aligni database.
        :param name: The name of the vendor.
        Returns ID of created vendor.
        """
        # First contstruct the XML tree for the request.
        root = Et.Element("vendor")
        name_xml = Et.SubElement(root, "name")
        name_xml.text = str(self.name)
        if self.short_name is not None:
            short_name_xml = Et.SubElement(root, "short_name")
            short_name_xml.text = str(self.short_name)
        return root


class Contact(Entity):
    int_params = ["id", "vendor_id"]


class LineCard(Entity):
    int_params = ["id", "manufacturer_id", "vendor_id"]

    def __init__(self, vendor_id, manufacturer_id):
        self.id = None
        self.vendor_id = vendor_id
        self.manufacturer_id = manufacturer_id

    def to_xml(self):
        root = Et.Element("linecard")
        manufacturer_id_xml = Et.SubElement(root, "manufacturer_id")
        manufacturer_id_xml.text = str(self.manufacturer_id)
        vendor_id_xml = Et.SubElement(root, "vendor_id")
        vendor_id_xml.text = str(self.vendor_id)
        return root


class PartType(Entity):
    int_params = ["id", "parent_id", "part_next"]
    bool_params = ["is_non_material", "parent_only"]
    float_params = ["attrition"]

    def __init__(
        self,
        name,
        attrition=None,
        is_non_material=False,
        parent_id=None,
        parent_only=False,
        part_next=1,
        partnumber_key="",
    ):
        self.name = str(name)
        self.attrition = attrition
        self.is_non_material = bool(is_non_material)
        self.parent_id = parent_id
        self.parent_only = bool(parent_only)
        self.part_next = part_next
        self.partnumber_key = partnumber_key

    def to_xml(self):
        """
        Creates a parttype in the Aligni database.
        :param manufacturer_name: The name of the manufacturer.
        Returns ID of created manufacturer.
        """
        # First contstruct the XML tree for the request.
        root = Et.Element("parttype")
        name_xml = Et.SubElement(root, "name")
        name_xml.text = str(self.name)
        attrition_xml = Et.SubElement(root, "attrition")
        if self.attrition is not None:
            attrition_xml.text = str(self.attrition)
        material_xml = Et.SubElement(root, "is_non_material")
        if self.is_non_material:
            material_xml.text = "true"
        else:
            material_xml.text = "false"
        parent_id_xml = Et.SubElement(root, "parent_id")
        if self.parent_id is not None:
            parent_id_xml.text = str(self.parent_id)
        parent_only_xml = Et.SubElement(root, "parent_only")
        if self.parent_only:
            parent_only_xml.text = "true"
        else:
            parent_only_xml.text = "false"
        part_next_xml = Et.SubElement(root, "part_next")
        part_next_xml.text = str(self.part_next)
        partnumber_key_xml = Et.SubElement(root, "partnumber_key")
        if self.partnumber_key is not None:
            partnumber_key_xml.text = str(self.partnumber_key)
        return root


class AlternatePart(Entity):
    int_params = ["part_id", "quality"]


class VendorPartNumber(Entity):
    int_params = ["id", "part_id", "vendor_id", "unit_id"]

    def __init__(
        self, part_id=None, vendor_id=None, unit_id=None, part_number="", comment=""
    ):
        self.id = None
        self.part_id = int(part_id)
        self.vendor_id = int(vendor_id)
        self.unit_id = int(unit_id)
        self.part_number = str(part_number)
        self.comment = str(comment)

    def to_xml(self):
        root = Et.Element("vendor_partnumber")
        part_id_xml = Et.SubElement(root, "part_id")
        part_id_xml.text = str(self.part_id)
        vendor_id_xml = Et.SubElement(root, "vendor_id")
        vendor_id_xml.text = str(self.vendor_id)
        unit_id_xml = Et.SubElement(root, "unit_id")
        unit_id_xml.text = str(self.unit_id)
        part_number_xml = Et.SubElement(root, "part_number")
        part_number_xml.text = str(self.part_number)
        comment_xml = Et.SubElement(root, "comment")
        comment_xml.text = str(self.comment)
        return root


class PartParameterOption(Entity):
    pass


class PartParameterField(Entity):
    bool_params = ["revisioned"]

    def __init__(
        self,
        name,
        xml_name,
        description,
        revisioned,
        param_type,
        part_parameter_options=None,
    ):
        self.id = None
        self.name = str(name)
        self.xml_name = str(xml_name)
        self.description = str(description)
        self.revisioned = str(revisioned)
        self.param_type = str(param_type)
        self.part_parameter_options = part_parameter_options

    @classmethod
    def from_xml(cls, et):
        obj = cls.__new__(cls)
        for attr in et:
            if attr.tag in obj.int_params:
                setattr(obj, attr.tag, str(attr.text))
            elif attr.tag == "part_parameter_options":
                obj.part_parameter_options = []
                for m in attr:
                    obj.part_parameter_options.append(PartParameterOption.from_xml(m))
            elif attr.tag in obj.bool_params:
                if attr.text.lower() == "true":
                    setattr(obj, attr.tag, True)
                else:
                    setattr(obj, attr.tag, False)
            else:
                setattr(obj, attr.tag, attr.text)
        return obj


class PartParameterValue(Entity):
    def __init__(self, part_parameter_field, value):
        self.part_parameter_field = part_parameter_field
        self.value = str(value)

    def to_xml(self):
        root = Et.Element(self.part_parameter_field.xml_name)
        root.text = str(self.value)
        return root


class PartRevision(Entity):
    int_params = ["id", "rohs"]

    def __init__(
        self,
        description="",
        comment="",
        revision_name="01",
        revision_description="",
        rohs=None,
        revisioned_custom_parameters=None,
    ):
        self.id = None
        self.description = str(description)
        self.comment = str(comment)
        self.revision_name = str(revision_name)
        self.revision_description = str(revision_description)
        self.rohs = rohs
        self.revisioned_custom_parameters = revisioned_custom_parameters

    def to_xml(self):
        # First contstruct the XML tree for the request.
        root = Et.Element("revision")
        revision_name_xml = Et.SubElement(root, "revision_name")
        revision_name_xml.text = str(self.revision_name)
        revision_description_xml = Et.SubElement(root, "revision_description")
        revision_description_xml.text = str(self.revision_description)
        comment_xml = Et.SubElement(root, "comment")
        comment_xml.text = str(self.comment)
        description_xml = Et.SubElement(root, "description")
        description_xml.text = str(self.description)
        rohs_xml = Et.SubElement(root, "rohs")
        if self.rohs is True:
            rohs_xml.text = "1"
        elif self.rohs == "Unknown":
            rohs_xml.text = "-1"
        else:
            rohs_xml.text = "0"
        if self.revisioned_custom_parameters is not None:
            for (
                parameter_name,
                parameter_value,
            ) in self.revisioned_custom_parameters.items():
                if parameter_name.startswith("x_"):
                    parameter_xml = Et.SubElement(root, parameter_name)
                else:
                    parameter_xml = Et.SubElement(root, "x_" + parameter_name)
                parameter_xml.text = str(parameter_value)
        return root

    @classmethod
    def from_xml(cls, et):
        obj = cls.__new__(cls)
        obj.revisioned_custom_parameters = {}

        for attr in et:
            if attr.tag in obj.int_params:
                setattr(obj, attr.tag, str(attr.text))
            elif attr.tag.startswith("x_"):
                obj.revisioned_custom_parameters[attr.tag] = attr.text
            elif attr.tag == "subparts":
                obj.subparts = []
                for m in attr:
                    obj.subparts.append(SubPart.from_xml(m))
            else:
                setattr(obj, attr.tag, attr.text)
        return obj


class SubPart(Entity):
    int_params = ["id", "part_id", "part_revision_id", "quantity", "position"]
    bool_params = ["no_load"]

    def __init__(
        self,
        part_id,
        part_revision_id,
        quantity,
        designator,
        no_load,
        position,
        comment=None,
    ):
        self.id = None
        self.part_id = part_id
        self.part_revision_id = part_revision_id
        self.quantity = quantity
        self.comment = comment
        self.designator = designator
        self.no_load = no_load
        self.position = position

    def to_xml(self):
        root_xml = Et.Element("subpart")
        part_id_xml = Et.SubElement(root_xml, "part_id")
        part_id_xml.text = str(self.part_id)
        part_revision_id_xml = Et.SubElement(root_xml, "part_revision_id")
        part_revision_id_xml.text = str(self.part_revision_id)
        quantity_xml = Et.SubElement(root_xml, "quantity")
        quantity_xml.text = str(self.quantity)
        designator_xml = Et.SubElement(root_xml, "designator")
        designator_xml.text = str(self.designator)
        no_load_xml = Et.SubElement(root_xml, "no_load")
        if self.no_load:
            no_load_xml.text = "true"
        else:
            no_load_xml.text = "false"
        position_xml = Et.SubElement(root_xml, "position")
        position_xml.text = str(self.position)
        if self.comment is not None:
            comment_xml = Et.SubElement(root_xml, "comment")
            comment_xml.text = str(self.comment)
        return root_xml


class Part(Entity):
    int_params = ["id", "parttype_id", "manufacturer_id", "unit_id"]
    float_params = ["estimated_cost"]
    bool_params = ["manufactured_here"]

    def __init__(
        self,
        manufacturer_pn,
        manufacturer_id,
        parttype_id,
        unit_id,
        description="",
        value_text="",
        estimated_cost=None,
        estimated_cost_currency=None,
        manufactured_here=False,
        comment="",
        revision_name="01",
        revision_description="",
        rohs=None,
        custom_parameters=None,
        revisioned_custom_parameters=None,
        partnumber=None,
    ):
        self.id = None
        self.manufacturer_pn = str(manufacturer_pn)
        self.manufacturer_id = int(manufacturer_id)
        self.parttype_id = int(parttype_id)
        self.unit_id = int(unit_id)
        self.value_text = value_text
        self.estimated_cost = estimated_cost
        self.estimated_cost_currency = estimated_cost_currency
        self.manufactured_here = manufactured_here
        self.partnumber = partnumber
        self.custom_parameters = custom_parameters
        self.revision = PartRevision(
            description,
            comment,
            revision_name,
            revision_description,
            rohs,
            revisioned_custom_parameters,
        )

    def to_xml(self):
        # First contstruct the XML tree for the request.
        root = Et.Element("part")
        if self.partnumber is not None:
            partnumber_xml = Et.SubElement(root, "partnumber")
            partnumber_xml.text = str(self.partnumber)
        manufacturer_pn_xml = Et.SubElement(root, "manufacturer_pn")
        manufacturer_pn_xml.text = str(self.manufacturer_pn)
        manufacturer_id_xml = Et.SubElement(root, "manufacturer_id")
        manufacturer_id_xml.text = str(self.manufacturer_id)
        parttype_id_xml = Et.SubElement(root, "parttype_id")
        parttype_id_xml.text = str(self.parttype_id)

        unit_id_xml = Et.SubElement(root, "unit_id")
        unit_id_xml.text = str(self.unit_id)
        # Aligni derives the value from the value_text field
        # (sending the value with cause part creation to fail)
        if self.value_text is not None:
            value_text_xml = Et.SubElement(root, "value_text")
            value_text_xml.text = str(self.value_text)
        if self.custom_parameters is not None:
            for parameter_name, parameter_value in self.custom_parameters.items():
                if parameter_name.startswith("x_"):
                    parameter_xml = Et.SubElement(root, parameter_name)
                else:
                    parameter_xml = Et.SubElement(root, "x_" + parameter_name)
                parameter_xml.text = str(parameter_value)
        if (self.estimated_cost is not None) and (
            self.estimated_cost_currency is not None
        ):
            estimated_cost_xml = Et.SubElement(root, "estimated_cost")
            estimated_cost_xml.text = str(self.estimated_cost)
            estimated_cost_currency_xml = Et.SubElement(root, "estimated_cost_currency")
            estimated_cost_currency_xml.text = str(self.estimated_cost_currency)
        manufactured_here_xml = Et.SubElement(root, "manufactured_here")
        if self.manufactured_here:
            manufactured_here_xml.text = "true"
        else:
            manufactured_here_xml.text = "false"
        # Add the revision info subtree.
        root.append(self.revision.to_xml())
        return root

    @classmethod
    def from_xml(cls, et):  # noqa: C901
        """
        Initialise a Part from an ElementTree
        """
        obj = cls.__new__(cls)
        obj.custom_parameters = {}

        for attr in et:
            if attr.tag in obj.int_params:
                if attr.text is not None:
                    setattr(obj, attr.tag, int(attr.text))
                else:
                    setattr(obj, attr.tag, None)
            elif attr.tag in obj.bool_params:
                if attr.text is not None:
                    if attr.text.lower() == "true":
                        setattr(obj, attr.tag, True)
                    else:
                        setattr(obj, attr.tag, False)
                else:
                    setattr(obj, attr.tag, None)
            elif attr.tag in obj.float_params:
                if attr.text is not None:
                    setattr(obj, attr.tag, float(attr.text))
                else:
                    setattr(obj, attr.tag, None)
            elif attr.tag == "alternate_parts":
                obj.alternate_parts = []
                for m in attr:
                    obj.alternate_parts.append(AlternatePart.from_xml(m))
            elif attr.tag == "quotes":
                obj.quotes = []
                for m in attr:
                    obj.quotes.append(Quote.from_xml(m))
            elif attr.tag.startswith("x_"):
                obj.custom_parameters[attr.tag] = attr.text
            elif attr.tag == "vendor_part_numbers":
                obj.vendor_part_numbers = []
                for m in attr:
                    obj.vendor_part_numbers.append(VendorPartNumber.from_xml(m))
            elif attr.tag == "inventory_units":
                obj.inventory_units = []
                for m in attr:
                    obj.inventory_units.append(InventoryUnit.from_xml(m))
            elif attr.tag == "revision" or attr.tag == "active_revision":
                obj.revision = PartRevision.from_xml(attr)
            else:
                setattr(obj, attr.tag, attr.text)
        return obj


class UnitConversion(Entity):
    int_params = ["id", "from_unit_id", "to_unit_id"]
    float_params = ["factor"]

    def __init__(self, from_unit_id, to_unit_id, factor):
        self.id = None
        self.from_unit_id = int(from_unit_id)
        self.to_unit_id = int(to_unit_id)
        self.factor = float(factor)

    def to_xml(self):
        unit_conversion_xml = Et.Element("unit_conversion")
        from_unit_id_xml = Et.SubElement(unit_conversion_xml, "from_unit_id")
        from_unit_id_xml.text = str(self.from_unit_id)
        to_unit_id_xml = Et.SubElement(unit_conversion_xml, "to_unit_id")
        to_unit_id_xml.text = str(self.to_unit_id)
        factor_xml = Et.SubElement(unit_conversion_xml, "factor")
        factor_xml.text = str(self.factor)
        return unit_conversion_xml


class Unit(Entity):
    bool_params = ["allow_fractional"]

    def __init__(self, name, allow_fractional=False):
        self.id = None
        self.name = str(name)
        self.allow_fractional = bool(allow_fractional)
        self.unit_conversions = []

    @classmethod
    def from_xml(cls, et):
        obj = cls.__new__(cls)
        for attr in et:
            if attr.tag in obj.int_params:
                setattr(obj, attr.tag, int(attr.text))
            elif attr.tag in obj.bool_params:
                if attr.text is not None:
                    if attr.text.lower() == "true":
                        setattr(obj, attr.tag, True)
                    else:
                        setattr(obj, attr.tag, False)
                else:
                    setattr(obj, attr.tag, None)
            elif attr.tag == "unit_conversions":
                obj.unit_conversions = []
                for m in attr:
                    obj.unit_conversions.append(UnitConversion.from_xml(m))
            else:
                setattr(obj, attr.tag, attr.text)
        return obj

    def to_xml(self):
        root = Et.Element("unit")
        unit_name_xml = Et.SubElement(root, "name")
        unit_name_xml.text = str(self.name)
        allow_fractional_xml = Et.SubElement(root, "allow_fractional")
        if self.allow_fractional:
            allow_fractional_xml.text = "true"
        else:
            allow_fractional_xml.text = "false"
        return root


class InventorySublocation(Entity):
    int_params = ["id", "inventory_location_id"]

    def __init__(self, name, inventory_location_id=None):
        self.id = None
        self.name = str(name)
        self.inventory_location_id = inventory_location_id

    def to_xml(self):
        root = Et.Element("inventory_sublocation")
        name_xml = Et.SubElement(root, "name")
        name_xml.text = str(self.name)
        if self.inventory_location_id is not None:
            inventory_location_id_xml = Et.SubElement(root, "inventory_location_id")
            inventory_location_id_xml.text = str(self.inventory_location_id)
        return root


class InventoryLocation(Entity):
    def __init__(
        self, name, shortname, ship_to_name, description="", inventory_sublocations=None
    ):
        self.id = None
        self.name = str(name)
        self.shortname = str(shortname)
        self.ship_to_name = str(ship_to_name)
        self.description = str(description)
        if inventory_sublocations is not None:
            self.inventory_sublocations = inventory_sublocations

    @classmethod
    def from_xml(cls, et):
        obj = cls.__new__(cls)
        obj.inventory_sublocations = []
        for attr in et:
            if attr.tag in obj.int_params:
                if attr.text is not None:
                    setattr(obj, attr.tag, int(attr.text))
                else:
                    setattr(obj, attr.tag, None)
            elif attr.tag == "inventory_sublocation":
                obj.inventory_sublocations.append(InventorySublocation.from_xml(attr))
            else:
                setattr(obj, attr.tag, attr.text)
        return obj

    def to_xml(self):
        root = Et.Element("inventory_location")
        name_xml = Et.SubElement(root, "name")
        name_xml.text = str(self.name)
        shortname_xml = Et.SubElement(root, "shortname")
        shortname_xml.text = str(self.shortname)
        ship_to_name_xml = Et.SubElement(root, "ship_to_name")
        ship_to_name_xml.text = str(self.ship_to_name)
        description_xml = Et.SubElement(root, "description")
        description_xml.text = str(self.description)
        sublocations_xml = Et.SubElement(root, "inventory_sublocations")
        for sublocation in self.inventory_sublocations:
            sublocations_xml.append(sublocation.to_xml())
        return root


class InventoryUnit(Entity):
    int_params = [
        "id",
        "part_id",
        "unit_id",
        "inventory_location_id",
        "inventory_sublocation_id",
    ]
    float_params = ["quantity"]

    def __init__(
        self,
        part_id,
        unit_id,
        quantity,
        inventory_location_id,
        inventory_sublocation_id,
        details=None,
    ):
        self.id = None
        self.part_id = int(part_id)
        self.unit_id = int(unit_id)
        self.quantity = int(quantity)
        self.inventory_location_id = int(inventory_location_id)
        self.inventory_sublocation_id = int(inventory_sublocation_id)
        self.details = str(details)

    def to_xml(self):
        root = Et.Element("inventory_unit")
        part_id_xml = Et.SubElement(root, "part_id")
        part_id_xml.text = str(self.part_id)
        unit_id_xml = Et.SubElement(root, "unit_id")
        unit_id_xml.text = str(self.unit_id)
        quantity_xml = Et.SubElement(root, "quantity")
        quantity_xml.text = str(self.quantity)
        inventory_location_id_xml = Et.SubElement(root, "inventory_location_id")
        inventory_location_id_xml.text = str(self.inventory_location_id)
        inventory_sublocation_id_xml = Et.SubElement(root, "inventory_sublocation_id")
        inventory_sublocation_id_xml.text = str(self.inventory_sublocation_id)
        if self.details is not None:
            details_xml = Et.SubElement(root, "details")
            details_xml.text = str(self.details)
        return root


class Quote(Entity):
    int_params = [
        "id",
        "part_id",
        "vendor_id",
        "unit_id",
        "quantity_min",
        "quantity_max",
        "leadtime",
        "inventory",
    ]
    float_params = ["price"]

    def __init__(
        self,
        part_id,
        vendor_id,
        unit_id,
        price,
        currency,
        quantity_min,
        quantity_mult,
        inventory=None,
        comment=None,
        leadtime=None,
    ):
        self.id = None
        self.part_id = part_id
        self.vendor_id = vendor_id
        self.unit_id = unit_id
        self.price = price
        self.currency = currency
        self.quantity_min = quantity_min
        self.quantity_mult = quantity_mult
        self.inventory = inventory
        self.comment = comment
        self.leadtime = leadtime

    def to_xml(self):
        root_xml = Et.Element("quote")
        part_id_xml = Et.SubElement(root_xml, "part_id")
        part_id_xml.text = str(self.part_id)
        vendor_id_xml = Et.SubElement(root_xml, "vendor_id")
        vendor_id_xml.text = str(self.vendor_id)
        price_xml = Et.SubElement(root_xml, "price")
        price_xml.text = str(self.price)
        quantity_min_xml = Et.SubElement(root_xml, "quantity_min")
        quantity_min_xml.text = str(self.quantity_min)
        quantity_mult_xml = Et.SubElement(root_xml, "quantity_mult")
        quantity_mult_xml.text = str(self.quantity_mult)
        if self.leadtime is not None:
            leadtime_xml = Et.SubElement(root_xml, "leadtime")
            leadtime_xml.text = str(self.leadtime)
        if self.inventory is not None:
            inventory_xml = Et.SubElement(root_xml, "inventory")
            inventory_xml.text = str(self.inventory)
        unit_id_xml = Et.SubElement(root_xml, "unit_id")
        unit_id_xml.text = str(self.unit_id)
        currency_id_xml = Et.SubElement(root_xml, "currency_id")
        currency_id_xml.text = str(self.currency)
        if self.comment is not None:
            comment_xml = Et.SubElement(root_xml, "comment")
            comment_xml.text = str(self.comment)
        return root_xml
