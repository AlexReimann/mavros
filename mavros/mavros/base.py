# -*- coding: utf-8 -*-
# vim:set ts=4 sw=4 et:
#
# Copyright 2021 Vladimir Ermakov.
#
# This file is part of the mavros package and subject to the license terms
# in the top-level LICENSE file of the mavros repository.
# https://github.com/mavlink/mavros/tree/master/LICENSE.md

import random
import string
import typing
from functools import cached_property  # noqa F401

import rclpy  # noqa F401
import rclpy.node
import rclpy.qos

DEFAULT_NAMESPACE = 'mavros'
DEFAULT_NODE_NAME_PREFIX = 'mavpy_'

# STATE_QOS used for state topics, like ~/state, ~/mission/waypoints etc.
STATE_QOS = rclpy.qos.QoSProfile(
    depth=10, durability=rclpy.qos.QoSDurabilityPolicy.TRANSIENT_LOCAL)

# SENSOR_QOS used for most of sensor streams
SENSOR_QOS = rclpy.qos.QoSPresetProfiles.SENSOR_DATA

TopicType = typing.Union[typing.Tuple, str]
QoSType = typing.Union[rclpy.qos.QoSProfile, int]
ServiceCallable = rclpy.node.Callable[
    [rclpy.node.SrvTypeRequest, rclpy.node.SrvTypeResponse],
    rclpy.node.SrvTypeResponse]
SubscriptionCallable = rclpy.node.Callable[[rclpy.node.MsgType], None]


class BaseNode(rclpy.node.Node):
    """
    Base class for mavros client object. It's used to hide plugin parameters.
    """

    _ns: str

    def __init__(self,
                 node_name: typing.Optional[str] = None,
                 mavros_ns: str = DEFAULT_NAMESPACE):
        """
        :param node_name: name of the node, would be random if None
        :param mavros_ns: node name of mavros::UAS
        """
        if node_name is None:
            node_name = DEFAULT_NODE_NAME_PREFIX + ''.join(
                random.choices(string.ascii_lowercase + string.digits, k=4))

        super().__init__(node_name)
        self._ns = mavros_ns

    def get_topic(self, *args: str) -> str:
        return '/'.join((self._ns, ) + args)


class PluginModule:
    """
    PluginModule is a base class for modules used to talk to mavros plugins
    """

    _node: BaseNode

    def __init__(self, parent_node: BaseNode):
        self._node = parent_node

    def create_publisher(self, msg_type: rclpy.node.MsgType, topic: TopicType,
                         qos_profile: QoSType, *,
                         **kwargs) -> rclpy.node.Publisher:
        if isinstance(topic, str):
            topic = (topic, )

        return self._node.create_publisher(msg_type,
                                           self._node.get_topic(*topic),
                                           qos_profile, **kwargs)

    def create_subscription(self, msg_type: rclpy.node.MsgType,
                            topic: TopicType, callback: SubscriptionCallable,
                            qos_profile: QoSType, *,
                            **kwargs) -> rclpy.node.Subscription:
        if isinstance(topic, str):
            topic = (topic, )

        return self._node.create_subscription(msg_type,
                                              self._node.get_topic(*topic),
                                              callback, qos_profile, **kwargs)

    def create_client(self, srv_type: rclpy.node.SrvType, srv_name: TopicType,
                      *, **kwargs) -> rclpy.node.Client:
        if isinstance(srv_name, str):
            srv_name = (srv_name, )

        return self._node.create_client(srv_type,
                                        self._node.get_topic(*srv_name),
                                        **kwargs)

    def create_service(self, srv_type: rclpy.node.SrvType, srv_name: TopicType,
                       callback: ServiceCallable, *,
                       **kwargs) -> rclpy.node.Service:
        if isinstance(srv_name, str):
            srv_name = (srv_name, )

        return self._node.create_service(srv_type,
                                         self._node.get_topic(*srv_name),
                                         callback, **kwargs)