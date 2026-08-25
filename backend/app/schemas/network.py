from ipaddress import IPv4Address

from pydantic import BaseModel, Field, field_validator


class NetworkInfoResponse(BaseModel):
    client_ip: str | None
    scanner_ip: str | None


class NetworkScanRequest(BaseModel):
    start_ip: str = Field(
        ...,
        description="First IPv4 address to inspect.",
    )

    end_ip: str = Field(
        ...,
        description="Last IPv4 address to inspect.",
    )

    @field_validator("start_ip", "end_ip")
    @classmethod
    def validate_ipv4(cls, value: str) -> str:
        try:
            address = IPv4Address(value)
        except ValueError as exc:
            raise ValueError(
                "Must be a valid IPv4 address"
            ) from exc

        return str(address)


class DiscoveredHost(BaseModel):
    ip: str
    hostname: str | None = None
    reachable: bool


class NetworkScanResponse(BaseModel):
    start_ip: str
    end_ip: str
    requested_hosts: int
    reachable_hosts: int
    hosts: list[DiscoveredHost]