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

Generating SPDX SBOMs into different formats is currently provided by [spdx-tools](https://pypi.org/project/spdx-tools/), which alma-sbom will depend on.

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
    "SPDXID": "SPDXRef-424bb7a2-e4d7-472b-8260-23ec0feb7f07",
    "creationInfo": {
        "created": "2023-06-19T10:49:04.839885Z",
        "creators": [
            "Organization: AlmaLinux OS Foundation (cloud-infra@almalinux.org)",
            "Tool: AlmaLinux Build System 0.1",
            "Tool: alma-sbom 0.0.1",
            "Tool: spdx-tools 0.0",
            "Tool: Community Attestation Service (CAS) 1.0.3"
        ]
    },
    "dataLicense": "CC0-1.0",
    "name": "bash-5.1.8-6.el9_1",
    "spdxVersion": "SPDX-2.3",
    "documentNamespace": "https://almalinux.org/spdx",
    "packages": [
        {
            "SPDXID": "SPDXRef-0",
            "annotations": [
                {
                    "annotationDate": "2023-06-19T10:49:04.840258Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:epoch=None"
                },
                {
                    "annotationDate": "2023-06-19T10:49:04.840313Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:version=5.1.8"
                },
                {
                    "annotationDate": "2023-06-19T10:49:04.840358Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:release=6.el9_1"
                },
                {
                    "annotationDate": "2023-06-19T10:49:04.840390Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:arch=x86_64"
                },
                {
                    "annotationDate": "2023-06-19T10:49:04.840430Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:sourcerpm=bash-5.1.8-6.el9_1.src.rpm"
                },
                {
                    "annotationDate": "2023-06-19T10:49:04.840469Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:buildhost=x64-builder02.almalinux.org"
                },
                {
                    "annotationDate": "2023-06-19T10:49:04.840509Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:package:timestamp=2023-01-24T09:44:30.238513999Z"
                },
                {
                    "annotationDate": "2023-06-19T10:49:04.840551Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:targetArch=x86_64"
                },
                {
                    "annotationDate": "2023-06-19T10:49:04.840592Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:packageType=rpm"
                },
                {
                    "annotationDate": "2023-06-19T10:49:04.840630Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:sbom:casHash=1bfcf5bf3187ff21db8109d48a0198b92341a9124f63db82cf501d1968ba1374"
                },
                {
                    "annotationDate": "2023-06-19T10:49:04.840659Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:ID=5636"
                },
                {
                    "annotationDate": "2023-06-19T10:49:04.840687Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:URL=https://build.almalinux.org/build/5636"
                },
                {
                    "annotationDate": "2023-06-19T10:49:04.840715Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:author=eabdullin1 <55892454+eabdullin1@users.noreply.github.com>"
                },
                {
                    "annotationDate": "2023-06-19T10:49:04.840743Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitURL=https://git.almalinux.org/rpms/bash.git"
                },
                {
                    "annotationDate": "2023-06-19T10:49:04.840770Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:type=git"
                },
                {
                    "annotationDate": "2023-06-19T10:49:04.840798Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitCommit=1a3ebc6398c31698863ba9b31a9f5effdb425c4f"
                },
                {
                    "annotationDate": "2023-06-19T10:49:04.840826Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitRef=imports/c9/bash-5.1.8-6.el9_1"
                },
                {
                    "annotationDate": "2023-06-19T10:49:04.840865Z",
                    "annotationType": "OTHER",
                    "annotator": "Tool: alma-sbom 0.0.1",
                    "comment": "almalinux:albs:build:source:gitCommitCasHash=70c5a02df7074eada535aa35643f019574f7005ff345fd6f482eca797ae7c1d8"
                }
            ],
            "builtDate": "2023-01-24T09:44:30.238513+00:00Z",
            "checksums": [
                {
                    "algorithm": "SHA256",
                    "checksumValue": "1bfcf5bf3187ff21db8109d48a0198b92341a9124f63db82cf501d1968ba1374"
                }
            ],
            "downloadLocation": "pkg:rpm/almalinux/bash@5.1.8-6.el9_1?arch=x86_64&upstream=bash-5.1.8-6.el9_1.src.rpm",
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
    ]
}
```

#### SPDX SBOM record of a build

**TBD**

## Authors

* [Matthias Kruk](mailto:matthias@almalinux.org)
* [Javier Hernández](mailto:javi@almalinux.org)
