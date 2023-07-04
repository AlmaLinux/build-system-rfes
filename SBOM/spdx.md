# [RFE] Support for SPDX SBOM generation

## Introduction

### Purpose of this document

As a follow up on the [initial implementation of SBOM](https://github.com/AlmaLinux/build-system-rfes/blob/master/SBOM/SBOM.md), this document aims to describe the way we want to add support to [alma-sbom](https://github.com/AlmaLinux/alma-sbom) for SPDX SBOM generation.

### Why SPDX?

Initially, **alma-sbom** was implemented to generate SBOM documents in [OWASP CycloneDX](https://cyclonedx.org/) SBOM format, and as described in the [SBOM RFE](https://github.com/AlmaLinux/build-system-rfes/blob/master/SBOM/SBOM.md), we wanted to also extend its support to generate SBOM documents in the popular ISO-standarized format backed by the Linux Foundation, [SPDX](https://spdx.dev/).

The benefit, the AlmaLinux OS community would be able to generate SBOM documents in two of the most popular SBOM standards available.

## SPDX support overview

### Changes to be made on alma-sbom

We need to extend alma-sbom in different ways:

#### 1. SPDX formatter

Add an SPDX formatter in the same way we already have one for [CycloneDX](https://github.com/AlmaLinux/alma-sbom/blob/main/libsbom/cyclonedx.py)

#### 2. Extending alma-sbom CLI

Extend the command line options of alma-sbom in a way that we can generate SBOMs according to SPDX specification and in different output formats. Currently, we can generate SBOMs using CycloneDX into both JSON and XML formats, and we can generate SPDX SBOMs into:

* JSON
* XML
* Tag/Value
* YAML

Generating SPDX SBOMs into different formats is currently provided by [spdx-tools](https://pypi.org/project/spdx-tools/), which alma-sbom will depend on. This module also provides
support for RDF format, but which has not been added to alma-sbom yet.

### SPDX SBOM data

Both SPDX and CycloneDX SBOMs will share, mostly, the same data. There will be only changes in how the data is presented in SBOM records.
To have an idea of the data that make up a SBOM record, you can check it in the [SBOM RFE](https://github.com/AlmaLinux/build-system-rfes/blob/master/SBOM/SBOM.md).

Ideally, common data could be included as part of a DB record, this way, we could simplify how **alma-sbom** retrieves and formats data that is going to end up in SBOM records.

In addition to that, we only add the data that is specific to SPDX specification. At the time of writing this RFE, the current version of the SPDX specification is [v2.3](https://spdx.github.io/spdx-spec/v2.3/).

#### SPDX-specific fields

Apart from the fields that are shared between the CycloneDX and SPDX formats, SBOMs in SPDX format contain the
following fields that are unique to the SPDX format.

1. Data license
2. SPDX identifier field
3. Document name field
4. SPDX document namespace field

The data license field contains the name of the license under which the SBOM is published. The data license field
of AlmaLinux SPDX SBOMs will be set to `CC0-1.0`, Creative Commons CC0 1.0 Universal Public Domain Dedication.

The SPDX identifier field is hardcoded to the value `SPDXRef-DOCUMENT`.

The document name field will be set to the name and version of the package in the SBOM, separated with a hyphen.
If the SBOM contains multiple packages, the name will be set to the value of the name field in the build metadata
of the DB record.

The value of the SPDX document namespace field will be constructed from the string `https://security.almalinux.org/spdx/`, the value of the document name field, and a UUID, joined by hyphens.

Records in the database that cannot be mapped to fields in the SPDX format will be represented with SPDX Annotations. The name and value of the record that could not be mapped will be stored in the comment field
of the annotation in the form `name=value`, and the type of the annotation will be set to `OTHER`. If the record pertains to a package in the SBOM, the SPDX identifier reference field of the annotation will be set
to the SPDX identifier of that package.


#### SPDX SBOM record of a package

```javascript
{
    "SPDXID": "SPDXRef-DOCUMENT",
    "creationInfo": {
        "created": "2023-07-04T19:48:27Z",
        "creators": [
            "Organization: AlmaLinux OS Foundation (cloud-infra@almalinux.org)",
            "Tool: AlmaLinux Build System 0.1",
            "Tool: alma-sbom 0.0.1",
            "Tool: Community Attestation Service (CAS) 1.0.3",
            "Tool: spdx-tools 0.0"
        ]
    },
    "dataLicense": "CC0-1.0",
    "name": "bash-5.1.8-6.el9_1",
    "spdxVersion": "SPDX-2.3",
    "documentNamespace": "https://security.almalinux.org/spdx-bash-5.1.8-6.el9_1-da70a594-c9a5-4ecf-b1d8-a833d96eac71",
    "packages": [
        {
            "SPDXID": "SPDXRef-0",
            "annotations": [
                {
                    "annotationDate": "2023-07-04T19:48:27Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:epoch=None"
                },
                {
                    "annotationDate": "2023-07-04T19:48:27Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:version=5.1.8"
                },
                {
                    "annotationDate": "2023-07-04T19:48:27Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:release=6.el9_1"
                },
                {
                    "annotationDate": "2023-07-04T19:48:27Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:arch=x86_64"
                },
                {
                    "annotationDate": "2023-07-04T19:48:27Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:sourcerpm=bash-5.1.8-6.el9_1.src.rpm"
                },
                {
                    "annotationDate": "2023-07-04T19:48:27Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:buildhost=x64-builder02.almalinux.org"
                },
                {
                    "annotationDate": "2023-07-04T19:48:27Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:timestamp=2023-01-24T09:44:30.238513999Z"
                },
                {
                    "annotationDate": "2023-07-04T19:48:27Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:targetArch=x86_64"
                },
                {
                    "annotationDate": "2023-07-04T19:48:27Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:packageType=rpm"
                },
                {
                    "annotationDate": "2023-07-04T19:48:27Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:sbom:casHash=1bfcf5bf3187ff21db8109d48a0198b92341a9124f63db82cf501d1968ba1374"
                },
                {
                    "annotationDate": "2023-07-04T19:48:27Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:ID=5636"
                },
                {
                    "annotationDate": "2023-07-04T19:48:27Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:URL=https://build.almalinux.org/build/5636"
                },
                {
                    "annotationDate": "2023-07-04T19:48:27Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:author=eabdullin1 <55892454+eabdullin1@users.noreply.github.com>"
                },
                {
                    "annotationDate": "2023-07-04T19:48:27Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitURL=https://git.almalinux.org/rpms/bash.git"
                },
                {
                    "annotationDate": "2023-07-04T19:48:27Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:type=git"
                },
                {
                    "annotationDate": "2023-07-04T19:48:27Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitCommit=1a3ebc6398c31698863ba9b31a9f5effdb425c4f"
                },
                {
                    "annotationDate": "2023-07-04T19:48:27Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitRef=imports/c9/bash-5.1.8-6.el9_1"
                },
                {
                    "annotationDate": "2023-07-04T19:48:27Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitCommitCasHash=70c5a02df7074eada535aa35643f019574f7005ff345fd6f482eca797ae7c1d8"
                }
            ],
            "builtDate": "2023-01-24T09:44:30+00:00Z",
            "checksums": [
                {
                    "algorithm": "SHA256",
                    "checksumValue": "1bfcf5bf3187ff21db8109d48a0198b92341a9124f63db82cf501d1968ba1374"
                }
            ],
            "downloadLocation": "NONE",
            "externalRefs": [
                {
                    "referenceCategory": "SECURITY",
                    "referenceLocator": "cpe:2.3:a:almalinux:bash:5.1.8-6.el9_1:*:*:*:*:*:*:*",
                    "referenceType": "cpe23Type"
                },
                {
                    "referenceCategory": "PACKAGE_MANAGER",
                    "referenceLocator": "pkg:rpm/almalinux/bash@5.1.8-6.el9_1?arch=x86_64&upstream=bash-5.1.8-6.el9_1.src.rpm",
                    "referenceType": "purl"
                }
            ],
            "filesAnalyzed": false,
            "name": "bash",
            "supplier": "Organization: AlmaLinux OS Foundation (cloud-infra@almalinux.org)",
            "versionInfo": "5.1.8-6.el9_1"
        }
    ],
    "relationships": [
        {
            "spdxElementId": "SPDXRef-DOCUMENT",
            "relatedSpdxElement": "SPDXRef-0",
            "relationshipType": "DESCRIBES"
        }
    ]
}
```

#### SPDX SBOM record of a build

```javascript
{
    "SPDXID": "SPDXRef-DOCUMENT",
    "annotations": [
        {
            "annotationDate": "2023-07-04T19:42:47Z",
            "annotationType": "OTHER",
            "annotator": "Tool: alma-sbom 0.0.1",
            "comment": "almalinux:albs:build:ID=6854"
        },
        {
            "annotationDate": "2023-07-04T19:42:47Z",
            "annotationType": "OTHER",
            "annotator": "Tool: alma-sbom 0.0.1",
            "comment": "almalinux:albs:build:URL=https://build.almalinux.org/build/6854"
        },
        {
            "annotationDate": "2023-07-04T19:42:47Z",
            "annotationType": "OTHER",
            "annotator": "Tool: alma-sbom 0.0.1",
            "comment": "almalinux:albs:build:timestamp=2023-06-15T12:58:07.030330"
        }
    ],
    "creationInfo": {
        "created": "2023-07-04T19:42:47Z",
        "creators": [
            "Organization: AlmaLinux OS Foundation (cloud-infra@almalinux.org)",
            "Tool: AlmaLinux Build System 0.1",
            "Tool: alma-sbom 0.0.1",
            "Tool: Community Attestation Service (CAS) 1.0.3",
            "Tool: spdx-tools 0.0"
        ]
    },
    "dataLicense": "CC0-1.0",
    "name": "build-6854",
    "spdxVersion": "SPDX-2.3",
    "documentNamespace": "https://security.almalinux.org/spdx-build-6854-b2b256c5-c483-4228-9820-11d943cb9919",
    "packages": [
        {
            "SPDXID": "SPDXRef-0",
            "annotations": [
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:epoch=None"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:version=8.7"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:release=1.el8"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:arch=noarch"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:sourcerpm=None"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:buildhost=x64-builder02.almalinux.org"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:targetArch=i686"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:packageType=rpm"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:sbom:casHash=46e24404ce51c409d2d3908c74155208a25c5fff13a7732da79b7990ad848ebf"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:ID=6854"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:URL=https://build.almalinux.org/build/6854"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:author=andrewlukoshko <andrew.lukoshko@gmail.com>"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitURL=https://git.almalinux.org/rpms/lorax-templates-almalinux.git"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:type=git"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitCommit=a707ac0b22f76710ff0599878fbea6b19369f2bd"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitRef=8.7-1"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitCommitCasHash=b0a1febf5f38c62090c056f8e11a5a05274e94018a4225ecff309b0df4fcafd4"
                }
            ],
            "builtDate": "2023-06-15T12:58:07Z",
            "checksums": [
                {
                    "algorithm": "SHA256",
                    "checksumValue": "46e24404ce51c409d2d3908c74155208a25c5fff13a7732da79b7990ad848ebf"
                }
            ],
            "downloadLocation": "NONE",
            "externalRefs": [
                {
                    "referenceCategory": "SECURITY",
                    "referenceLocator": "cpe:2.3:a:almalinux:lorax-templates-almalinux:8.7-1.el8:*:*:*:*:*:*:*",
                    "referenceType": "cpe23Type"
                },
                {
                    "referenceCategory": "PACKAGE_MANAGER",
                    "referenceLocator": "pkg:rpm/almalinux/lorax-templates-almalinux@8.7-1.el8?arch=noarch",
                    "referenceType": "purl"
                }
            ],
            "filesAnalyzed": false,
            "name": "lorax-templates-almalinux",
            "supplier": "Organization: AlmaLinux OS Foundation (cloud-infra@almalinux.org)",
            "versionInfo": "8.7"
        },
        {
            "SPDXID": "SPDXRef-1",
            "annotations": [
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:epoch=None"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:version=8.7"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:release=1.el8"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:arch=noarch"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:sourcerpm=lorax-templates-almalinux-8.7-1.el8.src.rpm"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:buildhost=s390x-builder03"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:targetArch=s390x"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:packageType=rpm"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:sbom:casHash=b94c08b7d0e4ca090f0d636b6efb53228159b629d519b7051556421bf272c439"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:ID=6854"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:URL=https://build.almalinux.org/build/6854"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:author=andrewlukoshko <andrew.lukoshko@gmail.com>"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitURL=https://git.almalinux.org/rpms/lorax-templates-almalinux.git"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:type=git"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitCommit=a707ac0b22f76710ff0599878fbea6b19369f2bd"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitRef=8.7-1"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitCommitCasHash=b0a1febf5f38c62090c056f8e11a5a05274e94018a4225ecff309b0df4fcafd4"
                }
            ],
            "builtDate": "2023-06-15T12:58:07Z",
            "checksums": [
                {
                    "algorithm": "SHA256",
                    "checksumValue": "b94c08b7d0e4ca090f0d636b6efb53228159b629d519b7051556421bf272c439"
                }
            ],
            "downloadLocation": "NONE",
            "externalRefs": [
                {
                    "referenceCategory": "SECURITY",
                    "referenceLocator": "cpe:2.3:a:almalinux:lorax-templates-almalinux:8.7-1.el8:*:*:*:*:*:*:*",
                    "referenceType": "cpe23Type"
                },
                {
                    "referenceCategory": "PACKAGE_MANAGER",
                    "referenceLocator": "pkg:rpm/almalinux/lorax-templates-almalinux@8.7-1.el8?arch=noarch&upstream=lorax-templates-almalinux-8.7-1.el8.src.rpm",
                    "referenceType": "purl"
                }
            ],
            "filesAnalyzed": false,
            "name": "lorax-templates-almalinux",
            "supplier": "Organization: AlmaLinux OS Foundation (cloud-infra@almalinux.org)",
            "versionInfo": "8.7"
        },
        {
            "SPDXID": "SPDXRef-2",
            "annotations": [
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:epoch=None"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:version=8.7"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:release=1.el8"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:arch=noarch"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:sourcerpm=None"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:buildhost=x64-builder02.almalinux.org"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:targetArch=i686"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:packageType=rpm"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:sbom:casHash=e3c6bf2e91c88e3207b2676f6a6fb63147183d0329c9bb1914e09fba2bd64ca8"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:ID=6854"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:URL=https://build.almalinux.org/build/6854"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:author=andrewlukoshko <andrew.lukoshko@gmail.com>"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitURL=https://git.almalinux.org/rpms/lorax-templates-almalinux.git"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:type=git"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitCommit=a707ac0b22f76710ff0599878fbea6b19369f2bd"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitRef=8.7-1"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitCommitCasHash=b0a1febf5f38c62090c056f8e11a5a05274e94018a4225ecff309b0df4fcafd4"
                }
            ],
            "builtDate": "2023-06-15T12:58:07Z",
            "checksums": [
                {
                    "algorithm": "SHA256",
                    "checksumValue": "e3c6bf2e91c88e3207b2676f6a6fb63147183d0329c9bb1914e09fba2bd64ca8"
                }
            ],
            "downloadLocation": "NONE",
            "externalRefs": [
                {
                    "referenceCategory": "SECURITY",
                    "referenceLocator": "cpe:2.3:a:almalinux:lorax-templates-almalinux:8.7-1.el8:*:*:*:*:*:*:*",
                    "referenceType": "cpe23Type"
                },
                {
                    "referenceCategory": "PACKAGE_MANAGER",
                    "referenceLocator": "pkg:rpm/almalinux/lorax-templates-almalinux@8.7-1.el8?arch=noarch",
                    "referenceType": "purl"
                }
            ],
            "filesAnalyzed": false,
            "name": "lorax-templates-almalinux",
            "supplier": "Organization: AlmaLinux OS Foundation (cloud-infra@almalinux.org)",
            "versionInfo": "8.7"
        },
        {
            "SPDXID": "SPDXRef-3",
            "annotations": [
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:epoch=None"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:version=8.7"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:release=1.el8"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:arch=noarch"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:sourcerpm=lorax-templates-almalinux-8.7-1.el8.src.rpm"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:buildhost=s390x-builder03"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:targetArch=s390x"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:packageType=rpm"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:sbom:casHash=b94c08b7d0e4ca090f0d636b6efb53228159b629d519b7051556421bf272c439"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:ID=6854"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:URL=https://build.almalinux.org/build/6854"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:author=andrewlukoshko <andrew.lukoshko@gmail.com>"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitURL=https://git.almalinux.org/rpms/lorax-templates-almalinux.git"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:type=git"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitCommit=a707ac0b22f76710ff0599878fbea6b19369f2bd"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitRef=8.7-1"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitCommitCasHash=b0a1febf5f38c62090c056f8e11a5a05274e94018a4225ecff309b0df4fcafd4"
                }
            ],
            "builtDate": "2023-06-15T12:58:07Z",
            "checksums": [
                {
                    "algorithm": "SHA256",
                    "checksumValue": "b94c08b7d0e4ca090f0d636b6efb53228159b629d519b7051556421bf272c439"
                }
            ],
            "downloadLocation": "NONE",
            "externalRefs": [
                {
                    "referenceCategory": "SECURITY",
                    "referenceLocator": "cpe:2.3:a:almalinux:lorax-templates-almalinux:8.7-1.el8:*:*:*:*:*:*:*",
                    "referenceType": "cpe23Type"
                },
                {
                    "referenceCategory": "PACKAGE_MANAGER",
                    "referenceLocator": "pkg:rpm/almalinux/lorax-templates-almalinux@8.7-1.el8?arch=noarch&upstream=lorax-templates-almalinux-8.7-1.el8.src.rpm",
                    "referenceType": "purl"
                }
            ],
            "filesAnalyzed": false,
            "name": "lorax-templates-almalinux",
            "supplier": "Organization: AlmaLinux OS Foundation (cloud-infra@almalinux.org)",
            "versionInfo": "8.7"
        },
        {
            "SPDXID": "SPDXRef-4",
            "annotations": [
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:epoch=None"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:version=8.7"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:release=1.el8"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:arch=noarch"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:sourcerpm=None"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:buildhost=x64-builder02.almalinux.org"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:targetArch=i686"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:packageType=rpm"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:sbom:casHash=46e24404ce51c409d2d3908c74155208a25c5fff13a7732da79b7990ad848ebf"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:ID=6854"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:URL=https://build.almalinux.org/build/6854"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:author=andrewlukoshko <andrew.lukoshko@gmail.com>"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitURL=https://git.almalinux.org/rpms/lorax-templates-almalinux.git"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:type=git"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitCommit=a707ac0b22f76710ff0599878fbea6b19369f2bd"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitRef=8.7-1"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitCommitCasHash=b0a1febf5f38c62090c056f8e11a5a05274e94018a4225ecff309b0df4fcafd4"
                }
            ],
            "builtDate": "2023-06-15T12:58:07Z",
            "checksums": [
                {
                    "algorithm": "SHA256",
                    "checksumValue": "46e24404ce51c409d2d3908c74155208a25c5fff13a7732da79b7990ad848ebf"
                }
            ],
            "downloadLocation": "NONE",
            "externalRefs": [
                {
                    "referenceCategory": "SECURITY",
                    "referenceLocator": "cpe:2.3:a:almalinux:lorax-templates-almalinux:8.7-1.el8:*:*:*:*:*:*:*",
                    "referenceType": "cpe23Type"
                },
                {
                    "referenceCategory": "PACKAGE_MANAGER",
                    "referenceLocator": "pkg:rpm/almalinux/lorax-templates-almalinux@8.7-1.el8?arch=noarch",
                    "referenceType": "purl"
                }
            ],
            "filesAnalyzed": false,
            "name": "lorax-templates-almalinux",
            "supplier": "Organization: AlmaLinux OS Foundation (cloud-infra@almalinux.org)",
            "versionInfo": "8.7"
        },
        {
            "SPDXID": "SPDXRef-5",
            "annotations": [
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:epoch=None"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:version=8.7"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:release=1.el8"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:arch=noarch"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:sourcerpm=lorax-templates-almalinux-8.7-1.el8.src.rpm"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:buildhost=s390x-builder03"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:targetArch=s390x"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:packageType=rpm"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:sbom:casHash=b94c08b7d0e4ca090f0d636b6efb53228159b629d519b7051556421bf272c439"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:ID=6854"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:URL=https://build.almalinux.org/build/6854"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:author=andrewlukoshko <andrew.lukoshko@gmail.com>"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitURL=https://git.almalinux.org/rpms/lorax-templates-almalinux.git"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:type=git"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitCommit=a707ac0b22f76710ff0599878fbea6b19369f2bd"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitRef=8.7-1"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitCommitCasHash=b0a1febf5f38c62090c056f8e11a5a05274e94018a4225ecff309b0df4fcafd4"
                }
            ],
            "builtDate": "2023-06-15T12:58:07Z",
            "checksums": [
                {
                    "algorithm": "SHA256",
                    "checksumValue": "b94c08b7d0e4ca090f0d636b6efb53228159b629d519b7051556421bf272c439"
                }
            ],
            "downloadLocation": "NONE",
            "externalRefs": [
                {
                    "referenceCategory": "SECURITY",
                    "referenceLocator": "cpe:2.3:a:almalinux:lorax-templates-almalinux:8.7-1.el8:*:*:*:*:*:*:*",
                    "referenceType": "cpe23Type"
                },
                {
                    "referenceCategory": "PACKAGE_MANAGER",
                    "referenceLocator": "pkg:rpm/almalinux/lorax-templates-almalinux@8.7-1.el8?arch=noarch&upstream=lorax-templates-almalinux-8.7-1.el8.src.rpm",
                    "referenceType": "purl"
                }
            ],
            "filesAnalyzed": false,
            "name": "lorax-templates-almalinux",
            "supplier": "Organization: AlmaLinux OS Foundation (cloud-infra@almalinux.org)",
            "versionInfo": "8.7"
        },
        {
            "SPDXID": "SPDXRef-6",
            "annotations": [
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:epoch=None"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:version=8.7"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:release=1.el8"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:arch=noarch"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:sourcerpm=None"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:buildhost=x64-builder02.almalinux.org"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:targetArch=i686"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:packageType=rpm"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:sbom:casHash=46e24404ce51c409d2d3908c74155208a25c5fff13a7732da79b7990ad848ebf"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:ID=6854"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:URL=https://build.almalinux.org/build/6854"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:author=andrewlukoshko <andrew.lukoshko@gmail.com>"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitURL=https://git.almalinux.org/rpms/lorax-templates-almalinux.git"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:type=git"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitCommit=a707ac0b22f76710ff0599878fbea6b19369f2bd"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitRef=8.7-1"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitCommitCasHash=b0a1febf5f38c62090c056f8e11a5a05274e94018a4225ecff309b0df4fcafd4"
                }
            ],
            "builtDate": "2023-06-15T12:58:07Z",
            "checksums": [
                {
                    "algorithm": "SHA256",
                    "checksumValue": "46e24404ce51c409d2d3908c74155208a25c5fff13a7732da79b7990ad848ebf"
                }
            ],
            "downloadLocation": "NONE",
            "externalRefs": [
                {
                    "referenceCategory": "SECURITY",
                    "referenceLocator": "cpe:2.3:a:almalinux:lorax-templates-almalinux:8.7-1.el8:*:*:*:*:*:*:*",
                    "referenceType": "cpe23Type"
                },
                {
                    "referenceCategory": "PACKAGE_MANAGER",
                    "referenceLocator": "pkg:rpm/almalinux/lorax-templates-almalinux@8.7-1.el8?arch=noarch",
                    "referenceType": "purl"
                }
            ],
            "filesAnalyzed": false,
            "name": "lorax-templates-almalinux",
            "supplier": "Organization: AlmaLinux OS Foundation (cloud-infra@almalinux.org)",
            "versionInfo": "8.7"
        },
        {
            "SPDXID": "SPDXRef-7",
            "annotations": [
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:epoch=None"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:version=8.7"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:release=1.el8"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:arch=noarch"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:sourcerpm=lorax-templates-almalinux-8.7-1.el8.src.rpm"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:buildhost=s390x-builder03"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:targetArch=s390x"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:packageType=rpm"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:sbom:casHash=b94c08b7d0e4ca090f0d636b6efb53228159b629d519b7051556421bf272c439"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:ID=6854"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:URL=https://build.almalinux.org/build/6854"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:author=andrewlukoshko <andrew.lukoshko@gmail.com>"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitURL=https://git.almalinux.org/rpms/lorax-templates-almalinux.git"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:type=git"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitCommit=a707ac0b22f76710ff0599878fbea6b19369f2bd"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitRef=8.7-1"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitCommitCasHash=b0a1febf5f38c62090c056f8e11a5a05274e94018a4225ecff309b0df4fcafd4"
                }
            ],
            "builtDate": "2023-06-15T12:58:07Z",
            "checksums": [
                {
                    "algorithm": "SHA256",
                    "checksumValue": "b94c08b7d0e4ca090f0d636b6efb53228159b629d519b7051556421bf272c439"
                }
            ],
            "downloadLocation": "NONE",
            "externalRefs": [
                {
                    "referenceCategory": "SECURITY",
                    "referenceLocator": "cpe:2.3:a:almalinux:lorax-templates-almalinux:8.7-1.el8:*:*:*:*:*:*:*",
                    "referenceType": "cpe23Type"
                },
                {
                    "referenceCategory": "PACKAGE_MANAGER",
                    "referenceLocator": "pkg:rpm/almalinux/lorax-templates-almalinux@8.7-1.el8?arch=noarch&upstream=lorax-templates-almalinux-8.7-1.el8.src.rpm",
                    "referenceType": "purl"
                }
            ],
            "filesAnalyzed": false,
            "name": "lorax-templates-almalinux",
            "supplier": "Organization: AlmaLinux OS Foundation (cloud-infra@almalinux.org)",
            "versionInfo": "8.7"
        },
        {
            "SPDXID": "SPDXRef-8",
            "annotations": [
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:epoch=None"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:version=8.7"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:release=1.el8"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:arch=noarch"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:sourcerpm=None"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:buildhost=x64-builder02.almalinux.org"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:targetArch=i686"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:packageType=rpm"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:sbom:casHash=46e24404ce51c409d2d3908c74155208a25c5fff13a7732da79b7990ad848ebf"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:ID=6854"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:URL=https://build.almalinux.org/build/6854"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:author=andrewlukoshko <andrew.lukoshko@gmail.com>"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitURL=https://git.almalinux.org/rpms/lorax-templates-almalinux.git"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:type=git"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitCommit=a707ac0b22f76710ff0599878fbea6b19369f2bd"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitRef=8.7-1"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitCommitCasHash=b0a1febf5f38c62090c056f8e11a5a05274e94018a4225ecff309b0df4fcafd4"
                }
            ],
            "builtDate": "2023-06-15T12:58:07Z",
            "checksums": [
                {
                    "algorithm": "SHA256",
                    "checksumValue": "46e24404ce51c409d2d3908c74155208a25c5fff13a7732da79b7990ad848ebf"
                }
            ],
            "downloadLocation": "NONE",
            "externalRefs": [
                {
                    "referenceCategory": "SECURITY",
                    "referenceLocator": "cpe:2.3:a:almalinux:lorax-templates-almalinux:8.7-1.el8:*:*:*:*:*:*:*",
                    "referenceType": "cpe23Type"
                },
                {
                    "referenceCategory": "PACKAGE_MANAGER",
                    "referenceLocator": "pkg:rpm/almalinux/lorax-templates-almalinux@8.7-1.el8?arch=noarch",
                    "referenceType": "purl"
                }
            ],
            "filesAnalyzed": false,
            "name": "lorax-templates-almalinux",
            "supplier": "Organization: AlmaLinux OS Foundation (cloud-infra@almalinux.org)",
            "versionInfo": "8.7"
        },
        {
            "SPDXID": "SPDXRef-9",
            "annotations": [
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:epoch=None"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:version=8.7"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:release=1.el8"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:arch=noarch"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:sourcerpm=lorax-templates-almalinux-8.7-1.el8.src.rpm"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:buildhost=s390x-builder03"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:targetArch=s390x"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:packageType=rpm"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:sbom:casHash=b94c08b7d0e4ca090f0d636b6efb53228159b629d519b7051556421bf272c439"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:ID=6854"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:URL=https://build.almalinux.org/build/6854"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:author=andrewlukoshko <andrew.lukoshko@gmail.com>"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitURL=https://git.almalinux.org/rpms/lorax-templates-almalinux.git"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:type=git"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitCommit=a707ac0b22f76710ff0599878fbea6b19369f2bd"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitRef=8.7-1"
                },
                {
                    "annotationDate": "2023-07-04T19:42:47Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitCommitCasHash=b0a1febf5f38c62090c056f8e11a5a05274e94018a4225ecff309b0df4fcafd4"
                }
            ],
            "builtDate": "2023-06-15T12:58:07Z",
            "checksums": [
                {
                    "algorithm": "SHA256",
                    "checksumValue": "b94c08b7d0e4ca090f0d636b6efb53228159b629d519b7051556421bf272c439"
                }
            ],
            "downloadLocation": "NONE",
            "externalRefs": [
                {
                    "referenceCategory": "SECURITY",
                    "referenceLocator": "cpe:2.3:a:almalinux:lorax-templates-almalinux:8.7-1.el8:*:*:*:*:*:*:*",
                    "referenceType": "cpe23Type"
                },
                {
                    "referenceCategory": "PACKAGE_MANAGER",
                    "referenceLocator": "pkg:rpm/almalinux/lorax-templates-almalinux@8.7-1.el8?arch=noarch&upstream=lorax-templates-almalinux-8.7-1.el8.src.rpm",
                    "referenceType": "purl"
                }
            ],
            "filesAnalyzed": false,
            "name": "lorax-templates-almalinux",
            "supplier": "Organization: AlmaLinux OS Foundation (cloud-infra@almalinux.org)",
            "versionInfo": "8.7"
        }
    ],
    "relationships": [
        {
            "spdxElementId": "SPDXRef-DOCUMENT",
            "relatedSpdxElement": "SPDXRef-0",
            "relationshipType": "DESCRIBES"
        },
        {
            "spdxElementId": "SPDXRef-DOCUMENT",
            "relatedSpdxElement": "SPDXRef-1",
            "relationshipType": "DESCRIBES"
        },
        {
            "spdxElementId": "SPDXRef-DOCUMENT",
            "relatedSpdxElement": "SPDXRef-2",
            "relationshipType": "DESCRIBES"
        },
        {
            "spdxElementId": "SPDXRef-DOCUMENT",
            "relatedSpdxElement": "SPDXRef-3",
            "relationshipType": "DESCRIBES"
        },
        {
            "spdxElementId": "SPDXRef-DOCUMENT",
            "relatedSpdxElement": "SPDXRef-4",
            "relationshipType": "DESCRIBES"
        },
        {
            "spdxElementId": "SPDXRef-DOCUMENT",
            "relatedSpdxElement": "SPDXRef-5",
            "relationshipType": "DESCRIBES"
        },
        {
            "spdxElementId": "SPDXRef-DOCUMENT",
            "relatedSpdxElement": "SPDXRef-6",
            "relationshipType": "DESCRIBES"
        },
        {
            "spdxElementId": "SPDXRef-DOCUMENT",
            "relatedSpdxElement": "SPDXRef-7",
            "relationshipType": "DESCRIBES"
        },
        {
            "spdxElementId": "SPDXRef-DOCUMENT",
            "relatedSpdxElement": "SPDXRef-8",
            "relationshipType": "DESCRIBES"
        },
        {
            "spdxElementId": "SPDXRef-DOCUMENT",
            "relatedSpdxElement": "SPDXRef-9",
            "relationshipType": "DESCRIBES"
        }
    ]
}
```

## Authors

* [Matthias Kruk](mailto:matthias@almalinux.org)
* [Javier Hernández](mailto:javi@almalinux.org)
