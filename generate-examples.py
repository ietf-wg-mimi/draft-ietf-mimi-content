#! /usr/bin/env python3
import cbor2

# ****** Generically useful functions

def bytes2hex(bytes):
    import binascii
    return binascii.hexlify(bytes).decode("utf-8")

def hex2bytes(string):
    return bytes.fromhex(string)

def new_redacted_entry_tag(value):
    REDACTED_ENTRY_TAG = 59
    return cbor2.CBORTag(REDACTED_ENTRY_TAG, value)

def new_salt():
    import secrets
    return secrets.token_bytes(16)

def sha256(bytes):
    import hashlib
    return hashlib.sha256(bytes).digest()

def write_to_file(value, filename):
    if isinstance(value, bytes):
        mode = 'wb'
    elif isinstance(value, str):
        mode = 'w'
    else:
        raise Exception("Can only write a bytes or str")
    with open(filename, mode) as f:
        f.write(value)

def pretty_hex(hex_str, indent=0):
    # takes a string of hex digits and returns an h'' EDN string
    # with at most 32 hex digits per line/row, indented `indent` spaces 
    l = len(hex_str)
    if l % 2 == 1:
        raise Exception("Odd number of hex digits")
    if l == 0:
        return "h''"
    # zero-indexed last row of hex chars
    last_row = (l - 1) // 32
    pretty = "h'"
    for row in range(last_row + 1):
        start = row*32
        if row != last_row:
            pretty += hex_str[start:start+32] + '\n' + ' '*(indent+2)
        else:
            pretty += hex_str[start:] + "'"
    return pretty

def pretty_id(message_id, indent=0):
    return pretty_hex(bytes2hex(message_id), indent=indent)

def iso_date(secs_since_epoch):
    import datetime
    t = datetime.datetime.fromtimestamp(secs_since_epoch, datetime.UTC)
    return t.isoformat() + 'Z'

def iso_msdate(ms_since_epoch):
    return iso_date(ms_since_epoch / 1000)

def indent(string, num_spaces=4):
    # take a multi-line string and add `num_spaces` spaces (if positive)
    # TBC: or remove (if negative)
    new_string = ""
    if num_spaces > 0:
        for line in string.splitlines():
            new_string += (' '*num_spaces + line + '\n')
        return new_string
    #elif spaces < 0:
        # trimming not yet supported
    else:
        return string


# ****** 

def message_id(message_array):
    if type(message_array) is not list:
        raise Exception("message_array needs to be a list")
    if type(message_array[0]) is not bytes or len(message_array[0]) != 16:
        raise Exception("first element of array is not a salt!")
    if type(message_array[5]) is not dict:
        raise Exception("extensions element not found in array")
    if SENDER in message_array[5]:
        sender_uri = message_array[5][SENDER]
    if ROOM in message_array[5]:
        room_uri = message_array[5][SENDER]
    if type(sender_uri) is not str or type(room_uri) is not str:
        raise Exception("sender_uri and room_uri must be text strings")
    hash_output = sha256(
        sender_uri.encode('utf-8') +
        room_uri.encode('utf-8') +
        cbor2.dumps(message_array) +
        message_array[0]  # salt
    )
    return b'\x01' + hash_output[0:31]


# ****** 

# numbered extensions
SENDER = 1
ROOM   = 2

# dispositions
RENDER = 1

# cardinalities
NULLPART = 0
SINGLEPART = 1
EXTERNALPART = 2
MULTIPART = 3

if __name__ == "__main__":
    room = "mimi://example.com/r/engineering_team"
    alice = "mimi://example.com/u/alice-smith"
    bob   = "mimi://example.com/u/bob-jones"
    cathy = "mimi://example.com/u/cathy-washington"
    t = 1644387225019
    message_ids = {}
    salts = [
        '5eed9406c2545547ab6f09f20a18b003',
        '11a458c73b8dd2cf404db4b378b8fe4d',
        'd37bc0e6a8b4f04e9e6382375f587bf6',
        '04f290e215d0f82d1750bfa8b7dc089d',
        '15d9705fd5bf5e02b0af47c85f8b98fe',
        'b8c2e6d8800ecf45df39be6c45f4c042',
        '0a590d73b2c7761c39168be5ebf7f2e6',
        'c5ba86dc9fd272e58ca52ec805b79199',
        '33be993eb39f418f9295afc2ae160d2d',
        '18fac6371e4e53f1aeaf8a013155c166',
        '678ac6cd54de049c3e9665cd212470fa',
        '261c953e178af653fe3d42641b91d814',
        '8528dc2d92e4f1944d62042907ab94d0',
        'b8362793168d18c049b882d4642a2274',
        'ccdc008f57a1e9610f6a14348276ea9f',
        '7a1bcbb03c3af6634e46233f06079bf9',
        '9438fa187e880bcc7392ffcea5abcea0',
        '59f11a86f4bd12638ae2f5a74eae8372',
        'fac9b9b4541212aa666c0be17c80dcef',
        '1e5561ed4304b627fdfddb89f0c04f25'
    ]

    def make_singlepart(content=b'',
            content_type="text/markdown;variant=GFM-MIMI",
            lang="", dispo=RENDER):
        body = [
            dispo,
            lang,
            SINGLEPART,
            content_type,
            content
        ]
        return body
        #        body_edn = f'''  [ {' '*34} / body (NestedPart) /
        #    {dispo_edn}
        #    {lang_edn}
        #    {SINGLEPART},                                / cardinality = single part /
        #    {content_type_edn}
        #                                      / content                   /
        #    '{content}'
        #  ]
        #'''
        #        return(body, body_edn)

    def make_nullpart(lang="", dispo=RENDER):
        body = [
            dispo,
            lang,
            NULLPART
        ]
        return body

    def make_externalpart(lang="", dispo=RENDER,
            content_type="", url="", expires=0, size=0,
            encAlg=0, key=b'', nonce=b'', aad=b'',
            hashAlg=1, contentHash=b'',
            description="", filename=""):
        body = [
            dispo,
            lang,
            EXTERNALPART,
            content_type,
            url,
            expires,
            size,
            encAlg,
            key,
            nonce,
            aad,
            hashAlg,
            contentHash,
            description,
            filename
        ]
        return body

    def make_multipart(parts_array, lang="", dispo=RENDER):
        if type(parts_array) is not list or len(parts_array) < 2:
            raise Exception("invalid Parts array")
        body = [
            dispo,
            lang,
            MULTIPART,
            parts_array
        ]
        return body

    
    def make_message(message_name, salt_index,
            sender=alice, room=room,
            replaces=None, topic=b'',
            expires=None, relative_expires=False,
            reply_to=None, body=None, body_edn=None):
        # generates and writes CBOR version of message
        # TODO make EDN too
        # returns message_id
        if body is None:
            raise Exception("Can't make message with no body. Maybe you wanted a nullpart?")
        if expires is None:
            exp = None
        else:
            exp = [ relative_expires, expires ]
        msg = [
            hex2bytes(salts[salt_index]),  # salt
            replaces,                      # replaces
            topic,                         # topic
            exp,                           # expires
            reply_to,                      # inReplyTo
            {                              # extensions
                SENDER: sender,
                ROOM: room
            },
            body
        ]
        write_to_file(cbor2.dumps(msg), "examples/" + message_name + ".cbor")
        msgid = message_id(msg)
        print(message_name + ":")
        print(pretty_id(msgid, 0))
        return msgid

    # ORIGINAL MESSAGE
#    part = make_singlepart(
#        b'Hi everyone, we just shipped release 2.0. __Good  work__!')
#    message_ids[0] = make_message("original", 0,
#        sender=alice, room=room,
#        replaces=None, topic=b'',
#        expires=None, relative_expires=False,
#        reply_to=None, body=part)




    original = [
        hex2bytes(salts[0]),  # salt
        None,                 # replaces
        b'',                  # topic
        None,                 # expires
        None,                 # inReplyTo
        {                     # extensions
            SENDER: alice,
            ROOM: room
        },
        [                     # body
            RENDER,
            "",
            SINGLEPART,
            "text/markdown;variant=GFM-MIMI",
            b'Hi everyone, we just shipped release 2.0. __Good  work__!'
        ]
    ]
    msgid = message_id(original)
    message_ids["original"] = msgid

    original_edn = f"""/ message ID = {pretty_hex(bytes2hex(msgid), 15)} /
/ timestamp  = {t} = {iso_msdate(t)} /
[
  h'{salts[0]}', / salt /
  null,                                / replaces /
  h'',                                 / topicId /
  null,                                / expires /
  null,                                / inReplyTo /
  {{                                    / extensions /
    {SENDER}: "{alice}",
    {ROOM}: "{room}"
  }},
  [                                    / body (NestedPart) /
    {RENDER},                                / dispostion = render       /
    "",                               / language                  /
    {SINGLEPART},                                / cardinality = single part /
    "text/markdown;variant=GFM",      / contentType               /
                                      / content                   /
    'Hi everyone, we just shipped release 2.0. __Good  work__!'
  ]
]"""
    write_to_file(cbor2.dumps(original), "examples/original.cbor")
    write_to_file(original_edn, "examples/original.edn")
    
    
    # REPLY MESSAGE

    reply = [
        hex2bytes(salts[1]),         # salt
        None,                        # replaces
        b'',                         # topic
        None,                        # expires
        message_ids["original"],     # inReplyTo
        {                            # extensions
            SENDER: bob,
            ROOM: room
        },
        [                       # body
            RENDER,
            "",
            SINGLEPART,
            "text/markdown;variant=GFM",
            b"Right on! _Congratulations_ 'all!"
        ]
    ]
    msgid = message_id(reply)
    message_ids["reply"] = msgid

    original_edn = f"""/ message ID = {pretty_id(msgid, 15)} /
/ timestamp  = {t+12473} = {iso_msdate(t+12473)} /
[
  h'{salts[1]}', / salt /
  null,                                / replaces /
  h'',                                 / topicId /
  null,                                / expires /
  {pretty_id(message_ids["original"], 2)}, / inReplyTo /
  {{                                    / extensions /
    {SENDER}: "{bob}",
    {ROOM}: "{room}"
  }},
  [                                    / body (NestedPart) /
    {RENDER},                                / dispostion = render       /
    "",                               / language                  /
    {SINGLEPART},                                / cardinality = single part /
    "text/markdown;variant=GFM",      / contentType               /
                                      / content                   /
    'Right on! _Congratulations_ \'all!'
  ]
]"""
    write_to_file(cbor2.dumps(original), "examples/reply.cbor")
    write_to_file(original_edn, "examples/reply.edn")
    

