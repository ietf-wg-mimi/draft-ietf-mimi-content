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
value = "draft-ietf-mimi-content-02"
stream = "IETF"

[[author]]
initials="R."
surname="Mahy"
fullname="Rohan Mahy"
organization = "Unaffiliated"
  [author.address]
  email = "rohan.ietf@gmail.com"
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
the MLS protocol [@!RFC9420]. Other relevant terminology may be
found in [@?I-D.barnes-mimi-arch] and [@?I-D.ralston-mimi-terminology].

# Introduction

RFC EDITOR: PLEASE REMOVE THE FOLLOWING PARAGRAPH. The source for
this draft is maintained in GitHub. Suggested changes should be
submitted as pull requests at https://github.com/ietf-wg-mimi/draft-ietf-mimi-content.
Editorial changes can be managed in GitHub, but any substantive 
change should be discussed on the MIMI mailing list (mimi@ietf.org).

MLS [@!RFC9420] is a group key establishment protocol
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

## Message ID and Accepted Timestamp

Every MIMI content message has a message ID which is calculated from the
hash of the ciphertext of the message. When the content is end-to-encrypted
with MLS for a specific MLS group, the cipher suite for the group specifies
a hash algorithm. The message ID is the first 32 octets of the hash of the
`MLSMessage` struct using that hash algorithm.

As described in the the MIMI architecture [@?I-D.barnes-mimi-arch], one
provider, called the hub, is responsible for ordering messages. The hub is
also responsible for recording the time that any application message is
accepted, and conveying it to any "follower" providers which receive messages
from the group. It is represented as the whole number of milliseconds since
the start of the UNIX epoch (01-Jan-1970 00:00:00 UTC). To the extent that
the accepted timestamp is available to a MIMI client, the client can use it
for fine grain sorting of messages into a consistent order.

## Message Container

Most common instant messaging features are expressed as individual messages.
A plain or rich text message is obviously a message, but a reaction (ex: like),
a reply, editing a previous message, deleting an earlier message, and read
receipts are all typically modeled as another message with different properties. 

This document describes the semantics of a message container, which
can represent most of these previously mentioned message types.
The container typically carries one or more body parts with the actual message
content (for example, an emoji used in a reaction, a plain text or rich text
message or reply, a link, or an inline image).

## Message Status Report

This document also describes the semantics of a status report of other messages.
Because some messaging systems deliver messages in batches and allow a user to
mark several messages read at a time, the report format allows a single report
to convey the read/delivered status of multiple messages (by message ID) within
the same MLS group at a time.

# MIMI Content Container Message Semantics

Each MIMI Content message is a container format with two categories
of information: 

* the message behavior fields (which can have default or empty values), and
* the body part(s) and associated parameters

> **NOTE**: The choice of a concrete binary syntax for MIMI Content messages
> is currently an open issue in the Working Group with the respondents of a
> poll split roughly 50/50 between using TLS Presentation Language (defined
> in Section 3 of [@!RFC8446]) vs. Concise Binary Object Representation
> (CBOR) [@!RFC8949]. This document will present the examples in the TLS
> Presentation Language and provide the same contents in CBOR in an Appendix.

The choice of a binary format was constrained in part because:

* we do not want to scan body parts to check for boundary marker
collisions. This rules out using multipart MIME types.
* we do not want to base64 encode body parts with binary media
types (ex: images). This rules out using JSON to carry the binary data.

The object fields in the structure defined below are numbered in
curly braces for reference in the text.


## Message Behavior Fields 

``` tls
struct {
    uint8 present;
    select (present) {
        case 0: struct{};
        case 1: T value;
    };
} optional<T>;

uint8  MessageId[32];
uint64 Timestamp;  /* milliseconds since 01-Jan-1970 */
uint8  Utf8;       /* a UTF-8 character */
uint8  IdUrl;      /* an identifier URL character */

struct {
    optional<MessageId> replaces;    /* {1} */
    opaque topicId<V>;               /* {2} */
    uint32 expires;                  /* 0 = does not expire {3} */
    optional<ReplyToInfo> inReplyTo; /* {4} */
    MessageId lastSeen<V>;           /* {5} */
    Extension extensions<V>;         /* {6} */
    NestablePart body;               /* {7} */
} MimiContent;
```

The `replaces` {1} data field indicates that the current message
is a replacement or update to a previous message whose message ID
is in the `replaces` data field. It is used to edit previously-sent
messages, delete previously-sent messages, and adjust reactions to
messages to which the client previously reacted.
 If the `replaces` field is absent, the receiver
assumes that the current message has not identified any special
relationship with another previous message. 

The `topicId` {2} data field indicates that the current message is
part of a logical grouping of messages which all share the same
value in the `topicId` data field. If the `topicId` is zero length,
there is no such grouping.

The `expires` {3} data field is a hint from the sender to the receiver
that the message should be locally deleted and disregarded at a specific
timestamp in the future. Indicate a message with no specific expiration
time with the value zero. The data field is an unsigned integer number of
seconds after the start of the UNIX epoch. Using an 32-bit unsigned
integer allows expiration dates until the year 2106. Note that
specifying an expiration time provides no assurance that the client
actually honors or can honor the expiration time, nor that the end user
didn't otherwise save the expiring message (ex: via a screenshot).

The `inReplyTo` {4} data field indicates that the current message is
a related continuation of another message sent in the same MLS group.
If present, it contains the message ID of the referenced message and the
SHA-256 hash [@!RFC6234] of its `MimiContent` structure. Otherwise,
the receiver assumes that the current message has not
identified any special relationship with another previous message. 

The `inReplyTo` hash is a message digest used to make sure that a MIMI
message cannot refer to a sequence of referred messages which refers
back to itself. When replying, a client MUST NOT knowingly create a sequence
of replies which create a loop.

When receiving a message, the client verifies that the hash is correct. Next
it checks if the referenced message is itself a Reply. If so, it continues
following the referenced messages, checking that neither the messageId nor
the hash of any of referenced messages indicates a Reply which "loops" back
to a message later in the inReplyTo chain.

``` tls
enum {
    none(0),
    sha256(1),
    (255)
} HashAlgorithm;

struct {
    MessageId message;
    HashAlgorithm hashAlg;
    opaque replyToHash<V>;  /* hash of content format */
} inReplyTo;
```

Note that a `inReplyTo`
always references a specific message ID. Even if the original message
was edited several times, a reply always refers to a specific version
of that message, and SHOULD refer to the most current version at the
time the reply is sent.

## Message Ordering

The `lastSeen` {5} data field indicates the latest message the sender
was aware of in the group.  It is a list of message ids.

If the sender recently joined the group and has not yet seen any messages,
the list is empty.

If the sender identifies a single message as unambiguously the latest
message in the group, the `lastSeen` list contains a single message id
from that message.

Imagine however that two users (Bob and Cathy) see a message from Alice
offering free Hawaiian pizza, and reply at the same time. Bob and Cathy both send
messages with their `lastSeen` including a single message id (Alice's)
message about pizza.  Their messages don't need to be replies or reactions.
Bob might just send a message saying he doesn't like pineapple on pizza.
Now Doug receives all these messages and replies
as well. Doug's message contains a `lastSeen` including the message id
list of both Bob's and Cathy's replies, effectively "merging" the order
of messages. 

The next message after Doug's message contains a `lastSeen` containing
only the message id of Doug's message.

## Extension Fields

In order to add additional functionality to MIMI, senders can include
extension fields in the message format {6}. Each extension has a name, which
contains between 1 and 255 octets of UTF-8, and an opaque value. The value
of each extension can be between 0 and 65535 octets.
The message content `extensions` field MUST NOT include more than one
extension field with the same name.

``` tls
struct {
    Utf8 name<1..255>;
    opaque value<0..65535>;
} Extension;
```

## Message Bodies

Every MIMI content message has a body {7} which can have multiple,
possibly nested parts. A body with zero parts is permitted when
deleting or unliking. External body parts (#external) are also supported.
When there is a single (inline) part or a (single) externally reference
part, its IANA media type, subtype, and parameters are included in the
contentType field {8}. 

``` tls
enum {
    null(0),
    single(1),
    external(2),
    multi(3),
    (255)
} PartCardinality;

struct {
    Utf8 contentType<V>; /* An IANA media type {8} */
    opaque content<V>;
} SinglePart;

enum {             /* {9} */
    chooseOne(0),  /* receiver picks exactly one part to process */
    singleUnit(1), /* receiver processes all parts as single unit */
    processAll(2), /* receiver processes all parts individually */
    (255)
} MultiplePartSemantics;

struct {
    Disposition disposition;  /* {10} */
    Utf8 language<V>;         /* {11} */
    uint16 partIndex;         /* {12} */
    PartCardinality cardinality;
    select(cardinality) {
        case null:
            struct {};
        case single:
            SinglePart part;
        case external:
            ExternalPart part;
        case multi:
            MultiplePartSemantics partSemantics;
            NestablePart parts<V>;
    };
} NestablePart;
```

With some types of message content, there are multiple media types
associated with the same message which need to be rendered together,
for example a rich-text message with an inline image. With other
messages, there are multiple choices available for the same content,
for example a choice among multiple languages, or between two
different image formats. The relationship semantics among the parts
is specified as an enumeration {9}. 

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

The disposition {10} and language {11} of each part can be specified
for any part, including for nested parts. The disposition represents
the intended semantics of the body part or a set of nested parts.
It is inspired by the values in the Content-Disposition MIME header
[@?RFC2183].

``` tls
enum {
    unspecified(0),
    render(1),
    reaction(2),
    profile(3),
    inline(4),
    icon(5),
    attachment(6),
    session(7),
    preview(8),
    (255)
} Disposition;
```

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

Each part also has an part index {12}, which is a zero-indexed,
depth-first integer. It is used to efficiently refer to a specific
body part (for example, an inline image) within another part. See
{Nested body examples} for an example of how the part index is
calculated.

## External content {#external}

It is common in Instant Messaging systems to reference external
content via URI that will be processed automatically, either to
store bulky content (ex: videos, images, recorded sounds) outside
the messaging infrastructure, or to access a specific service URI,
for example, a media forwarding service for conferencing.

An `ExternalPart` is a convenient way to reference this content. It
provides a similar function to the `message/external-body` media type.
It optionally includes the size of the data in octets (or zero if
the length is not provided). It also includes an optional timestamp
after which the external content is invalid, expressed as seconds
since the start of the UNIX epoch (01-Jan-1970), or zero if the
content does not expire.

``` tls
struct {
  Utf8 contentType<V>;   /* An IANA media type {8} */
  Utf8 url<V>;           /* A URL where the content can be fetched */
  uint32 expires;        /* 0 = does not expire */
  uint64 size;           /* size of content in octets */
  uint16 encAlg;         /* An IANA AEAD Algorithm number, or zero */
  opaque key<V>;         /* AEAD key */
  opaque nonce<V>;       /* AEAD nonce */
  opaque aad<V>;         /* AEAD additional authentiation data */
  HashAlgorithm hashAlg;
  opaque contentHash<V>; /* hash of the content at the target url */
  Utf8 description<V>;   /* an optional text description */
} ExternalPart;
```

Typically, external content is encrypted with an ephemeral symmetric
key before it is uploaded, and whatever is necessary for decryption
is shared over the message channel.

It is a matter of local policy to where the content is uploaded. Often
in federated messaging systems, the sender of the content stores the
external content in their own domain, but in some systems the content
is stored in the "owning" or "hub" domain of the MLS group.

Before being uploaded, private external content is encrypted with an
IANA-registered Authenticated Encryption with Additional Data (AEAD)
algorithm as described in [@!RFC5116]. The key, nonce, and additional
authenticated data (aad) values are set to the values used during the
encryption. Unless modified by an extension, the default value of the
`aad` is empty.

If the external URL is a service, or the external content is not considered
private, the `encAlg` is set to zero, and the `key`, `nonce`, and `aad`
fields are zero length.

Implementations of this specification MUST implement the AES-128-GCM
algorithm.

## Derived Data Values

In addition to fields which are contained in a MIMI content message,
there are also two fields which the implementation can definitely derive
(the MLS group ID {13}, and the leaf index of the sender {14}). Many
implementations could also determine one or more of: the sender's client
identifier URL {15}, the user identifier URL of the credential associated
with the sender {16}, and the identifier URL for the MIMI room {17}.

``` tls
struct {
    MessageId messageId;
    Timestamp hubAcceptedTimestamp;
    opaque mlsGroupId<V>;      /* value always available {13} */
    uint32 senderLeafIndex;    /* value always available {14} */
    IdUrl senderClientUrl<V>;  /* {15} */
    IdUrl senderUserUrl<V>;    /* "From" {16} */
    IdUrl roomUrl<V>;          /* "To" {17} */
} MessageDerivedValues;
```

# Examples

In the following examples, we assume that an MLS group is already established and
that either out-of-band or using the MLS protocol or MLS extensions that the
following is known to every member of the group:

* The membership of the group (via MLS).
* The identity of any MLS client which sends an application message (via MLS).
* The MLS group ID (via MLS)
* The human readable name(s) of the MIMI room, if any (out-of-band or extension).
* Which media types are mandatory to implement (MLS content advertisement extensions).
* For each member, the media types each supports (MLS content advertisement extensions).

Messages sent to an MLS group are delivered to every member of the group active during
the epoch in which the message was sent.

For the sake of readability, all message IDs will be shown using only the first six octets of 32, for example: `"\xe701beee59f9..."`.


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
* The MIMI room URL:
  im:#engineering_team@example.com
* The MIMI group name: "Engineering Team"

In addition, the messageId and timestamp are:

~~~ c++
messageId = "\x28fd19857ad7...";
timestamp = 1644387225019;  // 2022-02-08T22:13:45-00:00
~~~

Below are the relevant data fields set by the sender:

~~~~~~~ c++
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
* messageId = "\xe701beee59f9...";
* timestamp = 1644387237492;  // 2022-02-08T22:13:57-00:00

The data fields needed:

~~~~~~~ c++
inReplyTo.message: "\x28fd19857ad7...";
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
* messageId = "\x1a771ca1d84f...";
* timestamp = 1644387237728;   // 2022-02-08T22:13:57-00:00

~~~~~~~ c++
inReplyTo.message: "\x28fd19857ad7...";
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
* messageId = "\x4dcab7711a77...";
* timestamp = 1644387243008;   // 2022-02-08T22:14:03-00:00


~~~~~~~ c++
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
* messageId = "\x89d3472622a4...";
* timestamp = 1644387248621;   // 2022-02-08T22:14:08-00:00


~~~~~~~ c++
replaces: "\xe701beee59f9...";
expires = 0;
body.disposition = render;
body.partIndex = 0;
body.contentType = "text/markdown;charset=utf-8";
body.content = "Right on! _Congratulations_ y'all!";
~~~~~~~

Note that replies and reactions always refer to a specific message id,
and therefore a specific "version" of a message, which could have been
edited before and/or after the message id referenced in the reply or reaction.
It is a matter of local policy how to render (if at all) a reaction to
a subsequently edited message.

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

* Sender user handle URL:
  im:%40bob-jones@example.com
* messageId = "\x89d3472622a4...";
* timestamp = 1644387248621;   // 2022-02-08T22:14:08-00:00

~~~~~~~
replaces: "\xe701beee59f9...";
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
* messageId = "\xd052cace46f8...";
* timestamp = 1644387250389;   // 2022-02-08T22:14:10-00:00

~~~~~~~ c++
replaces: "\x1a771ca1d84f...";
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
* messageId = "\x5c95a4dfddab...";
* timestamp = 1644389403227;   // 2022-02-08T22:49:06-00:00

~~~~~~~ c++
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
statuses[0].messageId = "\x4dcab7711a77...";
statuses[0].status = read;
statuses[1].messageId = "\x285f75c46430...";
statuses[1].status = read;
statuses[2].messageId = "\xc5e0cd6140e6...";
statuses[2].status = unread;
statuses[3].messageId = "\x5c95a4dfddab...";
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

Clients compliant with this specification must be able to download
ExternalParts with `http` and `https` URLs, and decrypt downloaded content
encrypted with the AES-128-GCM AEAD algorithm.

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
  - which duplicate another message ID already encountered
* timestamps
  - received more than a few minutes in the future, or 
  - before the first concrete syntax of this document is published
  - before the room containing them was created
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
* lastSeen
  - is empty, but the sender has previously sent messages in the room
  - results in a loop
  - refers to an excessive number of lastSeen messages simultaneously
    (contains more than 65535 message IDs). (Note that a popular
    message sent in a large group can result in thousands of reactions in
    a few hundred milliseconds.)
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
* lastSeen
  - refers to an unknown message
  - is empty for the sender's first message sent in the room
* body
  - where a body part contains an unrecognized Disposition value. The
  unknown value should be treated as if it where `render`.
  - where a contentType is unrecognized or unsupported.
  - where a language tag is unrecognized or unsupported.

## Validation of timestamp

The timestamp is the time a message is accepted by the hub provider. As such,
the hub provider can manipulate the timestamp, and the sending provider
can delay sending messages selectively to cause the timestamp on a hub to
be later.

> **TODO**: Discuss how to sanity check lastSeen, timestamp and the MLS
> epoch and generation, and the limitations of this approach.

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

Both Markdown and HTML support links. Using the example of an `https` link,
if the rendered text and the link target match exactly or are canonically
equivalent, there is no need for confirmation if the end user selects the link.

~~~
[example.com/foobar](https://example.com/foobar)
[https://example.com/foobar](https://example.com/foobar)
[https://example.com:443/foobar](https://example.com/foobar)
~~~

However, if the link text is different, or the scheme is downgraded
from https to http, the user should be presented with
an alert warning that the text is not the same.

~~~
[https://example.com/foobar](https://spearphishers.example/foobar)
[https://example.com/foobar](http://example.com/foobar)
~~~

An IM URI link to a user who has a member client in the MLS
group in which the message was sent is considered a mention. Clients may
support special rendering of mentions instead of treating them like any
other type of link. In Markdown and HTML, the display text portion of a
link is considered a rendering hint from the sender to the receiver of
the message. The receiver should use local policy to decide if the hint
is an acceptable local representation of the user represented by the link
itself. If the hint is not an acceptable representation, the client should
instead display its canonical representation for the user. 

For example, in the first examples, the sender expresses no preference
about how to render the mention. In the second example, the sender requests
that the mention is rendered as the literal URI. In the third example, the
sender requests the canonical handle for Alice. In the fourth example, the
sender requests Alice's first name.

~~~
<im:alice-smith@example.com>
[im:alice-smith@example.com](im:alice-smith@example.com)
[@AliceSmith](im:alice-smith@example.com)
[Alice](im:alice-smith@example.com)
~~~

Note that in some clients, presence of a mention for the local user may
result in a different notification policy.

If the client does not support special rendering of mentions, the
application, should render the text like any other link.

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

# CBOR Encoding of Examples

## Original message

```
0xf6 replaces is null
0x40 topicId is zero length bytes
0x00 expires is zero 
0xf6 inReplyTo is null
0x80 lastSeen is an empty array
0xa0 extensions is an empty map

  /* NestablePart */
  0x01 disposition = render
  0x60 language is empty sting
  0x00 partIndex = 0 (1st part)
  0x01 cardinality = single part

    /* SinglePart */
    0x78 0x1b contentType is string of 0x1b octets
      0x746578742f6d61726b646f776e3b6368  "text/markdown;cha"
        61727365743d7574662d38            "rset=utf-8"
    0x58 0x38 content is bytes of 0x38 octets
      0x48692065766572796f6e652c20776520  "Hi everyone, we "
        6a75737420736869707065642072656c  "just shipped rel"
        6561736520322e302e205f5f476f6f64  "ease 2.0. __Good"
        20776f726b5f5f21                  " work__!"

message ID
  0xd3c14744d1791d02548232c23d35efa9
    7668174ba385af066011e43bd7e51501
```

## Reply

```
0xf6 replaces is null
0x40 topicId is zero length bytes
0x00 expires is zero 
  /* inReplyTo */
  0x58 0x20 messageId is 0x20 bytes
    0xd3c14744d1791d02548232c23d35efa9
      7668174ba385af066011e43bd7e51501
  0x01 hashAlg = sha256
  0x58 0x20 hash is 0x20 bytes
    0x6b44053cb68e3f0cdd219da8d7104afc
      2ae5ffff782154524cef093de39345a5
0x81 lastSeen is an array of 1 item
  0x58 0x20 
    0xd3c14744d1791d02548232c23d35efa9  // Original message
      7668174ba385af066011e43bd7e51501
0xa0 extensions is an empty map

  /* NestablePart */
  0x01 disposition = render
  0x60 language is empty sting
  0x00 partIndex = 0 (1st part)
  0x01 cardinality = single part

    /* SinglePart */
    0x78 0x1b contentType is string of 0x1b octets
      0x746578742f6d61726b646f776e3b6368  "text/markdown;cha"
        61727365743d7574662d38            "rset=utf-8"
    0x58 0x21 content is bytes of 0x21 octets
      0x5269676874206f6e21205f436f6e6772  "Right on! _Congr"
        6174756c6174696f6e735f2027616c6c  "atulations_ 'all"
        21                                "!"

message ID
  0xe701beee59f9376282f39092e1041b2a
    c2e3aad1776570c1a28de244979c71ed
```

## Reaction

```
0xf6 replaces is null
0x40 topicId is zero length bytes
0x00 expires is zero 
  /* inReplyTo */
  0x58 0x20 messageId is 0x20 bytes
    0xd3c14744d1791d02548232c23d35efa9
      7668174ba385af066011e43bd7e51501
  0x01 hashAlg = sha256
  0x58 0x20 hash is 0x20 bytes
    0x6b44053cb68e3f0cdd219da8d7104afc
      2ae5ffff782154524cef093de39345a5
0x81 lastSeen is an array of 1 item
  0x58 0x20 
    0xe701beee59f9376282f39092e1041b2a  // Reply above
      c2e3aad1776570c1a28de244979c71ed
0xa0 extensions is an empty map

  /* NestablePart */
  0x02 disposition = reaction
  0x60 language is empty sting
  0x00 partIndex = 0 (1st part)
  0x01 cardinality = single part

    /* SinglePart */
    0x78 0x18 contentType is string of 0x18 octets
      0x746578742f706c61696e3b6368617273  "text/plain;charse"
        65743d7574662d38                  "t=utf-8"
    0x43 content is bytes of 0x03 octets
      0xe29da4                            "❤"

message ID
  0x4dcab7711a77ea1dd025a6a1a7fe01ab
    3b0d690f82417663cb752dfcc37779a1
```

## Mention

```
0xf6 replaces is null
0x40 topicId is zero length bytes
0x00 expires is zero 
0xf6 inReplyTo is null
0x81 lastSeen is an array of 1 item
  0x58 0x20 
    0xe701beee59f9376282f39092e1041b2a  // Reply above
      c2e3aad1776570c1a28de244979c71ed  // (didn't see Reaction yet)
0xa0 extensions is an empty map

  /* NestablePart */
  0x01 disposition = render
  0x60 language is empty sting
  0x00 partIndex = 0 (1st part)
  0x01 cardinality = single part

    /* SinglePart */
    0x78 0x1b contentType is string of 0x1b octets
      0x746578742f6d61726b646f776e3b6368  "text/markdown;cha"
        61727365743d7574662d38            "rset=utf-8"
    0x58 0x52 content is bytes of 0x52 octets
      0x4b75646f7320746f205b40416c696365  "Kudos to [@Alice"
        20536d6974685d28696d3a616c696365  " Smith](im:alice"
        2d736d697468406578616d706c652e63  "-smith@example.c"
        6f6d2920666f72206d616b696e672074  "om) for making t"
        68652072656c65617365206861707065  "he release happe"
        6e21                              "n!"

message ID
  0x4dcab7711a774b75a91effb51266d44e
    ba77985da34528a515fac3c38e4998b8
```

## Edit

```
0x58 0x20 replaces is bytes of 0x20 octets
  0xe701beee59f9376282f39092e1041b2a
    c2e3aad1776570c1a28de244979c71ed
0x40 topicId is zero length bytes
0x00 expires is zero
0xf6 inReplyTo is null
0x82 lastSeen is an array of 2 items
  0x58 0x20 
    0x4dcab7711a77ea1dd025a6a1a7fe01ab  // Reaction
      3b0d690f82417663cb752dfcc37779a1
  0x58 0x20 
    0x4dcab7711a774b75a91effb51266d44e  // Mention
      ba77985da34528a515fac3c38e4998b8
0xa0 extensions is an empty map

  /* NestablePart */
  0x01 disposition = render
  0x60 language is empty sting
  0x00 partIndex = 0 (1st part)
  0x01 cardinality = single part

    /* SinglePart */
    0x78 0x1b contentType is string of 0x1b octets
      0x746578742f6d61726b646f776e3b6368  "text/markdown;cha"
        61727365743d7574662d38            "rset=utf-8"
    0x58 0x22 content is bytes of 0x21 octets
      0x5269676874206f6e21205f436f6e6772  "Right on! _Congr"
        6174756c6174696f6e735f207927616c  "atulations_ y'al"
        6c21                              "l!"

message ID
  0x89d3472622a4d9de526742bcd00b09dc
    78fa4edceaf2720e17b730c6dfba8be4
```

## Delete

```
0x58 0x20 replaces is bytes of 0x20 octets
  0xe701beee59f9376282f39092e1041b2a
    c2e3aad1776570c1a28de244979c71ed
0x40 topicId is zero length bytes
0x00 expires is zero
0xf6 inReplyTo is null
0x81 lastSeen is an array of 1 item
  0x58 0x20 
    0x89d3472622a4d9de526742bcd00b09dc  // Edit
      78fa4edceaf2720e17b730c6dfba8be4
0xa0 extensions is an empty map

  /* NestablePart */
  0x01 disposition = render
  0x60 language is empty sting
  0x00 partIndex = 0 (1st part)
  0x00 cardinality = null (zero parts)

message ID
  0x89d3472622a40d6ceeb27c42490fdc64
    c0e9c20c598f9d7c8e81640dae8db0fb
```

## Unlike

```
0x58 0x20 replace is bytes of 0x20 octets
  0x4dcab7711a77ea1dd025a6a1a7fe01ab  // Like
    3b0d690f82417663cb752dfcc37779a1
0x40 topicId is zero length bytes
0x00 expires is zero 
  /* inReplyTo */
  0x58 0x20 messageId is 0x20 bytes
    0xd3c14744d1791d02548232c23d35efa9
      7668174ba385af066011e43bd7e51501
  0x01 hashAlg = sha256
  0x58 0x20 hash is 0x20 bytes
    0x6b44053cb68e3f0cdd219da8d7104afc
      2ae5ffff782154524cef093de39345a5
0x81 lastSeen is an array of 1 item
  0x58 0x20 
    0x89d3472622a40d6ceeb27c42490fdc64  // Delete
      c0e9c20c598f9d7c8e81640dae8db0fb
0xa0 extensions is an empty map

  /* NestablePart */
  0x02 disposition = reaction
  0x60 language is empty sting
  0x00 partIndex = 0 (1st part)
  0x00 cardinality = null (zero parts)

message ID
  0x1a771ca1d84f8fda4184a1e02a549e20
    1bf434c6bfcf1237fa45463c6861853b
```

## Expiring

```
0xf6 replaces is null
0x40 topicId is zero length bytes
0x1a expires on 1644390004 
  0x62036674  // 10 minutes later
0xf6 inReplyTo is null
0x81 lastSeen is an array of 1 item
  0x58 0x20 
    0x1a771ca1d84f8fda4184a1e02a549e20  // Unlike
      1bf434c6bfcf1237fa45463c6861853b
0xa0 extensions is an empty map

  /* NestablePart */
  0x01 disposition = render
  0x60 language is empty sting
  0x00 partIndex = 0 (1st part)
  0x01 cardinality = single part

    /* SinglePart */
    0x78 0x1b contentType is string of 0x1b octets
      0x746578742f6d61726b646f776e3b6368  "text/markdown;cha"
        61727365743d7574662d38            "rset=utf-8"
    0x58 0x50 content is bytes of 0x50 octets
      0x5f5f2a56504e20474f494e4720444f57  "__*VPN GOING DOW"
        4e2a5f5f0a49276d207265626f6f7469  "N*__ I'm rebooti"
        6e67207468652056504e20696e207465  "ng the VPN in te"
        6e206d696e7574657320756e6c657373  "n minutes unless"
        20616e796f6e65206f626a656374732e  " anyone objects."

message ID
  0x5c95a4dfddab84348bcc265a479299fb
    d3a2eecfa3d490985da5113e5480c7f1
```

## Attachments

```
0xf6 replaces is null
0x40 topicId is zero length bytes
0x00 expires is zero
0xf6 inReplyTo is null
0x81 lastSeen is an array of 1 item
  0x58 0x20
    0x5c95a4dfddab84348bcc265a479299fb  // Expiring
      d3a2eecfa3d490985da5113e5480c7f1
0xa0 extensions is an empty map

  /* NestablePart */
  0x06 disposition = attachment
  0x62 language is a string of 0x02 octets
    0x656e                                "en"
  0x00 partIndex = 0 (1st part)
  0x02 cardinality = external part

    /* External Part *
    0x69 contentType is string of 0x09 octets
      0x766964656f2f6d7034                "video/mp4"
    0x78 0x27 url is string of 0x27 octets
      0x68747470733a2f2f6578616d706c652e  "https://example."
        636f6d2f73746f726167652f62696766  "com/storage/bigf"
        696c652e6d7034                    "ile.mp4"
    0x00 expires is zero
    0x1a size is 708234961 octets
      0x2a36ced1
    0x01 encAlg is 0x0001 = AES-128-GCM
    0x50 key is bytes of 16 octets
      0x21399320958a6f4c745dde670d95e0d8
    0x4c nonce is bytes of 12 octents
      0xc86cf2c33f21527d1dd76f5b
    0x40 aad is zero bytes
    0x01 hashAlg = sha256
    0x58 0x20 content hash is bytes of 32 octets
      0x9ab17a8cf0890baaae7ee016c7312fcc
        080ba46498389458ee44f0276e783163
    0x78 0x1c  description is string of 0x1c octets
      0x3220686f757273206f66206b65792073  "2 hours of key s"
        69676e696e6720766964656f          "igning video"

message ID
  0xb267614d43e7676d28ef5b15e8676f23
    679fe365c78849d83e2ba0ae8196ec4e
```

## Conferencing

```
0xf6 replaces is null
0x47 topicId is bytes of 0x07 octets
  0x466f6f20313138                        "Foo 118"
0x00 expires is zero
0xf6 inReplyTo is null
0x81 lastSeen is an array of 1 item
  0x58 0x20
    0xb267614d43e7676d28ef5b15e8676f23  // Attachment
      679fe365c78849d83e2ba0ae8196ec4e
0xa0 extensions is an empty map

  /* NestablePart */
  0x07 disposition = session
  0x60 language is an empty string
  0x00 partIndex = 0 (1st part)
  0x02 cardinality = external part

    /* External Part *
    0x60 contentType is an empty
    0x78 0x1e url is string of 0x1e octets
      0x68747470733a2f2f6578616d706c652e  "https://example."
        636f6d2f6a6f696e2f3132333435      "com/join/12345"
    0x00 expires is zero
    0xf6 size is null
    0xf6 encryption is null
    0xf6 hashing is null
    0x78 0x1b  description is string of 0x1b octets
      0x4a6f696e2074686520466f6f20313138  "Join the Foo 118"
        20636f6e666572656e6365            " conference"

message ID
  0xb267614d43e7676d28ef5b15e8676f23
    679fe365c78849d83e2ba0ae8196ec4e
```

# TLS Presentation Language

## Original Message

```
/* MimiContent struct */
0x00       optional replaces (present = 0)
0x00       length of topicId
0x00000000 expires
0x00       optional inReplyTo (present = 0)
0x00       length of lastSeen vector
0x00       length of extensions vector
  /* NestablePart struct (body)*/
  0x01     disposition = render
  0x00     length of language
  0x0000   partIndex = 0 (1st part)
  0x01     cardinality = single part
  /* SinglePart struct (part) */
    0x1b   length of contentType
      0x746578742f6d61726b646f776e3b6368  "text/markdown;cha"
        61727365743d7574662d38            "rset=utf-8"
    0x38   length of content
      0x48692065766572796f6e652c20776520  "Hi everyone, we "
        6a75737420736869707065642072656c  "just shipped rel"
        6561736520322e302e205f5f476f6f64  "ease 2.0. __Good"
        20776f726b5f5f21                  " work__!"

message ID
  0xd3c14744d1791d02548232c23d35efa9
    7668174ba385af066011e43bd7e51501
```

## Reply

```
/* MimiContent struct */
0x00       optional replaces (present = 0)
0x00       length of topicId
0x00000000 expires
/* inReplyTo */
  0x01       optional inReplyTo (present = 1)
  0xd3c14744d1791d02548232c23d35efa9  // 0x20 octet message ID
    7668174ba385af066011e43bd7e51501
  0x01 hashAlg = sha256
  0x20 hash is 0x20 bytes
    0x6b44053cb68e3f0cdd219da8d7104afc
      2ae5ffff782154524cef093de39345a5
0x20       length of lastSeen vector (1 item)
  0xd3c14744d1791d02548232c23d35efa9  // Original message
    7668174ba385af066011e43bd7e51501  
0x00       length of extensions vector
  /* NestablePart struct (body)*/
  0x01     disposition = render
  0x00     length of language
  0x0000   partIndex = 0 (1st part)
  0x01     cardinality = single part
  /* SinglePart struct (part) */
    0x1b   length of contentType
      0x746578742f6d61726b646f776e3b6368  "text/markdown;cha"
        61727365743d7574662d38            "rset=utf-8"
    0x21   length of content
      0x5269676874206f6e21205f436f6e6772  "Right on! _Congr"
        6174756c6174696f6e735f2027616c6c  "atulations_ 'all"
        21                                "!"

message ID
  0xe701beee59f9376282f39092e1041b2a
    c2e3aad1776570c1a28de244979c71ed
```

## Reaction

```
/* MimiContent struct */
0x00       optional replaces (present = 0)
0x00       length of topicId
0x00000000 expires
/* inReplyTo */
  0x01       optional inReplyTo (present = 1)
  0xd3c14744d1791d02548232c23d35efa9  // 0x20 octet message ID
    7668174ba385af066011e43bd7e51501
  0x01 hashAlg = sha256
  0x20 hash is 0x20 bytes
    0x6b44053cb68e3f0cdd219da8d7104afc
      2ae5ffff782154524cef093de39345a5
0x20       length of lastSeen vector (1 item)
    0xe701beee59f9376282f39092e1041b2a  // Reply (above)
      c2e3aad1776570c1a28de244979c71ed
0x00       length of extensions vector
  /* NestablePart */
  0x02   disposition = reaction
  0x00   length of language is zero
  0x0000 partIndex = 0 (1st part)
  0x01   cardinality = single part

    /* SinglePart */
    0x18 contentType is 0x18 octets
      0x746578742f706c61696e3b6368617273  "text/plain;charse"
        65743d7574662d38                  "t=utf-8"
    0x03 content is 0x03 octets
      0xe29da4                            "❤"

message ID
  0x4dcab7711a77ea1dd025a6a1a7fe01ab
    3b0d690f82417663cb752dfcc37779a1

```

## Mention

```
/* MimiContent struct */
0x00       optional replaces (present = 0)
0x00       length of topicId
0x00000000 expires
0x00       optional inReplyTo (present = 0)
0x20       length of lastSeen vector (1 item)
  0x58 0x20 
    0xe701beee59f9376282f39092e1041b2a  // Reply above
      c2e3aad1776570c1a28de244979c71ed  // (didn't see Reaction yet)
0x00       length of extensions vector

  /* NestablePart */
  0x01 disposition = render
  0x60 language is empty sting
  0x00 partIndex = 0 (1st part)
  0x01 cardinality = single part

    /* SinglePart */
    0x1b contentType is 0x1b octets
      0x746578742f6d61726b646f776e3b6368  "text/markdown;cha"
        61727365743d7574662d38            "rset=utf-8"
    0x52 content is 0x52 octets
      0x4b75646f7320746f205b40416c696365  "Kudos to [@Alice"
        20536d6974685d28696d3a616c696365  " Smith](im:alice"
        2d736d697468406578616d706c652e63  "-smith@example.c"
        6f6d2920666f72206d616b696e672074  "om) for making t"
        68652072656c65617365206861707065  "he release happe"
        6e21                              "n!"

message ID
  0x4dcab7711a774b75a91effb51266d44e
    ba77985da34528a515fac3c38e4998b8
```

## Edit

```
/* MimiContent struct */
0x01       optional replaces (present = 1)
  0xe701beee59f9376282f39092e1041b2a
    c2e3aad1776570c1a28de244979c71ed
0x00       length of topicId
0x00000000 expires
/* inReplyTo */
  0x01       optional inReplyTo (present = 1)
  0xd3c14744d1791d02548232c23d35efa9  // 0x20 octet message ID
    7668174ba385af066011e43bd7e51501
  0x01 hashAlg = sha256
  0x20 hash is 0x20 bytes
    0x6b44053cb68e3f0cdd219da8d7104afc
      2ae5ffff782154524cef093de39345a5
0x40       length of lastSeen vector (2 items)
    0x4dcab7711a77ea1dd025a6a1a7fe01ab  // Reaction
      3b0d690f82417663cb752dfcc37779a1
    0x4dcab7711a774b75a91effb51266d44e  // Mention
      ba77985da34528a515fac3c38e4998b8
0x00       length of extensions vector
  /* NestablePart struct (body)*/
  0x01     disposition = render
  0x00     length of language
  0x0000   partIndex = 0 (1st part)
  0x01     cardinality = single part
  /* SinglePart struct (part) */
    0x1b   length of contentType
      0x746578742f6d61726b646f776e3b6368  "text/markdown;cha"
        61727365743d7574662d38            "rset=utf-8"
    0x21   length of content
      0x5269676874206f6e21205f436f6e6772  "Right on! _Congr"
        6174756c6174696f6e735f2027616c6c  "atulations_ 'all"
        21                                "!"

message ID
  0x89d3472622a4d9de526742bcd00b09dc
    78fa4edceaf2720e17b730c6dfba8be4
```

## Delete

```
/* MimiContent struct */
0x01       optional replaces (present = 1)
  0xe701beee59f9376282f39092e1041b2a
    c2e3aad1776570c1a28de244979c71ed
0x00       length of topicId
0x00000000 expires
/* inReplyTo */
  0x01       optional inReplyTo (present = 1)
  0xd3c14744d1791d02548232c23d35efa9  // 0x20 octet message ID
    7668174ba385af066011e43bd7e51501
  0x01 hashAlg = sha256
  0x20 hash is 0x20 bytes
    0x6b44053cb68e3f0cdd219da8d7104afc
      2ae5ffff782154524cef093de39345a5
0x20       length of lastSeen vector (1 item)
    0x89d3472622a4d9de526742bcd00b09dc  // Edit
      78fa4edceaf2720e17b730c6dfba8be4
0x00       length of extensions vector
  /* NestablePart struct (body)*/
  0x01     disposition = render
  0x00     length of language
  0x0000   partIndex = 0 (1st part)
  0x00 cardinality = null (zero parts)

message ID
  0x89d3472622a40d6ceeb27c42490fdc64
    c0e9c20c598f9d7c8e81640dae8db0fb
```

## Unlike

```
/* MimiContent struct */
0x01       optional replaces (present = 1)
  0x4dcab7711a77ea1dd025a6a1a7fe01ab  // Like
    3b0d690f82417663cb752dfcc37779a1
0x00       length of topicId
0x00000000 expires is zero
/* inReplyTo */
  0x01       optional inReplyTo (present = 1)
  0xd3c14744d1791d02548232c23d35efa9  // 0x20 octet message ID
    7668174ba385af066011e43bd7e51501
  0x01 hashAlg = sha256
  0x20 hash is 0x20 bytes
    0x6b44053cb68e3f0cdd219da8d7104afc
      2ae5ffff782154524cef093de39345a5
0x20       length of lastSeen vector (1 item)
    0x89d3472622a40d6ceeb27c42490fdc64  // Delete
      c0e9c20c598f9d7c8e81640dae8db0fb
0x00       length of extensions vector
  /* NestablePart */
  0x02   disposition = reaction
  0x00   length of language is zero
  0x0000 partIndex = 0 (1st part)
  0x00 cardinality = null (zero parts)

message ID
  0x1a771ca1d84f8fda4184a1e02a549e20
    1bf434c6bfcf1237fa45463c6861853b
```

## Expiring

```
/* MimiContent struct */
0x00       optional replaces (present = 0)
0x00       length of topicId
0x62036674 expires on 1644390004  // 10 minutes later
0x00       optional inReplyTo (present = 0)
0x20       length of lastSeen vector
    0x1a771ca1d84f8fda4184a1e02a549e20  // Unlike
      1bf434c6bfcf1237fa45463c6861853b
0x00       length of extensions vector
  /* NestablePart struct (body)*/
  0x01     disposition = render
  0x00     length of language
  0x0000   partIndex = 0 (1st part)
  0x01     cardinality = single part
  /* SinglePart struct (part) */
    0x1b   length of contentType
      0x746578742f6d61726b646f776e3b6368  "text/markdown;cha"
        61727365743d7574662d38            "rset=utf-8"
    0x50   length of content
      0x5f5f2a56504e20474f494e4720444f57  "__*VPN GOING DOW"
        4e2a5f5f0a49276d207265626f6f7469  "N*__ I'm rebooti"
        6e67207468652056504e20696e207465  "ng the VPN in te"
        6e206d696e7574657320756e6c657373  "n minutes unless"
        20616e796f6e65206f626a656374732e  " anyone objects."

message ID
  0x5c95a4dfddab84348bcc265a479299fb
    d3a2eecfa3d490985da5113e5480c7f1
```

## Attachments

```
/* MimiContent struct */
0x00       optional replaces (present = 0)
0x00       length of topicId
0x00000000 expires is zero
0x00       optional inReplyTo (present = 0)
0x20       length of lastSeen vector
    0x5c95a4dfddab84348bcc265a479299fb  // Expiring
      d3a2eecfa3d490985da5113e5480c7f1
0x00       length of extensions vector
  /* NestablePart struct (body)*/
  0x06     disposition = attachment
  0x02     length of language
    0x656e                                "en"
  0x0000   partIndex = 0 (1st part)
  0x02     cardinality = external part
    /* External Part *
    0x09 length of contentType
      0x766964656f2f6d7034                "video/mp4"
    0x27 length of url
      0x68747470733a2f2f6578616d706c652e  "https://example."
        636f6d2f73746f726167652f62696766  "com/storage/bigf"
        696c652e6d7034                    "ile.mp4"
    0x00000000 expires is zero
    0x000000002a36ced1 size is 708234961 octets
    0x0001     encAlg is 0x0001 = AES-128-GCM
    0x10       key is 16 octets
      0x21399320958a6f4c745dde670d95e0d8
    0x0c       nonce is 12 octets
      0xc86cf2c33f21527d1dd76f5b
    0x00       aad is zero octets
    0x01       hashAlg = sha256
    0x20       content hash is 32 octets
      0x9ab17a8cf0890baaae7ee016c7312fcc
        080ba46498389458ee44f0276e783163
    0x1c       description is 0x1c octets
      0x3220686f757273206f66206b65792073  "2 hours of key s"
        69676e696e6720766964656f          "igning video"

message ID
  0xb267614d43e7676d28ef5b15e8676f23
    679fe365c78849d83e2ba0ae8196ec4e
```

## Conferencing

```
/* MimiContent struct */
0x00       optional replaces (present = 0)
0x07       length of topicId
  0x466f6f20313138                        "Foo 118"
0x00000000 expires is zero
0x00       optional inReplyTo (present = 0)
0x20       length of lastSeen vector
    0xb267614d43e7676d28ef5b15e8676f23  // Attachment
      679fe365c78849d83e2ba0ae8196ec4e
0x00       length of extensions vector
  /* NestablePart struct (body)*/
  0x07     disposition = session
  0x00     length of language
  0x0000   partIndex = 0 (1st part)
  0x02     cardinality = external part
    /* External Part *
    0x00 length of contentType
    0x1e length of url
      0x68747470733a2f2f6578616d706c652e  "https://example."
        636f6d2f6a6f696e2f3132333435      "com/join/12345"
    0x00000000 expires is zero
    0x0000000000000000 size is 0 octets // undetermined
    0x0000     encAlg is 0x0000 = none
    0x00       key is zero octets
    0x00       nonce is zero octets
    0x00       aad is zero octets
    0x00       hashAlg = none
    0x00       content hash is 32 octets
    0x1b  description is 0x1b octets
      0x4a6f696e2074686520466f6f20313138  "Join the Foo 118"
        20636f6e666572656e6365            " conference"

message ID
  0xb267614d43e7676d28ef5b15e8676f23
    679fe365c78849d83e2ba0ae8196ec4e
```

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
[@?RFC9420]. Concretely, an implementation has to scan through the
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
* clarified the difference between `render` and `inline` dispositions
* created a way for the messageId and timestamp to be shared in the MLS
  additional authenticated data field
* expanded discussion of what can and should be rendered when a mention is
  encountered; discussed how to prevent confusion attacks with mentions.
* added a lastSeen field used to ensure a more consistent sort order of
  messages in a room.

## Changes between draft-ietf-mimi-content-01 and draft-ietf-mimi-content-02

* consensus at IETF 118 was to use a hash of the ciphertext in lieu of the
  message ID
* consensus at IETF 118 was to use the hub accepted timestamp for protocol
  actions like sorting
* Updated author's address
