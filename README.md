# PYarn

If, for some weird reason, you need to parse a Yarn's `yarn.lock` file using
Python, you are in the right place!

PYarn is currently in an early developmente stage. It will create a dict from a
yarn.lock file, given the yarn.lock file is correct as per [its
implementation](https://github.com/yarnpkg/yarn/blob/master/src/lockfile/parse.js).
At this moment, there is no guarantees that PYarn will behave well (e.g., raise
an error) in case a malformed Yarn lockfile is passed to PYarn.

PYarn only supports Yarn v1 lockfiles. Parsing Yarn v2 lockfiles should be
trivial since they are yaml files.

## Development

```
make devel
make check
```

## Usage

The following prints all the content in the `yarn.lock` file:

```
from pyarn import lockfile

my_lockfile = lockfile.Lockfile.from_file(FILE_NAME)
print(my_lockfile.data)
# or
my_lockfile.to_json()
```

`my_lockfile.data` is a `dict` where the top level keys are the top level entries
(i.e., the package names) for the `yarn.lock` file entries.
