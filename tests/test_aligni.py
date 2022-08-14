import pytest

import aligni.api


@pytest.fixture
def my_aligni_api():
    """Returns an Aligni API instance"""
    return aligni.api.API("demo", "oid3vLgynoy_Yl1gZkrgkLEq3J")


def test_lookup_manufacturer(my_aligni_api):
    x = my_aligni_api.manufacturers.lookup("name", "Kemet")
    assert x.name == "Kemet"
    assert x.id == 147


def test_lookup_vendor(my_aligni_api):
    x = my_aligni_api.vendors.lookup("name", "Digi-Key")
    assert x.name == "Digi-Key"
    assert x.id == 40


def test_lookup_unit(my_aligni_api):
    x = my_aligni_api.units.lookup("name", "foot")
    assert x.name == "foot"


def test_lookup_part(my_aligni_api):
    part = my_aligni_api.parts.lookup("id", 728)
    print(part)
    assert part.id == 728
    assert part.manufacturer_pn == "C0603C104K4RACTU"


def test_linecard(my_aligni_api):
    manuf_name = "Test Corp XYZ"
    # Check if manufacturer already exists and, if so, delete.
    x = my_aligni_api.manufacturers.lookup("name", manuf_name)
    if x is not None:
        my_aligni_api.manufacturers.delete(x)
    manuf = my_aligni_api.manufacturers.create(
        aligni.datatypes.Manufacturer(manuf_name)
    )
    vendor = my_aligni_api.vendors.lookup("name", "Digi-Key")
    my_aligni_api.linecards.create(aligni.datatypes.LineCard(vendor.id, manuf.id))
    manuf = my_aligni_api.manufacturers.lookup("name", manuf_name)
    full_manuf = my_aligni_api.manufacturers.get(manuf.id)
    assert full_manuf.vendor_ids[0] == vendor.id
    my_aligni_api.manufacturers.delete(manuf)


def test_create_parttype(my_aligni_api):
    test_parttype_name = "test_PartType"
    # Check if parttype already exists and, if so, delete.
    x = my_aligni_api.parttypes.lookup("name", test_parttype_name)
    if x is not None:
        my_aligni_api.parttypes.delete(x)

    # Attempt to create new parttype
    my_aligni_api.parttypes.create(aligni.datatypes.PartType(test_parttype_name))
    x = my_aligni_api.parttypes.lookup("name", test_parttype_name)
    assert x.name == test_parttype_name
    my_aligni_api.parttypes.delete(x)


def test_create_part(my_aligni_api):
    mpn = "1234ABC"
    manufacturer = my_aligni_api.manufacturers.lookup("name", "Kemet")
    parttype = my_aligni_api.parttypes.lookup("name", "Capacitor")
    unit = my_aligni_api.units.lookup("name", "each")

    # Check if part already exists and, if so, delete.
    x = my_aligni_api.parts.lookup("manufacturer_pn", mpn)
    if x is not None:
        # Must change all inventory to zero first.
        x_full = my_aligni_api.parts.get(x.id)
        if hasattr(x_full, "inventory_units"):
            for inventory_unit in x_full.inventory_units:
                my_aligni_api.partinventoryunits.adjust_quantity(x, inventory_unit, 0)
        my_aligni_api.parts.delete(x)
        check_part = my_aligni_api.parts.get(x.id)
        assert check_part is None

    part = my_aligni_api.parts.create(
        aligni.datatypes.Part(
            manufacturer_pn=mpn,
            manufacturer_id=manufacturer.id,
            parttype_id=parttype.id,
            unit_id=unit.id,
            description="Test Capacitor",
            value_text="1 u",
            estimated_cost=0.09,
            estimated_cost_currency="USD",
            manufactured_here=False,
            comment="0603 test cap",
            revision_name="01",
        )
    )
    assert part.id > 0
    aligni_part = my_aligni_api.parts.lookup("id", part.id)
    assert aligni_part.manufacturer_pn == mpn
    assert int(aligni_part.parttype_id) == parttype.id


def test_update_part(my_aligni_api):
    mpn = "1234ABC"
    part = my_aligni_api.parts.lookup("manufacturer_pn", mpn)
    assert part is not None
    my_aligni_api.parts.update(
        part, {"manufactured_here": "true", "estimated_cost": 0.55}
    )
    updated_part = my_aligni_api.parts.get(part.id)
    assert updated_part.manufactured_here is True
    assert updated_part.estimated_cost == 0.55


def test_release_part(my_aligni_api):
    # Use part created by test_create_part.
    mpn = "1234ABC"
    part = my_aligni_api.parts.lookup("manufacturer_pn", mpn)
    assert part is not None
    rev = my_aligni_api.partrevisions.get_list(part)
    my_aligni_api.partrevisions.release(part, rev[0])
    # TODO: Added check to confirm part was released.


def test_update_part_revisioned_parameter(my_aligni_api):
    mpn = "1234ABC"
    part = my_aligni_api.parts.lookup("manufacturer_pn", mpn)
    assert part is not None
    my_aligni_api.parts.update(part, {"revision/x_pcb_footprint_1": "Test1"})
    updated_part = my_aligni_api.parts.get(part.id)
    print(updated_part.revision)
    assert (
        updated_part.revision.revisioned_custom_parameters["x_pcb_footprint_1"]
        == "Test1"
    )


def test_create_inventory_sublocation(my_aligni_api):
    inventory_sublocation_name = "Test_Inventory_Sublocation"
    location = my_aligni_api.inventorylocation.get_list()[0]
    full_location = my_aligni_api.inventorylocation.get(location.id)
    for existing_sublocation in full_location.inventory_sublocations:
        if existing_sublocation.name == inventory_sublocation_name:
            my_aligni_api.inventorysublocation.delete(existing_sublocation)

    sublocation = my_aligni_api.inventorysublocation.create(
        aligni.datatypes.InventorySublocation(inventory_sublocation_name, location.id)
    )

    assert sublocation.id > 0
    updated_location = my_aligni_api.inventorylocation.get(location.id)
    sublocation_found = False
    for updated_sublocation in updated_location.inventory_sublocations:
        if updated_sublocation.name == inventory_sublocation_name:
            sublocation_found = True
            break
    assert sublocation_found


def test_create_inventory_unit(my_aligni_api):
    inventory_sublocation_name = "Test_Inventory_Sublocation"
    location = my_aligni_api.inventorylocation.get_list()[0]
    unit = my_aligni_api.units.lookup("name", "each")
    full_location = my_aligni_api.inventorylocation.get(location.id)
    sublocation = None
    for existing_sublocation in full_location.inventory_sublocations:
        if existing_sublocation.name == inventory_sublocation_name:
            sublocation = existing_sublocation
            break
    assert sublocation

    mpn = "1234ABC"
    part = my_aligni_api.parts.lookup("manufacturer_pn", mpn)
    assert part is not None

    inventory_unit = my_aligni_api.partinventoryunits.create(
        part,
        aligni.datatypes.InventoryUnit(
            part_id=part.id,
            unit_id=unit.id,
            quantity=10,
            inventory_location_id=location.id,
            inventory_sublocation_id=sublocation.id,
        ),
    )
    assert inventory_unit.id > 0
    part_full = my_aligni_api.parts.get(part.id)
    assert part_full.inventory_units[0].quantity == 10


def test_adjust_inventory(my_aligni_api):
    mpn = "1234ABC"
    part = my_aligni_api.parts.lookup("manufacturer_pn", mpn)
    assert part is not None
    part_full = my_aligni_api.parts.get(part.id)
    inventory_unit = part_full.inventory_units[0]

    my_aligni_api.partinventoryunits.adjust_quantity(part, inventory_unit, 200)

    updated_part = my_aligni_api.parts.get(part.id)
    assert updated_part.inventory_units[0].quantity == 200


def test_delete_part(my_aligni_api):
    mpn = "1234ABC"
    part = my_aligni_api.parts.lookup("manufacturer_pn", mpn)
    assert part is not None
    # Must change all inventory to zero first.
    part_full = my_aligni_api.parts.get(part.id)
    if hasattr(part_full, "inventory_units"):
        for inventory_unit in part_full.inventory_units:
            my_aligni_api.partinventoryunits.adjust_quantity(part, inventory_unit, 0)
    my_aligni_api.parts.delete(part)
    check_part = my_aligni_api.parts.get(part.id)
    assert check_part is None
