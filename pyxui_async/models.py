import json

from pydantic import BaseModel, field_validator
from typing import List, Optional, Any, Union, Dict

POST = 'POST'
GET = 'GET'


class Client(BaseModel):
    id: Optional[str] = "" # UUID
    flow: Optional[str] = ""
    email: str  # уникальный email клиента, используется для поиска и операций
    limitIp: Optional[int] = 0
    totalGB: Optional[int] = 0
    expiryTime: Optional[int] = 0
    enable: Optional[bool] = True
    tgId: Optional[Any] = ""  # может быть int или str
    subId: Optional[str] = ""  # id подписки
    reset: Optional[int] = 0
    comment: Optional[str] = ""
    security: Optional[str] = ""  # для некоторых протоколов
    password: Optional[str] = ""  # для некоторых протоколов
    created_at: Optional[int] = None
    updated_at: Optional[int] = None

class ClientSettings(BaseModel):
    clients: List[Client]

class AddClientRequest(BaseModel):
    id: int
    settings: ClientSettings


class RealitySettings(BaseModel):
    show: bool
    xver: int
    dest: Optional[str] = None
    serverNames: List[str]
    privateKey: str
    minClient: Optional[str] = None
    maxClient: Optional[str] = None
    minClientVer: Optional[str] = None
    maxClientVer: Optional[str] = None
    maxTimediff: int
    shortIds: List[str]
    mldsa65Seed: Optional[str]
    settings: Dict[str, Any]


class TcpSettings(BaseModel):
    acceptProxyProtocol: bool
    header: Dict[str, str]


class Certificate(BaseModel):
    certificateFile: Optional[str] = ""
    keyFile: Optional[str] = ""
    oneTimeLoading: Optional[bool] = False
    usage: Optional[str] = "encipherment"
    buildChain: Optional[bool] = False

    @field_validator('certificateFile', 'keyFile', mode='before')
    @classmethod
    def empty_string_to_none(cls, v):
        if v == "":
            return None
        return v


class TlsSettingsInner(BaseModel):
    allowInsecure: Optional[bool] = False
    fingerprint: Optional[str] = None
    echConfigList: Optional[str] = None

    @field_validator('fingerprint', 'echConfigList', mode='before')
    @classmethod
    def empty_string_to_none(cls, v):
        if v == "":
            return None
        return v


class TlsSettings(BaseModel):
    serverName: Optional[str] = None
    minVersion: Optional[str] = ""
    maxVersion: Optional[str] = ""
    cipherSuites: Optional[str] = None
    rejectUnknownSni: Optional[bool] = False
    verifyPeerCertInNames: Optional[List[str]] = []
    disableSystemRoot: Optional[bool] = False
    enableSessionResumption: Optional[bool] = False
    certificates: Optional[List[Certificate]] = []
    alpn: Optional[List[str]] = []
    echServerKeys: Optional[str] = None
    echForceQuery: Optional[str] = "none"
    settings: Optional[TlsSettingsInner] = None

    @field_validator('serverName', 'cipherSuites', 'echServerKeys', mode='before')
    @classmethod
    def empty_string_to_none(cls, v):
        if v == "":
            return None
        return v


class StreamSettings(BaseModel):
    network: str
    security: str
    externalProxy: List[Any] = []
    realitySettings: Optional[RealitySettings] = None
    tcpSettings: Optional[TcpSettings] = None
    tlsSettings: Optional[TlsSettings] = None


class SniffingSettings(BaseModel):
    enabled: bool
    destOverride: List[str]
    metadataOnly: Optional[bool] = False
    routeOnly: Optional[bool] = False


# Исправленная модель InboundSettings - clients теперь опциональное
class InboundSettings(BaseModel):
    clients: Optional[List[Client]] = []  # Сделано опциональным для протоколов типа Wireguard
    fallbacks: List[Any] = []
    # Добавляем дополнительные поля для Wireguard и других протоколов
    mtu: Optional[int] = None
    secretKey: Optional[str] = None
    peers: Optional[List[Dict[str, Any]]] = []
    reserved: Optional[List[int]] = []
    workers: Optional[int] = None
    domainStrategy: Optional[str] = None
    noKernelTun: Optional[bool] = None


# Исправленная модель Sniffing - все поля опциональные с дефолтными значениями
class Sniffing(BaseModel):
    enabled: bool
    destOverride: List[str]
    metadataOnly: Optional[bool] = False  # Сделано опциональным с дефолтом
    routeOnly: Optional[bool] = False     # Сделано опциональным с дефолтом


class InboundRequest(BaseModel):
    up: int
    down: int
    total: int
    remark: str
    enable: bool
    expiryTime: int
    listen: str
    port: int
    protocol: str
    settings: InboundSettings
    streamSettings: Optional[StreamSettings] = None
    sniffing: Optional[SniffingSettings] = None
    allocate: Optional[Any] = None


class InboundClientStats(BaseModel):
    id: int
    inboundId: int
    enable: bool
    email: str
    up: int
    down: int
    allTime: int
    expiryTime: int
    total: int
    reset: int
    lastOnline: int

class Inbound(BaseModel):
    id: int
    up: int
    down: int
    total: int
    allTime: int
    remark: str
    enable: bool
    expiryTime: int
    clientStats: Optional[List[InboundClientStats]] = []
    listen: str
    port: int
    protocol: str
    settings: InboundSettings
    streamSettings: Optional[StreamSettings] = None
    tag: str
    sniffing: Sniffing

    @field_validator('settings', mode='before')
    @classmethod
    def parse_settings(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

    @field_validator('sniffing', mode='before')
    @classmethod
    def parse_sniffing(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        elif isinstance(v, dict):
            # Добавляем дефолтные значения если их нет
            if 'metadataOnly' not in v:
                v['metadataOnly'] = False
            if 'routeOnly' not in v:
                v['routeOnly'] = False
        return v

    @field_validator('streamSettings', mode='before')
    @classmethod
    def parse_stream_settings(cls, v):
        if isinstance(v, str):
            if v.strip() == '':  # Обработка пустых строк
                return None
            return json.loads(v)
        return v


class ResponseBase(BaseModel):
    success: bool
    msg: str
    obj: Optional[Any] = None

class InboundsResponse(ResponseBase):
    success: bool
    msg: str
    obj: List[Inbound]

class InboundResponse(ResponseBase):
    obj: Optional[Inbound]

class ClientTraffic(BaseModel):
    id: int
    inboundId: int
    enable: bool
    email: str
    up: int
    down: int
    allTime: int
    expiryTime: int
    total: int
    reset: int
    lastOnline: int

class ClientTrafficsResponse(ResponseBase):
    obj: Optional[Union[ClientTraffic, List[ClientTraffic]]]

class GenericObjResponse(ResponseBase):
    obj: Optional[Any]

class UUIDData(BaseModel):
    uuid: str

class UUIDResponse(ResponseBase):
    obj: UUIDData

class X25519CertResponse(ResponseBase):
    obj: Dict[str, str]

class Mldsa65Response(ResponseBase):
    obj: Dict[str, str]

class VlessEncAuth(BaseModel):
    decryption: str
    encryption: str
    label: str

class VlessEncResponse(ResponseBase):
    obj: Dict[str, List[VlessEncAuth]]

class EchCertResponse(ResponseBase):
    obj: Dict[str, str]