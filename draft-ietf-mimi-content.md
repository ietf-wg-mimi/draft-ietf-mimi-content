%%%
title = "More Instant Messaging Interoperability (MIMI) message content"
abbrev = "MIMI Content"
ipr= "trust200902"
area = "art"
workgroup = "MIMI"
keyword = ["mimi","content","mls","mime"]

[seriesInfo]
status = "informational"
name = "Internet-Draft"
value = "draft-ietf-mimi-content-00"
stream = "IETF"

[[author]]
initials="R."
surname="Mahy"
fullname="Rohan Mahy"
organization = "Wire"
  [author.address]
  email = "rohan.mahy@wire.com"
%%%

.# Abstract

This document describes content semantics common in Instant Messaging (IM)
systems and describes a profile suitable for instant messaging
interoperability of messages end-to-end encrypted inside the MLS 
(Message Layer Security) Protocol.

{mainmatter}

# Terminology
The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in BCP 14 [@!RFC2119] [@!RFC8174] when,
and only when, they appear in all capitals, as shown here.

The terms MLS client, MLS group, and KeyPackage have the same meanings as in
the MLS protocol [@!I-D.ietf-mls-protocol].

# Introduction

RFC EDITOR: PLEASE REMOVE THE FOLLOWING PARAGRAPH. The source for
this draft is maintained in GitHub. Suggested changes should be
submitted as pull requests at https://github.com/ietf-wg-mimi/draft-ietf-mimi-content.
Editorial changes can be managed in GitHub, but any substantive 
change should be discussed on the MIMI mailing list (mimi@ietf.org).

MLS [@!I-D.ietf-mls-protocol] is a group key establishment protocol
motivated by the desire for group chat with efficient end-to-end encryption.
While one of the motivations of MLS is interoperable standards-based secure
messaging, the MLS protocol does not define or prescribe any format for the
encrypted "application messages" encoded by MLS.  The development of MLS
was strongly motivated by the needs of a number of Instant Messaging (IM)
systems, which encrypt messages end-to-end using variations of the
Double Ratchet protocol [@?DoubleRatchet].

End-to-end encrypted instant messaging was also a motivator for the Common
Protocol for Instant Messaging (CPIM) [@?RFC3862], however the model used at the time
assumed standalone encryption of each message using a protocol such as S/MIME
[@?RFC8551] or PGP [@?RFC3156] to interoperate between IM protocols such as
SIP [@?RFC3261] and XMPP [@?RFC6120].  For a variety of practical reasons, interoperable
end-to-end encryption between IM systems was never deployed commercially.

There are now several instant messaging vendors implementing MLS, and the
MIMI (More Instant Messaging Interoperability) Working Group is chartered
to standardize an extensible interoperable messaging format for common
features to be conveyed "inside" MLS application messages.
Most of these features can reuse the semantics of
previously-defined URIs, message headers, and media types.
This document represents a solution to one part of the
MIMI problem outline [@!I-D.mahy-mimi-problem-outline].

This document assumes that MLS clients advertise media types they support
and can determine what media types are required to join a
specific MLS group using the content advertisement extensions in Section 2.3 of
[@!I-D.ietf-mls-extensions]. It allows implementations to define MLS groups
with different media type requirements and allows MLS clients to send
extended or proprietary messages that would be interpreted by some members
of the group while assuring that an interoperable end-to-end encrypted
baseline is available to all members, even when the group spans multiple
systems or vendors.

Below is a list of some features commonly found in IM group chat systems:

* plain text and rich text messaging
* mentions
* replies
* reactions
* edit or delete previously sent messages
* expiring messages
* delivery notifications
* read receipts
* shared files/audio/videos
* calling / conferencing
* message threading

# Overview

## Naming schemes

IM systems have a number of types of identifiers. These are described in detail
in [@?I-D.mahy-mimi-identity]. A few of these used in this document are:

* handle identifier (external, friendly representation). This is the type 
of identifier described later as the senderUserUrl in the examples, which
is analogous to the From header in email.
* client/device identifier (internal representation). This is the type
of identifier described as the senderClientUrl in the examples.
* group or room or conversation or channel name (either internal or external representation).
This is the type of identifier described as the MLS group URL in the examples.

This proposal relies on URIs for naming and identifiers. All the example use
the `im:` URI scheme (defined in [@!RFC3862]), but any instant messaging scheme
could be used.

## Message Container

Most common instant messaging features are expressed as individual messages.
A plain or rich text message is obviously a message, but a reaction (ex: like),
a reply, editing a previous message, deleting an earlier message, and read
receipts are all typically modeled as another message with different properties. 

This document describes the semantics of a message container, which contains a
message ID and timestamp and represents most of these previously mentioned messages.
The container typically carries one or more body parts with the actual message
content (for example, an emoji used in a reaction, a plain text or rich text
message or reply, a link, or an inline image).

## Message Status Report

This document also describes the semantics of a status report of other messages.
The status report has a timestamp, but does not have a message ID of its own.
Because some messaging systems deliver messages in batches and allow a user to
mark several messages read at a time, the report format allows a single report
to convey the read/delivered status of multiple messages (by message ID) within
the same MLS group at a time.

# MIMI Content Container Message Semantics

Each MIMI Content message is a container format with three categories
of information: 

* the required message ID and timestamp fields, 
* the message behavior fields (which can have default or empty values), and
* the body part(s) and associated parameters

To focus on the semantics of a MIMI Content message, we use C/C++ struct
notation to describe its data fields. These fields are numbered in
curly braces for reference in the text. We do not propose any specific syntax
for the format, but two reasonable constraints are:

* we do not want to scan body parts to check for boundary marker
collisions. This rules out using multipart MIME types.
* we do not want to base64 encode body parts with binary media
types (ex: images). This rules out using JSON to carry the binary data.

## Required Fields

Every MIMI content message has a message ID {1}. The message ID
has a local part and a domain part. The domain part corresponds to the
domain of the sender of the message. The local part must be unique
among all messages sent in the domain. Using a UUID for the local part
is RECOMMENDED.

``` c++
struct MessageId {
    Octets localPart;
    String domain;
};

struct MimiContent {
    MessageId messageId;     // required value {1}
    uint64 timestamp;        // milliseconds since 01-Jan-1970 {2}
    MessageId replaces;      // {3}
    Octets topicId;          // {4}
    uint32 expires;          // 0 = does not expire {5}
    ReplyToInfo inReplyTo;   // {6}
    NestablePart body;       // {7}
};
```

Every MIMI content message has a timestamp {2} when the message was
encrypted. It is represented as
the whole number of milliseconds since the start of the UNIX epoch
(01-Jan-1970 00:00:00 UTC).

## Message Behavior Fields 

The `replaces` {3} data field indicates that the current message
is a replacement or update to a previous message whose message ID
is in the `replaces` data field. It is used to edit previously-sent
messages, delete previously-sent messages, and adjust reactions to
messages to which the client previously reacted.
 If the `replaces` field is empty (i.e. both the message ID
`localPart` and the `domain` are zero length), the receiver
assumes that the current message has not identified any special
relationship with another previous message. 

The `topicId` {4} data field indicates that the current message is
part of a logical grouping of messages which all share the same
value in the `topicId` data field. If the `topicId` is zero length,
there is no such grouping.

The `expires` {5} data field is a hint from the sender to the receiver
that the message should be locally deleted and disregarded at a specific
timestamp in the future. Indicate a message with no specific expiration
time with the value zero. The data field is an unsigned integer number of
seconds after the start of the UNIX epoch. Using an 32-bit unsigned
integer allows expiration dates until the year 2106. Note that
specifying an expiration time provides no assurance that the client
actually honors or can honor the expiration time, nor that the end user
didn't otherwise save the expiring message (ex: via a screenshot).

The `inReplyTo` {6} data field indicates that the current message is
a related continuation of another message sent in the same MLS group.
It contains the message ID of the referenced message and the SHA-256
hash [@!RFC6234] of its `MimiContent` structure. If the `message` field is
empty (i.e. both the message ID `localPart` and the `domain` are
zero length), the receiver assumes that the current message has not
identified any special relationship with another previous message;
in that case the `hash-alg` is `none` and the `replyToHash` is zero
length. 

The `inReplyTo` hash is a message digest used to make sure that a MIMI
message cannot refer to a sequence of referred messages which refers
back to itself. When replying a client checks if the referenced message
is itself a Reply. It compares the hash

When receiving a message, the client verifies that the hash is correct. Next
it checks if the referenced message is itself a Reply. If so, it continues
following the referenced messages, checking that neither the messageId nor
the hash of any of referenced messages indicates a Reply which "loops" back
to a message later in the inReplyTo chain.

``` c++
enum HashAlgorithm {
    none = 0,
    sha256 = 1
};

struct ReplyToInfo {
    MessageId message;
    HashAlgorithm hashAlg;
    Octets replyToHash;      // empty or hash of body.content
};
```
Note that a `inReplyTo`
always references a specific message ID. Even if the original message
was edited several times, a reply always refers to a specific version
of that message, and SHOULD refer to the most current version at the
time the reply is sent.


## Message Bodies

Every MIMI content message has a body {7} which can have multiple,
possibly nested parts. A body with zero parts is permitted when
deleting or unliking {8}. When there is a single body, its IANA
media type, subtype, and parameters are included in the
contentType field {9}. 

```c++
typedef std::monostate NullPart; // {8}

struct SinglePart {
    String contentType;   // An IANA media type {9}
    Octets content;       // The actual content
};

struct ExternalPart {
    String contentType;   // An IANA media type {9}
    String url;           // A URL where the content can be fetched
    uint32 expires;       // 0 = does not expire
    uint64 size;          // size of content in octets
    uint16 encAlg;        // An IANA AEAD Algorithm number, or zero
    Octets key;           // AEAD key
    Octets nonce;         // AEAD nonce
    Octets aad;           // AEAD additional authentiation data
    String description;   // an optional text description
};

typedef std::vector<NestablePart> MultiParts; 

enum PartSemantics { // {10}
    nullPart = 0,    
    singlePart = 1, // the bodyParts is a single part
    chooseOne = 2,  // receiver picks exactly one part to process
    singleUnit = 3  // receiver processes all parts as single unit
    processAll = 4  // receiver processes all parts individually
};

enum Disposition {
    unspecified = 0,
    render = 1,
    reaction = 2,
    profile = 3,
    inline = 4,
    icon = 5,
    attachment = 6,
    session = 7,
    preview = 8
};

struct NestablePart {
    Disposition disposition;  // {11}
    String language;          // {12}
    uint16 partIndex;         // {13}
    PartSemantics partSemantics;
    std::variant<NullPart, SinglePart, ExternalPart, MultiParts> part;
};

```

With some types of message content, there are multiple media types
associated with the same message which need to be rendered together,
for example a rich-text message with an inline image. With other
messages, there are multiple choices available for the same content,
for example a choice among multiple languages, or between two
different image formats. The relationship semantics among the parts
is specified as an enumeration {10}. 

The `nullPart` part semantic is used when there is no body part--for
deleting and unliking. The `singlePart` part semantic is used when
there is a single body part.

The `chooseOne` part semantic is roughly analogous to the semantics of the
`multipart/alternative` media type, except that the ordering of the
nested body parts is merely a preference of the sender. The receiver
can choose the body part among those provided according to its own
policy.

The `singleUnit` part semantic is roughly analogous to the semantics
of the `multipart/related` media type, in that all the nested body
parts at this level are part of a single entity (for example, a
rich text message with an inline image). If the receiver does not
understand even one of the nested parts at this level, the receiver
should not process any of them.

The `processAll` part semantic is roughly analogous to the semantics
of the `multipart/mixed` media type. The receiver should process as
many of the nested parts at this level as possible. For example, a
rich text document with a link, and a preview image of the link target
could be expressed using this semantic. Processing the preview image
is not strictly necessary for the correct rendering of the rich text
part.

The disposition {11} and language {12} of each part can be specified
for any part, including for nested parts. The disposition represents
the intended semantics of the body part or a set of nested parts.
It is inspired by the values in the Content-Disposition MIME header
[@?RFC2183].
The `render` disposition means that the content should be rendered
according to local policy. The  `inline` dispositions means that the
content should be rendered "inline" directly in the chat interface.
The `attachment` disposition means that the content is intended to
be downloaded by the receiver instead of being rendered immediately.
The `reaction` disposition means that the content is a single
reaction to another message, typically an emoji, but which could be
an image, sound, or video. The `reaction` disposition was originally published
in [@?RFC9078], but was incorrectly placed in the Content Disposition
Parameters IANA registry instead of in the Content Disposition Values
registry.
The `session` disposition means that the content is a description of
a multimedia session, or a URI used to join one.
The `preview` disposition means that the content is a sender-generated
preview of something, such as the contents of a link. 
The value of the language data field is an empty string or a
comma-separated list of one or more `Language-tag`s as defined
in [@!RFC5646]. 

Each part also has an part index {13}, which is a zero-indexed,
depth-first integer. It is used to efficiently refer to a specific
body part (for example, an inline image) within another part. See
{Nested body examples} for an example of how the part index is
calculated.

## External content

It is common in Instant Messaging systems to reference external
content via URI that will be processed automatically, either to
store bulky content (ex: videos, images, recorded sounds) outside the
the messaging infrastructure, or to access a specific service URI,
for example, a media forwarding service for conferencing. 

An ExternalPart is a convenient way to reference this content. It
provides a similar function to the message/external-body media type.
It optionally includes the size of the data in octets (or zero if
the length is not provided). It also includes an optional timestamp
after which the external content is invalid, expressed as seconds
since the start of the UNIX epoch (01-Jan-1970), or zero if the
content does not expire.

Typically, external content is encrypted with an ephemeral symmetric
key before it is uploaded, and whatever is necessary for decryption
is shared over the message channel.

It is a matter of local policy where the content is uploaded. Often
in federated messaging systems, the sender of the content stores the
external content in their own domain, but in some systems the content
is stored in the "owning" or "hub" domain of the MLS group.

Before being uploaded, external content is encrypted with an
IANA-registered Authenticated Encryption with Additional Data (AEAD)
algorithm as described in [@!RFC5116]. The key, nonce, and additional
authenticated data (aad) values are set to the values used during the
encryption. Unless modified by an extension, the default value of the
`aad` is zero length.

If the external URL is a service, the `encAlg` is set to zero, and the
`key`, `nonce`, and `aad` fields are zero length. 

Implementations of this specification MUST implement the AES-128-GCM
algorithm.

## Derived Data Values

In addition to fields which are contained in a MIMI content message,
there are also two fields which the implementation can definitely derive
(the MLS group ID {14}, and the leaf index of the sender {15}). Many
implementations could also determine one or more of: the senders client
identifier URL {16}, the user identifier URL of the credential associated with
the sender {17}, and the identifier URL for the MLS group {18}.

~~~~~~~ c++
struct MessageDerivedValues {
    Octets mlsGroupId;       // value always available {14}
    uint32 senderLeafIndex;  // value always available {15}
    ImUrl senderClientUrl;   // {16}
    ImUrl senderUserUrl;     // "From" {17}
    ImUrl mlsGroupUrl;       // "To" {18}
};
~~~~~~~

# Examples

In the following examples, we assume that an MLS group is already established and
that either out-of-band or using the MLS protocol or MLS extensions that the
following is known to every member of the group:

* The membership of the group (via MLS).
* The identity of any MLS client which sends an application message (via MLS).
* The MLS group ID (via MLS)
* The human readable name(s) of the MLS group, if any (out-of-band or extension).
* Which media types are mandatory to implement (MLS content advertisement extensions).
* For each member, the media types each supports (MLS content advertisement extensions).

Messages sent to an MLS group are delivered to every member of the group active during
the epoch in which the message was sent.


## Original Message

In this example, Alice Smith sends a rich-text (Markdown) [@!RFC7763]
message to the Engineering Team MLS group. The following values are
derived from the client:

* Sender leaf index: 4
* Sender client ID URL:
  im:3b52249d-68f9-45ce-8bf5-c799f3cad7ec/0003@example.com
* Sender user handle URL:
  im:%40alice-smith@example.com
* MLS group ID:
  7u4NEqe1tbeBFa0aHdsTgRyD/XOHxD5meZpZS+7aJr8=
* The MLS group URL:
  im:#engineering_team@example.com
* The MLS group name: "Engineering Team"

Below are the relevant data fields set by the sender:

~~~~~~~ c++
messageId = "28fd19857ad7@example.com";
timestamp = 1644387225019;  // 2022-02-08T22:13:45-00:00
expires = 0;
body.disposition = render;
body.partIndex = 0;
body.contentType = "text/markdown;charset=utf-8";
body.content = "Hi everyone, we just shipped release 2.0." +
               " __Good work__!";
~~~~~~~

## Reply

A reply message looks similar, but contains the message ID of the
original message in the `inReplyTo` data field. The derived MLS
group ID, URL, and name do not change in this example. The derived
senderClientId and senderLeafIndex are not especially relevant so
all but the user handle URL will be omitted.

* Sender user handle URL:
  im:%40bob-jones@example.com

The data fields needed:

~~~~~~~ c++
messageId = "e701beee59f9@example.com";
timestamp = 1644387237492;   // 2022-02-08T22:13:57-00:00
inReplyTo.message: "28fd19857ad7@example.com";
inReplyTo.hash-alg: sha256;
inReplyTo.replyToHash: "\xd3c14744d1791d02548232c23d35efa9" +
                       "\x7668174ba385af066011e43bd7e51501";
expires = 0;
body.disposition = render;
body.partIndex = 0;
body.contentType = "text/markdown;charset=utf-8";
body.content = "Right on! _Congratulations_ 'all!";
~~~~~~~

## Reaction

A reaction looks like a reply, but uses the Disposition token of reaction. It is
modeled on the reaction Content-Disposition token defined in [@RFC9078].
Both indicate that the intended disposition of the
contents of the message is a reaction.

The content in the sample message is a single Unicode heart character (U+2665).
Discovering the range of characters each implementation could render as a
reaction can occur out-of-band and is not within the scope of this proposal.
However, an implementation which receives a reaction character string it
does not recognize could render the reaction as a reply, possibly prefixing
with a localized string such as "Reaction: ".  Note that a reaction could
theoretically even be another media type (ex: image, audio, or video), although
not currently implemented in major instant messaging systems.
Note that many systems allow mutiple independent reactions per sender.

* Sender user handle URL:
  im:cathy-washington@example.com

~~~~~~~ c++
messageId = "1a771ca1d84f@example.com";
timestamp = 1644387237728;   // 2022-02-08T22:13:57-00:00
inReplyTo.message: "28fd19857ad7@example.com";
inReplyTo.hash-alg: sha256;
inReplyTo.replyToHash: "\xd3c14744d1791d02548232c23d35efa9" +
                       "\x7668174ba385af066011e43bd7e51501";
expires = 0;
body.disposition = reaction;
body.partIndex = 0;
body.contentType = "text/plain;charset=utf-8";
body.content = "\u2665"; \\ ♥
~~~~~~~

## Mentions

In instant messaging systems and social media, a mention allows special
formatting and behavior when a name, handle, or tag associated with a
known group is encountered, often when prefixed with a commercial-at "@"
character for mentions of users or a hash "#" character for groups or tags.
A message which contains a mention may trigger distinct notifications on
the IM client.

We can convey a mention by linking the user handle URI, or group URI in Markdown
or HTML rich content. For example, a mention using Markdown is indicated below.

* Sender user handle URL:
  im:cathy-washington@example.com

~~~~~~~ c++
messageId = "4dcab7711a77@example.com";
timestamp = 1644387243008;   // 2022-02-08T22:14:03-00:00
expires = 0;
body.disposition = render;
body.partIndex = 0;
body.contentType = "text/markdown;charset=utf-8";
body.content = "Kudos to [@Alice Smith](im:alice-smith@example.com)"
             + "for making the release happen!";
~~~~~~~

The same mention using HTML [@!W3C.CR-html52-20170808] is indicated below.

~~~~~~~
body.contentType = "text/html;charset=utf-8";
body.content = "<p>Kudos to <a href='im:alice-smith@example.com'>" +
               "@Alice Smith</a> for making the release happen!</p>"
~~~~~~~

## Edit

Unlike with email messages, it is common in IM systems to allow the sender of
a message to edit or delete the message after the fact. Typically the message
is replaced in the user interface of the receivers (even after the original
message is read) but shows a visual indication that it has been edited.

The `replaces` data field includes the message ID of the message to
edit/replace. The message included in the body is a replacement for the message
with the replaced message ID.

Here Bob Jones corrects a typo in his original message:

* Sender user handle URL:
  im:%40bob-jones@example.com

~~~~~~~ c++
messageId = "89d3472622a4@example.com";
timestamp = 1644387248621;   // 2022-02-08T22:14:08-00:00
replaces: "e701beee59f9@example.com";
expires = 0;
body.disposition = render;
body.partIndex = 0;
body.contentType = "text/markdown;charset=utf-8";
body.content = "Right on! _Congratulations_ y'all!";
~~~~~~~


## Delete

In IM systems, a delete means that the author of a specific message has
retracted the message, regardless if other users have read the message
or not. Typically a placeholder remains in the user interface showing
that a message was deleted. Replies which reference a deleted message
typically hide the quoted portion and reflect that the original message
was deleted.

If Bob deleted his message instead of modifying it, we would represent it
using the `replaces` data field, and using an empty body (NullPart),
as shown below.

~~~~~~~
messageId = "89d3472622a4@example.com";
timestamp = 1644387248621;   // 2022-02-08T22:14:08-00:00
replaces: "e701beee59f9@example.com";
expires = 0;
body.disposition = render;
body.partSemantics = nullPart;
body.part = NullPart;
~~~~~~~

## Unlike

In most IM systems, not only is it possible to react to a message ("Like"),
but it is possible to remove a previous reaction ("Unlike"). This can be
accomplished by deleting the message which creates the original reaction

If Cathy removes her reaction, we would represent the removal using a
`replaces` data field with an empty body, referring to the message which
created the reaction, as shown below.

* Sender user handle URL:
  im:cathy-washington@example.com

~~~~~~~ c++
messageId = "d052cace46f8@example.com";
timestamp = 1644387250389;   // 2022-02-08T22:14:10-00:00
replaces: "1a771ca1d84f@example.com";
expires = 0;
body.disposition = reaction;
body.partIndex = 0;
body.partSemantics = nullPart;
body.part = NullPart;
~~~~~~~


## Expiring

Expiring messages are designed to be deleted automatically by the receiving
client at a certain time whether they have been read or not.  As with manually
deleted messages, there is no guarantee that an uncooperative client or a
determined user will not save the content of the message, however most clients
respect the convention.

The `expires` data field contains the timestamp when the message can be deleted.
The semantics of the header are that the message is automatically deleted
by the receiving clients at the indicated time without user interaction or
network connectivity necessary.

* Sender user handle URL:
  im:alice-smith@example.com
  
~~~~~~~ c++
messageId = "5c95a4dfddab@example.com";
timestamp = 1644389403227;   // 2022-02-08T22:49:06-00:00
expires = 1644390004;         // ~10 minutes later
body.disposition = render;
body.partIndex = 0;
body.contentType = "text/markdown;charset=utf-8";
body.content = "__*VPN GOING DOWN*__\n" +
    "I'm rebooting the VPN in ten minutes unless anyone objects."
~~~~~~~

## Attachments

An ExternalPart is a convenient way to present both "attachments" and
(possibly inline rendered) content which is too large to be included
in an MLS application message. The disposition data
field is set to inline if the sender recommends inline rendering, or
attachment if the sender intends the content to be downloaded or
rendered separately.

~~~~~~~
body.disposition = attachment;
body.expires = 0;
body.contentType = "video/mp4";
body.URL = "https://example.com/storage/bigfile.mp4";
body.size = 708234961;
body.encAlg = 0x0001;    // AES-128-GCM
body.key = "\x21399320958a6f4c745dde670d95e0d8";
body.nonce = "\xc86cf2c33f21527d1dd76f5b";
body.aad = "";
body.description = "2 hours of key signing video";
~~~~~~~

Other dispositions of external content are also possible, for example
an external GIF animation of a rocket ship could be used with a
reaction disposition.


## Conferencing

Joining a conference via an external URL is possible. The link could be
rendered to the user, requiring a click. Alternatively the URL could be
rendered the 
disposition could be specified as `session` which could be processed 
differently by the client (for example, alerting the user or presenting
a dialog box). 
Further discussion of calling and conferencing functionality is out-of-scope
of this document.

~~~~~~~
body.expires = 0;
body.url = "https://example.com/join/12345";
body.description = "Join the Foo 118 conference";
body.expires = 1699671600; // 10-Nov-2023 19:00 UTC
body.contentType = "";     // contentType not relevant
body.size = 0;             // no defined size
body.encAlg = 0;           // no encryption
body.key = "";
body.nonce = "";
body.aad = "";
~~~~~~~

## Topics / Threading

As popularized by the messaging application Slack, some messaging
applications have a notion of a Topic or message Thread
(not to be confused with message threading as used in email).
Clients beginning a new "topic" populate the `topicId` with a unique
opaque octet string. This could be the message ID of the first message
sent related to the topic. Subsequent messages may include the same
`topicId` for those messages to be associated with the same topic. The sort order
for messages within a thread uses the timestamp field. If more than
one message has the same timestamp, the lexically lowest message ID
sorts earlier.


## Delivery Reporting and Read Receipts

In instant messaging systems, read receipts typically generate a distinct
indicator for each message. In some systems, the number of users in a group
who have read the message is subtly displayed and the list of users who
read the message is available on further inspection.

Of course, Internet mail has support for read receipts as well, but
the existing message disposition notification mechanism defined for email
in [@?RFC8098] is completely inappropriate in this context:

* notifications can be sent by intermediaries
* only one notification can be sent about a single message per recipient
* a human-readable version of the notification is expected
* each notification can refer to only one message
* it is extremely verbose

Instead we would like to be able to include status changes about multiple
messages in each report, the ability to mark a message delivered, then read, then unread, then expired
for example.

The proposed format below, application/mimi-message-status is sent
by one member of an MLS group to the entire group and can refer to multiple messages in that group. 
The format contains its own timestamp, and a list of message ID / status pairs. As
the status at the recipient changes, the status can be updated in a subsequent notification.

~~~~~~~ c++
enum MessageStatus {
    unread = 0,
    delivered = 1,
    read = 2,
    expired = 3,
    deleted = 4,
    hidden = 5,
    error = 6
};

struct PerMessageStatus {
    MessageId messageId;
    MessageStatus status;
};

struct MessageStatusReport {
    unit64 timestamp;
    // a vector of message statuses in the same MLS group
    std::vector<PerMessageStatus> statuses;
};
~~~~~~~

* Sender user handle URL:
  im:bob-jones@example.com

~~~~~~~ c++
timestamp = 1644284703227;
statuses[0].messageId = "4dcab7711a77@example.com";
statuses[0].status = read;
statuses[1].messageId = "285f75c46430@example.com";
statuses[1].status = read;
statuses[2].messageId = "c5e0cd6140e6@example.com";
statuses[2].status = unread;
statuses[3].messageId = "5c95a4dfddab@example.com";
statuses[3].status = expired;
~~~~~~~


# Support for Specific Media Types

## MIMI Required and Recommended media types

As the MIMI Content container is just a container, the plain text or rich
text messages sent inside, and any image or other formats needs to be specified.
Clients compliant with MIMI MUST be able to receive the following media types:

* application/mimi-content -- the MIMI Content container format (described in this document)
* text/plain;charset=utf-8 
* text/markdown;variant=GFM -- Github Flavored Markdown [@!GFM])

Note that it is acceptable to render the contents of a received markdown
document as plain text.

The following MIME types are RECOMMENDED:

* text/markdown;variant=CommonMark -- [CommonMark](https://spec.commonmark.org/0.30)
* text/html
* application/mimi-message-status -- (described in this document)
* image/jpeg
* image/png

Clients compliant with this specification must be able to decrypt ExternalParts
encrypted with AES-128-GCM.

## Use of proprietary media types

As most messaging systems are proprietary, standalone systems, it is useful to allow
clients to send and receive proprietary formats among themselves. Using the
functionality in the MIMI Content container, clients can send a message using the basic
functionality described in this document AND a proprietary format for
same-vendor clients simultaneously over the same group with end-to-end
encryption. An example is given in the Appendix.


# IANA Considerations

## MIME subtype registration of application/mimi-content

This document proposes registration of a media subtype with IANA.

~~~~~~~
Type name: application

Subtype name: mimi-content

Required parameters: none

Optional parameters: none

Encoding considerations:
   This message type should be encoded as binary data

Security considerations:
   See Section A of RFC XXXX

Interoperability considerations:
   See Section Y.Z of RFC XXXX

Published specification: RFC XXXX

Applications that use this media type:
   Instant Messaging Applications

Fragment identifier considerations: N/A

Additional information:

   Deprecated alias names for this type: N/A
   Magic number(s): N/A
   File extension(s): N/A
   Macintosh file type code(s): N/A

Person & email address to contact for further information:
   IETF MIMI Working Group mimi@ietf.org


~~~~~~~

## MIME subtype registration of application/mimi-message-status

This document proposes registration of a media subtype with IANA.

~~~~~~~
Type name: application

Subtype name: mimi-message-status

Required parameters: none

Optional parameters: none

Encoding considerations:
   This message type should be encoded as binary data

Security considerations:
   See Section A of RFC XXXX

Interoperability considerations:
   See Section Y.Z of RFC XXXX

Published specification: RFC XXXX

Applications that use this media type:
   Instant Messaging Applications

Fragment identifier considerations: N/A

Additional information:

   Deprecated alias names for this type: N/A
   Magic number(s): N/A
   File extension(s): N/A
   Macintosh file type code(s): N/A

Person & email address to contact for further information:
   IETF MIMI Working Group mimi@ietf.org

~~~~~~~

# Security Considerations

## General handling

The following cases are examples of nonsensical values that most likely
represent malicious messages. These should be logged and discarded.

* sender of the message
  - where the apparent sender is not a member of the target MLS group
* message IDs
  - which are very long (greater than 4096 octets)
  - where the sender domain and the `messageId` domain are different
  - where the `messageId` in this format is expected to match a similar
    field in the enclosing transfer protocol, but does not
* timestamps
  - received more than a few minutes in the future, or 
  - before the first concrete syntax of this document is published
* inReplyTo
  - `inReplyTo.hash-alg` is `none` even when the `inReplyTo.message` is present
  - `inReplyTo.hash-alg` is an unknown value
  - the length of `inReplyTo.replyToHash` does not correspond to the algorithm
    specified in `inReplyTo.hash-alg`
* topicId
  - the `topicId` is very long (greater than 4096 octets)
  - a topic is specified, but an `inReplyTo` or `replaces` field refers to a
    message outside of the topic
* expires
  - refers to a date more than a year in the past
  - refers to a date more than a year in the future
* body
  - has too many body parts (more than 1024)
  - is nested too deeply (more than 4 levels deep)
  - is too large (according to local policy)
  - has an unknown PartSemantics value
  - contains `partIndex` values which are not continuous from zero

For the avoidance of doubt, the following cases may be examples of legitimate use
cases, and should not be considered the result of a malicious sender.

* message IDs
  - where `inReplyTo.message` or `replaces` refer to an unknown message.
    Such a message could have been sent before the local client joined.
* body
  - where a body part contains an unrecognized Disposition value. The
  unknown value should be treated as if it where `render`.
  - where a contentType is unrecognized or unsupported.
  - where a language tag is unrecognized or unsupported.

## Alternate content rendering

This document includes a mechanism where the sender can offer alternate
versions of content in a single message. For example, the sender could
send:

* an plain text and an HTML version of a text message
* a thumbnail preview and link to a high-resolution image or video
* versions of the same message in multiple languages
* an PNG image and a scalable vector graphics version of a line drawing

A malicious client could use this mechanism to send content that will appear
different to a subset of the members of a group and possibly elicit an
incorrect or misleading response.

~~~
Message as seen by Alice (manager)
Xavier: Do you want me to reserve a room for the review meeting?

Message as seen by Bob (Alice's assistant)
Xavier: @Bob I need to pickup Alice's Ferarri keys. She'll confirm

Reply sent by Alice
Alice: Yes please.
~~~

## Link and Mention handling

Both Markdown and HTML support links. Using the example of an HTTP link,
if the rendered text and the link target match exactly or are canonically
equivalent, there is no need for confirmation if the end user selects the link.

~~~
[example.com/foobar](https://example.com/foobar)
[https://example.com/foobar](https://example.com/foobar)
[https://example.com:443/foobar](https://example.com/foobar)
~~~

However, if the link text is different, the user should be presented with
an alert warning that the text is not the same.

~~~
[https://example.com/foobar](https://spearphishers.example/foobar)
~~~

Likewise, for a Mention, if the link text exactly matches the IM URI, or
exactly matches the canonical handle for that URI, the IM application
can render the link as a Mention. In some clients, this may result in
a different notification policy.

~~~
[im:alice-smith@example.com](im:alice-smith@example.com)
[@AliceSmith](im:alice-smith@example.com)
~~~

Otherwise, the application, should render the text as any other link
that requires an alert warning.

## Delivery and Read Receipts

Delivery and Read Receipts can provide useful information inside a group,
or they can reveal sensitive private information. In many IM systems
there is are per-group policies for and/or delivery read receipts:

* they are required
* they are permitted, but optional
* they are forbidden

In the first case, everyone in the group would have to claim to support
read receipts to be in the group and agree to the policy of sending them
whenever a message was read. A user who did not wish to send read receipts could
review the policy (automatically or manually) and choose not to join
the group. Of course, requiring read receipts is a cooperative effort
just like using self-deleting messages. A malicious client could obviously 
read a message and not send a read receipt, or send a read receipt for a
message that was never rendered. However, cooperating clients have a way to
agree that they will send read receipts when a message is read in a specific
group.

In the second case, sending a read receipt would be at the discretion
of each receiver of the message (via local preferences).


{backmatter}

<reference anchor="OTR" target="https://otr.cypherpunks.ca/otr-wpes.pdf">
  <front>
    <title>Off-the-Record Communication, or, Why Not To Use PGP</title>
    <author fullname="Nikita Borisov">
      <organization>UC Berkeley</organization>
    </author>
    <author fullname="Ian Goldberg">
      <organization></organization>
    </author>
    <author fullname="Eric Brewer">
      <organization>UC Berkeley</organization>
    </author>
    <date month="October" day="28" year="2004"/>
  </front>
</reference>

<reference anchor="DoubleRatchet" target="https://signal.org/docs/specifications/doubleratchet/">
  <front>
    <title>The Double Ratchet Algorithm</title>
    <author fullname="Trevor Perrin">
      <organization>Signal</organization>
    </author>
    <author fullname="Moxie Marlinspike">
      <organization>Signal</organization>
    </author>
    <date month="November" day="20" year="2016"/>
  </front>
</reference>

<reference anchor="GFM" target="https://github.github.com/gfm/">
  <front>
    <title>GitHub Flavored Markdown Spec, Version 0.29-gfm</title>
    <author>
      <organization>GitHub</organization>
    </author>
    <date month="March" day="6" year="2019"/>
  </front>
</reference>


# Multipart examples

## Proprietary and Common formats sent as alternatives

Example of body needed to send this profile and a proprietary
messaging protocol simultaneously.

~~~~~~~
body = new NestablePart();
body.disposition = render;
body.language = "";
body.partIndex = 0;
body.partSemantics = chooseOne;

s = new SinglePart();
s.contentType = "application/mimi-content";
s.content = "\xabcdef0123456789....";

standardPart = new NestablePart()
standardPart.disposition = render;
standardPart.language = "";
standardPart.partIndex = 1;
standardPart.partSemantics = singlePart;
standardPart.part = s;

p = new SinglePart();
p.contentType = 
  "application/vnd.examplevendor-fancy-im-message";
p.content = "\x0123456789abcdef....";

proprietaryPart = new NestablePart()
proprietaryPart.disposition = render;
proprietaryPart.language = "";
proprietaryPart.partIndex = 2;
proprietaryPart.partSemantics = singlePart;
proprietaryPart.part = p;

body.part = new MultiParts();
body.part.push(standardPart);
body.part.push(proprietaryPart);
~~~~~~~

## Mulitple Reactions Example

This shows sending a reaction with multiple separate emojis.

TBC

## Complicated Nested Example

This example shows separate English and French versions of HTML message with
inline images. Each of the images is presented in alternate formats: an animated GIF,
and a single PNG.

TBC

## TLS Presentation Language multipart container format

In a heterogenous group of IM clients, it is often desirable to send more than one
media type as alternatives, such that IM clients have a choice of which media
type to render. For example, imagine an IM group containing a set of clients
which support a common video format and a subset which only support animated GIFs.
The sender could use a `MultiParts` NestablePart with `chooseOne` semantics
containing both media types. Every client in the group chat could render something
resembling the media sent. This is analogous to the `multipart/alternative` [@?RFC2046]
media type.

Likewise it is often desirable to send more than one media type intended to be
rendered together as in (for example a rich text document with embedded images),
which can be represented using a `MultiParts` NestablePart with `processAll`
semantics. This is analogous to the `multipart/mixed` [@?RFC2046] media type.

Some implementors complain that the multipart types are unnatural to use inside a
binary protocol which requires explicit lengths such as MLS
[@?I-D.ietf-mls-protocol]. Concretely, an implementation has to scan through the
entire content to construct a boundary token which is not contained in the content.

Note that there is a minor semantic difference between multipart/alternative and
`MultiParts` with `chooseOne` semantics. In multipart/alternative, the parts are 
presented in preference order by the sender. With `MultiParts` the receiver
chooses its "best" format to render according to its own preferences.

# Changelog

## Changes between draft-mahy-mimi-content-01 and draft-mahy-mimi-content-02

* made semantics abstract (C++ structs) instead of using CPIM or MIME headers

## Changes between draft-mahy-mimi-content-02 and draft-ietf-mimi-content-00

* replaced threadId with topicId
* inReplyTo now has a hash of the referenced message
* clarified that replies are always to a specific version of a modified message
* changed timestamp to a whole number of milliseconds since the epoch
to avoid confusion
* added Security Considerations section
* added IANA Considerations section
* added change log

## Changes between draft-ietf-mimi-content-00 and draft-ietf-mimi-content-01

* created new abstract format for attachment information, instead of using
  message/external-body
* added discussion of encrypting external content
