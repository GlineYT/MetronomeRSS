# METRONOME RSS DOCUMENTATION
## ERROR CODES
Metronome RSS may emit various error codes depending on issues found at a given step processing a given input
Those can be from the Loading, Validating, Parsing or Rendering steps, aswell as from any other processes MetronomeRSS does

## Severity types and information codes
### Error codes can be seperated by severety as such

- FTL_ - Fatal, stops execution 
- ERR_ - Error, the operation has encountered a error, must be handled
- WRN_ - Warning, the operation has finished, but with unintended data. May or may not cause problems later
- INF_ - Information, the operation has finished sucessfully, or needs to report information. 



## Fatal Error Codes

| Code | Description |
|------|-------------|
| `FTL_GNR_CRS` | Fatal generic crash. The program, dependent systems or environment has crashed. |

---

## Error Codes (ERR_)

### Loading Errors

| Code | Description |
|------|-------------|
| `ERR_NO_FILE` | File does not exist. Usually issued during loading of a feed, resource, file, etc. Format-agnostic  |
| `ERR_INV_XML` | The XML file is invalid.|
| `ERR_LD_FILE` | Generic error relating to file loading. |

### Validation Errors - Feed Type Detection

| Code | Description |
|------|-------------|
| `ERR_NO_RSS` | No root element found in the XML document. The file may be empty or malformed. |
| `ERR_UNK_FEED` | Unknown feed format. The root element is neither RSS nor Atom. |
| `ERR_UNK_RSS` | Unknown RSS version. The RSS version attribute is not recognized (e.g., "3.0"). |
| `ERR_UNK_ATM` | Unknown Atom feed. The Atom namespace is not recognized. |

### Validation Errors - Required Fields (RSS)

| Code | Description |
|------|-------------|
| `ERR_NO_CNL` | Missing `<channel>` element. RSS feed must contain a channel. |
| `ERR_NO_TTL` | Missing `<title>` element. Required in both RSS and Atom feeds. |
| `ERR_NO_DSC` | Missing `<description>` element. Required in RSS channel. |
| `ERR_NO_LNK` | Missing `<link>` element. Required in both RSS and Atom feeds. |
| `ERR_NO_RDF` | Missing or incorrect RDF namespace. Required for RSS 1.0 feeds. |

### Validation Errors - Required Fields (Atom)

| Code | Description |
|------|-------------|
| `ERR_NO_IDN` | Missing `<id>` element. Required in Atom feeds for unique identification. |
| `ERR_NO_UPD` | Missing `<updated>` element. Required in Atom feeds for timestamp tracking. |

### Unknown/Uncategorized Errors

| Code | Description |
|------|-------------|
| `ERR_UNK_ERR` | Unknown or uncategorized error. Used as a fallback when no specific error code applies. |

---

## Warning Codes (WRN_)

| Code | Description |
|------|-------------|
| `WRN_NO_LNG` | Missing `<language>` element. RSS 0.91 recommends but does not strictly require language. The user may manually set this in settings. |

---

## Information Codes (INF_)

| Code | Description |
|------|-------------|
| `INF_ALL_OK` | All operations completed successfully. The operation finished in a successful state |

---

## Error Code Quick Reference

| Severity | Codes |
|----------|-------|
| **FTL_** | `FTL_GNR_CRS` |
| **ERR_** | `ERR_NO_FILE`, `ERR_NO_RSS`, `ERR_UNK_FEED`, `ERR_UNK_RSS`, `ERR_UNK_ATM`, `ERR_NO_CNL`, `ERR_NO_TTL`, `ERR_NO_DSC`, `ERR_NO_LNK`, `ERR_NO_RDF`, `ERR_NO_IDN`, `ERR_NO_UPD`, `ERR_UNK_ERR`,`ERR_INV_XML`, `ERR_LD_FILE` |
| **WRN_** | `WRN_NO_LNG` |
| **INF_** | `INF_ALL_OK` |

---

## Usage Notes

- Error codes are returned as strings from functions
- The UI layer should resolve error codes to user-friendly messages
- Fatal errors (FTL_) should cause immediate program termination
- Errors (ERR_) should be handled and reported to the user
- Warnings (WRN_) should be logged but do not prevent operation
- Information (INF_) indicates successful completion
