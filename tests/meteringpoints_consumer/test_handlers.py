# from typing import List
# from dataclasses import dataclass
#
# from energytt_platform.bus import messages as m
# from energytt_platform.models.meteringpoints import \
#     MeteringPoint, MeteringPointType
#
# from meteringpoints_shared.queries import MeteringPointQuery
# from meteringpoints_consumer.handlers import dispatcher
#
#
# # @dataclass
# # class NestedTestSerializable(Serializable):
# #     friends: List[str]
# #
# #
# # @dataclass
# # class TestSerializable(Serializable):
# #     name: str
# #     age: int
# #     nested: NestedTestSerializable
#
#
# class TestJsonSerializer:
#
#     def test__on_meteringpoint_added__should_add_meteringpoint_or_overwrite_properties(self):
#
#         dispatcher(m.MeteringPointAdded(
#             meteringpoint=MeteringPoint(
#                 gsrn='1',
#                 type=MeteringPointType.production,
#                 sector='DK1',
#             )
#         ))
#
#         # -- Arrange ---------------------------------------------------------
#
#         obj = TestSerializable(
#             name='John',
#             age=50,
#             nested=NestedTestSerializable(
#                 friends=['Bill', 'Joe', 'Tedd'],
#             )
#         )
#
#         uut = JsonSerializer()
#
#         # -- Act -------------------------------------------------------------
#
#         serialized = uut.serialize(obj)
#         deserialized = uut.deserialize(serialized, TestSerializable)
#
#         # -- Assert ----------------------------------------------------------
#
#         assert deserialized == obj
