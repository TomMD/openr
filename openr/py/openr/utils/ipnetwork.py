#!/usr/bin/env python3

#
# Copyright (c) 2014-present, Facebook, Inc.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

from __future__ import absolute_import, division, print_function, unicode_literals

import ipaddress
import socket

from openr.Lsdb import ttypes as lsdb_types
from openr.Network import ttypes as network_types


def sprint_addr(addr):
    """ binary ip addr -> string """

    if not len(addr):
        return ""

    return str(ipaddress.ip_address(addr))


def sprint_prefix(prefix):
    """
    :param prefix: network_types.IpPrefix representing an CIDR network

    :returns: string representation of prefix (CIDR network)
    :rtype: str or unicode
    """

    return "{}/{}".format(sprint_addr(prefix.prefixAddress.addr), prefix.prefixLength)


def ip_str_to_addr(addr_str):
    """
    :param addr_str: ip address in string representation

    :returns: thrift struct BinaryAddress
    :rtype: network_types.BinaryAddress
    """

    # Try v4
    try:
        addr = socket.inet_pton(socket.AF_INET, addr_str)
        return network_types.BinaryAddress(addr=addr)
    except socket.error:
        pass

    # Try v6
    addr = socket.inet_pton(socket.AF_INET6, addr_str)
    return network_types.BinaryAddress(addr=addr)


def ip_str_to_prefix(prefix_str):
    """
    :param prefix_str: string representing a prefix (CIDR network)

    :returns: thrift struct IpPrefix
    :rtype: network_types.IpPrefix
    """

    ip_str, ip_len_str = prefix_str.split("/")
    return network_types.IpPrefix(
        prefixAddress=ip_str_to_addr(ip_str), prefixLength=int(ip_len_str)
    )


def sprint_prefix_type(prefix_type):
    """
    :param prefix: lsdb_types.PrefixType
    """

    return lsdb_types.PrefixType._VALUES_TO_NAMES.get(prefix_type, None)


def sprint_prefix_forwarding_type(forwarding_type):
    """
    :param forwarding_type: lsdb_types.PrefixForwardingType
    """

    return lsdb_types.PrefixForwardingType._VALUES_TO_NAMES.get(forwarding_type)


def sprint_prefix_is_ephemeral(prefix_entry: lsdb_types.PrefixEntry) -> str:
    """
    :param prefix_entry: lsdb_types.PrefixEntry
    """

    return (
        str(prefix_entry.ephemeral) if prefix_entry.ephemeral is not None else "False"
    )


def ip_version(addr):
    """ return ip addr version
    """

    return ipaddress.ip_address(addr).version


def is_same_subnet(addr1, addr2, subnet):
    """
    Check whether two given addresses belong to the same subnet
    """

    if ipaddress.ip_network((addr1, subnet), strict=False) == ipaddress.ip_network(
        (addr2, subnet), strict=False
    ):
        return True

    return False


def is_link_local(addr):
    """
    Check whether given addr is link local or not
    """
    return ipaddress.ip_network(addr).is_link_local


def is_subnet_of(a, b):
    """
    Check if network-b is subnet of network-a
    """

    if a.network_address != b.network_address:
        return False

    return a.prefixlen >= b.prefixlen


def contain_any_prefix(prefix, ip_networks):
    """
    Utility function to check if prefix contain any of the prefixes/ips

    :returns: True if prefix contains any of the ip_networks else False
    """

    if ip_networks is None:
        return True
    prefix = ipaddress.ip_network(prefix)
    return any(is_subnet_of(prefix, net) for net in ip_networks)
