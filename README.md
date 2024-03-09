# auth-poc

## Prerequisites

- [rye](https://rye-up.com/)
- [SpiceDB](https://authzed.com/docs/spicedb/getting-started/installing-spicedb)
- [Zed](https://authzed.com/docs/spicedb/getting-started/installing-zed)
- [REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client)

## Getting Started

#### Start SpiceDB

```shell
spicedb serve --grpc-preshared-key "freshbeef"
```

#### Start app

```shell
rye run flask --app auth_poc run
```

## Running the tests

#### Prepare test data

```shell
zed context set auth localhost:50051 freshbeef --insecure
zed schema write auth.zed
zed relationship create content:1234 writer user:jon
zed relationship create content:1234 reader user:alice
zed relationship create content:1234 writer user:alice
```

#### Run tests

- use test.http
