---
title: Pydantic types
updated: 2026-08-23
source: pydantic 2.13.4, pydantic-extra-types 2.11.1, pydantic-settings 2.15.0, read from the installed packages
---

Every type below validates in pydantic-core, so a PRD line that names one maps to the core schema bucket.

## Standard library, validated natively

str, bytes, int, float, bool, complex, Decimal, Fraction, None, list, tuple, set, frozenset, dict, deque, Sequence, Mapping, Iterable, Literal, Enum, IntEnum, StrEnum, datetime, date, time, timedelta, timezone, ZoneInfo, UUID, Path, PurePath, IPv4Address, IPv6Address, IPv4Network, IPv6Network, IPv4Interface, IPv6Interface, Pattern, TypedDict, NamedTuple, dataclass, Callable, type, Any, Optional, Union, Annotated, generics.

## pydantic

```csv
group,types
numbers,"PositiveInt, NegativeInt, NonNegativeInt, NonPositiveInt, PositiveFloat, NegativeFloat, NonNegativeFloat, NonPositiveFloat, FiniteFloat, AllowInfNan"
strict,"StrictBool, StrictInt, StrictFloat, StrictStr, StrictBytes, Strict"
strings and bytes,"StringConstraints, Base64Str, Base64Bytes, Base64UrlStr, Base64UrlBytes, EncodedStr, EncodedBytes, Base64Encoder, EncoderProtocol"
secrets,"SecretStr, SecretBytes, Secret"
time,"AwareDatetime, NaiveDatetime, PastDate, FutureDate, PastDatetime, FutureDatetime"
ids,"UUID1, UUID3, UUID4, UUID5, UUID6, UUID7, UUID8"
paths,"FilePath, DirectoryPath, NewPath, SocketPath"
json and imports,"Json, JsonValue, ImportString"
misc,"ByteSize, PaymentCardNumber, OnErrorOmit, FailFast"
union and schema control,"Discriminator, Tag, GetPydanticSchema"
legacy constrained functions,"conint, confloat, condecimal, constr, conbytes, condate, conlist, conset, confrozenset"
```

## pydantic.networks

```csv
group,types
urls,"AnyUrl, AnyHttpUrl, HttpUrl, FileUrl, FtpUrl, WebsocketUrl, AnyWebsocketUrl, UrlConstraints"
email,"EmailStr, NameEmail, validate_email"
ip,"IPvAnyAddress, IPvAnyInterface, IPvAnyNetwork"
dsn,"PostgresDsn, CockroachDsn, MySQLDsn, MariaDBDsn, ClickHouseDsn, SnowflakeDsn, MongoDsn, RedisDsn, AmqpDsn, KafkaDsn, NatsDsn"
```

EmailStr and NameEmail need the `email` extra. AwareDatetime and TimeZoneName need the `timezone` extra on Windows.

## pydantic_extra_types

```csv
module,types
color,"Color, RGBA"
coordinate,"Coordinate, Latitude, Longitude"
country,"CountryAlpha2, CountryAlpha3, CountryNumericCode, CountryShortName, CountryInfo"
currency_code,"Currency, ISO4217"
language_code,"LanguageAlpha2, LanguageName, ISO639_3, ISO639_5, LanguageInfo"
script_code,ISO_15924
timezone_name,"TimeZoneName, TimeZoneNameSettings"
phone_numbers,"PhoneNumber, PhoneNumberValidator"
payment,"PaymentCardNumber, PaymentCardBrand"
routing_number,ABARoutingNumber
iban,IBAN
isbn,ISBN
mac_address,MacAddress
domain,DomainStr
s3,S3Path
path,ResolvedPathType
mime_types,"MimeType, Application, Audio, Font, Haptics, Image, Message, Model, Multipart, Text, Video, MimeTypeInfo"
epoch,"Integer, Number"
cron,CronStr
semantic_version,SemanticVersion
ulid,ULID
mongo_object_id,MongoObjectId
pendulum_dt,"Date, DateTime, Time, Duration, DateTimeSettings"
```

The `all` extra installs the backing libraries: pycountry, phonenumbers, pendulum, semver, python-ulid, cron-converter, pymongo, uuid-utils, pytz, tzdata.

## pydantic_settings

No value types. Adds BaseSettings and sources: environment, dotenv, secrets directory, CLI, JSON, YAML, TOML, Azure Key Vault, AWS Secrets Manager, GCP Secret Manager.
