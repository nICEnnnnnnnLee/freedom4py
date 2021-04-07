#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import struct
import socket
from io import BytesIO
# https://tools.ietf.org/html/rfc1035


class DNS:
    def __init__(self, id, query, answer):
        self.id = id
        self.query = query
        self.answer = answer


class Query:
    def __init__(self, _name, _type, _class):
        self._name = _name
        self._type = _type
        self._class = _class


class Answer:
    def __init__(self, _name, _type, _class, _ttl, _rData):
        self._name = _name
        self._type = _type
        self._class = _class
        self._ttl = _ttl
        self._rData = _rData


def parse(plainResonse: bytes, query: None or 'offetQuestion' or 'offetAnswer' or 'offetAuthority' or 'offetAdditional' = None):
    # https://tools.ietf.org/html/rfc1035#24
    try:
        offetHeader = 0
        _id = struct.unpack_from('>H', plainResonse, 0)[0]
        # tt = struct.unpack_from('>H', plainResonse, 2)[0]
        _qd_count = struct.unpack_from('>H', plainResonse, 4)[0]
        _an_count = struct.unpack_from('>H', plainResonse, 6)[0]
        _ns_count = struct.unpack_from('>H', plainResonse, 8)[0]
        _ar_count = struct.unpack_from('>H', plainResonse, 10)[0]
        # print(_qd_count, _an_count, _ns_count, _ar_count)
        offetQuestion = offetHeader + 12
        if query == 'offetQuestion':
            return offetQuestion
        dns = DNS(_id, [], [])
        # Question
        for i in range(_qd_count):
            offetQuestion, query = parseQD(plainResonse, offetQuestion)
            dns.query.append(query)
        # Answer
        offetAnswer = offetQuestion
        if query == 'offetAnswer':
            return offetAnswer
        for i in range(_an_count):
            offetAnswer, answer = parse_RR(plainResonse, offetAnswer)
            if len(answer._rData) <= 15:  # \d{3}.\d{3}.\d{3}.\d{3}
                dns.answer.append(answer)
        # Authority records
        offetAuthority = offetAnswer
        if query == 'offetAuthority':
            return offetAuthority
        for i in range(_ns_count):
            offetAuthority, _ = parse_RR(plainResonse, offetAuthority)
        # Additional records
        offetAdditional = offetAuthority
        if query == 'offetAdditional':
            return offetAdditional
        for i in range(_ar_count):
            offetAdditional, _ = parse_RR(plainResonse, offetAdditional)
        return dns
    except:
        print('not a valid DNS message')
        return None


def parse_field(plainResonse: bytes, offset):
    _len = plainResonse[offset]
    if _len == 0:
        return None, offset + 1
    _offset_begin = offset + 1
    _offset_end = _offset_begin + _len
    _value = plainResonse[_offset_begin: _offset_end].decode()
    return _value, _offset_end


def parse_name(plainResonse: bytes, offset):
    names = []
    while True:
        value, offset = parse_field(plainResonse, offset)
        if value:
            names.append(value)
        else:
            break
    return '.'.join(names), offset


def parseQD(plainResonse: bytes, offset_QD):
    '''
    https://tools.ietf.org/html/rfc1035#25
    QNAME       xN
    QTYPE       x2
    QCLASS      x2
    '''
    offsetQName = offset_QD
    _qname, offsetQType = parse_name(plainResonse, offsetQName)
    offsetQClass = offsetQType + 2
    offsetEnd = offsetQClass + 2
    _qtype = struct.unpack_from('>H', plainResonse, offsetQType)[0]
    _qclass = struct.unpack_from('>H', plainResonse, offsetQClass)[0]
    query = Query(_qname, _qtype, _qclass)
    return offsetEnd, query


def parse_RR(plainResonse: bytes, offset_RR):
    '''
    https://tools.ietf.org/html/rfc1035#10
    https://tools.ietf.org/html/rfc1035#28
    # NAME      xN
    # TYPE      x2
    # CLASS     x2
    # TTL       x4
    # RDLENGTH  x2
    # RDATA     xN
    '''

    offsetName = offset_RR
    _name, offsetType = parse_name(plainResonse, offsetName)
    offsetClass = offsetType + 2
    offsetTTL = offsetClass + 2
    offsetRdLength = offsetTTL + 4
    RdLength = struct.unpack_from('>H', plainResonse, offsetRdLength)[0]
    offsetRData = offsetRdLength + 2
    offsetEnd = offsetRData + RdLength
    _type = struct.unpack_from('>H', plainResonse, offsetType)[0]
    _class = struct.unpack_from('>H', plainResonse, offsetClass)[0]
    _ttl = struct.unpack_from('>I', plainResonse, offsetTTL)[0]
    # _rData = socket.inet_ntoa(plainResonse[offsetRData: offsetRData + RdLength])
    _rData = struct.unpack_from(
        ''.join(['B' for x in range(RdLength)]), plainResonse, offsetRData)
    _rData = [str(x) for x in list(_rData)]
    _rData = '.'.join(_rData)
    answer = Answer(_name, _type, _class, _ttl, _rData)
    return offsetEnd, answer


def _write_query(_io, domain):
    # 写域名
    labels = domain.split('.')
    for label in labels:
        bytes_label = label.encode()
        _io.write(len(bytes_label).to_bytes(1, byteorder='big', signed=False))
        _io.write(bytes_label)
    _io.write(b'\x00')
    # 写类型
    # type A, class IN
    type_and_class = bytearray(4)
    struct.pack_into('>HH', type_and_class, 0, 1, 1)
    _io.write(type_and_class)


def _write_answer(_io, domain, ip, ttl):
    # 写域名
    labels = domain.split('.')
    for label in labels:
        bytes_label = label.encode()
        _io.write(len(bytes_label).to_bytes(1, byteorder='big', signed=False))
        _io.write(bytes_label)
    _io.write(b'\x00')
    # 其它
    type_class_ttl_iplength = bytearray(10)
    struct.pack_into('>HHIH', type_class_ttl_iplength, 0, 1, 1, ttl, 4)
    _io.write(type_class_ttl_iplength)
    # 写ip
    _io.write(socket.inet_aton(ip))


def gen_A_query(domain, id=0):
    # https://tools.ietf.org/html/rfc1035#24
    # qd =1, an=ns=ar=0,
    # QR(1) Opcode(4) AA(1) TC(1) RD(1) RA(1)   Z(3)   RCODE(4)
    # 0     0000       0      0     0    0      000     0000
    f = BytesIO()
    # 写头部
    header = bytearray(12)
    struct.pack_into('>HHHHHH', header, 0, id, 0, 1, 0, 0, 0)
    f.write(header)
    # 写query
    _write_query(f, domain)
    data = f.getvalue()
    f.close()
    return data


def gen_empty_response(domain, id=0):
    f = BytesIO()
    header = bytearray(12)
    struct.pack_into('>HHHHHH', header, 0, id, 33152, 1, 0, 0, 0)
    f.write(header)
    _write_query(f, domain)
    data = f.getvalue()
    f.close()
    return data


def gen_A_response(domain, ip, id=0, ttl=19808):
    # https://tools.ietf.org/html/rfc1035#24
    # an =1, qd=ns=ar=0,
    # QR(1) Opcode(4) AA(1) TC(1) RD(1) RA(1)   Z(3)   RCODE(4)
    # 1     0000       0      0     1    0      000     0000
    f = BytesIO()
    # 写头部
    header = bytearray(12)
    struct.pack_into('>HHHHHH', header, 0, id, 33152, 1, 1, 0, 0)
    f.write(header)
    _write_query(f, domain)
    _write_answer(f, domain, ip, ttl)
    data = f.getvalue()
    f.close()
    return data


if __name__ == '__main__':
    res_bytes = gen_A_query('www.example.com', id=0)
    print(res_bytes)
    parse(res_bytes)
    res_bytes = gen_A_response('www.example.com', '93.184.216.34', id=0)
    print(res_bytes)
    parse(res_bytes)
