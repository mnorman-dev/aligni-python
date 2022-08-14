import xml.etree.ElementTree as Et


class _BaseCreateDelete:
    """Class for the simplist endpoint which only supports create & delete"""

    def __init__(self, post_cmd, delete_cmd, aligni_type, aligni_endpoint):
        self.post_cmd = post_cmd
        self.delete_cmd = delete_cmd
        self.aligni_type = aligni_type
        self.aligni_endpoint = aligni_endpoint

    def create(self, obj):
        xml_string = Et.tostring(obj.to_xml()).decode()
        resp = self.post_cmd(self.aligni_endpoint.format(""), xml_string)
        return self.aligni_type.from_xml(resp)

    def delete(self, obj):
        self.delete_cmd(self.aligni_endpoint.format(obj.id))


class _BaseCreateGetDelete(_BaseCreateDelete):
    """Class for basic endpoints which support get in addition to create & delete"""

    def __init__(self, get_cmd, post_cmd, delete_cmd, aligni_type, aligni_endpoint):
        self.get_cmd = get_cmd
        self.post_cmd = post_cmd
        self.delete_cmd = delete_cmd
        self.aligni_type = aligni_type
        self.aligni_endpoint = aligni_endpoint

    def get(self, obj_id):
        resp = self.get_cmd(self.aligni_endpoint.format(obj_id))
        if resp is None:
            return None
        else:
            return self.aligni_type.from_xml(resp)


class _BaseList:
    """Class for types which allow a full list of objects to be downloaded.
    This class caches the list of data locally to avoid having to download multiple times."""

    def __init__(
        self, get_cmd, post_cmd, put_cmd, delete_cmd, aligni_type, aligni_endpoint
    ):
        self.get_cmd = get_cmd
        self.post_cmd = post_cmd
        self.put_cmd = put_cmd
        self.delete_cmd = delete_cmd
        self.aligni_type = aligni_type
        self.aligni_endpoint = aligni_endpoint
        self.data = None

    def get_list(self):
        if self.data is None:
            resp = self.get_cmd(self.aligni_endpoint.format(""))
            # Parse the response
            self.data = []
            for item in resp:
                self.data.append(self.aligni_type.from_xml(item))
        return self.data

    def get(self, obj_id):
        resp = self.get_cmd(self.aligni_endpoint.format(obj_id))
        if resp is None:
            return None
        else:
            return self.aligni_type.from_xml(resp)

    def lookup(self, attribute_name, attribute_data):
        list_obj = self.get_list()
        for m in list_obj:
            d = getattr(m, attribute_name)
            if d == attribute_data:
                return m
        return None

    def create(self, obj):
        xml_string = Et.tostring(obj.to_xml()).decode()
        resp = self.post_cmd(self.aligni_endpoint.format(""), xml_string)
        # Force list to be regenerated
        self.data = None
        return self.aligni_type.from_xml(resp)

    def update(self, obj, changes_dict):
        obj_xml = obj.to_xml()
        obj_name = obj_xml.tag
        changes_xml = Et.Element(obj_name)
        for change_key in changes_dict:
            change_key_items = change_key.split("/")
            change_xml = Et.SubElement(changes_xml, str(change_key_items[0]))
            for change_key_item in change_key_items[1:]:
                change_xml = Et.SubElement(change_xml, str(change_key_item))
            change_xml.text = str(changes_dict[change_key])
        xml_string = Et.tostring(changes_xml).decode()
        resp = self.put_cmd(self.aligni_endpoint.format(obj.id), xml_string)
        return self.aligni_type.from_xml(resp)

    def delete(self, obj):
        self.delete_cmd(self.aligni_endpoint.format(obj.id))
        # Force list to be regenerated
        self.data = None


# Linecard API unlike other API does not use XML Data.
# Simply, sending a request for POST and DELTE at the end point /linecard?vendor_id=X&manufacturer_id=Y
# will create a linecard relationship between vendor with id X and manufacturer with id Y
class _Linecard:
    def __init__(self, post_cmd, delete_cmd, aligni_type, aligni_endpoint):
        self.post_cmd = post_cmd
        self.delete_cmd = delete_cmd
        self.aligni_type = aligni_type
        self.aligni_endpoint = aligni_endpoint

    def create(self, obj):
        endpoint = self.aligni_endpoint.format(
            int(obj.vendor_id), int(obj.manufacturer_id)
        )
        resp = self.post_cmd(endpoint, "")
        return resp

    def delete(self, obj):
        self.aligni_endpoint = self.aligni_endpoint.format(
            int(obj.vendor_id), int(obj.manufacturer_id)
        )
        self.delete_cmd(self.aligni_endpoint)


class _BasePart:
    """Class used for Part revision and inventory items due to the unique fields."""

    def __init__(self, get_cmd, post_cmd, delete_cmd, aligni_type, aligni_endpoint):
        self.get_cmd = get_cmd
        self.post_cmd = post_cmd
        self.delete_cmd = delete_cmd
        self.aligni_type = aligni_type
        self.aligni_endpoint = aligni_endpoint

    def get_list(self, part):
        resp = self.get_cmd(self.aligni_endpoint.format(part.id, ""))
        # Parse the response
        data = []
        for item in resp:
            data.append(self.aligni_type.from_xml(item))
        return data

    def get(self, part, part_subitem):
        resp = self.get_cmd(self.aligni_endpoint.format(part.id, part_subitem.id))
        return self.aligni_type.from_xml(resp)

    def create(self, part, part_subitem):
        xml_string = Et.tostring(part_subitem.to_xml()).decode()
        resp = self.post_cmd(self.aligni_endpoint.format(part.id, ""), xml_string)
        return self.aligni_type.from_xml(resp)

    def delete(self, part, part_subitem):
        self.delete_cmd(self.aligni_endpoint.format(part.id, part_subitem.id))


class _PartRevision(_BasePart):
    def __init__(self, get_cmd, post_cmd, delete_cmd, aligni_type, aligni_endpoint):
        self.get_cmd = get_cmd
        self.post_cmd = post_cmd
        self.delete_cmd = delete_cmd
        self.aligni_type = aligni_type
        self.aligni_endpoint = aligni_endpoint

    # Specific function for releasing part revisions.
    # The function fails when their are more than one revisions for the part
    def release(self, part, part_revision):
        self.post_cmd(
            self.aligni_endpoint.format(part.id, part_revision.id) + "/release",
            params={"bypass_part_ancestor_up_rev_guard": "keep"},
        )


class _PartInventory(_BasePart):
    def __init__(
        self, get_cmd, post_cmd, put_cmd, delete_cmd, aligni_type, aligni_endpoint
    ):
        self.get_cmd = get_cmd
        self.post_cmd = post_cmd
        self.put_cmd = put_cmd
        self.delete_cmd = delete_cmd
        self.aligni_type = aligni_type
        self.aligni_endpoint = aligni_endpoint

    def adjust_quantity(self, part, inventory_unit, quantity):
        self.put_cmd(
            self.aligni_endpoint.format(part.id, inventory_unit.id)
            + "/adjust_quantity",
            params={"inventory_unit[quantity]": str(quantity)},
        )
